#!/usr/bin/env python3
"""Debug face transformation with actual camera landmarks"""
import sys
sys.path.insert(0, ".")

import numpy as np
import cv2
from src.core.face_detector import FaceDetector
from src.filters.face_transformer import FaceTransformer
from src.filters.filter_manager import FilterManager

print("=" * 60)
print("FACE TRANSFORMATION DEBUG")
print("=" * 60)

# Initialize components
detector = FaceDetector()
transformer = FaceTransformer()
fm = FilterManager()

# Load filter
filter_data = fm.load_filter("Pratham")
print(f"\n✓ Filter loaded: Pratham")
print(f"  - Landmarks: {len(filter_data.get('landmarks', []))}")
print(f"  - Delaunay triangles: {len(filter_data.get('delaunay_indices', []))}")

# Create a test image (simulating camera feed)
test_image = np.zeros((480, 640, 3), dtype=np.uint8)

# Add a simple face pattern for testing
cv2.rectangle(test_image, (150, 100), (490, 400), (100, 150, 200), -1)  # Face region
cv2.circle(test_image, (200, 180), 30, (50, 100, 150), -1)  # Left eye
cv2.circle(test_image, (440, 180), 30, (50, 100, 150), -1)  # Right eye
cv2.circle(test_image, (320, 300), 40, (180, 120, 100), -1)  # Nose/mouth area

print(f"\n✓ Test image created: {test_image.shape}")

# Detect faces in test image
faces = detector.detect_faces(test_image)
print(f"\n✓ Faces detected: {len(faces)}")

if len(faces) > 0:
    face = faces[0]
    x, y, w, h = face['bbox']
    x1, y1 = max(0, x), max(0, y)
    x2, y2 = min(test_image.shape[1], x + w), min(test_image.shape[0], y + h)
    
    print(f"  - Face bbox: ({x1}, {y1}) to ({x2}, {y2})")
    print(f"  - Face size: {x2-x1}x{y2-y1}")
    
    # Get landmarks
    landmarks = detector.get_face_landmarks(test_image)
    
    if landmarks is not None:
        print(f"\n✓ Landmarks extracted: {len(landmarks)} points")
        print(f"  - X range: {landmarks[:, 0].min():.1f} to {landmarks[:, 0].max():.1f}")
        print(f"  - Y range: {landmarks[:, 1].min():.1f} to {landmarks[:, 1].max():.1f}")
        
        # Extract face region
        face_region = test_image[y1:y2, x1:x2].copy()
        print(f"\n✓ Face region extracted: {face_region.shape}")
        
        # Apply transformation
        print(f"\n✓ Applying transformation...")
        print(f"  - Filter intensity: 0.8")
        print(f"  - Face bbox for adjustment: ({x1}, {y1}, {x2}, {y2})")
        
        try:
            result = transformer.apply_face_transform(
                face_region,
                landmarks,
                filter_data,
                intensity=0.8,
                face_bbox=(x1, y1, x2, y2)
            )
            
            print(f"\n✓ Transformation completed!")
            print(f"  - Result shape: {result.shape}")
            print(f"  - Result dtype: {result.dtype}")
            
            # Check if transformation was applied
            diff = np.abs(result.astype(float) - face_region.astype(float))
            mean_diff = diff.mean()
            max_diff = diff.max()
            
            print(f"  - Mean pixel difference: {mean_diff:.2f}")
            print(f"  - Max pixel difference: {max_diff:.2f}")
            
            if mean_diff > 0.5:
                print(f"\n✓ TRANSFORMATION APPLIED - Face should look different!")
            else:
                print(f"\n✗ WARNING: Minimal transformation - check coordinates or landmarks")
                
        except Exception as e:
            print(f"\n✗ ERROR during transformation: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"\n✗ No landmarks detected")
else:
    print(f"\n✗ No faces detected in test image")

print("\n" + "=" * 60)
