#!/usr/bin/env python3
"""Debug script to check landmark scaling"""
import sys
sys.path.insert(0, ".")

import numpy as np
from src.filters.filter_manager import FilterManager

# Load filter
fm = FilterManager()
filter_data = fm.load_filter("Pratham")

landmarks = np.array(filter_data['landmarks'])
print(f"Filter landmarks shape: {landmarks.shape}")
print(f"X range: {landmarks[:, 0].min():.1f} to {landmarks[:, 0].max():.1f}")
print(f"Y range: {landmarks[:, 1].min():.1f} to {landmarks[:, 1].max():.1f}")

# Estimate the photo size
x_range = landmarks[:, 0].max() - landmarks[:, 0].min()
y_range = landmarks[:, 1].max() - landmarks[:, 1].min()
aspect_ratio = x_range / y_range

print(f"Estimated photo width: ~{landmarks[:, 0].max():.0f}px")
print(f"Estimated photo height: ~{landmarks[:, 1].max():.0f}px")
print(f"Aspect ratio: {aspect_ratio:.2f}")

# Typical camera resolution
print("\nTypical camera resolutions:")
print("- VGA: 640x480")
print("- HD: 1280x720")
print("- Full HD: 1920x1080")

print("\nLandmarks in filter are absolute coordinates from original photo")
print("Camera feed will have different resolution - need scaling!")
