import pygame
from pygame.locals import *
import numpy as np
import time
import picamera
import picamera.array

screen_width = 640
screen_height = 480

camera = picamera.PiCamera()
camera.resolution = (screen_width, screen_height)

pygame.init()
pygame.display.set_caption("OpenCV camera stream on Pygame")

screen = pygame.display.set_mode([screen_width, screen_height])
video = picamera.array.PiRGBArray(camera)

try:
    for frameBuf in camera.capture_continuous(video, format ="rgb", use_video_port=True):
        frame = np.rot90(frameBuf.array)        
        video.truncate(0)
        frame = pygame.surfarray.make_surface(frame)
        screen.fill([0,0,0])
        screen.blit(frame, (0,0))
        pygame.display.update()
        
        for event in pygame.event.get():
         if event.type == KEYDOWN:
          raise KeyboardInterrupt
except KeyboardInterrupt,SystemExit:
    pygame.quit()
