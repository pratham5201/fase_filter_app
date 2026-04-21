#!/usr/bin/env python3
"""Test face transformation signature"""
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

# Create dummy test image and landmarks
test_image = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
test_landmarks = np.random.rand(468, 2) * 100  # 468 landmarks in 100x100 image

# Test that the method accepts the new face_bbox parameter
try:
    result = ft.apply_face_transform(
        test_image, 
        test_landmarks, 
        filter_data, 
        intensity=0.8,
        face_bbox=(10, 10, 90, 90)
    )
    print("apply_face_transform accepts face_bbox parameter: OK")
    print(f"Result shape: {result.shape}")
    print(f"Result dtype: {result.dtype}")
    print("Face transformation signature test PASSED!")
except TypeError as e:
    print(f"ERROR: Method signature issue: {e}")
except Exception as e:
    print(f"ERROR: {e}")
