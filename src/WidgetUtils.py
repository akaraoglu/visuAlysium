from PyQt6.QtWidgets import QPushButton, QSlider, QApplication
from PyQt6.QtGui import QIcon, QPalette
from PyQt6.QtCore import QSize

class HoverButton(QPushButton):
    def __init__(self, parent, text, icon, icon_size, button_size, *args, **kwargs):
        super().__init__(text, parent, *args, **kwargs)
        self.setMouseTracking(True)  # Enable mouse tracking for hovering
        self.button_size = button_size
        self.icon_size = icon_size
        self.icon_path = icon
        self.setIcon(QIcon(self.icon_path))  # Set icon
        self.setFixedSize(self.button_size)  # Set fixed size
        self.setIconSize(self.icon_size)  # Set icon size
        self.setToolTip(text)
        # Set initial stylesheet (optional)
        palette = QApplication.instance().palette()
        self.default_stylesheet = f"background-color: rgba(125, 125, 125, 0.3); border: 1px ; border-radius: 10px; color: {palette.color(QPalette.ColorRole.Base).name()};"
        self.hover_stylesheet = f"background-color: rgba(125, 125, 125, 0.7); border: 1px solid black; border-radius: 10px; color: {palette.color(QPalette.ColorRole.Base).name()};"  # Hover stylesheet
        self.setStyleSheet(self.default_stylesheet)  # Adjust styles as needed

    def enterEvent(self, event):
        self.setStyleSheet(self.hover_stylesheet)

    def leaveEvent(self, event):
        self.setStyleSheet(self.default_stylesheet)

class DoubleClickSlider(QSlider):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent=parent)
        self.default_value = 50  # Default value for the slider
        self.setRange(0, 100)  # Example range, adjust as necessary
        self.setValue(self.default_value)
        self.setMaximumSize(250, self.sizeHint().height())  # Set fixed size

    def mouseDoubleClickEvent(self, event):
        self.reset_default()
        super().mouseDoubleClickEvent(event)

    def reset_default(self):
        self.setValue(self.default_value)
