from PyQt6.QtWidgets import QPushButton
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize

class HoverButton(QPushButton):
    def __init__(self, text, icon, icon_size, button_size, *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        self.setMouseTracking(True)  # Enable mouse tracking for hovering
        self.button_size = button_size
        self.icon_size = icon_size
        self.icon_path = icon
        self.setIcon(QIcon(self.icon_path))  # Set icon
        self.setFixedSize(QSize(self.button_size, self.button_size))  # Set fixed size
        self.setIconSize(QSize(self.icon_size, self.icon_size))  # Set icon size
        # Set initial stylesheet (optional)
        self.default_stylesheet = "background-color: rgba(125, 125, 125, 0.3); border: 1px ; border-radius: 10px; color: white;"
        self.hover_stylesheet = "background-color: rgba(125, 125, 125, 0.7); border: 1px solid black; border-radius: 10px; color: white;"  # Hover stylesheet
        self.setStyleSheet(self.default_stylesheet)  # Adjust styles as needed

    def enterEvent(self, event):
        self.setStyleSheet(self.hover_stylesheet)

    def leaveEvent(self, event):
        self.setStyleSheet(self.default_stylesheet)