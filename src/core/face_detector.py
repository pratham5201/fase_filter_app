"""
Face Detection and Analysis Module
Uses MediaPipe for face detection and landmark detection
"""

import mediapipe as mp
import cv2
import numpy as np
from typing import List, Tuple, Optional


class FaceDetector:
    def __init__(self):
        self.mp_face_detection = mp.solutions.face_detection
        self.mp_drawing = mp.solutions.drawing_utils
        self.detector = self.mp_face_detection.FaceDetection(
            model_selection=1,  # 1 for full range of distances
            min_detection_confidence=0.5
        )
        
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )

    def detect_faces(self, image: np.ndarray) -> List[dict]:
        """Detect faces in image"""
        h, w, c = image.shape
        results = self.detector.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        faces = []
        if results.detections:
            for detection in results.detections:
                bbox = detection.location_data.relative_bounding_box
                
                x = int(bbox.xmin * w)
                y = int(bbox.ymin * h)
                width = int(bbox.width * w)
                height = int(bbox.height * h)
                
                faces.append({
                    'bbox': (x, y, width, height),
                    'confidence': detection.score[0]
                })
        
        return faces

    def get_face_landmarks(self, image: np.ndarray) -> Optional[np.ndarray]:
        """Get face landmarks (468 points)"""
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.face_mesh.process(rgb_image)
        
        if results.multi_face_landmarks:
            landmarks = results.multi_face_landmarks[0]
            h, w = image.shape[:2]
            
            landmark_points = []
            for landmark in landmarks.landmark:
                x = int(landmark.x * w)
                y = int(landmark.y * h)
                landmark_points.append([x, y])
            
            return np.array(landmark_points)
        
        return None

    def extract_face_region(self, image: np.ndarray, bbox: Tuple) -> Tuple[np.ndarray, Tuple]:
        """Extract face region from image with padding"""
        x, y, width, height = bbox
        
        # Add padding
        padding = 20
        x_min = max(0, x - padding)
        y_min = max(0, y - padding)
        x_max = min(image.shape[1], x + width + padding)
        y_max = min(image.shape[0], y + height + padding)
        
        face_region = image[y_min:y_max, x_min:x_max]
        return face_region, (x_min, y_min, x_max, y_max)

    def draw_faces(self, image: np.ndarray, faces: List[dict]) -> np.ndarray:
        """Draw bounding boxes on detected faces"""
        result_image = image.copy()
        
        for face in faces:
            x, y, width, height = face['bbox']
            cv2.rectangle(result_image, (x, y), (x + width, y + height), (0, 255, 0), 2)
            cv2.putText(result_image, f"Conf: {face['confidence']:.2f}", 
                       (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        return result_image
