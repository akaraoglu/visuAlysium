from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QPushButton, QLabel, QListWidget, QListWidgetItem, QWidget, QSizePolicy, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt, QSize
from ImageViewer import ImageViewer
from HoverButton import HoverButton
from CropWindow import CropWindow

class ButtonLayer(QWidget):
    button_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.button_size = 60
        self.icon_size = 40

        layout = QGridLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Aligns widgets at the top within the layout
        self.setLayout(layout)

        # Create two columns of button lists with 10 buttons each
        for i in range(5):
            for k in range(2):
                # button = QPushButton("Button %d"%i)
                button = self.create_new_button(icon="icons/image_settings.png", connect_to= self.button_clicked)
                layout.addWidget(button, i, k)
                # print(i,k)
    
    def create_new_button(self, icon, connect_to):
        new_button = HoverButton(self, icon=icon, button_size=self.button_size, icon_size=self.icon_size)
        new_button.clicked.connect(self.button_clicked.emit)  # Connect button click to emit button_clicked signal
        return new_button

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
        self.cropWindow = CropWindow()

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.graphics_view = ImageViewer()
        self.history_widget = HistoryWidget()  # Create instance of HistoryWidget
        self.buttons_layer = ButtonLayer()

        main_layout = QGridLayout(central_widget)

        image_layout = QVBoxLayout()
        image_layout.addWidget(self.graphics_view)

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
        self.buttons_layer.button_clicked.connect(self.edit_button_clicked)

    def show_image(self,image_path):
        self.graphics_view.open(self.image_path) 
        self.history_widget.update_history_list(self.graphics_view.get_current_pixmap(), "Original Image")

    def edit_button_clicked(self):
        self.cropWindow.show()
        self.cropWindow.set_image(self.graphics_view.get_current_pixmap())

        # Handle edit button click event
        print("Handle edit button click event")
        pass  # Placeholder, put your code here to handle the edit button click
