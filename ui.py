import tkinter as tk
import datetime as dt
from PIL import Image, ImageTk
import cv2
import os

import capture
import pipeline


class UI:

    def __init__(self, root):
        self.root = root
        self.root.title("Webcam Filter")
        self.frame = None

        # UI elements

        self.webcam_label = tk.Label(root)
        self.webcam_label.pack()

        self.snap_button = tk.Button(root, text="Take Snapshot", command=self.on_snap_button_pressed)
        self.snap_button.pack()

        self.webcam_mirrored = tk.BooleanVar()
        self.mirror_switch = tk.Checkbutton(root, text="Mirror webcam", 
                                            variable=self.webcam_mirrored,
                                            onvalue=True, offvalue=False)
        self.mirror_switch.pack()

        self.brightness_slider = tk.Scale(root, label="Brightness", 
                                          from_=-100, to=100, 
                                          orient="horizontal")
        self.brightness_slider.set(0)
        self.brightness_slider.pack()

        self.contrast_slider = tk.Scale(root, label="Contrast", 
                                        from_=0.0, to=2.0, resolution=0.05, 
                                        orient="horizontal")
        self.contrast_slider.set(1.0)
        self.contrast_slider.pack()

        self.saturation_slider = tk.Scale(root, label="Saturation", 
                                          from_=0.0, to=2.0, resolution=0.05, 
                                          orient="horizontal")
        self.saturation_slider.set(1.0)
        self.saturation_slider.pack()

        self.hue_slider = tk.Scale(root, label="Hue", 
                                          from_=-180, to=180,
                                          orient="horizontal")
        self.hue_slider.set(0)
        self.hue_slider.pack()

        self.running = True

        # start camera refresh loop
        self.update_frame()

        # handle window close properly
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)



    def update_frame(self):
        if not self.running:
            return

        self.frame = pipeline.process_frame(
            mirrored=self.webcam_mirrored.get(),
            brightness_offset=self.brightness_slider.get(),
            contrast_strength=self.contrast_slider.get(),
            saturation_strength=self.saturation_slider.get(),
            hue_change=self.hue_slider.get()
        )

        if self.frame is not None:
            rgb_frame = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)

            # Convert to PIL image
            img = Image.fromarray(rgb_frame)

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
        if self.frame is not None:
            now = dt.datetime.now()
            file_name = "snapshot_" + now.strftime("%y%m%d%H%M%S") + ".png"

            if not os.path.exists("./snapshots"):
                os.mkdir("./snapshots")

            cv2.imwrite("./snapshots/" + file_name, self.frame)


if __name__ == "__main__":
    root = tk.Tk()
    app_ui = UI(root)
    root.mainloop()