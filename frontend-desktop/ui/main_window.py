"""
Main application window
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QMenuBar, QStatusBar, QAction, QLabel, QPushButton,
    QStackedWidget, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QKeySequence

from utils.api_client import APIClient
from ui.auth_dialogs import AuthDialog, LogoutConfirmDialog
from ui.landing_widget import LandingWidget
from ui.upload_widget import UploadWidget
from ui.analytics_widget import AnalyticsWidget
from ui.history_widget import HistoryWidget


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.api_client = APIClient(config.api_base_url)
        self.current_user = None
        
        self.setup_ui()
        self.setup_menu()
        self.setup_status_bar()
        self.restore_window_state()
        
        # Show authentication dialog on startup
        self.show_auth_dialog()
    
    def setup_ui(self):
        """Set up the user interface"""
        self.setWindowTitle("Chemical Equipment Parameter Visualizer")
        self.setMinimumSize(1200, 800)  # Increased minimum size
        
        # Set modern color scheme
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
            }
        """)
        
        # Central widget with stacked layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Navigation bar with gradient
        nav_widget = QWidget()
        nav_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea, stop:1 #764ba2);
                padding: 10px;
            }
        """)
        nav_layout = QHBoxLayout(nav_widget)
        nav_layout.setContentsMargins(15, 10, 15, 10)
        nav_layout.setSpacing(15)
        
        # Home button
        self.home_nav_btn = QPushButton("🏠 Home")
        self.home_nav_btn.setMinimumHeight(40)
        self.home_nav_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
        """)
        self.home_nav_btn.clicked.connect(lambda: self.show_page(0))
        nav_layout.addWidget(self.home_nav_btn)
        
        self.upload_nav_btn = QPushButton("📁 Upload")
        self.upload_nav_btn.setMinimumHeight(40)
        self.upload_nav_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
        """)
        self.upload_nav_btn.clicked.connect(lambda: self.show_page(1))
        nav_layout.addWidget(self.upload_nav_btn)
        
        self.analytics_nav_btn = QPushButton("📊 Analytics")
        self.analytics_nav_btn.setMinimumHeight(40)
        self.analytics_nav_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
        """)
        self.analytics_nav_btn.clicked.connect(lambda: self.show_page(2))
        nav_layout.addWidget(self.analytics_nav_btn)
        
        self.history_nav_btn = QPushButton("📜 History")
        self.history_nav_btn.setMinimumHeight(40)
        self.history_nav_btn.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: 2px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                padding: 0 20px;
            }
            QPushButton:hover {
                background-color: rgba(255, 255, 255, 0.3);
                border: 2px solid rgba(255, 255, 255, 0.5);
            }
        """)
        self.history_nav_btn.clicked.connect(lambda: self.show_page(3))
        nav_layout.addWidget(self.history_nav_btn)
        
        nav_layout.addStretch()
        
        # User info label
        self.user_label = QLabel("Not logged in")
        self.user_label.setStyleSheet("""
            color: white;
            font-size: 14px;
            background: transparent;
            padding: 5px 10px;
        """)
        nav_layout.addWidget(self.user_label)
        
        layout.addWidget(nav_widget)
        
        # Stacked widget for different pages
        self.stacked_widget = QStackedWidget()
        layout.addWidget(self.stacked_widget)
        
        # Create pages
        self.landing_widget = LandingWidget()
        self.upload_widget = UploadWidget(self.api_client)
        self.analytics_widget = AnalyticsWidget(self.api_client)
        self.history_widget = HistoryWidget(self.api_client)
        
        # Connect landing page signals
        self.landing_widget.navigate_to_upload.connect(lambda: self.show_page(1))
        self.landing_widget.navigate_to_analytics.connect(lambda: self.show_page(2))
        self.landing_widget.navigate_to_history.connect(lambda: self.show_page(3))
        
        self.stacked_widget.addWidget(self.landing_widget)
        self.stacked_widget.addWidget(self.upload_widget)
        self.stacked_widget.addWidget(self.analytics_widget)
        self.stacked_widget.addWidget(self.history_widget)
        
        # Connect signals
        self.upload_widget.upload_completed.connect(self.on_upload_completed)
        
        # Initially disable navigation (until authenticated)
        self.set_navigation_enabled(False)
    
    def setup_menu(self):
        """Set up the menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu('File')
        
        # Upload action
        upload_action = QAction('Upload CSV...', self)
        upload_action.setShortcut(QKeySequence.Open)
        upload_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(upload_action)
        
        file_menu.addSeparator()
        
        # Exit action
        exit_action = QAction('Exit', self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # View menu
        view_menu = menubar.addMenu('View')
        
        # Navigation actions
        upload_action = QAction('Upload', self)
        upload_action.setShortcut('Ctrl+1')
        upload_action.triggered.connect(lambda: self.show_page(0))
        view_menu.addAction(upload_action)
        
        analytics_action = QAction('Analytics', self)
        analytics_action.setShortcut('Ctrl+2')
        analytics_action.triggered.connect(lambda: self.show_page(1))
        view_menu.addAction(analytics_action)
        
        history_action = QAction('History', self)
        history_action.setShortcut('Ctrl+3')
        history_action.triggered.connect(lambda: self.show_page(2))
        view_menu.addAction(history_action)
        
        # Account menu
        account_menu = menubar.addMenu('Account')
        
        # Login action
        self.login_action = QAction('Login...', self)
        self.login_action.triggered.connect(self.show_auth_dialog)
        account_menu.addAction(self.login_action)
        
        # Logout action
        self.logout_action = QAction('Logout', self)
        self.logout_action.triggered.connect(self.handle_logout)
        self.logout_action.setEnabled(False)
        account_menu.addAction(self.logout_action)
        
        # Help menu
        help_menu = menubar.addMenu('Help')
        
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_status_bar(self):
        """Set up the status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def show_auth_dialog(self):
        """Show authentication dialog"""
        auth_dialog = AuthDialog(self.api_client, self.config, self)
        auth_dialog.authenticated.connect(self.on_authentication_success)
        auth_dialog.exec_()
    
    def on_authentication_success(self, username: str):
        """Handle successful authentication"""
        self.current_user = username
        self.user_label.setText(f"Logged in as: {username}")
        self.set_navigation_enabled(True)
        self.login_action.setEnabled(False)
        self.logout_action.setEnabled(True)
        self.status_bar.showMessage(f"Logged in as {username}")
        
        # Refresh data in widgets
        self.analytics_widget.refresh_data()
        self.history_widget.refresh_data()
    
    def handle_logout(self):
        """Handle logout request"""
        if not self.current_user:
            return
        
        # Show confirmation dialog
        confirm_dialog = LogoutConfirmDialog(self.current_user, self)
        if confirm_dialog.exec_() == QMessageBox.Accepted:
            # Perform logout
            self.api_client.logout()
            self.current_user = None
            self.user_label.setText("Not logged in")
            self.set_navigation_enabled(False)
            self.login_action.setEnabled(True)
            self.logout_action.setEnabled(False)
            self.status_bar.showMessage("Logged out")
            
            # Show auth dialog again
            self.show_auth_dialog()
    
    def set_navigation_enabled(self, enabled: bool):
        """Enable or disable navigation"""
        self.home_nav_btn.setEnabled(enabled)
        self.upload_nav_btn.setEnabled(enabled)
        self.analytics_nav_btn.setEnabled(enabled)
        self.history_nav_btn.setEnabled(enabled)
        
        if not enabled:
            self.show_page(0)  # Default to landing page
    
    def show_page(self, index: int):
        """Show a specific page"""
        if not self.api_client.is_authenticated():
            return
        
        self.stacked_widget.setCurrentIndex(index)
        
        # Update navigation button styles with better visual feedback
        buttons = [self.home_nav_btn, self.upload_nav_btn, self.analytics_nav_btn, self.history_nav_btn]
        for i, btn in enumerate(buttons):
            if i == index:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(255, 255, 255, 0.9);
                        color: #667eea;
                        border: 2px solid white;
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: bold;
                        padding: 0 20px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background-color: rgba(255, 255, 255, 0.2);
                        color: white;
                        border: 2px solid rgba(255, 255, 255, 0.3);
                        border-radius: 8px;
                        font-size: 14px;
                        font-weight: bold;
                        padding: 0 20px;
                    }
                    QPushButton:hover {
                        background-color: rgba(255, 255, 255, 0.3);
                        border: 2px solid rgba(255, 255, 255, 0.5);
                    }
                """)
        
        # Update status bar
        pages = ["Home", "Upload", "Analytics", "History"]
        self.status_bar.showMessage(f"Viewing: {pages[index]}")
    
    def open_file_dialog(self):
        """Open file dialog for CSV upload"""
        if not self.api_client.is_authenticated():
            QMessageBox.warning(self, "Authentication Required", "Please login first.")
            return
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            self.show_page(1)  # Switch to upload page (index 1 now)
            self.upload_widget.upload_file(file_path)
    
    def on_upload_completed(self, success: bool, message: str):
        """Handle upload completion"""
        if success:
            self.status_bar.showMessage("Upload completed successfully")
            # Refresh analytics and history
            self.analytics_widget.refresh_data()
            self.history_widget.refresh_data()
        else:
            self.status_bar.showMessage(f"Upload failed: {message}")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Chemical Equipment Visualizer",
            "Chemical Equipment Parameter Visualizer v1.0\n\n"
            "A desktop application for analyzing and visualizing\n"
            "chemical equipment parameters from CSV data.\n\n"
            "Built with PyQt5 and Matplotlib."
        )
    
    def restore_window_state(self):
        """Restore window geometry and state"""
        geometry = self.config.get_window_geometry()
        if geometry:
            self.restoreGeometry(geometry)
        
        state = self.config.get_window_state()
        if state:
            self.restoreState(state)
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Save window state
        self.config.save_window_geometry(self.saveGeometry())
        self.config.save_window_state(self.saveState())
        
        # Logout if authenticated
        if self.api_client.is_authenticated():
            self.api_client.logout()
        
        event.accept()