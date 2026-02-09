"""
History widget for viewing upload history
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QGroupBox,
    QMessageBox, QFileDialog, QProgressBar, QTextEdit
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot, QDateTime
from PyQt5.QtGui import QFont

from utils.api_client import APIClient


class HistoryWorker(QThread):
    """Worker thread for fetching history data"""
    
    data_loaded = pyqtSignal(bool, list, str)  # success, data, message
    
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
    
    def run(self):
        """Fetch history data"""
        try:
            success, data, message = self.api_client.get_history()
            if success and isinstance(data, list):
                self.data_loaded.emit(True, data, message)
            else:
                self.data_loaded.emit(False, [], message)
        except Exception as e:
            self.data_loaded.emit(False, [], f"Error loading history: {str(e)}")


class PDFDownloadWorker(QThread):
    """Worker thread for downloading PDF reports"""
    
    download_progress = pyqtSignal(int)  # progress percentage
    download_completed = pyqtSignal(bool, bytes, str)  # success, data, message
    
    def __init__(self, api_client: APIClient, upload_id: int = None):
        super().__init__()
        self.api_client = api_client
        self.upload_id = upload_id
    
    def run(self):
        """Download PDF report"""
        try:
            self.download_progress.emit(50)
            success, data, message = self.api_client.download_pdf_report(self.upload_id)
            self.download_progress.emit(100)
            self.download_completed.emit(success, data, message)
        except Exception as e:
            self.download_completed.emit(False, b'', f"Download error: {str(e)}")


class HistoryWidget(QWidget):
    """Main history widget"""
    
    def __init__(self, api_client: APIClient):
        super().__init__()
        self.api_client = api_client
        self.history_data = []
        self.history_worker = None
        self.pdf_worker = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        layout = QVBoxLayout(self)
        
        # Title and refresh button with gradient header
        header_widget = QWidget()
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #4facfe, stop:1 #00f2fe);
                border-radius: 10px;
                padding: 15px;
            }
        """)
        header_layout = QHBoxLayout(header_widget)
        
        title = QLabel("📜 Upload History")
        title.setAlignment(Qt.AlignLeft)
        title.setStyleSheet("""
            color: white;
            font-size: 24px;
            font-weight: bold;
            background: transparent;
        """)
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        self.refresh_button = QPushButton("🔄 Refresh History")
        self.refresh_button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.9);
                color: #4facfe;
                border: 2px solid white;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: white;
            }
        """)
        self.refresh_button.clicked.connect(self.refresh_data)
        header_layout.addWidget(self.refresh_button)
        
        layout.addWidget(header_widget)
        
        # History table
        history_group = QGroupBox("Recent Uploads (Last 5)")
        history_layout = QVBoxLayout(history_group)
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels([
            "Upload ID", "Filename", "Upload Date", "Record Count", "User", "Actions"
        ])
        
        # Set column widths
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # ID
        header.setSectionResizeMode(1, QHeaderView.Stretch)           # Filename
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)  # Date
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Count
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)  # User
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Actions
        
        self.history_table.setAlternatingRowColors(True)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setStyleSheet("""
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                gridline-color: #dee2e6;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                color: #333333;
            }
            QTableWidget::item:selected {
                background-color: #667eea;
                color: white;
            }
        """)
        
        history_layout.addWidget(self.history_table)
        layout.addWidget(history_group)
        
        # Details section
        details_group = QGroupBox("Upload Details")
        details_layout = QVBoxLayout(details_group)
        
        # Selected upload info
        self.details_label = QLabel("Select an upload to view details")
        self.details_label.setWordWrap(True)
        details_layout.addWidget(self.details_label)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        self.download_pdf_button = QPushButton("📥 Download PDF Report")
        self.download_pdf_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5568d3, stop:1 #653a8b);
            }
            QPushButton:disabled {
                background: #cccccc;
                color: #666666;
            }
        """)
        self.download_pdf_button.clicked.connect(self.download_selected_pdf)
        self.download_pdf_button.setEnabled(False)
        actions_layout.addWidget(self.download_pdf_button)
        
        self.download_latest_pdf_button = QPushButton("📥 Download Latest PDF")
        self.download_latest_pdf_button.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #43e97b, stop:1 #38f9d7);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #3ad066, stop:1 #2de0c2);
            }
            QPushButton:disabled {
                background: #cccccc;
                color: #666666;
            }
        """)
        self.download_latest_pdf_button.clicked.connect(self.download_latest_pdf)
        self.download_latest_pdf_button.setEnabled(False)
        actions_layout.addWidget(self.download_latest_pdf_button)
        
        actions_layout.addStretch()
        details_layout.addLayout(actions_layout)
        
        # Progress bar for downloads
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        details_layout.addWidget(self.progress_bar)
        
        layout.addWidget(details_group)
        
        # Status label
        self.status_label = QLabel("Click 'Refresh History' to load upload history")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: #6c757d;
            font-style: italic;
            font-size: 14px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 6px;
        """)
        layout.addWidget(self.status_label)
        
        # Connect table selection
        self.history_table.itemSelectionChanged.connect(self.on_selection_changed)
    
    def refresh_data(self):
        """Refresh history data"""
        if not self.api_client.is_authenticated():
            QMessageBox.warning(self, "Authentication Required", "Please login first.")
            return
        
        # Disable refresh button
        self.refresh_button.setEnabled(False)
        self.refresh_button.setText("Loading...")
        self.status_label.setText("Loading upload history...")
        
        # Start history worker
        self.history_worker = HistoryWorker(self.api_client)
        self.history_worker.data_loaded.connect(self.on_data_loaded)
        self.history_worker.start()
    
    @pyqtSlot(bool, list, str)
    def on_data_loaded(self, success: bool, data: list, message: str):
        """Handle data loading completion"""
        # Re-enable refresh button
        self.refresh_button.setEnabled(True)
        self.refresh_button.setText("Refresh History")
        
        if success:
            self.history_data = data
            self.update_history_table()
            self.status_label.setText(f"Loaded {len(data)} upload records")
            self.download_latest_pdf_button.setEnabled(len(data) > 0)
        else:
            self.status_label.setText(f"Failed to load history: {message}")
            self.clear_history_table()
            self.download_latest_pdf_button.setEnabled(False)
        
        # Clean up worker
        if self.history_worker:
            self.history_worker.deleteLater()
            self.history_worker = None
    
    def update_history_table(self):
        """Update the history table with data"""
        self.history_table.setRowCount(len(self.history_data))
        
        for row, upload in enumerate(self.history_data):
            # Upload ID
            id_item = QTableWidgetItem(str(upload.get('id', '')))
            self.history_table.setItem(row, 0, id_item)
            
            # Filename
            filename_item = QTableWidgetItem(upload.get('filename', ''))
            self.history_table.setItem(row, 1, filename_item)
            
            # Upload date
            upload_time = upload.get('upload_timestamp', '')
            if upload_time:
                # Parse and format the datetime
                try:
                    # Assuming ISO format from Django
                    dt = QDateTime.fromString(upload_time[:19], Qt.ISODate)
                    formatted_time = dt.toString("yyyy-MM-dd hh:mm:ss")
                except:
                    formatted_time = upload_time
            else:
                formatted_time = 'Unknown'
            
            date_item = QTableWidgetItem(formatted_time)
            self.history_table.setItem(row, 2, date_item)
            
            # Record count
            count_item = QTableWidgetItem(str(upload.get('record_count', 0)))
            self.history_table.setItem(row, 3, count_item)
            
            # User (if available)
            user_item = QTableWidgetItem(upload.get('user', 'Unknown'))
            self.history_table.setItem(row, 4, user_item)
            
            # Actions - create download button
            download_btn = QPushButton("📥 PDF")
            download_btn.setStyleSheet("""
                QPushButton {
                    background-color: #667eea;
                    color: white;
                    border: none;
                    border-radius: 6px;
                    padding: 6px 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #5568d3;
                }
            """)
            download_btn.clicked.connect(lambda checked, uid=upload.get('id'): self.download_pdf(uid))
            self.history_table.setCellWidget(row, 5, download_btn)
    
    def clear_history_table(self):
        """Clear the history table"""
        self.history_table.setRowCount(0)
        self.details_label.setText("No upload history available")
        self.download_pdf_button.setEnabled(False)
    
    def on_selection_changed(self):
        """Handle table selection change"""
        selected_rows = self.history_table.selectionModel().selectedRows()
        
        if selected_rows:
            row = selected_rows[0].row()
            if 0 <= row < len(self.history_data):
                upload = self.history_data[row]
                self.show_upload_details(upload)
                self.download_pdf_button.setEnabled(True)
            else:
                self.details_label.setText("Select an upload to view details")
                self.download_pdf_button.setEnabled(False)
        else:
            self.details_label.setText("Select an upload to view details")
            self.download_pdf_button.setEnabled(False)
    
    def show_upload_details(self, upload: dict):
        """Show details for selected upload"""
        details = f"""
        <div style='background: #f8f9fa; padding: 15px; border-radius: 8px; border: 2px solid #e9ecef;'>
        <p style='color: #667eea; font-size: 16px; font-weight: bold; margin-bottom: 10px;'>📋 Upload Details</p>
        <p style='color: #333333; margin: 5px 0;'><b>ID:</b> {upload.get('id', 'Unknown')}</p>
        <p style='color: #333333; margin: 5px 0;'><b>Filename:</b> {upload.get('filename', 'Unknown')}</p>
        <p style='color: #333333; margin: 5px 0;'><b>Upload Time:</b> {upload.get('upload_timestamp', 'Unknown')}</p>
        <p style='color: #333333; margin: 5px 0;'><b>Record Count:</b> {upload.get('record_count', 0)}</p>
        <p style='color: #333333; margin: 5px 0;'><b>User:</b> {upload.get('user', 'Unknown')}</p>
        </div>
        """
        
        self.details_label.setText(details)
    
    def download_selected_pdf(self):
        """Download PDF for selected upload"""
        selected_rows = self.history_table.selectionModel().selectedRows()
        
        if selected_rows:
            row = selected_rows[0].row()
            if 0 <= row < len(self.history_data):
                upload_id = self.history_data[row].get('id')
                self.download_pdf(upload_id)
    
    def download_latest_pdf(self):
        """Download PDF for latest upload"""
        if self.history_data:
            upload_id = self.history_data[0].get('id')  # First item is latest
            self.download_pdf(upload_id)
    
    def download_pdf(self, upload_id: int):
        """Download PDF report for specific upload"""
        if not self.api_client.is_authenticated():
            QMessageBox.warning(self, "Authentication Required", "Please login first.")
            return
        
        # Get save location
        filename = f"equipment_report_{upload_id}.pdf"
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF Report",
            filename,
            "PDF Files (*.pdf);;All Files (*)"
        )
        
        if not file_path:
            return
        
        # Start download
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.download_pdf_button.setEnabled(False)
        self.download_latest_pdf_button.setEnabled(False)
        
        self.pdf_worker = PDFDownloadWorker(self.api_client, upload_id)
        self.pdf_worker.download_progress.connect(self.update_download_progress)
        self.pdf_worker.download_completed.connect(
            lambda success, data, msg: self.on_download_completed(success, data, msg, file_path)
        )
        self.pdf_worker.start()
    
    @pyqtSlot(int)
    def update_download_progress(self, value: int):
        """Update download progress"""
        self.progress_bar.setValue(value)
    
    @pyqtSlot(bool, bytes, str)
    def on_download_completed(self, success: bool, data: bytes, message: str, file_path: str):
        """Handle download completion"""
        # Hide progress bar and re-enable buttons
        self.progress_bar.setVisible(False)
        self.download_pdf_button.setEnabled(True)
        self.download_latest_pdf_button.setEnabled(True)
        
        if success and data:
            try:
                # Save PDF file
                with open(file_path, 'wb') as f:
                    f.write(data)
                
                QMessageBox.information(
                    self, 
                    "Download Successful", 
                    f"PDF report saved to:\n{file_path}"
                )
                
            except Exception as e:
                QMessageBox.critical(
                    self, 
                    "Save Failed", 
                    f"Failed to save PDF file:\n{str(e)}"
                )
        else:
            QMessageBox.critical(
                self, 
                "Download Failed", 
                f"Failed to download PDF report:\n{message}"
            )
        
        # Clean up worker
        if self.pdf_worker:
            self.pdf_worker.deleteLater()
            self.pdf_worker = None