#!/usr/bin/env python3
"""
Face Filter App - Main Entry Point
Real-time AR Face Filter Creator and Applicator for Ubuntu
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from src.ui.main_window import main

if __name__ == "__main__":
    main()
