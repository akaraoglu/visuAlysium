from src.WindowSliderAbstract import ImageEditingsWindow

class WindowLighting(ImageEditingsWindow):

    slider_list = [ "Brightness",
                    "Contrast",
                    "Gamma",
                    "Shadows",
                    "Highlights"]

    def slider_values_changed(self, value):
        self.read_values_from_sliders()
        self._image_viewer.adjust_lightning(self.__contrast_value, self.__brightness_value, self.__gamma_value, self.__shadows_value, self.__highlights_value)

    def read_values_from_sliders(self):
        # self.slider_layer.print_values()
        self.__contrast_value = 1- self.editing_options_layout.sliders["Contrast"].value()/50.0
        self.__brightness_value = self.editing_options_layout.sliders["Brightness"].value()/50.0 - 1
        self.__gamma_value = 2 - self.editing_options_layout.sliders["Gamma"].value()/50.0
        self.__shadows_value = self.editing_options_layout.sliders["Shadows"].value()/50.0 - 1
        self.__highlights_value = self.editing_options_layout.sliders["Highlights"].value()/50.0 - 1
