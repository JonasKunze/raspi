import pygame
from pygame.locals import *
import numpy as np
import time
import picamera
import picamera.array

screen_width = 640
screen_height = 480

class PiCam(object):
    def __init__(self):
        self.cam = picamera.PiCamera()
        self.resolution = (screen_width, screen_height)
        self.cam.resolution = self.resolution
        self.video = picamera.array.PiRGBArray(self.cam)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cam.close()

    def draw_preview(self, frame_buffer):
        frame = np.rot90(frame_buffer.array)        
        self.video.seek(0)
        frame = pygame.surfarray.make_surface(frame)
        screen.fill([0,0,0])
        screen.blit(frame, (0,0))
        pygame.display.update()

    def get_stream(self):
        return self.cam.capture_continuous(self.video, format ="rgb", use_video_port=True, resize=self.cam.resolution)

with PiCam() as cam:
    pygame.init()
    pygame.display.set_caption("OpenCV camera stream on Pygame")

    screen = pygame.display.set_mode([screen_width, screen_height])

    try:
        for frameBuf in cam.get_stream():
            cam.draw_preview(frameBuf)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    raise KeyboardInterrupt
    except KeyboardInterrupt,SystemExit:
        pygame.quit()
