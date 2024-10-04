from PyQt6.QtWidgets import QPushButton, QSlider, QApplication
from PyQt6.QtGui import QIcon, QPalette
from PyQt6.QtCore import QSize

class HoverButton(QPushButton):
    def __init__(self, parent, text, icon, icon_size, button_size, *args, **kwargs):
        super().__init__(text, parent, *args, **kwargs)
        self.setMouseTracking(True)  # Enable mouse tracking for hovering
        self.__button_size = button_size
        self.__icon_size = icon_size
        self.__icon_path = icon
        self.setIcon(QIcon(self.__icon_path))  # Set icon
        self.setFixedSize(self.__button_size)  # Set fixed size
        self.setIconSize(self.__icon_size)  # Set icon size
        self.setToolTip(text)
        # Set initial stylesheet (optional)
        palette = QApplication.instance().palette()
        self.__default_stylesheet = f"background-color: rgba(125, 125, 125, 0.3); border: 1px ; border-radius: 10px; color: {palette.color(QPalette.ColorRole.Base).name()};"
        self.__hover_stylesheet = f"background-color: rgba(125, 125, 125, 0.7); border: 1px solid black; border-radius: 10px; color: {palette.color(QPalette.ColorRole.Base).name()};"  # Hover stylesheet
        self.setStyleSheet(self.__default_stylesheet)  # Adjust styles as needed

    def enterEvent(self, event):
        self.setStyleSheet(self.__hover_stylesheet)

    def leaveEvent(self, event):
        self.setStyleSheet(self.__default_stylesheet)

class DoubleClickSlider(QSlider):

    DEFAULT_VALUE = 50  # Default value for the slider

    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent=parent)
        self.setRange(0, 100)  # Example range, adjust as necessary
        self.setValue(self.DEFAULT_VALUE)
        self.setMaximumSize(250, self.sizeHint().height())  # Set fixed size

    def mouseDoubleClickEvent(self, event):
        self.reset_default()
        super().mouseDoubleClickEvent(event)

    def reset_default(self):
        self.setValue(self.DEFAULT_VALUE)
