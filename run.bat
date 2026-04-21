@echo off
REM Face Filter App - Run Script for Windows

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
