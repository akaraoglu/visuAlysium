from PyQt6.QtWidgets import QMainWindow,  QVBoxLayout, QHBoxLayout, QWidget, QLabel, QSizePolicy, QPushButton, QMessageBox, QSpacerItem, QToolBar, QGridLayout, QLineEdit, QApplication
from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt, QSize, QPoint, QRect, QRectF, QPointF, QSizeF
from PyQt6.QtGui import QPixmap, QIcon, QAction, QIntValidator
from ImageViewer import ImageViewer
from WidgetUtils import HoverButton

class CropWindow_ButtonLayout(QWidget):
    flip_v_clicked = pyqtSignal()
    flip_h_clicked = pyqtSignal()
    rotate_r_clicked = pyqtSignal()
    rotate_l_clicked = pyqtSignal()
    crop_rectangle_changed = pyqtSignal(int,int,int,int)
    def __init__(self):
        super().__init__()
        
        self.button_size = 60  # Button size (width and height)
        self.icon_size = 40  # Icon size within the button

        layout = QHBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)  # Aligns widgets at the top within the layout
        self.setLayout(layout)

        # Create and add buttons for each action
        self.add_button("icons/flip_v.png", "Flip Vertically", self.flip_v_clicked)
        self.add_button("icons/flip_h.png", "Flip Horizontally", self.flip_h_clicked)
        self.add_button("icons/rotate_r.png", "Rotate Right", self.rotate_r_clicked)
        self.add_button("icons/rotate_l.png", "Rotate Left", self.rotate_l_clicked)
            
        # Layout for crop info
        self.crop_layout = QVBoxLayout()
        self.crop_layout_settings = QHBoxLayout()
        self.crop_layout.addWidget(QLabel("Cropping Settings:"))        
        
       # Creating QLineEdit widgets for crop rectangle information using the new method
        self.crop_x_edit = self.add_crop_edit_line("X:", self.update_crop_rectangle)
        self.crop_y_edit = self.add_crop_edit_line("Y:", self.update_crop_rectangle)
        self.crop_width_edit = self.add_crop_edit_line("Width:", self.update_crop_rectangle)
        self.crop_height_edit = self.add_crop_edit_line("Height:", self.update_crop_rectangle)


        self.crop_layout.addLayout(self.crop_layout_settings)
        # Assuming `layout` is the main layout, add the crop layout
        # Add a spacer item between the buttons and the crop info label
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        layout.addItem(spacer)
        layout.addLayout(self.crop_layout)
        layout.addItem(spacer)

    def add_crop_edit_line(self,placeholder,signal_function):
        """
        Creates, configures, and returns a QLineEdit widget for crop dimension input.
        """
        text_layout = QVBoxLayout()

        # Assuming a character width of about 10 pixels for a digit, plus some padding.
        digit_width = 10
        padding = 20  # Add padding for aesthetics
        max_digits = 5
        line_edit_width = (digit_width * max_digits) + padding

        line_edit = QLineEdit(self)
        line_edit.setFixedWidth(line_edit_width)
        line_edit.setPlaceholderText(placeholder)
        max_value = 99999
        line_edit.setValidator(QIntValidator(0, max_value, self))
        line_edit.setMaxLength(5)  # Optional: if you want to strictly enforce a 4-digit maximum
        
        text_layout.addWidget(QLabel(placeholder))
        text_layout.addWidget(line_edit)
        self.crop_layout_settings.addLayout(text_layout)

        line_edit.editingFinished.connect(signal_function)

        return line_edit
        
    def add_button(self, icon, tooltip, signal):
        new_button = HoverButton(self, icon=icon, button_size=self.button_size, icon_size=self.icon_size)
        new_button.setToolTip(tooltip)
        new_button.clicked.connect(signal.emit)  # Connect button click to emit button_clicked signal
        self.layout().addWidget(new_button)

    def update_crop_rectangle(self):
        # Method to emit signal with new crop rectangle information
        x = int(self.crop_x_edit.text())
        y = int(self.crop_y_edit.text())
        width = int(self.crop_width_edit.text())
        height = int(self.crop_height_edit.text())
        self.crop_rectangle_changed.emit(x, y, width, height)

    def set_crop_info(self, x, y, width, height):
        self.crop_x_edit.setText(str(int(x)))
        self.crop_y_edit.setText(str(int(y)))
        self.crop_width_edit.setText(str(int(width)))
        self.crop_height_edit.setText(str(int(height)))
    
class CropWindow(QWidget):
    editing_confirmed = pyqtSignal(QPixmap, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crop Window")
        self.setGeometry(100, 100, 800, 600)

        # Assuming ImageViewer and CropWindow_ButtonLayout are defined elsewhere
        self.image_viewer = ImageViewer()
        self.image_viewer.info_widget.setVisible(False)
        
        self.pixmap_image_orig = None
        self.button_layer = CropWindow_ButtonLayout()

        # Connect ButtonLayer signals to slot methods
        self.button_layer.flip_v_clicked.connect(self.flip_vertical)
        self.button_layer.flip_h_clicked.connect(self.flip_horizontal)
        self.button_layer.rotate_r_clicked.connect(self.rotate_right)
        self.button_layer.rotate_l_clicked.connect(self.rotate_left)

        # Create the main layout for the widget
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(self.image_viewer)
        main_layout.addWidget(self.button_layer)

        # Layout for confirmation buttons
        confirmation_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        confirmation_layout.addItem(spacer)

        ok_button = QPushButton("OK")
        ok_button.setFixedSize(100, 30)
        ok_button.clicked.connect(self.ok_pressed)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedSize(100, 30)
        cancel_button.clicked.connect(self.cancel_pressed)
        
        confirmation_layout.addWidget(ok_button)
        confirmation_layout.addWidget(cancel_button)
        main_layout.addLayout(confirmation_layout)

        # Connect new signal to a method
        self.button_layer.crop_rectangle_changed.connect(self.update_image_viewer_crop)
        self.image_viewer.crop_rectangle_changed.connect(self.update_crop_info_in_button_layer)

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
    
    def keyPressEvent(self, event):
        self.image_viewer.keyPressEvent(event)
        super().keyPressEvent(event)
        
    def update_crop_info_in_button_layer(self, crop_rect):
        # Assuming the crop_rect is a QRectF or similar
        self.button_layer.set_crop_info(crop_rect.x(), crop_rect.y(), crop_rect.width(), crop_rect.height())

    def update_image_viewer_crop(self, x, y, width, height):
        # Update the crop rectangle of the image viewer
        print("Update the crop rectangle of the image viewer")
        self.image_viewer.set_crop_rectangle(x, y, width, height)

    def set_image(self, pixmap_image):
        
        self.pixmap_image_orig = pixmap_image
        self.image_viewer.set_crop_mode(True)
        self.image_viewer.show_new_pixmap(pixmap_image)
        
        self.image_viewer.reset_rect()

    def flip_vertical(self):
        if self.image_viewer.get_current_pixmap() is not None:
            # Assuming ImageViewer has a method to flip the image vertically
            self.image_viewer.flip_vertical()
            print("Flip Vertical", "The image has been flipped vertically.")

    def flip_horizontal(self):
        if self.image_viewer.get_current_pixmap() is not None:
            # Assuming ImageViewer has a method to flip the image horizontally
            self.image_viewer.flip_horizontal()
            print( "Flip Horizontal", "The image has been flipped horizontally.")

    def rotate_right(self):
        if self.image_viewer.get_current_pixmap() is not None:
            # Assuming ImageViewer has a method to rotate the image 90 degrees to the right
            self.image_viewer.rotate_right()
            print( "Rotate Right", "The image has been rotated 90 degrees to the right.")

    def rotate_left(self):
        if self.image_viewer.get_current_pixmap() is not None:
            # Assuming ImageViewer has a method to rotate the image 90 degrees to the left
            self.image_viewer.rotate_left()
            print("Rotate Left", "The image has been rotated 90 degrees to the left.")

    def ok_pressed(self):
        # Here you would typically confirm the changes and possibly close the window or reset it for another operation
        print( "OK", "Changes have been applied.")
        # self.image_viewer.get_current_crop_rect()
        self.image_viewer.crop_image(self.image_viewer.get_current_crop_rect())

        self.editing_confirmed.emit(self.image_viewer.get_current_pixmap(), "Crop and Rotate")
        self.close() #to close the window

    def cancel_pressed(self):
        # Here you would typically revert any changes or simply close the window without applying changes
        print("Cancel", "Operation has been cancelled.")
        self.close() #to close the window
