from PyQt6.QtWidgets import QApplication, QGridLayout, QLabel, QListWidget, QListWidgetItem, QWidget, QSizePolicy, QVBoxLayout, QMenu
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt, QSize
from src.ImageViewer import ImageViewer
from src.WidgetUtils import HoverButton
from src.WindowCropping import WindowCropping

from src.WindowLighting import WindowLighting
from src.WindowColors import WindowColors
from src.WindowCurveAdjustement import WindowCurveAdjustement

class ImageEditor_ButtonLayout(QWidget):
    
    # Define signals for different button actions
    button_crop_clicked = pyqtSignal()
    button_brightness_clicked = pyqtSignal()
    button_colors_clicked = pyqtSignal()
    button_edit_curve_clicked = pyqtSignal()
    button_effects_clicked = pyqtSignal()
    button_de_noise_clicked = pyqtSignal()
    button_histogram_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.button_size = QSize(120,60)  # Button size (width and height)
        self.icon_size = QSize(40,40)  # Icon size within the button

        # Create a layout for buttons
        layout = QGridLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Aligns widgets at the top within the layout
        self.setLayout(layout)

        # Create and add buttons for each action
        self.add_button("icons/histogram.png", "Histogram", self.button_histogram_clicked)
        self.add_button("icons/crop.png", "Cropping", self.button_crop_clicked)
        self.add_button("icons/brightness.png", "Lighting", self.button_brightness_clicked)
        self.add_button("icons/colors.png", "Colors", self.button_colors_clicked)
        self.add_button("icons/edit-image.png", "Curves", self.button_edit_curve_clicked)
        self.add_button("icons/edit-image-2.png", "Sharpness", self.button_effects_clicked)
        # Assuming the "De-Noise" button should have a unique action, use `button_de_noise_clicked` signal
        self.add_button("icons/edit-image-2.png", "De-Noise", self.button_de_noise_clicked)
        
        

    def add_button(self, icon, tooltip, signal):
        # Assuming HoverButton is a custom button class that supports `setToolTip` and `clicked` signal
        new_button = HoverButton(self, text=tooltip, icon=icon, button_size=self.button_size, icon_size=self.icon_size)
        new_button.setToolTip(tooltip)  # Set tooltip for the button
        new_button.clicked.connect(signal.emit)  # Connect button click to the respective signal
        self.layout().addWidget(new_button)  # Add button to the layout

class HistoryWidget(QWidget):
    show_image_requested = pyqtSignal(QPixmap)
    delete_image_requested = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        self.label = QLabel("Editing History")
        layout.addWidget(self.label)

        self.history_list_widget = QListWidget()
        self.history_list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.history_list_widget.setIconSize(QSize(300, 100))
        self.history_list_widget.setWordWrap(True)
        self.history_list_widget.setSpacing(10)

        layout.addWidget(self.history_list_widget)
        self.original_pixmaps = []  # List to store original pixmaps
        # Connect the itemDoubleClicked signal to a slot
        self.history_list_widget.itemDoubleClicked.connect(self.onItemDoubleClicked)
    
    def clearHistory(self):
        self.history_list_widget.clear()
        for pix in self.original_pixmaps:
            del pix # Also remove the pixmap reference
        self.original_pixmaps = []

    def update_history_list(self, pixmap, description=""):
        self.original_pixmaps.append(pixmap)  # Store the original pixmap
        # icon = QIcon(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))  # Scale for display
        # item = QListWidgetItem(icon, description)
        item = QListWidgetItem(QIcon(pixmap), description)
        item.setToolTip(description)
        item.setSizeHint(QSize(200, 120))
        item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.history_list_widget.addItem(item)
            
    def onItemDoubleClicked(self, item):
        row = self.history_list_widget.row(item)
        if row != -1:
            self.show_image_requested.emit(self.original_pixmaps[row])

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        show_action = context_menu.addAction("Show Image")
        delete_action = context_menu.addAction("Delete Image")
        
        # Get the row of the item right-clicked on
        row = self.history_list_widget.indexAt(self.history_list_widget.mapFromGlobal(event.globalPos())).row()

        # Only add the delete option if the item is not the first one
        # Assuming the first item (index 0) is the original image
        if row < 1:
            delete_action.setDisabled(True)

        action = context_menu.exec(event.globalPos())

        if action == show_action:
            if row != -1:
                self.show_image_requested.emit(self.original_pixmaps[row])
        elif action == delete_action:
            if row != -1:
                self.delete_image_requested.emit(row)
                self.history_list_widget.takeItem(row)
                del self.original_pixmaps[row]  # Also remove the pixmap reference
                if row < self.history_list_widget.count(): 
                    self.show_image_requested.emit(self.original_pixmaps[row])
                else:
                    self.show_image_requested.emit(self.original_pixmaps[row-1])

class ImageViewerWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Viewer Window")
      
        self.image_viewer = ImageViewer()
        
        self.history_widget = HistoryWidget()  # Create instance of HistoryWidget
        self.buttons_layer = ImageEditor_ButtonLayout()
        
        self.crop_window = WindowCropping()
        self.crop_window.editing_confirmed.connect(self.editing_confirmed)
        self.lighting_window = WindowLighting()
        self.lighting_window.editing_confirmed.connect(self.editing_confirmed)
        self.colors_window = WindowColors()
        self.colors_window.editing_confirmed.connect(self.editing_confirmed)
        self.curve_editing = WindowCurveAdjustement()
        self.curve_editing.editing_confirmed.connect(self.editing_confirmed)

        main_layout = QGridLayout(self)
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
        self.buttons_layer.button_crop_clicked.connect(self.crop_button_clicked)
        self.buttons_layer.button_brightness_clicked.connect(self.brightness_button_clicked)
        self.buttons_layer.button_colors_clicked.connect(self.colors_button_clicked)
        self.buttons_layer.button_edit_curve_clicked.connect(self.button_edit_curve_clicked)
        self.buttons_layer.button_histogram_clicked.connect(self.image_viewer.toggle_info_display)
        self.history_widget.show_image_requested.connect(self.show_image_from_history)
        self.history_widget.delete_image_requested.connect(self.delete_image_from_history)
        
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
        self.image_viewer.setFocus()
    
    def keyPressEvent(self, event):
        self.image_viewer.keyPressEvent(event)
        super().keyPressEvent(event)
        
    def show_image_from_history(self, pixmap):
        self.image_viewer.show_pixmap(pixmap)  # Assuming your ImageViewer widget has a method to set a QPixmap

    def delete_image_from_history(self, index):
        # Handle the deletion of an image from the history
        print(f"Image at index {index} has been requested to delete")

    def show_new_image(self,image_path):
        self.history_widget.clearHistory()
        self.image_viewer.open_new_image(image_path)
        self.image_viewer.show_image_fit_to_screen()
        # self.image_viewer.open_new_image(image_path)
        self.history_widget.update_history_list(self.image_viewer.get_current_pixmap(), "Original Image")
        self.image_viewer.show_image_initial_size()

    def crop_button_clicked(self):
        self.crop_window.show()
        self.crop_window.set_image(self.image_viewer.get_current_pixmap())
        
    def brightness_button_clicked(self):
        self.lighting_window.show()
        self.lighting_window.set_image(self.image_viewer.get_current_pixmap())

    def colors_button_clicked(self):
        self.colors_window.show()
        self.colors_window.set_image(self.image_viewer.get_current_pixmap())

    def button_edit_curve_clicked(self):
        self.curve_editing.show()
        self.curve_editing.set_image(self.image_viewer.get_current_pixmap())

    def editing_confirmed(self, pixmap, description):
        print("Editing confirmed!")
        self.image_viewer.show_pixmap(pixmap)
        self.history_widget.update_history_list(pixmap, description)

        # print(f"Rectangle Coordinates: Top Left ({rect.topLeft().x()}, {rect.topLeft().y()}) - Bottom Right ({rect.bottomRight().x()}, {rect.bottomRight().y()})")
        # print(f"Rectangle Size: Width {rect.width()} - Height {rect.height()}")
