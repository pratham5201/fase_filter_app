"""
Configuration file for Face Filter App
"""

# Camera Settings
CAMERA_ID = 0  # Default camera (0 = first camera/built-in)
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# Face Detection
FACE_DETECTION_CONFIDENCE = 0.5
MIN_FACE_SIZE = 300  # Minimum pixels for detection

# Filter Settings
DEFAULT_FILTER_INTENSITY = 0.8
MAX_FILTER_INTENSITY = 1.0
MIN_FILTER_INTENSITY = 0.0

# Photo Capture
PHOTOS_PER_FILTER = 5
PHOTO_FORMAT = "jpg"

# Video Processing
VIDEO_OUTPUT_CODEC = "mp4v"
VIDEO_QUALITY = 1.0

# UI Settings
WINDOW_WIDTH = 1400
WINDOW_HEIGHT = 900
THEME = "default"  # Can be extended for different themes

# Data Paths
DATA_DIR = "data"
FILTERS_DIR = "data/filters"
SAMPLE_PHOTOS_DIR = "data/sample_photos"
TEMP_DIR = "/tmp"

# Performance
ENABLE_GPU = False  # Set to True if CUDA is available
MAX_THREADS = 4
FRAME_SKIP = 0  # Process every Nth frame (0 = process all)

# Logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FILE = None  # Set to file path to enable logging
