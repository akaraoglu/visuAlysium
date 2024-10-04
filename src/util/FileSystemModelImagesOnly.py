from PyQt6.QtGui import QFileSystemModel, QPixmap
from PyQt6.QtCore import QDir, QModelIndex, Qt
from PyQt6.QtWidgets import QApplication
from src.ImageProcessingAlgorithms import supported_extensions

class FileSystemModelImagesOnly(QFileSystemModel):
    def __init__(self, cacheWidth=100, cacheHeight=100):
        super().__init__()
        self.__previews = {'None': None}
        self.__cache_width = cacheWidth
        self.__cache_height = cacheHeight
        self.__ncols = 2
        
        # Specify the types of files to show
        self.setNameFilters(supported_extensions)
        self.setNameFilterDisables(False)  # Hide files that are not images

        # Include only directories and the specified files
        # Include directories and files but exclude '.' and '..'
        self.setFilter(QDir.Filter.AllDirs | QDir.Filter.Files | QDir.Filter.NoDotAndDotDot) 

    def getPreview(self, index: QModelIndex):
        itemName = super().data(index, Qt.ItemDataRole.DisplayRole)

        if itemName not in self.__previews:
            QApplication.setOverrideCursor(Qt.CursorShape.WaitCursor)  # Set cursor to waiting

            qpm = QPixmap(self.rootPath() + "/" + itemName)

            if qpm is None or qpm.isNull():
                qpm = super().data(index, Qt.ItemDataRole.DecorationRole)
                if qpm and not qpm.isNull():
                    qpm = qpm.pixmap(self.__cache_width, self.__cache_height)
            if qpm and not qpm.isNull():
                qpm = qpm.scaled(self.__cache_width, self.__cache_height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

            self.__previews[itemName] = qpm
            QApplication.restoreOverrideCursor()  # Restore the cursor

        return self.__previews[itemName]

    def data(self, index, role):
        if role == Qt.ItemDataRole.DecorationRole:
            return self.getPreview(index)
        elif role == Qt.ItemDataRole.ToolTipRole:
            # Return the filename as tooltip
            return self.filePath(index)
        else:
            return super().data(index, role)
