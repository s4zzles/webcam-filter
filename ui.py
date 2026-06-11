import tkinter as tk
from PIL import Image, ImageTk
import cv2

import capture
import pipeline


class UI:
    def __init__(self, root):
        self.root = root
        self.root.title("Webcam Filter")

        # UI element to display video
        self.webcam_label = tk.Label(root)
        self.webcam_label.pack()

        self.snap_button = tk.Button(root, text="Take Snapshot", command=self.on_snap_button_pressed)
        self.snap_button.pack()

        self.webcam_mirrored = tk.BooleanVar()
        self.mirror_switch = tk.Checkbutton(root, text="Mirror webcam", 
                                            variable=self.webcam_mirrored,
                                            onvalue=True, offvalue=False)
        self.mirror_switch.pack()

        self.brightness_label = tk.Label(root, text="Brightness")
        self.brightness_label.pack()
        self.brightness_slider = tk.Scale(root, from_=-100, to=100, orient="horizontal")
        self.brightness_slider.set(0)
        self.brightness_slider.pack()

        self.running = True

        # start camera refresh loop
        self.update_frame()

        # handle window close properly
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_frame(self):
        if not self.running:
            return

        frame = pipeline.process_frame(
            mirrored=self.webcam_mirrored.get(),
            brightness_offset=self.brightness_slider.get()
        )

        if frame is not None:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert to PIL image
            img = Image.fromarray(frame)

            # Convert to Tkinter image
            imgtk = ImageTk.PhotoImage(image=img)

            # Update webcam label
            self.webcam_label.temp_ref = imgtk   # prevent garbage collection of imgtk
            self.webcam_label.configure(image=imgtk)

        # restart camera refresh loop (results in abt. 30fps refresh rate)
        self.root.after(15, self.update_frame)

    def on_close(self):
        self.running = False
        capture.release()
        self.root.destroy()

    def on_snap_button_pressed(self):
        print("af")


if __name__ == "__main__":
    root = tk.Tk()
    app_ui = UI(root)
    root.mainloop()