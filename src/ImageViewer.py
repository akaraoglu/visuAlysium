
import numpy as np
import os
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas


from PyQt6.QtGui import QWheelEvent, QPaintEvent
from PyQt6.QtCore import pyqtSlot,pyqtSignal, Qt, QSize, QPoint, QRect, QRectF, QPointF, QSizeF
from PyQt6.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QSpacerItem, QSizePolicy, QVBoxLayout,QHBoxLayout,QComboBox, QPushButton, QGraphicsRectItem, QFileDialog, QMenu, QGraphicsProxyWidget, QRubberBand, QLabel, QWidget
from PyQt6.QtGui import QPixmap, QCursor, QAction, QPen, QImage, QPainterPath, QTransform, QColor, QFont, QBrush

from src.WidgetUtils import HoverButton
import src.ImageProcessingAlgorithms as ImageProcessingAlgorithms
from src.util.CustomInfoPanel import CustomInfoPanel


class ImageViewer(QGraphicsView):
    crop_rectangle_changed = pyqtSignal(QRectF)

    BUTTON_SIZE = QSize(60, 60)
    ICON_SIZE = QSize(40, 40)

    def __init__(self):
        super().__init__()
        self.__scene = QGraphicsScene()
        self.setScene(self.__scene)
        
        # Flags for active zooming/panning.
        self.__is_panning = False        # to enable or disable pan
        self.__pixmap_item = None
        
        # Store temporary position in screen pixels or scene units.
        self.__pixel_position = QPoint()
        self.__scene_position = QPointF()
        self.__crop_mode = False
        self.__crop_active = False

        self.__current_pixmap = None
        self.__previous_pixmap = None
        self.__original_pixmap = None
        
        self.__crop_rect = QGraphicsRectItem()
        self.__crop_rect.setPen(QPen(QColor('red'), 2, Qt.PenStyle.SolidLine))
         
        # # Add buttons
        button_fit_screen = self.create_new_button(icon="icons/fullscreen.png", connect_to=self.show_image_fit_to_screen)
        button_original_size = self.create_new_button(icon="icons/original_size.png", connect_to=self.show_image_in_original_size)
        button_zoom_in = self.create_new_button(icon="icons/zoom-in.png", connect_to=self.zoom_in)
        button_zoom_out = self.create_new_button(icon="icons/zoom-out.png", connect_to=self.zoom_out)

        self.__button_proxy_list = [button_fit_screen, button_original_size, button_zoom_in, button_zoom_out]

        self.createContextMenu()
        self.__aspect_ratio_mode = Qt.AspectRatioMode.KeepAspectRatio
        self.__region_zoom_key = Qt.Key.Key_Control  # Drag a zoom box.
        self.__region_zoom_key_pressed = False

        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setInteractive(True)

        self.__rect_start_point = None

        self.__image_path = ""
        self.__info_display_visible = False
        self.__info_widget = CustomInfoPanel()
        self.__info_label_proxy = QGraphicsProxyWidget()
        self.__info_label_proxy.setWidget(self.__info_widget)
        self.__info_widget.setGeometry(10, 10, 400, 400)
        self.__scene.addItem(self.__info_label_proxy)

        self.init_info_display()
        
        self.__curve_option = "Luminance" #default
        self.__info_widget.channel_combo_box.currentTextChanged.connect(self.channel_option_selected)
        
        # Set the focus policy to accept focus by tabbing and clicking
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

    def init_info_display(self):
        if self.__info_display_visible == True:
            # self.__info_label_proxy.setVisible(True)
            self.__info_widget.setVisible(True)
        else:
            # self.__info_label_proxy.setVisible(False)
            self.__info_widget.setVisible(False)

    def toggle_info_display(self):
        # self.show_pixmap(self.get_current_pixmap())
        if self.__info_display_visible == False:
            self.__info_display_visible = True
        else:
            self.__info_display_visible = False
        self.init_info_display()
        self.update_image_info()
        
        print("Showing histogram: ", self.__info_display_visible)

    def createContextMenu(self):
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.showContextMenu)

        self.__context_menu = QMenu(self)
        self.__copy_action = QAction("Copy Image", self)
        self.__copy_action.triggered.connect(self.copyImage)
        self.__paste_action = QAction("Paste Image", self)
        self.__paste_action.triggered.connect(self.pasteImage)
        self.__save_action = QAction("Save As ...", self)
        self.__save_action.triggered.connect(self.saveImage)

        self.__context_menu.addAction(self.__copy_action)
        self.__context_menu.addAction(self.__paste_action)
        self.__context_menu.addAction(self.__save_action)
    
    def toggle_zoom_mode(self):
        if self.transform().m11() == 1.0:  # If the current zoom is 100% (original size)
            self.show_image_fit_to_screen()
        else:
            self.show_image_in_original_size()

    def set_zoom(self, factor):
        self.resetTransform()  # Reset any existing transformations
        self.scale(factor, factor)  # Apply the new zoom factor


    def create_new_button(self, icon, connect_to) -> QGraphicsProxyWidget:
        new_button = HoverButton(parent=None, text="", icon=icon, button_size=self.BUTTON_SIZE, icon_size=self.ICON_SIZE)
        new_button.clicked.connect(connect_to)  # Connect button click to originalSize method

        # Add the buttons to the scene
        new_button_proxy = QGraphicsProxyWidget()
        new_button_proxy.setWidget(new_button)
        
        self.__scene.addItem(new_button_proxy)
        return new_button_proxy
    
    def channel_option_selected(self, option):
        print(f"Selected curve option: {option}")
        self.__curve_option = option
        self.update_image_info()
        # Implement functionality based on selected option

    def update_image_info(self):
        if self.__info_display_visible == True:
            # Update the display with new information
            if self.__current_pixmap:
                if self.__image_path != "":
                    # Getting file properties
                    file_info = os.stat(self.__image_path)
                    file_size = file_info.st_size / 1024  # Size in KB
                    modification_time = datetime.fromtimestamp(file_info.st_mtime).strftime('%Y-%m-%d %H:%M:%S')

                    # Getting image properties
                    image = QImage(self.__image_path)  # Using QImage to get bit depth
                    bit_depth = image.depth()

                    # Preparing info text
                    info_list = [
                        f"{os.path.basename(self.__image_path)}",
                        f"{os.path.dirname(self.__image_path)}",
                        f"{self.__image_path.split('.')[-1].upper()}",
                        f"{file_size:.2f} KB",
                        f"{modification_time}",
                        f"{self.__current_pixmap.width()}x{self.__current_pixmap.height()}",
                        f"{bit_depth} bits" ]

                    # self.info_label.setText(info_text)
                    self.__info_widget.update_info(info_list)

                # Calculate histogram for luminance
                option = self.__curve_option
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
                
                self.__info_widget.update_histogram(QPixmap.fromImage(qimage))

                # Clear the figure to release memory
                plt.close(fig)

    def set_crop_mode(self, enabled):
        self.__crop_mode = enabled
        self.setCursor(Qt.CursorShape.CrossCursor)

    def reset_rect(self):
        if self.__crop_rect is not None:
            self.__scene.removeItem(self.__crop_rect)
            self.__crop_rect.setRect(self.__pixmap_item.sceneBoundingRect())
            if self.update_rect():
                self.crop_rectangle_changed.emit(self.get_current_crop_rect())

    def showContextMenu(self, pos):
        self.__context_menu.exec(QCursor.pos())

    def copyImage(self):
        if self.__pixmap_item is not None:
            # Copy the pixmap
            QApplication.clipboard().setPixmap(self.__pixmap_item.pixmap())

    def pasteImage(self):
        # Get the pixmap from clipboard if available and add it to the scene
        clipboard = QApplication.clipboard()
        if clipboard.mimeData().hasImage():
            pixmap = clipboard.pixmap()
            self.show_pixmap(pixmap)

    def saveImage(self):
        if self.__pixmap_item is not None:
            filename, _ = QFileDialog.getSaveFileName(self, "Save As", "", "Images (*.png *.jpg *.bmp)")
            if filename:
                self.__pixmap_item.pixmap().save(filename)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.__reposition_buttons()

    def __reposition_buttons(self): 
        """Repositions the buttons to the view"""
        number_of_buttons = len(self.__button_proxy_list)
        bottom_center = int(self.viewport().width() / 2)
        dis_bet_buttons = 1
        height_needed = self.BUTTON_SIZE.height() + 15 # distance from lower boundry
        width_needed  = (self.BUTTON_SIZE.width()  * number_of_buttons) + (dis_bet_buttons*(number_of_buttons-1)) #  distance between the buttons
        
        y = self.viewport().height() - height_needed

        for i,button_proxy in enumerate(self.__button_proxy_list):
            x = bottom_center - int(width_needed/2 - (self.BUTTON_SIZE.width()*i) - (dis_bet_buttons*i))
            # Position the buttons at the bottom center
            scene_point = self.mapToScene(int(x), int(y))
            button_proxy: QGraphicsProxyWidget

            button_proxy.setPos(scene_point)

    def show_image_initial_size(self):
        pixmapSize = self.__pixmap_item.sceneBoundingRect().size()
        viewSize = self.size()

        if (pixmapSize.width() <= viewSize.width()) and (pixmapSize.height() <= viewSize.height()):
            self.show_image_in_original_size()
        else: 
            self.show_image_fit_to_screen()

    def show_image_fit_to_screen(self):
        # Implement fit to screen functionality
        if self.__pixmap_item is not None:
            self.fitInView(self.__pixmap_item, Qt.AspectRatioMode.KeepAspectRatio)
        print("Fit to screen.")
            
    def show_image_in_original_size(self):
        # Implement original size functionality
        if self.__pixmap_item is not None:
            original_size = self.__pixmap_item.pixmap().size()
            if not original_size.isEmpty():
                self.resetTransform()  # Reset any previous transformation
                scene_rect = self.__pixmap_item.sceneBoundingRect()
                width_ratio = scene_rect.width() / original_size.width()
                height_ratio = scene_rect.height() / original_size.height()
                self.scale(1 / width_ratio, 1 / height_ratio)
        print("Original size.")
    
    def show_pixmap(self, new_pixmap):
        if not new_pixmap.isNull():
            # Assign new_pixmap to current_pixmap if current_pixmap is None
            if self.__current_pixmap is None:
                self.__current_pixmap = new_pixmap

            # Fix: Assign new_pixmap to original_pixmap if original_pixmap is None
            if self.__original_pixmap is None:
                self.__original_pixmap = new_pixmap

            self.__previous_pixmap = self.__current_pixmap
            self.__current_pixmap = new_pixmap

            if self.__pixmap_item and self.__pixmap_item.scene() == self.__scene:
                self.__scene.removeItem(self.__pixmap_item)
            
            self.__pixmap_item = QGraphicsPixmapItem(self.__current_pixmap)
            self.__pixmap_item.setZValue(-1)
            self.setSceneRect(QRectF(self.__current_pixmap.rect()))  # Set scene size to image size
            self.__scene.addItem(self.__pixmap_item)            

        # show the rectangle over the image.
        if self.__crop_rect is not None:
            self.reset_rect()
            if self.__crop_rect.scene() == self.__scene: 
                self.__scene.removeItem(self.__crop_rect)
            # self.__crop_rect = QGraphicsRectItem()
            # self.__crop_rect.setPen(QPen(QColor('red'), 2, Qt.PenStyle.SolidLine))
            if self.__crop_mode:
                self.__scene.addItem(self.__crop_rect)
                self.crop_rectangle_changed.emit(self.get_current_crop_rect())

        self.update_image_info()

    def show_new_pixmap(self, pixmap):
        self.__original_pixmap = pixmap
        self.__previous_pixmap = pixmap
        self.__current_pixmap = pixmap
        self.show_pixmap(pixmap)
        self.show_image_initial_size()

        # self.reset_rect()

    def open_new_image(self, image_path):
        self.__image_path = image_path
        image = ImageProcessingAlgorithms.load_image_to_qimage(image_path)
        pixmap = QPixmap.fromImage(image)

        self.__original_pixmap = pixmap
        self.__previous_pixmap = pixmap
        self.__current_pixmap = pixmap
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
        self.__reposition_buttons()
        
    def zoom_in(self):
        self.zoom(1.1)
        self.__reposition_buttons()
        
    def zoom(self, factor):
            self.scale(factor, factor)
            self.__reposition_buttons()
    
    def updateViewer(self, zoomRect):
        if not self.hasImage():
            return
        if (zoomRect):
            self.fitInView(zoomRect, self.__aspect_ratio_mode)  # Show zoomed rect.
        else:
            self.fitInView(self.sceneRect(), self.__aspect_ratio_mode)  # Show entire image.

    def hasImage(self):
        """ Returns whether the scene contains an image pixmap.
        """
        return self.__pixmap_item is not None
            
    def keyPressEvent(self, event):
        if (self.__region_zoom_key is not None) and (event.key() == self.__region_zoom_key):
            self.__region_zoom_key_pressed = True
            if self.__crop_mode:
                self.setCursor(Qt.CursorShape.OpenHandCursor)
            else:
                self.setCursor(Qt.CursorShape.CrossCursor)

        if event.key() == Qt.Key.Key_1:
            self.toggle_zoom_mode()
        elif event.key() == Qt.Key.Key_2:
            self.set_zoom(2.0)  # 200%
        elif event.key() == Qt.Key.Key_3:
            self.set_zoom(3.0)  # 300%
        elif event.key() == Qt.Key.Key_4:
            self.set_zoom(4.0)  # 400%
        # Check if the pressed key is Esc
        elif event.key() == Qt.Key.Key_Escape:
            self.parent().close()  # Close the window
            
    def keyReleaseEvent(self, event):
        if (self.__region_zoom_key is not None) and (event.key() == self.__region_zoom_key):
            self.__region_zoom_key_pressed = False

            if self.__crop_mode:
                self.setCursor(Qt.CursorShape.CrossCursor)
            else:
                self.setCursor(Qt.CursorShape.ArrowCursor)


    def mousePressEvent(self, event):
        # Start dragging to pan?
        self.__pixel_position = event.pos()  # store pixel position

        super().mousePressEvent(event)
        if self.__crop_mode:
            if  (self.__region_zoom_key_pressed == True) and (event.button() == Qt.MouseButton.LeftButton):
                self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
                self.__is_panning = True
                self._startPosPanning = event.pos()
            elif (event.button() == Qt.MouseButton.LeftButton):
                self.__crop_active = True
                self.__rect_start_point = self.mapToScene(event.pos())
                self.__scene.addItem(self.__crop_rect)
                self.__crop_rect.setRect(QRectF(self.__rect_start_point, self.__rect_start_point))
        else:
            # Start dragging a region zoom box?
            if (self.__region_zoom_key_pressed == True) and (event.button() == Qt.MouseButton.LeftButton):
                self.__pixel_position = event.pos()  # store pixel position
                self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            elif (event.button() == Qt.MouseButton.LeftButton):
                self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
                self.__is_panning = True
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
        self.__crop_rect.setRect(rect)
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
        self.__crop_rect.setRect(rect)
        return rect_changed
        
    def mouseMoveEvent(self, event):
        # print(event.button())
        super().mouseMoveEvent(event)
        if self.__is_panning:
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
        
        elif self.__crop_mode and self.__crop_active:
            current_point = self.mapToScene(event.pos())
            
            # Ensure current_point does not go beyond the image's boundaries
            # Assuming self.imageRect represents the QRectF of the image's dimensions
            max_x = max(min(current_point.x(), self.sceneRect().right()), self.sceneRect().left())
            max_y = max(min(current_point.y(), self.sceneRect().bottom()), self.sceneRect().top())
            current_point.setX(max_x)
            current_point.setY(max_y)
            
            if self.__rect_start_point and current_point: 
                rect = QRectF(self.__rect_start_point, current_point).normalized()
            
                self.__crop_rect.setRect(rect)
                self.update_rect()

        QGraphicsView.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        if self.__crop_mode:
            if self.__is_panning:
                self.setDragMode(QGraphicsView.DragMode.NoDrag)
                self.__is_panning = False
            elif event.button() == Qt.MouseButton.LeftButton and self.__crop_active:
                # rect = self.__crop_rect.rect()
                # Emit updating the crop rectangle
                self.crop_rectangle_changed.emit(self.get_current_crop_rect())
                self.__crop_active = False
        else:
            if (self.__region_zoom_key_pressed == True) and (event.button() == Qt.MouseButton.LeftButton):
                zoomRect = self.__scene.selectionArea().boundingRect().intersected(self.sceneRect())
                self.setDragMode(QGraphicsView.DragMode.NoDrag)
                self.__scene.setSelectionArea(QPainterPath())
                zoomPixelWidth = abs(event.pos().x() - self.__pixel_position.x())
                zoomPixelHeight = abs(event.pos().y() - self.__pixel_position.y())
                if zoomPixelWidth > 3 and zoomPixelHeight > 3:
                    if zoomRect.isValid() and (zoomRect != self.sceneRect()):
                        self.updateViewer(zoomRect)
            elif self.__is_panning:
                self.setDragMode(QGraphicsView.DragMode.NoDrag)
                self.__is_panning = False
    
    
    def get_original_pixmap(self):
        return self.__original_pixmap
    
    def get_current_pixmap(self):
        return self.__current_pixmap
    
    def get_previous_pixmap(self):
        return self.__previous_pixmap
    
    def get_current_crop_rect(self):
        return self.__crop_rect.rect()
    
    def set_crop_rectangle(self, x, y, width, height):
        self.__crop_rect.setRect(QRectF(QPointF(x,y), QSizeF(width, height)))
        if self.update_rect():
            self.crop_rectangle_changed.emit(self.get_current_crop_rect())

    def flip_vertical(self):
        if self.__current_pixmap:
            # Flip the pixmap vertically
            self.__current_pixmap = self.__current_pixmap.transformed(QTransform().scale(1, -1))
            # Update the pixmap item with the new pixmap
            self.show_pixmap(self.__current_pixmap)
            self.show_image_initial_size()  # Adjust the view to fit the flipped image
            self.reset_rect()

    def flip_horizontal(self):
        if self.__current_pixmap:
            # Flip the pixmap horizontally
            self.__current_pixmap = self.__current_pixmap.transformed(QTransform().scale(-1, 1))
            # Update the pixmap item with the new pixmap
            self.show_pixmap(self.__current_pixmap)
            self.show_image_initial_size()  # Adjust the view to fit the flipped image
            self.reset_rect()

    def rotate_left(self):
        if self.__current_pixmap:
            # Rotate the pixmap 90 degrees counter-clockwise
            self.__current_pixmap = self.__current_pixmap.transformed(QTransform().rotate(-90))
            # Update the pixmap item with the new pixmap
            self.show_pixmap(self.__current_pixmap)
            self.show_image_initial_size()  # Adjust the view to fit the rotated image
            self.reset_rect()

    def rotate_right(self):
        if self.__current_pixmap:
            # Rotate the pixmap 90 degrees clockwise
            self.__current_pixmap = self.__current_pixmap.transformed(QTransform().rotate(90))
            # Update the pixmap item with the new pixmap
            self.show_pixmap(self.__current_pixmap)
            self.show_image_initial_size()  # Adjust the view to fit the rotated image
            self.reset_rect()

    def adjust_lightning(self, contrast_value, brightness_value, gamma_value, shadows_value, highlights_value):
        print("Adjust Contrast: %.2f  Brightness: %.2f  Gamma: %.2f Shadows: %.2f Highlights: %.2f" % (contrast_value, brightness_value, gamma_value, shadows_value, highlights_value))

        mask_fulres_cv = self.create_mask_luminance()

        image_cv = self.convert_pixmap_to_opencv_image(self.get_original_pixmap())
        image_cv = ImageProcessingAlgorithms.adjust_contrast_brightness_gamma(image_cv, contrast_value, brightness_value, gamma_value, shadows_value, highlights_value, mask_fulres_cv)
        image_pixmap = self.convert_opencv_image_to_pixmap(image_cv)
        self.__current_pixmap = image_pixmap
        self.show_pixmap(self.__current_pixmap)

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
        self.__current_pixmap = image_pixmap
        self.show_pixmap(self.__current_pixmap)
    
    def create_mask_luminance(self):
        grayscale_image = self.get_original_pixmap().toImage().convertToFormat(QImage.Format.Format_Grayscale8)
        mask_lowres = grayscale_image.scaled(64, 64)    
        mask_fulres = mask_lowres.scaled(self.get_original_pixmap().width(), 
                                            self.get_original_pixmap().height(), 
                                            Qt.AspectRatioMode.IgnoreAspectRatio, 
                                            Qt.TransformationMode.SmoothTransformation)
        
        mask_fulres_cv = ImageProcessingAlgorithms.convert_qimage_to_array(mask_fulres)[:,:,0] # decerease the 3 dimension to 2
        return mask_fulres_cv
    
    def apply_lut_to_current_pixmap(self, lut_global, lut_shadows, lut_highlight, mask, channel):
        print("Apply LUT to current image.")

        if self.__original_pixmap is not None:
            mask_fulres_cv = self.create_mask_luminance()
            
            image_cv = self.convert_pixmap_to_opencv_image(self.get_original_pixmap())
            image_cv = ImageProcessingAlgorithms.apply_lut_global(image_cv, lut_global, channel)
            image_cv = ImageProcessingAlgorithms.apply_lut_local(image_cv, lut_shadows, lut_highlight, channel, mask_fulres_cv)
            image_pixmap = self.convert_opencv_image_to_pixmap(image_cv)

            self.__current_pixmap = image_pixmap
            self.show_pixmap(self.__current_pixmap)

    def convert_pixmap_to_opencv_image(self, pixmap):
        return ImageProcessingAlgorithms.convert_qimage_to_array(pixmap.toImage())

    def convert_opencv_image_to_pixmap(self, cv_image):
        return QPixmap.fromImage(ImageProcessingAlgorithms.convert_array_to_qimage(cv_image))
    
            
    