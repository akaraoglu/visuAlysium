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
from PyQt6.QtGui import QImage
from numpy.lib.stride_tricks import as_strided


def convertArrayToQImage(array):
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

def convertQImageToArray(image):
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

#Adjust Brightness

def color_brightness(image, brightness_factor):
    b, g, r = cv2.split(image)

    b = cv2.add(b, 255 * brightness_factor)
    g = cv2.add(g, 255 * brightness_factor)
    r = cv2.add(r, 255 * brightness_factor)

    b = np.clip(b, 0, 255)
    g = np.clip(g, 0, 255)
    r = np.clip(r, 0, 255)

    adjusted_image = cv2.merge((b, g, r))

    return np.asarray(adjusted_image, np.uint8)


# Adjust Contrast

# def adjust_contrast_brightness(image, alpha_amount, beta_amount):
#     """
#     Adjusts the contrast and brightness of an image.
    
#     :param image: Input image.
#     :param alpha_amount: Contrast adjustment factor. Values > 1 increase contrast, values between 0 and 1 decrease contrast.
#     :param beta_amount: Brightness adjustment factor. The value is added to each pixel after contrast adjustment.
#     :return: Image with adjusted contrast and brightness.
#     """

#     # Compute the original intensity range
#     min_val, max_val = image.min(), image.max()
    
#     # Compute the target range for contrast adjustment
#     target_min = (1 - alpha_amount) * min_val + alpha_amount * (255 * 0.25)
#     target_max = (1 - alpha_amount) * max_val + alpha_amount * (255 * 0.75)

#     # Vectorized computation of the lookup table for performance improvement
#     original_range = np.arange(256, dtype=np.float32)
#     adjusted_range = np.clip(((original_range - min_val) / (max_val - min_val) * (target_max - target_min) + target_min) + (beta_amount * 255), 0, 255).astype(np.uint8)
    
#     # Apply the lookup table
#     return cv2.LUT(image, adjusted_range)

def adjust_contrast_brightness(image, alpha_amount, beta_amount, gamma_amount):
    """
    Adjusts the contrast, brightness, and applies gamma correction to an image.
    
    :param image: Input image.
    :param alpha_amount: Contrast adjustment factor. Values > 1 increase contrast, values between 0 and 1 decrease contrast.
    :param beta_amount: Brightness adjustment factor. The value is added to each pixel after contrast adjustment.
    :param gamma_amount: Gamma correction factor. Values > 1 make the image darker, values < 1 make the image brighter.
    :return: Image with adjusted contrast, brightness, and gamma correction.
    """

    # Ensure alpha_amount is within a reasonable range
    alpha_amount = max(min(alpha_amount, 1), -1)
    
    # Ensure gamma_amount is positive
    gamma_amount = max(gamma_amount, 0.01)  # Avoid division by zero or negative values
    
    # Compute the original intensity range
    min_val, max_val = image.min(), image.max()
    
    # Compute the target range for contrast adjustment
    target_min = (1 - alpha_amount) * min_val + alpha_amount * (255 * 0.25)
    target_max = (1 - alpha_amount) * max_val + alpha_amount * (255 * 0.75)

    # Vectorized computation of the lookup table for performance improvement
    original_range = np.arange(256, dtype=np.float32) / 255  # Normalize to [0,1] for gamma correction
    # Apply gamma correction in the normalized space
    gamma_corrected = np.power(original_range, gamma_amount)
    # Adjust for contrast and brightness, then scale back to [0,255]
    adjusted_range = np.clip(((gamma_corrected - min_val / 255) / ((max_val - min_val) / 255) * (target_max - target_min) + target_min) + (beta_amount * 255), 0, 255).astype(np.uint8)
    
    # Apply the lookup table
    return cv2.LUT(image, adjusted_range)

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