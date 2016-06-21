
# coding: utf-8

from gphoto import GPhoto
from gphoto import ImageAnalyzer 
import RPi.GPIO as GPIO
from gpio import *
import subprocess
import math
import os
import time

camera = GPhoto(subprocess)
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

current_config = 1 
MIN_BRIGHTNESS = 230 
MAX_BRIGHTNESS = 250
pic_id = 0



# In[ ]:

def change_setting(current_config, delta):
    current_config = current_config + delta
    camera.set_shutter_speed(secs=CONFIGS[current_config][0])
    camera.set_iso(iso=str(CONFIGS[current_config][1]))  
    print("Changed config to %s %s" % CONFIGS[current_config])
    return current_config

def check_brightness(filename, current_config):
    brightness = float(ImageAnalyzer.mean_brightness(filename))

    delta = 0
    if brightness < MIN_BRIGHTNESS and current_config < len(CONFIGS) - 1:
        delta = MIN_BRIGHTNESS - brightness
        print("too dark")
    elif brightness > MAX_BRIGHTNESS and current_config > 0:
        delta = MAX_BRIGHTNESS - brightness 
        print("too bright")

    print("delta is %d"% delta)
    optimum = (MAX_BRIGHTNESS+MIN_BRIGHTNESS)/2
    delta = int(round(math.log(optimum/brightness)/math.log(1.3)))
    print("%d, delta is %d"% (brightness, delta))

    if current_config + delta > len(CONFIGS) - 1:
        print("returning %d" % (len(CONFIGS)-1 - current_config))
        return len(CONFIGS)-1 - current_config
    elif current_config + delta  < 0:
        print("returning %d" % -current_config)
        return -current_config

    return delta

def take_pic():
    filename = camera.capture_image_and_download()
    return filename
    #return "capt0000.jpg"

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
change_setting(current_config, 0)

try:
    def add_buzzer_listener(button):
        GPIO.add_event_detect(button, GPIO.FALLING, callback=on_buzzer_pushed_once, bouncetime=200)
        print("done")

    def on_buzzer_pushed_once(channel):  
#        GPIO.remove_event_detect ( channel )

        global current_config
        print("Taking pic!")
        filename = take_pic()

        current_config, changed = check_pic(filename, current_config)
 #       add_buzzer_listener(channel)
    add_buzzer_listener(BUTTON)

    while True:
        time.sleep(1)
        
except Exception as e:  
    print("Exception caught: {0}".format(e))
finally:
    cleanup()

