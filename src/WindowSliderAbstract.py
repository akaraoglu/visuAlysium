from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QSizePolicy, QPushButton, QSpacerItem,  QGridLayout, QSlider, QApplication
from PyQt6.QtCore import pyqtSignal, Qt, QSize
from PyQt6.QtGui import QPixmap
from src.ImageViewer import ImageViewer

from src.WidgetUtils import DoubleClickSlider
from src.WindowImageViewerAbstract import ImageViewerWindowAbstract

class SliderLayout(QHBoxLayout):

    def __init__(self, slider_list):
        super().__init__()
        
        self.button_size = QSize(120,60)  # Button size (width and height)
        self.icon_size = QSize(40,40)  # Icon size within the button


        # layout = QHBoxLayout()
        self.setAlignment(Qt.AlignmentFlag.AlignTop)
        # self.setLayout(layout)

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
        self.addItem(spacer)
        self.addLayout(self.lighting_layout)
        self.addItem(spacer)
    
    def reset_sliders(self):
        for i, (label, slider) in enumerate(self.sliders.items()):
            slider.reset_default()

    def print_values(self):
        for i, (label, slider) in enumerate(self.sliders.items()):
            print(label, ":" , slider.value())

class ImageEditingsWindow(ImageViewerWindowAbstract):
    editing_confirmed = pyqtSignal(QPixmap, str)
    slider_list = [ "slider1"]
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Editing Window")
    
    def create_editing_options_layout(self):
        temp_layout = SliderLayout(slider_list=self.slider_list)
   
        for slider in self.slider_list:
            temp_layout.sliders[slider].valueChanged.connect(self.slider_values_changed)
    
        return temp_layout
    
    def initialize_values(self):
        self.editing_options_layout.reset_sliders()

    # Define placeholder functions for slider adjustments
    def slider_values_changed(self, value):
        self.read_values_from_sliders()
        # self.image_viewer.adjust_colors(self.temperature_value, self.saturation_value, self.hue_value, self.red_value, self.green_value, self.blue_value)

    def read_values_from_sliders(self):
        # self.slider_layer.print_values()
        self.slider_value  = self.editing_options_layout.sliders["Slider1"].value()  /50.0

    def reset_pressed(self):
        self.editing_options_layout.reset_sliders()
