#!/usr/bin/env python3
"""Test landmark scaling and transformation"""
import sys
sys.path.insert(0, ".")

import numpy as np
import cv2
from src.filters.face_transformer import FaceTransformer
from src.filters.filter_manager import FilterManager

# Load filter
fm = FilterManager()
filter_data = fm.load_filter("Pratham")

# Create transformer
ft = FaceTransformer()

# Create a realistic test scenario
# Camera resolution: 640x480
camera_h, camera_w = 480, 640
face_region_h, face_region_w = 200, 150  # Small face region

# Create test image
test_image = np.random.randint(100, 200, (face_region_h, face_region_w, 3), dtype=np.uint8)

# Create test landmarks (468 points in camera feed)
# These should be within camera bounds
camera_landmarks = np.zeros((468, 2), dtype=np.float32)
for i in range(468):
    camera_landmarks[i, 0] = np.random.uniform(50, 590)  # x in camera range
    camera_landmarks[i, 1] = np.random.uniform(50, 430)  # y in camera range

# Simulate face bbox (where face was detected in camera)
face_bbox = (100, 100, 250, 300)  # x1, y1, x2, y2

print("Test Setup:")
print(f"  Camera resolution: {camera_w}x{camera_h}")
print(f"  Face region size: {face_region_w}x{face_region_h}")
print(f"  Face bbox in camera: {face_bbox}")
print(f"  Camera landmarks: {len(camera_landmarks)} points")
print(f"  Filter landmarks: {len(filter_data['landmarks'])} points")

try:
    result = ft.apply_face_transform(
        test_image,
        camera_landmarks,
        filter_data,
        intensity=0.8,
        face_bbox=face_bbox
    )
    
    print("\nTransformation Result:")
    print(f"  Output shape: {result.shape}")
    print(f"  Output dtype: {result.dtype}")
    print(f"  Value range: {result.min()} to {result.max()}")
    
    # Check if transformation was applied
    diff = np.abs(result.astype(float) - test_image.astype(float)).mean()
    print(f"  Difference from original: {diff:.2f}")
    
    if diff > 1:
        print("\n✓ Transformation applied successfully!")
    else:
        print("\n⚠ Transformation seems minimal - check intensity or landmark ranges")
        
except Exception as e:
    print(f"\n✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
