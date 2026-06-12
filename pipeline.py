import capture
import filters


def process_frame(mirrored:bool, 
                  brightness_offset:int, 
                  contrast_strength:float, 
                  saturation_strength:float):
    frame = capture.get_frame()

    if frame is None:
        return

    if mirrored:
        frame = filters.mirror(frame)

    frame = filters.brightness(frame, brightness_offset)
    frame = filters.contrast(frame, contrast_strength)
    frame = filters.saturation(frame, saturation_strength)

    return frame
