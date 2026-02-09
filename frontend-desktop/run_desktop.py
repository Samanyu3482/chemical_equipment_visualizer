#!/usr/bin/env python3
"""
Desktop application launcher with dependency checking
"""

import sys
import os
import subprocess
import importlib.util

def check_dependency(package_name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = package_name
    
    spec = importlib.util.find_spec(import_name)
    return spec is not None

def install_dependencies():
    """Install required dependencies"""
    dependencies = [
        ("PyQt5", "PyQt5.QtWidgets"),
        ("matplotlib", "matplotlib"),
        ("requests", "requests")
    ]
    
    missing = []
    for package, import_name in dependencies:
        if not check_dependency(package, import_name):
            missing.append(package)
    
    if missing:
        print(f"Missing dependencies: {', '.join(missing)}")
        print("Installing dependencies...")
        
        try:
            for package in missing:
                subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print("Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Failed to install dependencies: {e}")
            return False
    
    return True

def main():
    """Main launcher function"""
    print("Chemical Equipment Visualizer - Desktop Application")
    print("=" * 55)
    
    # Check and install dependencies
    if not install_dependencies():
        print("❌ Failed to install required dependencies.")
        print("Please install manually:")
        print("pip install PyQt5 matplotlib requests")
        return False
    
    # Check if main.py exists
    if not os.path.exists("main.py"):
        print("❌ main.py not found in current directory")
        return False
    
    print("✓ All dependencies available")
    print("🚀 Starting desktop application...")
    
    try:
        # Import and run the main application
        import main
        main.main()
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Please ensure all application files are present")
        return False
    except Exception as e:
        print(f"❌ Application error: {e}")
        return False

if __name__ == '__main__':
    success = main()
    if not success:
        input("Press Enter to exit...")
    sys.exit(0 if success else 1)