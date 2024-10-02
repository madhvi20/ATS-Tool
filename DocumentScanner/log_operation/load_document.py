import numpy as np
import cv2

def resize_image(image, size=(800, 600)):
    """Resize image to specified size."""
    resized_image = cv2.resize(image, size)
    return resized_image

def adjust_brightness(image, factor=1.2):
    """Adjust brightness of the image."""
    bright_image = np.clip(image * factor, 0, 1)
    return bright_image
