@echo off
REM Face Filter App - Installation Script for Windows

echo ==========================================
echo Face Filter App - Installation Script
echo ==========================================
echo.

REM Check if Python is installed
echo Checking Python installation...
python --version >nul 2>&1

if errorlevel 1 (
    echo Error: Python 3 is not installed!
    echo Please download and install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    pause
    exit /b 1
)

python --version

REM Check if virtual environment exists
if exist "venv" (
    echo. Virtual environment already exists
) else (
    echo.
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Error: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully
)

REM Activate virtual environment
echo.
echo Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Error: Failed to activate virtual environment
    pause
    exit /b 1
)
echo Virtual environment activated

REM Upgrade pip
echo.
echo Upgrading pip...
python -m pip install --upgrade pip
if errorlevel 1 (
    echo Warning: Failed to upgrade pip, continuing anyway...
)

REM Install requirements
echo.
echo Installing dependencies...
echo This may take a few minutes...
pip install -r requirements.txt

if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ==========================================
echo Installation completed successfully!
echo.
echo You can now run the app with:
echo   - run.bat (normal mode)
echo   - run_debug.bat (debug mode)
echo ==========================================

pause
