import cv2
import numpy as np


def mirror(img):
    return cv2.flip(img, 1)

# Color adjustment methods

def brightness(img, brightness_offset):
    return np.clip(img.astype(np.int16) + brightness_offset, 0, 255).astype(np.uint8)


def contrast(img):
    pass


def saturation(img):
    pass


def temperature(img):
    pass


# Filter methods

def blur_bg(img):
    pass


def kuwahara(img):
    pass