from PyQt6.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLabel, QSizePolicy, QPushButton, QSpacerItem,  QGridLayout, QSlider, QApplication
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QPixmap
from ImageViewer import ImageViewer

class ImageViewerWindowAbstract(QWidget):
    editing_confirmed = pyqtSignal(QPixmap, str)
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Viewer Window")
        # self.setGeometry(100, 100, 800, 600)

        # Assuming ImageViewer and LightingWindow_ButtonLayout are defined elsewhere
        self.image_viewer = ImageViewer()
        self.pixmap_image_orig = None

        # Abstract method to setup editing options
        self.editing_options_layout = self.create_editing_options_layout()


        self.confirmation_layout = QHBoxLayout()
        self.setup_generic_buttons(self.confirmation_layout)

        # Create the main layout for the widget
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.image_viewer)
        main_layout.addLayout(self.editing_options_layout)
        main_layout.addLayout(self.confirmation_layout)

        # Center and size the window
        self.center_and_size_window()
    
    def create_editing_options_layout(self):
        """
        Create and return the layout for editing options.
        Must be implemented by any subclass.
        """
        temp_layout = QHBoxLayout()
        return temp_layout
    
    def center_and_size_window(self):
        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)
        screen = QApplication.primaryScreen()
        screen_size = screen.size()
        width = screen_size.width() // 2
        height = (2 * screen_size.height()) // 3
        x = (screen_size.width() - width) // 2
        y = (screen_size.height() - height) // 2
        self.setGeometry(x, y, width, height)
    
    def setup_generic_buttons(self, layout):
        # Buttons for various actions
        hdtsoi_button = QPushButton("Hold Down to See Original Image")
        hdtsoi_button.pressed.connect(self.hdtsoi_pressed)
        hdtsoi_button.released.connect(self.hdtsoi_released)
        
        reset_button = QPushButton("Reset")
        reset_button.pressed.connect(self.reset_pressed)
        
        hist_button = QPushButton("Histogram")
        hist_button.pressed.connect(self.histogram_pressed)
        
        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.ok_pressed)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.cancel_pressed)
        
        # Adding buttons to layout
        layout.addWidget(hdtsoi_button)
        layout.addWidget(reset_button)
        layout.addWidget(hist_button)
        layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addWidget(ok_button)
        layout.addWidget(cancel_button)

    def set_image(self, pixmap_image):
        self.initialize_values()
        self.pixmap_image_orig = pixmap_image
        new_width = 1024
        new_height = 1024
        scaled_pixmap = pixmap_image.scaled(new_width, new_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        self.image_viewer.show_new_pixmap(scaled_pixmap)
    
    def initialize_values(self):
        print("Fill the function with necessary initialization values")

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
        self.editing_confirmed.emit(self.image_viewer.get_current_pixmap(), "Lighting Adjustment")
        self.close() #to close the window

    def cancel_pressed(self):
        # Here you would typically revert any changes or simply close the window without applying changes
        print("Cancel", "Operation has been cancelled.")
        self.close() #to close the window

    # Define placeholder functions for slider adjustments
    def update_image(self):
        print("Update image")

    def reset_pressed(self):
        print("Reset placeholder.")

    def histogram_pressed(self):
        self.image_viewer.toggle_info_display()
    
    def keyPressEvent(self, event):
        self.image_viewer.keyPressEvent(event)
        super().keyPressEvent(event)