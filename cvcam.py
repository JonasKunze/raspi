import pygame
from pygame.locals import *
import numpy as np
import time
import picamera
import picamera.array

screen_width = 640  
screen_height = 360 

class CamPreview(pygame.sprite.Sprite):
    def __init__(self, width, height):
        self.cam = picamera.PiCamera()
        self.cam.resolution = (screen_height, screen_width)
        self.video = picamera.array.PiRGBArray(self.cam)
        self.image = pygame.Surface([width, height])

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cam.close()

    def update(self):
        frame = np.fliplr(frame_buffer.array)        
        print(len(frame))
        self.video.seek(0)
        frame = pygame.surfarray.make_surface(frame)
        screen.fill([0,0,0])
        screen.blit(frame, (0,0))
        pygame.display.update()

    def get_stream(self):
        return self.cam.capture_continuous(self.video, format ="rgb", use_video_port=True, resize=self.cam.resolution)

with CamPreview(screen_width, screen_height) as cam:
    pygame.init()
    pygame.display.set_caption("OpenCV camera stream on Pygame")

    screen = pygame.display.set_mode([screen_width, screen_height])

    try:
        for frameBuf in cam.get_stream():
            cam.draw_preview(frameBuf, screen)
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    raise KeyboardInterrupt
    except KeyboardInterrupt,SystemExit:
        pygame.quit()
