#!/usr/bin/env python3
"""
Database inspection script.
This script now delegates to the display_all_tables function in db.py
"""

import sys
import os

# Add the backend directory to the Python path
backend_dir = os.path.join(os.path.dirname(__file__), "backend", "src")
sys.path.insert(0, backend_dir)

from core.db import display_all_tables

if __name__ == "__main__":
    # Use the function from db.py
    display_all_tables()
