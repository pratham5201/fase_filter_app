"""
Face Transformer - Real Face Morphing/Transformation
Transforms one face to look like another using facial landmarks and warping
"""

import numpy as np
import cv2
from typing import Dict, List, Tuple, Optional
from scipy.spatial import Delaunay


class FaceTransformer:
    """Transform faces to match a target face using landmark-based morphing"""
    
    def __init__(self):
        self.source_landmarks = None
        self.source_face_image = None
        self.cached_delaunay = None  # Cache Delaunay triangulation
        self.cached_source_landmarks = None
        
    def extract_landmarks(self, image: np.ndarray, landmarks_points: np.ndarray) -> np.ndarray:
        """Extract and validate facial landmarks"""
        if landmarks_points is None or len(landmarks_points) == 0:
            return None
        
        # Ensure landmarks are within image bounds
        h, w = image.shape[:2]
        landmarks = np.clip(landmarks_points, [0, 0], [w-1, h-1])
        
        return landmarks.astype(np.float32)
    
    def create_face_filter(self, face_images: List[np.ndarray], 
                          all_landmarks: List[np.ndarray]) -> Dict:
        """
        Create a face transformation filter from multiple source images
        
        Args:
            face_images: List of face images to extract features from
            all_landmarks: List of facial landmarks for each image
        
        Returns:
            Filter profile containing source face data for morphing
        """
        valid_faces = []
        valid_landmarks = []
        
        for img, landmarks in zip(face_images, all_landmarks):
            if landmarks is not None and len(landmarks) > 0:
                valid_faces.append(img)
                valid_landmarks.append(landmarks)
        
        if not valid_faces:
            raise ValueError("No valid faces with landmarks found")
        
        # Average the landmarks from all source faces
        avg_landmarks = np.mean([lm.astype(np.float32) for lm in valid_landmarks], axis=0)
        
        # Use first face as reference (or average)
        reference_face = valid_faces[0]
        
        # Create Delaunay triangulation on average landmarks
        hull = cv2.convexHull(np.array(avg_landmarks, dtype=np.int32))
        delaunay = Delaunay(avg_landmarks)
        
        return {
            'landmarks': avg_landmarks.tolist(),
            'delaunay_indices': delaunay.simplices.tolist(),
            'hull': hull.tolist(),
            'reference_shape': list(reference_face.shape),
            'num_landmarks': len(avg_landmarks)
        }
    
    def apply_face_transform(self, target_image: np.ndarray, 
                            target_landmarks: np.ndarray,
                            filter_profile: Dict, 
                            intensity: float = 0.8,
                            face_bbox: Tuple = None) -> np.ndarray:
        """
        Apply OPTIMIZED face transformation to target image
        Morphs target face to match the filter face structure
        
        Args:
            target_image: Target face region image to transform
            target_landmarks: Facial landmarks from full frame
            filter_profile: Filter profile with source face data
            intensity: Blending intensity (0.0 to 1.0)
            face_bbox: (x1, y1, x2, y2) bounding box of face in original frame
        
        Returns:
            Transformed face image
        """
        if target_landmarks is None or len(target_landmarks) == 0:
            return target_image
        
        if len(filter_profile.get('landmarks', [])) == 0:
            return target_image
        
        try:
            h, w = target_image.shape[:2]
            result = target_image.copy().astype(np.float32)
            
            source_landmarks = np.array(filter_profile['landmarks'], dtype=np.float32)
            target_landmarks = target_landmarks.astype(np.float32)
            
            # Step 1: Adjust target landmarks to be relative to face region AND clip to valid range
            if face_bbox is not None:
                x1, y1, x2, y2 = face_bbox
                adjusted_landmarks = target_landmarks.copy()
                adjusted_landmarks[:, 0] -= x1  # Subtract x offset
                adjusted_landmarks[:, 1] -= y1  # Subtract y offset
                # Clip negative values to 0
                adjusted_landmarks = np.maximum(adjusted_landmarks, 0)
                target_landmarks = adjusted_landmarks
            
            # Step 2: Ensure same landmark count
            if len(target_landmarks) != len(source_landmarks):
                target_landmarks = self._resample_landmarks(
                    target_landmarks, len(source_landmarks)
                )
            
            # Step 3: SCALE source landmarks to match target image size
            # Calculate bounding boxes of landmarks
            src_bbox = self._get_landmark_bbox(source_landmarks)
            tgt_bbox = self._get_landmark_bbox(target_landmarks)
            
            # Calculate scale factors
            src_width = src_bbox[2] - src_bbox[0]
            src_height = src_bbox[3] - src_bbox[1]
            tgt_width = tgt_bbox[2] - tgt_bbox[0]
            tgt_height = tgt_bbox[3] - tgt_bbox[1]
            
            if src_width > 0 and src_height > 0 and tgt_width > 0 and tgt_height > 0:
                scale_x = tgt_width / src_width
                scale_y = tgt_height / src_height
                
                # Scale and translate source landmarks to match target
                scaled_source = source_landmarks.copy()
                scaled_source[:, 0] = (source_landmarks[:, 0] - src_bbox[0]) * scale_x + tgt_bbox[0]
                scaled_source[:, 1] = (source_landmarks[:, 1] - src_bbox[1]) * scale_y + tgt_bbox[1]
                source_landmarks = scaled_source
            
            # Step 4: Get Delaunay triangulation
            delaunay_indices = np.array(filter_profile.get('delaunay_indices', []))
            if len(delaunay_indices) == 0:
                return target_image
            
            # Step 5: Process triangles (use MORE triangles for better coverage)
            max_triangles = min(len(delaunay_indices), 500)  # Increased from 300 for fuller coverage
            triangles_processed = 0
            triangles_skipped = 0
            
            for idx, simplex in enumerate(delaunay_indices[:max_triangles]):
                try:
                    # Get source and target triangle vertices
                    src_pts = source_landmarks[simplex[:3]].astype(np.float32)
                    dst_pts = target_landmarks[simplex[:3]].astype(np.float32)
                    
                    # Skip if points are invalid
                    if (np.any(np.isnan(src_pts)) or np.any(np.isnan(dst_pts))):
                        triangles_skipped += 1
                        continue
                    
                    # Relax bounds checking - allow points slightly outside image
                    # (OpenCV will handle this gracefully)
                    if (np.any(src_pts < -100) or np.any(src_pts > [w + 100, h + 100]) or
                        np.any(dst_pts < -100) or np.any(dst_pts > [w + 100, h + 100])):
                        triangles_skipped += 1
                        continue
                    
                    # Calculate affine transformation
                    affine_matrix = cv2.getAffineTransform(src_pts, dst_pts)
                    
                    # Create mask for this triangle
                    mask = np.zeros((h, w), dtype=np.uint8)
                    triangle_pts = dst_pts.astype(np.int32).reshape((-1, 1, 2))
                    cv2.drawContours(
                        mask, 
                        [triangle_pts], 
                        0, 
                        255, 
                        -1,
                        lineType=cv2.LINE_AA
                    )
                    
                    # Warp target image using transformation
                    warped = cv2.warpAffine(
                        target_image.astype(np.float32),
                        affine_matrix,
                        (w, h),
                        flags=cv2.INTER_LINEAR,
                        borderMode=cv2.BORDER_REFLECT
                    )
                    
                    # Blend using triangle mask
                    mask_3ch = mask[:,:,np.newaxis].astype(np.float32) / 255.0
                    blend_strength = intensity  # Full intensity blending for visible effect
                    result = result * (1 - mask_3ch * blend_strength) + warped * (mask_3ch * blend_strength)
                    triangles_processed += 1
                
                except Exception as e:
                    # Skip problematic triangles silently
                    triangles_skipped += 1
                    continue
            
            # Only print debug info occasionally
            import random
            if random.random() < 0.1:  # Print 10% of frames
                print(f"DEBUG: Processed {triangles_processed} triangles, skipped {triangles_skipped}")
            
            # Step 6: Final blend with original for natural look
            result_uint8 = np.clip(result, 0, 255).astype(np.uint8)
            final = cv2.addWeighted(
                result_uint8, intensity,  # Full intensity for visible morphing
                target_image, 1.0 - intensity,
                0
            )
            
            return final
        
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
            return target_image
    
    def _get_landmark_bbox(self, landmarks: np.ndarray) -> Tuple:
        """Get bounding box of landmarks as (x_min, y_min, x_max, y_max)"""
        if len(landmarks) == 0:
            return (0, 0, 1, 1)
        return (
            float(np.min(landmarks[:, 0])),
            float(np.min(landmarks[:, 1])),
            float(np.max(landmarks[:, 0])),
            float(np.max(landmarks[:, 1]))
        )
    
    def _resample_landmarks(self, landmarks: np.ndarray, target_count: int) -> np.ndarray:
        """Resample landmarks to match target count"""
        if len(landmarks) == target_count:
            return landmarks
        
        # Use linear interpolation to resample
        old_indices = np.linspace(0, len(landmarks) - 1, len(landmarks))
        new_indices = np.linspace(0, len(landmarks) - 1, target_count)
        
        resampled = np.zeros((target_count, 2), dtype=np.float32)
        for i in range(2):
            resampled[:, i] = np.interp(
                new_indices, old_indices, landmarks[:, i]
            )
        
        return resampled
    
    def _match_skin_tone(self, result: np.ndarray, target: np.ndarray, 
                        intensity: float) -> np.ndarray:
        """Match skin tone between result and target"""
        # Convert to LAB color space for better color matching
        result_lab = cv2.cvtColor(result.astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
        target_lab = cv2.cvtColor(target.astype(np.uint8), cv2.COLOR_BGR2LAB).astype(np.float32)
        
        # Calculate mean color for central region (face area)
        h, w = result.shape[:2]
        face_region = slice(h//4, 3*h//4), slice(w//4, 3*w//4)
        
        result_mean = np.mean(result_lab[face_region], axis=(0, 1))
        target_mean = np.mean(target_lab[face_region], axis=(0, 1))
        
        # Adjust result color towards target
        color_diff = target_mean - result_mean
        result_lab = result_lab + color_diff * intensity * 0.3
        
        # Convert back to BGR
        result_lab = np.clip(result_lab, 0, 255).astype(np.uint8)
        result_bgr = cv2.cvtColor(result_lab, cv2.COLOR_LAB2BGR)
        
        return result_bgr.astype(np.float32)
    
    def _color_correct(self, result: np.ndarray, target: np.ndarray,
                      intensity: float) -> np.ndarray:
        """Apply color correction between images"""
        # Gentle color blending
        result_uint8 = np.clip(result, 0, 255).astype(np.uint8)
        
        # Blend result and target colors
        blended = cv2.addWeighted(
            result_uint8, 1 - intensity * 0.2,
            target, intensity * 0.2,
            0
        )
        
        return blended.astype(np.float32)
    
    def create_blank_filter(self) -> Dict:
        """Create a blank filter profile (no transformation)"""
        return {
            'landmarks': [],
            'delaunay_indices': [],
            'hull': [],
            'reference_shape': [1, 1, 3],
            'num_landmarks': 0
        }
