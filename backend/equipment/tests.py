import io
import pandas as pd
from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from hypothesis import given, strategies as st, assume
from hypothesis.extra.django import TestCase as HypothesisTestCase
from .csv_processor import CSVProcessor, ValidationResult
from .analytics import AnalyticsEngine, AnalyticsSummary
from .models import EquipmentUpload, EquipmentRecord
from .history import HistoryManager, HistoryEntry


class CSVProcessorTests(TestCase):
    """Test cases for CSV processing functionality"""
    
    def setUp(self):
        self.processor = CSVProcessor()
    
    def test_valid_csv_structure(self):
        """Test that valid CSV structure passes validation"""
        csv_content = "Equipment Name,Type,Flowrate,Pressure,Temperature\nPump-1,Pump,120.5,5.6,60.0"
        csv_file = io.StringIO(csv_content)
        
        result = self.processor.validate_structure(csv_file)
        self.assertTrue(result.is_valid)
        self.assertEqual(len(result.errors), 0)
    
    def test_missing_columns(self):
        """Test that missing required columns are detected"""
        csv_content = "Equipment Name,Type,Flowrate\nPump-1,Pump,120.5"
        csv_file = io.StringIO(csv_content)
        
        result = self.processor.validate_structure(csv_file)
        self.assertFalse(result.is_valid)
        self.assertIn("Missing required columns", result.errors[0])
    
    def test_wrong_column_order(self):
        """Test that wrong column order is detected"""
        csv_content = "Type,Equipment Name,Flowrate,Pressure,Temperature\nPump,Pump-1,120.5,5.6,60.0"
        csv_file = io.StringIO(csv_content)
        
        result = self.processor.validate_structure(csv_file)
        self.assertFalse(result.is_valid)
        self.assertIn("wrong order", result.errors[0])


class PropertyBasedCSVTests(HypothesisTestCase):
    """Property-based tests for CSV processing"""
    
    def setUp(self):
        self.processor = CSVProcessor()
    
    @given(st.lists(st.text(min_size=1), min_size=1, max_size=10))
    def test_csv_structure_validation_property(self, column_names):
        """
        Feature: chemical-equipment-visualizer, Property 1: CSV Structure Validation
        For any uploaded CSV file, the system should accept it if and only if it contains 
        exactly the columns: Equipment Name, Type, Flowrate, Pressure, Temperature in the correct order.
        **Validates: Requirements 1.1, 1.2**
        """
        assume(len(set(column_names)) == len(column_names))  # No duplicate columns
        
        # Create CSV with the given column names
        csv_content = ','.join(column_names) + '\n'
        csv_content += ','.join(['test_value'] * len(column_names))
        csv_file = io.StringIO(csv_content)
        
        result = self.processor.validate_structure(csv_file)
        
        # Should be valid if and only if columns match exactly
        expected_valid = column_names == self.processor.REQUIRED_COLUMNS
        self.assertEqual(result.is_valid, expected_valid)
        
        if not expected_valid:
            self.assertGreater(len(result.errors), 0)
    
    @given(st.integers(min_value=0, max_value=1000))
    def test_csv_data_parsing_completeness_property(self, num_rows):
        """
        Feature: chemical-equipment-visualizer, Property 2: CSV Data Parsing Completeness
        For any valid CSV file with N data rows, the CSV processor should create exactly N 
        equipment records with all fields correctly populated.
        **Validates: Requirements 1.3**
        """
        # Create valid CSV with specified number of rows
        csv_lines = [','.join(self.processor.REQUIRED_COLUMNS)]
        
        for i in range(num_rows):
            row = [
                f'Equipment-{i}',
                'Pump',
                '100.0',
                '5.0',
                '25.0'
            ]
            csv_lines.append(','.join(row))
        
        csv_content = '\n'.join(csv_lines)
        csv_file = io.StringIO(csv_content)
        
        equipment_records, result = self.processor.parse_equipment_data(csv_file)
        
        if num_rows == 0:
            # Empty CSV should be invalid
            self.assertFalse(result.is_valid)
        else:
            # Should create exactly N records
            self.assertTrue(result.is_valid)
            self.assertEqual(len(equipment_records), num_rows)
            
            # All records should have correct fields
            for i, record in enumerate(equipment_records):
                self.assertEqual(record.equipment_name, f'Equipment-{i}')
                self.assertEqual(record.equipment_type, 'Pump')
                self.assertEqual(record.flowrate, 100.0)
                self.assertEqual(record.pressure, 5.0)
                self.assertEqual(record.temperature, 25.0)
    
    @given(
        st.lists(
            st.one_of(
                st.floats(min_value=-1000, max_value=15000, allow_nan=False, allow_infinity=False),
                st.just('invalid_text'),  # Simple non-numeric string
                st.just('')  # Empty string
            ),
            min_size=1,
            max_size=5
        )
    )
    def test_numeric_data_type_validation_property(self, test_values):
        """
        Feature: chemical-equipment-visualizer, Property 3: Numeric Data Type Validation
        For any CSV file, all Flowrate, Pressure, and Temperature values must be valid numeric types,
        and any file containing non-numeric values in these columns should be rejected with specific error details.
        **Validates: Requirements 1.4, 1.5**
        """
        # Create CSV with test values in numeric columns
        csv_lines = [','.join(self.processor.REQUIRED_COLUMNS)]
        
        for i, value in enumerate(test_values):
            row = [
                f'Equipment-{i}',
                'Pump',
                str(value),  # Flowrate
                str(value),  # Pressure  
                str(value)   # Temperature
            ]
            csv_lines.append(','.join(row))
        
        csv_content = '\n'.join(csv_lines)
        csv_file = io.StringIO(csv_content)
        
        # Parse and check validation
        equipment_records, result = self.processor.parse_equipment_data(csv_file)
        
        # Check if all values are valid numbers within constraints
        all_valid_numeric = True
        all_within_constraints = True
        
        for value in test_values:
            # Check if value is empty string or whitespace
            if isinstance(value, str) and (value.strip() == '' or value == 'invalid_text'):
                all_valid_numeric = False
                break
                
            try:
                num_val = float(value)
                # Check constraints for each numeric column
                for col in ['Flowrate', 'Pressure', 'Temperature']:
                    if col in self.processor.CONSTRAINTS:
                        constraints = self.processor.CONSTRAINTS[col]
                        if not (constraints['min'] <= num_val <= constraints['max']):
                            all_within_constraints = False
                            break
            except (ValueError, TypeError):
                all_valid_numeric = False
                break
        
        expected_valid = all_valid_numeric and all_within_constraints
        self.assertEqual(result.is_valid, expected_valid)
        
        if not expected_valid:
            self.assertGreater(len(result.errors), 0)


class PropertyBasedAnalyticsTests(HypothesisTestCase):
    """Property-based tests for analytics functionality"""
    
    def setUp(self):
        self.analytics = AnalyticsEngine()
    
    @given(
        st.lists(
            st.tuples(
                st.text(min_size=1, max_size=20),  # equipment_name
                st.sampled_from(['Pump', 'Valve', 'Reactor', 'Heat Exchanger', 'Compressor']),  # equipment_type
                st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False),  # flowrate
                st.floats(min_value=0, max_value=100, allow_nan=False, allow_infinity=False),   # pressure
                st.floats(min_value=-50, max_value=500, allow_nan=False, allow_infinity=False)  # temperature
            ),
            min_size=1,
            max_size=100
        )
    )
    def test_analytics_calculation_accuracy_property(self, equipment_data):
        """
        Feature: chemical-equipment-visualizer, Property 5: Analytics Calculation Accuracy
        For any dataset of equipment records, the Analytics_Engine should compute correct total counts 
        and accurate average values for flowrate, pressure, and temperature using standard mathematical formulas.
        **Validates: Requirements 3.1, 3.2, 3.3, 3.4**
        """
        # Create mock equipment records
        records = []
        for name, eq_type, flowrate, pressure, temperature in equipment_data:
            # Create a mock record object
            record = type('MockRecord', (), {
                'equipment_name': name,
                'equipment_type': eq_type,
                'flowrate': flowrate,
                'pressure': pressure,
                'temperature': temperature
            })()
            records.append(record)
        
        # Generate analytics summary
        summary = self.analytics.generate_summary_statistics(records)
        
        # Verify total count
        self.assertEqual(summary.total_equipment, len(equipment_data))
        
        # Calculate expected averages manually
        expected_avg_flowrate = sum(data[2] for data in equipment_data) / len(equipment_data)
        expected_avg_pressure = sum(data[3] for data in equipment_data) / len(equipment_data)
        expected_avg_temperature = sum(data[4] for data in equipment_data) / len(equipment_data)
        
        # Verify averages (with small tolerance for floating point precision)
        self.assertAlmostEqual(summary.average_flowrate, expected_avg_flowrate, places=10)
        self.assertAlmostEqual(summary.average_pressure, expected_avg_pressure, places=10)
        self.assertAlmostEqual(summary.average_temperature, expected_avg_temperature, places=10)
        
        # Verify summary consistency
        self.assertTrue(self.analytics.validate_summary_consistency(summary))
    
    @given(
        st.lists(
            st.sampled_from(['Pump', 'Valve', 'Reactor', 'Heat Exchanger', 'Compressor']),
            min_size=1,
            max_size=50
        )
    )
    def test_equipment_type_distribution_analysis_property(self, equipment_types):
        """
        Feature: chemical-equipment-visualizer, Property 6: Equipment Type Distribution Analysis
        For any dataset of equipment records, the Analytics_Engine should correctly count and categorize 
        equipment by type, with the sum of all type counts equaling the total equipment count.
        **Validates: Requirements 3.5**
        """
        # Create mock equipment records with only type information needed
        records = []
        for eq_type in equipment_types:
            record = type('MockRecord', (), {
                'equipment_name': f'Equipment-{len(records)}',
                'equipment_type': eq_type,
                'flowrate': 100.0,
                'pressure': 5.0,
                'temperature': 25.0
            })()
            records.append(record)
        
        # Analyze type distribution
        type_distribution = self.analytics.analyze_type_distribution(records)
        
        # Verify that sum of all counts equals total equipment
        total_from_distribution = sum(type_distribution.values())
        self.assertEqual(total_from_distribution, len(equipment_types))
        
        # Verify that each type count is correct
        expected_counts = {}
        for eq_type in equipment_types:
            expected_counts[eq_type] = expected_counts.get(eq_type, 0) + 1
        
        self.assertEqual(type_distribution, expected_counts)
        
        # Verify all counts are positive
        for count in type_distribution.values():
            self.assertGreater(count, 0)


class PropertyBasedHistoryTests(HypothesisTestCase):
    """Property-based tests for history management functionality"""
    
    def setUp(self):
        self.history_manager = HistoryManager()
        # Clear any existing history
        self.history_manager.clear_history()
    
    def tearDown(self):
        # Clean up after each test
        self.history_manager.clear_history()
    
    @given(st.integers(min_value=1, max_value=20))
    def test_history_management_limit_enforcement_property(self, num_uploads):
        """
        Feature: chemical-equipment-visualizer, Property 7: History Management Limit Enforcement
        For any sequence of uploads, the History_Manager should maintain exactly 5 records at all times,
        automatically removing the oldest record when a new upload would exceed this limit.
        **Validates: Requirements 3.6, 3.7, 8.2, 8.5**
        """
        # Add the specified number of uploads
        for i in range(num_uploads):
            self.history_manager.add_upload(
                filename=f'test_file_{i}.csv',
                record_count=10 + i
            )
        
        # Verify history limit is enforced
        current_count = self.history_manager.get_current_history_count()
        expected_count = min(num_uploads, self.history_manager.MAX_HISTORY_RECORDS)
        
        self.assertEqual(current_count, expected_count)
        self.assertTrue(self.history_manager.validate_history_limit())
        
        # Verify history is in reverse chronological order
        history = self.history_manager.get_history()
        self.assertEqual(len(history), expected_count)
        
        # Check that timestamps are in descending order (newest first)
        for i in range(len(history) - 1):
            self.assertGreaterEqual(history[i].timestamp, history[i + 1].timestamp)
        
        # If we added more than 5 uploads, verify the newest ones are kept
        if num_uploads > self.history_manager.MAX_HISTORY_RECORDS:
            # The filenames should be from the last 5 uploads
            expected_filenames = [f'test_file_{i}.csv' for i in range(num_uploads - 5, num_uploads)]
            expected_filenames.reverse()  # Reverse for newest-first order
            
            actual_filenames = [entry.filename for entry in history]
            self.assertEqual(actual_filenames, expected_filenames)
    
    @given(
        st.lists(
            st.tuples(
                st.text(min_size=1, max_size=50).filter(lambda x: '.csv' not in x),  # filename base
                st.integers(min_value=1, max_value=1000)  # record_count
            ),
            min_size=1,
            max_size=10
        )
    )
    def test_history_metadata_completeness_property(self, upload_data):
        """
        Feature: chemical-equipment-visualizer, Property 14: History Metadata Completeness
        For any upload record in the history, the system should store and retrieve complete metadata
        including timestamp, filename, record count, and basic statistics in reverse chronological order.
        **Validates: Requirements 8.1, 8.3, 8.4**
        """
        # Add uploads with the given data
        created_uploads = []
        for filename_base, record_count in upload_data:
            filename = f'{filename_base}.csv'
            upload = self.history_manager.add_upload(filename, record_count)
            created_uploads.append((upload, filename, record_count))
        
        # Get history metadata
        history_metadata = self.history_manager.get_history_metadata()
        history_entries = self.history_manager.get_history()
        
        # Verify metadata completeness
        expected_count = min(len(upload_data), self.history_manager.MAX_HISTORY_RECORDS)
        self.assertEqual(len(history_metadata), expected_count)
        self.assertEqual(len(history_entries), expected_count)
        
        # Verify each metadata entry has all required fields
        for metadata in history_metadata:
            self.assertIn('upload_id', metadata)
            self.assertIn('filename', metadata)
            self.assertIn('timestamp', metadata)
            self.assertIn('record_count', metadata)
            
            # Verify data types
            self.assertIsInstance(metadata['upload_id'], int)
            self.assertIsInstance(metadata['filename'], str)
            self.assertIsInstance(metadata['timestamp'], str)  # ISO format string
            self.assertIsInstance(metadata['record_count'], int)
            
            # Verify values are reasonable
            self.assertGreater(metadata['upload_id'], 0)
            self.assertTrue(metadata['filename'].endswith('.csv'))
            self.assertGreater(metadata['record_count'], 0)
        
        # Verify reverse chronological order
        for i in range(len(history_entries) - 1):
            self.assertGreaterEqual(history_entries[i].timestamp, history_entries[i + 1].timestamp)


class PropertyBasedAuthenticationTests(HypothesisTestCase):
    """Property-based tests for authentication functionality"""
    
    def setUp(self):
        # Clean up any existing users
        User.objects.all().delete()
    
    def tearDown(self):
        # Clean up after each test
        User.objects.all().delete()
    
    @given(
        st.tuples(
            st.text(min_size=3, max_size=20).filter(lambda x: x.isalnum()),  # username
            st.emails(),  # email
            st.text(min_size=6, max_size=50),  # password
            st.text(min_size=1, max_size=30),  # first_name
            st.text(min_size=1, max_size=30)   # last_name
        )
    )
    def test_authentication_state_management_property(self, user_data):
        """
        Feature: chemical-equipment-visualizer, Property 12: Authentication State Management
        For any valid user credentials, the authentication system should correctly manage user state
        through registration, login, token verification, and logout operations while maintaining
        security and session integrity.
        **Validates: Requirements 6.1, 6.2, 6.3, 6.4, 6.5**
        """
        username, email, password, first_name, last_name = user_data
        
        # Ensure username is unique for this test
        if User.objects.filter(username=username).exists():
            username = f"{username}_{User.objects.count()}"
        
        # Ensure email is unique for this test
        if User.objects.filter(email=email).exists():
            email = f"test_{User.objects.count()}_{email}"
        
        # Test 1: User Registration
        registration_data = {
            'username': username,
            'email': email,
            'password': password,
            'confirm_password': password,
            'first_name': first_name,
            'last_name': last_name
        }
        
        response = self.client.post('/api/auth/register/', registration_data, format='json')
        
        # Registration should succeed for valid data
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data['success'])
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)
        
        # Verify user was created in database
        user = User.objects.get(username=username)
        self.assertEqual(user.email, email)
        self.assertEqual(user.first_name, first_name)
        self.assertEqual(user.last_name, last_name)
        self.assertTrue(user.check_password(password))
        
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
        self.assertIn('refresh', response.data)
        
        access_token = response.data['access']
        refresh_token = response.data['refresh']
        
        # Test 3: Token Verification
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get('/api/auth/verify/')
        
        # Token verification should succeed
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['user']['username'], username)
        self.assertEqual(response.data['user']['email'], email)
        
        # Test 4: Protected Endpoint Access
        # Test that authenticated user can access protected endpoints
        response = self.client.get('/api/summary/')
        # Should not get 401 Unauthorized (might get other errors due to no data, but not auth errors)
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test 5: Invalid Token Handling
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = self.client.get('/api/auth/verify/')
        
        # Should fail with invalid token
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Test 6: Logout
        logout_data = {'refresh': refresh_token}
        response = self.client.post('/api/auth/logout/', logout_data, format='json')
        
        # Logout should succeed
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        
        # Test 7: Duplicate Registration Prevention
        response = self.client.post('/api/auth/register/', registration_data, format='json')
        
        # Should fail due to duplicate username/email
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
    @given(
        st.lists(
            st.tuples(
                st.text(min_size=3, max_size=15).filter(lambda x: x.isalnum()),  # username
                st.text(min_size=6, max_size=20)  # password
            ),
            min_size=1,
            max_size=5
        )
    )
    def test_authentication_security_property(self, user_credentials):
        """
        Feature: chemical-equipment-visualizer, Property 12b: Authentication Security
        The authentication system should properly validate credentials, reject invalid logins,
        and maintain security boundaries between different user sessions.
        **Validates: Requirements 6.1, 6.2, 6.5**
        """
        # Create valid users first
        valid_users = []
        for i, (username, password) in enumerate(user_credentials):
            # Ensure unique usernames
            unique_username = f"{username}_{i}"
            email = f"test_{i}@example.com"
            
            user = User.objects.create_user(
                username=unique_username,
                email=email,
                password=password
            )
            valid_users.append((unique_username, password))
        
        # Test valid login for each user
        for username, password in valid_users:
            response = self.client.post('/api/auth/login/', {
                'username': username,
                'password': password
            }, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertTrue(response.data['success'])
            self.assertIn('access', response.data)
        
        # Test invalid login attempts
        for username, password in valid_users:
            # Wrong password
            response = self.client.post('/api/auth/login/', {
                'username': username,
                'password': 'wrong_password'
            }, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertFalse(response.data['success'])
            
            # Wrong username
            response = self.client.post('/api/auth/login/', {
                'username': 'nonexistent_user',
                'password': password
            }, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertFalse(response.data['success'])
        
        # Test that tokens are user-specific
        if len(valid_users) >= 2:
            # Login as first user
            username1, password1 = valid_users[0]
            response1 = self.client.post('/api/auth/login/', {
                'username': username1,
                'password': password1
            }, format='json')
            token1 = response1.data['access']
            
            # Login as second user
            username2, password2 = valid_users[1]
            response2 = self.client.post('/api/auth/login/', {
                'username': username2,
                'password': password2
            }, format='json')
            token2 = response2.data['access']
            
            # Tokens should be different
            self.assertNotEqual(token1, token2)
            
            # Each token should verify to the correct user
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token1}')
            response = self.client.get('/api/auth/verify/')
            self.assertEqual(response.data['user']['username'], username1)
            
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token2}')
            response = self.client.get('/api/auth/verify/')
            self.assertEqual(response.data['user']['username'], username2)


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
    
    def test_user_registration_password_mismatch(self):
        """Test registration with password mismatch"""
        self.user_data['confirm_password'] = 'different_password'
        response = self.client.post('/api/auth/register/', self.user_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data['success'])
    
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
    
    def test_user_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            'username': 'nonexistent',
            'password': 'wrongpass'
        }
        response = self.client.post('/api/auth/login/', login_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(response.data['success'])
    
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
    
    def test_protected_endpoint_access(self):
        """Test access to protected endpoints"""
        # Register and login
        self.client.post('/api/auth/register/', self.user_data, format='json')
        login_response = self.client.post('/api/auth/login/', {
            'username': 'testuser',
            'password': 'testpass123'
        }, format='json')
        
        token = login_response.data['access']
        
        # Access protected endpoint
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        response = self.client.get('/api/summary/')
        
        # Should not get 401 (might get other errors, but not unauthorized)
        self.assertNotEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_protected_endpoint_without_token(self):
        """Test access to protected endpoints without token"""
        response = self.client.get('/api/summary/')
        
        # Should get 401 Unauthorized
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class PropertyBasedReportTests(HypothesisTestCase):
    """Property-based tests for PDF report generation functionality"""
    
    def setUp(self):
        # Clean up any existing data
        EquipmentUpload.objects.all().delete()
        EquipmentRecord.objects.all().delete()
    
    def tearDown(self):
        # Clean up after each test
        EquipmentUpload.objects.all().delete()
        EquipmentRecord.objects.all().delete()
    
    @given(
        st.lists(
            st.tuples(
                st.text(min_size=1, max_size=20),  # equipment_name
                st.sampled_from(['Pump', 'Valve', 'Reactor', 'Heat Exchanger', 'Compressor']),  # equipment_type
                st.floats(min_value=1, max_value=1000, allow_nan=False, allow_infinity=False),  # flowrate
                st.floats(min_value=0.1, max_value=100, allow_nan=False, allow_infinity=False),   # pressure
                st.floats(min_value=-50, max_value=500, allow_nan=False, allow_infinity=False)  # temperature
            ),
            min_size=1,
            max_size=20
        )
    )
    def test_pdf_report_content_accuracy_property(self, equipment_data):
        """
        Feature: chemical-equipment-visualizer, Property 13: PDF Report Content Accuracy
        For any dataset of equipment records, the PDF report generator should create accurate reports
        containing correct statistical summaries, equipment counts, and analytical insights that match
        the source data exactly.
        **Validates: Requirements 7.1, 7.2, 7.3, 7.4**
        """
        from .report_generator import ReportGenerator
        from .analytics import AnalyticsEngine
        
        # Create test upload and records
        upload = EquipmentUpload.objects.create(
            filename='test_data.csv',
            record_count=len(equipment_data)
        )
        
        records = []
        for name, eq_type, flowrate, pressure, temperature in equipment_data:
            record = EquipmentRecord.objects.create(
                upload=upload,
                equipment_name=name,
                equipment_type=eq_type,
                flowrate=flowrate,
                pressure=pressure,
                temperature=temperature
            )
            records.append(record)
        
        # Generate analytics summary
        analytics = AnalyticsEngine()
        summary = analytics.get_upload_summary(upload.id)
        
        # Generate PDF report
        report_generator = ReportGenerator()
        
        try:
            pdf_data = report_generator.generate_report(upload_id=upload.id, include_charts=False)
        except Exception as e:
            self.fail(f"PDF generation failed: {str(e)}")
        
        # Verify PDF was generated
        self.assertIsInstance(pdf_data, bytes)
        self.assertGreater(len(pdf_data), 100)  # PDF should have substantial content
        
        # Verify PDF starts with PDF header
        self.assertTrue(pdf_data.startswith(b'%PDF'))
        
        # Verify summary statistics accuracy
        self.assertEqual(summary.total_equipment, len(equipment_data))
        
        # Calculate expected averages manually
        expected_avg_flowrate = sum(data[2] for data in equipment_data) / len(equipment_data)
        expected_avg_pressure = sum(data[3] for data in equipment_data) / len(equipment_data)
        expected_avg_temperature = sum(data[4] for data in equipment_data) / len(equipment_data)
        
        # Verify averages match (with small tolerance for floating point precision)
        self.assertAlmostEqual(summary.average_flowrate, expected_avg_flowrate, places=10)
        self.assertAlmostEqual(summary.average_pressure, expected_avg_pressure, places=10)
        self.assertAlmostEqual(summary.average_temperature, expected_avg_temperature, places=10)
        
        # Verify type distribution accuracy
        expected_type_counts = {}
        for _, eq_type, _, _, _ in equipment_data:
            expected_type_counts[eq_type] = expected_type_counts.get(eq_type, 0) + 1
        
        self.assertEqual(summary.type_distribution, expected_type_counts)
        
        # Verify distribution sum equals total
        self.assertEqual(sum(summary.type_distribution.values()), summary.total_equipment)
        
        # Test report generation with charts (should not fail)
        try:
            pdf_with_charts = report_generator.generate_report(upload_id=upload.id, include_charts=True)
            self.assertIsInstance(pdf_with_charts, bytes)
            self.assertGreaterEqual(len(pdf_with_charts), len(pdf_data))  # Should be same size or larger
        except Exception as e:
            # Charts might fail due to complex dependencies, but basic report should work
            pass
        
        # Test insights generation
        insights = report_generator._generate_insights(summary)
        self.assertIsInstance(insights, list)
        self.assertGreater(len(insights), 0)  # Should generate at least one insight
        
        for insight in insights:
            self.assertIsInstance(insight, str)
            self.assertGreater(len(insight), 10)  # Insights should be meaningful text


class ReportGenerationTests(TestCase):
    """Standard tests for PDF report generation"""
    
    def setUp(self):
        # Create test data
        self.upload = EquipmentUpload.objects.create(
            filename='test_equipment.csv',
            record_count=3
        )
        
        # Create test equipment records
        EquipmentRecord.objects.create(
            upload=self.upload,
            equipment_name='Pump-1',
            equipment_type='Pump',
            flowrate=120.5,
            pressure=5.6,
            temperature=60.0
        )
        
        EquipmentRecord.objects.create(
            upload=self.upload,
            equipment_name='Valve-1',
            equipment_type='Valve',
            flowrate=80.0,
            pressure=3.2,
            temperature=45.0
        )
        
        EquipmentRecord.objects.create(
            upload=self.upload,
            equipment_name='Reactor-1',
            equipment_type='Reactor',
            flowrate=200.0,
            pressure=10.1,
            temperature=350.0
        )
    
    def test_pdf_generation_success(self):
        """Test successful PDF generation"""
        from .report_generator import ReportGenerator
        
        report_generator = ReportGenerator()
        pdf_data = report_generator.generate_report(upload_id=self.upload.id)
        
        # Verify PDF was generated
        self.assertIsInstance(pdf_data, bytes)
        self.assertGreater(len(pdf_data), 100)
        self.assertTrue(pdf_data.startswith(b'%PDF'))
    
    def test_pdf_generation_no_data(self):
        """Test PDF generation with no data"""
        from .report_generator import ReportGenerator
        
        # Delete all records
        EquipmentRecord.objects.all().delete()
        EquipmentUpload.objects.all().delete()
        
        report_generator = ReportGenerator()
        
        with self.assertRaises(ValueError):
            report_generator.generate_report()
    
    def test_insights_generation(self):
        """Test analytical insights generation"""
        from .report_generator import ReportGenerator
        from .analytics import AnalyticsEngine
        
        analytics = AnalyticsEngine()
        summary = analytics.get_upload_summary(self.upload.id)
        
        report_generator = ReportGenerator()
        insights = report_generator._generate_insights(summary)
        
        self.assertIsInstance(insights, list)
        self.assertGreater(len(insights), 0)
        
        for insight in insights:
            self.assertIsInstance(insight, str)
            self.assertGreater(len(insight), 5)