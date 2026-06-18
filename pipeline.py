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
   

    return frame
