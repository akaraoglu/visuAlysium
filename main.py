import os
import sys
from PyQt6.QtCore import pyqtSlot
from PyQt6.QtCore import Qt, QDir, QStandardPaths, QSize, QThread, pyqtSignal, QRunnable, QThreadPool, QObject
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeView, QHBoxLayout, QWidget, QListWidget, QListWidgetItem, QSplitter, QMenu, QMenuBar, QMessageBox
from PyQt6.QtGui import QPixmap, QIcon, QFileSystemModel, QAction
import time


class WorkerSignals(QObject):
    finished = pyqtSignal()
    result = pyqtSignal(object, object)


class Worker(QRunnable):
    def __init__(self, function, *args, **kwargs):
        super().__init__()
        self.function = function
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

    @pyqtSlot()
    def run(self):
        result1, result2   = self.function(*self.args, **self.kwargs)
        self.signals.result.emit(result1, result2 )
        self.signals.finished.emit()

def load_thumbnail(image_path):
    pixmap = QPixmap(image_path).scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    image_file = os.path.basename(image_path)
    icon = QIcon(pixmap)
    return icon, image_file

class ImageLoaderThread(QThread):
    image_loaded = pyqtSignal(QIcon, str)

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path

    def run(self):
        image_files = [file for file in os.listdir(self.folder_path) if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
        
        thread_pool = QThreadPool.globalInstance()
        
        for image_file in image_files:
            image_path = os.path.join(self.folder_path, image_file)
            runnable = Worker(load_thumbnail, image_path)
            runnable.signals.result.connect(self.image_loaded.emit)
            QThreadPool.globalInstance().start(runnable)


class ImageViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Experimental Image Viewer")

        self.initUI()

    def initUI(self):
        # Create a menu bar
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        # Create a "File" menu and add it to the menu bar
        file_menu = QMenu("&File", self)
        menu_bar.addMenu(file_menu)

        # Create actions for the "File" menu
        open_folder_action = QAction("Open Folder", self)
        open_image_action = QAction("Open Image", self)
        about_action = QAction("About", self)

        # Add actions to the "File" menu
        file_menu.addAction(open_folder_action)
        file_menu.addAction(open_image_action)
        file_menu.addAction(about_action)

        # Connect actions to methods
        open_folder_action.triggered.connect(self.open_folder)
        open_image_action.triggered.connect(self.open_image)
        about_action.triggered.connect(self.about)

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
        self.folder_tree_view.setColumnWidth(0, 250)  # Set the width of the "Name" column

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
        self.image_loader_thread = ImageLoaderThread(folder_path)
        self.image_loader_thread.image_loaded.connect(self.add_thumbnail)
        self.image_loader_thread.run()


    # def load_images(self, folder_path):
    #     image_files = [file for file in os.listdir(folder_path) if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    #     thread_pool = QThreadPool.globalInstance()
        
    #     for image_file in image_files:
    #         image_path = os.path.join(folder_path, image_file)
    #         runnable = Worker(load_thumbnail, image_path)
    #         runnable.signals.result.connect(self.add_thumbnail)
    #         QThreadPool.globalInstance().start(runnable)
    #         # thread_pool.start(runnable)
            
    def add_thumbnail(self, icon, image_path):
        # item = QListWidgetItem(QIcon(pixmap), os.path.basename(image_path))
        # self.image_list_widget.addItem(item)
        
        item = QListWidgetItem(icon, image_path)
        item.setToolTip(image_path)  # Set tooltip to display full file name
        item.setSizeHint(QSize(100, 120))  # Set a fixed size for the items
        item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)  # Center align text
        self.image_list_widget.addItem(item)
        
    def image_selected(self, index):
        # Retrieve the selected image and perform any necessary action
        pass

    def open_folder(self):
        # Implement this method to open a folder
        pass

    def open_image(self):
        # Implement this method to open an image
        pass
        
    def about(self):
        # Create a QMessageBox
        msg_box = QMessageBox()
        msg_box.setWindowTitle("About")
        msg_box.setIcon(QMessageBox.Icon.Information)


        # Set text and customize appearance
        msg_box.setText(
            "<p>This is an experimental Python-based image visualizer and editor.</p>"
            "<p>Copyright (c) 2024 VisuAlysium</p>"
            "<p>This program is free software: you can redistribute it and/or modify it under the terms of the "
            "GNU General Public License as published by the Free Software Foundation, either version 3 of the License, "
            "or (at your option) any later version.</p>"
            "<p>This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without "
            "even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General "
            "Public License for more details.</p>"
            "<p>You should have received a copy of the GNU General Public License along with this program. If not, "
            "see <a href='http://www.gnu.org/licenses/'>http://www.gnu.org/licenses/</a>.</p>"
      
        )

        # # Customize appearance
        # msg_box.setStyleSheet("QLabel{min-width: 600px;}")
        
        # Set fixed size
        msg_box.setFixedSize(800, 400)

        # Display the message box
        msg_box.exec()


from PyQt6.QtGui import QPalette, QColor

def main():
    app = QApplication(sys.argv)

    # Set the application style to Fusion
    app.setStyle("Fusion")

    # Create a dark palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Base, QColor(25, 25, 25))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
    palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
    palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
    app.setPalette(palette)

    # Change some style settings
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #2a82da; border: 1px solid white; }")

    window = ImageViewer()
    
    # Get the screen dimensions
    screen_rect = app.primaryScreen().availableGeometry()

    # Calculate the dimensions for the window (50% of screen dimensions)
    window_width = screen_rect.width() * 0.5
    window_height = screen_rect.height() * 0.75

    # Calculate the position for the window to be centered
    window_x = (screen_rect.width() - window_width) / 2
    window_y = (screen_rect.height() - window_height) / 2

    # Set the geometry of the window
    window.setGeometry(int(window_x), int(window_y), int(window_width), int(window_height))

    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()


if __name__ == '__main__':
    main()
