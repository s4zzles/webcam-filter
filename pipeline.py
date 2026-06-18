import cv2
import numpy as np

import capture
import filters


def process_frame(mirrored:bool, 
                  brightness_offset:int, 
                  contrast_strength:float, 
                  saturation_strength:float,
                  hue_change:int,
                  filter_mode:str,
                  blur_strength:int,
                  kuwahara_ksize:int):
                
    frame = capture.get_frame()

    if frame is None:
        return

    if mirrored:
        frame = filters.mirror(frame)
     

    frame = filters.brightness(frame, brightness_offset)
    frame = filters.contrast(frame, contrast_strength)
    frame = filters.saturation(frame, saturation_strength)
    frame = filters.hue(frame, hue_change)

    match filter_mode:
        case "Blur Background":
            frame = filters.blur_bg(frame, blur_strength)

        case "Kuwahara":
            frame = filters.kuwahara(frame, kuwahara_ksize)

    scaled_frame = fit_to_canvas(frame, 640, 480)
    rgb_frame = cv2.cvtColor(scaled_frame, cv2.COLOR_BGR2RGB)
   
    return rgb_frame


def fit_to_canvas(img, target_width, target_height):
    height, width = img.shape[:2]
    # determine which side's scale to use
    scale = min((target_width / width), (target_height / height))
    scaled_width = int(width * scale)
    scaled_height = int(height * scale)
    scaled_img = cv2.resize(img, (scaled_width, scaled_height))

    # if aspect ratio is different use letterboxes/pillarboxes
    canvas = np.zeros((target_height, target_width, 3), 
                    dtype=np.uint8)

    x_pos = int((target_width - scaled_width) / 2)
    y_pos = int((target_height - scaled_height) / 2)

    canvas[y_pos:y_pos+scaled_height, x_pos:x_pos+scaled_width] = scaled_img

    return canvas
