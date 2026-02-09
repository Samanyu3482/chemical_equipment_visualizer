"""
Application configuration management
"""

import os
import json
from typing import Optional, Dict, Any
from PyQt5.QtCore import QSettings


class AppConfig:
    """Manages application configuration and settings"""
    
    def __init__(self):
        self.settings = QSettings()
        self.api_base_url = self.get_setting('api_base_url', 'http://localhost:8000/api')
        self.remember_credentials = self.get_setting('remember_credentials', False)
        self.last_username = self.get_setting('last_username', '')
        
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        return self.settings.value(key, default)
    
    def set_setting(self, key: str, value: Any) -> None:
        """Set a setting value"""
        self.settings.setValue(key, value)
        self.settings.sync()
    
    def get_api_url(self, endpoint: str) -> str:
        """Get full API URL for an endpoint"""
        return f"{self.api_base_url.rstrip('/')}/{endpoint.lstrip('/')}"
    
    def save_credentials(self, username: str, remember: bool = False) -> None:
        """Save user credentials (username only, never password)"""
        self.set_setting('last_username', username)
        self.set_setting('remember_credentials', remember)
    
    def clear_credentials(self) -> None:
        """Clear saved credentials"""
        self.set_setting('last_username', '')
        self.set_setting('remember_credentials', False)
    
    def get_window_geometry(self) -> Optional[bytes]:
        """Get saved window geometry"""
        return self.settings.value('window_geometry')
    
    def save_window_geometry(self, geometry: bytes) -> None:
        """Save window geometry"""
        self.set_setting('window_geometry', geometry)
    
    def get_window_state(self) -> Optional[bytes]:
        """Get saved window state"""
        return self.settings.value('window_state')
    
    def save_window_state(self, state: bytes) -> None:
        """Save window state"""
        self.set_setting('window_state', state)