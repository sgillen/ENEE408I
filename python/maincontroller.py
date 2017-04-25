#definitions so far:

#computer sends "s,l_num,r_num!" is going to mean set left motor to l_num and right motor to righ_nu
# the arduino will send back a "A\n" to acknowledge this command

#computer sends "p!" and will get the ping sensor data in the form p,l_sense,r_sense,fsense


#In all cases the arduino will return B if it could not parse the input

import serial
import time

#these are for the CV side of things. 
from collections import deque
import numpy as np
import argparse
import imutils
import cv2

from skimage.morphology import dilation



 
def get_pings():
    while(True):
        ser.write("s!")
        time.sleep(.05)
        print 'waiting for pings'
        ret = ser.readline().rstrip()
        if(ret[0] == 'S'):
            print "S received extracting pings"
            pings = ret[2:].split(',')
            print pings
            return pings

    

#relies on a global serial variable because I am a bad programmer. 
def set_speed(left, right):
       # print ('p,' + str(left) + ',' + str(right) + '!')
        ser.write('p,' + str(left) + ',' + str(right) + '!')
      #  time.sleep(.05)
#        print 'waiting for P'
        while(1):
           ret = ser.readline().rstrip()
           if(ret == 'P'):
               print 'P received'
               return
           else:
               print "missed a P"
        
class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


getch = _Getch()
               


ser = serial.Serial(port = 'COM3',baudrate = 115200, timeout=3)
time.sleep(3)
print "serial port established (probably)"


count = 0
max_speed = 100
turn_speed = 80
flag = 0

while(True):
    
    x = getch()
    flag = 0
    pings = get_pings()
    for i in pings:
        if(int(i) < 15 and int(i) != 0):
           flag = 1

    if (flag == 1 and x == 'w'):
       set_speed(0,0)
       continue

    

   
    if(x == 'w'):
         set_speed(max_speed, max_speed)
         print "moving forward"
    elif(x == 'a'):
         set_speed(-turn_speed, turn_speed)
         print "moving left"
    elif(x == 'd'):
         set_speed(turn_speed,-turn_speed)
         print "moving right"
    elif(x == 'q'):
        set_speed(0,0)
    
 
