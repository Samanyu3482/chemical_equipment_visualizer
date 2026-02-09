# Chemical Equipment Parameter Visualizer

A comprehensive data visualization application for analyzing chemical equipment parameters from CSV data. The system provides both web and desktop interfaces backed by a Django REST API with property-based testing for reliability.

## Features

### Core Functionality
- **CSV Data Upload**: Upload and validate chemical equipment parameter data
- **Data Analytics**: Calculate averages, distributions, and statistical summaries
- **Interactive Visualizations**: Charts and graphs for data analysis
- **History Management**: Track and manage upload history (5-record limit)
- **PDF Report Generation**: Generate professional reports with charts and statistics
- **User Authentication**: Secure JWT-based authentication system

### Multi-Platform Support
- **Web Interface**: React.js application with Chart.js visualizations
- **Desktop Application**: PyQt5 application with modern UI, animations, and Matplotlib charts
- **REST API**: Django backend serving both interfaces

### Desktop Application Features
- 🎨 **Modern UI**: Animated landing page with gradient backgrounds
- 📊 **Interactive Charts**: Real-time data visualization with Matplotlib
- 🎯 **Drag & Drop**: Easy CSV file upload with visual feedback
- 📥 **PDF Reports**: Download comprehensive analysis reports
- ⚡ **Smooth Animations**: Professional fade-in effects and transitions
- 🎨 **Light Theme**: Clean, modern design with purple/pink/blue gradients

### Data Requirements
CSV files must contain the following columns:
- **Equipment Name**: Text identifier for equipment
- **Type**: Equipment type/category
- **Flowrate**: Numeric value (flow rate parameter)
- **Pressure**: Numeric value (pressure parameter)  
- **Temperature**: Numeric value (temperature parameter)

## Project Structure

```
├── backend/                    # Django REST API backend
│   ├── equipment/             # Main Django app
│   ├── equipment_visualizer/  # Django project settings
│   ├── frontend-web/          # React.js web application
│   ├── venv/                  # Python virtual environment
│   └── requirements.txt       # Backend dependencies
├── frontend-desktop/          # PyQt5 desktop application
│   ├── ui/                    # User interface components
│   ├── utils/                 # Utility modules
│   └── requirements.txt       # Desktop dependencies
├── sample_equipment_data.csv  # Sample data file
└── README.md                  # This file
```

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Node.js 14 or higher (for web frontend)
- Git

### Backend Setup (Django REST API)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd chemical-equipment-visualizer
   ```

2. **Set up Python virtual environment**
   ```bash
   cd backend
   python -m venv venv
   
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install backend dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up database**
   ```bash
   python manage.py migrate
   ```

5. **Create superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Start the Django development server**
   ```bash
   python manage.py runserver
   ```
   
   The API will be available at `http://localhost:8000/api/`

### Web Frontend Setup (React.js)

1. **Navigate to web frontend directory**
   ```bash
   cd backend/frontend-web
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Start the React development server**
   ```bash
   npm start
   ```
   
   The web application will be available at `http://localhost:3000`

### Desktop Application Setup (PyQt5)

1. **Navigate to desktop frontend directory**
   ```bash
   cd frontend-desktop
   ```

2. **Install desktop dependencies** (in the same virtual environment as backend)
   ```bash
   # Activate the backend virtual environment first
   source ../backend/venv/bin/activate
   
   # Install desktop requirements
   pip install -r requirements.txt
   ```

3. **Run the desktop application**
   ```bash
   python main.py
   ```
   
   **Note**: The desktop application features:
   - Animated landing page with smooth transitions
   - Modern light theme with gradient accents
   - Drag-and-drop file upload
   - Interactive charts with proper spacing
   - Professional PDF report downloads
   
   See `DESKTOP_APP_GUIDE.md` for detailed usage instructions.

## Usage Guide

### Getting Started

1. **Start the Backend Server**
   - Ensure the Django server is running on `http://localhost:8000`
   - The API endpoints will be available for both frontends

2. **Choose Your Interface**
   - **Web**: Open `http://localhost:3000` in your browser
   - **Desktop**: Run `python main.py` from the `frontend-desktop` directory

3. **Create an Account**
   - Register a new user account or login with existing credentials
   - Authentication is required for all data operations

### Uploading Data

1. **Prepare Your CSV File**
   - Ensure your CSV has the required columns: Equipment Name, Type, Flowrate, Pressure, Temperature
   - Use the provided `sample_equipment_data.csv` as a reference
   - Maximum file size: 10MB

2. **Upload Process**
   - Navigate to the Upload page/tab
   - Drag and drop your CSV file or use the browse button
   - Review validation results and upload the file
   - View processing results and any warnings

### Viewing Analytics

1. **Analytics Dashboard**
   - View summary statistics (total equipment, averages)
   - Explore interactive charts and visualizations
   - Analyze equipment type distributions

2. **Chart Types Available**
   - **Pie Charts**: Equipment type distribution
   - **Bar Charts**: Average parameter values
   - **Summary Dashboard**: Combined metrics overview

### Managing History

1. **Upload History**
   - View last 5 uploads with metadata
   - See upload timestamps, record counts, and filenames
   - Access historical data for comparison

2. **PDF Reports**
   - Generate comprehensive PDF reports
   - Download reports for specific uploads
   - Include charts and statistical summaries

## API Endpoints

### Authentication
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - User login
- `POST /api/auth/logout/` - User logout

### Data Operations
- `POST /api/upload/` - Upload CSV file
- `GET /api/summary/` - Get analytics summary
- `GET /api/history/` - Get upload history
- `GET /api/report/pdf/` - Download PDF report

### Sample Data
- `GET /api/sample-csv/` - Download sample CSV file

## Configuration

### Backend Configuration
Edit `backend/equipment_visualizer/settings.py` for:
- Database settings
- CORS configuration
- JWT token settings
- File upload limits

### Desktop Application Configuration
The desktop app stores settings in:
- **macOS**: `~/Library/Preferences/com.EquipmentAnalytics.ChemicalEquipmentVisualizer.plist`
- **Windows**: Registry under `HKEY_CURRENT_USER\Software\Equipment Analytics\Chemical Equipment Visualizer`
- **Linux**: `~/.config/Equipment Analytics/Chemical Equipment Visualizer.conf`

## Testing

### Property-Based Testing
The system includes comprehensive property-based tests using Hypothesis:

```bash
cd backend
python manage.py test equipment.tests
python manage.py test equipment.auth_tests
```

### Test Coverage
- CSV structure validation
- Data parsing completeness
- Numeric data type validation
- Analytics calculation accuracy
- Authentication state management
- PDF report content accuracy
- History management limits

## Documentation

### User Guides
- **`QUICK_START.md`** - Quick reference for getting started
- **`DESKTOP_APP_GUIDE.md`** - Complete desktop application user guide
- **`USAGE_EXAMPLES.md`** - API usage examples and code samples

### Technical Documentation
- **`DESKTOP_UI_FINAL_IMPROVEMENTS.md`** - UI/UX improvements and design details
- **`DESKTOP_UI_IMPROVEMENTS.md`** - Chart layout fixes and enhancements
- **`.kiro/specs/chemical-equipment-visualizer/`** - Complete specification documents
  - `requirements.md` - Feature requirements and acceptance criteria
  - `design.md` - System design and architecture
  - `tasks.md` - Implementation task list

## Troubleshooting

### Common Issues

1. **Backend Server Won't Start**
   - Check if port 8000 is available
   - Ensure virtual environment is activated
   - Verify all dependencies are installed

2. **Web Frontend Connection Issues**
   - Confirm backend server is running
   - Check CORS settings in Django
   - Verify API base URL in React configuration

3. **Desktop Application Issues**
   - Ensure PyQt5 is properly installed
   - Check API base URL in desktop configuration
   - Verify matplotlib backend compatibility
   - **Animation errors**: Fixed in latest version - update code
   - **Text visibility**: Improved with shadows and white text
   - **Chart overlapping**: Fixed with proper spacing and sizing

4. **CSV Upload Failures**
   - Verify CSV format matches requirements
   - Check file size (max 10MB)
   - Ensure all required columns are present
   - Validate numeric data types

5. **Authentication Problems**
   - Clear browser cache/cookies for web
   - Reset desktop application settings
   - Check JWT token expiration settings

### Performance Optimization

1. **Large CSV Files**
   - Consider splitting large files into smaller chunks
   - Monitor memory usage during processing
   - Use database indexing for better query performance

2. **Chart Rendering**
   - Limit data points for better performance
   - Use data aggregation for large datasets
   - Consider chart caching for repeated views

## Development

### Adding New Features

1. **Backend Development**
   - Add new API endpoints in `backend/equipment/views.py`
   - Create corresponding serializers in `backend/equipment/serializers.py`
   - Add URL patterns in `backend/equipment/urls.py`
   - Write property-based tests for new functionality

2. **Web Frontend Development**
   - Add new React components in `backend/frontend-web/src/components/`
   - Create new pages in `backend/frontend-web/src/pages/`
   - Update routing in `backend/frontend-web/src/App.js`

3. **Desktop Frontend Development**
   - Add new widgets in `frontend-desktop/ui/`
   - Update main window navigation
   - Implement corresponding API client methods

### Code Quality
- Follow PEP 8 for Python code
- Use ESLint for JavaScript/React code
- Write comprehensive tests for new features
- Document API changes in this README

## License

This project is licensed under the MIT License. See LICENSE file for details.

## Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the test output for specific error messages
3. Ensure all dependencies are correctly installed
4. Verify configuration settings match your environment

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes with appropriate tests
4. Submit a pull request with detailed description

---

**Note**: This application is designed for educational and demonstration purposes. For production use, consider additional security measures, performance optimizations, and scalability improvements.