# encoding=utf8


import RPi.GPIO  as GPIO 
import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(16, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
GPIO.setup(21, GPIO.OUT)

GPIO.output(16,1),GPIO.output(20,1),GPIO.output(21,0)


GPIO.setup(16, GPIO.IN)
GPIO.setup(20, GPIO.IN)
GPIO.setup(21, GPIO.IN)

print(GPIO.input(16),GPIO.input(20),GPIO.input(21))
