
# coding: utf-8

# In[40]:

import RPi.GPIO as GPIO
import time
import sys

B1 = 3
B2 = 4
def init():
    # to use Raspberry Pi board pin numbers
    GPIO.setmode(GPIO.BCM)
       
    GPIO.setup(B1, GPIO.IN, pull_up_down=GPIO.PUD_UP)  
    GPIO.setup(B2, GPIO.IN, pull_up_down=GPIO.PUD_UP)  
  
def cleanup():
    print "Cleaning up GPIO"
    GPIO.cleanup() 


# In[1]:

print(1)
init()
print(1)
try:
    print(1)
    def my_callback(channel):  
        print "Rising edge detected on port 24 - even though, in the main thread,"  
        print "we are still waiting for a falling edge - how cool?\n"
    print(2)
    GPIO.add_event_detect(B1, GPIO.FALLING, callback=my_callback, bouncetime=200)
    print(3)
  
    print "Waiting for falling edge on port 23"  
    GPIO.wait_for_edge(B2, GPIO.FALLING)
    print "Falling edge detected. Here endeth the second lesson."  
    cleanup()
except Exception as e:  
    print("Exception caught: {0}".format(e))
    cleanup()
