import os
import sys
from PyQt6.QtCore import Qt, QDir, QStandardPaths, QSize, QThreadPool, QRunnable, QObject, pyqtSignal, pyqtSlot, QThread
from PyQt6.QtGui import QPixmap, QIcon, QAction, QPalette, QColor, QFileSystemModel, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeView, QHBoxLayout, QWidget, QListWidget, QListView, QListWidgetItem, QSplitter, QMenu, QMenuBar, QMessageBox, QFileDialog
from ImageEditorWindow import ImageViewerWindow
from FilePreviewModel import FolderExplorer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VisuAlysium - Image Editor")
        self.initUI()

    def initUI(self):
        # Create a menu bar
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        # Create a "File" menu and add it to the menu bar
        file_menu = QMenu("&File", self)
        menu_bar.addMenu(file_menu)

        self.image_viewer = ImageViewerWindow()

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
        self.folder_tree_view.clicked.connect(self.folder_selected)

        default_path = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.HomeLocation)[0]
        default_index = self.folder_model.index(default_path)
        self.folder_tree_view.setCurrentIndex(default_index)

        self.image_list_widget = FolderExplorer(default_path)
        self.image_list_widget.show_image.connect(self.open_image_viewer)
        self.image_list_widget.path_updated.connect(self.set_folder_tree_view_path)

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
    
    def set_folder_tree_view_path(self, new_path):
        default_index = self.folder_model.index(new_path)
        self.folder_tree_view.setCurrentIndex(default_index)
    
    def open_image_menu(self, position):
        menu = QMenu()
        open_image_action = QAction("Show Image", self)
        open_image_action.triggered.connect(lambda: self.image_double_clicked(self.image_list_widget.currentItem()))
        menu.addAction(open_image_action)
        menu.exec(self.image_list_widget.viewport().mapToGlobal(position))
        
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
        self.image_list_widget.update_root_path(folder_path)

    def image_double_clicked(self, item):
        image_path = item.toolTip()
        self.image_viewer.show()
        self.image_viewer.show_new_image(image_path)

    def open_image_viewer(self, image_path):
        self.image_viewer.show()
        self.image_viewer.show_new_image(image_path)

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.load_images(folder_path)

    def open_image(self):
        file_dialog = QFileDialog()
        image_path, _ = file_dialog.getOpenFileName(self, "Open Image", QDir.homePath(), "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)")
        if image_path:
            self.open_image_viewer(image_path)

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

        # Set fixed size
        msg_box.setFixedSize(800, 400)

        # Display the message box
        msg_box.exec()


from PyQt6.QtGui import QPalette, QColor

def main():
    
    # This bit gets the taskbar icon working properly in Windows
    if sys.platform.startswith('win'):
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u'Visualysium.ExImaVi.ImageVisualizer.0.01') # Arbitrary string

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
        # Set application icon

    window = MainWindow()

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
    icon_path = "icons/main_icon.png"
    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)
    app.setApplicationName("VisuAlysium")
    app.setApplicationDisplayName("VisuAlysium")
    

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
