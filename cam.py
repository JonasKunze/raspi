
# coding: utf-8

from gphoto import GPhoto
from gphoto import Identify
from gphoto import NetworkInfo
import RPi.GPIO as GPIO
import subprocess
import math
import os
import time

camera = GPhoto(subprocess)
idy = Identify(subprocess)
BUTTON = 3 # connects to ground

def init():  
    GPIO.setmode(GPIO.BCM)

    GPIO.setup(BUTTON, GPIO.IN, pull_up_down=GPIO.PUD_UP)  

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
        ("1/50", 200),
        ("1/40", 200),
        ("1/40", 200),
        ("1/25", 200),
        ("1/20", 200),
        ("1/15", 200),
        ("1/20", 400),
        ("1/15", 400),
        ("1/13", 400),
        ("1/10", 400),
        ("1/10", 800)]

current_config = 22
MIN_BRIGHTNESS = 50000
MAX_BRIGHTNESS = 55000
pic_id = 0



# In[ ]:

def change_setting(current_config, delta):
    print("Changing settings")
    current_config = current_config + delta
    camera.set_shutter_speed(secs=CONFIGS[current_config][0])
    camera.set_iso(iso=str(CONFIGS[current_config][1]))  
    return current_config

def check_brightness(filename, current_config):
    brightness = float(idy.mean_brightness(filename))
    delta = 0
    if brightness < MIN_BRIGHTNESS and current_config < len(CONFIGS) - 1:
        delta = 1
        print("too dark")
    elif brightness > MAX_BRIGHTNESS and current_config > 0:
        delta = -1
        print("too bright")

    print(brightness)
    print(delta)

    return delta

def take_pic():
    filename = camera.capture_image_and_download()
    return filename

def check_pic(filename, current_config):
    config_delta = check_brightness(filename, current_config)
    if config_delta != 0: 
        current_config = change_setting(current_config, config_delta)
        return current_config, False 
    return current_config, True

def store_pic(filename):
    os.rename(filename, "pic"+str(pic_id)+".jpg")
    pic_id += 1

init()
#change_setting(current_config, 0)

try:
    def add_buzzer_listener(button):
        GPIO.add_event_detect(button, GPIO.FALLING, callback=on_buzzer_pushed_once, bouncetime=200)
    def on_buzzer_pushed_once(channel):  
        GPIO.remove_event_detect ( channel )

        global current_config
        print("Taking pic!")
        filename = take_pic()
#	print(filename)
#	print(current_config)
        add_buzzer_listener(channel)
    add_buzzer_listener(BUTTON)

    while True:
        time.sleep(1)
        
except Exception as e:  
    print("Exception caught: {0}".format(e))
finally:
    cleanup()

