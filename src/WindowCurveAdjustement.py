import sys
import cv2
import numpy as np

from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QRect
from PyQt6.QtGui import QPainter, QPen, QColor, QLinearGradient, QBrush, QPixmap, QImage
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QSizePolicy, QSpacerItem, QGridLayout, QComboBox

from PyQt6.QtGui import QPainter, QPen, QColor, QLinearGradient, QBrush

from src.ImageViewer import ImageViewer
from src.WindowImageViewerAbstract import ImageViewerWindowAbstract

from scipy.interpolate import CubicSpline, interp1d

class CurveWidget(QWidget):
    curve_updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.number_of_points = 7
        self.margin = 0  # Adjusted to provide margin
        self.width = 255  # Width of the drawable area
        self.height = 255  # Height of the drawable area
        self.setMinimumSize(self.width + 2 * self.margin, self.height + 2 * self.margin)  # Include margin in the size
        self.points = [QPoint(i * 40 + self.margin, i * 40 + self.margin) for i in range(self.number_of_points)]  # Start with points spaced out
        self.initialize_curve()
        self.selected_point = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.draw_background(painter)
        self.draw_grid(painter)  # Draw grid on the background
        self.draw_points(painter)
        self.draw_curve(painter)

    def draw_background(self, painter):
        # Draw background and border
        # gradient = QLinearGradient(0, 0, self.width, self.height)
        # gradient.setColorAt(0, QColor(240, 240, 240))
        # gradient.setColorAt(1, QColor(200, 200, 200))
        # painter.fillRect(self.rect(), QBrush(gradient))
        pen = QPen(QColor(15, 15, 15), 2)
        painter.setPen(pen)
        painter.drawRect(self.margin, self.margin, self.width - 2 * self.margin, self.height - 2 * self.margin)
    
    def draw_grid(self, painter):
        # Draw a 7x7 grid
        pen = QPen(QColor(75, 75, 75), 1, Qt.PenStyle.DotLine)  # Light grey, dotted lines for the grid
        painter.setPen(pen)
        grid_spacing_x = (self.width - 2 * self.margin) / 7  # 7 lines, 6 spaces
        grid_spacing_y = (self.height - 2 * self.margin) / 7

        # Vertical lines
        for i in range(1, 7):  # Skip the first line because it overlaps with the border
            x = np.int32(self.margin + i * grid_spacing_x)
            painter.drawLine(x, self.margin, x, self.height - self.margin)

        # Horizontal lines
        for i in range(1, 7):  # Skip the first line for the same reason
            y = np.int32(self.margin + i * grid_spacing_y)
            painter.drawLine(self.margin, y, self.width - self.margin, y)

    def draw_points(self, painter):
        # Draw control points
        pen = QPen(QColor(15, 15, 15), 2)
        painter.setPen(pen)
        # painter.setBrush(QColor(15, 15, 15))
        for point in self.points:
            painter.drawRect(point.x()-7, point.y()-7, 15, 15)

    def draw_curve(self, painter):
        # Draw interpolated curve
        pen = QPen(QColor(15, 15, 15), 2)
        painter.setPen(pen)
        x_vals, y_vals = zip(*[(p.x(), 255 - p.y()) for p in self.points])  # Prepare curve data
        cs = interp1d(x_vals, y_vals, kind="cubic", bounds_error=False, fill_value="extrapolate")
        x_new = np.arange(0, 256, 1)

        prev_point = QPoint(np.clip(int(x_new[0]), self.margin, self.width - self.margin) , int(255 - np.clip(cs(x_new[0]),self.margin,self.height - self.margin)))
        for x in x_new[1:]:
            current_point = QPoint(np.clip(int(x), self.margin, self.width - self.margin), int(255 - np.clip(cs(x),self.margin,self.width - self.margin)))
            painter.drawLine(prev_point, current_point)
            prev_point = current_point

        self.curve = np.clip(cs(x_new), 0, 255).astype(np.uint8)
        # print(x_vals)
        # print(y_vals)

    def mousePressEvent(self, event):
        pos = event.position().toPoint()  # Convert to QPoint
        for idx, point in enumerate(self.points):
            if (pos - point).manhattanLength() < 10:
                self.selected_point = idx
                return
            
    def mouseMoveEvent(self, event):
        if self.selected_point is not None:
            new_point = event.pos()
            min_x = self.points[self.selected_point - 1].x() + 10 if self.selected_point > 0 else self.margin
            max_x = self.points[self.selected_point + 1].x() - 10 if self.selected_point < len(self.points) - 1 else self.width - self.margin
            new_point.setX(max(min_x, min(new_point.x(), max_x)))
            new_point.setY(max(self.margin, min(new_point.y(), self.height - self.margin)))
            self.points[self.selected_point] = new_point
            self.update()

    def mouseReleaseEvent(self, event):
        self.selected_point = None
        self.curve_updated()

    def initialize_curve(self):
        # Initialize or reset the curve
        step = (self.width+1) // (len(self.points) - 1)
        self.points = [QPoint(i * step, (self.height) - i * step) for i in range(len(self.points))]
        
        x_vals, y_vals = zip(*[(p.x(), 255 - p.y()) for p in self.points])  # Prepare curve data
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
        
        self.curve_channel = "Luminance" # Set default
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
        self.curve_channel = option
        self.reset_pressed()
        self.update_image()
        # Implement functionality based on selected option
        
    def initialize_values(self):
        self.editing_options_layout.curve_channel_dropdown.setCurrentIndex(0)
        self.curve_channel = self.editing_options_layout.curve_channel_dropdown.currentText()
        self.reset_pressed()

    def update_image(self):
        print("Update image")
        self.image_viewer.apply_lut_to_current_pixmap(self.editing_options_layout.curve_widget_global.curve,
                                                      self.editing_options_layout.curve_widget_local_shadow.curve,
                                                      self.editing_options_layout.curve_widget_local_highlight.curve,
                                                      mask = None,
                                                      channel=self.curve_channel)
        
    def reset_pressed(self):
        print("Reset curves.")
        self.editing_options_layout.curve_widget_global.reset_curve()
        self.editing_options_layout.curve_widget_local_highlight.reset_curve()
        self.editing_options_layout.curve_widget_local_shadow.reset_curve()
        self.editing_options_layout.curve_widget_global.curve_updated()
