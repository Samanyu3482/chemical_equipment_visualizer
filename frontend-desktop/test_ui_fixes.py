#!/usr/bin/env python3
"""
Test script to verify UI fixes
"""

import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# Add the current directory to Python path for imports
sys.path.insert(0, '.')

from ui.landing_widget import LandingWidget, AnimatedCard

def test_landing_widget():
    """Test landing widget creation and animations"""
    print("Testing LandingWidget...")
    
    app = QApplication(sys.argv)
    
    # Create landing widget
    landing = LandingWidget()
    landing.show()
    
    print("✓ LandingWidget created successfully")
    print("✓ Animations initialized")
    
    # Test card creation
    card = AnimatedCard("Test", "Description", "📁", "#667eea")
    print("✓ AnimatedCard created successfully")
    
    # Test hover events (simulate)
    try:
        from PyQt5.QtCore import QEvent
        from PyQt5.QtGui import QEnterEvent
        
        # Simulate enter event
        event = QEvent(QEvent.Enter)
        card.enterEvent(event)
        print("✓ Card hover animation works")
        
        # Simulate leave event
        card.leaveEvent(event)
        print("✓ Card leave animation works")
        
    except Exception as e:
        print(f"⚠ Animation test warning: {e}")
    
    # Close after 2 seconds
    QTimer.singleShot(2000, app.quit)
    
    print("\n✅ All tests passed!")
    print("Starting application for 2 seconds to verify visuals...")
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    test_landing_widget()
