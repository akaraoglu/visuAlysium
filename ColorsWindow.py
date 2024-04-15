from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QSizePolicy, QPushButton, QSpacerItem,  QGridLayout, QSlider, QApplication
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from ImageViewer import ImageViewer

from WidgetUtils import DoubleClickSlider

colors_slider_list = [ "Temperature",
                "Saturation",
                "Hue",
                "R",
                "G",
                "B"]

class ColorsWindow_ButtonLayout(QWidget):
    def __init__(self):
        super().__init__()
        self.button_size = 60
        self.icon_size = 40

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)

        self.lighting_layout = QGridLayout()

        # Add sliders
        self.sliders = {}
        for slider in colors_slider_list:
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

class ColorsWindow(QWidget):
    editing_confirmed = pyqtSignal(QPixmap, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Colors Window")
        # self.setGeometry(100, 100, 800, 600)

        # Assuming ImageViewer and LightingWindow_ButtonLayout are defined elsewhere
        self.image_viewer = ImageViewer()
        self.pixmap_image_orig = None
        self.slider_layer = ColorsWindow_ButtonLayout()

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
        self.slider_layer.sliders["Temperature"].valueChanged.connect(self.adjust_temperature)
        self.slider_layer.sliders["Saturation"].valueChanged.connect(self.adjust_saturation)
        self.slider_layer.sliders["Hue"].valueChanged.connect(self.adjust_hue)
        self.slider_layer.sliders["R"].valueChanged.connect(self.adjust_RGB)
        self.slider_layer.sliders["G"].valueChanged.connect(self.adjust_RGB)
        self.slider_layer.sliders["B"].valueChanged.connect(self.adjust_RGB)
        
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
    def adjust_temperature(self, value):
        self.read_values_from_sliders()
        self.image_viewer.adjust_colors(self.temperature_value, self.saturation_value, self.hue_value, self.red_value, self.green_value, self.blue_value)

    def adjust_saturation(self, value):
        self.read_values_from_sliders()
        self.image_viewer.adjust_colors(self.temperature_value, self.saturation_value, self.hue_value, self.red_value, self.green_value, self.blue_value)

    def adjust_hue(self, value):
        self.read_values_from_sliders()
        self.image_viewer.adjust_colors(self.temperature_value, self.saturation_value, self.hue_value, self.red_value, self.green_value, self.blue_value)

    def adjust_RGB(self, value):
        self.read_values_from_sliders()
        self.image_viewer.adjust_colors(self.temperature_value, self.saturation_value, self.hue_value, self.red_value, self.green_value, self.blue_value)

    def read_values_from_sliders(self):
        # self.slider_layer.print_values()

        self.temperature_value  = self.slider_layer.sliders["Temperature"].value()  /50.0
        self.saturation_value   = self.slider_layer.sliders["Saturation"].value()   /50.0
        self.hue_value          = 1 - self.slider_layer.sliders["Hue"].value()      /50.0
        self.red_value          = self.slider_layer.sliders["R"].value()            /50.0
        self.green_value        = self.slider_layer.sliders["G"].value()            /50.0
        self.blue_value         = self.slider_layer.sliders["B"].value()            /50.0
