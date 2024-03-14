import os
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeView, QVBoxLayout, QHBoxLayout, QWidget, QListWidget, QListWidgetItem, QLabel, QSplitter, QMenu
from PyQt6.QtGui import QPixmap, QIcon, QFileSystemModel , QAction
from PyQt6.QtCore import QDir, QStandardPaths, QSize
import os

class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Image Viewer")
        self.setGeometry(100, 100, 800, 600)

        self.initUI()

    def initUI(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QHBoxLayout(self.central_widget)

        # Left panel: Folder tree view
        self.folder_model = QFileSystemModel()
        self.folder_model.setRootPath(QDir.rootPath())
        self.folder_tree_view = QTreeView()
        self.folder_tree_view.setModel(self.folder_model)
        self.folder_tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.folder_tree_view.customContextMenuRequested.connect(self.open_menu)
        self.folder_tree_view.setRootIndex(self.folder_model.index(''))  # Set the root index to root directory


        # # Set default path to user's desktop directory
        desktop_path = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.DesktopLocation)[0]
        # self.folder_model.setRootPath(desktop_path)
        desktop_index = self.folder_model.index(desktop_path)
        self.folder_tree_view.setCurrentIndex(desktop_index)

        self.image_list_widget = QListWidget()
        self.image_list_widget.setViewMode(QListWidget.ViewMode.IconMode)  # Set the view mode to IconMode
        self.image_list_widget.setIconSize(QSize(100, 100))  # Set the icon size to 100x100 pixels
        self.image_list_widget.setWordWrap(True)  # Enable word wrap
        self.image_list_widget.setTextElideMode(Qt.TextElideMode.ElideRight)  # Set text elide mode to elide right
        self.image_list_widget.setUniformItemSizes(True)  # Enable uniform item sizes
        self.image_list_widget.setResizeMode(QListWidget.ResizeMode.Adjust)  # Set resize mode to Adjust
        self.image_list_widget.setSpacing(10)  # Set spacing between items

        # Add widgets to layout
        splitter = QSplitter()
        splitter.addWidget(self.folder_tree_view)
        splitter.addWidget(self.image_list_widget)
        splitter.setStretchFactor(0, 0)  # Prevent the folder view from stretching
        splitter.setStretchFactor(1, 1)  # Allow the image view to stretch
        
        # Set default sizes for the left and right panels
        splitter.setSizes([400, 600])

        self.layout.addWidget(splitter)

    def open_menu(self, position):
        menu = QMenu()
        show_images_action = QAction("Show Images", self)
        show_images_action.triggered.connect(lambda: self.folder_selected(self.folder_tree_view.currentIndex()))
        menu.addAction(show_images_action)
        menu.exec(self.folder_tree_view.viewport().mapToGlobal(position))


    def folder_selected(self, index):
        folder_path = self.folder_model.filePath(index)
        self.load_images(folder_path)

    def load_images(self, folder_path):
        image_files = [file for file in os.listdir(folder_path) if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

        # Clear previous items
        self.image_list_widget.clear()

        # Add image thumbnails
        for image_file in image_files:
            image_path = os.path.join(folder_path, image_file)
            pixmap = QPixmap(image_path).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)  # Adjust the size here
            icon = QIcon(pixmap)
            item = QListWidgetItem(icon, image_file)
            item.setToolTip(image_file)  # Set tooltip to display full file name
            item.setSizeHint(QSize(100, 120))  # Set a fixed size for the items
            item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)  # Center align text
            self.image_list_widget.addItem(item)

        if self.image_list_widget.count() == 0:
            print("No images found in this folder.")
        else:
            print("Images loaded successfully.")

    def image_selected(self, index):
        # Retrieve the selected image and perform any necessary action
        pass

def main():
    app = QApplication(sys.argv)
    window = ImageViewer()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
