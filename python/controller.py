import pygame
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
import threading
import math

from skimage.morphology import dilation



# Threshold hsv image within hue range
minHue = 26
maxHue = 37
minSaturation = 97
maxSaturation = 136
minValue = 128
maxValue = 231
mode = 0 #0 for remote, 1 for ball following
x = 'q'


def run(self):
    while(True):
        x = getch()
        if(x == 'm'):
            mode = (mode + 1) % 2
            set_speed(0,0)
            x = 'q'
                
            
               
 
def get_pings():
    while(True):
        ser.write("s!")
        time.sleep(.05)
        print 'waiting for pings'
        ret = ser.readline().rstrip()
        print ret
        if ret is None or ret == "":
            return ["0","0","0"]
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
               break
        
def find_ball():
    # Image
    re, img = cap.read()
    # Convert image to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    mask = cv2.GaussianBlur(hsv,(5,5),0)
    
    mask = 255 * (
        (hsv[:,:,0] > minHue) & (hsv[:,:,0] < maxHue) \
        & (hsv[:,:,1] > minSaturation) & (hsv[:,:,1] < maxSaturation) \
        & (hsv[:,:,2] > minValue) & (hsv[:,:,2] < maxValue) \
        ).astype(np.uint8)
    # Dilate mask to remove holes from noise
    mask = dilation(mask, np.ones((3, 3)))

 #   cv2.imshow('mask', mask)
    # display mask here because findContours modifies it
    # Find contours in image
    _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours):
        largestContourIdx = np.argmax([len(c) for c in contours])

               # cv2.drawContours(img, contours, largestContourIdx, (0,255,0), 3)
        # Display images
        area = cv2.contourArea(contours[largestContourIdx])

        if area < 30:
            return None
        
        M = cv2.moments(contours[largestContourIdx])
        try:
            center = (int(M['m10']/M['m00']), int(M['m01']/M['m00']))
        except ZeroDivisionError:
            return None

            
        height, width, channels = img.shape
        print "height =", height
        print "width =", width
        return (width/2 - center[0])
    return None


# define the lower and upper boundaries of the needed color
# ball in the HSV color space, then initialize the
# list of tracked points Current color:GREEN
colorLower = (30, 75, 70)
colorUpper = (140, 240, 216)
pts =  deque(maxlen=64)

#define some parameters for talking to the arduino/turning or whatever. 
offset_thresh = 100

# if a video path was not supplied, grab the reference
# to the webcam

cap = cv2.VideoCapture(0)
        #cv2.waitKey(50)
if not cap.isOpened():
    print "something went wrong! video not open"


ser = serial.Serial(port = 'COM3',baudrate = 115200, timeout=3)
time.sleep(3)
print "serial port established (probably)"


count = 0
max_speed = 200
max_speed2 = 100
turn_speed = 80
flag = 0

# mythread = threading.Thread(target=run)
# mythread.start()




pygame.init()
pygame.display.set_mode([100,100])

delay = 100
interval = 50
pygame.key.set_repeat(delay, interval)

# while True:
#     keys = pygame.key.get_pressed()  #checking pressed keys
#     if keys[pygame.K_w]:
#         print("Hey, you pressed the key, 'w'!")
#         set_speed(max_speed, max_speed)
#         print "moving forward"
#     elif keys[pygame.K_a]:
#         set_speed(-turn_speed, turn_speed)
#         print "moving left"
#     elif keys[pygame.K_a]:
#           set_speed(turn_speed,-turn_speed)
#           print "moving right"
#     time.sleep(.1)    


pygame.joystick.init()
print pygame.joystick.get_count()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

print joysticks[0].get_name()
joysticks[0].init()

# while True:
#     print joysticks[0].get_axis(0)
#     time.sleep(.1)


joystick_count = pygame.joystick.get_count()





mode = 0

flag = 0
while True:
    flag = 0

    pings = get_pings()
    for i in pings:
        if(int(i) < 15 and int(i) != 0):
            flag = 1

    if(flag == 1):
        set_speed(0,0)

            
    for event in pygame.event.get():
        if event.type == pygame.JOYBUTTONDOWN:
            if event.button == 1:
                mode = (mode + 1) % 2
                set_speed(0,0)
        if mode == 0:        
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w and flag != 1:
                    set_speed(max_speed, max_speed)
                elif event.key == pygame.K_a:
                    set_speed(-turn_speed, turn_speed)
                elif event.key == pygame.K_d:
                    set_speed(turn_speed,-turn_speed)
            elif event.type == pygame.JOYAXISMOTION:
                x = joysticks[event.joy].get_axis(0)
                y = -joysticks[event.joy].get_axis(1)

                if(y < 0 or flag == 1):
                    y = 0
                
                set_speed(max(min((x+y)*max_speed,max_speed),-max_speed), max(min((-x+y)*max_speed,max_speed),-max_speed))

                #set_speed(math.sqrt(x**2 + y**2)*np.sign(x)*max_speed, math.sqrt(x**2 + y**2)*np.sign(x)*max_speed)
                
                # r = math.sqrt(x**2 + y **2)
                # angle = math.atan(y/x)+
                # if(angle > 5*math.pi/6):
                #     set_speed(np.sign(x)*r*max_speed, np.sign(x)*-r*max_speed)
                # elif(angle < math.pi/6):
                #     set_speed(np.sign(x)*-r*max_speed, np.sign(x)*r*max_speed)
                # else:
                #     set_speed(r*max_speed, r*max_speed)
                    
                print "Joystick '",joysticks[event.joy].get_name(),""
                print "axis 0 " , joysticks[event.joy].get_axis(0)
                print "axis 1 " , joysticks[event.joy].get_axis(1)

    if(mode == 1):
        maxspeed = 100
        offset = find_ball()
        #can't find any ball, spin in circles
        if(offset is None):
            set_speed(-max_speed2, max_speed2)
        elif(offset < offset_thresh and offset > -offset_thresh):
            set_speed(max_speed2, max_speed2)
        #ball is to the left
        elif(offset > offset_thresh):
            set_speed(-turn_speed, turn_speed)
        #ball is to the right
        elif(offset < -offset_thresh):
            set_speed(turn_speed,-turn_speed)
            
  
