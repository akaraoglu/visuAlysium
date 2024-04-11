from PyQt6.QtWidgets import QMainWindow,  QVBoxLayout, QHBoxLayout, QWidget, QLabel, QSizePolicy, QPushButton, QMessageBox, QSpacerItem, QToolBar, QGridLayout, QLineEdit, QSlider
from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt, QSize, QPoint, QRect, QRectF, QPointF, QSizeF
from PyQt6.QtGui import QPixmap, QIcon, QAction, QIntValidator
from ImageViewer import ImageViewer
from HoverButton import HoverButton


class LightingWindow_ButtonLayout(QWidget):
    def __init__(self):
        super().__init__()
        
        self.button_size = 60
        self.icon_size = 40

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

        self.lighting_layout = QGridLayout()

        # Add sliders
        self.sliders = {
            "Brightness": QSlider(Qt.Orientation.Horizontal),
            "Contrast": QSlider(Qt.Orientation.Horizontal),
            "Shadows": QSlider(Qt.Orientation.Horizontal),
            "Highlights": QSlider(Qt.Orientation.Horizontal),
            "Gamma": QSlider(Qt.Orientation.Horizontal)
        }

        for i, (label, slider) in enumerate(self.sliders.items()):
            slider.setRange(0, 100)  # Example range, adjust as necessary
            slider.setValue(50)
            self.lighting_layout.addWidget(QLabel(label), i, 50)
            self.lighting_layout.addWidget(slider, i, 1)

        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout.addItem(spacer)
        layout.addLayout(self.lighting_layout)
        layout.addItem(spacer)
    
    def reset_sliders(self):
        for i, (label, slider) in enumerate(self.sliders.items()):
            slider.setValue(50)

class LightingWindow(QWidget):
    editing_confirmed = pyqtSignal(QPixmap, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lighting Window")
        self.setGeometry(100, 100, 800, 600)

        # Assuming ImageViewer and LightingWindow_ButtonLayout are defined elsewhere
        self.image_viewer = ImageViewer()
        self.pixmap_image_orig = None
        self.slider_layer = LightingWindow_ButtonLayout()

        # Create the main layout for the widget
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.image_viewer)
        main_layout.addWidget(self.slider_layer)

        # Layout for confirmation buttons
        confirmation_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        confirmation_layout.addItem(spacer)

        ok_button = QPushButton("OK")
        ok_button.setFixedSize(100, 30)
        ok_button.clicked.connect(self.ok_pressed)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedSize(100, 30)
        cancel_button.clicked.connect(self.cancel_pressed)
        
        confirmation_layout.addWidget(ok_button)
        confirmation_layout.addWidget(cancel_button)
        main_layout.addLayout(confirmation_layout)

        # Connect slider value changes to functions directly
        self.slider_layer.sliders["Brightness"].valueChanged.connect(self.adjust_brightness)
        self.slider_layer.sliders["Contrast"].valueChanged.connect(self.adjust_contrast)
        self.slider_layer.sliders["Shadows"].valueChanged.connect(self.adjust_shadows)
        self.slider_layer.sliders["Highlights"].valueChanged.connect(self.adjust_highlights)
        self.slider_layer.sliders["Gamma"].valueChanged.connect(self.adjust_gamma)

    def set_image(self, pixmap_image):
        self.slider_layer.reset_sliders()
        self.pixmap_image_orig = pixmap_image
        self.image_viewer.show_new_pixmap(pixmap_image)

    def ok_pressed(self):
        # Here you would typically confirm the changes and possibly close the window or reset it for another operation
        print( "OK", "Changes have been applied.")
        self.editing_confirmed.emit(self.image_viewer.get_current_pixmap(), "Lighting Adjustment")
        self.close() #to close the window

    def cancel_pressed(self):
        # Here you would typically revert any changes or simply close the window without applying changes
        print("Cancel", "Operation has been cancelled.")
        self.close() #to close the window

    # Define placeholder functions for slider adjustments
    def adjust_brightness(self, value):
        self.read_values_from_sliders()
        self.image_viewer.adjust_contrast_brightness(self.contrast_value, self.brightness_value, self.gamma_value)

    def adjust_contrast(self, value):
        self.read_values_from_sliders()
        self.image_viewer.adjust_contrast_brightness(self.contrast_value, self.brightness_value, self.gamma_value)

    def adjust_shadows(self, value):
        self.read_values_from_sliders()
        # Placeholder for shadows adjustment logic
        pass

    def adjust_highlights(self, value):
        self.read_values_from_sliders()
        # Placeholder for highlights adjustment logic
        pass

    def adjust_gamma(self, value):
        self.read_values_from_sliders()
        self.image_viewer.adjust_contrast_brightness(self.contrast_value, self.brightness_value, self.gamma_value)


    def read_values_from_sliders(self):
        self.contrast_value = 1- self.slider_layer.sliders["Contrast"].value()/50.0
        self.brightness_value = self.slider_layer.sliders["Brightness"].value()/50.0 - 1
        self.gamma_value = 2 - self.slider_layer.sliders["Gamma"].value()/50.0
        self.shadows_value = self.slider_layer.sliders["Shadows"].value()/50.0
        self.highlights_value = self.slider_layer.sliders["Highlights"].value()/50.0