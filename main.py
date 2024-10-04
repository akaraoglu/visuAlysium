
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of VisuAlysium, which is released under the GNU General Public License (GPL).
# See the LICENSE or COPYING file in the root of this project or visit 
# http://www.gnu.org/licenses/gpl-3.0.html for the full text of the license.

"""
VisuAlysium 
=================================================================

This file is the main class for image visualization and editing application. 

(c) Visualysium, 2024

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Ali Karaoglu"
__version__ = "0.0.0"
__date__ = "2024-04-10"

import os
import sys
from PyQt6.QtCore import Qt, QDir, QStandardPaths, QUrl, QTimer
from PyQt6.QtGui import QIcon, QAction, QPalette, QColor, QFileSystemModel, QDesktopServices, QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QTreeView, QHBoxLayout, QWidget, QSplitter, QMenu, QMenuBar, QMessageBox, QFileDialog, QSplashScreen
from src.ImageEditorWindow import ImageViewerWindow
from src.FolderExplorer import FolderExplorer

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VisuAlysium - Image Editor")
        self.initUI()

    def initUI(self):
        self.setup_menus()  # Set up the menus
                
        self.__image_viewer_window = ImageViewerWindow()
        self.__central_widget = QWidget()
        self.setCentralWidget(self.__central_widget)
        self.__layout = QHBoxLayout(self.__central_widget)
        
        self.__default_path = QStandardPaths.standardLocations(QStandardPaths.StandardLocation.HomeLocation)[0]

        self.__image_list_widget = FolderExplorer(self.__default_path)
        self.__image_list_widget.show_image.connect(self.open_image_viewer)
        self.__image_list_widget.path_updated.connect(self.set_folder_tree_view_path)

        # Add widgets to layout
        self.__folder_tree_view = QTreeView()

        splitter = QSplitter()
        splitter.addWidget(self.__folder_tree_view)
        splitter.addWidget(self.__image_list_widget)
        splitter.setStretchFactor(0, 0)  # Prevent the folder view from stretching
        splitter.setStretchFactor(1, 1)  # Allow the image view to stretch
        splitter.setSizes([400, 600])
        self.__layout.addWidget(splitter)

        # Setting the width of the columns do not work if it is set before the splitters added.
        # Uknown issue. 
        self.setup_folder_tree_view()
        
        self.set_theme("dark") # Default Mode

            
    def setup_menus(self):
        # Create a menu bar
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        # Create a "File" menu
        file_menu = QMenu("&File", self)
        open_folder_action = QAction("Open Folder", self)
        open_image_action = QAction("Open Image", self)
        file_menu.addAction(open_folder_action)
        file_menu.addAction(open_image_action)
        open_folder_action.triggered.connect(self.open_folder)
        open_image_action.triggered.connect(self.open_image)
        exit_action = QAction("Exit", self)  # Create the exit action
        file_menu.addSeparator()  # Optionally add a separator before the exit action
        file_menu.addAction(exit_action)
        
        # Create a "Help" menu
        help_menu = QMenu("&Help", self)
        
        help_action = QAction("Help", self)
        license_action = QAction("License Agreement", self)
        homepage_action = QAction("Home Page", self)
        about_action = QAction("About", self)
        
        help_menu.addAction(help_action)
        help_menu.addAction(license_action)
        help_menu.addAction(homepage_action)
        help_menu.addAction(about_action)
        
        help_action.triggered.connect(self.show_help)
        license_action.triggered.connect(self.show_license)
        homepage_action.triggered.connect(self.show_homepage)
        about_action.triggered.connect(self.about)
        
        # Create a "Settings" menu with a "Themes" submenu
        settings_menu = QMenu("&Settings", self)
        
        themes_menu = QMenu("Themes", self)
        settings_menu.addMenu(themes_menu)

        dark_theme_action = QAction("Dark", self)
        gray_theme_action = QAction("Gray", self)
        light_theme_action = QAction("Light", self)

        themes_menu.addAction(dark_theme_action)
        themes_menu.addAction(gray_theme_action)
        themes_menu.addAction(light_theme_action)
        
        dark_theme_action.triggered.connect(lambda: self.set_theme("dark"))
        gray_theme_action.triggered.connect(lambda: self.set_theme("gray"))
        light_theme_action.triggered.connect(lambda: self.set_theme("light"))
        exit_action.triggered.connect(self.exit_application)  # Connect the exit action to its handler
        
        # Add tje file menus in order.
        menu_bar.addMenu(file_menu)
        menu_bar.addMenu(settings_menu)
        menu_bar.addMenu(help_menu)


    def set_theme(self, theme_name):
        palette = QPalette()
        if theme_name == "dark":
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
        elif theme_name == "gray":
            palette.setColor(QPalette.ColorRole.Window, QColor(189, 189, 189))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.Base, QColor(125, 125, 125))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(150, 150, 150))
            palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.Button, QColor(53, 53, 53))
            palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)

        elif theme_name == "light":
            palette.setColor(QPalette.ColorRole.Window, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.Base, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.AlternateBase, QColor(255, 255, 255))
            palette.setColor(QPalette.ColorRole.ToolTipBase, Qt.GlobalColor.white)
            palette.setColor(QPalette.ColorRole.ToolTipText, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.Button, QColor(240, 240, 240))
            palette.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.black)
            palette.setColor(QPalette.ColorRole.BrightText, Qt.GlobalColor.red)
            palette.setColor(QPalette.ColorRole.Link, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
            palette.setColor(QPalette.ColorRole.HighlightedText, Qt.GlobalColor.black)
        
        QApplication.instance().setPalette(palette)
        
        if hasattr(self, '_MainWindow__image_list_widget'):
            self.__image_list_widget.update_colors()  # Assuming you've added this method to FolderExplorer
        self.update()  # Ensure the main window and all its children are repainted


    def show_help(self):
        QMessageBox.information(self, "Help", "This section will provide help and FAQs related to the application.")


    def show_license(self):
        # Create a QMessageBox
        msg_box = QMessageBox()
        msg_box.setWindowTitle("License Agreement")
        msg_box.setIcon(QMessageBox.Icon.Information)

        # Set text and customize appearance
        msg_box.setText(
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

    def show_homepage(self):
        QDesktopServices.openUrl(QUrl("https://github.com/akaraoglu/visuAlysium"))  # Replace with your actual URL

    def about(self):
        msg_box = QMessageBox()
        msg_box.setWindowTitle("About")
        msg_box.setIcon(QMessageBox.Icon.Information)
        msg_box.setText(
            "<h2>VisuAlysium - Image Editor</h2>"
            "<p>This application is an <strong>experimental image visualizer and editor</strong> designed to demonstrate "
            "the capabilities of Python with PyQt. It serves as a foundation that can be expanded or customized for various "
            "purposes, including educational tools, professional image editing, or as a base for more specialized graphical "
            "applications.</p>"
            "<p>As an open-source project, it encourages community involvement and contributions to evolve its features "
            "and capabilities. Users and developers are invited to adapt the software to their specific needs or to contribute "
            "to its development.</p>"
        )
        msg_box.setDetailedText(
            "Copyright (c) 2024 VisuAlysium\n"
            "This program is distributed under the terms of the GNU General Public License (GPL), which permits "
            "redistribution and modification under certain conditions. This promotes software freedom and collaboration, "
            "making it a valuable tool for community-driven development."
        )
        msg_box.setFixedSize(500, 300)
        msg_box.exec()

    def setup_folder_tree_view(self):
        # Left panel: Folder tree view
        self.__folder_model = QFileSystemModel()
        self.__folder_model.setRootPath(QDir.rootPath())
        self.__folder_tree_view.setModel(self.__folder_model)
        self.__folder_tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.__folder_tree_view.customContextMenuRequested.connect(self.open_menu)
        self.__folder_tree_view.setRootIndex(self.__folder_model.index(''))  # Set the root index to root directory
        self.__folder_tree_view.clicked.connect(self.folder_selected)
        default_index = self.__folder_model.index(self.__default_path)
        self.__folder_tree_view.setCurrentIndex(default_index)
        self.__folder_tree_view.setColumnWidth(0, 250)  # Set the width of the "Name" column

    def set_folder_tree_view_path(self, new_path):
        default_index = self.__folder_model.index(new_path)
        self.__folder_tree_view.setCurrentIndex(default_index)
    
    def open_image_menu(self, position):
        menu = QMenu()
        open_image_action = QAction("Show Image", self)
        open_image_action.triggered.connect(lambda: self.image_double_clicked(self.__image_list_widget.currentItem()))
        menu.addAction(open_image_action)
        menu.exec(self.__image_list_widget.viewport().mapToGlobal(position))
        
    def open_menu(self, position):
        menu = QMenu()
        show_images_action = QAction("Show Images", self)
        show_images_action.triggered.connect(lambda: self.folder_selected(self.__folder_tree_view.currentIndex()))
        menu.addAction(show_images_action)
        menu.exec(self.__folder_tree_view.viewport().mapToGlobal(position))

    def folder_selected(self, index):
        folder_path = self.__folder_model.filePath(index)
        self.load_images(folder_path)

    def load_images(self, folder_path):
        self.__image_list_widget.update_root_path(folder_path)

    def image_double_clicked(self, item):
        image_path = item.toolTip()
        self.__image_viewer_window.show()
        self.__image_viewer_window.show_new_image(image_path)

    def open_image_viewer(self, image_path):
        self.__image_viewer_window.show()
        self.__image_viewer_window.show_new_image(image_path)

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder_path:
            self.load_images(folder_path)

    def open_image(self):
        file_dialog = QFileDialog()
        image_path, _ = file_dialog.getOpenFileName(self, "Open Image", QDir.homePath(), "Image Files (*.png *.jpg *.jpeg *.bmp *.gif)")
        if image_path:
            self.open_image_viewer(image_path)

    def exit_application(self):
        reply = QMessageBox.question(self, 'Exit Confirmation', 
                                    'Are you sure you want to exit?', 
                                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                                    QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            QApplication.instance().quit()  # Exit the application
                
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
           self.exit_application()

        super().keyPressEvent(event)  # Continue processing other key events

def main():
    
    # This bit gets the taskbar icon working properly in Windows
    if sys.platform.startswith('win'):
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(u'Visualysium.ExImaVi.ImageVisualizer.0.01') # Arbitrary string

    app = QApplication(sys.argv)
    
    # Set the application style to Fusion
    # ['Breeze', 'Oxygen', 'QtCurve', 'Windows', 'Fusion']
    app.setStyle("Fusion")
    
    
    # Prepare the splash screen
    splash_pix = QPixmap("icons/main_logo_black.png").scaled(600,600, aspectRatioMode=Qt.AspectRatioMode.KeepAspectRatio, transformMode=Qt.TransformationMode.SmoothTransformation)  # Ensure this path points to an actual image file
    splash = QSplashScreen(splash_pix)
    splash.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
    splash.setEnabled(False)  # Disable interactions
    splash.show()
    app.processEvents()  # Process any pending events to ensure the splash displays immediately

    window = MainWindow()
    
    # Set a timer to wait for 2 seconds before showing the main window
    QTimer.singleShot(2000, lambda: (window.show(), splash.finish(window)))

    ################################
    # Set the geometry of the window
    # Get the screen dimensions
    screen_rect = app.primaryScreen().availableGeometry()
    # Calculate the dimensions for the window (50% of screen dimensions)
    window_width = screen_rect.width() * 0.5
    window_height = screen_rect.height() * 0.75
    # Calculate the position for the window to be centered
    window_x = (screen_rect.width() - window_width) / 2
    window_y = (screen_rect.height() - window_height) / 2
    window.setGeometry(int(window_x), int(window_y), int(window_width), int(window_height))
    ####################
    window.show()
    icon_path = "icons/main_icon.png"
    app_icon = QIcon(icon_path)
    app.setWindowIcon(app_icon)
    app.setApplicationName("VisuAlysium")
    app.setApplicationDisplayName("VisuAlysium")
    

    sys.exit(app.exec())

if __name__ == '__main__':
    main()
