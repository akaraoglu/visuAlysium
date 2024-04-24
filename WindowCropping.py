from PyQt6.QtWidgets import  QVBoxLayout, QHBoxLayout, QLabel, QSizePolicy, QSpacerItem, QLineEdit, QApplication
from PyQt6.QtCore import pyqtSlot, pyqtSignal, Qt, QSize
from PyQt6.QtGui import QPixmap, QIntValidator, QPalette

from WidgetUtils import HoverButton
from WindowImageViewerAbstract import ImageViewerWindowAbstract

class CropWindow_ButtonLayout(QHBoxLayout):
    flip_v_clicked = pyqtSignal()
    flip_h_clicked = pyqtSignal()
    rotate_r_clicked = pyqtSignal()
    rotate_l_clicked = pyqtSignal()
    crop_rectangle_changed = pyqtSignal(int,int,int,int)
    def __init__(self):
        super().__init__()
        
        self.button_size = QSize(120,60)  # Button size (width and height)
        self.icon_size = QSize(40,40)  # Icon size within the button

        # layout = QHBoxLayout()
        self.setAlignment(Qt.AlignmentFlag.AlignTop)  # Aligns widgets at the top within the layout
        # self.setLayout(layout)

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
        self.addItem(spacer)
        self.addLayout(self.crop_layout)
        self.addItem(spacer)

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

        line_edit = QLineEdit()

        palette = QApplication.instance().palette()
        line_edit.setStyleSheet(f"color: {palette.color(QPalette.ColorRole.Text).name()};")

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
        new_button = HoverButton(None, text=tooltip, icon=icon, button_size=self.button_size, icon_size=self.icon_size)
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
    
class WindowCropping(ImageViewerWindowAbstract):
    editing_confirmed = pyqtSignal(QPixmap, str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Crop Window")
        # Connect new signal to a method
        self.editing_options_layout.crop_rectangle_changed.connect(self.update_image_viewer_crop)
        self.image_viewer.crop_rectangle_changed.connect(self.update_crop_info_in_button_layer)

    def create_editing_options_layout(self):
        temp_layout = CropWindow_ButtonLayout()

        # Connect ButtonLayer signals to slot methods
        temp_layout.flip_v_clicked.connect(self.flip_vertical)
        temp_layout.flip_h_clicked.connect(self.flip_horizontal)
        temp_layout.rotate_r_clicked.connect(self.rotate_right)
        temp_layout.rotate_l_clicked.connect(self.rotate_left)
        return temp_layout
    
    def update_crop_info_in_button_layer(self, crop_rect):
        print("Crop rect changed!")
        print(crop_rect)
        # Assuming the crop_rect is a QRectF or similar
        self.editing_options_layout.set_crop_info(crop_rect.x(), crop_rect.y(), crop_rect.width(), crop_rect.height())

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
    
    # Define placeholder functions for slider adjustments
    def update_image(self):
        print("Update image")

    def reset_pressed(self):
        print("Reset placeholder.")

    def cancel_pressed(self):
        # Here you would typically revert any changes or simply close the window without applying changes
        print("Cancel", "Operation has been cancelled.")
        self.close() #to close the window
