# encoding=utf8

import time ,datetime 
import sys 
import threading  
import get_char

import RPi.GPIO  as GPIO 

# class GPIO:
#     BCM = 0 
#     OUT = 0 
#     IN = 0 
#     LOW = 0 
#     HIGH = 1 
#     def setmode(self,*arg,**kws):
#         pass 
#     def output(self,*arg,**kws):
#         pass 
#     def PWM(self,*arg,**kws):
#         class _PWM:
#             def ChangeDutyCycle(self,*arg,**kws):
#                 pass 
#             def start(self,*arg,**kws):
#                 pass 
             
#         return _PWM() 


GPIO.setmode(GPIO.BCM)

A_EN_PIN = 21 
A_INPUT1 = 20 
A_INPUT2 = 16 

B_EN_PIN = 13 
B_INPUT1 = 19
B_INPUT2 = 26



elock=threading.RLock() 


UP_LEVEL = 0
DOWN_LEVEL=0
LEFT_LEVEL=0
RIGHT_LEVEL=0 
STEP = 5
MAX_LEVEL = 100
G_STOP = False # 结束标示  


class Motor:
    STOP= 0
    FWD = 1
    REV = -1 
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
        self.state = self.STOP
    
    def fwd(self,speed):
        """正转"""
        print("fwd %d,%d,%d,%d" % (self.en_pin,self.pin1,self.pin2,speed),"\r")
        GPIO.output(self.pin1,GPIO.HIGH)
        GPIO.output(self.pin2,GPIO.LOW)
        self.pwm.ChangeDutyCycle(speed)
        self.state = self.FWD
    def rev(self,speed):
        """反转"""
        print("rev %d,%d,%d,%d" % (self.en_pin,self.pin1,self.pin2,speed),"\r")
        GPIO.output(self.pin1,GPIO.LOW)
        GPIO.output(self.pin2,GPIO.HIGH)
        self.pwm.ChangeDutyCycle(speed)
        self.state = self.REV

    def stop(self):
        if self.STOP == self.state:
            return 
        print("stop %d,%d,%d" % (self.en_pin,self.pin1,self.pin2),"\r")
        GPIO.output(self.pin1,GPIO.LOW)
        GPIO.output(self.pin2,GPIO.LOW)
        self.state = self.STOP

    
    

ma = Motor(A_EN_PIN,A_INPUT1,A_INPUT2)
mb = Motor(B_EN_PIN,B_INPUT1,B_INPUT2)

    






def show_info():
    print("show_info start ")
    global UP_LEVEL
    global DOWN_LEVEL
    global LEFT_LEVEL
    global RIGHT_LEVEL 
    global G_STOP 
    while not G_STOP:
        elock.acquire()
        print(
            "UP_LEVEL    %d " % UP_LEVEL,
            "DOWN_LEVEL  %d " % DOWN_LEVEL,
            "LEFT_LEVEL  %d " % LEFT_LEVEL,
            "RIGHT_LEVEL %d\r" % RIGHT_LEVEL,
        )
        elock.release() 
        time.sleep(0.5)
    print("show_info stop ")

def update_motor():
    if UP_LEVEL>0:
        ma.fwd(UP_LEVEL)
        mb.fwd(UP_LEVEL)
    if DOWN_LEVEL>0:
        ma.rev(DOWN_LEVEL)
        mb.rev(DOWN_LEVEL) 
    if LEFT_LEVEL>0 :
        mb.fwd(LEFT_LEVEL) 
    if RIGHT_LEVEL>0 :
        ma.fwd(RIGHT_LEVEL) 
            
    if UP_LEVEL == 0 and DOWN_LEVEL == 0 and RIGHT_LEVEL == 0 and LEFT_LEVEL == 0:
        ma.stop() 
        mb.stop() 
    

def level_change(e):
    global UP_LEVEL
    global DOWN_LEVEL
    global LEFT_LEVEL
    global RIGHT_LEVEL 
    elock.acquire()
    if e["name"] == "up" and UP_LEVEL < MAX_LEVEL:
        if UP_LEVEL > MAX_LEVEL/3:
            UP_LEVEL += 2*STEP
        else:
            UP_LEVEL += STEP
        UP_LEVEL = min(UP_LEVEL, MAX_LEVEL)
        DOWN_LEVEL=0
    if e["name"] == "down" and DOWN_LEVEL < MAX_LEVEL:
        DOWN_LEVEL += STEP
        UP_LEVEL=0
    if e["name"] == "left" and LEFT_LEVEL < MAX_LEVEL:
        LEFT_LEVEL += STEP
        RIGHT_LEVEL= 0 
    if e["name"] == "right" and RIGHT_LEVEL < MAX_LEVEL:
        RIGHT_LEVEL += STEP
        LEFT_LEVEL=0 
    update_motor()
    elock.release() 
    




def auto_stop():
    print("auto_stop start \r")
    global UP_LEVEL
    global DOWN_LEVEL
    global LEFT_LEVEL
    global RIGHT_LEVEL 
    global G_STOP 
    while not G_STOP:
        elock.acquire()
        if UP_LEVEL>0:
            UP_LEVEL   -= STEP
        if DOWN_LEVEL>0:
            DOWN_LEVEL -= STEP
        if LEFT_LEVEL>0:
            LEFT_LEVEL -= STEP
        if RIGHT_LEVEL>0:
            RIGHT_LEVEL-= STEP
        update_motor()
        elock.release() 
        time.sleep(0.2)
    print("auto_stop stop \r")


t_auto_stop =  threading.Thread(target=auto_stop,daemon=True)
t_auto_stop.start()
#threading.Thread(target=show_info,daemon=True).start()


#keyboard.hook(lambda e: print(e.to_json(), datetime.datetime.now()))
#keyboard.hook(hook_keyboard)
def catch_key():
    c = ""
    cmap = {
        '\x03': {"name":"ctrlc"},
        "\x1b[A":{"name":"up"},
        "\x1b[B":{"name":"down"},
        "\x1b[D":{"name":"left"},
        "\x1b[C":{"name":"right"},
    }
    while 1:
        #print([c])
        c = get_char.getch(1) 
        if  c == '\x03':
            return cmap[c]
        
        if c == '\x1b':
            c += get_char.getch(1) 
            if c[1] == '[':
                c += get_char.getch(1)
                if c[2] in ('A','B','C','D'):
                    return cmap[c]




num = 300000
while num:
    num -= 1 
    #print(num,"\r")
    key = catch_key()
    if key["name"] == "ctrlc":
        break 
    level_change(key) 

G_STOP = True 
t_auto_stop.join() 
ma.stop() 
mb.stop() 
GPIO.cleanup() 
