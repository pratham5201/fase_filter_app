# Quick Start Guide - Face Filter App

## ⚡ 30 Second Setup

### Option 1: Automatic Installation (Recommended)

```bash
cd /home/developer/own/face_filter_app
chmod +x install.sh
./install.sh
./run.sh
```

### Option 2: Manual Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python3 main.py
```

---

## 🎬 First Time Users - Quick Workflow

### 1. **Create Your First Filter (2-3 minutes)**
   - Open the app → **Create Filter** tab
   - Click **Capture Photos from Camera**
   - Take 5 photos from different angles
   - Name your filter: `"MyFilter"` or `"Personal_Face"`
   - Click **Create & Save Filter**
   - ✅ Filter created!

### 2. **Apply Filter in Real-Time (1 minute)**
   - Go to **Apply Filter (Live)** tab
   - Click **Start Camera**
   - Select your filter from the dropdown
   - Adjust intensity slider to your preference
   - ✅ See your filter applied to your face in real-time!

### 3. **Set as Default (30 seconds)**
   - With your filter selected
   - Click **Set as Default Filter**
   - Next time you open the app, this filter auto-applies
   - ✅ Done! Camera will always use your filter!

---

## 🎥 Process Your First Video

1. Record or download a video (or use existing one)
2. Go to **Process Video** tab
3. Select video → Choose filter → Click **Process**
4. Wait for processing to complete
5. Your filtered video is ready! 🎬

---

## 📱 Create Filters for Others

**Person A (Create Filter):**
1. Create Filter tab → Capture 5 photos
2. Name: `"PersonA_Face"`
3. Save

**Person B (Use the Filter):**
1. Apply Filter tab
2. Select `"PersonA_Face"` from dropdown
3. Start camera and record/take photos
4. Your face now has Person A's filter applied! 🎭

---

## ⚙️ System Requirements Check

```bash
# Check Python version (need 3.7+)
python3 --version

# Check camera is available
ls /dev/video*

# If you get "command not found"
sudo apt update
sudo apt install python3 python3-pip
```

---

## 🚨 Troubleshooting

### "Camera not found"
```bash
# Grant camera permission
sudo usermod -a -G video $USER
# Log out and back in
```

### "ImportError: No module named 'PyQt5'"
```bash
# Make sure virtual environment is active
source venv/bin/activate
pip install -r requirements.txt
```

### Slow performance
- Use less filter intensity (70% instead of 100%)
- Close other applications
- Try reducing camera resolution in code

### "Permission denied" on shell scripts
```bash
chmod +x install.sh run.sh main.py
```

---

## 📁 Project Structure

```
face_filter_app/
├── main.py                 # Run this! 🎬
├── README.md              # Full documentation
├── requirements.txt       # Python packages
├── config.py             # Settings
├── install.sh            # Auto installer
├── run.sh               # Quick launcher
└── src/
    ├── core/            # Face detection, camera
    ├── filters/         # Filter creation/storage
    └── ui/             # Main GUI window
```

---

## 💡 Pro Tips

✅ **Best Lighting**: Use natural window light or bright indoor lighting
✅ **Best Angles**: Capture filter photos from front, left, right, up, down
✅ **Filter Intensity**: 70-85% looks most natural
✅ **Face Size**: Keep your face filling 30-70% of camera frame
✅ **Multiple Filters**: Create filters for different moods/occasions

---

## 🎯 Next Steps

1. ✅ Create your first filter
2. ✅ Apply it to live camera
3. ✅ Process a video
4. ✅ Set it as default
5. ✅ Create filters for friends
6. ✅ Share and have fun!

---

## 📞 Need Help?

1. Check README.md for detailed documentation
2. Review config.py for advanced settings
3. Look for error messages - they're usually helpful!

---

**Ready? Let's go!** 🚀

```bash
./run.sh
```

Or if first time:
```bash
./install.sh
./run.sh
```

Have fun creating your custom face filters! 🎉
