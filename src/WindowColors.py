from src.WindowSliderAbstract import ImageEditingsWindow

class WindowColors(ImageEditingsWindow):
    slider_list = [ "Temperature",
                "Saturation",
                "Hue",
                "R",
                "G",
                "B"]

    def slider_values_changed(self, value):
        self.read_values_from_sliders()
        self.image_viewer.adjust_colors(self.__temperature_value, self.__saturation_value, self.__hue_value, self.__red_value, self.__green_value, self.__blue_value)

    def read_values_from_sliders(self):
        # self.slider_layer.print_values()
        self.__temperature_value  = self.editing_options_layout.sliders["Temperature"].value()  /50.0
        self.__saturation_value   = self.editing_options_layout.sliders["Saturation"].value()   /50.0
        self.__hue_value          = 1 - self.editing_options_layout.sliders["Hue"].value()      /50.0
        self.__red_value          = self.editing_options_layout.sliders["R"].value()            /50.0
        self.__green_value        = self.editing_options_layout.sliders["G"].value()            /50.0
        self.__blue_value         = self.editing_options_layout.sliders["B"].value()            /50.0
    