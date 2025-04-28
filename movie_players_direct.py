# Author(s): Dr. Patrick Lemoine

import tkinter as tk
#from tkinter import ttk, filedialog
import cv2
import os
import pygame
#import threading
#import time
from PIL import Image, ImageTk
import sys

class VideoPlayer:
    def __init__(self, master, video_path=None):
        self.master = master
        self.video_path  = video_path
        self.audio_path = None
        self.pygame_initialized = False
        self.paused = False
        self.current_frame = 0
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
            self.pause_button["state"] = "normal"
            self.capture_button["state"] = "normal"
            self.prev_frame_button["state"] = "normal"
            self.next_frame_button["state"] = "normal"
            self.master.after(100, self.play)
  
        
    def initialize_pygame(self):
        if not self.pygame_initialized:
            pygame.init()
            try:
                pygame.mixer.init()
                self.pygame_initialized = True
                print("Pygame and mixer initialized successfully.")
            except pygame.error as e:
                print(f"Error initializing Pygame mixer: {e}")
                
                
    def setup_ui(self):     
        self.master.config(bg="#333333") 
        
        self.canvas = tk.Label(self.master, bg="#333333")
        self.canvas.pack(fill="both", expand=True)  

        self.slider = tk.Scale(self.master, from_=0, to=100, orient="horizontal", command=self.slider_changed, bg="#444444", fg="white")
        self.slider.pack(fill="x")

        button_frame = tk.Frame(self.master)
        button_frame.pack()

        self.select_video_button = tk.Button(button_frame, text="Select video", command=self.select_video, bg="#444444", fg="white")
        self.select_video_button.pack(side="left")

        self.play_button = tk.Button(button_frame, text="Play", command=self.play, state="disabled", bg="#444444", fg="white")
        self.play_button.pack(side="left")

        self.pause_button = tk.Button(button_frame, text="Pause", command=self.pause, state="disabled", bg="#444444", fg="white")
        self.pause_button.pack(side="left")

        self.capture_button = tk.Button(button_frame, text="Capture", command=self.capture_frame, state="disabled", bg="#444444", fg="white")
        self.capture_button.pack(side="left")
        
        self.prev_frame_button = tk.Button(button_frame, text="Previous", command=self.prev_frame, state="disabled", bg="#444444", fg="white")
        self.prev_frame_button.pack(side="left")

        self.next_frame_button = tk.Button(button_frame, text="Next", command=self.next_frame, state="disabled", bg="#444444", fg="white")
        self.next_frame_button.pack(side="left")
        
        self.exit_button = tk.Button(button_frame, text="Exit", command=self.exit_app, bg="#444444", fg="white")
        self.exit_button.pack(side="left") 
        self.master.resizable(True, True)
        
        


    def select_video(self):
        self.video_path = filedialog.askopenfilename(filetypes=[("Files video", "*.mp4 *.avi *.mov *.webm")])
        if self.video_path:
            self.play_button["state"] = "normal"
            self.pause_button["state"] = "normal"
            self.capture_button["state"] = "normal"
            self.prev_frame_button["state"] = "normal"
            self.next_frame_button["state"] = "normal"

    def play(self):
        self.paused = False
        if (self.current_frame == 0):
            if not self.pygame_initialized:
                self.initialize_pygame()
            self.cap = cv2.VideoCapture(self.video_path)
            self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            self.fps = self.cap.get(cv2.CAP_PROP_FPS)
            self.slider.config(to=self.total_frames - 1)
        self.update_frame()

    def pause(self):
        if self.paused:
            self.paused=False
            self.update_frame()
        else:
            self.paused=True

    def update_frame(self):
        if not self.paused:
            ret, frame = self.cap.read()
            if ret:
                width = self.master.winfo_width()
                height = self.master.winfo_height()-100
                aspect_ratio = frame.shape[1] / frame.shape[0]
                new_width = int(height * aspect_ratio)
                if new_width > width:
                    new_width = width
                    new_height = int(width / aspect_ratio)
                else:
                    new_height = height
                
                frame = cv2.resize(frame, (new_width, new_height))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.canvas.config(image=photo)
                self.canvas.image = photo
                
                self.slider.set(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)))
                self.master.after(int(1000/self.fps), self.update_frame)  
                self.current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            else:
                self.cap.release()
                
                
    def next_frame(self):
        if self.cap:
            self.paused = True
            ret, frame = self.cap.read()
            if ret:
                width = self.master.winfo_width()
                height = self.master.winfo_height()-100
                aspect_ratio = frame.shape[1] / frame.shape[0]
                new_width = int(height * aspect_ratio)
                if new_width > width:
                    new_width = width
                    new_height = int(width / aspect_ratio)
                else:
                    new_height = height
                
                frame = cv2.resize(frame, (new_width, new_height))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.canvas.config(image=photo)
                self.canvas.image = photo
                
                self.slider.set(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)))
                self.current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

    def prev_frame(self):
        if self.cap:
            self.paused = True
            current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
            if current_frame > 0:
                self.cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame - 3)
                ret, frame = self.cap.read()
                if ret:
                    width = self.master.winfo_width()
                    height = self.master.winfo_height()-100
                    aspect_ratio = frame.shape[1] / frame.shape[0]
                    new_width = int(height * aspect_ratio)
                    if new_width > width:
                        new_width = width
                        new_height = int(width / aspect_ratio)
                    else:
                        new_height = height
                    
                    frame = cv2.resize(frame, (new_width, new_height))
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                    self.canvas.config(image=photo)
                    self.canvas.image = photo
                    
                    self.slider.set(int(self.cap.get(cv2.CAP_PROP_POS_FRAMES)))
                    self.current_frame = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))

    def slider_changed(self, value):
        if self.cap:
            frame_number = int(float(value))
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = self.cap.read()
            if ret:
                width = self.master.winfo_width()
                height = self.master.winfo_height()-100
                aspect_ratio = frame.shape[1] / frame.shape[0]
                new_width = int(height * aspect_ratio)
                if new_width > width:
                    new_width = width
                    new_height = int(width / aspect_ratio)
                else:
                    new_height = height
                
                frame = cv2.resize(frame, (new_width, new_height))
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                photo = ImageTk.PhotoImage(image=Image.fromarray(frame))
                self.canvas.config(image=photo)
                self.canvas.image = photo

            
    def capture_frame(self):
        if self.cap:
            ret, frame = self.cap.read()
            if ret:
                if not os.path.exists("captures"):
                    os.makedirs("captures")
                video_name = os.path.splitext(os.path.basename(self.video_path))[0]
                frame_number = int(self.cap.get(cv2.CAP_PROP_POS_FRAMES))
                cv2.imwrite(f"captures/{video_name}_frame_{frame_number}.jpg", frame)
                print(f"Frame {frame_number} captured and saved.")
                
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

