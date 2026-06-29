A webcam filter app I built using OpenCV, MediaPipe and NumPy for image processing and filtering, TKinter for the UI and PyVirtualcam to use it as a webcam source in other programs.

<img width="662" height="846" alt="Screenshot 2026-06-24 131156" src="https://github.com/user-attachments/assets/32769efc-d000-4691-8c39-4e9ee6630072" />

Usage:

Start your webcam by pressing the "Start camera" button. It automatically selects your first webcam if it's not currently being used by another program.
You can take a snapshot by pressing the according button. Snapshots are saved in a directory called "snapshots" the program creates at the root.

Adjust your image by flipping or adjusting brightness, contrast, saturation and hue.
Furthermore, there are two filter options available:
Blur Background detects a person in the camera feed and blurs everything else using the Blur strength slider value.
Kuwahara uses a fast approximation of the classic Kuwahara filter that is viable for real time filtering. You can choose different kernel sizes to increase the size of the splotches.
