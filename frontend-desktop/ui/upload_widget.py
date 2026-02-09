"""
File upload widget for CSV files
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QTextEdit, QFileDialog, QMessageBox,
    QGroupBox, QGridLayout, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QDragEnterEvent, QDropEvent

from utils.api_client import APIClient


class UploadWorker(QThread):
    """Worker thread for file upload"""
    
    upload_progress = pyqtSignal(int)  # progress percentage
    upload_completed = pyqtSignal(bool, dict, str)  # success, data, message
    
    def __init__(self, api_client: APIClient, file_path: str):
        super().__init__()
        self.api_client = api_client
        self.file_path = file_path
    
    def run(self):
        """Run the upload in background thread"""
        try:
            # Simulate progress updates
            self.upload_progress.emit(25)
            
            # Perform actual upload
            success, data, message = self.api_client.upload_csv(self.file_path)
            
            self.upload_progress.emit(100)
            self.upload_completed.emit(success, data, message)
            
        except Exception as e:
            self.upload_completed.emit(False, {}, f"Upload error: {str(e)}")


class DropZone(QFrame):
    """Drag and drop zone for file uploads"""
    
    file_dropped = pyqtSignal(str)  # file path
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.setAcceptDrops(True)
    
    def setup_ui(self):
        """Set up the UI"""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                border: 3px dashed #667eea;
                border-radius: 12px;
                background-color: white;
                min-height: 200px;
            }
            QFrame:hover {
                border-color: #5568d3;
                background-color: #f8f9fa;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(15)
        
        # Icon or placeholder
        icon_label = QLabel("📁")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 72px; background: transparent;")
        layout.addWidget(icon_label)
        
        # Instructions
        instruction_label = QLabel("Drag and drop CSV file here\nor click to browse")
        instruction_label.setAlignment(Qt.AlignCenter)
        instruction_label.setWordWrap(True)
        instruction_label.setStyleSheet("""
            color: #667eea;
            font-size: 18px;
            font-weight: bold;
            background: transparent;
        """)
        layout.addWidget(instruction_label)
        
        # File format info
        format_label = QLabel("Supported format: CSV files (.csv)")
        format_label.setAlignment(Qt.AlignCenter)
        format_label.setStyleSheet("color: #6c757d; font-size: 14px; background: transparent;")
        layout.addWidget(format_label)
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) == 1 and urls[0].toLocalFile().endswith('.csv'):
                event.acceptProposedAction()
                self.setStyleSheet("""
                    QFrame {
                        border: 3px dashed #43e97b;
                        border-radius: 12px;
                        background-color: #d4edda;
                        min-height: 200px;
                    }
                """)
    
    def dragLeaveEvent(self, event):
        """Handle drag leave event"""
        self.setStyleSheet("""
            QFrame {
                border: 3px dashed #667eea;
                border-radius: 12px;
                background-color: white;
                min-height: 200px;
            }
            QFrame:hover {
                border-color: #5568d3;
                background-color: #f8f9fa;
            }
        """)
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop event"""
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            if file_path.endswith('.csv'):
                self.file_dropped.emit(file_path)
                event.acceptProposedAction()
        
        # Reset style
        self.dragLeaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press to open file dialog"""
        if event.button() == Qt.LeftButton:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select CSV File",
                "",
                "CSV Files (*.csv);;All Files (*)"
            )
            if file_path:
                self.file_dropped.emit(file_path)


class UploadWidget(QWidget):
    """Main upload widget"""
    
    upload_completed = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.upload_worker = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Title with gradient background
        title_widget = QWidget()
        title_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 10px;
                padding: 15px;
            }
        """)
        title_layout = QVBoxLayout(title_widget)
        
        title = QLabel("📁 Upload CSV Data")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
            background: transparent;
        """)
        title_layout.addWidget(title)
        
        subtitle = QLabel("Import your equipment data for analysis")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("""
            color: rgba(255, 255, 255, 0.9);
            font-size: 14px;
            background: transparent;
        """)
        title_layout.addWidget(subtitle)
        
        layout.addWidget(title_widget)
        
        # Upload section
        upload_group = QGroupBox("File Upload")
        upload_layout = QVBoxLayout(upload_group)
        
        # Drop zone
        self.drop_zone = DropZone()
        self.drop_zone.file_dropped.connect(self.upload_file)
        upload_layout.addWidget(self.drop_zone)
        
        # Browse button
        browse_layout = QHBoxLayout()
        browse_layout.addStretch()
        
        self.browse_button = QPushButton("Browse Files...")
        self.browse_button.clicked.connect(self.browse_file)
        browse_layout.addWidget(self.browse_button)
        
        browse_layout.addStretch()
        upload_layout.addLayout(browse_layout)
        
        layout.addWidget(upload_group)
        
        # Progress section
        progress_group = QGroupBox("Upload Progress")
        progress_layout = QVBoxLayout(progress_group)
        
        # File info
        self.file_info_label = QLabel("No file selected")
        progress_layout.addWidget(self.file_info_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        # Upload button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.upload_button = QPushButton("Upload File")
        self.upload_button.setEnabled(False)
        self.upload_button.clicked.connect(self.start_upload)
        button_layout.addWidget(self.upload_button)
        
        button_layout.addStretch()
        progress_layout.addLayout(button_layout)
        
        layout.addWidget(progress_group)
        
        # Results section
        results_group = QGroupBox("Upload Results")
        results_layout = QVBoxLayout(results_group)
        
        self.results_text = QTextEdit()
        self.results_text.setMaximumHeight(150)
        self.results_text.setReadOnly(True)
        results_layout.addWidget(self.results_text)
        
        layout.addWidget(results_group)
        
        # File requirements info
        info_group = QGroupBox("File Requirements")
        info_layout = QVBoxLayout(info_group)
        
        requirements_text = """
        CSV File Requirements:
        • File must have .csv extension
        • Required columns: Equipment Name, Type, Flowrate, Pressure, Temperature
        • Numeric values for Flowrate, Pressure, and Temperature
        • No missing values in required columns
        • Maximum file size: 10MB
        """
        
        requirements_label = QLabel(requirements_text)
        requirements_label.setWordWrap(True)
        requirements_label.setStyleSheet("""
            color: #495057;
            font-size: 13px;
            background: transparent;
            padding: 10px;
        """)
        info_layout.addWidget(requirements_label)
        
        layout.addWidget(info_group)
        
        layout.addStretch()
        
        # Initialize state
        self.selected_file_path = None
    
    def browse_file(self):
        """Open file browser dialog"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            self.upload_file(file_path)
    
    def upload_file(self, file_path: str):
        """Handle file selection"""
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "File Error", "Selected file does not exist.")
            return
        
        if not file_path.endswith('.csv'):
            QMessageBox.warning(self, "File Error", "Please select a CSV file.")
            return
        
        # Check file size (10MB limit)
        file_size = os.path.getsize(file_path)
        if file_size > 10 * 1024 * 1024:  # 10MB
            QMessageBox.warning(
                self, 
                "File Too Large", 
                "File size exceeds 10MB limit. Please select a smaller file."
            )
            return
        
        self.selected_file_path = file_path
        
        # Update UI
        filename = os.path.basename(file_path)
        file_size_mb = file_size / (1024 * 1024)
        self.file_info_label.setText(f"Selected: {filename} ({file_size_mb:.2f} MB)")
        self.upload_button.setEnabled(True)
        self.results_text.clear()
    
    def start_upload(self):
        """Start the upload process"""
        if not self.selected_file_path:
            return
        
        if not self.api_client.is_authenticated():
            QMessageBox.warning(self, "Authentication Required", "Please login first.")
            return
        
        # Disable UI during upload
        self.upload_button.setEnabled(False)
        self.browse_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Start upload worker
        self.upload_worker = UploadWorker(self.api_client, self.selected_file_path)
        self.upload_worker.upload_progress.connect(self.update_progress)
        self.upload_worker.upload_completed.connect(self.on_upload_completed)
        self.upload_worker.start()
    
    @pyqtSlot(int)
    def update_progress(self, value: int):
        """Update progress bar"""
        self.progress_bar.setValue(value)
    
    @pyqtSlot(bool, dict, str)
    def on_upload_completed(self, success: bool, data: dict, message: str):
        """Handle upload completion"""
        # Re-enable UI
        self.upload_button.setEnabled(True)
        self.browse_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Show results
        if success:
            result_text = f"✅ Upload Successful!\n\n"
            result_text += f"Message: {message}\n"
            
            if 'record_count' in data:
                result_text += f"Records processed: {data['record_count']}\n"
            
            if 'upload_id' in data:
                result_text += f"Upload ID: {data['upload_id']}\n"
            
            if 'warnings' in data and data['warnings']:
                result_text += f"\nWarnings:\n"
                for warning in data['warnings']:
                    result_text += f"• {warning}\n"
            
            self.results_text.setStyleSheet("""
                color: #155724;
                background-color: #d4edda;
                border: 2px solid #c3e6cb;
                border-radius: 6px;
                padding: 10px;
            """)
            
        else:
            result_text = f"❌ Upload Failed!\n\n"
            result_text += f"Error: {message}\n"
            
            if 'errors' in data and data['errors']:
                result_text += f"\nDetails:\n"
                for error in data['errors']:
                    result_text += f"• {error}\n"
            
            self.results_text.setStyleSheet("""
                color: #721c24;
                background-color: #f8d7da;
                border: 2px solid #f5c6cb;
                border-radius: 6px;
                padding: 10px;
            """)
        
        self.results_text.setText(result_text)
        
        # Emit signal for main window
        self.upload_completed.emit(success, message)
        
        # Clean up worker
        if self.upload_worker:
            self.upload_worker.deleteLater()
            self.upload_worker = None