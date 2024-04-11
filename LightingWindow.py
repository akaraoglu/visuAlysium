from PyQt6.QtWidgets import QMainWindow,  QVBoxLayout, QHBoxLayout, QWidget, QLabel, QSizePolicy, QPushButton, QMessageBox, QSpacerItem, QToolBar, QGridLayout, QLineEdit, QSlider, QApplication
from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt, QSize, QPoint, QRect, QRectF, QPointF, QSizeF
from PyQt6.QtGui import QPixmap, QIcon, QAction, QIntValidator
from ImageViewer import ImageViewer
from HoverButton import HoverButton

class DoubleClickSlider(QSlider):
    def __init__(self, orientation, parent=None):
        super().__init__(orientation, parent=parent)
        self.default_value = 50  # Default value for the slider
        self.setRange(0, 100)  # Example range, adjust as necessary
        self.setValue(50)
        self.setMaximumSize(250, self.sizeHint().height())  # Set fixed size

    def mouseDoubleClickEvent(self, event):
        self.reset_default()
        super().mouseDoubleClickEvent(event)

    def reset_default(self):
        self.setValue(self.default_value)

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
            "Brightness": DoubleClickSlider(Qt.Orientation.Horizontal),
            "Contrast": DoubleClickSlider(Qt.Orientation.Horizontal),
            "Gamma": DoubleClickSlider(Qt.Orientation.Horizontal),
            "Shadows": DoubleClickSlider(Qt.Orientation.Horizontal),
            "Highlights": DoubleClickSlider(Qt.Orientation.Horizontal)
        }

        for i, (label, slider) in enumerate(self.sliders.items()):
            mod3 = i % 3
            div = i//3  
            qlabel = QLabel(str(label + " :"))
            qlabel.setMaximumSize(80, qlabel.sizeHint().height())  # Set fixed size
            qlabel.setAlignment(Qt.AlignmentFlag.AlignRight)
            self.lighting_layout.addWidget(qlabel, mod3, div*2)
            self.lighting_layout.addWidget(slider, mod3, (div*2)+1)

        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout.addItem(spacer)
        layout.addLayout(self.lighting_layout)
        layout.addItem(spacer)

        self.sliders["Shadows"].setDisabled(True) # NOT IMPLEMENTED 
        self.sliders["Highlights"].setDisabled(True) # NOT IMPLEMENTED 
    
    def reset_sliders(self):
        for i, (label, slider) in enumerate(self.sliders.items()):
            slider.reset_default()

    def print_values(self):
        for i, (label, slider) in enumerate(self.sliders.items()):
            print(slider.value())

class LightingWindow(QWidget):
    editing_confirmed = pyqtSignal(QPixmap, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Lighting Window")
        # self.setGeometry(100, 100, 800, 600)

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
        
        hdtsoi_button = QPushButton("Hold Down to See Original Image")
        hdtsoi_button.setFixedSize(300, 30)
        hdtsoi_button.pressed.connect(self.hdtsoi_pressed)
        hdtsoi_button.released.connect(self.hdtsoi_released)

        ok_button = QPushButton("OK")
        ok_button.setFixedSize(100, 30)
        ok_button.clicked.connect(self.ok_pressed)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedSize(100, 30)
        cancel_button.clicked.connect(self.cancel_pressed)
        
        confirmation_layout.addWidget(hdtsoi_button)
        confirmation_layout.addItem(spacer)
        confirmation_layout.addWidget(ok_button)
        confirmation_layout.addWidget(cancel_button)
        main_layout.addLayout(confirmation_layout)

        # Connect slider value changes to functions directly
        self.slider_layer.sliders["Brightness"].valueChanged.connect(self.adjust_brightness)
        self.slider_layer.sliders["Contrast"].valueChanged.connect(self.adjust_contrast)
        self.slider_layer.sliders["Shadows"].valueChanged.connect(self.adjust_shadows)
        self.slider_layer.sliders["Highlights"].valueChanged.connect(self.adjust_highlights)
        self.slider_layer.sliders["Gamma"].valueChanged.connect(self.adjust_gamma)
        
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
        self.slider_layer.reset_sliders()
        self.pixmap_image_orig = pixmap_image
        self.image_viewer.show_new_pixmap(pixmap_image)
    
    def hdtsoi_pressed(self):
        print( "HDtSOI", "Showing original image.")
        self.image_viewer.show_pixmap(self.image_viewer.get_original_pixmap())

    def hdtsoi_released(self):
        print( "HDtSOI", "Showing edited image.")
        self.image_viewer.show_pixmap(self.image_viewer.get_previous_pixmap())


    def ok_pressed(self):

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
        self.slider_layer.print_values()

        self.contrast_value = 1- self.slider_layer.sliders["Contrast"].value()/50.0
        self.brightness_value = self.slider_layer.sliders["Brightness"].value()/50.0 - 1
        self.gamma_value = 2 - self.slider_layer.sliders["Gamma"].value()/50.0
        self.shadows_value = self.slider_layer.sliders["Shadows"].value()/50.0
        self.highlights_value = self.slider_layer.sliders["Highlights"].value()/50.0
