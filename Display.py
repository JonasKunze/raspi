from picamera import PiCamera
import io
import time
import numpy as np


from PIL import Image
from time import sleep

class Display(PiCamera):
    def __init__(self, size):
        PiCamera.__init__(self) 
        self.size = size
        self.resolution = size 
        self.framerate = 25 
        self.rotation = -90
        self.hflip = True
        self.foreground = 2
        self.background = 1
        self.overlay = None

        self.small_window = (0, 0, 640, 480)

    def start_preview(self):
        if self.previewing == False:
            super(Display, self).start_preview()
            self.preview.layer = 10

    def show_video_fullscreen(self):
        self.start_preview()
        self.preview.fullscreen = True
        self.preview.layer = self.background

    def show_video_small(self):
        self.start_preview()
        self.preview.fullscreen = True
        self.preview.layer = self.foreground
        self.preview.fullscreen = False
        self.preview.window = self.small_window 

    def hide_video(self):
        super(Display, self).stop_preview()

    def show_image_fullscreen(self, image):
        if self.previewing == True:
            self.show_video_small()
        self.show_image(image)
        self.overlay.layer = self.background 

    def show_image_small(self, image):
        if self.previewing == True:
            self.show_video_fullscreen()
        self.show_image(image)
        self.overlay.layer = self.foreground 
        self.overlay.fullscreen = False
        self.overlay.window = (100, 100, 640, 480)

    def show_image(self, image):
        if self.overlay is not None:
            self.remove_overlay(self.overlay)

        pad = image
        # make sure the image has the right size and is in RGB mode
        pad = Image.new("RGB", (
            ((img.size[0] + 31) // 32) * 32,
            ((img.size[1] + 15) // 16) * 16,
            ))
        pad.paste(img, (0, 0))

        self.overlay = self.add_overlay(pad.tostring(), image.size)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        print("Shutting down the Display")
        super(Display, self).__exit__(exc_type, exc_value, traceback)



with Display((1680, 1050)) as camera:

    # Load the arbitrarily sized image
    img = Image.open('overlay.png')

    camera.show_video_fullscreen()
    camera.show_image_fullscreen(img)
    camera.stop_preview()
    camera.show_image_small(img)
    camera.show_video_small()
    camera.show_video_fullscreen()
    try:
        while True:
            time.sleep(2)
    except KeyboardInterrupt, SystemExit:
        print("Closing app")
