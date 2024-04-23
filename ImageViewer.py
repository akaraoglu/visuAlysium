
import numpy as np
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas


from PyQt6.QtGui import QWheelEvent
from PyQt6.QtCore import pyqtSlot,pyqtSignal, Qt, QSize, QPoint, QRect, QRectF, QPointF, QSizeF
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QSpacerItem, QSizePolicy, QVBoxLayout,QHBoxLayout,QComboBox, QPushButton, QGraphicsRectItem, QFileDialog, QMenu, QGraphicsProxyWidget, QRubberBand, QLabel, QWidget
from PyQt6.QtGui import QPixmap, QCursor, QAction, QPen, QImage, QPainterPath, QTransform, QColor, QFont, QBrush

from WidgetUtils import HoverButton
import ImageProcessingAlgorithms


class CustomInfoPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)  # Pass the parent to the superclass initializer
        self.setup_ui()
        
        # Add a border to the widget
        # self.setStyleSheet("QWidget { border: 1px solid black; }")
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.GlobalColor.red)
        self.setPalette(p)
        # self.setStyleSheet("background-color: rgba(125, 125, 125, 0.3); border: 1px ; border-radius: 10px; color: white;")
        
    def setup_ui(self):
        # Use QVBoxLayout to layout the labels and histogram vertically
        layout = QVBoxLayout()
        
        # Set the layout for the widget
        self.setLayout(layout)

        # Create a consistent font size for all labels
        label_font = QFont("Arial", 10)

        # Helper function to create a label with right alignment
        def create_label(text):
            label = QLabel(text)

            label.setFont(label_font)
            label.setFixedSize(QSize(100,20))
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            return label

        labels_and_info_layout = QHBoxLayout()

        labels_layout = QVBoxLayout()
        # Add the labels for file attributes
        file_name_label = create_label (" File Name: ")
        location_label = create_label  ("  Location: ")
        type_label = create_label      ("      Type: ")
        size_label = create_label      ("      Size: ")
        date_time_label = create_label (" Date Time: ")
        attributes_label = create_label("Resolution: ")
        dpi_label = create_label       (" Bit depth: ")
        # Add labels to the layout
        labels = [
            file_name_label, location_label, type_label,
            size_label, date_time_label, attributes_label,
            dpi_label
        ]
        for label in labels:
            labels_layout.addWidget(label)

        info_layout = QVBoxLayout()
        # Add the labels for file attributes
        info_file_name_label = create_label (" ")
        info_location_label = create_label  (" ")
        info_type_label = create_label      (" ")
        info_size_label = create_label      (" ")
        info_date_time_label = create_label (" ")
        info_attributes_label = create_label(" ")
        info_dpi_label = create_label       (" ")
        # Add labels to the layout
        self.info_labels = [
            info_file_name_label, info_location_label, info_type_label,
            info_size_label, info_date_time_label, info_attributes_label,
            info_dpi_label
        ]
        for label in self.info_labels:
            label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            label.setFixedSize(QSize(400,20))
            info_layout.addWidget(label)

        labels_and_info_layout.addLayout(labels_layout)
        labels_and_info_layout.addLayout(info_layout)
        layout.addLayout(labels_and_info_layout)

        # Placeholder for histogram
        self.histogram_display = QLabel()
        layout.addWidget(self.histogram_display)

            
        # Combo box and button for histogram controls
        histogram_controls_layout = QHBoxLayout()

        # Add a spacer item to push the combo box to the right
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        

        # Combo box for selecting the channel
        self.channel_combo_box = QComboBox()
        self.channel_combo_box.setMinimumSize(100, 10)

        
        self.channel_combo_box.addItems(["Luminance", "Red", "Green", "Blue"])
        histogram_controls_layout.addWidget(self.channel_combo_box)
        histogram_controls_layout.addItem(spacer)

        layout.addLayout(histogram_controls_layout)

    def update_info(self, info_dict):
        for i,info in enumerate(info_dict):
            print(info)
            self.info_labels[i].setText(info)

    def update_histogram(self, pixmap):
        scaled_pixmap = pixmap.scaled(self.histogram_display.width(), self.histogram_display.height())
        self.histogram_display.setPixmap(scaled_pixmap)

            
class ImageViewer(QGraphicsView):
    crop_rectangle_changed = pyqtSignal(QRectF)

    def __init__(self):
        super().__init__()

        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.zoomX = 1              # zoom factor w.r.t size of qlabel_image
        self.position = [0, 0]      # position of top left corner of qimage_label w.r.t. qimage_scaled
        
        # Flags for active zooming/panning.
        self._isZooming = False
        self._isPanning = False        # to enable or disable pan
        self.pixmap_item = None
        
        # Store temporary position in screen pixels or scene units.
        self._pixelPosition = QPoint()
        self._scenePosition = QPointF()
        self._crop_mode = False

        self.button_size = 60
        self.icon_size = 40
        
        self.current_pixmap = None
        self.previous_pixmap = None
        self.original_pixmap = None

        self.cropRect = QGraphicsRectItem()
        self.cropRect.setPen(QPen(QColor('red'), 2, Qt.PenStyle.SolidLine))
         
        # # Add buttons
        self.button_list = []

        button_fit_screen = self.create_new_button(icon="icons/fullscreen.png", connect_to=self.show_image_fit_to_screen)
        button_original_size = self.create_new_button(icon="icons/original_size.png", connect_to=self.show_image_in_original_size)
        button_zoom_in = self.create_new_button(icon="icons/zoom-in.png", connect_to=self.zoom_in)
        button_zoom_out = self.create_new_button(icon="icons/zoom-out.png", connect_to=self.zoom_out)

        self.button_list = [button_fit_screen, button_original_size, button_zoom_in, button_zoom_out]

        self.createContextMenu()
        self.aspectRatioMode = Qt.AspectRatioMode.KeepAspectRatio
        self.regionZoomKey = Qt.Key.Key_Control  # Drag a zoom box.
        self.regionZoomKeyPressed = False

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setInteractive(True)

        self.rubber_band = None
        self.rect_start_point = None

        self.image_path = ""
        self.info_display_visible = True
        self.info_widget = CustomInfoPanel(self)
        self.info_label_proxy = QGraphicsProxyWidget()
        self.info_label_proxy.setWidget(self.info_widget)
        self.info_widget.setGeometry(10, 10, 400, 400)
        self.scene.addItem(self.info_label_proxy)

        self.init_info_display()
        
        self.curve_option = "Luminance" #default
        self.info_widget.channel_combo_box.currentTextChanged.connect(self.channel_option_selected)
    
    def init_info_display(self):
        if self.info_display_visible == True:
            # self.info_label_proxy.setVisible(True)
            self.info_widget.setVisible(True)
        else:
            # self.info_label_proxy.setVisible(False)
            self.info_widget.setVisible(False)

    def toggle_info_display(self):
        # self.show_pixmap(self.get_current_pixmap())
        if self.info_display_visible == False:
            self.info_display_visible = True
        else:
            self.info_display_visible = False
        self.init_info_display()
        # self.update_image_info()
        
        print("Showing histogram: ", self.info_display_visible)

    def createContextMenu(self):
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        self.contextMenu = QMenu(self)
        self.copyAction = QAction("Copy Image", self)
        self.copyAction.triggered.connect(self.copyImage)
        self.pasteAction = QAction("Paste Image", self)
        self.pasteAction.triggered.connect(self.pasteImage)
        self.saveAction = QAction("Save Image", self)
        self.saveAction.triggered.connect(self.saveImage)

        self.contextMenu.addAction(self.copyAction)
        self.contextMenu.addAction(self.pasteAction)
        self.contextMenu.addAction(self.saveAction)
        
    def keyPressEvent(self, event):
        print(f"Image Viewer Key pressed: {event.key()}")
        super().keyPressEvent(event)
    
    def toggle_zoom_mode(self):
        if self.transform().m11() == 1.0:  # If the current zoom is 100% (original size)
            self.show_image_fit_to_screen()
        else:
            self.show_image_in_original_size()

    def set_zoom(self, factor):
        self.resetTransform()  # Reset any existing transformations
        self.scale(factor, factor)  # Apply the new zoom factor


    def create_new_button(self, icon, connect_to):
        new_button = HoverButton(self, icon=icon, button_size=self.button_size, icon_size=self.icon_size)
        new_button.clicked.connect(connect_to)  # Connect button click to originalSize method

        # Add the buttons to the scene
        self.new_button_proxy = QGraphicsProxyWidget()
        self.new_button_proxy.setWidget(new_button)
        self.scene.addItem(self.new_button_proxy)
        return new_button
    
    def channel_option_selected(self, option):
        print(f"Selected curve option: {option}")
        self.curve_option = option
        self.update_image_info()
        # Implement functionality based on selected option

    def update_image_info(self):
        if self.info_display_visible == True:
            # Update the display with new information
            if self.current_pixmap:
                if self.image_path != "":
                    # Getting file properties
                    file_info = os.stat(self.image_path)
                    file_size = file_info.st_size / 1024  # Size in KB
                    modification_time = datetime.fromtimestamp(file_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

                    # Getting image properties
                    image = QImage(self.image_path)  # Using QImage to get bit depth
                    bit_depth = image.depth()

                    # Preparing info text
                    info_list = [
                        f"{os.path.basename(self.image_path)}",
                        f"{os.path.dirname(self.image_path)}",
                        f"{self.image_path.split('.')[-1].upper()}",
                        f"{file_size:.2f} KB",
                        f"{modification_time}",
                        f"{self.current_pixmap.width()}x{self.current_pixmap.height()}",
                        f"{bit_depth} bits" ]

                    # self.info_label.setText(info_text)
                    self.info_widget.update_info(info_list)

                # Calculate histogram for luminance
                option = self.curve_option
                image = self.convert_pixmap_to_opencv_image(self.get_current_pixmap())
                hist = ImageProcessingAlgorithms.calculate_histogram(image, option)

                # Plot histogram
                fig, ax = plt.subplots(figsize=(4, 2))
                fig.patch.set_alpha(0)  # Set the figure background to transparent
                ax.patch.set_alpha(0)  # Set the axes background to transparent
                ax.plot(hist, color='gray')
                # ax.set_title('Histogram for Luminance')
                # ax.set_xlabel('Bins')
                # ax.set_ylabel('# of Pixels')
                # Hide Y-axis
                ax.yaxis.set_visible(False)
                # Convert to QPixmap and display in QLabel
                qimage = ImageProcessingAlgorithms.plot_to_qimage(fig)
                
                self.info_widget.update_histogram(QPixmap.fromImage(qimage))

                # Clear the figure to release memory
                plt.close(fig)

    def set_crop_mode(self, enabled):
        self._crop_mode = enabled
        self.setCursor(Qt.CursorShape.CrossCursor)

    def reset_rect(self):
        if self.cropRect is not None:
            self.scene.removeItem(self.cropRect)
            self.cropRect.setRect(self.pixmap_item.sceneBoundingRect())
            if self.update_rect():
                self.crop_rectangle_changed.emit(self.get_current_crop_rect())

    def showContextMenu(self, pos):
        self.contextMenu.exec(QCursor.pos())

    def copyImage(self):
        if self.pixmap_item is not None:
            # Copy the pixmap
            QApplication.clipboard().setPixmap(self.pixmap_item.pixmap())

    def pasteImage(self):
        # Get the pixmap from clipboard if available and add it to the scene
        clipboard = QApplication.clipboard()
        if clipboard.mimeData().hasImage():
            pixmap = clipboard.pixmap()
            self.show_pixmap(pixmap)

    def saveImage(self):
        if self.pixmap_item is not None:
            filename, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Images (*.png *.jpg *.bmp)")
            if filename:
                self.pixmap_item.pixmap().save(filename)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        number_of_buttons = len(self.button_list)
        bottom_center = int(self.width() / 2)
        dis_bet_buttons = 5
        height_needed = self.button_size + 15 # distance from lower boundry
        width_needed  = (self.button_size * number_of_buttons) + (dis_bet_buttons*(number_of_buttons-1)) #  distance between the buttons

        y = self.height() - height_needed

        for i,button in enumerate(self.button_list):

            x = bottom_center - int(width_needed/2 - (self.button_size*i) - (dis_bet_buttons*i))
            # Position the buttons at the bottom center
            button.setGeometry(x, y, self.button_size, self.button_size)
    
    def show_image_initial_size(self):
        pixmapSize = self.pixmap_item.sceneBoundingRect().size()
        viewSize = self.size()

        if (pixmapSize.width() <= viewSize.width()) and (pixmapSize.height() <= viewSize.height()):
            self.show_image_in_original_size()
        else: 
            self.show_image_fit_to_screen()

    def show_image_fit_to_screen(self):
        # Implement fit to screen functionality
        if self.pixmap_item is not None:
            self.fitInView(self.pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
        print("Fit to screen.")
            
    def show_image_in_original_size(self):
        # Implement original size functionality
        if self.pixmap_item is not None:
            original_size = self.pixmap_item.pixmap().size()
            if not original_size.isEmpty():
                self.resetTransform()  # Reset any previous transformation
                scene_rect = self.pixmap_item.sceneBoundingRect()
                width_ratio = scene_rect.width() / original_size.width()
                height_ratio = scene_rect.height() / original_size.height()
                self.scale(1 / width_ratio, 1 / height_ratio)
        print("Original size.")
    
    def show_pixmap(self, new_pixmap):
        if not new_pixmap.isNull():
            # Assign new_pixmap to current_pixmap if current_pixmap is None
            if self.current_pixmap is None:
                self.current_pixmap = new_pixmap

            # Fix: Assign new_pixmap to original_pixmap if original_pixmap is None
            if self.original_pixmap is None:
                self.original_pixmap = new_pixmap

            self.previous_pixmap = self.current_pixmap
            self.current_pixmap = new_pixmap

            if self.pixmap_item:
                print("Line 178: self.scene.removeItem(self.pixmap_item)")
                self.scene.removeItem(self.pixmap_item)
            
            self.pixmap_item = QGraphicsPixmapItem(self.current_pixmap)
            self.setSceneRect(QRectF(self.current_pixmap.rect()))  # Set scene size to image size
            self.scene.addItem(self.pixmap_item)            
            # self.zoom_in()

        # show the rectangle over the image.
        if self.cropRect is not None:
            self.reset_rect()
            self.scene.removeItem(self.cropRect)
            # self.cropRect = QGraphicsRectItem()
            # self.cropRect.setPen(QPen(QColor('red'), 2, Qt.PenStyle.SolidLine))
            if self._crop_mode:
                self.scene.addItem(self.cropRect)
                self.crop_rectangle_changed.emit(self.get_current_crop_rect())

        self.update_image_info()

    def show_new_pixmap(self, pixmap):
        self.original_pixmap = pixmap
        self.previous_pixmap = pixmap
        self.current_pixmap = pixmap
        self.show_pixmap(pixmap)
        self.show_image_initial_size()

        # self.reset_rect()

    def open_new_image(self, image_path):
        self.image_path = image_path
        image = ImageProcessingAlgorithms.load_image_to_qimage(image_path)
        pixmap = QPixmap.fromImage(image)

        self.original_pixmap = pixmap
        self.previous_pixmap = pixmap
        self.current_pixmap = pixmap
        self.show_pixmap(pixmap)
        self.show_image_initial_size()
        # self.reset_rect()
    
    def setImage(self, image):
        if type(image) is QPixmap:
            pixmap = image
        elif type(image) is QImage:
            pixmap = QPixmap.fromImage(image)
        elif (np is not None) and (type(image) is np.ndarray):
            if len(image.shape) == 2:  # Grayscale image
                qimage = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_Grayscale8)
            elif len(image.shape) == 3 and image.shape[2] == 3:  # Color image
                qimage = QImage(image.data, image.shape[1], image.shape[0], image.shape[1] * 3, QImage.Format_RGB888)
            else:
                raise ValueError("Unsupported image shape.")
            pixmap = QPixmap.fromImage(qimage)
        else:
            raise RuntimeError("ImageViewer.setImage: Argument must be a QImage, QPixmap, or numpy.ndarray.")
        
        self.show_pixmap(pixmap)
        self.show_image_initial_size()
    
    def crop_image(self, rect):
        pixmap = self.get_current_pixmap()
        # rect = self.get_current_crop_rect()
        if not pixmap or rect.isNull():
            print("No pixmap or invalid crop rectangle.")
            return None
        # Crop the pixmap using the QRect. Note that QRect should be in the pixmap's coordinate system.
        cropped_pixmap = pixmap.copy(rect.toRect())
        self.show_pixmap(cropped_pixmap)
        self.show_image_initial_size()

    def wheelEvent(self, event: QWheelEvent):
        if event.angleDelta().y() > 0:
            self.zoom(1.1)
        else:
            self.zoom(0.9)

    def zoom_out(self):
        self.zoom(0.9)
        
    def zoom_in(self):
        self.zoom(1.1)
        
    def zoom(self, factor):
            self.scale(factor, factor)
    
    def updateViewer(self, zoomRect):
        if not self.hasImage():
            return
        if (zoomRect):
            self.fitInView(zoomRect, self.aspectRatioMode)  # Show zoomed rect.
        else:
            self.fitInView(self.sceneRect(), self.aspectRatioMode)  # Show entire image.

    def hasImage(self):
        """ Returns whether the scene contains an image pixmap.
        """
        return self.pixmap_item is not None
            
    def keyPressEvent(self, event):
        if (self.regionZoomKey is not None) and (event.key() == self.regionZoomKey):
            self.regionZoomKeyPressed = True
            if self._crop_mode:
                self.setCursor(Qt.CursorShape.OpenHandCursor)
            else:
                self.setCursor(Qt.CursorShape.CrossCursor)
    
    def keyReleaseEvent(self, event):
        if (self.regionZoomKey is not None) and (event.key() == self.regionZoomKey):
            self.regionZoomKeyPressed = False

            if self._crop_mode:
                self.setCursor(Qt.CursorShape.CrossCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)
    

    def mousePressEvent(self, event):
        # Start dragging to pan?
        self._pixelPosition = event.pos()  # store pixel position

        super().mousePressEvent(event)
        if self._crop_mode:
            if  (self.regionZoomKeyPressed == True) and (event.button() == Qt.MouseButton.LeftButton):
                self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
                self._isPanning = True
                self._startPosPanning = event.pos()
            elif (event.button() == Qt.MouseButton.LeftButton):
                self.rect_start_point = self.mapToScene(event.pos())
                # if self.scene.itemAt(1) is not self.cropRect :
                self.scene.addItem(self.cropRect)

                self.cropRect.setRect(QRectF(self.rect_start_point, self.rect_start_point))
        else:
            # Start dragging a region zoom box?
            if (self.regionZoomKeyPressed == True) and (event.button() == Qt.MouseButton.LeftButton):
                self._pixelPosition = event.pos()  # store pixel position
                self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
                self._isZooming = True
            elif (event.button() == Qt.MouseButton.LeftButton):
                self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
                self._isPanning = True
                self._startPosPanning = event.pos()

        # event.accept()
        QGraphicsView.mousePressEvent(self, event)
    
    def reset_rect(self):
        rect_changed = False
        rect = self.get_current_crop_rect()
        # Adjust rect to ensure it's within the image boundaries
        rect.setLeft(self.sceneRect().left())
        rect.setRight(self.sceneRect().right())
        rect.setTop(self.sceneRect().top())
        rect.setBottom(self.sceneRect().bottom())
        self.cropRect.setRect(rect)
        return rect_changed
    
    def update_rect(self):
        rect_changed = False
        rect = self.get_current_crop_rect()
        # Adjust rect to ensure it's within the image boundaries
        if rect.left() < self.sceneRect().left():
            rect.setLeft(self.sceneRect().left())
            rect_changed = True
        if rect.right() > self.sceneRect().right():
            rect.setRight(self.sceneRect().right())
            rect_changed = True
        if rect.top() < self.sceneRect().top():
            rect.setTop(self.sceneRect().top())
            rect_changed = True
        if rect.bottom() > self.sceneRect().bottom():
            rect.setBottom(self.sceneRect().bottom())
            rect_changed = True
        self.cropRect.setRect(rect)
        return rect_changed
        
    def mouseMoveEvent(self, event):
        # print(event.button())
        super().mouseMoveEvent(event)
        if self._isPanning:
            # Calculate the movement delta in the view's coordinate system
            delta = event.pos() - self._startPosPanning
            
            # Scaling factor for panning sensitivity
            scaling_factor = 0.01  # Adjust based on testing
            
            # Apply the scaled delta to the scroll bars, converting to int
            new_h_value = self.horizontalScrollBar().value() - int(delta.x() * scaling_factor)
            new_v_value = self.verticalScrollBar().value() - int(delta.y() * scaling_factor)
            
            self.horizontalScrollBar().setValue(new_h_value)
            self.verticalScrollBar().setValue(new_v_value)
            
            # Update the start position for the next event
            self._startPosPanning = event.pos()
        
        elif self._crop_mode:
            current_point = self.mapToScene(event.pos())
            
            # Ensure current_point does not go beyond the image's boundaries
            # Assuming self.imageRect represents the QRectF of the image's dimensions
            max_x = max(min(current_point.x(), self.sceneRect().right()), self.sceneRect().left())
            max_y = max(min(current_point.y(), self.sceneRect().bottom()), self.sceneRect().top())
            current_point.setX(max_x)
            current_point.setY(max_y)
            
            rect = QRectF(self.rect_start_point, current_point).normalized()
            
            self.cropRect.setRect(rect)
            self.update_rect()

        QGraphicsView.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        if self._crop_mode:
            if self._isPanning:
                self.setDragMode(QGraphicsView.DragMode.NoDrag)
                self._isPanning = False
            elif event.button() == Qt.MouseButton.LeftButton:
                # rect = self.cropRect.rect()
                # Emit updating the crop rectangle
                self.crop_rectangle_changed.emit(self.get_current_crop_rect())
        else:
            if (self.regionZoomKeyPressed == True) and (event.button() == Qt.MouseButton.LeftButton):
                zoomRect = self.scene.selectionArea().boundingRect().intersected(self.sceneRect())
                self.setDragMode(QGraphicsView.DragMode.NoDrag)
                self.scene.setSelectionArea(QPainterPath())
                zoomPixelWidth = abs(event.pos().x() - self._pixelPosition.x())
                zoomPixelHeight = abs(event.pos().y() - self._pixelPosition.y())
                if zoomPixelWidth > 3 and zoomPixelHeight > 3:
                    if zoomRect.isValid() and (zoomRect != self.sceneRect()):
                        self.updateViewer(zoomRect)
            elif self._isPanning:
                self.setDragMode(QGraphicsView.DragMode.NoDrag)
                self._isPanning = False
    
    
    def get_original_pixmap(self):
        return self.original_pixmap
    
    def get_current_pixmap(self):
        return self.current_pixmap
    
    def get_previous_pixmap(self):
        return self.previous_pixmap
    
    def get_current_crop_rect(self):
        return self.cropRect.rect()
    
    def set_crop_rectangle(self, x, y, width, height):
        self.cropRect.setRect(QRectF(QPointF(x,y), QSizeF(width, height)))
        if self.update_rect():
            self.crop_rectangle_changed.emit(self.get_current_crop_rect())

    def flip_vertical(self):
        if self.current_pixmap:
            # Flip the pixmap vertically
            self.current_pixmap = self.current_pixmap.transformed(QTransform().scale(1, -1))
            # Update the pixmap item with the new pixmap
            self.show_pixmap(self.current_pixmap)
            self.show_image_initial_size()  # Adjust the view to fit the flipped image
            self.reset_rect()

    def flip_horizontal(self):
        if self.current_pixmap:
            # Flip the pixmap horizontally
            self.current_pixmap = self.current_pixmap.transformed(QTransform().scale(-1, 1))
            # Update the pixmap item with the new pixmap
            self.show_pixmap(self.current_pixmap)
            self.show_image_initial_size()  # Adjust the view to fit the flipped image
            self.reset_rect()

    def rotate_left(self):
        if self.current_pixmap:
            # Rotate the pixmap 90 degrees counter-clockwise
            self.current_pixmap = self.current_pixmap.transformed(QTransform().rotate(-90))
            # Update the pixmap item with the new pixmap
            self.show_pixmap(self.current_pixmap)
            self.show_image_initial_size()  # Adjust the view to fit the rotated image
            self.reset_rect()

    def rotate_right(self):
        if self.current_pixmap:
            # Rotate the pixmap 90 degrees clockwise
            self.current_pixmap = self.current_pixmap.transformed(QTransform().rotate(90))
            # Update the pixmap item with the new pixmap
            self.show_pixmap(self.current_pixmap)
            self.show_image_initial_size()  # Adjust the view to fit the rotated image
            self.reset_rect()

    def adjust_lightning(self, contrast_value, brightness_value, gamma_value):
        print("Adjust Contrast: %.2f  Brightness: %.2f  Gamma: %.2f" % (contrast_value, brightness_value, gamma_value))
        
        image_cv = self.convert_pixmap_to_opencv_image(self.get_original_pixmap())
        image_cv = ImageProcessingAlgorithms.adjust_contrast_brightness_gamma(image_cv, contrast_value, brightness_value, gamma_value)
        image_pixmap = self.convert_opencv_image_to_pixmap(image_cv)
        self.current_pixmap = image_pixmap
        self.show_pixmap(self.current_pixmap)

    def adjust_colors(self, temperature_value, saturation_value, hue_value, red_value, green_value, blue_value):
        print("Adjust Colors : temperature_value:  %.2f, saturation_value:  %.2f, hue_value:  %.2f, red_value:  %.2f, green_value:  %.2f, blue_value: %.2f" % (temperature_value, saturation_value, hue_value, red_value, green_value, blue_value))
        
        temperature_value = np.clip(temperature_value*5500 + 1050, 1000, 12000)
        print("Adjust Temperature: %.2f Kelvin" % (temperature_value))
        
        hue_value = hue_value*180
        print("Hue shift: %.2f degrees" % (hue_value))
        

        image_cv = self.convert_pixmap_to_opencv_image(self.get_original_pixmap())
        image_cv = ImageProcessingAlgorithms.change_color_temperature(image_cv, temperature_value, red_value, green_value, blue_value)
        image_cv = ImageProcessingAlgorithms.adjust_saturation_hue(image_cv, saturation_value, hue_value)
        
        image_pixmap = self.convert_opencv_image_to_pixmap(image_cv)
        self.current_pixmap = image_pixmap
        self.show_pixmap(self.current_pixmap)
    
    def apply_lut_to_current_pixmap(self, lut_global, lut_shadows, lut_highlight, mask, channel):
        print("Apply LUT to current image.")
        
        

        if self.original_pixmap is not None:
            # Generate mask
            grayscale_image = self.get_original_pixmap().toImage().convertToFormat(QImage.Format.Format_Grayscale8)
            mask_lowres = grayscale_image.scaled(16, 16)    
            mask_fulres = mask_lowres.scaled(self.get_original_pixmap().width(), 
                                                self.get_original_pixmap().height(), 
                                                Qt.AspectRatioMode.IgnoreAspectRatio, 
                                                Qt.TransformationMode.SmoothTransformation)
            
            mask_fulres_cv = ImageProcessingAlgorithms.convertQImageToArray(mask_fulres)[:,:,0] # decerease the 3 dimension to 2
            
            image_cv = self.convert_pixmap_to_opencv_image(self.get_original_pixmap())
            image_cv = ImageProcessingAlgorithms.apply_lut_global(image_cv, lut_global, channel)
            
            image_cv = ImageProcessingAlgorithms.apply_lut_local(image_cv, lut_shadows, lut_highlight, channel, mask_fulres_cv)
            image_pixmap = self.convert_opencv_image_to_pixmap(image_cv)
            self.current_pixmap = image_pixmap
            self.show_pixmap(self.current_pixmap)

    def convert_pixmap_to_opencv_image(self, pixmap):
        return ImageProcessingAlgorithms.convertQImageToArray(pixmap.toImage())

    def convert_opencv_image_to_pixmap(self, cv_image):
        return QPixmap.fromImage(ImageProcessingAlgorithms.convertArrayToQImage(cv_image))
    
            
    