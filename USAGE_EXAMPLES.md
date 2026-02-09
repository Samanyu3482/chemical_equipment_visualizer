# Usage Examples and API Documentation

## Sample Data Format

### CSV File Structure
Your CSV file should follow this exact format:

```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-001,Centrifugal Pump,150.5,45.2,85.3
Heat-Exchanger-001,Shell and Tube,200.0,30.5,120.7
Reactor-001,CSTR,75.8,25.0,95.4
Compressor-001,Rotary,300.2,60.8,110.2
Valve-001,Control Valve,180.5,40.0,75.8
```

### Data Requirements
- **Equipment Name**: Unique identifier (text, max 100 characters)
- **Type**: Equipment category (text, max 50 characters)
- **Flowrate**: Numeric value (float, positive)
- **Pressure**: Numeric value (float, positive)
- **Temperature**: Numeric value (float, can be negative for Celsius)

## API Usage Examples

### Authentication

#### Register New User
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "engineer1",
    "email": "engineer1@company.com",
    "password": "securepassword123"
  }'
```

**Response:**
```json
{
  "message": "User created successfully"
}
```

#### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "engineer1",
    "password": "securepassword123"
  }'
```

**Response:**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

### Data Upload

#### Upload CSV File
```bash
curl -X POST http://localhost:8000/api/upload/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@sample_equipment_data.csv"
```

**Response:**
```json
{
  "success": true,
  "upload_id": 1,
  "record_count": 5,
  "warnings": []
}
```

#### Error Response Example
```json
{
  "success": false,
  "errors": [
    "Missing required column: Temperature",
    "Invalid numeric value in row 3: 'invalid_number'"
  ]
}
```

### Analytics

#### Get Summary Statistics
```bash
curl -X GET http://localhost:8000/api/summary/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
{
  "total_equipment": 5,
  "average_flowrate": 181.4,
  "average_pressure": 40.3,
  "average_temperature": 97.48,
  "type_distribution": {
    "Centrifugal Pump": 1,
    "Shell and Tube": 1,
    "CSTR": 1,
    "Rotary": 1,
    "Control Valve": 1
  }
}
```

### History Management

#### Get Upload History
```bash
curl -X GET http://localhost:8000/api/history/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response:**
```json
[
  {
    "id": 1,
    "filename": "sample_equipment_data.csv",
    "upload_timestamp": "2024-02-04T10:30:00Z",
    "record_count": 5,
    "user": "engineer1"
  }
]
```

### PDF Report Generation

#### Download PDF Report
```bash
curl -X GET "http://localhost:8000/api/report/pdf/?upload_id=1&include_charts=true" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -o equipment_report.pdf
```

## Web Interface Usage

### 1. User Registration/Login
1. Open `http://localhost:3000` in your browser
2. Click "Register" to create a new account or "Login" with existing credentials
3. Fill in the required information and submit

### 2. Uploading Data
1. Navigate to the "Upload" page
2. Drag and drop your CSV file or click "Browse" to select
3. Review the file information and click "Upload"
4. View upload results and any validation messages

### 3. Viewing Analytics
1. Go to the "Analytics" page after successful upload
2. View summary statistics at the top
3. Explore interactive charts:
   - Equipment type distribution (pie chart)
   - Average parameter values (bar chart)
   - Data table with individual records

### 4. Managing History
1. Visit the "History" page to see recent uploads
2. Click on any upload to view details
3. Download PDF reports for specific uploads
4. View metadata including timestamps and record counts

## Desktop Application Usage

### 1. Starting the Application
```bash
cd frontend-desktop
python main.py
```

### 2. Authentication
1. The login dialog appears automatically
2. Register a new account or login with existing credentials
3. Check "Remember username" to save login information

### 3. Navigation
- Use the navigation buttons at the top: Upload, Analytics, History
- Or use keyboard shortcuts: Ctrl+1, Ctrl+2, Ctrl+3
- Access functions through the menu bar

### 4. File Upload
1. Click "Upload Data" or use File → Upload CSV
2. Drag and drop files or browse for CSV files
3. Monitor upload progress with the progress bar
4. View detailed results in the results section

### 5. Analytics Dashboard
1. Click "Refresh Data" to load latest analytics
2. View summary statistics and charts
3. Export charts using "Export Charts" button
4. Scroll down to see the data table

### 6. History Management
1. Click "Refresh History" to load upload history
2. Select uploads to view details
3. Download PDF reports for any upload
4. Use "Download Latest PDF" for the most recent upload

## Common Workflows

### Workflow 1: First-Time Setup
1. Start the backend server: `python manage.py runserver`
2. Start the web frontend: `npm start` (in frontend-web directory)
3. Register a new user account
4. Upload the sample CSV file
5. Explore analytics and generate a PDF report

### Workflow 2: Regular Data Analysis
1. Login to your preferred interface (web or desktop)
2. Upload new CSV data
3. Compare with historical data in the History section
4. Generate and download PDF reports for documentation
5. Export charts for presentations

### Workflow 3: Batch Processing
1. Prepare multiple CSV files with consistent format
2. Upload files one by one (system maintains 5-record history)
3. Use the History page to track all uploads
4. Generate comparative reports for different time periods

## Error Handling Examples

### CSV Validation Errors
```
❌ Upload Failed!

Error: CSV validation failed

Details:
• Missing required column: Temperature
• Invalid data type in row 3, column 'Flowrate': expected number, got 'N/A'
• Empty value in row 5, column 'Pressure'
```

### Authentication Errors
```
❌ Login Failed!

Error: Invalid credentials

Please check your username and password and try again.
```

### Network Errors
```
❌ Connection Failed!

Error: Network error: Connection refused

Please ensure the backend server is running on http://localhost:8000
```

## Performance Tips

### Large Files
- Keep CSV files under 10MB for optimal performance
- For larger datasets, consider splitting into multiple files
- Use the history feature to track multiple related uploads

### Chart Performance
- Charts are optimized for up to 1000 data points
- Large datasets are automatically aggregated
- Use the export feature for high-resolution charts

### Memory Usage
- The application processes data in memory
- Close unused browser tabs to free memory
- Restart the desktop application if performance degrades

## Troubleshooting

### Backend Issues
```bash
# Check if server is running
curl http://localhost:8000/api/

# View server logs
python manage.py runserver --verbosity=2

# Reset database
python manage.py flush
python manage.py migrate
```

### Frontend Issues
```bash
# Clear React cache
npm start -- --reset-cache

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install
```

### Desktop Application Issues
```bash
# Test dependencies
python test_desktop.py

# Reinstall PyQt5
pip uninstall PyQt5
pip install PyQt5

# Clear application settings (macOS)
rm ~/Library/Preferences/com.EquipmentAnalytics.ChemicalEquipmentVisualizer.plist
```

## Advanced Configuration

### Custom API Endpoint
For desktop application, edit the configuration:
```python
# In utils/config.py
self.api_base_url = 'http://your-server:8000/api'
```

### CORS Settings
For web application, update Django settings:
```python
# In backend/equipment_visualizer/settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://your-domain.com",
]
```

### File Upload Limits
```python
# In Django settings
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024  # 10MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10MB
```

This documentation provides comprehensive examples for using all aspects of the Chemical Equipment Parameter Visualizer system.