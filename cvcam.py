import pygame
from pygame.locals import *
import numpy as np
import time
import picamera
import picamera.array

from gpio import *

screen_width = 640  
screen_height = 480 

OFFSCREEN = (2*screen_width, 2* screen_height)

BUZZER_PIN = 3
LED_PIN = 4


BUZZER_PUSHED_EVENT = USEREVENT
COUNTER_TICK = USEREVENT + 1

class Counter(pygame.sprite.Sprite):

    def __init__(self, x, y, seconds):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.set_value("")
        self.running = False
        self.seconds = seconds
        self.current_time = 0


    def start(self):
        self.set_value(str(self.seconds))
        self.current_time = self.seconds
        pygame.time.set_timer(COUNTER_TICK, 1000)
        
    def tick(self):
        print(self.current_time)
        self.current_time -= 1
        if self.current_time == 0:
            self.set_value("")
            pygame.time.set_timer(COUNTER_TICK, 0)
        else:
            self.set_value(str(self.current_time))
        

    def set_value(self, value):
        if value == "":
            self.image = pygame.Surface((0, 0), pygame.SRCALPHA)
            self.rect = self.image.get_rect()
            return

        self.font = pygame.font.SysFont("Arial", 128)
        text = self.font.render(value, 1, (255,255,255))
        pixels_alpha = pygame.surfarray.pixels_alpha(text)
        pixels_alpha[...] = (pixels_alpha * (100 / 255.0))
        del pixels_alpha

        W = text.get_width()
        H = text.get_height()

        self.image = pygame.Surface((W, H), pygame.SRCALPHA)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

        self.image.fill((255, 255, 255, 0), None, pygame.BLEND_RGBA_MULT)
        self.image.blit(text, (0, 0))
        
 
    def update(self):
        print("updating Counter")

class CamPreview(pygame.sprite.Sprite):
    def __init__(self, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.width = width
        self.height = height

        self.minimize()

    def set_resolution(self, width, height):
        if hasattr(self, 'cam'):
            self.cam.close()
        self.cam = picamera.PiCamera()
        self.cam.resolution = (height, width) 
        self.video = picamera.array.PiRGBArray(self.cam)
        self.stream_iterator = self.cam.capture_continuous(self.video, format ="rgb", use_video_port=True, resize=self.cam.resolution)

    def minimize(self):
        self.set_resolution(self.width/4, self.height/4)
        self.image = pygame.Surface([self.width/4, self.height/4])

        self.rect = self.image.get_rect()
        self.rect.center = (self.width/2, self.height/2)

    def maximize(self):
        self.set_resolution(self.width, self.height)
        self.image = pygame.Surface([self.width, self.height])

        self.rect = self.image.get_rect()
        self.rect.center = (self.width/2, self.height/2)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cam.close()

    def update(self):
        print("!")
        #frame_buffer = next(self.stream_iterator)
        #frame = np.fliplr(frame_buffer.array)        
        #self.video.seek(0)
        #frame = pygame.surfarray.make_surface(frame)
        #self.image.blit(frame, (0,0))

GPIO_init()
pygame.init()

with CamPreview(screen_width, screen_height) as cam:
    buzzer = Button(BUZZER_PIN, 100)
    led = Led(LED_PIN)

    slide_show_on = True
    
    def on_button_pushed():
        print("buzzer_pushed!!!")
        pygame.event.post(pygame.event.Event(BUZZER_PUSHED_EVENT))
    buzzer.on_pushed = on_button_pushed

    def on_buzzer_pushed_pygame():
        counter.start()
        global slide_show_on
        slide_show_on = not slide_show_on
        if slide_show_on:
            cam.minimize()
        else:
            cam.maximize()

    counter = Counter(screen_width/2, screen_height/2, 3)

    allsprites = pygame.sprite.OrderedUpdates((cam, counter))

    pygame.display.set_caption("OpenCV camera stream on Pygame")

    screen = pygame.display.set_mode([screen_width, screen_height])

    running = True
    clock = pygame.time.Clock()
    try:
        while running: 
            allsprites.update()

            screen.fill((255,255,255))
            allsprites.draw(screen)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    raise KeyboardInterrupt
                if event.type == BUZZER_PUSHED_EVENT:
                    on_buzzer_pushed_pygame()
                if event.type == COUNTER_TICK:
                    counter.tick()
            clock.tick(30)
    except KeyboardInterrupt,SystemExit:
        pygame.quit()
GPIO_cleanup()
