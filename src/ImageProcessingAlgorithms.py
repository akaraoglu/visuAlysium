#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# This file is part of VisuAlysium, which is released under the GNU General Public License (GPL).
# See the LICENSE or COPYING file in the root of this project or visit 
# http://www.gnu.org/licenses/gpl-3.0.html for the full text of the license.

"""
VisuAlysium 
=================================================================

This file includes the necessery image processing algorithm for the image editor. 

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
import cv2
import numpy as np
import OpenEXR
import Imath
import rawpy
from PyQt6.QtGui import QImage, QImageReader
from numpy.lib.stride_tricks import as_strided
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

supportedFormats = QImageReader.supportedImageFormats()
# text_filter = "Images ({})".format(" ".join(["*.{}".format(fo.data().decode()) for fo in supportedFormats]))

raw_extensions = [
    '*.cr2', '*.cr3', '*.crw',  # Canon
    '*.nef', '*.nrw',          # Nikon
    '*.pef',                  # Pentax
    '*.raf',                  # Fuji
    '*.rwl',                  # Leica
    '*.mrw',                  # Minolta
    '*.orf',                  # Olympus
    '*.srw',                  # Samsung
    '*.x3f',                  # Sigma
    '*.arw', '*.sr2', '*.srf',  # Sony
    '*.rw2',                  # Panasonic
    '*.dng'                   # Adobe DNG
]

standard_extensions = [
    '*.jpg', '*.jpeg', '*.bmp', '*.gif', '*.png', '*.tiff',
    '*.pcx', '*.tga', '*.jp2', '*.psd', '*.eps', '*.wmf',
    '*.cur', '*.heic', '*.webp', '*.pdf',  # Existing extensions
    '*.icns', '*.ico', '*.pbm', '*.pgm', '*.ppm', '*.svg',
    '*.svgz', '*.wbmp', '*.xbm', '*.xpm'  # New extensions added
]

exr_extensions = ['*.exr', '*.EXR']

supported_extensions = raw_extensions + standard_extensions + exr_extensions

kelvin_list = [1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900,
            2000, 2100, 2200, 2300, 2400, 2500, 2600, 2700, 2800, 2900,
            3000, 3100, 3200, 3300, 3400, 3500, 3600, 3700, 3800, 3900,
            4000, 4100, 4200, 4300, 4400, 4500, 4600, 4700, 4800, 4900,
            5000, 5100, 5200, 5300, 5400, 5500, 5600, 5700, 5800, 5900,
            6000, 6100, 6200, 6300, 6400, 6500, 6550, 6600, 6700, 6800, 6900,
            7000, 7100, 7200, 7300, 7400, 7500, 7600, 7700, 7800, 7900,
            8000, 8100, 8200, 8300, 8400, 8500, 8600, 8700, 8800, 8900,
            9000, 9100, 9200, 9300, 9400, 9500, 9600, 9700, 9800, 9900,
            10000, 10100, 10200, 10300, 10400, 10500, 10600, 10700, 10800, 10900,
            11000, 11100, 11200, 11300, 11400, 11500, 11600, 11700, 11800, 11900,
            12000]

kelvin_table = {
    1000: (255, 56, 0),
    1100: (255, 71, 0),
    1200: (255, 83, 0),
    1300: (255, 93, 0),
    1400: (255, 101, 0),
    1500: (255, 109, 0),
    1600: (255, 115, 0),
    1700: (255, 121, 0),
    1800: (255, 126, 0),
    1900: (255, 131, 0),
    2000: (255, 138, 18),
    2100: (255, 142, 33),
    2200: (255, 147, 44),
    2300: (255, 152, 54),
    2400: (255, 157, 63),
    2500: (255, 161, 72),
    2600: (255, 165, 79),
    2700: (255, 169, 87),
    2800: (255, 173, 94),
    2900: (255, 177, 101),
    3000: (255, 180, 107),
    3100: (255, 184, 114),
    3200: (255, 187, 120),
    3300: (255, 190, 126),
    3400: (255, 193, 132),
    3500: (255, 196, 137),
    3600: (255, 199, 143),
    3700: (255, 201, 148),
    3800: (255, 204, 153),
    3900: (255, 206, 159),
    4000: (255, 209, 163),
    4100: (255, 211, 168),
    4200: (255, 213, 173),
    4300: (255, 215, 177),
    4400: (255, 217, 182),
    4500: (255, 219, 186),
    4600: (255, 221, 190),
    4700: (255, 223, 194),
    4800: (255, 225, 198),
    4900: (255, 227, 202),
    5000: (255, 228, 206),
    5100: (255, 230, 210),
    5200: (255, 232, 213),
    5300: (255, 233, 217),
    5400: (255, 235, 220),
    5500: (255, 236, 224),
    5600: (255, 238, 227),
    5700: (255, 239, 230),
    5800: (255, 240, 233),
    5900: (255, 242, 236),
    6000: (255, 243, 239),
    6100: (255, 244, 242),
    6200: (255, 245, 245),
    6300: (255, 246, 247),
    6400: (255, 248, 251),
    6500: (255, 249, 253),
    6550: (255, 255, 255),
    6600: (254, 249, 255),
    6700: (252, 247, 255),
    6800: (249, 246, 255),
    6900: (247, 245, 255),
    7000: (245, 243, 255),
    7100: (243, 242, 255),
    7200: (240, 241, 255),
    7300: (239, 240, 255),
    7400: (237, 239, 255),
    7500: (235, 238, 255),
    7600: (233, 237, 255),
    7700: (231, 236, 255),
    7800: (230, 235, 255),
    7900: (228, 234, 255),
    8000: (227, 233, 255),
    8100: (225, 232, 255),
    8200: (224, 231, 255),
    8300: (222, 230, 255),
    8400: (221, 230, 255),
    8500: (220, 229, 255),
    8600: (218, 229, 255),
    8700: (217, 227, 255),
    8800: (216, 227, 255),
    8900: (215, 226, 255),
    9000: (214, 225, 255),
    9100: (212, 225, 255),
    9200: (211, 224, 255),
    9300: (210, 223, 255),
    9400: (209, 223, 255),
    9500: (208, 222, 255),
    9600: (207, 221, 255),
    9700: (207, 221, 255),
    9800: (206, 220, 255),
    9900: (205, 220, 255),
    10000: (207, 218, 255),
    10100: (207, 218, 255),
    10200: (206, 217, 255),
    10300: (205, 217, 255),
    10400: (204, 216, 255),
    10500: (204, 216, 255),
    10600: (203, 215, 255),
    10700: (202, 215, 255),
    10800: (202, 214, 255),
    10900: (201, 214, 255),
    11000: (200, 213, 255),
    11100: (200, 213, 255),
    11200: (199, 212, 255),
    11300: (198, 212, 255),
    11400: (198, 212, 255),
    11500: (197, 211, 255),
    11600: (197, 211, 255),
    11700: (197, 210, 255),
    11800: (196, 210, 255),
    11900: (195, 210, 255),
    12000: (195, 209, 255)}

def linear_interpolation(kelvin_value):
    """
    Interpolate linearly in the kelvin_list to find an interpolated index for a given kelvin value.

    Args:
    kelvin_value (float): The Kelvin temperature to interpolate.
    kelvin_list (list): The list of Kelvin temperatures.

    Returns:
    float: An interpolated index or interpolated value.
    """
    # Check if the kelvin_value is outside the bounds of the list
    if kelvin_value < kelvin_list[0] or kelvin_value > kelvin_list[-1]:
        raise ValueError("Kelvin value is outside the range of the kelvin list.")
   
    if kelvin_value in kelvin_table:
        return kelvin_table[kelvin_value]
    
    
    # Find the closest values
    lower_kelvin = max([k for k in kelvin_list if k < kelvin_value], default=None)
    higher_kelvin = min([k for k in kelvin_list if k > kelvin_value], default=None)
    
    if lower_kelvin is None or higher_kelvin is None:
        raise ValueError("Kelvin value is outside the range of the table.")

    # Get RGB values for the closest Kelvin temperatures
    lower_rgb = kelvin_table[lower_kelvin]
    higher_rgb = kelvin_table[higher_kelvin]

    # Linear interpolation for each color channel
    fraction = (kelvin_value - lower_kelvin) / (higher_kelvin - lower_kelvin)
    r = lower_rgb[0] + (higher_rgb[0] - lower_rgb[0]) * fraction
    g = lower_rgb[1] + (higher_rgb[1] - lower_rgb[1]) * fraction
    b = lower_rgb[2] + (higher_rgb[2] - lower_rgb[2]) * fraction

    # Return the interpolated RGB values rounded to the nearest integer
    return (int(round(r)), int(round(g)), int(round(b)))


def convert_array_to_qimage(array):
        """Convert an array-like image to a QImage in PyQt6.

        The created QImage is using a copy of the array data.

        Limitation: Only RGB or RGBA images with 8 bits per channel are supported.

        :param array: Array-like image data of shape (height, width, channels)
                    Channels are expected to be either RGB or RGBA.
        :type array: numpy.ndarray of uint8
        :return: Corresponding Qt image with RGB888 or ARGB32 format.
        :rtype: QImage
        """
        array = np.array(array, copy=False, order='C', dtype=np.uint8)

        if array.ndim != 3 or array.shape[2] not in (3, 4):
            raise ValueError('Image must be a 3D array with 3 or 4 channels per pixel.')

        if array.shape[2] == 4:
            format_ = QImage.Format.Format_ARGB32
            # RGBA -> ARGB + take care of endianness
            if sys.byteorder == 'little':  # RGBA -> BGRA
                array = array[:, :, (2, 1, 0, 3)]
            else:  # big endian: RGBA -> ARGB
                array = array[:, :, (3, 0, 1, 2)]

            array = np.require(array, requirements=['C', 'A'])  # Ensure array is C-contiguous and aligned

        else:  # array.shape[2] == 3
            format_ = QImage.Format.Format_RGB888

        height, width, depth = array.shape
        qimage = QImage(
            array.tobytes(),  # Convert the array to bytes
            width,
            height,
            array.strides[0],  # bytesPerLine
            format_)

        return qimage.copy()  # Making a copy of the image and its data

def convert_qimage_to_array(image):
    """Convert a QImage to a numpy array in PyQt6.

    If QImage format is not Format_RGB888, Format_RGBA8888, or Format_ARGB32,
    it is first converted to one of these formats depending on
    the presence of an alpha channel.

    The created numpy array is using a copy of the QImage data.

    :param QImage image: The QImage to convert.
    :return: The image array of RGB or RGBA channels of shape
            (height, width, channels (3 or 4))
    :rtype: numpy.ndarray of uint8
    """
    # In PyQt6, enums are accessed directly through the class rather than as attributes
    format_rgb888 = QImage.Format.Format_RGB888
    format_argb32 = QImage.Format.Format_ARGB32
    format_rgba8888 = QImage.Format.Format_RGBA8888

    # Convert to supported format if needed
    if image.format() not in (format_argb32, format_rgb888, format_rgba8888):
        if image.hasAlphaChannel():
            image = image.convertToFormat(format_rgba8888)
        else:
            image = image.convertToFormat(format_rgb888)

    format_ = image.format()
    channels = 3 if format_ == format_rgb888 else 4

    ptr = image.bits()
    # Adjustments for PyQt6: image.byteCount() is replaced with image.sizeInBytes()
    ptr.setsize(image.sizeInBytes())

    # Create an array view on QImage internal data
    view = as_strided(
        np.frombuffer(ptr, dtype=np.uint8),
        shape=(image.height(), image.width(), channels),
        strides=(image.bytesPerLine(), channels, 1))

    if format_ == format_argb32:
        # Convert from ARGB to RGBA
        # Not a byte-ordered format: do care about endianness
        if sys.byteorder == 'little':  # BGRA -> RGBA
            view = view[:, :, (2, 1, 0, 3)]
        else:  # big endian: ARGB -> RGBA
            view = view[:, :, (1, 2, 3, 0)]

    # Format_RGB888 and Format_RGBA8888 do not need reshuffling channels:
    # They are byte-ordered and already in the right order

    return np.array(view, copy=True, order='C')

def adjust_contrast_brightness_gamma(image, contrast_amount, brightness_amount, gamma_amount, shadows_amount, highlights_amount, weight_mask):
    """
    Adjusts the contrast, brightness, and applies gamma correction to an image.
    
    :param image: Input image.
    :param alpha_amount: Contrast adjustment factor. Values > 1 increase contrast, values between 0 and 1 decrease contrast.
    :param beta_amount: Brightness adjustment factor. The value is added to each pixel after contrast adjustment.
    :param gamma_amount: Gamma correction factor. Values > 1 make the image darker, values < 1 make the image brighter.
    :return: Image with adjusted contrast, brightness, and gamma correction.
    """

    # Ensure alpha_amount is within a reasonable range
    contrast_amount = max(min(contrast_amount, 1), -1)
    
    # Ensure gamma_amount is positive
    gamma_amount = max(gamma_amount, 0.01)  # Avoid division by zero or negative values
    
    # Compute the original intensity range
    min_val, max_val = image.min(), image.max()
    
    # Compute the target range for contrast adjustment
    target_min = (1 - contrast_amount) * min_val + contrast_amount * (255 * 0.25)
    target_max = (1 - contrast_amount) * max_val + contrast_amount * (255 * 0.75)

    # Vectorized computation of the lookup table for performance improvement
    original_range = np.arange(256, dtype=np.float32) / 255  # Normalize to [0,1] for gamma correction
    # Apply gamma correction in the normalized space
    gamma_corrected = np.power(original_range, gamma_amount)
    # Adjust for contrast and brightness, then scale back to [0,255]
    adjusted_range = np.clip(((gamma_corrected - min_val / 255) / ((max_val - min_val) / 255) * (target_max - target_min) + target_min) + (brightness_amount * 255), 0, 255).astype(np.uint8)
    
    # Apply the lookup table
    image_global = cv2.LUT(image, adjusted_range)
    adjusted_shadows = np.clip((image_global) + (shadows_amount * 255), 0, 255).astype(np.uint8)
    adjusted_highlights = np.clip((image_global) + (highlights_amount * 255), 0, 255).astype(np.uint8)
    mask_norm = (weight_mask[:,:,None]/255.0)
    return ( mask_norm * adjusted_highlights) + ((1-mask_norm) * adjusted_shadows)

# Adjust Sharpening
def color_sharpening(image, amount):
    b, g, r = cv2.split(image)

    blurred_b = cv2.GaussianBlur(b, (0, 0), 3)
    sharp_b = cv2.addWeighted(b, 1 + amount, blurred_b, -amount, 0)

    blurred_g = cv2.GaussianBlur(g, (0, 0), 3)
    sharp_g = cv2.addWeighted(g, 1 + amount, blurred_g, -amount, 0)

    blurred_r = cv2.GaussianBlur(r, (0, 0), 3)
    sharp_r = cv2.addWeighted(r, 1 + amount, blurred_r, -amount, 0)

    lab_sharp = cv2.merge((sharp_b, sharp_g, sharp_r))

    return lab_sharp

#Adjust Blurring
def colour_blurring(image,kernel_size):
    # Split the image into RGB channels
    b, g, r = cv2.split(image)

    b_blur = cv2.medianBlur(b, kernel_size)
    g_blur = cv2.medianBlur(g, kernel_size)
    r_blur = cv2.medianBlur(r, kernel_size)

    # Merge the blurred channels back into an RGB image
    blurred_image = cv2.merge((b_blur, g_blur, r_blur))

    return blurred_image

def adjust_gamma(image, gamma):
    lookUpTable = np.empty((1,256), np.uint8)
    for i in range(256):
        lookUpTable[0,i] = np.clip(pow(i / 255.0, gamma) * 255.0, 0, 255)
    
    return cv2.LUT(image, lookUpTable)


# temperature value between 100 (warmer) to 12000 (cooler)
def change_color_temperature(image, kelvin_value, red_gain=1.0, green_gain=1.0, blue_gain=1.0):
    
    # Vectorized computation of the lookup table for performance improvement
    original_range = np.arange(256, dtype=np.float32) 
    original_range_rgb = original_range[:,None].repeat(3,1)

    quality_factor = 2   # higher values means lesser quality. because.

    print('Working on Kelvin value: ', kelvin_value)
    temp = linear_interpolation(kelvin_value)
    r, g, b = temp

    # Apply gain adjustments to each channel based on the parameters
    r *= red_gain
    g *= green_gain
    b *= blue_gain

    transformation_matrix = [
    [r / 255.0, 0.0, 0.0],  # Red channel increases
    [0.0, g / 255.0, 0.0],  # Green channel decreases
    [0.0, 0.0, b / 255.0]   # Blue channel decreases
]
    # Matrix multiplication
    transformed_img = np.dot(original_range_rgb, transformation_matrix)

    adjusted_range = np.clip(np.round(transformed_img),0,255)
    
    # Apply the lookup table
    for c in range(3): 
        CH_RGB = image[:,:,c]
        new_range = adjusted_range[:,c]
        CH_RGB_NEW = cv2.LUT(CH_RGB, new_range)
        image[:,:,c] = CH_RGB_NEW
    return image

# def adjust_saturation_hue(image, saturation_amount):
#     # Convert RGB to HSV
#     image_HSV = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
       
#     # Adjust saturation
#     image_HSV[..., 1] = np.clip(image_HSV[..., 1] * saturation_amount, 0, 255)

#     return cv2.cvtColor(image_HSV, cv2.COLOR_HSV2RGB)

def adjust_saturation_hue(image, saturation_amount, hue_shift):
    # Convert RGB to HSV
    image_HSV = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
    
    # Adjust saturation
    image_HSV[..., 1] = np.clip(image_HSV[..., 1] * saturation_amount, 0, 255)
    
    # Adjust hue
    # OpenCV represents hue in the range 0-180 instead of 0-360
    # Hue_shift should be provided in degrees and will be converted to OpenCV's scale
    hue_shift = int((hue_shift / 360.0) * 180)  # Convert degrees to OpenCV hue scale
    image_HSV[..., 0] = (image_HSV[..., 0] + hue_shift) % 180

    # Convert back to RGB
    return cv2.cvtColor(image_HSV, cv2.COLOR_HSV2RGB)


def calculate_histogram(image, channel):
    if channel == 'Luminance':
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
    else:
        channel_map = {'Red': 0, 'Green': 1, 'Blue': 2}
        hist = cv2.calcHist([image], [channel_map[channel]], None, [256], [0, 256])
    return hist

def plot_to_qimage(fig):
    canvas = FigureCanvas(fig)
    canvas.draw()
    buf, (width, height) = canvas.print_to_buffer()
    qimage = QImage(buf, width, height, QImage.Format.Format_RGBA8888)
    return qimage

rawpy_params = rawpy.Params(
    demosaic_algorithm=None, 
    half_size=False, 
    four_color_rgb=False, 
    dcb_iterations=0, 
    dcb_enhance=False, 
    fbdd_noise_reduction=rawpy.FBDDNoiseReductionMode.Off, 
    noise_thr=None, 
    median_filter_passes=0, 
    use_camera_wb=False, 
    use_auto_wb=False, 
    user_wb=None, 
    output_color=rawpy.ColorSpace.sRGB, 
    output_bps=8, 
    user_flip=None, 
    user_black=None, 
    user_sat=None, 
    no_auto_bright=False, 
    auto_bright_thr=None, 
    adjust_maximum_thr=0.75, 
    bright=1.0, 
    highlight_mode=rawpy.HighlightMode.Clip, 
    exp_shift=None, 
    exp_preserve_highlights=0.0, 
    no_auto_scale=False, 
    gamma=None, 
    chromatic_aberration=None, 
    bad_pixels_path=None)

def exr_to_numpy(exr_file, clip=False):
    # Open the EXR file
    exr = OpenEXR.InputFile(exr_file)

    # Get the header to retrieve the size of the image
    header = exr.header()
    dw = header['dataWindow']
    width, height = dw.max.x - dw.min.x + 1, dw.max.y - dw.min.y + 1

    # Define the data type of the pixels
    pt = Imath.PixelType(Imath.PixelType.FLOAT)

    # Read the color channels (R, G, B)
    redstr = exr.channel('R', pt)
    greenstr = exr.channel('G', pt)
    bluestr = exr.channel('B', pt)

    # Convert the channel strings to numpy arrays
    red = np.frombuffer(redstr, dtype=np.float32).reshape(height, width)
    green = np.frombuffer(greenstr, dtype=np.float32).reshape(height, width)
    blue = np.frombuffer(bluestr, dtype=np.float32).reshape(height, width)

    if clip: 
        red = np.clip(red, 0, 1)
        green = np.clip(green, 0, 1)
        blue = np.clip(blue, 0, 1)

    # Combine the channels into a single numpy array
    img = np.stack([red, green, blue], axis=-1)

    return img

def load_image_to_qimage(image_path):

    # Check if the file is a RAW file by its extension
    if any(image_path.lower().endswith(ext[1:]) for ext in raw_extensions):
        try:
            # Handle RAW files
            with rawpy.imread(image_path) as raw:
                # Postprocess and get the image data as a numpy array
                rgb_image = raw.postprocess()
            # Convert the image to a format that QImage can handle
            height, width, colors = rgb_image.shape
            bytes_per_line = 3 * width
            image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        except Exception as e:
            print(f"Failed to load RAW image: {e}")
            return None
    elif any(image_path.lower().endswith(ext[1:]) for ext in exr_extensions):
        try:
            # Handle EXR image formats
            rgb_image = exr_to_numpy(image_path, clip=True)
            # Values are clipped between 0..1 to deal with overexposed areas. Multiply so we get channel values of 0..255 to show the RGB image: 
            rgb_image = np.uint8(rgb_image * 255)
            height, width, colors = rgb_image.shape
            bytes_per_line = 3 * width
            image = QImage(rgb_image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        except Exception as e:
            print(f"Failed to load image: {e}")
            return None
    else:
        try:
            # Handle standard image formats
            image = QImage(image_path)
        except Exception as e:
            print(f"Failed to load image: {e}")
            return None

    if image.isNull():
        print("Unable to load image.")
        return None

    return image

def apply_lut_global(image, lut, channel):
    channel_list = ["Luminance", "Red", "Green", "Blue"]
    
    if channel not in channel_list:
        raise ValueError(f"Option must be one of {channel_list}")

    if channel == "Luminance":
        # Convert to HSV, apply LUT to the V channel, convert back to RGB
        hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        hsv_image[:, :, 2] = cv2.LUT(hsv_image[:, :, 2], lut)
        return cv2.cvtColor(hsv_image, cv2.COLOR_HSV2RGB)
    else:
        # Apply the LUT to the respective RGB channel
        [channel_red, channel_green, channel_blue] = cv2.split(image)
        if channel == "Red":
            channel_red = cv2.LUT(channel_red, lut)  # Red channel in OpenCV is index 2
        elif channel == "Green":
            channel_green = cv2.LUT(channel_green, lut)  # Green channel is index 1
        elif channel == "Blue":
            channel_blue = cv2.LUT(channel_blue, lut)  # Blue channel is index 0
        return cv2.merge((channel_red, channel_green, channel_blue))


def apply_lut_local(image, lut_1, lut_2, channels, mask):
    channel_list = ["Luminance", "Red", "Green", "Blue"]
    
    if channels not in channel_list:
        raise ValueError(f"Option must be one of {channel_list}")

    # Ensure mask values are within [0, 1]
    mask = np.clip(mask/255.0, 0, 1)

    if channels == "Luminance":
        # Convert to HSV, interpolate LUT for the V channel, convert back to RGB
        hsv_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        v_channel = hsv_image[:, :, 2]
        output_channel = np.zeros_like(v_channel, dtype=np.uint8)
        
        # Applying LUTs based on the mask
        for i in range(256):
            use_lut_1 = lut_1[i] * (1 - mask)
            use_lut_2 = lut_2[i] * mask
            output_channel[v_channel == i] = (use_lut_1 + use_lut_2)[v_channel == i]
        
        hsv_image[:, :, 2] = output_channel
        return cv2.cvtColor(hsv_image, cv2.COLOR_HSV2RGB)
    else:
        # Apply the LUT to the respective RGB channel
        # output_image = np.zeros_like(image, dtype=np.uint8)
        [channel_red, channel_green, channel_blue] = cv2.split(image)
        
        # Interpolate LUT application for each channel
        channel_map = {
            "Red": 0,
            "Green": 1,
            "Blue": 2
        }
        selected_channel_index = channel_map[channels]
        selected_channel = [channel_red, channel_green, channel_blue][selected_channel_index]
        
        output_channel = np.zeros_like(selected_channel, dtype=np.uint8)
        
        for i in range(256):
            use_lut_1 = lut_1[i] * (1 - mask)
            use_lut_2 = lut_2[i] * mask
            output_channel[selected_channel == i] = (use_lut_1 + use_lut_2)[selected_channel == i]
        
        output_image = cv2.merge((channel_red, channel_green, channel_blue))
        output_image[:, :, selected_channel_index] = output_channel
        return output_image


