import tkinter as tk
from tkinter import ttk

import threading
import datetime as dt
import numpy as np
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
        self.update_id = None # not None if a camera update loop is currently active


        # UI elements

        # Top frame (shows camera and controls)
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(anchor="n", fill=tk.X, padx=10, pady=10)

        # webcam canvas
        self.webcam_frame = tk.Frame(self.top_frame, width=640, height=480)
        self.webcam_frame.pack()
        self.webcam_frame.pack_propagate(False) # keeps size constant

        self.webcam_label = tk.Label(self.webcam_frame, text="Camera Off",
                                     bg="gray", fg="white",
                                     font=("Arial", 22))
        self.webcam_label.pack(fill="both", expand=True)

        # cam controls
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


        # Bottom frame (2 columns: left is color adj, right is filters)
        self.bottom_frame = tk.Frame(root)
        self.bottom_frame.pack(anchor="s", fill=tk.X, padx=10, pady=10)

        self.bottom_frame.columnconfigure(0, weight=1)
        self.bottom_frame.columnconfigure(1, weight=1)
        self.bottom_frame.rowconfigure(0, weight=1)

        # Color adjustments
        self.color_adj_frame = tk.Frame(self.bottom_frame)
        self.color_adj_frame.grid(column=0, row=0, padx=10, sticky="nsew")

        self.color_adj_label = tk.Label(self.color_adj_frame, 
                                        text="Color adjustments", 
                                        font="Arial 10 bold")
        self.color_adj_label.pack(side="top", fill=tk.X)

        self.brightness_slider = tk.Scale(self.color_adj_frame, label="Brightness", 
                                          from_=-100, to=100, 
                                          orient="horizontal")
        self.brightness_slider.set(0)
        self.brightness_slider.pack(fill=tk.X)

        self.contrast_slider = tk.Scale(self.color_adj_frame, label="Contrast", 
                                        from_=0.0, to=2.0, resolution=0.05, 
                                        orient="horizontal")
        self.contrast_slider.set(1.0)
        self.contrast_slider.pack(fill=tk.X)

        self.saturation_slider = tk.Scale(self.color_adj_frame, label="Saturation", 
                                          from_=0.0, to=2.0, resolution=0.05, 
                                          orient="horizontal")
        self.saturation_slider.set(1.0)
        self.saturation_slider.pack(fill=tk.X)

        self.hue_slider = tk.Scale(self.color_adj_frame, label="Hue", 
                                          from_=-180, to=180,
                                          orient="horizontal")
        self.hue_slider.set(0)
        self.hue_slider.pack(fill=tk.X)


        # Filters
        self.filter_frame = tk.Frame(self.bottom_frame)
        self.filter_frame.grid(column=1, row=0, padx=10, sticky="nsew")

        self.filter_label = tk.Label(self.filter_frame, 
                                        text="Filters", 
                                        font="Arial 10 bold")
        self.filter_label.pack(side="top", fill=tk.X)


        self.filter_var = tk.StringVar()
        self.blur_var = tk.IntVar()
        self.kuwahara_var = tk.IntVar(value=5)

        self.filter_dropdown = ttk.Combobox(self.filter_frame,
                                            textvariable=self.filter_var,
                                            state="readonly")

        self.filter_dropdown["values"] = ["None", 
                                          "Blur Background",
                                          "Kuwahara"]
        self.filter_dropdown.current(0)

        self.filter_dropdown.pack(fill=tk.X, pady=30)
        self.filter_dropdown.bind("<<ComboboxSelected>>", self.on_filter_change)

        self.filter_options_frame = tk.Frame(self.filter_frame)
        self.filter_options_frame.pack(fill=tk.BOTH, expand=True)

        self.on_filter_change("None") # to display the correct menu on start up



        # handle window close properly
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)


    def on_filter_change(self, event=None):
        # remove old widgets
        for widget in self.filter_options_frame.winfo_children():
            widget.destroy()

        selected = self.filter_var.get()

        if selected == "None":
            tk.Label(self.filter_options_frame, text="No filter selected").pack()

        elif selected == "Blur Background":
            tk.Scale(self.filter_options_frame, from_=0, to=100, 
                    label="Blur strength", variable=self.blur_var,
                    orient="horizontal").pack(fill=tk.X)
            
 
        elif selected == "Kuwahara":
            tk.Label(self.filter_options_frame, text="Kernel size:").pack()
            tk.Radiobutton(self.filter_options_frame, text="5x5", value=5,
                           variable=self.kuwahara_var).pack()
            tk.Radiobutton(self.filter_options_frame, text="7x7", value=7,
                           variable=self.kuwahara_var).pack()
            tk.Radiobutton(self.filter_options_frame, text="9x9", value=9,
                           variable=self.kuwahara_var).pack()



    def update_image(self):
        if not self.running or not self.capturing:
            return

        self.image = pipeline.process_frame(
            mirrored=self.webcam_mirrored.get(),
            brightness_offset=self.brightness_slider.get(),
            contrast_strength=self.contrast_slider.get(),
            saturation_strength=self.saturation_slider.get(),
            hue_change=self.hue_slider.get(),
            filter_mode=self.filter_var.get(),
            blur_strength=self.blur_var.get(),
            kuwahara_ksize=self.kuwahara_var.get()
        )

        if self.image is not None:
            scaled_image = self.fit_to_canvas(self.image, 640, 480)
            rgb_image = cv2.cvtColor(scaled_image, cv2.COLOR_BGR2RGB)

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

    def on_close(self):
        self.running = False

        if self.update_id is not None:
            self.root.after_cancel(self.update_id)
        if self.capturing:
            capture.release()
        self.root.destroy()


    def start_camera_thread(self):
        try:
            capture.start()
            # after method ensures it runs outside of this thread
            self.root.after(0, self.camera_started)

        except Exception as e:
            # reenable button if sth fails
            self.root.after(0, lambda: self.cam_button.config(
                            state="normal", text="Start camera"))
            print(e)

    def camera_started(self):
        self.capturing = True
        self.update_image()
        self.cam_button.config(state="normal", text="Stop camera")

    def on_cam_button_pressed(self):
        if not self.capturing:
            self.cam_button.config(state="disabled", text="Starting...")
            threading.Thread(target=self.start_camera_thread, daemon=True).start()
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
    root.resizable(False, False)
    root.mainloop()