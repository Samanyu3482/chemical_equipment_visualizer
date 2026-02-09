#!/usr/bin/env python3
"""
Chemical Equipment Parameter Visualizer - Desktop Application
Main entry point for the PyQt5 desktop application
"""

import sys
import os
from PyQt5.QtWidgets import QApplication, QStyleFactory
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

# Add the current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow
from utils.config import AppConfig


def main():
    """Main application entry point"""
    # Create QApplication instance
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Chemical Equipment Visualizer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Equipment Analytics")
    
    # Set application style
    app.setStyle(QStyleFactory.create('Fusion'))
    
    # Apply modern light theme
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f8f9fa;
        }
        QWidget {
            background-color: #ffffff;
            color: #333333;
        }
        QPushButton {
            background-color: #667eea;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: 500;
        }
        QPushButton:hover {
            background-color: #5568d3;
        }
        QPushButton:pressed {
            background-color: #4451b8;
        }
        QPushButton:disabled {
            background-color: #cccccc;
            color: #666666;
        }
        QLineEdit {
            background-color: #ffffff;
            border: 2px solid #e0e0e0;
            padding: 8px;
            border-radius: 6px;
            color: #333333;
        }
        QLineEdit:focus {
            border: 2px solid #667eea;
        }
        QTableWidget {
            background-color: #ffffff;
            alternate-background-color: #f8f9fa;
            gridline-color: #e0e0e0;
            color: #333333;
        }
        QHeaderView::section {
            background-color: #f8f9fa;
            border: 1px solid #e0e0e0;
            padding: 8px;
            color: #333333;
            font-weight: bold;
        }
        QGroupBox {
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            font-weight: bold;
            color: #333333;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px;
        }
        QScrollBar:vertical {
            border: none;
            background: #f8f9fa;
            width: 10px;
            margin: 0px;
        }
        QScrollBar::handle:vertical {
            background: #cccccc;
            border-radius: 5px;
            min-height: 20px;
        }
        QScrollBar::handle:vertical:hover {
            background: #999999;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
    """)
    
    # Initialize configuration
    config = AppConfig()
    
    # Create and show main window
    main_window = MainWindow(config)
    main_window.show()
    
    # Start event loop
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()