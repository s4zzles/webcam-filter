import cv2

capture = cv2.VideoCapture(0)
width = int(capture.get(3))
height = int(capture.get(4))

if not capture.isOpened():
    raise RuntimeError("Could not open webcam")

def get_frame():
    ret, frame = capture.read()

    if not ret:
        return None
    
    return frame


def release() -> None:
    capture.release()
