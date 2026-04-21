# Linux/Ubuntu Troubleshooting Guide

## Common Ubuntu/Linux Issues & Solutions

### 1. Camera Permission Issues

**Problem**: "Cannot open camera" or "Camera not found"

**Solution for Ubuntu/Debian**:
```bash
# Add current user to video group
sudo usermod -a -G video $USER

# Apply group changes (choose one):
# Option 1: Log out and log back in

# Option 2: Use newgrp command
newgrp video

# Verify camera access
ls -la /dev/video*
```

**For Snap-based Apps**:
If you're running this in a Snap environment:
```bash
sudo snap connect face-filter-app:camera
```

---

### 2. OpenCV/MediaPipe Issues

**Problem**: "ImportError: libGL.so.1" or OpenCV fails

**Solution**:
```bash
# Install required libraries
sudo apt update
sudo apt install -y libgl1-mesa-glx libsm6 libxext6

# Reinstall OpenCV
pip install --force-reinstall opencv-python opencv-contrib-python
```

**For headless servers** (no GUI):
```bash
sudo apt install xvfb python3-tk
```

---

### 3. GUI Not Appearing (PyQt5)

**Problem**: App runs but no window appears

**Solution - Missing Qt5 libraries**:
```bash
# Install Qt5
sudo apt install -y qt5-qmake qtbase5-dev

# Or complete Qt5
sudo apt install -y qt5-default
```

**For Wayland sessions** (newer Ubuntu):
```bash
# Try running with XCB backend
QT_QPA_PLATFORM=xcb python3 main.py

# Or switch to X11 session temporarily
```

---

### 4. Audio in Processed Videos

**Problem**: Processed videos lose audio

**Solution** - Install ffmpeg:
```bash
sudo apt install ffmpeg

# Then reinstall dependencies
pip install moviepy
```

---

### 5. Performance Issues on Ubuntu

**Problem**: Slow video processing or lag in real-time

**Solutions**:
```bash
# Check available system resources
free -h                    # RAM
ps aux | grep python       # Running processes

# Close unnecessary apps
sudo systemctl stop bluetooth

# Increase process priority
nice -n -10 python3 main.py
```

**For better GPU support**:
```bash
# If you have NVIDIA GPU
sudo apt install nvidia-cuda-toolkit

# Then install CUDA-enabled versions
pip install opencv-contrib-python-headless
```

---

### 6. Virtual Environment Issues

**Problem**: "command not found: python3" or venv errors

**Solution**:
```bash
# Install Python3 and venv
sudo apt update
sudo apt install -y python3 python3-pip python3-venv

# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate

# Verify
which python
```

---

### 7. Dependency Conflicts

**Problem**: "pip install" fails with conflicts

**Solution**:
```bash
# Create fresh virtual environment
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Install with specific versions
pip install -r requirements.txt --no-cache-dir
```

---

### 8. Screen Resolution/Scaling Issues

**Problem**: Window too small/too large or text is blurry

**Solution**:
```bash
# For high DPI screens (4K)
QT_AUTO_SCREEN_SCALE_FACTOR=1 python3 main.py

# Or modify in main_window.py:
# Add this before creating QApplication:
os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
```

---

### 9. Webcam Multiple Instances

**Problem**: "Camera already in use" error

**Solution**:
```bash
# Check what's using camera
sudo lsof /dev/video*

# Kill conflicting processes
sudo killall cheese      # GNOME Camera
sudo killall firefox     # If Firefox accessed camera
sudo killall skype       # etc.

# Or restart the service
sudo systemctl restart systemd-logind
```

---

### 10. Audio/Video Codec Issues

**Problem**: "Cannot write codec" when processing video

**Solution**:
```bash
# Install multimedia codecs
sudo apt install -y libavcodec-extra ffmpeg

# Check available codecs
ffmpeg -codecs | grep h264

# Install libx264
sudo apt install -y libx264-dev
```

---

## System-Specific Setup

### For Ubuntu 20.04 LTS
```bash
# Tested working setup
sudo apt update
sudo apt install -y python3.8 python3.8-venv python3-pip
python3.8 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### For Ubuntu 22.04 LTS
```bash
# Same as above, Python 3.10 included by default
sudo apt update
sudo apt install -y python3-venv python3-pip
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### For Linux Mint
```bash
# Mint is Debian-based, same instructions as Ubuntu
# Plus: ensure Cinnamon doesn't interfere with camera access
gsettings set org.cinnamon.settings-daemon.plugins.power lid-close-ac-action 'nothing'
```

### For Fedora/RHEL
```bash
# Install dependencies
sudo dnf install -y python3 python3-pip python3-devel

# Install system packages
sudo dnf install -y opencv-devel qt5-qtbase-devel

# Create venv and install
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Debugging Commands

### Check your Ubuntu version
```bash
lsb_release -a
uname -a
```

### List installed Python packages
```bash
pip list | grep -E "PyQt|OpenCV|mediapipe"
```

### Test camera access
```bash
python3 -c "import cv2; print(cv2.VideoCapture(0).isOpened())"
```

### Test all dependencies
```bash
python3 -c "
import cv2
import mediapipe
import PyQt5
import numpy
import scipy
print('✓ All dependencies OK!')
"
```

### Check graphics/display info
```bash
# GPU info
lspci | grep -i vga
glxinfo | grep "OpenGL"

# Display server
echo $DISPLAY
echo $XDG_SESSION_TYPE  # X11 or wayland
```

---

## Advanced Optimization for Ubuntu

### Enable GPU Acceleration
```bash
# For NVIDIA
sudo apt install nvidia-driver-535

# For Intel
sudo apt install intel-gpu-tools

# Verify
nvidia-smi  # NVIDIA
glxinfo | grep -i vendor  # Intel
```

### Disable unnecessary services
```bash
# Disable Bluetooth
sudo systemctl disable bluetooth

# Disable automatic updates during use
sudo systemctl stop unattended-upgrades
```

### Optimize thread usage
Edit `config.py`:
```python
MAX_THREADS = 8  # Match your CPU cores
```

---

## Getting Help

If issues persist:
1. Run with verbose output: `python3 main.py -v`
2. Check system logs: `journalctl -xe`
3. Test with minimal setup: Just camera feed first
4. Report specific error messages to help debug

---

**Good Luck! 🍀**
