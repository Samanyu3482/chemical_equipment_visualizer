# Desktop Application User Guide

## Chemical Equipment Parameter Visualizer - Desktop Edition

### Overview
A modern PyQt5 desktop application for analyzing and visualizing chemical equipment parameters from CSV data. Features an animated landing page, intuitive navigation, and powerful data visualization tools.

---

## Getting Started

### Installation

1. **Navigate to the desktop app directory:**
   ```bash
   cd frontend-desktop
   ```

2. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate  # On macOS/Linux
   # or
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies (if not already installed):**
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application

```bash
python main.py
```

Or use the run script:
```bash
python run_desktop.py
```

---

## Application Features

### 1. Landing Page

**What You'll See:**
- Animated title and subtitle with fade-in effects
- Three interactive cards:
  - 📁 **Upload Data**: Import CSV files
  - 📊 **Analytics**: View charts and insights
  - 📜 **History**: Review past uploads
- Feature highlights at the bottom

**How to Use:**
- Click any card to navigate to that section
- Or use the navigation bar at the top

### 2. Authentication

**First Time Setup:**
1. On startup, you'll see a login/register dialog
2. Choose "Register" to create a new account
3. Enter username, email, and password
4. Click "Register" to create your account

**Logging In:**
1. Enter your username and password
2. Click "Login"
3. Your session will be saved for future use

**Logging Out:**
- Go to Account menu → Logout
- Or use the user info in the navigation bar

### 3. Upload Page

**Uploading CSV Files:**

**Method 1: Drag and Drop**
1. Navigate to the Upload page
2. Drag your CSV file onto the drop zone
3. The file will be automatically selected
4. Click "Upload File" to process

**Method 2: Browse**
1. Click "Browse Files..." button
2. Select your CSV file from the file dialog
3. Click "Upload File" to process

**CSV Requirements:**
- File extension: `.csv`
- Required columns:
  - Equipment Name
  - Type
  - Flowrate
  - Pressure
  - Temperature
- Numeric values for Flowrate, Pressure, Temperature
- No missing values in required columns
- Maximum file size: 10MB

**Upload Results:**
- Success: Green message with record count and upload ID
- Failure: Red message with error details
- Warnings: Yellow messages for non-critical issues

### 4. Analytics Page

**Viewing Charts:**

The analytics page displays multiple visualizations:

1. **Summary Statistics Chart** (Top)
   - Bar chart showing mean values
   - Flowrate, Pressure, Temperature averages
   - Color-coded bars (purple, pink, blue)

2. **Equipment Type Distribution** (Bottom Left)
   - Pie chart showing equipment types
   - Percentage breakdown
   - Color-coded segments

3. **Flowrate Distribution** (Bottom Center)
   - Histogram of flowrate values
   - Shows data distribution
   - Purple bars with grid

4. **Pressure vs Temperature** (Bottom Right)
   - Scatter plot showing correlation
   - Each point represents equipment
   - Pink dots with grid

**Refreshing Data:**
- Click "Refresh Data" button to reload latest upload
- Data automatically refreshes after successful upload

**Exporting Charts:**
- Right-click on any chart
- Select "Save image as..."
- Choose location and format

### 5. History Page

**Viewing Upload History:**

1. Click "Refresh History" to load recent uploads
2. View table with:
   - Upload ID
   - Filename
   - Upload Date
   - Record Count
   - User
   - Actions (PDF download button)

**Downloading PDF Reports:**

**Method 1: From Table**
- Click the "📥 PDF" button in the Actions column
- Choose save location
- PDF will be downloaded

**Method 2: Selected Upload**
- Click on a row to select it
- View details in the "Upload Details" section
- Click "📥 Download PDF Report"
- Choose save location

**Method 3: Latest Upload**
- Click "📥 Download Latest PDF"
- Automatically downloads most recent report
- Choose save location

**Upload Details:**
- Select any row to view detailed information
- Shows: ID, Filename, Upload Time, Record Count, User

---

## Navigation

### Navigation Bar
Located at the top of the window:
- 🏠 **Home**: Return to landing page
- 📁 **Upload**: Go to upload page
- 📊 **Analytics**: View charts and data
- 📜 **History**: View upload history
- **User Info**: Shows logged-in username

### Menu Bar

**File Menu:**
- Upload CSV... (Ctrl+O): Quick file upload
- Exit (Ctrl+Q): Close application

**View Menu:**
- Upload (Ctrl+1): Go to upload page
- Analytics (Ctrl+2): Go to analytics page
- History (Ctrl+3): Go to history page

**Account Menu:**
- Login...: Show login dialog
- Logout: Log out current user

**Help Menu:**
- About: Application information

---

## Keyboard Shortcuts

- `Ctrl+O` or `Cmd+O`: Open file upload dialog
- `Ctrl+1` or `Cmd+1`: Go to Upload page
- `Ctrl+2` or `Cmd+2`: Go to Analytics page
- `Ctrl+3` or `Cmd+3`: Go to History page
- `Ctrl+Q` or `Cmd+Q`: Quit application

---

## Troubleshooting

### Application Won't Start

**Issue:** ModuleNotFoundError
**Solution:**
```bash
cd frontend-desktop
source venv/bin/activate
pip install -r requirements.txt
```

**Issue:** Backend not running
**Solution:**
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

### Upload Fails

**Issue:** "Authentication Required"
**Solution:** Make sure you're logged in

**Issue:** "File Too Large"
**Solution:** Ensure CSV file is under 10MB

**Issue:** "Invalid CSV format"
**Solution:** Check CSV has required columns:
- Equipment Name
- Type
- Flowrate
- Pressure
- Temperature

### Charts Not Displaying

**Issue:** No data shown
**Solution:**
1. Upload a CSV file first
2. Click "Refresh Data" on Analytics page
3. Check that upload was successful

**Issue:** Charts overlapping
**Solution:** This has been fixed in the latest version. Make sure you're running the updated code.

### Animation Issues

**Issue:** Landing page animations not smooth
**Solution:** This is normal on slower systems. Animations will complete but may be less smooth.

**Issue:** RuntimeError with QGraphicsOpacityEffect
**Solution:** This has been fixed in the latest version. Update your code.

---

## Tips and Best Practices

### Data Management
1. **Keep CSV files organized**: Use descriptive filenames
2. **Regular uploads**: Upload new data regularly to track trends
3. **Download reports**: Save PDF reports for record-keeping
4. **Check history**: Review past uploads before uploading duplicates

### Performance
1. **File size**: Keep CSV files under 5MB for best performance
2. **Close unused windows**: Close the app when not in use
3. **Regular updates**: Keep the application updated

### Workflow
1. **Start with upload**: Always upload data first
2. **Review analytics**: Check charts for insights
3. **Download reports**: Save important findings
4. **Check history**: Track your upload history

---

## Sample Data

A sample CSV file is provided: `sample_equipment_data.csv`

**Location:** Project root directory

**Contents:**
- 10 sample equipment records
- All required columns
- Valid data format
- Ready to upload

**Usage:**
1. Navigate to Upload page
2. Click "Browse Files..."
3. Select `sample_equipment_data.csv`
4. Click "Upload File"

---

## Technical Details

### System Requirements
- **OS**: macOS, Linux, or Windows
- **Python**: 3.8 or higher
- **RAM**: 2GB minimum, 4GB recommended
- **Display**: 1200x800 minimum resolution

### Dependencies
- PyQt5: GUI framework
- matplotlib: Chart generation
- requests: API communication
- See `requirements.txt` for complete list

### Backend Connection
- **Default URL**: http://localhost:8000
- **API Endpoints**: /api/equipment/
- **Authentication**: JWT tokens
- **Session**: Persistent across restarts

### Data Storage
- **Local**: Window state, user preferences
- **Server**: CSV data, analytics, reports
- **Cache**: Temporary chart images

---

## Support

### Getting Help
1. Check this guide first
2. Review error messages carefully
3. Check backend server status
4. Verify CSV file format

### Common Questions

**Q: Can I use the app offline?**
A: No, the app requires connection to the backend server.

**Q: How many uploads can I have?**
A: The system keeps the last 5 uploads per user.

**Q: Can I export charts?**
A: Yes, right-click on any chart and select "Save image as..."

**Q: Is my data secure?**
A: Yes, all data is transmitted over secure connections and requires authentication.

**Q: Can multiple users use the same computer?**
A: Yes, each user has their own account and data.

---

## Version Information

**Current Version:** 1.0.0

**Recent Updates:**
- Modern light theme with gradients
- Animated landing page
- Improved chart layouts
- Enhanced text visibility
- Fixed animation bugs
- Better error handling

**Upcoming Features:**
- Dark mode toggle
- Custom color themes
- More chart types
- Export to Excel
- Batch file upload

---

## Credits

**Built with:**
- PyQt5 for GUI
- Matplotlib for charts
- Django REST Framework for backend
- JWT for authentication

**Design:**
- Modern gradient color scheme
- Smooth animations
- Intuitive navigation
- Professional appearance

---

## License

Chemical Equipment Parameter Visualizer
Version 1.0.0

For educational and commercial use.

---

**Enjoy using the Chemical Equipment Parameter Visualizer!**

For more information, see:
- `README.md`: Project overview
- `DESKTOP_UI_FINAL_IMPROVEMENTS.md`: UI/UX details
- `USAGE_EXAMPLES.md`: API usage examples
