from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QPushButton, QLabel, QListWidget, QListWidgetItem, QWidget, QSizePolicy, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt, QSize
from ImageViewer import ImageViewer
from HoverButton import HoverButton
from CropWindow import CropWindow

class ButtonLayer(QWidget):
    # Define signals for different button actions
    button_crop_clicked = pyqtSignal()
    button_brightness_clicked = pyqtSignal()
    button_colors_clicked = pyqtSignal()
    button_edit_image_clicked = pyqtSignal()
    button_effects_clicked = pyqtSignal()
    button_de_noise_clicked = pyqtSignal()
    button_histogram_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.button_size = 60  # Button size
        self.icon_size = 40  # Icon size inside the button

        # Create a layout for buttons
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Aligns widgets at the top within the layout
        self.setLayout(layout)

        # Create and add buttons for each action
        self.add_button("icons/crop.png", "Adjust Cropping", self.button_crop_clicked)
        self.add_button("icons/brightness.png", "Adjust Lighting", self.button_brightness_clicked)
        self.add_button("icons/colors.png", "Adjust Colors", self.button_colors_clicked)
        self.add_button("icons/edit-image.png", "Adjust Levels", self.button_edit_image_clicked)
        self.add_button("icons/button_effects.png", "Sharpness", self.button_effects_clicked)
        # Assuming the "De-Noise" button should have a unique action, use `button_de_noise_clicked` signal
        self.add_button("icons/button_effects.png", "De-Noise", self.button_de_noise_clicked)
        self.add_button("icons/histogram.png", "Histogram", self.button_histogram_clicked)
        

    def add_button(self, icon, tooltip, signal):
        # Assuming HoverButton is a custom button class that supports `setToolTip` and `clicked` signal
        new_button = HoverButton(self, icon=icon, button_size=self.button_size, icon_size=self.icon_size)
        new_button.setToolTip(tooltip)  # Set tooltip for the button
        new_button.clicked.connect(signal.emit)  # Connect button click to the respective signal
        self.layout().addWidget(new_button)  # Add button to the layout

class HistoryWidget(QWidget):
    def __init__(self):
        super().__init__()
        
        layout = QVBoxLayout(self)
        self.label = QLabel("Editing History")
        layout.addWidget(self.label)
        
        self.history_list_widget = QListWidget()
        self.history_list_widget.setViewMode(QListWidget.ViewMode.IconMode)  # Set the view mode to IconMode
        self.history_list_widget.setIconSize(QSize(300, 100))  # Set the icon size to 100x100 pixels
        self.history_list_widget.setWordWrap(True)  # Enable word wrap
        # self.history_list_widget.setTextElideMode(Qt.TextElideMode.ElideRight)  # Set text elide mode to elide right
        # self.history_list_widget.setUniformItemSizes(True)  # Enable uniform item sizes
        # self.history_list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)  # Set resize mode to Adjust
        self.history_list_widget.setSpacing(10)  # Set spacing between items

        layout.addWidget(self.history_list_widget)

    def update_history_list(self, pixmap, description=""):
        item = QListWidgetItem(QIcon(pixmap), description)
        item.setToolTip(description)  # Set tooltip to display full file name
        item.setSizeHint(QSize(200, 120))  # Set a fixed size for the items

        item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)  # Bottom Center align text
        
        self.history_list_widget.addItem(item)

class ImageViewerWindow(QMainWindow):
    def __init__(self, image_path):
        super().__init__()
        self.setWindowTitle("Image Viewer")
        self.image_path = image_path
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.image_viewer = ImageViewer()
        self.history_widget = HistoryWidget()  # Create instance of HistoryWidget
        self.buttons_layer = ButtonLayer()

        main_layout = QGridLayout(central_widget)

        image_layout = QVBoxLayout()
        image_layout.addWidget(self.image_viewer)

        main_layout.addWidget(self.buttons_layer, 0, 0)
        main_layout.addLayout(image_layout, 0, 1)
        main_layout.addWidget(self.history_widget, 0, 2)
        
        # Set column stretch to achieve desired proportions
        main_layout.setColumnStretch(0, 0)  
        main_layout.setColumnStretch(1, 10)  
        main_layout.setColumnStretch(2, 0)  

        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

        # Adjust window size to half of the screen size
        screen = QApplication.primaryScreen()
        screen_size = screen.size()
        half_screen_size = screen_size / 2
        self.resize(half_screen_size)

        # Connect button signal to slot
        self.buttons_layer.button_crop_clicked.connect(self.edit_button_clicked)

    def show_image(self,image_path):
        self.image_viewer.open(self.image_path) 
        self.history_widget.update_history_list(self.image_viewer.get_current_pixmap(), "Original Image")

    def edit_button_clicked(self):
        self.cropWindow = CropWindow()
        self.cropWindow.crop_confirmed.connect(self.cropping_confirmed)
        self.cropWindow.show()
        self.cropWindow.set_image(self.image_viewer.get_current_pixmap())
        # Handle edit button click event
        print("Handle edit button click event")
        pass  # Placeholder, put your code here to handle the edit button click
    
    def cropping_confirmed(self, pixmap):
        print("cropping_confirmed")
        self.image_viewer.load_new_pixmap(pixmap)
        self.history_widget.update_history_list(pixmap,"Crop and rotate.")
        
        # print(f"Rectangle Coordinates: Top Left ({rect.topLeft().x()}, {rect.topLeft().y()}) - Bottom Right ({rect.bottomRight().x()}, {rect.bottomRight().y()})")
        # print(f"Rectangle Size: Width {rect.width()} - Height {rect.height()}")
