# coding: utf-8

import RPi.GPIO as GPIO
import subprocess
import math
import time
import os
import sys 

BUTTON = 3 # connects to ground
LED = 4 # connects to ground
running = True

def eprint(err):
    sys.stderr.write(err)

def init():  
    GPIO.setmode(GPIO.BCM)

def cleanup():
    print "Cleaning up GPIO"
    GPIO.cleanup()


class Button():
    def __init__(self, pin, debounce_ms=100):
        self.pin = pin
        self.debounce_ms = debounce_ms
        if pin < 5:
            GPIO.setup(pin, GPIO.IN)
        else:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  

        self._start_listening()

    def _start_listening(self):
        GPIO.add_event_detect(self.pin, GPIO.FALLING, callback=self._on_buzzer_pushed_once, bouncetime=self.debounce_ms)
        
    def _on_buzzer_pushed_once(self, channel):  
        GPIO.remove_event_detect (self.pin)
        if hasattr(self, 'on_pushed'):
            self.on_pushed()
        else:
            eprint('Buzzer.on_pushed() not defined!')
        self._start_listening()

class Led():
    def __init__(self, pin):
        self.pin = pin

        GPIO.setup(pin, GPIO.OUT)
    def on(self):
        GPIO.output(self.pin, GPIO.HIGH)
    def off(self):
        GPIO.output(self.pin, GPIO.LOW)
    def set(self, on):
        GPIO.output(self.pin, on)
    def toggle(self):
        GPIO.output(self.pin, not GPIO.input(self.pin))


def main():
    button = Button(BUTTON, 100)
    led = Led(LED)
    led.off()
    def t():
        led.toggle()
        
    button.on_pushed = t

    while running:
        time.sleep(1)
 
    
try:
    init()
    print("starting")
    main()
except KeyboardInterrupt:
    cleanup()
