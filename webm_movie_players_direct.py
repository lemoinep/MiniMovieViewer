import tkinter as tk
from tkinter import filedialog
from tkvideo import tkvideo
import cv2
import os
from PIL import ImageGrab
import numpy as np
import sys

class VideoPlayer:
    def __init__(self, master, video_path=None):
        self.master = master
        self.video_path = video_path
        self.player = None
        self.setup_ui()
        self.master.resizable(True, True)
        self.master.overrideredirect(1)  
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        self.master.geometry(f"{screen_width}x{screen_height}") 
        self.capture_count = 0  
        self.master.bind("<Escape>", self.exit_app_key)  

        if self.video_path:
            self.play_button["state"] = "normal"
            self.capture_button["state"] = "normal"
            self.crop_button["state"] = "normal"
            self.master.after(100, self.play) 

    def setup_ui(self):
        self.master.config(bg="#333333")  
        
        self.video_label = tk.Label(self.master, bg="#333333") 
        self.video_label.pack(fill="both", expand=True)  

        button_frame = tk.Frame(self.master, bg="#333333")  
        button_frame.pack()

        self.select_video_button = tk.Button(button_frame, text="Sélectionner vidéo", command=self.select_video, bg="#444444", fg="white")
        self.select_video_button.pack(side="left")

        self.play_button = tk.Button(button_frame, text="Play", command=self.play, state="disabled", bg="#444444", fg="white")
        self.play_button.pack(side="left")

        self.capture_button = tk.Button(button_frame, text="Capture fenêtre", command=self.capture_window, state="disabled", bg="#444444", fg="white")
        self.capture_button.pack(side="left")

        self.crop_button = tk.Button(button_frame, text="Crop Image", command=self.crop_image, state="disabled", bg="#444444", fg="white")
        self.crop_button.pack(side="left")

        self.exit_button = tk.Button(button_frame, text="Exit", command=self.exit_app, bg="#444444", fg="white")
        self.exit_button.pack(side="left")  
        
        #self.master.resizable(True, True)
         

    def select_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("Fichiers vidéo", "*.mp4 *.avi *.mov *.webm")])
        if self.video_path:
            self.play_button["state"] = "normal"
            self.capture_button["state"] = "normal"
            self.crop_button["state"] = "normal"

    def play(self):
        self.master.update_idletasks() 
        width = self.master.winfo_width()
        height = self.master.winfo_height() - 50
        
        if width > 0 and height > 0:
            aspect_ratio = 16 / 9 
            new_width = int(height * aspect_ratio)
            if new_width > width:
                new_width = width
                new_height = int(width / aspect_ratio)
            else:
                new_height = height
            size = (new_width, new_height)
        else:
            size = (640, 480)  
        
        self.player = tkvideo(self.video_path, self.video_label, loop=1, size=size)
        self.player.play()

    def capture_window(self):
        x = self.master.winfo_rootx()
        y = self.master.winfo_rooty()
        x1 = x + self.master.winfo_width()
        y1 = y + self.master.winfo_height()
        
        if not os.path.exists("captures"):
            os.makedirs("captures")
        
        ImageGrab.grab(bbox=(x, y, x1, y1)).save(f"captures/window_capture_{self.capture_count}.jpg")
        print(f"Capture de la fenêtre {self.capture_count} sauvegardée.")
        self.capture_count += 1

    def crop_image(self):
        x = self.master.winfo_rootx()
        y = self.master.winfo_rooty()
        x1 = x + self.master.winfo_width()
        y1 = y + self.master.winfo_height()
        
        img = ImageGrab.grab(bbox=(x, y, x1, y1))
        
        img_np = np.array(img)
        

        img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)
        

        crop_x_start = 100   
        crop_y_start = 100   
        crop_width = img_np.shape[1] - 200  
        crop_height = img_np.shape[0] - 200  


        if crop_x_start + crop_width > img_np.shape[1]:
            crop_width = img_np.shape[1] - crop_x_start
        if crop_y_start + crop_height > img_np.shape[0]:
            crop_height = img_np.shape[0] - crop_y_start
        
        cropped_img = img_bgr[crop_y_start:crop_y_start + crop_height, crop_x_start:crop_x_start + crop_width]
        
        if not os.path.exists("captures"):
            os.makedirs("captures")
        
        cv2.imwrite(f"captures/cropped_image_{self.capture_count}.jpg", cropped_img)
        print(f"Image découpée {self.capture_count} sauvegardée.")
        self.capture_count += 1
        
    def exit_app(self):
        self.master.destroy()

    def exit_app_key(self, event):
        self.master.destroy()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        video_path = None

    root = tk.Tk()
    player = VideoPlayer(root, video_path)
    root.mainloop()
