import tkinter as tk
import ui

if __name__ == "__main__":
    root = tk.Tk()
    app_ui = ui.UI(root)
    root.resizable(False, False)
    root.mainloop()