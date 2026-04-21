"""
Camera and Video Processing Module
Handles real-time camera access and video processing
"""

import cv2
import numpy as np
from typing import Optional, Callable
import threading


class CameraManager:
    def __init__(self, camera_id: int = 0):
        self.camera_id = camera_id
        self.cap = None
        self.is_running = False
        self.current_frame = None
        self.frame_lock = threading.Lock()

    def open_camera(self) -> bool:
        """Open camera connection"""
        self.cap = cv2.VideoCapture(self.camera_id)
        
        if not self.cap.isOpened():
            return False
        
        # Set camera properties for better performance
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 30)
        
        return True

    def close_camera(self) -> None:
        """Close camera connection"""
        if self.cap:
            self.cap.release()

    def get_frame(self) -> Optional[np.ndarray]:
        """Get current frame from camera"""
        if not self.cap or not self.cap.isOpened():
            return None
        
        ret, frame = self.cap.read()
        
        if not ret:
            return None
        
        with self.frame_lock:
            self.current_frame = frame
        
        return frame

    def start_camera_stream(self, callback: Callable[[np.ndarray], None], fps: int = 30) -> threading.Thread:
        """
        Start continuous camera stream in background thread
        Callback receives each frame
        """
        def stream_thread():
            self.is_running = True
            frame_delay = int(1000 / fps)  # milliseconds
            
            while self.is_running:
                frame = self.get_frame()
                if frame is not None:
                    callback(frame)
                else:
                    self.is_running = False
                    break
        
        thread = threading.Thread(target=stream_thread, daemon=True)
        thread.start()
        return thread

    def stop_camera_stream(self) -> None:
        """Stop camera stream"""
        self.is_running = False

    def save_frame(self, filename: str) -> bool:
        """Save current frame to file"""
        if self.current_frame is None:
            return False
        
        return cv2.imwrite(filename, self.current_frame)


class VideoProcessor:
    def __init__(self):
        self.output_path = None

    def process_video_file(self, input_path: str, output_path: str, 
                          processor_fn: Callable[[np.ndarray], np.ndarray]) -> bool:
        """
        Process a video file frame by frame
        processor_fn: function that takes a frame and returns processed frame
        """
        cap = cv2.VideoCapture(input_path)
        
        if not cap.isOpened():
            return False
        
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            processed_frame = processor_fn(frame)
            out.write(processed_frame)
            
            frame_count += 1
            progress = (frame_count / total_frames) * 100
            print(f"Processing: {progress:.1f}%", end='\r')
        
        cap.release()
        out.release()
        
        return True

    def capture_photos_from_video(self, video_path: str, output_dir: str, 
                                 num_photos: int = 5) -> list:
        """
        Capture N evenly distributed photos from a video
        Returns list of saved photo paths
        """
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            return []
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_interval = total_frames // num_photos
        
        saved_photos = []
        photo_count = 0
        frame_count = 0
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            if frame_count % frame_interval == 0 and photo_count < num_photos:
                photo_path = f"{output_dir}/photo_{photo_count:03d}.jpg"
                cv2.imwrite(photo_path, frame)
                saved_photos.append(photo_path)
                photo_count += 1
            
            frame_count += 1
        
        cap.release()
        
        return saved_photos
