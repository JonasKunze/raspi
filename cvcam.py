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
        pygame.sprite.Sprite.__init__(self)
        self.cam = picamera.PiCamera()
        self.cam.resolution = (screen_height, screen_width)
        self.video = picamera.array.PiRGBArray(self.cam)
        self.image = pygame.Surface([width, height])

        self.rect = self.image.get_rect()
        self.rect.center = (screen_width/2, screen_height/2)
        
        self.stream_iterator = self.cam.capture_continuous(self.video, format ="rgb", use_video_port=True, resize=self.cam.resolution)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cam.close()

    def update(self):
        frame_buffer = next(self.stream_iterator)
        frame = np.fliplr(frame_buffer.array)        
        self.video.seek(0)
        frame = pygame.surfarray.make_surface(frame)
        self.image.blit(frame, (0,0))


with CamPreview(screen_width, screen_height) as cam:
    allsprites = pygame.sprite.RenderPlain((cam))

    pygame.init()
    pygame.display.set_caption("OpenCV camera stream on Pygame")

    screen = pygame.display.set_mode([screen_width, screen_height])


    running = True
    try:
        while running: 
            allsprites.update()

            allsprites.draw(screen)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    raise KeyboardInterrupt
    except KeyboardInterrupt,SystemExit:
        pygame.quit()
