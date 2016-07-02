import picamera
import picamera.array
import io
import time
import cv2
import numpy as np

import threading
import picamera
from PIL import Image


theGodArray = None

# Inherit from PiRGBAnalysis
class MyStream():
    def write(self, data):
        print("reading %d bytes" % len(data))
        data = np.fromstring(data, dtype=np.uint8)
        img = data
        print(img.shape)

with picamera.PiCamera() as camera:
    with picamera.array.PiRGBAnalysis(camera) as output:
        camera.resolution = (256, 256)
        camera.framerate = 30
        output = MyStream()
        output2 = MyStream()
        camera.start_recording(output, format='rgb')
        camera.start_recording(output, format='rgb', splitter_port=2, resize=(320, 240))
        camera.wait_recording(1)
        camera.stop_recording()

