"""
Main GUI Application for Face Filter Creator
"""

import sys
import os
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QComboBox, QSlider, QLabel, QTabWidget, QFileDialog,
    QMessageBox, QProgressDialog, QSpinBox, QDialog
)
from PyQt5.QtGui import QImage, QPixmap, QFont
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
import cv2
import numpy as np

from src.core.face_detector import FaceDetector
from src.core.camera_manager import CameraManager, VideoProcessor
from src.filters.filter_processor import FilterProcessor
from src.filters.filter_manager import FilterManager
from src.filters.face_transformer import FaceTransformer


class CameraThread(QThread):
    """Thread for continuous camera streaming"""
    frame_ready = pyqtSignal(np.ndarray)
    
    def __init__(self, camera_manager: CameraManager):
        super().__init__()
        self.camera_manager = camera_manager
        self.running = True
        self.frame_skip = 1  # Process every 2nd frame (was 2, which meant every 3rd)
        self.frame_count = 0
    
    def run(self):
        while self.running:
            frame = self.camera_manager.get_frame()
            if frame is not None:
                # Skip frames to reduce CPU usage (but not as aggressively)
                self.frame_count += 1
                if self.frame_count % (self.frame_skip + 1) == 0:
                    self.frame_ready.emit(frame)
    
    def stop(self):
        self.running = False


class FaceFilterApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        # Initialize components
        self.face_detector = FaceDetector()
        self.filter_processor = FilterProcessor()
        self.face_transformer = FaceTransformer()
        self.filter_manager = FilterManager()
        self.camera_manager = CameraManager()
        self.video_processor = VideoProcessor()
        
        # UI state
        self.current_frame = None
        self.current_filter = None
        self.current_landmarks = None
        self.captured_photos = []
        self.captured_landmarks = []
        self.filter_intensity = 0.8
        
        # Camera thread
        self.camera_thread = None
        
        # Debug counter
        self.frame_count = 0
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Face Filter Creator - Real-time AR Face Filters")
        self.setGeometry(100, 100, 1400, 900)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        
        # Tab widget for different sections
        tabs = QTabWidget()
        
        # Tab 1: Create Filter
        create_tab = self.create_filter_tab()
        tabs.addTab(create_tab, "Create Filter")
        
        # Tab 2: Apply Filter (Real-time)
        apply_tab = self.apply_filter_tab()
        tabs.addTab(apply_tab, "Apply Filter (Live)")
        
        # Tab 3: Process Video
        video_tab = self.process_video_tab()
        tabs.addTab(video_tab, "Process Video")
        
        # Tab 4: Manage Filters
        manage_tab = self.manage_filters_tab()
        tabs.addTab(manage_tab, "Manage Filters")
        
        main_layout.addWidget(tabs)
        central_widget.setLayout(main_layout)
    
    def create_filter_tab(self) -> QWidget:
        """Create the filter creation tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Instructions
        title = QLabel("Step 1: Create Your Face Filter")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        instructions = QLabel(
            "1. Click 'Capture Photos from Camera' to take multiple photos of your face\n"
            "   OR 'Upload Photos' to select existing photos\n"
            "2. Photos will be analyzed to create your unique filter\n"
            "3. Name your filter and save it"
        )
        layout.addWidget(instructions)
        
        # Buttons layout
        btn_layout = QHBoxLayout()
        
        self.capture_btn = QPushButton("Capture Photos from Camera")
        self.capture_btn.clicked.connect(self.capture_photos_from_camera)
        btn_layout.addWidget(self.capture_btn)
        
        self.upload_btn = QPushButton("Upload Photos")
        self.upload_btn.clicked.connect(self.upload_photos)
        btn_layout.addWidget(self.upload_btn)
        
        layout.addLayout(btn_layout)
        
        # Status label
        self.create_status_label = QLabel("Status: No photos captured yet")
        layout.addWidget(self.create_status_label)
        
        # Filter name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Filter Name:"))
        
        from PyQt5.QtWidgets import QLineEdit
        self.filter_name_input = QLineEdit()
        self.filter_name_input.setPlaceholderText("Enter a name for your filter")
        name_layout.addWidget(self.filter_name_input)
        
        layout.addLayout(name_layout)
        
        # Create and save filter button
        self.create_filter_btn = QPushButton("Create & Save Filter")
        self.create_filter_btn.clicked.connect(self.create_and_save_filter)
        self.create_filter_btn.setEnabled(False)
        layout.addWidget(self.create_filter_btn)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def apply_filter_tab(self) -> QWidget:
        """Create the live filter application tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Instructions
        title = QLabel("Apply Filter in Real-Time")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Camera preview and controls
        cam_layout = QHBoxLayout()
        
        # Left side - camera feed
        left_layout = QVBoxLayout()
        left_layout.addWidget(QLabel("Camera Preview:"))
        
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(400, 300)
        self.camera_label.setStyleSheet("border: 2px solid black;")
        left_layout.addWidget(self.camera_label)
        
        # Camera controls
        cam_btn_layout = QHBoxLayout()
        
        self.start_cam_btn = QPushButton("Start Camera")
        self.start_cam_btn.clicked.connect(self.start_camera)
        cam_btn_layout.addWidget(self.start_cam_btn)
        
        self.stop_cam_btn = QPushButton("Stop Camera")
        self.stop_cam_btn.clicked.connect(self.stop_camera)
        self.stop_cam_btn.setEnabled(False)
        cam_btn_layout.addWidget(self.stop_cam_btn)
        
        left_layout.addLayout(cam_btn_layout)
        cam_layout.addLayout(left_layout)
        
        # Right side - filter controls
        right_layout = QVBoxLayout()
        right_layout.addWidget(QLabel("Filter Selection:"))
        
        # Filter dropdown
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Select Filter:"))
        
        self.filter_combo = QComboBox()
        self.filter_combo.currentTextChanged.connect(self.on_filter_selected)
        filter_layout.addWidget(self.filter_combo)
        
        right_layout.addLayout(filter_layout)
        
        # Filter intensity slider
        intensity_layout = QHBoxLayout()
        intensity_layout.addWidget(QLabel("Intensity:"))
        
        self.intensity_slider = QSlider(Qt.Horizontal)
        self.intensity_slider.setMinimum(0)
        self.intensity_slider.setMaximum(100)
        self.intensity_slider.setValue(80)
        self.intensity_slider.valueChanged.connect(self.on_intensity_changed)
        intensity_layout.addWidget(self.intensity_slider)
        
        self.intensity_value_label = QLabel("80%")
        intensity_layout.addWidget(self.intensity_value_label)
        
        right_layout.addLayout(intensity_layout)
        
        # Set as default button
        self.set_default_btn = QPushButton("Set as Default Filter")
        self.set_default_btn.clicked.connect(self.set_as_default)
        self.set_default_btn.setEnabled(False)
        right_layout.addWidget(self.set_default_btn)
        
        # Current default display
        self.default_filter_label = QLabel("Default Filter: None")
        self.default_filter_label.setStyleSheet("color: blue; font-weight: bold;")
        right_layout.addWidget(self.default_filter_label)
        
        right_layout.addStretch()
        
        cam_layout.addLayout(right_layout)
        
        layout.addLayout(cam_layout)
        
        widget.setLayout(layout)
        return widget
    
    def process_video_tab(self) -> QWidget:
        """Create the video processing tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Process Video with Filter")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        instructions = QLabel(
            "Select a video file and a filter, then process it to create\n"
            "a new video with the filter applied to all frames"
        )
        layout.addWidget(instructions)
        
        # File selection
        file_layout = QHBoxLayout()
        file_layout.addWidget(QLabel("Video File:"))
        
        self.video_file_label = QLabel("No video selected")
        file_layout.addWidget(self.video_file_label)
        
        select_video_btn = QPushButton("Select Video")
        select_video_btn.clicked.connect(self.select_video_file)
        file_layout.addWidget(select_video_btn)
        
        layout.addLayout(file_layout)
        
        # Filter selection
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Filter:"))
        
        self.video_filter_combo = QComboBox()
        filter_layout.addWidget(self.video_filter_combo)
        
        layout.addLayout(filter_layout)
        
        # Intensity for video
        video_intensity_layout = QHBoxLayout()
        video_intensity_layout.addWidget(QLabel("Filter Intensity:"))
        
        self.video_intensity_slider = QSlider(Qt.Horizontal)
        self.video_intensity_slider.setMinimum(0)
        self.video_intensity_slider.setMaximum(100)
        self.video_intensity_slider.setValue(80)
        video_intensity_layout.addWidget(self.video_intensity_slider)
        
        self.video_intensity_label = QLabel("80%")
        video_intensity_layout.addWidget(self.video_intensity_label)
        
        layout.addLayout(video_intensity_layout)
        
        # Process button
        self.process_video_btn = QPushButton("Process Video")
        self.process_video_btn.clicked.connect(self.process_video)
        layout.addWidget(self.process_video_btn)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def manage_filters_tab(self) -> QWidget:
        """Create the filter management tab"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Manage Your Filters")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        layout.addWidget(title)
        
        # Filter list
        list_layout = QHBoxLayout()
        list_layout.addWidget(QLabel("Your Filters:"))
        
        self.filters_combo = QComboBox()
        list_layout.addWidget(self.filters_combo)
        
        layout.addLayout(list_layout)
        
        # Management buttons
        btn_layout = QHBoxLayout()
        
        delete_btn = QPushButton("Delete Filter")
        delete_btn.clicked.connect(self.delete_filter)
        btn_layout.addWidget(delete_btn)
        
        refresh_btn = QPushButton("Refresh List")
        refresh_btn.clicked.connect(self.refresh_filter_lists)
        btn_layout.addWidget(refresh_btn)
        
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def capture_photos_from_camera(self):
        """Capture multiple photos from camera"""
        dialog = CameraCaptureDialog(self.camera_manager, self)
        if dialog.exec_():
            self.captured_photos = dialog.saved_photos
            self.create_status_label.setText(
                f"Status: {len(self.captured_photos)} photos captured successfully"
            )
            self.create_filter_btn.setEnabled(len(self.captured_photos) > 0)
    
    def upload_photos(self):
        """Upload photos from file system - select multiple photos"""
        photos, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Photos for Filter (Hold Ctrl to select multiple)",
            "",
            "Image files (*.jpg *.jpeg *.png *.bmp)"
        )
        
        if photos:
            if len(photos) < 3:
                QMessageBox.warning(self, "Warning", 
                    "Recommended to use at least 3 photos for better filter quality.\n"
                    "You can still proceed with fewer photos.")
            
            self.captured_photos = photos
            self.create_status_label.setText(
                f"Status: {len(self.captured_photos)} photos uploaded"
            )
            self.create_filter_btn.setEnabled(len(self.captured_photos) > 0)
    
    def create_and_save_filter(self):
        """Create and save filter from captured photos with face morphing"""
        if not self.captured_photos:
            QMessageBox.warning(self, "Error", "No photos to process")
            return
        
        filter_name = self.filter_name_input.text().strip()
        if not filter_name:
            QMessageBox.warning(self, "Error", "Please enter a filter name")
            return
        
        # Load photos and extract facial landmarks
        face_images = []
        face_landmarks = []
        
        for photo_path in self.captured_photos:
            try:
                img = cv2.imread(str(photo_path))
                if img is None:
                    continue
                
                # Detect face and get landmarks
                faces = self.face_detector.detect_faces(img)
                if not faces:
                    print(f"Warning: No face detected in {photo_path}")
                    continue
                
                # Extract face region
                x, y, w, h = faces[0]['bbox']
                face_region = img[max(0, y):min(img.shape[0], y+h), 
                                  max(0, x):min(img.shape[1], x+w)]
                
                # Get landmarks
                landmarks = self.face_detector.get_face_landmarks(img)
                if landmarks is not None:
                    face_images.append(face_region)
                    face_landmarks.append(landmarks)
            
            except Exception as e:
                print(f"Error processing {photo_path}: {e}")
                continue
        
        if not face_images:
            QMessageBox.warning(self, "Error", 
                "Could not detect faces in any photos. \n"
                "Make sure faces are clearly visible.")
            return
        
        # Create filter using face transformer
        try:
            filter_profile = self.face_transformer.create_face_filter(
                face_images, face_landmarks
            )
            self.filter_manager.save_filter(filter_name, filter_profile)
            
            QMessageBox.information(self, "Success", 
                f"Face Transform Filter '{filter_name}' created!\n"
                f"Processed {len(face_images)} photos with face landmarks.\n"
                f"Use this filter to transform other faces!")
            
            # Clear and refresh
            self.filter_name_input.clear()
            self.captured_photos = []
            self.captured_landmarks = []
            self.create_filter_btn.setEnabled(False)
            self.create_status_label.setText("Status: Filter saved. Create another or apply it!")
            
            self.refresh_filter_lists()
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create filter: {str(e)}")
    
    def start_camera(self):
        """Start camera stream"""
        self.start_cam_btn.setEnabled(False)
        self.start_cam_btn.setText("Starting camera...")
        
        if self.camera_manager.open_camera():
            self.start_cam_btn.setText("Stop Camera")  # Already disabled, just for info
            self.stop_cam_btn.setEnabled(True)
            
            self.camera_thread = CameraThread(self.camera_manager)
            self.camera_thread.frame_ready.connect(self.update_camera_feed)
            self.camera_thread.start()
            
            self.start_cam_btn.setText("Camera Running...")
        else:
            QMessageBox.critical(self, "Error", "Could not open camera")
            self.start_cam_btn.setEnabled(True)
            self.start_cam_btn.setText("Start Camera")
    
    def stop_camera(self):
        """Stop camera stream"""
        if self.camera_thregibrad:
            self.camera_thread.stop()
            self.camera_thread.wait()
        
        self.camera_manager.close_camera()
        self.start_cam_btn.setEnabled(True)
        self.stop_cam_btn.setEnabled(False)
        self.camera_label.clear()
    
    def update_camera_feed(self, frame: np.ndarray):
        """Update camera label with face-morphing filter applied"""
        self.current_frame = frame
        display_frame = frame.copy()
        self.frame_count += 1
        
        # Debug every 5 frames to reduce spam
        debug = (self.frame_count % 5 == 0)
        
        # Detect faces
        faces = self.face_detector.detect_faces(frame)
        
        if debug and self.current_filter:
            if not faces:
                print("DEBUG: Filter selected but no faces detected")
            else:
                print(f"DEBUG: Processing {len(faces)} face(s) with filter intensity {self.filter_intensity:.1f}")
        
        # Apply face transformation if filter is selected
        if self.current_filter and faces:
            # Get full frame landmarks once
            frame_landmarks = self.face_detector.get_face_landmarks(frame)
            
            if debug:
                if frame_landmarks is not None:
                    print(f"DEBUG: Got {len(frame_landmarks)} landmarks from frame")
                else:
                    print("DEBUG: No landmarks detected in frame")
            
            for face_idx, face in enumerate(faces):
                x, y, w, h = face['bbox']
                # Make sure coordinates are valid
                x1, y1 = max(0, x), max(0, y)
                x2, y2 = min(display_frame.shape[1], x + w), min(display_frame.shape[0], y + h)
                
                if x2 > x1 and y2 > y1:
                    face_region = display_frame[y1:y2, x1:x2].copy()
                    
                    try:
                        if frame_landmarks is not None:
                            if debug:
                                print(f"DEBUG: Face {face_idx} region: ({x1},{y1}) to ({x2},{y2}), size: {x2-x1}x{y2-y1}")
                            
                            # Apply face transformation (morphing) with full frame landmarks
                            transformed = self.face_transformer.apply_face_transform(
                                face_region, frame_landmarks, self.current_filter, 
                                self.filter_intensity, face_bbox=(x1, y1, x2, y2)
                            )
                            
                            # Check if transformation was applied
                            diff = np.abs(transformed.astype(float) - face_region.astype(float)).mean()
                            if debug:
                                print(f"DEBUG: Transform applied, pixel difference: {diff:.2f}")
                            
                            display_frame[y1:y2, x1:x2] = transformed
                        else:
                            if debug:
                                print("DEBUG: No landmarks, skipping transformation")
                    
                    except Exception as e:
                        print(f"ERROR in transform: {e}")
        
        # Draw boxes on top
        display_frame = self.face_detector.draw_faces(display_frame, faces)
        
        # Convert to QImage and display
        h, w, ch = display_frame.shape
        bytes_per_line = ch * w
        q_img = QImage(display_frame.data, w, h, bytes_per_line, QImage.Format_BGR888)
        
        pixmap = QPixmap.fromImage(q_img)
        self.camera_label.setPixmap(pixmap.scaled(
            400, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
    
    def on_filter_selected(self):
        """Handle filter selection"""
        filter_name = self.filter_combo.currentText()
        
        if filter_name and filter_name != "None":
            try:
                self.current_filter = self.filter_manager.load_filter(filter_name)
                self.set_default_btn.setEnabled(True)
                print(f"Filter loaded: {filter_name}")
            except Exception as e:
                print(f"Error loading filter {filter_name}: {e}")
                QMessageBox.warning(self, "Error", f"Could not load filter: {str(e)}")
                self.current_filter = None
                self.set_default_btn.setEnabled(False)
        else:
            self.current_filter = None
            self.set_default_btn.setEnabled(False)
    
    def on_intensity_changed(self, value):
        """Handle intensity slider change"""
        self.filter_intensity = value / 100.0
        self.intensity_value_label.setText(f"{value}%")
    
    def set_as_default(self):
        """Set current filter as default"""
        filter_name = self.filter_combo.currentText()
        
        if filter_name and filter_name != "None":
            try:
                self.filter_manager.set_default_filter(filter_name)
                self.default_filter_label.setText(f"Default Filter: {filter_name}")
                QMessageBox.information(self, "Success", 
                    f"'{filter_name}' set as default filter!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not set default: {str(e)}")
    
    def select_video_file(self):
        """Select a video file for processing"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Video File",
            "",
            "Video files (*.mp4 *.avi *.mov *.mkv)"
        )
        
        if file_path:
            self.video_file_label.setText(os.path.basename(file_path))
            self.selected_video_path = file_path
    
    def process_video(self):
        """Process video with selected filter"""
        if not hasattr(self, 'selected_video_path'):
            QMessageBox.warning(self, "Error", "Please select a video file")
            return
        
        filter_name = self.video_filter_combo.currentText()
        if not filter_name or filter_name == "None":
            QMessageBox.warning(self, "Error", "Please select a filter")
            return
        
        try:
            # Get output file path
            output_path, _ = QFileDialog.getSaveFileName(
                self, "Save Processed Video", "", "MP4 files (*.mp4)"
            )
            
            if not output_path:
                return
            
            filter_profile = self.filter_manager.load_filter(filter_name)
            intensity = self.video_intensity_slider.value() / 100.0
            
            # Create processing function
            def process_frame(frame):
                faces = self.face_detector.detect_faces(frame)
                result = frame.copy()
                
                for face in faces:
                    x, y, w, h = face['bbox']
                    face_region = result[y:y+h, x:x+w]
                    
                    if face_region.size > 0:
                        filtered_region = self.filter_processor.apply_filter(
                            face_region, filter_profile, intensity
                        )
                        result[y:y+h, x:x+w] = filtered_region
                
                return result
            
            # Process video
            self.video_processor.process_video_file(
                self.selected_video_path,
                output_path,
                process_frame
            )
            
            QMessageBox.information(self, "Success", 
                f"Video processed and saved to:\n{output_path}")
        
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process video: {str(e)}")
    
    def refresh_filter_lists(self):
        """Refresh all filter dropdown lists"""
        filters = self.filter_manager.get_all_filters()
        
        # Update all dropdowns
        for combo in [self.filter_combo, self.video_filter_combo, self.filters_combo]:
            combo.clear()
            combo.addItem("None")
            combo.addItems(filters)
        
        # Update default filter display
        default = self.filter_manager.get_default_filter()
        if default:
            self.default_filter_label.setText(f"Default Filter: {default}")
        else:
            self.default_filter_label.setText("Default Filter: None")
    
    def delete_filter(self):
        """Delete selected filter"""
        filter_name = self.filters_combo.currentText()
        
        if not filter_name or filter_name == "None":
            QMessageBox.warning(self, "Error", "Please select a filter to delete")
            return
        
        reply = QMessageBox.question(self, "Confirm", 
            f"Are you sure you want to delete '{filter_name}'?",
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                self.filter_manager.delete_filter(filter_name)
                QMessageBox.information(self, "Success", f"Filter '{filter_name}' deleted")
                self.refresh_filter_lists()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete filter: {str(e)}")
    
    def closeEvent(self, event):
        """Clean up on close"""
        self.stop_camera()
        event.accept()


class CameraCaptureDialog(QDialog):
    """Dialog for capturing photos from camera"""
    
    def __init__(self, camera_manager: CameraManager, parent=None):
        super().__init__(parent)
        self.camera_manager = camera_manager
        self.saved_photos = []
        self.camera_thread = None
        self.photo_count = 0
        self.max_photos = 5
        
        self.init_ui()
    
    def init_ui(self):
        """Initialize dialog UI"""
        self.setWindowTitle("Capture Photos for Filter")
        self.setGeometry(200, 200, 800, 600)
        
        layout = QVBoxLayout()
        
        title = QLabel(f"Capture {self.max_photos} Photos of Your Face")
        title.setFont(QFont("Arial", 12, QFont.Bold))
        layout.addWidget(title)
        
        instruction = QLabel(
            "Position your face clearly in the camera view.\n"
            "Try different angles and lighting conditions.\n"
            "Click 'Capture Photo' to save each photo."
        )
        layout.addWidget(instruction)
        
        # Camera preview
        self.camera_label = QLabel()
        self.camera_label.setMinimumSize(600, 400)
        self.camera_label.setStyleSheet("border: 2px solid black;")
        layout.addWidget(self.camera_label)
        
        # Progress
        self.progress_label = QLabel(f"Photos captured: 0/{self.max_photos}")
        layout.addWidget(self.progress_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.capture_btn = QPushButton("Capture Photo")
        self.capture_btn.clicked.connect(self.capture_photo)
        btn_layout.addWidget(self.capture_btn)
        
        self.done_btn = QPushButton("Done")
        self.done_btn.clicked.connect(self.finish_capture)
        self.done_btn.setEnabled(False)
        btn_layout.addWidget(self.done_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
        
        # Start camera
        if self.camera_manager.open_camera():
            self.camera_thread = CameraThread(self.camera_manager)
            self.camera_thread.frame_ready.connect(self.update_preview)
            self.camera_thread.start()
        else:
            QMessageBox.critical(self, "Error", "Could not open camera")
            self.reject()
    
    def update_preview(self, frame: np.ndarray):
        """Update camera preview"""
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        q_img = QImage(frame.data, w, h, bytes_per_line, QImage.Format_BGR888)
        
        pixmap = QPixmap.fromImage(q_img)
        self.camera_label.setPixmap(pixmap.scaled(
            600, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation
        ))
    
    def capture_photo(self):
        """Capture a photo"""
        if self.photo_count < self.max_photos:
            import tempfile
            temp_dir = tempfile.gettempdir()
            photo_path = f"{temp_dir}/face_filter_photo_{self.photo_count:03d}.jpg"
            
            if self.camera_manager.save_frame(photo_path):
                self.saved_photos.append(photo_path)
                self.photo_count += 1
                self.progress_label.setText(f"Photos captured: {self.photo_count}/{self.max_photos}")
                
                if self.photo_count >= self.max_photos:
                    self.capture_btn.setEnabled(False)
                    self.done_btn.setEnabled(True)
                    QMessageBox.information(self, "Success", 
                        f"All {self.max_photos} photos captured!")
    
    def finish_capture(self):
        """Finish capturing photos"""
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread.wait()
        
        self.camera_manager.close_camera()
        self.accept()
    
    def closeEvent(self, event):
        """Clean up on close"""
        if self.camera_thread:
            self.camera_thread.stop()
            self.camera_thread.wait()
        
        self.camera_manager.close_camera()
        event.accept()


def main():
    app = QApplication(sys.argv)
    window = FaceFilterApp()
    window.show()
    
    # Refresh filter lists on startup
    window.refresh_filter_lists()
    
    # Load default filter if set
    default_filter = window.filter_manager.get_default_filter()
    if default_filter:
        # Find and select default filter in combo
        index = window.filter_combo.findText(default_filter)
        if index >= 0:
            window.filter_combo.setCurrentIndex(index)
            window.on_filter_selected()
    
    sys.exit(app.exec_())
