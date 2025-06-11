#!/usr/bin/env python3
"""
Launcher script for the Donation Reconciliation Tool
This script starts the Streamlit app and opens it in the default browser
"""

import subprocess
import sys
import os
import webbrowser
import time
from pathlib import Path

def get_app_path():
    """Get the path to the main app file"""
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        app_dir = Path(sys.executable).parent
    else:
        # Running as script
        app_dir = Path(__file__).parent
    
    return app_dir / "donation_tool.py"

def main():
    """Main launcher function"""
    print("🚀 Starting Donation Reconciliation Tool...")
    print("📊 This will open in your web browser automatically")
    print("🔒 All processing is done locally on your computer")
    print("=" * 50)
    
    app_path = get_app_path()
    
    if not app_path.exists():
        print(f"❌ Error: Could not find app file at {app_path}")
        input("Press Enter to exit...")
        return
    
    # Start Streamlit app
    proc = subprocess.Popen([
        sys.executable, "-m", "streamlit", "run", 
        str(app_path),
        "--server.port=8501",
        "--server.address=localhost",
        "--browser.gatherUsageStats=false",
        "--server.headless=true"
    ])
    
    # Wait a few seconds for the server to start
    time.sleep(3)
    
    # Open browser ONCE
    webbrowser.open("http://localhost:8501")
    
    # Wait for the Streamlit process to finish
    proc.wait()

if __name__ == "__main__":
    main()