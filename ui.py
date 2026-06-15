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

        self.image = None

        self.running = True # flag if the app is currently running
        self.capturing = False # flag if the camera currently being captured

        self.update_id = None # not None if an camera update loop is currently active

        # UI elements

        # Top frame

        self.top_frame = tk.Frame(root, bg="yellow")
        self.top_frame.pack(anchor="n", fill=tk.X, padx=10, pady=10)

        self.webcam_frame = tk.Frame(self.top_frame, bg="gray", width=640, height=480)
        self.webcam_frame.pack()
        self.webcam_frame.pack_propagate(False)

        self.webcam_label = tk.Label(self.webcam_frame, text="Camera Off",
                                     bg="gray", fg="white",
                                     font=("Arial", 22))
        self.webcam_label.pack(fill="both", expand=True)

        self.cam_ctrl_frame = tk.Frame(self.top_frame)
        self.cam_ctrl_frame.pack(fill=tk.X, pady=5)

        self.cam_ctrl_frame.columnconfigure(0, weight=1)
        self.cam_ctrl_frame.columnconfigure(1, weight=1)
        self.cam_ctrl_frame.columnconfigure(2, weight=1)

        self.cam_button = tk.Button(self.cam_ctrl_frame, text="Start camera",
                                    command=self.on_cam_button_pressed)
        self.cam_button.grid(column=0, row=0, padx=20, sticky="ew")

        self.snap_button = tk.Button(self.cam_ctrl_frame, text="Take Snapshot", 
                                    command=self.on_snap_button_pressed)
        self.snap_button.grid(column=1, row=0, padx=20, sticky="ew")

        self.webcam_mirrored = tk.BooleanVar()
        self.mirror_switch = tk.Checkbutton(self.cam_ctrl_frame, text="Mirror webcam", 
                                            variable=self.webcam_mirrored,
                                            onvalue=True, offvalue=False)
        self.mirror_switch.grid(column=2, row=0, padx=20)

        #Bottom frame

        self.bottom_frame = tk.Frame(root, bg="orange")
        self.bottom_frame.pack(anchor="s", fill=tk.X, padx=10, pady=10)

        self.bottom_frame.columnconfigure(0, weight=1)
        self.bottom_frame.columnconfigure(1, weight=1)


        self.color_adj_frame = tk.Frame(self.bottom_frame, bg="red")
        self.color_adj_frame.grid(column=0, row=0, padx=5, sticky="ew")

        self.brightness_slider = tk.Scale(self.color_adj_frame, label="Brightness", 
                                          from_=-100, to=100, 
                                          orient="horizontal")
        self.brightness_slider.set(0)
        self.brightness_slider.pack()

        self.contrast_slider = tk.Scale(self.color_adj_frame, label="Contrast", 
                                        from_=0.0, to=2.0, resolution=0.05, 
                                        orient="horizontal")
        self.contrast_slider.set(1.0)
        self.contrast_slider.pack()

        self.saturation_slider = tk.Scale(self.color_adj_frame, label="Saturation", 
                                          from_=0.0, to=2.0, resolution=0.05, 
                                          orient="horizontal")
        self.saturation_slider.set(1.0)
        self.saturation_slider.pack()

        self.hue_slider = tk.Scale(self.color_adj_frame, label="Hue", 
                                          from_=-180, to=180,
                                          orient="horizontal")
        self.hue_slider.set(0)
        self.hue_slider.pack()

        self.filter_frame = tk.Frame(self.bottom_frame, bg="green")
        self.filter_frame.grid(column=1, row=0, padx=5, sticky="ew")


        self.status_bar = tk.Label(text="This is a test", relief=tk.SUNKEN, anchor="w")
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, padx=2, pady=2)


        # handle window close properly
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)



    def update_image(self):
        if not self.running or not self.capturing:
            return

        self.image = pipeline.process_frame(
            mirrored=self.webcam_mirrored.get(),
            brightness_offset=self.brightness_slider.get(),
            contrast_strength=self.contrast_slider.get(),
            saturation_strength=self.saturation_slider.get(),
            hue_change=self.hue_slider.get()
        )

        if self.image is not None:
            #scaled_image = self.fit_to_canvas(self.image, 640, 480)
            rgb_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)

            # Convert to PIL image
            pil_image = Image.fromarray(rgb_image)

            # Convert to Tkinter image
            imgtk = ImageTk.PhotoImage(image=pil_image)

            # Update webcam label
            self.webcam_label.temp_ref = imgtk   # prevent garbage collection of imgtk
            self.webcam_label.configure(image=imgtk, text="")

        # restart camera refresh loop (results in abt. 30fps refresh rate)
        # update id gets set here for check if a loop is currently active
        self.update_id = self.root.after(15, self.update_image)

    def fit_to_canvas(self, img, target_width, target_height):
        pass # todo

    def on_close(self):
        self.running = False

        if self.update_id is not None:
            self.root.after_cancel(self.update_id)
        if self.capturing:
            capture.release()
        self.root.destroy()

    def on_cam_button_pressed(self):
        if not self.capturing:
            self.capturing = True
            capture.start()
            self.update_image()
            self.cam_button.config(text="Stop camera")
        else:
            capture.release()
            self.capturing = False
            # cancel the running loop
            if self.update_id is not None:
                self.root.after_cancel(self.update_id)
                self.update_id = None
            self.webcam_label.configure(image="", text="Camera Off", bg="gray")
            self.cam_button.config(text="Start camera")

    def on_snap_button_pressed(self):
        if self.image is not None:
            now = dt.datetime.now()
            file_name = "snapshot_" + now.strftime("%y%m%d%H%M%S") + ".png"

            if not os.path.exists("./snapshots"):
                os.mkdir("./snapshots")

            cv2.imwrite("./snapshots/" + file_name, self.image)


if __name__ == "__main__":
    root = tk.Tk()
    app_ui = UI(root)
    root.mainloop()