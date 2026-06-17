import cv2

capture = None



def start() -> None:
    global capture 
    capture = cv2.VideoCapture(0)

    if not capture.isOpened():
        raise RuntimeError("Could not open webcam")

def get_frame():
    ret, frame = capture.read()

    if not ret:
        return None
    
    return frame


def release() -> None:
    capture.release()
