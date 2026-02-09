"""
Authentication dialog windows
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QCheckBox,
    QMessageBox, QTabWidget, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from utils.api_client import APIClient


class AuthDialog(QDialog):
    """Authentication dialog with login and registration tabs"""
    
    # Signal emitted when authentication is successful
    authenticated = pyqtSignal(str)  # username
    
    def __init__(self, api_client: APIClient, config, parent=None):
        super().__init__(parent)
        self.api_client = api_client
        self.config = config
        self.setup_ui()
        self.load_saved_credentials()
        
    def setup_ui(self):
        """Set up the user interface"""
        self.setWindowTitle("Authentication Required")
        self.setModal(True)
        self.setFixedSize(400, 350)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Chemical Equipment Visualizer")
        title.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        title.setFont(font)
        layout.addWidget(title)
        
        # Tab widget for login/register
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Login tab
        self.login_tab = self.create_login_tab()
        self.tab_widget.addTab(self.login_tab, "Login")
        
        # Register tab
        self.register_tab = self.create_register_tab()
        self.tab_widget.addTab(self.register_tab, "Register")
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: red;")
        layout.addWidget(self.status_label)
        
    def create_login_tab(self) -> QWidget:
        """Create the login tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Username field
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Enter your username")
        form_layout.addRow("Username:", self.login_username)
        
        # Password field
        self.login_password = QLineEdit()
        self.login_password.setEchoMode(QLineEdit.Password)
        self.login_password.setPlaceholderText("Enter your password")
        form_layout.addRow("Password:", self.login_password)
        
        layout.addLayout(form_layout)
        
        # Remember credentials checkbox
        self.remember_checkbox = QCheckBox("Remember username")
        layout.addWidget(self.remember_checkbox)
        
        # Login button
        self.login_button = QPushButton("Login")
        self.login_button.clicked.connect(self.handle_login)
        self.login_button.setDefault(True)
        layout.addWidget(self.login_button)
        
        # Connect Enter key to login
        self.login_password.returnPressed.connect(self.handle_login)
        
        return widget
    
    def create_register_tab(self) -> QWidget:
        """Create the registration tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Form layout
        form_layout = QFormLayout()
        
        # Username field
        self.register_username = QLineEdit()
        self.register_username.setPlaceholderText("Choose a username")
        form_layout.addRow("Username:", self.register_username)
        
        # Email field
        self.register_email = QLineEdit()
        self.register_email.setPlaceholderText("Enter your email")
        form_layout.addRow("Email:", self.register_email)
        
        # Password field
        self.register_password = QLineEdit()
        self.register_password.setEchoMode(QLineEdit.Password)
        self.register_password.setPlaceholderText("Choose a password")
        form_layout.addRow("Password:", self.register_password)
        
        # Confirm password field
        self.register_confirm = QLineEdit()
        self.register_confirm.setEchoMode(QLineEdit.Password)
        self.register_confirm.setPlaceholderText("Confirm your password")
        form_layout.addRow("Confirm:", self.register_confirm)
        
        layout.addLayout(form_layout)
        
        # Register button
        self.register_button = QPushButton("Register")
        self.register_button.clicked.connect(self.handle_register)
        layout.addWidget(self.register_button)
        
        # Connect Enter key to register
        self.register_confirm.returnPressed.connect(self.handle_register)
        
        return widget
    
    def load_saved_credentials(self):
        """Load saved credentials if available"""
        if self.config.remember_credentials and self.config.last_username:
            self.login_username.setText(self.config.last_username)
            self.remember_checkbox.setChecked(True)
            self.login_password.setFocus()
        else:
            self.login_username.setFocus()
    
    def handle_login(self):
        """Handle login button click"""
        username = self.login_username.text().strip()
        password = self.login_password.text()
        
        if not username or not password:
            self.show_error("Please enter both username and password")
            return
        
        # Disable button during login
        self.login_button.setEnabled(False)
        self.login_button.setText("Logging in...")
        
        # Attempt login
        success, message = self.api_client.login(username, password)
        
        if success:
            # Save credentials if requested
            if self.remember_checkbox.isChecked():
                self.config.save_credentials(username, True)
            else:
                self.config.clear_credentials()
            
            self.authenticated.emit(username)
            self.accept()
        else:
            self.show_error(message)
        
        # Re-enable button
        self.login_button.setEnabled(True)
        self.login_button.setText("Login")
    
    def handle_register(self):
        """Handle register button click"""
        username = self.register_username.text().strip()
        email = self.register_email.text().strip()
        password = self.register_password.text()
        confirm = self.register_confirm.text()
        
        # Validation
        if not username or not email or not password:
            self.show_error("Please fill in all fields")
            return
        
        if password != confirm:
            self.show_error("Passwords do not match")
            return
        
        if len(password) < 6:
            self.show_error("Password must be at least 6 characters")
            return
        
        # Disable button during registration
        self.register_button.setEnabled(False)
        self.register_button.setText("Registering...")
        
        # Attempt registration
        success, message = self.api_client.register(username, email, password)
        
        if success:
            QMessageBox.information(
                self, 
                "Registration Successful", 
                "Account created successfully! Please login with your credentials."
            )
            # Switch to login tab and fill username
            self.tab_widget.setCurrentIndex(0)
            self.login_username.setText(username)
            self.login_password.setFocus()
        else:
            self.show_error(message)
        
        # Re-enable button
        self.register_button.setEnabled(True)
        self.register_button.setText("Register")
    
    def show_error(self, message: str):
        """Show error message"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: red;")
    
    def show_success(self, message: str):
        """Show success message"""
        self.status_label.setText(message)
        self.status_label.setStyleSheet("color: green;")


class LogoutConfirmDialog(QDialog):
    """Confirmation dialog for logout"""
    
    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self.username = username
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the user interface"""
        self.setWindowTitle("Confirm Logout")
        self.setModal(True)
        self.setFixedSize(300, 150)
        
        layout = QVBoxLayout(self)
        
        # Message
        message = QLabel(f"Are you sure you want to logout?\n\nUser: {self.username}")
        message.setAlignment(Qt.AlignCenter)
        layout.addWidget(message)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.logout_button = QPushButton("Logout")
        self.logout_button.clicked.connect(self.accept)
        button_layout.addWidget(self.logout_button)
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.cancel_button.setDefault(True)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)