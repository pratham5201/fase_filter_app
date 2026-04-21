@echo off
REM Face Filter App - Debug Mode for Windows

echo ================================
echo FACE FILTER APP - DEBUG MODE
echo ================================
echo.
echo Starting app with full debug output...
echo Watch the terminal for DEBUG lines
echo.
echo When you:
echo   1. Select Pratham filter
echo   2. Click Start Camera
echo   3. Your face appears
echo.
echo You should see in the terminal:
echo   - 'Filter selected' messages
echo   - 'Face(s) detected' count
echo   - 'Got XXX landmarks from frame'
echo   - 'Processed XXX triangles'
echo   - 'Transform applied' with pixel difference
echo.
echo If you see 'Transformation seems minimal' - coordinates issue
echo If you see '0 triangles processed' - bounds checking too strict
echo.
echo ================================
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found!
    echo Please run: install.bat
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the app
python main.py

pause
