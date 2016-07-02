import pygame
from pygame.locals import *
import numpy as np
import time
import io
import picamera
import picamera.array
import cv2
import threading

from gpio import *

screen_width = 1024  
screen_height = 768 

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


done = False
lock = threading.Lock()
pool = []

class ImageProcessor(threading.Thread):
    def __init__(self, callback):
        print("new ImageProcessor")
        super(ImageProcessor, self).__init__()
        self.stream = io.BytesIO()
        self.event = threading.Event()
        self.terminated = False
        self.callback = callback
        self.start()

    def run(self):
        print("ImageProcessor running")
        # This method runs in a separate thread
        global done
        while not self.terminated:
            # Wait for an image to be written to the stream
            print("event.wait")
            if self.event.wait(1):
                try:
                    self.stream.seek(0)
                    print("new frame available")
                    elf.callback(self.stream)   

                finally:
                    # Reset the stream and event
                    self.stream.seek(0)
                    self.stream.truncate()
                    self.event.clear()
                    # Return ourselves to the pool
                    with lock:
                        print("appending pool")
                        pool.append(self)
                        

def streams():
    while not done:
        print("lock")
        with lock:
            print("pop")
            if pool:
                processor = pool.pop()
            else:
                processor = None
        if processor:
            print("yield")
            yield processor.stream
            processor.event.set()
        else:
            # When the pool is starved, wait a while for it to refill
            print("pool empty")
            time.sleep(0.1)



class MyStream(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
    def write(self, data):
        data = np.fromstring(data, dtype=np.uint8) 
        data = np.reshape(data, (self.width, self.height, 3))
        data = np.flipud(data)        
        data = np.fliplr(data)        
        self.array = data 

class CamPreview(pygame.sprite.Sprite):
    def __init__(self, width, height):
        pygame.sprite.Sprite.__init__(self)
        self.width = width
        self.height = height

        self.cam = picamera.PiCamera()
        self.cam.resolution = (height, width) 
        self.cam.framerate = 15 

        pool = [ImageProcessor(self.set_next_frame_large) for i in range(4)]

        self.cam.capture_sequence(streams(), use_video_port=True)

#        self.cam.start_recording(self.large_stream, format="rgb")
#        self.cam.start_recording(self.small_stream, format="rgb", splitter_port=2, resize=(self.small_stream.height, self.small_stream.width))
        self.maximize()
        time.sleep(1)

    def set_next_frame_large(frame):
        self.large_frame = frame

    def set_next_frame_small(frame):
        self.small = frame

    def minimize(self):
        self.image = pygame.Surface((self.width/4, self.height/4))

        self.rect = self.image.get_rect()
        self.rect.center = (self.width/2, self.height/2)

    def maximize(self):
        self.image = pygame.Surface([self.width, self.height])

        self.rect = self.image.get_rect()
        self.rect.center = (self.width/2, self.height/2)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cam.close()
        print("closing cam")

    def update(self):
        print("updating")
        frame = pygame.surfarray.make_surface(self.large_frame)
#        self.image.blit(frame, (0,0))
#        frame = pygame.surfarray.make_surface(self.small_frame)
        self.image.blit(frame, (0,0))

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
            print(clock.get_fps())
            clock.tick(30)
    except KeyboardInterrupt,SystemExit:
        pygame.quit()

while pool:
    with lock:
        processor = pool.pop()
    processor.terminated = True
    processor.join()
GPIO_cleanup()
