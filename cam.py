
# coding: utf-8

from gphoto import GPhoto
from gphoto import ImageAnalyzer 
import RPi.GPIO as GPIO
from gpio import *
import subprocess
import math
import os
import time
from subprocess import call

camera = GPhoto(subprocess)
BUTTON = 3 # connects to ground

def init():  
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(BUTTON, GPIO.IN)  

def cleanup():
    print "Cleaning up GPIO"
    GPIO.cleanup()

CONFIGS = [("1/1600", 100),
        ("1/1000", 100),
        ("1/800", 100),
        ("1/500", 100),
        ("1/320", 100),
        ("1/250", 100),
        ("1/200", 100),
        ("1/160", 100),
        ("1/100", 100),
        ("1/80", 100),
        ("1/60", 100),
        ("1/50", 100),
        ("1/80", 200),
        ("1/60", 200),
        ("1/50", 200),
        ("1/40", 200),
        ("1/40", 200),
        ("1/25", 200),
        ("1/20", 200),
        ("1/15", 200),
        ("1/25", 400),
        ("1/20", 400),
        ("1/15", 400),
        ("1/13", 400),
        ("1/10", 400),
        ("1/15", 800),
        ("1/13", 800),
        ("1/10", 800)]

MIN_BRIGHTNESS = 230 
MAX_BRIGHTNESS = 250



class Cam():
    def __init__(self):
        self.config = len(CONFIGS)/2 
        self.pic_id = 0
        while True:
            try:
                self.change_setting(0)
                break
            except Exception as e:  
                call(["pkill", "gvfs-gphoto2*"])
                print("Exception caught: {0}".format(e))

    def change_setting(self, delta):
        self.config = self.config + delta
        camera.set_shutter_speed(secs=CONFIGS[self.config][0])
        camera.set_iso(iso=str(CONFIGS[self.config][1]))  
        print("Changed config to %s %s" % CONFIGS[self.config])
        return self.config

    def get_brightness_adj(self):
        brightness = float(ImageAnalyzer.mean_brightness(self.filename))

        delta = 0
        if brightness < MIN_BRIGHTNESS and self.config < len(CONFIGS) - 1:
            delta = MIN_BRIGHTNESS - brightness
            print("too dark")
        elif brightness > MAX_BRIGHTNESS and self.config > 0:
            delta = MAX_BRIGHTNESS - brightness 
            print("too bright")

        print("brightness is %d"% brightness)
        optimum = (MAX_BRIGHTNESS+MIN_BRIGHTNESS)/2
        adjustment = int(round(math.log(optimum/brightness)/math.log(1.3)))
        print("%d, delta is %d"% (brightness, adjustment))

        if self.config + adjustment > len(CONFIGS) - 1:
            return len(CONFIGS)-1 - self.config
        elif self.config + adjustment  < 0:
            return -self.config

        return adjustment 

    def take_pic(self):
        self.filename = camera.capture_image_and_download()
        return self.filename

    def check_brightness(self):
        config_delta = self.get_brightness_adj()
        if config_delta != 0: 
            self.config = self.change_setting(config_delta)
            return self.config, False 
        return self.config, True

    def store_pic(self):
        os.rename(self.filename, "pic"+str(self.pic_id)+".jpg")
        self.pic_id += 1

init()
cam = Cam()

try:
    def add_buzzer_listener(button):
        GPIO.add_event_detect(button, GPIO.FALLING, callback=on_buzzer_pushed_once, bouncetime=200)
        print("done")

    def on_buzzer_pushed_once(channel):  
#        GPIO.remove_event_detect ( channel )

        print("Taking pic!")
        cam.take_pic()

        cam.check_brightness()
 #       add_buzzer_listener(channel)
    add_buzzer_listener(BUTTON)

    while True:
        time.sleep(1)
        
except Exception as e:  
    print("Exception caught: {0}".format(e))
finally:
    cleanup()

