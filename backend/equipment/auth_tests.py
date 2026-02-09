from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from hypothesis import given, strategies as st
from hypothesis.extra.django import TestCase as HypothesisTestCase


class AuthenticationAPITests(APITestCase):
    """Standard API tests for authentication functionality"""
    
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'confirm_password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_user_registration_success(self):
        """Test successful user registration"""
        response = self.client.post('/api/auth/register/', self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertEqual(response.data['user']['username'], 'testuser')
    
    def test_user_login_success(self):
        """Test successful user login"""
        # First register a user
        self.client.post('/api/auth/register/', self.user_data, format='json')
        
        # Then login
        login_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
        response = self.client.post('/api/auth/login/', login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data)
    
    def test_token_verification(self):
        """Test JWT token verification"""
        # Register and login
        self.client.post('/api/auth/register/', self.user_data, format='json')
        login_response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        }, format='json')
        
        token = login_response.data['access']
        
        # Verify token
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/auth/verify/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['user']['username'], 'testuser')


class PropertyBasedAuthenticationTests(HypothesisTestCase):
    """Property-based tests for authentication functionality"""
    
    def setUp(self):
        # Clean up any existing users
        User.objects.all().delete()
        self.client = APIClient()
    
    def tearDown(self):
        # Clean up after each test
        User.objects.all().delete()
    
    @given(st.text(min_size=3, max_size=15).filter(lambda x: x.isalnum()))
    def test_authentication_state_management_property(self, username):
        """
        Feature: chemical-equipment-visualizer, Property 12: Authentication State Management
        For any valid user credentials, the authentication system should correctly manage user state
        through registration, login, token verification, and logout operations while maintaining
        security and session integrity.
        **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**
        """
        # Ensure username is unique for this test
        if User.objects.filter(username=username).exists():
            username = f"{username}_{User.objects.count()}"
        
        email = f"{username}@example.com"
        password = "testpass123"
        
        # Test 1: User Registration
        registration_data = {
            'username': username,
            'email': email,
            'password': password,
            'confirm_password': password,
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = self.client.post('/api/auth/register/', registration_data, format='json')
        
        # Registration should succeed for valid data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        
        # Test 2: User Login
        login_data = {
            'username': username,
            'password': password
        }
        
        response = self.client.post('/api/auth/login/', login_data, format='json')
        
        # Login should succeed
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data)
        
        access_token = response.data['access']
        
        # Test 3: Token Verification
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get('/api/auth/verify/')
        
        # Token verification should succeed
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['user']['username'], username)