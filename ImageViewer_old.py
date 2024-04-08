from PyQt6.QtGui import QWheelEvent
from PyQt6.QtCore import pyqtSlot, Qt, QSize, QPoint, QRect, QRectF, QPointF
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsRectItem, QApplication, QFileDialog, QMenu, QGraphicsProxyWidget
from PyQt6.QtGui import QPixmap, QCursor, QAction, QPen, QImage


from HoverButton import HoverButton
import numpy as np

class ImageViewer(QGraphicsView):
    def __init__(self):
        super().__init__()
        self.scene = QGraphicsScene()
        self.setScene(self.scene)
        self.zoomX = 1              # zoom factor w.r.t size of qlabel_image
        self.position = [0, 0]      # position of top left corner of qimage_label w.r.t. qimage_scaled
        self.panFlag = False        # to enable or disable pan
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

        # # Add buttons
        self.button_list = []

        button_fit_screen = self.create_new_button(icon="icons/fullscreen.png", connect_to=self.show_image_fit_to_screen)
        button_original_size = self.create_new_button(icon="icons/original_size.png", connect_to=self.show_image_in_original_size)
        button_zoom_in = self.create_new_button(icon="icons/zoom-in.png", connect_to=self.zoom_in)
        button_zoom_out = self.create_new_button(icon="icons/zoom-out.png", connect_to=self.zoom_out)

        self.button_list.append(button_fit_screen)
        self.button_list.append(button_original_size)
        self.button_list.append(button_zoom_in)
        self.button_list.append(button_zoom_out)

        self.createContextMenu()
    
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
            if self.pixmap_item is not None:
                if self.current_pixmap is None:  self.current_pixmap = new_pixmap
                if self.original_pixmap is None:  self.current_pixmap = new_pixmap
                self.previous_pixmap = self.current_pixmap
                self.scene.removeItem(self.pixmap_item)
                self.current_pixmap = new_pixmap
            self.scene.clear()  # Clear existing items
            self.resetTransform()  # Reset any previous transformation
            self.pixmap_item = QGraphicsPixmapItem(self.current_pixmap)
            self.scene.addItem(self.pixmap_item)
            # scene_rect = self.scene.itemsBoundingRect()
            # self.setSceneRect(scene_rect)
            self.setSceneRect(QRectF(new_pixmap.rect()))  # Set scene size to image size.
            self.show_image_initial_size()
        
    def setImage(self, imagePath):
        pixmap = QPixmap(imagePath)
        self.original_pixmap = pixmap
        self.previous_pixmap = pixmap
        self.current_pixmap = pixmap
        self.load_new_pixmap(pixmap)
    
    def setImage(self, image):
        """ Set the scene's current image pixmap to the input QImage or QPixmap.
        Raises a RuntimeError if the input image has type other than QImage or QPixmap.
        :type image: QImage | QPixmap
        """
        if type(image) is QPixmap:
            pixmap = image
        elif type(image) is QImage:
            pixmap = QPixmap.fromImage(image)
        elif (np is not None) and (type(image) is np.ndarray):
                image = image.astype(np.float32)
                image -= image.min()
                image /= image.max()
                image *= 255
                image[image > 255] = 255
                image[image < 0] = 0
                image = image.astype(np.uint8)
                height, width = image.shape
                bytes = image.tobytes()
                qimage = QImage(bytes, width, height, QImage.Format.Format_Grayscale8)
                pixmap = QPixmap.fromImage(qimage)
        else:
            raise RuntimeError("ImageViewer.setImage: Argument must be a QImage, QPixmap, or numpy.ndarray.")
        
        self.load_new_pixmap(pixmap)

        
        self.updateViewer()

        
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
            
    def mousePressEvent(self, event):
        # Start dragging to pan?
        self._pixelPosition = event.pos()  # store pixel position
        
        


        if self._crop_mode:
            self.rect_item = None
            self.rectItem = QGraphicsRectItem()
            self.rectItem.setPen(QPen(Qt.GlobalColor.red))
            self.scene.addItem(self.rectItem)
            self.startPoint = self.mapToScene(event.pos())
        else:
            if event.button() == Qt.MouseButton.LeftButton:
                self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
                # QGraphicsView.mousePressEvent(self, event)
                sceneViewport = self.mapToScene(self.viewport().rect()).boundingRect().intersected(self.sceneRect())
                self._scenePosition = sceneViewport.topLeft()
                # event.accept()
                self.panFlag = True
                self.startPos = self.mapToScene(event.pos())

    def mouseMoveEvent(self, event):
        if self._crop_mode:
            if self.rectItem is not None:
                rect = QRectF(self.startPoint, self.mapToScene(event.pos())).normalized()
                self.rectItem.setRect(rect)
        else:
            if self.panFlag:
                # sceneViewport = self.mapToScene(self.viewport().rect()).boundingRect().intersected(self.sceneRect())
                # delta = sceneViewport.topLeft() - self._scenePosition
                delta = self.mapToScene(event.pos()) - self.startPos
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - int(delta.x()))
                self.verticalScrollBar().setValue(self.verticalScrollBar().value() - int(delta.y()))
                print(self.horizontalScrollBar().value() , int(delta.x()))
                self.startPos = self.mapToScene(event.pos())


    def mouseReleaseEvent(self, event):
        if self._crop_mode:
            if self.rectItem is not None:
                rect = QRectF(self.startPoint, self.mapToScene(event.pos())).normalized()
                self.rectItem.setRect(rect)
                self.rectItem = None
        else:
            if event.button() == Qt.MouseButton.LeftButton:
                self.setDragMode(QGraphicsView.DragMode.NoDrag)
                self.panFlag = False
    
    def get_current_pixmap(self):
        return self.current_pixmap
    