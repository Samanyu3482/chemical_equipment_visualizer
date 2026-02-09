#!/usr/bin/env python3
"""
Simple test script to verify desktop application components
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        # Test PyQt5 imports
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        from PyQt5.QtGui import QFont
        print("✓ PyQt5 imports successful")
        
        # Test matplotlib imports
        import matplotlib.pyplot as plt
        from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
        print("✓ Matplotlib imports successful")
        
        # Test requests import
        import requests
        print("✓ Requests import successful")
        
        # Test our custom modules
        from utils.config import AppConfig
        from utils.api_client import APIClient
        print("✓ Custom utility imports successful")
        
        from ui.auth_dialogs import AuthDialog
        from ui.upload_widget import UploadWidget
        from ui.analytics_widget import AnalyticsWidget
        from ui.history_widget import HistoryWidget
        print("✓ UI component imports successful")
        
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False

def test_basic_functionality():
    """Test basic functionality without GUI"""
    print("\nTesting basic functionality...")
    
    try:
        # Test configuration
        from utils.config import AppConfig
        config = AppConfig()
        print(f"✓ Configuration initialized: API URL = {config.api_base_url}")
        
        # Test API client
        from utils.api_client import APIClient
        api_client = APIClient(config.api_base_url)
        print("✓ API client initialized")
        
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def test_gui_creation():
    """Test GUI component creation"""
    print("\nTesting GUI creation...")
    
    try:
        from PyQt5.QtWidgets import QApplication
        from utils.config import AppConfig
        from utils.api_client import APIClient
        from ui.main_window import MainWindow
        
        # Create QApplication (required for any Qt widgets)
        app = QApplication([])
        
        # Create configuration and API client
        config = AppConfig()
        
        # Create main window (but don't show it)
        main_window = MainWindow(config)
        print("✓ Main window created successfully")
        
        # Clean up
        app.quit()
        
        return True
        
    except Exception as e:
        print(f"✗ GUI creation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Chemical Equipment Visualizer - Desktop Application Test")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Basic Functionality", test_basic_functionality),
        ("GUI Creation", test_gui_creation)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        print("-" * 30)
        
        if test_func():
            passed += 1
            print(f"✓ {test_name} PASSED")
        else:
            print(f"✗ {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Desktop application is ready to run.")
        print("\nTo start the application, run:")
        print("python main.py")
    else:
        print("❌ Some tests failed. Please check the error messages above.")
        print("\nCommon solutions:")
        print("1. Install required packages: pip install PyQt5 matplotlib requests")
        print("2. Ensure you're using Python 3.8 or higher")
        print("3. Check that all files are in the correct directories")
    
    return passed == total

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)