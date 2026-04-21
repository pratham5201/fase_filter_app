# Face Filter App - Architecture & Technical Documentation

## System Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    USER INTERFACE LAYER                      │
│                   (PyQt5 Main Window)                        │
│  ┌──────────────┬──────────────┬──────────────┬────────────┐ │
│  │   Create     │    Apply     │   Process    │   Manage   │ │
│  │   Filter     │    Filter    │   Video      │   Filters  │ │
│  └──────────────┴──────────────┴──────────────┴────────────┘ │
└─────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  PROCESSING LAYER                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Filter Processor: Create & Apply Filters            │   │
│  │  - Color analysis (skin tone, makeup)                │   │
│  │  - Lighting adjustment                               │   │
│  │  - Texture smoothing                                 │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Face Detector: Detect & Analyze Faces              │   │
│  │  - MediaPipe face detection                          │   │
│  │  - Facial landmarks (468 points)                     │   │
│  │  - Face region extraction                            │   │
│  └──────────────────────────────────────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Camera Manager: Real-time Input                     │   │
│  │  - Camera stream handling                            │   │
│  │  - Video file processing                             │   │
│  │  - Frame capture                                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                  STORAGE LAYER                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Filter Manager: Persistence & Management            │   │
│  │  - Save/load filter profiles (JSON)                  │   │
│  │  - Default filter configuration                      │   │
│  │  - Filter indexing and listing                       │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   DATA STORAGE                               │
│  data/                                                       │
│  ├── filters/           (JSON filter profiles)              │
│  └── sample_photos/     (Temp captured images)              │
└─────────────────────────────────────────────────────────────┘
```

---

## Module Dependencies

```
main.py
  └── src/ui/main_window.py
      ├── src/core/face_detector.py
      │   └── mediapipe (face detection)
      │
      ├── src/filters/filter_processor.py
      │   ├── opencv (image processing)
      │   ├── numpy (numerical operations)
      │   └── scipy (mathematical functions)
      │
      ├── src/core/camera_manager.py
      │   ├── opencv (camera/video operations)
      │   └── threading (parallel processing)
      │
      └── src/filters/filter_manager.py
          ├── json (file persistence)
          └── pathlib (file system access)
```

---

## Data Flow Diagrams

### 1. Filter Creation Flow

```
User Photos (JPG/PNG)
        │
        ▼
  [Face Detector]
  - Detect faces
  - Extract regions
        │
        ▼
[Filter Analyzer]
  - Extract skin tone
  - Extract color profile
  - Extract lighting info
  - Estimate makeup intensity
  - Extract texture features
        │
        ▼
[Average Features] (from multiple photos)
        │
        ▼
[Filter Profile] (JSON)
        │
        ▼
[Filter Manager]
  - Save to JSON file
  - Update index
        │
        ▼
data/filters/{filter_name}.json
```

### 2. Real-time Filter Application Flow

```
Camera (Live Feed)
        │
        ▼
[Camera Manager]
  - Capture frames
  - Threading
        │
        ▼
[Face Detector]
  - Detect faces
  - Get landmarks
        │
        ▼
[Filter Processor]
  - Load saved filter
  - Apply transformations
  - Adjust intensity
        │
        ▼
[Processed Frame]
        │
        ▼
[PyQt5 UI]
  - Display in real-time
  - Update at 30 FPS
```

### 3. Video Processing Flow

```
Input Video File
        │
        ▼
[Video Processor]
  - Open video
  - Read frames
  - Get codec/fps
        │
        ▼
[For Each Frame]
  - Detect faces
  - Apply filter
  - Write to output
        │
        ▼
Output Video File (MP4)
```

---

## Filter Profile Structure

Each filter is saved as a JSON file:

```json
{
  "name": "john_filter",
  "profile": {
    "skin_tone": {
      "hsv": [15.5, 120.3, 200.2],
      "bgr": [145, 120, 100]
    },
    "color_profile": {
      "L": {"mean": 50.5, "std": 15.2},
      "a": {"mean": 5.3, "std": 8.1},
      "b": {"mean": 12.1, "std": 6.5}
    },
    "lighting": {
      "brightness": 120.5,
      "contrast": 45.3
    },
    "makeup_intensity": {
      "saturation_mean": 95.5,
      "saturation_std": 20.3
    },
    "texture": {
      "smoothness": 0.85
    }
  }
}
```

---

## Face Detection Technology

### MediaPipe Face Detection
- Lightweight and fast (~100ms per frame)
- Works with 1+ faces
- Returns bounding boxes and confidence scores

### MediaPipe Face Mesh
- 468 facial landmarks
- Provides precise face feature positions
- Used for detailed analysis

**Alternative Technologies** (not currently used):
- dlib (more robust but slower)
- MTCNN (better accuracy but higher overhead)
- TensorFlow Face Detection

---

## Filter Processing Steps

### 1. Skin Tone Adjustment
```
Input Frame (BGR)
    ↓
Convert to HSV
    ↓
Extract H,S,V channels
    ↓
Adjust toward target values
    ↓
Convert back to BGR
```

### 2. Lighting Adjustment
```
Extract brightness from LAB
    ↓
Compare with target
    ↓
Apply brightness delta
    ↓
Normalize values
```

### 3. Makeup Effect (Saturation)
```
Extract saturation channel
    ↓
Increase saturation factor
    ↓
Apply bilaterally filtered smoothing
    ↓
Blend with original (intensity control)
```

### 4. Texture Processing
```
Calculate edge energy
    ↓
Apply bilateral filter (smoothing)
    ↓
Weighted blend with original
    ↓
Result: Natural skin smoothing
```

---

## Performance Characteristics

### Real-time Performance (Live Camera)

| Operation | Time (ms) | CPU | GPU |
|-----------|-----------|-----|-----|
| Face Detection | 30-50 | ✓ | - |
| Landmark Detection | 20-40 | ✓ | - |
| Filter Processing | 10-20 | ✓ | ✓ |
| UI Rendering | 5-10 | - | ✓ |
| **Total Frame Time** | **60-120** | - | - |
| **FPS Achieved** | **8-16** | - | - |

*Note: 30 FPS target on modern systems*

### Video Processing Performance

| Factor | Impact |
|--------|--------|
| Video Resolution | ~2x slower per 2x pixels |
| Filter Intensity | Minimal impact (~2-5%) |
| Video Duration | Linear (2 min = 2x time) |
| System CPU | Major factor (4-core vs 8-core) |

**Estimated Speed**: 
- 1 minute video: 3-5 minutes processing (8-core CPU)
- 10 minute video: 30-50 minutes processing

---

## Configuration & Customization

### Key Configuration Points

1. **Camera Settings** (`config.py`):
```python
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30
```

2. **Filter Settings** (`config.py`):
```python
DEFAULT_FILTER_INTENSITY = 0.8
```

3. **Face Detection** (`src/core/face_detector.py`):
```python
min_detection_confidence=0.5  # Lower = more detections
```

4. **Number of Photos** (`src/ui/main_window.py`):
```python
self.max_photos = 5  # Change to require more photos
```

---

## Extension Points

### Add New Filter Type

1. Create new method in `FilterProcessor`:
```python
def apply_artistic_filter(self, image, profile):
    # Your custom filter logic
    return filtered_image
```

2. Call from `apply_filter()`:
```python
if filter_type == "artistic":
    result = self._apply_artistic_filter(image, profile, intensity)
```

### Add New UI Tab

1. Create new tab method in `FaceFilterApp`:
```python
def my_new_feature_tab(self) -> QWidget:
    widget = QWidget()
    layout = QVBoxLayout()
    # Add widgets
    widget.setLayout(layout)
    return widget
```

2. Add to tabs:
```python
tabs.addTab(self.my_new_feature_tab(), "My Feature")
```

### Add GPU Support

1. Install CUDA:
```bash
pip install torch  # or tensorflow-gpu
```

2. Modify `filter_processor.py` to use GPU:
```python
import torch
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
```

---

## Testing & Debugging

### Enable Debug Mode
```bash
# Add to main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Test Individual Components

```python
# Test face detection
from src.core.face_detector import FaceDetector
detector = FaceDetector()
faces = detector.detect_faces(image)

# Test filter processor
from src.filters.filter_processor import FilterProcessor
processor = FilterProcessor()
features = processor.analyzer.analyze_face(image)

# Test filter manager
from src.filters.filter_manager import FilterManager
manager = FilterManager()
all_filters = manager.get_all_filters()
```

---

## Future Architecture Enhancements

### Planned Improvements

1. **GPU Acceleration**
   - CUDA support for faster processing
   - Real-time 60+ FPS capability

2. **Multi-face Support**
   - Handle multiple faces per frame
   - Individual filter per face

3. **ML-based Filters**
   - Deep learning for advanced effects
   - Automatic style transfer

4. **Filter Marketplace**
   - Share filters online
   - Download community filters

5. **Recording Module**
   - Direct video recording with filter
   - Real-time MP4 export

6. **Mobile Companion**
   - Remote camera access
   - Cloud filter sync

---

## Code Quality & Best Practices

### Current Implementation

- ✅ Modular architecture (separation of concerns)
- ✅ Type hints for functions
- ✅ Documentation strings
- ✅ Error handling
- ✅ Threading for responsiveness
- ✅ Resource cleanup

### Recommended Improvements

- [ ] Unit tests (pytest)
- [ ] Integration tests
- [ ] Performance profiling
- [ ] Memory leak detection
- [ ] Async operations
- [ ] Configuration file validation

---

## Troubleshooting Architecture

```
Issue → Check Layer
  ├─ UI doesn't show
  │  └─ PyQt5 layer → Check imports & display server
  ├─ Filter not applied
  │  └─ Processing layer → Check detect_faces() result
  ├─ Camera not working
  │  └─ Input layer → Check /dev/video* permissions
  ├─ Filter not saving
  │  └─ Storage layer → Check data/filters/ permissions
  └─ Performance issues
     └─ All layers → Profile with cProfile
```

---

## Memory Usage & Optimization

### Typical Memory Profile

- Application base: ~150-200 MB (Python + PyQt5)
- Per frame buffer: ~3-4 MB (640x480)
- Filter profiles: ~10-20 KB each
- Landmark data: ~1-2 KB per face

**Optimization Tips**:
1. Release camera resources when not in use
2. Limit concurrent processing operations
3. Use smaller resolution for preview
4. Clear old temporary photos

---

## Security Considerations

### Data Privacy

1. All filters stored locally (no cloud upload)
2. Photos not retained after processing
3. Camera access controlled by OS permissions
4. No telemetry or tracking

### Best Practices

- Never share filter files if they contain sensitive biometric data
- Clear temporary files: `rm -rf /tmp/face_filter_photo_*`
- Run with minimal required permissions

---

**For more details, see specific module documentation in their source files.**
