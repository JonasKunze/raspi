import picamera
import io
import time
import numpy as np


from PIL import Image
from time import sleep

with picamera.PiCamera() as camera:
    camera.resolution = (1680, 1050)
    camera.framerate = 24
    camera.start_preview()
    camera.rotation = -90

    # Load the arbitrarily sized image
    img = Image.open('overlay.png')

    pad = Image.new("RGB", (
        ((img.size[0] + 31) // 32) * 32,
        ((img.size[1] + 15) // 16) * 16,
        ))
    pad.paste(img, (0, 0), img)

    o = camera.add_overlay(pad.tostring(), size=img.size)
    o.fullscreen = False
    o.window = (0, 0, 640, 480)
    o.alpha = 255 
    o.layer = 3
  
    try:
        while True:
            time.sleep(1)
    finally:
        camera.remove_overlay(o)
