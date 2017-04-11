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

import smach
#I stole this from here https://github.com/ros/executive_smach, it's a ROS package but can be used
#independently. I couldn't find anyway to install it with a package manager or otherwise, it's
#pretty small though so I just copied all the relavent bits into our code. 


# Threshold hsv image within hue range
minHue = 27
maxHue = 55
minSaturation = 163
maxSaturation = 225
minValue = 62
maxValue = 190

 
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
       # print ('p,' + str(left) + ',' + str(right) + '!')
#        ser.write('p,' + str(left) + ',' + str(right) + '!')
      #  time.sleep(.05)
#        print 'waiting for P'
        while(1):
            ser.write('p,' + str(left) + ',' + str(right) + '!')
            ret = ser.readline().rstrip()
            if(ret == 'P'):
                #print 'P received'
                return
            else:
                pass
               # print "missed a P"

               
def find_ball():
    # Image
    re, img = cap.read()
    
    #cv2.imshow('mask', img)
    #cv2.waitKey()
    # Convert image to HSV
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # Threshold hsv image within hue range
    # minHue = cv2.getTrackbarPos('minHue', 'mask')
    # maxHue = cv2.getTrackbarPos('maxHue', 'mask')
    # minSaturation = cv2.getTrackbarPos('minSaturation', 'mask')
    # maxSaturation = cv2.getTrackbarPos('maxSaturation', 'mask')
    # minValue = cv2.getTrackbarPos('minValue', 'mask')
    # maxValue = cv2.getTrackbarPos('maxValue', 'mask')

    mask = 255 * (
        (hsv[:,:,0] > minHue) & (hsv[:,:,0] < maxHue) \
        & (hsv[:,:,1] > minSaturation) & (hsv[:,:,1] < maxSaturation) \
        & (hsv[:,:,2] > minValue) & (hsv[:,:,2] < maxValue) \
        ).astype(np.uint8)
    # Dilate mask to remove holes from noise
    mask = dilation(mask, np.ones((3, 3)))

   
    # display mask here because findContours modifies it
    # Find contours in image
    _, contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    if len(contours):
        largestContourIdx = np.argmax([len(c) for c in contours])

        
        area = cv2.contourArea(contours[largestContourIdx])

        if area < 50:
            return None
        
               # cv2.drawContours(img, contours, largestContourIdx, (0,255,0), 3)
        # Display images


        M = cv2.moments(contours[largestContourIdx])
        try:
            center = (int(M['m10']/M['m00']), int(M['m01']/M['m00']))
        except ZeroDivisionError:
            return None
    
            
        height, width, channels = img.shape
       # print "height =", height
       # print "width =", width
        return (width/2 - center[0])
    return None


max_offset = 320.0 #pretty sure our image is 640x480..
max_motor_speed = 150.0
fwd_thresh = 160.0
speed = 0

class HaveBall(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['lost_ball',])
        self.counter = 0

    def execute(self, userdata):
        print 'Found ball, trying to navigate to it'
        while(True):
    
            offset = find_ball()
            print offset

            #time.sleep(.3)
            #can't find any ball, spin in circles
            if(offset is None):
                #set_speed(-70, 70)
                print 'couldn\'t find any ball'
                return 'lost_ball'
            else:
                speed = (offset/max_offset)*max_motor_speed
                fwd = 0
                if(abs(offset) < fwd_thresh):
                    fwd = 50

                print speed + fwd, -speed + fwd
                set_speed(-speed + fwd ,speed + fwd)
        

# define state Bar
class FindBall(smach.State):
    def __init__(self):
        smach.State.__init__(self, outcomes=['found_ball'])

    def execute(self, userdata):
        set_speed(0,0)
        while(True):
            offset = find_ball()
            print 'Lost the ball!'
            
            if offset:
                return 'found_ball'
        

#define some parameters for talking to the arduino/turning or whatever. 
offset_thresh = 160

# if a video path was not supplied, grab the reference
# to the webcam

cap = cv2.VideoCapture(0)
        #cv2.waitKey(50)
if not cap.isOpened():
    print "something went wrong! video not open"


ser = serial.Serial(port = 'COM3',baudrate = 115200, timeout=3)
time.sleep(.5)
print "serial port established (probably)"


# Create a SMACH state machine
sm = smach.StateMachine(outcomes=['found_ball', 'lost_ball'])

# Open the container
with sm:
    # Add states to the container
    smach.StateMachine.add('HAVEBALL', HaveBall(), 
                           transitions={'lost_ball':'FINDBALL'})
    smach.StateMachine.add('FINDBALL', FindBall(), 
                           transitions={'found_ball':'HAVEBALL'})
    
# Execute SMACH plan
outcome = sm.execute()
print outcome
