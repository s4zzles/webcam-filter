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


# optimized for real time filtering
# instead of calculating 4 means and variances of the quadrants for each pixel
# the algorithm shifts the image in the 4 direction and calculates means and vari
# on those shifted images
def kuwahara(img, k_size=5):
    # kernel size must be odd
    assert k_size % 2 == 1
    r = k_size // 2 # r = size of quadrant
    img = img.astype(np.float32)

    # shift helper function
    # shifts img in the direction (dy, dx)
    def shift(img, dy, dx):
        # pure translation matrix (no warp, scale, rotate)
        matrix = np.float32([[1, 0, dx], [0, 1, dy]])
        return cv2.warpAffine(img, matrix, (img.shape[1], img.shape[0]),
                              borderMode=cv2.BORDER_REFLECT)

    # 4 shifted images representing the kernel quadrants
    nw_quad = shift(img, -r, -r)
    ne_quad = shift(img, -r, r)
    sw_quad = shift(img, r, -r)
    se_quad = shift(img, r, r)

    # helper function for mean and variance calculation
    def calc_mean_variance(img, k_size):
        mean = cv2.blur(img, ksize=(k_size, k_size))
        mean_sq = cv2.blur(img * img, ksize=(k_size, k_size))
        vari = mean_sq - mean * mean
        return mean, vari

    nw_m, nw_v = calc_mean_variance(nw_quad, k_size)
    ne_m, ne_v = calc_mean_variance(ne_quad, k_size)
    sw_m, sw_v = calc_mean_variance(sw_quad, k_size)
    se_m, se_v = calc_mean_variance(se_quad, k_size)

    
    # stack variances and get the index of the lowest variance
    vari_stack = np.stack([nw_v, ne_v, sw_v, se_v], axis=-1)
    index = np.argmin(vari_stack, axis=-1)

    # stack means
    mean_stack = np.stack([nw_m, ne_m, sw_m, se_m], axis=-1)

    h, w = img.shape[:2]
    out = np.zeros((h, w, 3), dtype=np.float32)

    # create a mask for each of the 4 images to choose the
    # mean of the image with the lowest varicance in that area 
    for i in range(4):
        mask = (index == i)
        out += mean_stack[..., i] * mask

    return np.clip(out, 0, 255).astype(np.uint8)