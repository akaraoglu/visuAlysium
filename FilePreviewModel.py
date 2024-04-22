import sys, math
import os
import sys
from PyQt6.QtCore import Qt, QModelIndex, QDir, QStandardPaths, QSize, QThreadPool, QRunnable, QObject, pyqtSignal, pyqtSlot, QThread
from PyQt6.QtGui import QPixmap, QFont, QIcon, QAction, QPalette, QColor, QFileSystemModel, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QTreeView, QVBoxLayout, QLineEdit, QHBoxLayout, QWidget, QListWidget, QListView, QListWidgetItem, QSplitter, QMenu, QMenuBar, QMessageBox, QFileDialog
from ImageEditorWindow import ImageViewerWindow
import numpy as np
supported_extensions = ['*.jpg', '*.jpeg', '*.png', '*.gif', '*.bmp', '*.dng']
supported_extensions_list = [ext.replace('*.', '') for ext in supported_extensions]

class FileSystemModelImagesOnly(QFileSystemModel):
    def __init__(self, cacheWidth=100, cacheHeight=100):
        super().__init__()
        self.previews = {'None': None}
        self.cacheWidth = cacheWidth
        self.cacheHeight = cacheHeight
        self.ncols = 2
        
        # Specify the types of files to show
        self.setNameFilters(supported_extensions)
        self.setNameFilterDisables(False)  # Hide files that are not images

        # Include only directories and the specified files
        # Include directories and files but exclude '.' and '..'
        self.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot) 

    def getPreview(self, index):
        itemName = super().data(index, Qt.ItemDataRole.DisplayRole)

        if itemName not in self.previews:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)  # Set cursor to waiting

            qpm = QPixmap(self.rootPath() + "/" + itemName)

            if qpm is None or qpm.isNull():
                qpm = super().data(index, Qt.ItemDataRole.DecorationRole)
                if qpm and not qpm.isNull():
                    qpm = qpm.pixmap(self.cacheWidth, self.cacheHeight)
            if qpm and not qpm.isNull():
                qpm = qpm.scaled(self.cacheWidth, self.cacheHeight, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

            self.previews[itemName] = qpm
            QApplication.restoreOverrideCursor()  # Restore the cursor

        return self.previews[itemName]

    def data(self, index, role):
        if role == Qt.ItemDataRole.DecorationRole:
            return self.getPreview(index)
        elif role == Qt.ItemDataRole.ToolTipRole:
            # Return the filename as tooltip
            return self.filePath(index)
        else:
            return super().data(index, role)

class FolderExplorer(QWidget):
    show_image = pyqtSignal(str)
    path_updated = pyqtSignal(str)

    def __init__(self, dir_path):
        super().__init__()
        
        self.gridSize = QSize(140, 140)  # Initial grid size

        self.path = dir_path
        self.files = FileSystemModelImagesOnly()
        self.files.setRootPath(self.path)

        self.view = QListView()
        self.view.setModel(self.files)
        self.view.setRootIndex(self.files.index(dir_path))
        self.view.setViewMode(QListView.ViewMode.IconMode)
        self.view.setIconSize(QSize(140, 120))  # Icon size without text
        self.view.setGridSize(self.gridSize)
        self.view.setUniformItemSizes(True)
        self.view.setWordWrap(True)
        self.view.setStyleSheet("""
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
        self.view.setFont(QFont('Arial', 10))
        self.view.setSpacing(10)

        # Disable drag-and-drop
        # self.view.setDragEnabled(False)
        self.view.setAcceptDrops(False)
        # self.view.setDropIndicatorShown(False)

        # Create a QLineEdit to display and edit the current path
        self.pathLineEdit = QLineEdit(self.path)
        self.pathLineEdit.setReadOnly(False)  # Set to True if you don't want it to be editable
        self.pathLineEdit.returnPressed.connect(self.update_path_from_line_edit)

        # Create UP button
        self.upButton = QPushButton()
        self.upButton.setIcon(QIcon('icons/undo.png'))  # Ensure you have an 'up_arrow.png' in your resources
        self.upButton.clicked.connect(self.navigate_up)

        # Layout for the path editor and the UP button
        pathLayout = QHBoxLayout()
        pathLayout.addWidget(self.upButton)
        pathLayout.addWidget(self.pathLineEdit)

        # Main layout
        layout = QVBoxLayout()
        layout.addLayout(pathLayout)  # Add the QHBoxLayout containing the UP button and QLineEdit
        layout.addWidget(self.view)

        self.setLayout(layout)

        self.view.doubleClicked.connect(self.on_double_clicked)
    
    def navigate_up(self):
        # Navigate up one directory level
        current_directory = QDir(self.path)
        if current_directory.cdUp():
            new_path = current_directory.path()
            self.update_root_path(new_path)

    def update_path_from_line_edit(self):
        # Update the root path based on the text in QLineEdit
        new_path = self.pathLineEdit.text()
        if os.path.isdir(new_path):
            self.update_root_path(new_path)
        else:
            self.pathLineEdit.setText(self.path)  # Reset to the current valid path if the new path is not valid
        
    def resizeEvent(self, event):
        # Calculate the number of columns based on the widget's current width
        num_columns = max(1, self.width() // self.gridSize.width())  # Ensure at least one column
        self.update_columns(num_columns)
        super().resizeEvent(event)  # Don't forget to call the base class method

    def update_columns(self, num_columns):
        # Adjust the grid size based on the number of columns
        new_width = self.gridSize.height() # self.width() // num_columns
        new_grid_size = QSize(new_width, self.gridSize.height())
        self.view.setGridSize(new_grid_size)
        self.view.setIconSize(QSize(new_width - 10, 140))  # Adjust icon size if necessary

    def update_root_path(self, new_path):
        """Update the view to show files from a new directory."""
        self.path = new_path
        self.pathLineEdit.setText(self.path)
        self.files.setRootPath(self.path)
        self.view.setRootIndex(self.files.index(self.path))
        self.view.scrollToTop()  # Ensures the view starts at the top of the new directory
        self.path_updated.emit(self.path)

    def on_double_clicked(self, index: QModelIndex):
        if not index.isValid():
            return

        # Get the file path from the model
        file_path = self.files.filePath(index)

        if os.path.isdir(file_path):
            # If it's a directory, update the view to show the contents of this directory
            self.update_root_path(file_path)

        elif file_path.endswith(tuple(supported_extensions_list)):  # Check if it's an image
            # Optionally do something specific for image files, like opening in an image viewer
            self.open_image_viewer(file_path)

    def open_image_viewer(self, file_path):
        self.show_image.emit(file_path)
        
        