from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QPushButton, QLabel, QListWidget, QListWidgetItem, QWidget, QSizePolicy, QVBoxLayout, QHBoxLayout
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt, QSize
from ImageViewer import ImageViewer

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

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.graphics_view = ImageViewer()
        self.edit_button = QPushButton("Edit")
        self.history_widget = HistoryWidget()  # Create instance of HistoryWidget

        main_layout = QGridLayout(central_widget)

        buttons_layout = QVBoxLayout()
        buttons_layout.addWidget(self.edit_button)
        
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.graphics_view)

        main_layout.addLayout(buttons_layout, 0,0)
        main_layout.addLayout(image_layout, 0, 1)
        main_layout.addWidget(self.history_widget, 0, 2)
        
        # Set column stretch to achieve desired proportions
        main_layout.setColumnStretch(0, 1)  
        main_layout.setColumnStretch(1, 10)  
        main_layout.setColumnStretch(2, 2)  

        self.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.MinimumExpanding)

        # Adjust window size to half of the screen size
        screen = QApplication.primaryScreen()
        screen_size = screen.size()
        half_screen_size = screen_size / 2
        self.resize(half_screen_size)

        self.graphics_view.load_new_image(image_path)
        self.history_widget.update_history_list(self.graphics_view.get_current_pixmap(), "Original Image")

        # Connect button signal to slot
        self.edit_button.clicked.connect(self.edit_button_clicked)

    # def update_history_list(self, image_path, description=""):
    #     # Add thumbnail and description to history list
    #     pixmap = QPixmap(image_path).scaled(150, 150)  # Resize the image to thumbnail size
    #     item = QListWidgetItem(QIcon(pixmap), description)  # Empty string for icon
    #     item.setToolTip(description)  # Set tooltip to display full file name
    #     self.history_list.addItem(item)
    #     # Set the item widget for the current item
    #     item.setSizeHint(QSize(150, 200))  # Set the size of each item

    def edit_button_clicked(self):
        # Handle edit button click event
        pass  # Placeholder, put your code here to handle the edit button click
