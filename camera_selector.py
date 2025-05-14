import tkinter as tk
from tkinter import ttk
import cv2

def list_available_cameras(max_cameras=5):
    available = []
    for i in range(max_cameras):
        cap = cv2.VideoCapture(i)
        if cap is not None and cap.read()[0]:
            available.append(i)
        cap.release()
    return available

def select_camera_gui():
    selected_camera = [0]  

    def on_select():
        selected_camera[0] = int(combo.get())
        root.destroy()

    root = tk.Tk()
    root.title("Select Webcam")
    root.geometry("300x100")
    tk.Label(root, text="Choose a camera:").pack(pady=5)

    cameras = list_available_cameras()
    combo = ttk.Combobox(root, values=cameras, state="readonly")
    combo.current(0)
    combo.pack(pady=5)

    tk.Button(root, text="Select", command=on_select).pack(pady=5)
    root.mainloop()

    return selected_camera[0]