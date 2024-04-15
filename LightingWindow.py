from ImageEditingWindow import ImageEditingsWindow

class LightingWindow(ImageEditingsWindow):

    slider_list = [ "Brightness",
                    "Contrast",
                    "Gamma",
                    "Shadows",
                    "Highlights"]

    def slider_values_changed(self, value):
        self.read_values_from_sliders()
        self.image_viewer.adjust_lightning(self.contrast_value, self.brightness_value, self.gamma_value)

    def read_values_from_sliders(self):
        # self.slider_layer.print_values()
        self.contrast_value = 1- self.slider_layer.sliders["Contrast"].value()/50.0
        self.brightness_value = self.slider_layer.sliders["Brightness"].value()/50.0 - 1
        self.gamma_value = 2 - self.slider_layer.sliders["Gamma"].value()/50.0
        self.shadows_value = self.slider_layer.sliders["Shadows"].value()/50.0
        self.highlights_value = self.slider_layer.sliders["Highlights"].value()/50.0
