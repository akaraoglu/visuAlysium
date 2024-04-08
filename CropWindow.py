from PyQt6.QtWidgets import QMainWindow,  QVBoxLayout, QHBoxLayout, QWidget, QLabel, QSizePolicy, QPushButton, QMessageBox, QSpacerItem, QToolBar
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QIcon, QAction
from ImageViewer import ImageViewer


class CropWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Editor")
        self.setGeometry(100, 100, 800, 600)

        # Create ImageViewer instance
        self.image_viewer = ImageViewer()
        self.pixmap_image_orig = None
        # Create actions for editing options
        flip_v_action = QAction(QIcon("icons/flip_v.png"), "Flip V", self)
        flip_v_action.triggered.connect(self.flip_vertical)

        flip_h_action = QAction(QIcon("icons/flip_h.png"), "Flip H", self)
        flip_h_action.triggered.connect(self.flip_horizontal)

        rotate_r_action = QAction(QIcon("icons/rotate_r.png"), "Rotate R", self)
        rotate_r_action.triggered.connect(self.rotate_right)

        rotate_l_action = QAction(QIcon("icons/rotate_l.png"), "Rotate L", self)
        rotate_l_action.triggered.connect(self.rotate_left)

        # Add actions to toolbar
        # Create a toolbar and set its orientation to horizontal
        self.toolbar = QToolBar()
        self.toolbar.setOrientation(Qt.Orientation.Vertical)

        # Add actions to the toolbar
        self.toolbar.addAction(flip_v_action)
        self.toolbar.addAction(flip_h_action)
        self.toolbar.addAction(rotate_r_action)
        self.toolbar.addAction(rotate_l_action)

        # Add the toolbar to the left side of the QMainWindow
        self.addToolBar(Qt.ToolBarArea.LeftToolBarArea, self.toolbar)

        # Create a central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Create layout for central widget
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.image_viewer)

        # Create layout for confirmation buttons
        confirmation_layout = QHBoxLayout()
        layout.addLayout(confirmation_layout)

        # Add spacer item to push buttons to the right
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        confirmation_layout.addItem(spacer)

        # Create OK and Cancel buttons with fixed sizes
        ok_button = QPushButton("OK")
        ok_button.setFixedSize(100, 30)
        ok_button.clicked.connect(self.ok_pressed)

        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedSize(100, 30)
        cancel_button.clicked.connect(self.cancel_pressed)

        # Add buttons to the confirmation layout
        confirmation_layout.addWidget(ok_button)
        confirmation_layout.addWidget(cancel_button)

    def set_image(self, pixmap_image):
        self.pixmap_image_orig = pixmap_image
        self.image_viewer.load_new_pixmap(pixmap_image)
        self.image_viewer.set_crop_mode(True)
        
    def flip_vertical(self):
        # Implement flip vertically functionality
        QMessageBox.information(self, "Flip V", "Implement flip vertically functionality.")

    def flip_horizontal(self):
        # Implement flip horizontally functionality
        QMessageBox.information(self, "Flip H", "Implement flip horizontally functionality.")

    def rotate_right(self):
        # Implement rotate right functionality
        QMessageBox.information(self, "Rotate R", "Implement rotate right functionality.")

    def rotate_left(self):
        # Implement rotate left functionality
        QMessageBox.information(self, "Rotate L", "Implement rotate left functionality.")

    def ok_pressed(self):
        # Implement OK button functionality
        QMessageBox.information(self, "OK", "Implement OK functionality.")

    def cancel_pressed(self):
        # Implement Cancel button functionality
        QMessageBox.information(self, "Cancel", "Implement Cancel functionality.")
