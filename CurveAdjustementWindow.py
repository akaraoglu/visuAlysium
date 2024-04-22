import sys
import cv2
import numpy as np

from PyQt6.QtCore import Qt, QPoint, pyqtSignal, QRect
from PyQt6.QtGui import QPainter, QPen, QColor, QLinearGradient, QBrush, QPixmap, QImage
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QSlider, QSizePolicy, QSpacerItem, QGridLayout

from PyQt6.QtGui import QPainter, QPen, QColor, QLinearGradient, QBrush

from ImageViewer import ImageViewer

from scipy.interpolate import CubicSpline, interp1d

class CurveWidget(QWidget):
    curve_updated = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.number_of_points = 8
        self.margin = 10  # Adjusted to provide margin
        self.width = 256  # Width of the drawable area
        self.height = 256  # Height of the drawable area
        self.setMinimumSize(self.width + 2 * self.margin, self.height + 2 * self.margin)  # Include margin in the size
        self.points = [QPoint(i * 40 + self.margin, i * 40 + self.margin) for i in range(self.number_of_points)]  # Start with points spaced out
        self.initialize_curve()
        self.selected_point = None

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.draw_background(painter)
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
        step = (self.width - 2 * self.margin) // (len(self.points) - 1)
        self.points = [QPoint(self.margin + i * step, self.margin + (self.height - 2 * self.margin) - i * step) for i in range(len(self.points))]
        
        x_vals, y_vals = zip(*[(p.x(), 255 - p.y()) for p in self.points])  # Prepare curve data
        cs = interp1d(x_vals, y_vals, kind="cubic", bounds_error=False, fill_value="extrapolate")
        x_new = np.arange(0, 256, 1)
        self.curve = np.clip(cs(x_new), 0, 255).astype(np.uint8)
        self.update()

    def reset_curve(self):
        self.initialize_curve()  # Reset curve and update widget
        self.curve_updated()

class CurveAdjustmentWindow(QWidget):
    editing_confirmed = pyqtSignal(QPixmap, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Editing Window")
        # self.setGeometry(100, 100, 800, 600)

        # Assuming ImageViewer and LightingWindow_ButtonLayout are defined elsewhere
        self.image_viewer = ImageViewer()
        self.pixmap_image_orig = None
        self.curve_widget = CurveWidget()
        self.curve_widget.curve_updated = self.update_image

        # Create the main layout for the widget
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.image_viewer)
        main_layout.addWidget(self.curve_widget)

        # Layout for confirmation buttons
        confirmation_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        hdtsoi_button = QPushButton("Hold Down to See Original Image")
        hdtsoi_button.setFixedSize(300, 30)
        hdtsoi_button.pressed.connect(self.hdtsoi_pressed)
        hdtsoi_button.released.connect(self.hdtsoi_released)

        reset_button = QPushButton("Reset")
        reset_button.setFixedSize(100, 30)
        reset_button.pressed.connect(self.reset_pressed)

        hist_button = QPushButton("Histogram")
        hist_button.setFixedSize(100, 30)
        hist_button.pressed.connect(self.histogram_pressed)
        
        ok_button = QPushButton("OK")
        ok_button.setFixedSize(100, 30)
        ok_button.clicked.connect(self.ok_pressed)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedSize(100, 30)
        cancel_button.clicked.connect(self.cancel_pressed)
        
        confirmation_layout.addWidget(hdtsoi_button)
        confirmation_layout.addWidget(reset_button)
        confirmation_layout.addWidget(hist_button)
        confirmation_layout.addItem(spacer)
        confirmation_layout.addWidget(ok_button)
        confirmation_layout.addWidget(cancel_button)
        main_layout.addLayout(confirmation_layout)
  
        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

        # Adjust window size to half of the screen size
        screen = QApplication.primaryScreen()
        screen_size = screen.size()

        screenWidth = screen_size.width()
        screenHeight = screen_size.height()

        # Calculate width and height
        width = screenWidth // 2
        height = (2 * screenHeight) // 3

        # Calculate x and y positions to center the window
        x = (screenWidth - width) // 2
        y = (screenHeight - height) // 2

        # Set geometry to center the window with desired size
        self.setGeometry(x, y, width, height)
    
    def set_image(self, pixmap_image):
        self.curve_widget.reset_curve()
        self.pixmap_image_orig = pixmap_image
        new_width = 1024
        new_height = 1024
        scaled_pixmap = pixmap_image.scaled(new_width, new_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.image_viewer.show_new_pixmap(scaled_pixmap)
    
    def hdtsoi_pressed(self):
        print( "HDtSOI", "Showing original image.")
        self.image_viewer.show_pixmap(self.image_viewer.get_original_pixmap())

    def hdtsoi_released(self):
        print( "HDtSOI", "Showing edited image.")
        self.image_viewer.show_pixmap(self.image_viewer.get_previous_pixmap())

    def ok_pressed(self):
        print( "OK", "Changes have been applied.")
        self.image_viewer.show_new_pixmap(self.pixmap_image_orig)
        self.update_image()
        self.editing_confirmed.emit(self.image_viewer.get_current_pixmap(), "Curve Adjustment")
        self.close() #to close the window

    def cancel_pressed(self):
        # Here you would typically revert any changes or simply close the window without applying changes
        print("Cancel", "Operation has been cancelled.")
        self.close() #to close the window

    def update_image(self):
        print("Update image")
        self.image_viewer.apply_lut_to_current_pixmap(lut=self.curve_widget.curve)

    def reset_pressed(self):
        print("Reset")
        self.curve_widget.reset_curve()

    def histogram_pressed(self):
        self.image_viewer.toggle_info_display()