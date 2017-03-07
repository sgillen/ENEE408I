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
    	# grab the current frame
	(grabbed, frame) = camera.read()

    	# resize the frame, blur it, and convert it to the HSV
	# color space
	frame = imutils.resize(frame, width=600)

        #hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        #sg: if we want to add a blur use this, guassian is probably not a good idea
        #blurred = cv2.GaussianBlur(frame, (11, 11), 0)
       	#hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)


        blurred = cv2.bilateralFilter(frame,9,75,75)
        hsv = cv2.cvtColor(blurred, cv2.COLOR_BGR2HSV)
        
	# construct a mask for the color, then perform
	# a series of dilations and erosions to remove any small
	# blobs left in the mask
	mask = cv2.inRange(hsv, colorLower, colorUpper)
	mask = cv2.erode(mask, None, iterations=2)
	mask = cv2.dilate(mask, None, iterations=2)

	# find contours in the mask and initialize the current
	# (x, y) center of the ball
	cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2]
	center = None

        cv2.imshow('frame',blurred)
	# only proceed if at least one contour was found
        if len(cnts) > 0:
		# find the largest contour in the mask, then use
		# it to compute the minimum enclosing circle and
		# centroid
        
                c = max(cnts, key=cv2.contourArea)
                # print len(cnts)
                #for c in cnts:
                ((x, y), radius) = cv2.minEnclosingCircle(c)
	        M = cv2.moments(c)
	        center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                
                print center
                
	        height, width, channels = frame.shape
                print "h = " + str(height)
                print "c = " + str(center[0]/2) 
                return (width/2 - center[0])

                




# define the lower and upper boundaries of the needed color
# ball in the HSV color space, then initialize the
# list of tracked points Current color:GREEN
colorLower = (21, 80, 21)
colorUpper = (110, 200, 200)
pts =  deque(maxlen=64)

#define some parameters for talking to the arduino/turning or whatever. 
offset_thresh = 70

# if a video path was not supplied, grab the reference
# to the webcam

camera = cv2.VideoCapture(0)
        #cv2.waitKey(50)
if not camera.isOpened():
    print "something went wrong! video not open"


ser = serial.Serial(port = 'COM3',baudrate = 9600, timeout=3)
time.sleep(3)
print "serial port established (probably)"



while(True):
    
    offset = find_ball()
    print offset
    time.sleep(1)
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
    


 
