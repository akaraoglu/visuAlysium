
import os
import sys
from PyQt6.QtCore import Qt, QModelIndex, QDir, QSize, pyqtSignal, pyqtSlot, QThread
from PyQt6.QtGui import QPixmap, QFont, QIcon, QPalette, QFileSystemModel
from PyQt6.QtWidgets import QApplication, QPushButton, QVBoxLayout, QLineEdit, QHBoxLayout, QWidget,QListView

from src.ImageProcessingAlgorithms import supported_extensions
from src.util.FileSystemModelImagesOnly import FileSystemModelImagesOnly
# supported_extensions_list = [ext.replace('*.', '') for ext in raw_extensions]


class FolderExplorer(QWidget):
    show_image = pyqtSignal(str)
    path_updated = pyqtSignal(str)

    def __init__(self, dir_path):
        super().__init__()
        
        self.__grid_size = QSize(140, 140)  # Initial grid size

        self.__path = dir_path
        self.__files = FileSystemModelImagesOnly()
        self.__files.setRootPath(self.__path)

        self.__view = QListView()
        self.__view.setModel(self.__files)
        self.__view.setRootIndex(self.__files.index(dir_path))
        self.__view.setViewMode(QListView.ViewMode.IconMode)
        self.__view.setIconSize(QSize(140, 120))  # Icon size without text
        self.__view.setGridSize(self.__grid_size)
        self.__view.setUniformItemSizes(True)
        self.__view.setWordWrap(True)
        self.__view.setStyleSheet("""
            QListView::item {
                border: 1px solid #505050;  /* Gray border for each item */
                border-radius: 5px;         /* Rounded corners */
                padding: 3px;
                margin: 4px;
                text-align: center;
            }
            QListView::item:selected {
                background: #a0a0ff;        /* Light blue background for selected items */
                color: black;
            }
            """)
        self.__view.setFont(QFont('Arial', 10))
        self.__view.setSpacing(10)

        # Disable drag-and-drop
        # self.__view.setDragEnabled(False)
        self.__view.setAcceptDrops(False)
        # self.__view.setDropIndicatorShown(False)

        # Create a QLineEdit to display and edit the current path
        self.__path_line_edit = QLineEdit(self.__path)
        self.__path_line_edit.setReadOnly(False)  # Set to True if you don't want it to be editable
        self.__path_line_edit.returnPressed.connect(self.update_path_from_line_edit)

        # Create UP button
        self.__up_button = QPushButton()
        self.__up_button.setIcon(QIcon('icons/undo.png'))  # Ensure you have an 'up_arrow.png' in your resources
        self.__up_button.clicked.connect(self.navigate_up)

        # Layout for the path editor and the UP button
        self.__path_layout = QHBoxLayout()
        self.__path_layout.addWidget(self.__up_button)
        self.__path_layout.addWidget(self.__path_line_edit)

        # Main layout
        layout = QVBoxLayout()
        layout.addLayout(self.__path_layout)  # Add the QHBoxLayout containing the UP button and QLineEdit
        layout.addWidget(self.__view)

        self.setLayout(layout)

        self.__view.doubleClicked.connect(self.on_double_clicked)

    def update_colors(self):
        print("Setting palette")
        palette = QApplication.instance().palette()
        self.setStyleSheet(f"background-color: {palette.color(QPalette.ColorRole.Base).name()};")
        # Add more style changes as needed based on the widget's components

    def navigate_up(self):
        # Navigate up one directory level
        current_directory = QDir(self.__path)
        if current_directory.cdUp():
            new_path = current_directory.path()
            self.update_root_path(new_path)

    def update_path_from_line_edit(self):
        # Update the root path based on the text in QLineEdit
        new_path = self.__path_line_edit.text()
        if os.path.isdir(new_path):
            self.update_root_path(new_path)
        else:
            self.__path_line_edit.setText(self.__path)  # Reset to the current valid path if the new path is not valid
        
    def resizeEvent(self, event):
        # Calculate the number of columns based on the widget's current width
        num_columns = max(1, self.width() // self.__grid_size.width())  # Ensure at least one column
        self.update_columns(num_columns)
        super().resizeEvent(event)  # Don't forget to call the base class method

    def update_columns(self, num_columns):
        # Adjust the grid size based on the number of columns
        new_width:int = self.__grid_size.height() 
        new_grid_size = QSize(new_width, self.__grid_size.height())
        self.__view.setGridSize(new_grid_size)
        self.__view.setIconSize(QSize(new_width - 10, 140))  # Adjust icon size if necessary

    def update_root_path(self, new_path):
        """Update the view to show files from a new directory."""
        self.__path = new_path
        self.__path_line_edit.setText(self.__path)
        self.__files.setRootPath(self.__path)
        self.__view.setRootIndex(self.__files.index(self.__path))
        self.__view.scrollToTop()  # Ensures the view starts at the top of the new directory
        self.path_updated.emit(self.__path)

    def on_double_clicked(self, index: QModelIndex):
        if not index.isValid():
            return

        # Get the file path from the model
        file_path = self.__files.filePath(index)

        if os.path.isdir(file_path):
            # If it's a directory, update the view to show the contents of this directory
            self.update_root_path(file_path)

        else:
            self.open_image_viewer(file_path)

    def open_image_viewer(self, file_path):
        self.show_image.emit(file_path)    
    
    def keyPressEvent(self, event):
        print("keyPressEvent : ", event.key())

        if event.key() == Qt.Key.Key_Return:
            index = self.__view.currentIndex()

            if not index.isValid():
                return

            # Get the file path from the model
            file_path = self.__files.filePath(index)

            if os.path.isdir(file_path):
                # If it's a directory, update the view to show the contents of this directory
                self.update_root_path(file_path)

            elif file_path.endswith(tuple(supported_extensions)):  # Check if it's an image
                # Optionally do something specific for image files, like opening in an image viewer
                self.open_image_viewer(file_path)

        super().keyPressEvent(event)