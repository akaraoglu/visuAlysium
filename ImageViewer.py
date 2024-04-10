from PyQt6.QtGui import QWheelEvent
from PyQt6.QtCore import pyqtSlot,pyqtSignal, Qt, QSize, QPoint, QRect, QRectF, QPointF, QSizeF
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QFileDialog, QMenu, QGraphicsProxyWidget, QRubberBand
from PyQt6.QtGui import QPixmap, QCursor, QAction, QPen, QImage, QPainterPath, QTransform, QColor


from HoverButton import HoverButton
import numpy as np

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

        self.cropRect = None
         
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

    def set_crop_mode(self, enabled):
        self._crop_mode = enabled
        self.setCursor(Qt.CursorShape.CrossCursor)


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
            self.load_new_pixmap(pixmap)

    def saveImage(self):
        if self.pixmap_item is not None:
            filename, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Images (*.png *.jpg *.bmp)")
            if filename:
                self.pixmap_item.pixmap().save(filename)

    def create_new_button(self, icon, connect_to):
        new_button = HoverButton(self, icon=icon, button_size=self.button_size, icon_size=self.icon_size)
        new_button.clicked.connect(connect_to)  # Connect button click to originalSize method

        # Add the buttons to the scene
        self.new_button_proxy = QGraphicsProxyWidget()
        self.new_button_proxy.setWidget(new_button)
        self.scene.addItem(self.new_button_proxy)
        return new_button

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
    
    def load_new_pixmap(self, new_pixmap):
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
                self.scene.removeItem(self.pixmap_item)
            
            self.pixmap_item = QGraphicsPixmapItem(self.current_pixmap)
            self.scene.addItem(self.pixmap_item)
            self.setSceneRect(QRectF(new_pixmap.rect()))  # Set scene size to image size
            self.show_image_initial_size()

        # show the rectangle over the image.
        if self.cropRect is not None:
            self.update_rect()
            self.scene.removeItem(self.cropRect)
            # self.cropRect = QGraphicsRectItem()
            # self.cropRect.setPen(QPen(QColor('red'), 2, Qt.PenStyle.SolidLine))
            self.scene.addItem(self.cropRect)
        
    def open_new_image(self, imagePath):
        pixmap = QPixmap(imagePath)
        self.original_pixmap = pixmap
        self.previous_pixmap = pixmap
        self.current_pixmap = pixmap
        self.load_new_pixmap(pixmap)
        
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
        
        self.load_new_pixmap(pixmap)
    
    def crop_image(self, rect):
        pixmap = self.get_current_pixmap()
        # rect = self.get_current_crop_rect()
        if not pixmap or rect.isNull():
            print("No pixmap or invalid crop rectangle.")
            return None
        # Crop the pixmap using the QRect. Note that QRect should be in the pixmap's coordinate system.
        cropped_pixmap = pixmap.copy(rect.toRect())
        self.load_new_pixmap(cropped_pixmap)

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
                if self.cropRect is None:
                    self.cropRect = QGraphicsRectItem()
                    self.cropRect.setPen(QPen(QColor('red'), 2, Qt.PenStyle.SolidLine))
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
        print(event.button())
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
    
    def get_current_pixmap(self):
        return self.current_pixmap
    
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
            self.load_new_pixmap(self.current_pixmap)
            self.show_image_initial_size()  # Adjust the view to fit the flipped image

    def flip_horizontal(self):
        if self.current_pixmap:
            # Flip the pixmap horizontally
            self.current_pixmap = self.current_pixmap.transformed(QTransform().scale(-1, 1))
            # Update the pixmap item with the new pixmap
            self.load_new_pixmap(self.current_pixmap)
            self.show_image_initial_size()  # Adjust the view to fit the flipped image

    def rotate_left(self):
        if self.current_pixmap:
            # Rotate the pixmap 90 degrees counter-clockwise
            self.current_pixmap = self.current_pixmap.transformed(QTransform().rotate(-90))
            # Update the pixmap item with the new pixmap
            self.load_new_pixmap(self.current_pixmap)
            self.show_image_initial_size()  # Adjust the view to fit the rotated image

    def rotate_right(self):
        if self.current_pixmap:
            # Rotate the pixmap 90 degrees clockwise
            self.current_pixmap = self.current_pixmap.transformed(QTransform().rotate(90))
            # Update the pixmap item with the new pixmap
            self.load_new_pixmap(self.current_pixmap)
            self.show_image_initial_size()  # Adjust the view to fit the rotated image
