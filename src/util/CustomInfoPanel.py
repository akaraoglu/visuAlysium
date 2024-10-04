from PyQt6.QtWidgets import QSpacerItem, QSizePolicy, QVBoxLayout,QHBoxLayout,QComboBox, QLabel, QWidget
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont


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
        self.__info_labels = [
            info_file_name_label, info_location_label, info_type_label,
            info_size_label, info_date_time_label, info_attributes_label,
            info_dpi_label
        ]
        for label in self.__info_labels:
            label.setAlignment(Qt.AlignmentFlag.AlignLeft)
            label.setFixedSize(QSize(400,20))
            info_layout.addWidget(label)

        labels_and_info_layout.addLayout(labels_layout)
        labels_and_info_layout.addLayout(info_layout)
        layout.addLayout(labels_and_info_layout)

        # Placeholder for histogram
        self.__histogram_display = QLabel()
        layout.addWidget(self.__histogram_display)

            
        # Combo box and button for histogram controls
        histogram_controls_layout = QHBoxLayout()

        # Add a spacer item to push the combo box to the right
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        

        # Combo box for selecting the channel. 
        self.channel_combo_box = QComboBox()
        self.channel_combo_box.setMinimumSize(100, 10)
        
        self.channel_combo_box.addItems(["Luminance", "Red", "Green", "Blue"])
        histogram_controls_layout.addWidget(self.channel_combo_box)
        histogram_controls_layout.addItem(spacer)

        layout.addLayout(histogram_controls_layout)

    def update_info(self, info_dict):
        for i,info in enumerate(info_dict):
            print(info)
            self.__info_labels[i].setText(info)

    def update_histogram(self, pixmap):
        scaled_pixmap = pixmap.scaled(self.__histogram_display.width(), self.__histogram_display.height())
        self.__histogram_display.setPixmap(scaled_pixmap)