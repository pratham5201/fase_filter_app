#!/bin/bash
# Run app with debug output visible

cd /home/developer/own/face_filter_app

echo "================================"
echo "FACE FILTER APP - DEBUG MODE"
echo "================================"
echo ""
echo "Starting app with full debug output..."
echo "Watch the terminal for DEBUG lines"
echo ""
echo "When you:"
echo "  1. Select Pratham filter"
echo "  2. Click Start Camera"
echo "  3. Your face appears"
echo ""
echo "You should see in the terminal:"
echo "  - 'Filter selected' messages"
echo "  - 'Face(s) detected' count"
echo "  - 'Got XXX landmarks from frame'"
echo "  - 'Processed XXX triangles'"
echo "  - 'Transform applied' with pixel difference"
echo ""
echo "If you see 'Transformation seems minimal' -> coordinates issue"
echo "If you see '0 triangles processed' -> bounds checking too strict"
echo ""
echo "================================"
echo ""

source venv/bin/activate
python3 main.py
