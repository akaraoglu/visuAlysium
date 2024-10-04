from PyQt6.QtWidgets import QApplication, QGridLayout, QLabel, QListWidget, QListWidgetItem, QWidget, QSizePolicy, QVBoxLayout, QMenu
from PyQt6.QtGui import QPixmap, QIcon
from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt, QSize
from src.ImageViewer import ImageViewer
from src.WidgetUtils import HoverButton
from src.WindowCropping import WindowCropping

from src.WindowLighting import WindowLighting
from src.WindowColors import WindowColors
from src.WindowCurveAdjustement import WindowCurveAdjustement

class ImageViewerWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Viewer Window")
      
        self.__image_viewer = ImageViewer()
        
        self.__history_widget = HistoryWidget()  # Create instance of HistoryWidget
        self.__buttons_layer = ImageEditor_ButtonLayout()
        
        self.__crop_window = WindowCropping()
        self.__crop_window.editing_confirmed.connect(self.editing_confirmed)
        self.__lighting_window = WindowLighting()
        self.__lighting_window.editing_confirmed.connect(self.editing_confirmed)
        self.__colors_window = WindowColors()
        self.__colors_window.editing_confirmed.connect(self.editing_confirmed)
        self.__curve_editing = WindowCurveAdjustement()
        self.__curve_editing.editing_confirmed.connect(self.editing_confirmed)

        main_layout = QGridLayout(self)
        image_layout = QVBoxLayout()
        image_layout.addWidget(self.__image_viewer)

        main_layout.addWidget(self.__buttons_layer, 0, 0)
        main_layout.addLayout(image_layout, 0, 1)
        main_layout.addWidget(self.__history_widget, 0, 2)
        
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
        self.__buttons_layer.button_crop_clicked.connect(self.crop_button_clicked)
        self.__buttons_layer.button_brightness_clicked.connect(self.brightness_button_clicked)
        self.__buttons_layer.button_colors_clicked.connect(self.colors_button_clicked)
        self.__buttons_layer.button_edit_curve_clicked.connect(self.button_edit_curve_clicked)
        self.__buttons_layer.button_histogram_clicked.connect(self.__image_viewer.toggle_info_display)
        self.__history_widget.show_image_requested.connect(self.show_image_from_history)
        self.__history_widget.delete_image_requested.connect(self.delete_image_from_history)
        
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
        self.__image_viewer.setFocus()
    
    def keyPressEvent(self, event):
        self.__image_viewer.keyPressEvent(event)
        super().keyPressEvent(event)
        
    def show_image_from_history(self, pixmap):
        self.__image_viewer.show_pixmap(pixmap)  # Assuming your ImageViewer widget has a method to set a QPixmap

    def delete_image_from_history(self, index):
        # Handle the deletion of an image from the history
        print(f"Image at index {index} has been requested to delete")

    def show_new_image(self,image_path):
        self.__history_widget.clearHistory()
        self.__image_viewer.open_new_image(image_path)
        self.__image_viewer.show_image_fit_to_screen()
        # self.__image_viewer.open_new_image(image_path)
        self.__history_widget.update_history_list(self.__image_viewer.get_current_pixmap(), "Original Image")
        self.__image_viewer.show_image_initial_size()

    def crop_button_clicked(self):
        self.__crop_window.show()
        self.__crop_window.set_image(self.__image_viewer.get_current_pixmap())
        
    def brightness_button_clicked(self):
        self.__lighting_window.show()
        self.__lighting_window.set_image(self.__image_viewer.get_current_pixmap())

    def colors_button_clicked(self):
        self.__colors_window.show()
        self.__colors_window.set_image(self.__image_viewer.get_current_pixmap())

    def button_edit_curve_clicked(self):
        self.__curve_editing.show()
        self.__curve_editing.set_image(self.__image_viewer.get_current_pixmap())

    def editing_confirmed(self, pixmap, description):
        print("Editing confirmed!")
        self.__image_viewer.show_pixmap(pixmap)
        self.__history_widget.update_history_list(pixmap, description)

        # print(f"Rectangle Coordinates: Top Left ({rect.topLeft().x()}, {rect.topLeft().y()}) - Bottom Right ({rect.bottomRight().x()}, {rect.bottomRight().y()})")
        # print(f"Rectangle Size: Width {rect.width()} - Height {rect.height()}")

class HistoryWidget(QWidget):
    show_image_requested = pyqtSignal(QPixmap)
    delete_image_requested = pyqtSignal(int)

    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        self.__label = QLabel("Editing History")
        layout.addWidget(self.__label)

        self.__history_list_widget = QListWidget()
        self.__history_list_widget.setViewMode(QListWidget.ViewMode.IconMode)
        self.__history_list_widget.setIconSize(QSize(300, 100))
        self.__history_list_widget.setWordWrap(True)
        self.__history_list_widget.setSpacing(10)

        layout.addWidget(self.__history_list_widget)
        self.__original_pixmaps = []  # List to store original pixmaps
        # Connect the itemDoubleClicked signal to a slot
        self.__history_list_widget.itemDoubleClicked.connect(self.onItemDoubleClicked)
    
    def clearHistory(self):
        self.__history_list_widget.clear()
        for pix in self.__original_pixmaps:
            del pix # Also remove the pixmap reference
        self.__original_pixmaps = []

    def update_history_list(self, pixmap, description:str=""):
        self.__original_pixmaps.append(pixmap)  # Store the original pixmap
        # icon = QIcon(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))  # Scale for display
        # item = QListWidgetItem(icon, description)
        item = QListWidgetItem(QIcon(pixmap), description)
        item.setToolTip(description)
        item.setSizeHint(QSize(200, 120))
        item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
        self.__history_list_widget.addItem(item)
            
    def onItemDoubleClicked(self, item):
        row = self.__history_list_widget.row(item)
        if row != -1:
            self.show_image_requested.emit(self.__original_pixmaps[row])

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        show_action = context_menu.addAction("Show Image")
        delete_action = context_menu.addAction("Delete Image")
        
        # Get the row of the item right-clicked on
        row = self.__history_list_widget.indexAt(self.__history_list_widget.mapFromGlobal(event.globalPos())).row()

        # Only add the delete option if the item is not the first one
        # Assuming the first item (index 0) is the original image
        if row < 1:
            delete_action.setDisabled(True)

        action = context_menu.exec(event.globalPos())

        if action == show_action:
            if row != -1:
                self.show_image_requested.emit(self.__original_pixmaps[row])
        elif action == delete_action:
            if row != -1:
                self.delete_image_requested.emit(row)
                self.__history_list_widget.takeItem(row)
                del self.__original_pixmaps[row]  # Also remove the pixmap reference
                if row < self.__history_list_widget.count(): 
                    self.show_image_requested.emit(self.__original_pixmaps[row])
                else:
                    self.show_image_requested.emit(self.__original_pixmaps[row-1])


class ImageEditor_ButtonLayout(QWidget):
    """Widget for holding action buttons in a layout """
    # Define signals for different button actions
    button_crop_clicked = pyqtSignal()
    button_brightness_clicked = pyqtSignal()
    button_colors_clicked = pyqtSignal()
    button_edit_curve_clicked = pyqtSignal()
    button_effects_clicked = pyqtSignal()
    button_de_noise_clicked = pyqtSignal()
    button_histogram_clicked = pyqtSignal()
    
    BUTTON_SIZE = QSize(120, 60)
    ICON_SIZE = QSize(40, 40)

    def __init__(self):
        super().__init__()
        
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
        new_button = HoverButton(self, text=tooltip, icon=icon, button_size=self.BUTTON_SIZE, icon_size=self.ICON_SIZE)
        new_button.setToolTip(tooltip)  # Set tooltip for the button
        new_button.clicked.connect(signal.emit)  # Connect button click to the respective signal
        self.layout().addWidget(new_button)  # Add button to the layout
