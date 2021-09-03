# encoding=utf8

import time ,datetime 
import sys 
import keyboard
import threading  
from queue import Queue 

#import RPi.GPIO  as GPIO 

class GPIO:
    BCM = 0 
    OUT = 0 
    IN = 0 
    LOW = 0 
    HIGH = 1 
    def setmode(self,*arg,**kws):
        pass 
    def output(self,*arg,**kws):
        pass 
    def PWM(self,*arg,**kws):
        class _PWM:
            def ChangeDutyCycle(self,*arg,**kws):
                pass 
            def start(self,*arg,**kws):
                pass 
             
        return _PWM() 


GPIO.setmode(GPIO.BCM)

A_EN_PIN = 16 
A_INPUT1 = 20 
A_INPUT2 = 21 

B_EN_PIN = 0 
B_INPUT1 = 0 
B_INPUT2 = 0


eq  = Queue() 
elock=threading.RLock() 


UP_LEVEL = 0
DOWN_LEVEL=0
LEFT_LEVEL=0
RIGHT_LEVEL=0 
STEP = 2 
MAX_LEVEL = 100



class Motor:
    def __init__(self,en_pin,pin1,pin2):
        self.en_pin = en_pin
        self.pin1 = pin1
        self.pin2 = pin2 
        GPIO.setup(en_pin, GPIO.OUT)
        GPIO.setup(pin1, GPIO.OUT)
        GPIO.setup(pin2, GPIO.OUT)
        # 100HZ 
        self.pwm = GPIO.PWM(en_pin, 100)
        self.pwm.start(0)
    
    def fwd(self,speed):
        """正转"""
        GPIO.output(self.pin1,GPIO.HIGH)
        GPIO.output(self.pin2,GPIO.LOW)
        self.pwm.ChangeDutyCycle(speed)
    def rev(self,speed):
        """反转"""
        GPIO.output(self.pin1,GPIO.LOW)
        GPIO.output(self.pin2,GPIO.HIGH)
        self.pwm.ChangeDutyCycle(speed)

    def stop(self):
        GPIO.output(self.pin1,GPIO.LOW)
        GPIO.output(self.pin2,GPIO.LOW)

    
    



    


def hook_keyboard(e):
    if e.name == "up" and e.event_type == "down" :
        eq.put(e) 
    if e.name == "down" and e.event_type == "down" :
        eq.put(e) 
    if e.name == "left" and e.event_type == "down" :
        eq.put(e) 
    if e.name == "right" and e.event_type == "down" :
        eq.put(e) 



def show_info():
    print("show_info start ")
    global UP_LEVEL
    global DOWN_LEVEL
    global LEFT_LEVEL
    global RIGHT_LEVEL 
    while 1:
        elock.acquire()
        print(
            "UP_LEVEL    %d " % UP_LEVEL,
            "DOWN_LEVEL  %d " % DOWN_LEVEL,
            "LEFT_LEVEL  %d " % LEFT_LEVEL,
            "RIGHT_LEVEL %d " % RIGHT_LEVEL,
        )
        elock.release() 
        time.sleep(0.5)

def level_change(e):
    global UP_LEVEL
    global DOWN_LEVEL
    global LEFT_LEVEL
    global RIGHT_LEVEL 
    elock.acquire()
    if e.name == "up" and UP_LEVEL < MAX_LEVEL:
        if UP_LEVEL > MAX_LEVEL/3:
            UP_LEVEL += 2*STEP
        else:
            UP_LEVEL += STEP
        UP_LEVEL = min(UP_LEVEL, MAX_LEVEL)
        DOWN_LEVEL=0
    if e.name == "down" and DOWN_LEVEL < MAX_LEVEL:
        DOWN_LEVEL += STEP
        UP_LEVEL=0
    if e.name == "left" and LEFT_LEVEL < MAX_LEVEL:
        LEFT_LEVEL += STEP
        RIGHT_LEVEL= 0 
    if e.name == "right" and RIGHT_LEVEL < MAX_LEVEL:
        RIGHT_LEVEL += STEP
        LEFT_LEVEL=0 
    elock.release() 
        

def auto_stop():
    print("auto_stop start ")
    global UP_LEVEL
    global DOWN_LEVEL
    global LEFT_LEVEL
    global RIGHT_LEVEL 
    while 1:
        elock.acquire()
        if UP_LEVEL>0:
            UP_LEVEL   -= STEP
        if DOWN_LEVEL>0:
            DOWN_LEVEL -= STEP
        if LEFT_LEVEL>0:
            LEFT_LEVEL -= STEP
        if RIGHT_LEVEL>0:
            RIGHT_LEVEL-= STEP
        elock.release() 
        time.sleep(0.06)


threading.Thread(target=auto_stop,daemon=True).start()
threading.Thread(target=show_info,daemon=True).start()


#keyboard.hook(lambda e: print(e.to_json(), datetime.datetime.now()))
keyboard.hook(hook_keyboard)


while 1:
    e = eq.get()
    level_change(e)

    #print(sys.stdin.read(1))