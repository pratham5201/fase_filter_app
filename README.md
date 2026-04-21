# Face Filter App - Real-time AR Face Filters

A powerful desktop application for creating and applying AR face filters in real-time. Create custom face filters from your own photos and apply them to live camera feeds, videos, or pre-recorded content!

## Features

✨ **Create Custom Filters**
- Capture photos of any face from your camera
- Or upload existing photos
- Automatic facial analysis extracts skin tone, makeup, lighting, and texture characteristics
- Filters are created by averaging features from multiple photos

🎥 **Real-Time Camera Application**
- Apply filters instantly to live camera feed
- Adjust filter intensity with slider (0-100%)
- Set any filter as default for automatic application on startup
- Face detection and tracking in real-time

🎬 **Video Processing**
- Apply filters to entire videos frame-by-frame
- Maintain original video quality and fps
- Support for multiple video formats (MP4, AVI, MOV, MKV)

📁 **Filter Management**
- Save and organize unlimited filters
- Delete filters you no longer need
- Set default filter for quick access
- All filters stored locally in JSON format

## System Requirements

- **OS**: Ubuntu 18.04+ (Linux)
- **Python**: 3.7+
- **Webcam**: Required for real-time features
- **RAM**: Minimum 4GB recommended
- **GPU**: Optional (for better performance)

## Installation

### 1. Clone or Download the Project

```bash
cd /home/developer/own/face_filter_app
```

### 2. Create Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

If you face issues with OpenCV, try:
```bash
pip install --upgrade pip
pip install opencv-python opencv-contrib-python --no-binary opencv-python opencv-contrib-python
```

### 4. Run the Application

```bash
python3 main.py
```

Or make it executable:
```bash
chmod +x main.py
./main.py
```

## Usage Guide

### Tab 1: Create Filter

1. **Capture Photos from Camera**
   - Click "Capture Photos from Camera"
   - Position your face in good lighting
   - Click "Capture Photo" 5 times at different angles
   - Click "Done" when finished

   *OR*

   **Upload Photos**
   - Click "Upload Photos"
   - Select 3-5 photos of the same face from your computer
   - Photos should have good lighting and clear face visibility

2. **Create Filter**
   - Enter a name for your filter (e.g., "John_Filter", "Natural_Makeup")
   - Click "Create & Save Filter"
   - Filter will be analyzed and saved automatically

### Tab 2: Apply Filter (Live)

1. **Start Camera**
   - Click "Start Camera" to access your webcam
   - Your camera feed appears on the left

2. **Select Filter**
   - Choose a filter from the dropdown menu
   - Filter applies in real-time to detected faces

3. **Adjust Intensity**
   - Use the slider to adjust how strongly the filter is applied
   - 0% = no filter effect, 100% = full filter effect
   - Recommended: 70-90% for natural look

4. **Set as Default** (Optional)
   - Click "Set as Default Filter" to make this your startup filter
   - Next time you open the app and start the camera, this filter auto-applies

5. **Stop Camera**
   - Click "Stop Camera" when done

### Tab 3: Process Video

1. **Select Video**
   - Click "Select Video" and choose a video file from your computer
   - Supports: MP4, AVI, MOV, MKV

2. **Choose Filter**
   - Select the filter you want to apply

3. **Adjust Intensity**
   - Set the filter strength

4. **Process**
   - Click "Process Video"
   - Choose where to save the output video
   - Processing will begin (may take a few minutes depending on video length)

5. **Done**
   - Processed video is saved to your chosen location

### Tab 4: Manage Filters

- **View All Filters**: See all saved filters
- **Delete Filter**: Remove unwanted filters
- **Refresh List**: Update the filter list

## Filter Technology

The app uses advanced computer vision techniques:

- **Face Detection**: MediaPipe Face Detection for accurate face localization
- **Facial Landmarks**: 468-point face mesh for detailed facial features
- **Color Analysis**: LAB color space analysis for accurate skin tone matching
- **Texture Analysis**: Edge detection for smoothness and makeup intensity
- **Real-time Processing**: Optimized for smooth 30 FPS camera streaming

## Filter Characteristics

Each filter captures:

- **Skin Tone**: HSV and BGR color information
- **Lighting**: Brightness and contrast characteristics
- **Makeup Intensity**: Saturation levels and makeup effects
- **Texture**: Smoothness, skin condition, and detail

## Folder Structure

```
face_filter_app/
├── main.py                 # Entry point
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── src/
│   ├── core/
│   │   ├── face_detector.py    # Face detection logic
│   │   └── camera_manager.py   # Camera and video handling
│   ├── filters/
│   │   ├── filter_processor.py # Filter creation and application
│   │   └── filter_manager.py   # Filter storage and management
│   └── ui/
│       └── main_window.py      # Main GUI application
└── data/
    ├── filters/           # Stored filter JSON files
    └── sample_photos/     # Temporary photo storage
```

## Troubleshooting

### Camera Not Working
```bash
# Check if camera is recognized
ls /dev/video*

# Grant camera permissions
sudo usermod -a -G video $USER
# Then log out and log back in
```

### Permission Denied
```bash
chmod +x main.py
```

### Import Errors
```bash
# Ensure venv is activated
source venv/bin/activate

# Reinstall dependencies
pip install --force-reinstall -r requirements.txt
```

### Slow Performance
- Close other applications
- Reduce camera resolution (modify in code)
- Use filter intensity 50-70% instead of 100%
- Ensure good lighting

### Video Processing Issues
```bash
# For video codec issues
pip install opencv-contrib-python
```

## Configuration

### Camera Resolution
Edit [src/core/camera_manager.py](src/core/camera_manager.py#L20) (lines 20-22):
```python
self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)   # Change from 640
self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)  # Change from 480
```

### Filter Intensity Defaults
Edit [src/ui/main_window.py](src/ui/main_window.py) to change default slider positions.

### Number of Photos for Filter Creation
Edit [src/ui/main_window.py](src/ui/main_window.py#L400) (line ~400):
```python
self.max_photos = 10  # Change from 5
```

## Advanced Features

### Command Line Usage (Future)

Future versions will support:
```bash
./main.py --camera           # Start with camera tab
./main.py --process video.mp4 --filter my_filter
./main.py --set-default my_filter
```

### Batch Processing

Save multiple videos and process them with the same filter for consistency.

## Performance Tips

1. **Use Good Lighting**: Filters work best in well-lit environments
2. **Clear Background**: Solid backgrounds work better than busy ones
3. **Face Size**: Keep face filling 30-70% of camera frame
4. **Multiple Angles**: Capture filter photos from different angles for better results
5. **Realistic Intensity**: 70-85% intensity usually looks most natural

## Limitations

- Single face per frame (detects first face in each frame)
- Requires minimum 300x300 pixel face in frame
- Video processing is CPU-intensive (GPU support coming soon)
- Real-time performance varies by system specs

## Future Enhancements

🚀 Planned features:
- [ ] GPU acceleration for video processing
- [ ] Multiple face support in single frame
- [ ] Advanced beauty filters
- [ ] Eye color change
- [ ] Beard/facial hair effects
- [ ] Custom sticker overlays
- [ ] Face morphing effects
- [ ] Recording directly to MP4
- [ ] Real-time export options
- [ ] Filter sharing and marketplace

## License

MIT License - Feel free to use and modify for personal projects

## Support & Issues

For bugs or feature requests, check the project repository.

## Credits

Built with:
- **MediaPipe**: Face detection and landmarks
- **OpenCV**: Image processing
- **PyQt5**: User interface
- **NumPy/SciPy**: Mathematical operations

---

**Enjoy creating your custom face filters! 🎉**
