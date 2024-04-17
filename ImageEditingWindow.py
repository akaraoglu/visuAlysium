from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QSizePolicy, QPushButton, QSpacerItem,  QGridLayout, QSlider, QApplication
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from ImageViewer import ImageViewer

from WidgetUtils import DoubleClickSlider


class ImageEditingWindow_SliderLayout(QWidget):
    

    def __init__(self, slider_list):
        super().__init__()
        self.button_size = 60
        self.icon_size = 40

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

        self.lighting_layout = QGridLayout()

        # Add sliders
        self.sliders = {}
        for slider in slider_list:
            self.sliders[slider] = DoubleClickSlider(Qt.Orientation.Horizontal)

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
    
    def reset_sliders(self):
        for i, (label, slider) in enumerate(self.sliders.items()):
            slider.reset_default()

    def print_values(self):
        for i, (label, slider) in enumerate(self.sliders.items()):
            print(label, ":" , slider.value())

class ImageEditingsWindow(QWidget):
    editing_confirmed = pyqtSignal(QPixmap, str)
    slider_list = [ "slider1"]
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Editing Window")
        # self.setGeometry(100, 100, 800, 600)

        # Assuming ImageViewer and LightingWindow_ButtonLayout are defined elsewhere
        self.image_viewer = ImageViewer()
        self.pixmap_image_orig = None
        self.slider_layer = ImageEditingWindow_SliderLayout(slider_list=self.slider_list)
        self.create_sliders()

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

    def create_sliders(self):
        for slider in self.slider_list:
            self.slider_layer.sliders[slider].valueChanged.connect(self.slider_values_changed)

    def set_image(self, pixmap_image):
        self.slider_layer.reset_sliders()
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
        self.slider_values_changed(0)
        self.editing_confirmed.emit(self.image_viewer.get_current_pixmap(), "Lighting Adjustment")
        self.close() #to close the window

    def cancel_pressed(self):
        # Here you would typically revert any changes or simply close the window without applying changes
        print("Cancel", "Operation has been cancelled.")
        self.close() #to close the window

    # Define placeholder functions for slider adjustments
    def slider_values_changed(self, value):
        self.read_values_from_sliders()
        # self.image_viewer.adjust_colors(self.temperature_value, self.saturation_value, self.hue_value, self.red_value, self.green_value, self.blue_value)

    def read_values_from_sliders(self):
        # self.slider_layer.print_values()
        self.slider_value  = self.slider_layer.sliders["Slider1"].value()  /50.0

    def reset_pressed(self):
        self.slider_layer.reset_sliders()

    def histogram_pressed(self):
        self.image_viewer.toggle_info_display()