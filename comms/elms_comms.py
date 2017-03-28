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
        print ret
        if(ret[0] == 'S'):
            print "S received extracting pings"
            pings = ret.split(',')
            for i in pings:
                print i
            return pings

    

#relies on a global serial variable because I am a bad programmer. 
def set_speed(left, right):
    while(True):
       # print ('p,' + str(left) + ',' + str(right) + '!')
        ser.write('p,' + str(left) + ',' + str(right) + '!')
        time.sleep(.05)
        print 'waiting for P'
        ret = ser.readline().rstrip()
        print ret
        if(ret == 'P'):
            print 'P received'
            return
        
def find_ball():
    # Image
    re, img = cap.read()
    # Convert image to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Threshold hsv image within hue range
    # minHue = cv2.getTrackbarPos('minHue', 'mask')
    # maxHue = cv2.getTrackbarPos('maxHue', 'mask')
    # minSaturation = cv2.getTrackbarPos('minSaturation', 'mask')
    # maxSaturation = cv2.getTrackbarPos('maxSaturation', 'mask')
    # minValue = cv2.getTrackbarPos('minValue', 'mask')
    # maxValue = cv2.getTrackbarPos('maxValue', 'mask')


    # Threshold hsv image within hue range
    minHue = 27
    maxHue = 55
    minSaturation = 163
    maxSaturation = 225
    minValue = 62
    maxValue = 190

    mask = 255 * (
        (hsv[:,:,0] > minHue) & (hsv[:,:,0] < maxHue) \
        & (hsv[:,:,1] > minSaturation) & (hsv[:,:,1] < maxSaturation) \
        & (hsv[:,:,2] > minValue) & (hsv[:,:,2] < maxValue) \
    ).astype(np.uint8)
    # Dilate mask to remove holes from noise
    mask = dilation(mask, np.ones((10, 10)))
    cv2.imshow('mask', mask)
    # display mask here because findContours modifies it
    # Find contours in image
    _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours):
        largestContourIdx = np.argmax([len(c) for c in contours])
        
        cv2.drawContours(img, contours, largestContourIdx, (0,255,0), 3)
        # Display images
    

        M = cv2.moments(contours[largestContourIdx])
        center = (int(M['m10']/M['m00']), int(M['m01']/M['m00']))
        print center
        return center[0]
        
    cv2.imshow('image', img)
    cv2.waitKey(1)



# define the lower and upper boundaries of the needed color
# ball in the HSV color space, then initialize the
# list of tracked points Current color:GREEN
colorLower = (30, 75, 70)
colorUpper = (140, 240, 216)
pts =  deque(maxlen=64)

#define some parameters for talking to the arduino/turning or whatever. 
offset_thresh = 70

# if a video path was not supplied, grab the reference
# to the webcam

cap = cv2.VideoCapture(0)
        #cv2.waitKey(50)
if not cap.isOpened():
    print "something went wrong! video not open"


#ser = serial.Serial(port = 'COM3',baudrate = 9600, timeout=3)
#time.sleep(3)
#print "serial port established (probably)"



while(True):
    
    offset = find_ball()
    print offset
    #time.sleep(1)
    #can't find any ball, spin in circles
    if(not offset):
        #set_speed(-100, 100)
        print "couldn't fine any ball"
    elif(offset < offset_thresh and offset > -offset_thresh):
        #set_speed(100, 100)
        print "moving forward"
    #ball is to the left
    elif(offset < offset_thresh):
        #set_speed(-100,100)
        print "moving left"
    #ball is to the right
    elif(offset > offset_thresh):
        #set_speed(100,-100)
        print "moving right"
    #pings = get_pings()
 
