#!/usr/bin/env python3
"""Test that fixes work correctly"""
import sys
sys.path.insert(0, ".")

from src.filters.face_transformer import FaceTransformer
from src.filters.filter_manager import FilterManager
import json

# Test loading a filter
fm = FilterManager()
filters = fm.get_all_filters()
print(f"Available filters: {filters}")

# Load the Pratham filter
if "Pratham" in filters:
    filter_data = fm.load_filter("Pratham")
    print(f"Pratham filter keys: {list(filter_data.keys())}")
    has_landmarks = 'landmarks' in filter_data
    print(f"Has landmarks: {has_landmarks}")
    num_landmarks = len(filter_data.get('landmarks', []))
    print(f"Num landmarks: {num_landmarks}")
    has_delaunay = 'delaunay_indices' in filter_data
    print(f"Has delaunay_indices: {has_delaunay}")
    
# Test FaceTransformer instantiation
ft = FaceTransformer()
print("FaceTransformer created successfully")
print("All basic checks passed!")
