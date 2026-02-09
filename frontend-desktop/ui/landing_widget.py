"""
Landing page widget with animations and modern UI
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QGraphicsOpacityEffect, QFrame
)
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QPalette, QColor


class AnimatedCard(QFrame):
    """Animated card widget with hover effects"""
    
    clicked = pyqtSignal()
    
    def __init__(self, title, description, icon_text, color):
        super().__init__()
        self.setup_ui(title, description, icon_text, color)
        self.setup_animations()
        
    def setup_ui(self, title, description, icon_text, color):
        """Set up the card UI"""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {color}, stop:1 {self.lighten_color(color)});
                border-radius: 15px;
                padding: 30px;
                border: 3px solid rgba(255, 255, 255, 0.5);
            }}
            QFrame:hover {{
                border: 3px solid white;
            }}
        """)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumSize(320, 260)
        self.setMaximumSize(380, 300)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignCenter)
        
        # Icon
        icon_label = QLabel(icon_text)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 56px; background: transparent; border: none;")
        layout.addWidget(icon_label)
        
        # Title - simple with dark background
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: white;
            background-color: rgba(0, 0, 0, 0.6);
            padding: 12px 20px;
            border-radius: 8px;
            border: none;
        """)
        layout.addWidget(title_label)
        
        # Description - simple with dark background
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            font-size: 15px;
            color: white;
            background-color: rgba(0, 0, 0, 0.5);
            padding: 10px 15px;
            border-radius: 6px;
            border: none;
            line-height: 1.3;
        """)
        layout.addWidget(desc_label)
        
    def lighten_color(self, color):
        """Lighten a color for gradient effect"""
        color_map = {
            '#667eea': '#764ba2',
            '#f093fb': '#f5576c',
            '#4facfe': '#00f2fe',
            '#43e97b': '#38f9d7'
        }
        return color_map.get(color, color)
    
    def setup_animations(self):
        """Set up hover animations"""
        self.opacity_effect = QGraphicsOpacityEffect()
        self.setGraphicsEffect(self.opacity_effect)
        self.opacity_effect.setOpacity(1.0)
        
        self.scale_factor = 1.0
        self.anim = None
        
    def enterEvent(self, event):
        """Handle mouse enter"""
        try:
            # Stop any existing animation
            if self.anim and self.anim.state() == QPropertyAnimation.Running:
                self.anim.stop()
            
            # Check if opacity effect still exists
            if self.graphicsEffect() is None or not isinstance(self.graphicsEffect(), QGraphicsOpacityEffect):
                self.opacity_effect = QGraphicsOpacityEffect()
                self.setGraphicsEffect(self.opacity_effect)
            
            # Animate opacity with scale effect
            self.anim = QPropertyAnimation(self.graphicsEffect(), b"opacity")
            self.anim.setDuration(200)
            self.anim.setStartValue(self.graphicsEffect().opacity())
            self.anim.setEndValue(1.0)
            self.anim.setEasingCurve(QEasingCurve.OutCubic)
            self.anim.start()
        except RuntimeError:
            # If effect was deleted, recreate it
            self.opacity_effect = QGraphicsOpacityEffect()
            self.setGraphicsEffect(self.opacity_effect)
        
        super().enterEvent(event)
    
    def leaveEvent(self, event):
        """Handle mouse leave"""
        try:
            # Stop any existing animation
            if self.anim and self.anim.state() == QPropertyAnimation.Running:
                self.anim.stop()
            
            # Check if opacity effect still exists
            if self.graphicsEffect() is None or not isinstance(self.graphicsEffect(), QGraphicsOpacityEffect):
                self.opacity_effect = QGraphicsOpacityEffect()
                self.setGraphicsEffect(self.opacity_effect)
            
            self.anim = QPropertyAnimation(self.graphicsEffect(), b"opacity")
            self.anim.setDuration(200)
            self.anim.setStartValue(self.graphicsEffect().opacity())
            self.anim.setEndValue(1.0)
            self.anim.setEasingCurve(QEasingCurve.OutCubic)
            self.anim.start()
        except RuntimeError:
            # If effect was deleted, recreate it
            self.opacity_effect = QGraphicsOpacityEffect()
            self.setGraphicsEffect(self.opacity_effect)
        
        super().leaveEvent(event)
    
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class LandingWidget(QWidget):
    """Modern landing page with animations"""
    
    navigate_to_upload = pyqtSignal()
    navigate_to_analytics = pyqtSignal()
    navigate_to_history = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.start_animations()
        
    def setup_ui(self):
        """Set up the landing page UI"""
        # Set gradient background
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:0.5 #764ba2, stop:1 #f093fb);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(30)
        
        # Header section - simple and clean
        header_layout = QVBoxLayout()
        header_layout.setSpacing(15)
        header_layout.setAlignment(Qt.AlignCenter)
        
        # Main title
        self.title_label = QLabel("Chemical Equipment\nParameter Visualizer")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setStyleSheet("""
            font-size: 38px;
            font-weight: bold;
            color: white;
            background-color: rgba(0, 0, 0, 0.5);
            padding: 25px 40px;
            border-radius: 15px;
            line-height: 1.3;
        """)
        self.title_opacity = QGraphicsOpacityEffect()
        self.title_label.setGraphicsEffect(self.title_opacity)
        self.title_opacity.setOpacity(0)
        header_layout.addWidget(self.title_label)
        
        # Subtitle
        self.subtitle_label = QLabel("Analyze and visualize your equipment data\nwith powerful insights")
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        self.subtitle_label.setStyleSheet("""
            font-size: 16px;
            color: white;
            background-color: rgba(0, 0, 0, 0.45);
            padding: 15px 30px;
            border-radius: 10px;
            line-height: 1.4;
        """)
        self.subtitle_opacity = QGraphicsOpacityEffect()
        self.subtitle_label.setGraphicsEffect(self.subtitle_opacity)
        self.subtitle_opacity.setOpacity(0)
        header_layout.addWidget(self.subtitle_label)
        
        layout.addLayout(header_layout)
        layout.addSpacing(20)
        
        # Cards section
        cards_layout = QHBoxLayout()
        cards_layout.setSpacing(30)
        cards_layout.setAlignment(Qt.AlignCenter)
        
        # Upload card
        self.upload_card = AnimatedCard(
            "Upload Data",
            "Import CSV files with equipment parameters",
            "📁",
            "#667eea"
        )
        self.upload_card.clicked.connect(self.navigate_to_upload.emit)
        self.upload_card_opacity = QGraphicsOpacityEffect()
        self.upload_card.setGraphicsEffect(self.upload_card_opacity)
        self.upload_card_opacity.setOpacity(0)
        cards_layout.addWidget(self.upload_card)
        
        # Analytics card
        self.analytics_card = AnimatedCard(
            "Analytics",
            "View charts and statistical insights",
            "📊",
            "#f093fb"
        )
        self.analytics_card.clicked.connect(self.navigate_to_analytics.emit)
        self.analytics_card_opacity = QGraphicsOpacityEffect()
        self.analytics_card.setGraphicsEffect(self.analytics_card_opacity)
        self.analytics_card_opacity.setOpacity(0)
        cards_layout.addWidget(self.analytics_card)
        
        # History card
        self.history_card = AnimatedCard(
            "History",
            "Review past uploads and reports",
            "📜",
            "#4facfe"
        )
        self.history_card.clicked.connect(self.navigate_to_history.emit)
        self.history_card_opacity = QGraphicsOpacityEffect()
        self.history_card.setGraphicsEffect(self.history_card_opacity)
        self.history_card_opacity.setOpacity(0)
        cards_layout.addWidget(self.history_card)
        
        layout.addLayout(cards_layout)
        
        # Features section
        layout.addSpacing(50)
        
        features_layout = QHBoxLayout()
        features_layout.setSpacing(25)
        features_layout.setAlignment(Qt.AlignCenter)
        
        features = [
            ("⚡", "Fast Processing", "Quick CSV analysis"),
            ("🔒", "Secure", "Protected data storage"),
            ("📈", "Insights", "Detailed analytics"),
            ("💾", "History", "Track all uploads")
        ]
        
        self.feature_widgets = []
        for icon, title, desc in features:
            feature_widget = self.create_feature_widget(icon, title, desc)
            self.feature_widgets.append(feature_widget)
            features_layout.addWidget(feature_widget)
        
        layout.addLayout(features_layout)
        layout.addStretch()
        
    def create_feature_widget(self, icon, title, description):
        """Create a feature widget"""
        widget = QWidget()
        widget.setStyleSheet("""
            background-color: rgba(0, 0, 0, 0.5);
            border-radius: 12px;
            border: 2px solid rgba(255, 255, 255, 0.4);
        """)
        widget.setMinimumSize(210, 160)
        widget.setMaximumSize(250, 180)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(12)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 50px; background: transparent;")
        layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: white;
            background: transparent;
        """)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("""
            font-size: 14px;
            color: white;
            background: transparent;
        """)
        layout.addWidget(desc_label)
        
        # Set opacity effect
        opacity = QGraphicsOpacityEffect(widget)
        widget.setGraphicsEffect(opacity)
        opacity.setOpacity(0)
        
        return widget
    
    def start_animations(self):
        """Start entrance animations"""
        # Animate title
        QTimer.singleShot(100, lambda: self.animate_fade_in(self.title_opacity, 800))
        
        # Animate subtitle
        QTimer.singleShot(400, lambda: self.animate_fade_in(self.subtitle_opacity, 800))
        
        # Animate cards with stagger
        QTimer.singleShot(700, lambda: self.animate_fade_in(self.upload_card_opacity, 600))
        QTimer.singleShot(900, lambda: self.animate_fade_in(self.analytics_card_opacity, 600))
        QTimer.singleShot(1100, lambda: self.animate_fade_in(self.history_card_opacity, 600))
        
        # Animate features
        for i, widget in enumerate(self.feature_widgets):
            delay = 1300 + (i * 150)
            QTimer.singleShot(delay, lambda w=widget: self.animate_fade_in(
                w.graphicsEffect(), 500
            ))
    
    def animate_fade_in(self, opacity_effect, duration):
        """Animate fade in effect"""
        if opacity_effect is None:
            return
            
        anim = QPropertyAnimation(opacity_effect, b"opacity")
        anim.setDuration(duration)
        anim.setStartValue(0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        
        # Store animation to prevent garbage collection
        if not hasattr(self, '_animations'):
            self._animations = []
        self._animations.append(anim)
