"""
API client for communicating with Django backend
"""

import requests
import json
from typing import Optional, Dict, Any, Tuple
from PyQt5.QtCore import QObject, pyqtSignal


class APIClient(QObject):
    """Handles API communication with the Django backend"""
    
    # Signals for async operations
    login_completed = pyqtSignal(bool, str)  # success, message
    upload_completed = pyqtSignal(bool, dict, str)  # success, data, message
    
    def __init__(self, base_url: str):
        super().__init__()
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.access_token = None
        self.refresh_token = None
        
    def set_auth_tokens(self, access_token: str, refresh_token: str) -> None:
        """Set authentication tokens"""
        self.access_token = access_token
        self.refresh_token = refresh_token
        self.session.headers.update({
            'Authorization': f'Bearer {access_token}'
        })
    
    def clear_auth_tokens(self) -> None:
        """Clear authentication tokens"""
        self.access_token = None
        self.refresh_token = None
        if 'Authorization' in self.session.headers:
            del self.session.headers['Authorization']
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Tuple[bool, Dict[str, Any]]:
        """Make HTTP request to API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Try to parse JSON response
            try:
                data = response.json()
            except json.JSONDecodeError:
                data = {'message': response.text}
            
            return response.status_code < 400, data
            
        except requests.exceptions.RequestException as e:
            return False, {'error': f'Network error: {str(e)}'}
    
    def register(self, username: str, email: str, password: str) -> Tuple[bool, str]:
        """Register a new user"""
        success, data = self._make_request('POST', 'auth/register/', json={
            'username': username,
            'email': email,
            'password': password
        })
        
        if success:
            return True, 'Registration successful'
        else:
            error_msg = data.get('error', 'Registration failed')
            if isinstance(data, dict):
                # Handle field-specific errors
                errors = []
                for field, messages in data.items():
                    if isinstance(messages, list):
                        errors.extend(messages)
                    else:
                        errors.append(str(messages))
                if errors:
                    error_msg = '; '.join(errors)
            return False, error_msg
    
    def login(self, username: str, password: str) -> Tuple[bool, str]:
        """Login user and get authentication tokens"""
        success, data = self._make_request('POST', 'auth/login/', json={
            'username': username,
            'password': password
        })
        
        if success and 'access' in data:
            self.set_auth_tokens(data['access'], data['refresh'])
            return True, 'Login successful'
        else:
            error_msg = data.get('error', 'Login failed')
            return False, error_msg
    
    def logout(self) -> Tuple[bool, str]:
        """Logout user"""
        if self.refresh_token:
            success, data = self._make_request('POST', 'auth/logout/', json={
                'refresh': self.refresh_token
            })
        
        self.clear_auth_tokens()
        return True, 'Logged out successfully'
    
    def upload_csv(self, file_path: str) -> Tuple[bool, Dict[str, Any], str]:
        """Upload CSV file"""
        try:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                success, data = self._make_request('POST', 'upload/', files=files)
            
            if success:
                return True, data, 'Upload successful'
            else:
                error_msg = data.get('error', 'Upload failed')
                return False, data, error_msg
                
        except FileNotFoundError:
            return False, {}, 'File not found'
        except Exception as e:
            return False, {}, f'Upload error: {str(e)}'
    
    def get_summary(self) -> Tuple[bool, Dict[str, Any], str]:
        """Get analytics summary"""
        success, data = self._make_request('GET', 'summary/')
        
        if success:
            return True, data, 'Summary retrieved'
        else:
            error_msg = data.get('error', 'Failed to get summary')
            return False, data, error_msg
    
    def get_history(self) -> Tuple[bool, Dict[str, Any], str]:
        """Get upload history"""
        success, data = self._make_request('GET', 'history/')
        
        if success:
            return True, data, 'History retrieved'
        else:
            error_msg = data.get('error', 'Failed to get history')
            return False, data, error_msg
    
    def download_pdf_report(self, upload_id: Optional[int] = None) -> Tuple[bool, bytes, str]:
        """Download PDF report"""
        params = {}
        if upload_id:
            params['upload_id'] = upload_id
        
        try:
            url = f"{self.base_url}/report/pdf/"
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                return True, response.content, 'PDF downloaded'
            else:
                return False, b'', f'Download failed: {response.status_code}'
                
        except requests.exceptions.RequestException as e:
            return False, b'', f'Download error: {str(e)}'
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.access_token is not None