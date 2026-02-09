# Quick Start Guide

## Chemical Equipment Parameter Visualizer

### 🚀 Launch Application

```bash
cd frontend-desktop
source venv/bin/activate  # macOS/Linux
python main.py
```

---

## 📋 First Time Setup

1. **Register Account**
   - Click "Register" in login dialog
   - Enter username, email, password
   - Click "Register"

2. **Login**
   - Enter credentials
   - Click "Login"

---

## 📁 Upload Data

### Quick Upload
1. Go to Upload page (📁 button)
2. Drag CSV file to drop zone
3. Click "Upload File"

### CSV Format Required
```
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump A,Pump,150.5,45.2,85.3
Heat Exchanger B,Heat Exchanger,200.0,30.5,120.0
```

---

## 📊 View Analytics

1. Go to Analytics page (📊 button)
2. Click "Refresh Data"
3. View 4 charts:
   - Summary statistics
   - Equipment distribution
   - Flowrate histogram
   - Pressure vs Temperature

---

## 📜 Download Reports

1. Go to History page (📜 button)
2. Click "Refresh History"
3. Click "📥 PDF" button for any upload
4. Save PDF report

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+O` | Upload file |
| `Ctrl+1` | Upload page |
| `Ctrl+2` | Analytics page |
| `Ctrl+3` | History page |
| `Ctrl+Q` | Quit app |

---

## 🎨 Features

✨ **Animated Landing Page**
- Smooth fade-in effects
- Interactive cards
- Modern gradient design

🎯 **Drag & Drop Upload**
- Drop CSV files anywhere
- Instant validation
- Progress tracking

📈 **Real-time Analytics**
- 4 interactive charts
- Statistical insights
- Color-coded data

📥 **PDF Reports**
- Professional formatting
- Complete data analysis
- Easy download

---

## ⚠️ Troubleshooting

### Backend Not Running?
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

### Upload Failed?
- Check CSV format
- Verify file size < 10MB
- Ensure you're logged in

### No Charts?
- Upload data first
- Click "Refresh Data"
- Check upload success

---

## 📞 Need Help?

See full documentation:
- `DESKTOP_APP_GUIDE.md` - Complete user guide
- `DESKTOP_UI_FINAL_IMPROVEMENTS.md` - UI/UX details
- `README.md` - Project overview

---

**Happy Analyzing! 🎉**
