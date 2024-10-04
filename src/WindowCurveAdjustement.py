import sys
import cv2
import numpy as np

from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QRect
from PyQt6.QtGui import QPainter, QPen, QColor, QLinearGradient, QBrush, QPixmap, QImage, QPaintEvent
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QSizePolicy, QSpacerItem, QGridLayout, QComboBox

from PyQt6.QtGui import QPainter, QPen, QColor, QLinearGradient, QBrush

from src.ImageViewer import ImageViewer
from src.WindowImageViewerAbstract import ImageViewerWindowAbstract

from scipy.interpolate import CubicSpline, interp1d

class CurveWidget(QWidget):
    curve_updated = pyqtSignal()

    NUMBER_OF_POINTS = 7

    def __init__(self, parent=None):
        super().__init__(parent)
        self.__margin = 0  # Adjusted to provide margin
        self.__width = 255  # Width of the drawable area
        self.__height = 255  # Height of the drawable area
        self.setMinimumSize(self.__width + 2 * self.__margin, self.__height + 2 * self.__margin)  # Include margin in the size
        self.__points = [QPoint(i * 40 + self.__margin, i * 40 + self.__margin) for i in range(self.NUMBER_OF_POINTS)]  # Start with points spaced out
        self.initialize_curve()
        self.__selected_point = None

    def paintEvent(self, event:QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.draw_background(painter)
        self.draw_grid(painter)  # Draw grid on the background
        self.draw_points(painter)
        self.draw_curve(painter)

    def draw_background(self, painter: QPainter):
        # Draw background and border
        # gradient = QLinearGradient(0, 0, self.__width, self.__height)
        # gradient.setColorAt(0, QColor(240, 240, 240))
        # gradient.setColorAt(1, QColor(200, 200, 200))
        # painter.fillRect(self.rect(), QBrush(gradient))
        pen = QPen(QColor(15, 15, 15), 2)
        painter.setPen(pen)
        painter.drawRect(self.__margin, self.__margin, self.__width - 2 * self.__margin, self.__height - 2 * self.__margin)
    
    def draw_grid(self, painter):
        # Draw a 7x7 grid
        pen = QPen(QColor(75, 75, 75), 1, Qt.PenStyle.DotLine)  # Light grey, dotted lines for the grid
        painter.setPen(pen)
        grid_spacing_x = (self.__width - 2 * self.__margin) / 7  # 7 lines, 6 spaces
        grid_spacing_y = (self.__height - 2 * self.__margin) / 7

        # Vertical lines
        for i in range(1, 7):  # Skip the first line because it overlaps with the border
            x = np.int32(self.__margin + i * grid_spacing_x)
            painter.drawLine(x, self.__margin, x, self.__height - self.__margin)

        # Horizontal lines
        for i in range(1, 7):  # Skip the first line for the same reason
            y = np.int32(self.__margin + i * grid_spacing_y)
            painter.drawLine(self.__margin, y, self.__width - self.__margin, y)

    def draw_points(self, painter):
        # Draw control points
        pen = QPen(QColor(15, 15, 15), 2)
        painter.setPen(pen)
        # painter.setBrush(QColor(15, 15, 15))
        for point in self.__points:
            painter.drawRect(point.x()-7, point.y()-7, 15, 15)

    def draw_curve(self, painter):
        # Draw interpolated curve
        pen = QPen(QColor(15, 15, 15), 2)
        painter.setPen(pen)
        x_vals, y_vals = zip(*[(p.x(), 255 - p.y()) for p in self.__points])  # Prepare curve data
        cs = interp1d(x_vals, y_vals, kind="cubic", bounds_error=False, fill_value="extrapolate")
        x_new = np.arange(0, 256, 1)

        prev_point = QPoint(np.clip(int(x_new[0]), self.__margin, self.__width - self.__margin) , int(255 - np.clip(cs(x_new[0]),self.__margin,self.__height - self.__margin)))
        for x in x_new[1:]:
            current_point = QPoint(np.clip(int(x), self.__margin, self.__width - self.__margin), int(255 - np.clip(cs(x),self.__margin,self.__width - self.__margin)))
            painter.drawLine(prev_point, current_point)
            prev_point = current_point

        self.curve = np.clip(cs(x_new), 0, 255).astype(np.uint8)
        # print(x_vals)
        # print(y_vals)

    def mousePressEvent(self, event):
        pos = event.position().toPoint()  # Convert to QPoint
        for idx, point in enumerate(self.__points):
            if (pos - point).manhattanLength() < 10:
                self.__selected_point = idx
                return
            
    def mouseMoveEvent(self, event):
        if self.__selected_point is not None:
            new_point = event.pos()
            min_x = self.__points[self.__selected_point - 1].x() + 10 if self.__selected_point > 0 else self.__margin
            max_x = self.__points[self.__selected_point + 1].x() - 10 if self.__selected_point < len(self.__points) - 1 else self.__width - self.__margin
            new_point.setX(max(min_x, min(new_point.x(), max_x)))
            new_point.setY(max(self.__margin, min(new_point.y(), self.__height - self.__margin)))
            self.__points[self.__selected_point] = new_point
            self.update()

    def mouseReleaseEvent(self, event):
        self.__selected_point = None
        self.curve_updated()

    def initialize_curve(self):
        # Initialize or reset the curve
        step = (self.__width+1) // (len(self.__points) - 1)
        self.__points = [QPoint(i * step, (self.__height) - i * step) for i in range(len(self.__points))]
        
        x_vals, y_vals = zip(*[(p.x(), 255 - p.y()) for p in self.__points])  # Prepare curve data
        cs = interp1d(x_vals, y_vals, kind="cubic", bounds_error=False, fill_value="extrapolate")
        x_new = np.arange(0, 256, 1)
        self.curve = np.clip(np.round(cs(x_new)), 0, 255).astype(np.uint8)
        self.update()

    def reset_curve(self):
        self.initialize_curve()  # Reset curve and update widget

class CurveEditingLayout(QVBoxLayout):

    def __init__(self, parent=None):
        super().__init__(parent)
        # Curve widgets
        self.curve_widget_global = CurveWidget()
        self.curve_widget_local_shadow = CurveWidget()
        self.curve_widget_local_highlight = CurveWidget()
        
        # Create grid layout for curves with labels
        curve_layout = QGridLayout()
        
        # Adding labels and curve widgets to the grid layout
        curve_layout.addWidget(QLabel("Global Adjustment"), 0, 0, 1, 1, Qt.AlignmentFlag.AlignCenter)
        curve_layout.addWidget(self.curve_widget_global, 1, 0, Qt.AlignmentFlag.AlignCenter)
        
        curve_layout.addWidget(QLabel("Local Shadows"), 0, 1, 1, 1, Qt.AlignmentFlag.AlignCenter)
        curve_layout.addWidget(self.curve_widget_local_shadow, 1, 1, Qt.AlignmentFlag.AlignCenter)
        
        curve_layout.addWidget(QLabel("Local Highlights"), 0, 2, 1, 1, Qt.AlignmentFlag.AlignCenter)
        curve_layout.addWidget(self.curve_widget_local_highlight, 1, 2, Qt.AlignmentFlag.AlignCenter)

        # Setup curve option dropdown
        channel_selection_layout = QHBoxLayout()
        self.curve_channel_dropdown = QComboBox()
        self.curve_channel_dropdown.addItems(["Luminance", "Red", "Green", "Blue"])
        
        channel_selection_layout.addWidget(QLabel("Adjustment Type:"))
        channel_selection_layout.addWidget(self.curve_channel_dropdown)
        channel_selection_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.addLayout(curve_layout)
        self.addLayout(channel_selection_layout)

class WindowCurveAdjustement(ImageViewerWindowAbstract):
    editing_confirmed = pyqtSignal(QPixmap, str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Curve Adjustment Window")

    def create_editing_options_layout(self):
        temp_layout = CurveEditingLayout() 
        
        # Connect the global curve's update method
        temp_layout.curve_widget_global.curve_updated = self.update_image
        temp_layout.curve_widget_local_shadow.curve_updated = self.update_image
        temp_layout.curve_widget_local_highlight.curve_updated = self.update_image
        temp_layout.curve_channel_dropdown.currentTextChanged.connect(self.curve_option_selected)
        return temp_layout
    
    def curve_option_selected(self, option):
        print(f"Selected curve option: {option}")
        self.__curve_channel = option
        self.reset_pressed()
        self.update_image()
        # Implement functionality based on selected option
        
    def initialize_values(self):
        self.editing_options_layout.curve_channel_dropdown.setCurrentIndex(0)
        self.__curve_channel = self.editing_options_layout.curve_channel_dropdown.currentText()
        self.reset_pressed()

    def update_image(self):
        print("Update image")
        self._image_viewer.apply_lut_to_current_pixmap(self.editing_options_layout.curve_widget_global.curve,
                                                      self.editing_options_layout.curve_widget_local_shadow.curve,
                                                      self.editing_options_layout.curve_widget_local_highlight.curve,
                                                      mask = None,
                                                      channel=self.__curve_channel)
        
    def reset_pressed(self):
        print("Reset curves.")
        self.editing_options_layout.curve_widget_global.reset_curve()
        self.editing_options_layout.curve_widget_local_highlight.reset_curve()
        self.editing_options_layout.curve_widget_local_shadow.reset_curve()
        self.editing_options_layout.curve_widget_global.curve_updated()
