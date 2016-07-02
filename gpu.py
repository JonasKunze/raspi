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
    # Create an image padded to the required size with
    # mode 'RGB'
    pad = Image.new('RGB', (
        640,
        400,
        ))
    # Paste the original image into the padded one
    pad.paste(img, (0, 0))

    # Add the overlay with the padded image as the source,
    # but the original image's dimensions
    o = camera.add_overlay(pad.tostring(), size=(640, 400))
    # By default, the overlay is in layer 0, beneath the
    # preview (which defaults to layer 2). Here we make
    # the new overlay semi-transparent, then move it above
    # the preview
    o.alpha = 255 
    o.layer = 3
  
    while True:
        time.sleep(1)
 #       stream = io.BytesIO()
 #       print("capturing")
 #       camera.capture(stream, 'jpeg', resize=(640,400))
 #       stream.seek(0)
 #       print("pasting")
 #       img = Image.open(stream)
 #       pad = Image.new('RGB', (
 #           640,
 #           400,
 #       ))
 #       pad.paste(img, (0, 0))
 #       print("overlaying")
 #       camera.remove_overlay(o)
 #       o = camera.add_overlay(img.tostring(), size=(640, 400))
 #       o.alpha = 255 
 #       o.layer = 4
