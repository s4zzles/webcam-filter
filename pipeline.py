import capture
import filters


def process_frame(mirrored:bool, brightness_offset:int):
    frame = capture.get_frame()

    if frame is None:
        return

    if mirrored:
        frame = filters.mirror(frame)

    frame = filters.brightness(frame, brightness_offset)

    return frame


if __name__ == "__main__":
    process_frame(True, 0)