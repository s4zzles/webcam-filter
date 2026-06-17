import cv2
import numpy as np
import mediapipe as mp

mp_selfie = mp.solutions.selfie_segmentation
segmenter = mp_selfie.SelfieSegmentation(model_selection=1)


def mirror(img):
    return cv2.flip(img, 1)

# Color adjustment methods

def brightness(img, brightness_offset):
    # additive brightness offset
    return np.clip(img.astype(np.int16) + brightness_offset, 0, 255).astype(np.uint8)


def contrast(img, contrast_strength):
    return np.clip(128 + ((img.astype(np.int16)-128) * contrast_strength), 0, 255).astype(np.uint8)
    

def saturation(img, saturation_strength):
    # create grayscale base with luminance weights
    gray = (
        img[..., 0] * 0.0722 +
        img[..., 1] * 0.7152 +
        img[..., 2] * 0.2126
    )
    # restore original format of grayscale
    gray = np.stack([gray, gray, gray], axis=2)

    # calculate color difference
    color = (img.astype(np.int16) - gray) * saturation_strength
    
    return np.clip(gray + color, 0, 255).astype(np.uint8)


def hue(img, hue_change):
    hue_change = hue_change / 2.0
    hsv_image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # add hue_change offset to hue while ensuring wraparound
    h = hsv_image[..., 0].astype(np.float32) 
    h = (h + hue_change) % 180 
    hsv_image[..., 0] = h.astype(np.uint8)

    return cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)



# Filter methods
def create_mask(img):
    # get segmentation mask from rgb
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = segmenter.process(rgb)
    mask = result.segmentation_mask
    return np.stack((mask, mask, mask), axis=2)


def blur_bg(img, blur_strength):

    mask = create_mask(img)

    # ensure input is odd (required for kernel size)
    if blur_strength % 2 == 0:
        blur_strength += 1

    # blur entire image
    blurred_img = cv2.GaussianBlur(img, (blur_strength, blur_strength), 0)

    # blends foreground(mask) with background(1-mask)
    return (img * mask + blurred_img * (1 - mask)).astype(np.uint8)



def kuwahara(img, kernel_size):
    return img