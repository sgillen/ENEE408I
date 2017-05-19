#this setup will talk to the server while trying find a ball. Sends and responds to stop commands

#definitions so far:

#computer sends "s,l_num,r_num!" is going to mean set left motor to l_num and right motor to righ_nu
# the arduino will send back a "A\n" to acknowledge this command

#computer sends "p!" and will get the ping sensor data in the form p,l_sense,r_sense,fsense


#In all cases the arduino will return B if it could not parse the input

import serial
import time
import socket

#these are for the CV side of things. 
from collections import deque
import numpy as np
import argparse
import imutils
import cv2

from skimage.morphology import dilation



# Threshold hsv image within hue range
minHue = 26
maxHue = 37
minSaturation = 97
maxSaturation = 136
minValue = 128
maxValue = 231

# server info
SERVER_IP = "10.104.113.61" # might need to change based on the server's ip
PORT = 5000

# commands
STOP = "STOP"
FOUND = "FOUND"

# message format
DELIM = ","
MSG_END = "!"
MSG_TEMP = "%s" + DELIM + "%s" + MSG_END

# misc.
TEAM_NO = 1
BUF_SIZE = 1024
sock = None

NUM_ROBOTS = 5
 
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

# return 0 on success, -1 on failure
def handshake(team_no, target_ip=SERVER_IP):
	global TEAM_NO
	global sock
	if sock == None:
		sock = socket.socket()
		TEAM_NO = str(team_no)
		sock.settimeout(5)
		try:
			sock.connect((target_ip,PORT))
			sock.send(TEAM_NO)
			data = sock.recv(BUF_SIZE)
                        print data
			if data != TEAM_NO:
				print("Error in handshake")
				sock = None
				return -1
		except socket.timeout:
			print("Could not connect to server at %s:%d" % (target_ip, PORT))
			sock = None
			return -1
		print("Handshake success")
		sock.setblocking(0) # non-blocking	
		return 0
	else:
		print("Socket already connected")
		return 0

# returns a list of tuples ie [(team number, command), (team number, command)]
# or None if no data on socket or error in parsing
def recv():
	try:
		data = sock.recv(BUF_SIZE)
		return data
	except socket.error:
		print("No data found")
		return None
	except Error:
		print("Malformed packet")
		return None

# call to broadcast STOP command
def send_stop():
	sock.send(MSG_TEMP % (TEAM_NO, STOP))

# call to broadcast FOUND command
def send_found():
	sock.send(MSG_TEMP % (TEAM_NO, FOUND))

# call on exit
def close():
	sock.close()

        
#handshake(1,SERVER_IP)

#while 1:
 #       send_stop()
#	data = recv()
 #       print data
  #      time.sleep(1)

count = 0
max_speed = 100
turn_speed = 80
flag = 0

state = 0

#handshake(1,SERVER_IP)

while(True):
    data = None
    
    flag = 0
    pings = get_pings()
    for i in pings:
        if(int(i) < 15 and int(i) != 0):
            flag = 1
    offset = find_ball()

    cmf = int(pings[0])
    cml = int(pings[1])
    cmr = int(pings[2])
    
    if(data is None):
        if(state == 0): #not found
            if(offset is None):
                #move normally
                print "NORMAL"
                if(cmr <= 8 and cml <= 8 and cmr != 0 and cml != 0):
                    set_speed(-turn_speed, turn_speed)
                    time.sleep(1)
                elif(cmr <= 10 and cmr != 0):
                    set_speed(turn_speed, -turn_speed)
                elif(cml <= 10 and cml != 0):
                    set_speed(-turn_speed, turn_speed)
                elif(cmf <= 10 and cmf != 0):
                    set_speed(-turn_speed, turn_speed)
                else:
                    print "MAXSPEED"
                    set_speed(max_speed, max_speed)
            else:
                print "send stops"
               # send_stop()
                state = 1
        elif(state == 1): #found
            if (flag == 1):
                set_speed(0,0)
                continue
            offset = find_ball()
            if(offset is None):
                set_speed(-max_speed, max_speed)
                print "couldn't find any ball"
                #time.sleep(.3 )
            elif(offset < offset_thresh and offset > -offset_thresh):
                set_speed(max_speed, max_speed)
                print "moving forward"
                    #time.sleep(.3 )
                    #ball is to the left
            elif(offset > offset_thresh):
                set_speed(-turn_speed, turn_speed)
                print "moving left"
                    #ball is to the right
            elif(offset < -offset_thresh):
                set_speed(turn_speed,-turn_speed)
                print "moving right"
    else: #stop
         set_speed(0,0)
         time.sleep(5)












while(True):
    flag = 0
    pings = get_pings()
    for i in pings:
        print int(i)
        if(int(i) < 15 and int(i) != 0):
            flag = 1

    print flag

    if (flag == 1):
        set_speed(0,0)
        continue

    offset = find_ball()
    print offset
    #time.sleep(.3)
    #can't find any ball, spin in circles
    if(offset is None):
        set_speed(-max_speed, max_speed)
        print "couldn't find any ball"
        #time.sleep(.3 )
    elif(offset < offset_thresh and offset > -offset_thresh):
        set_speed(max_speed, max_speed)
        print "moving forward"
        #time.sleep(.3 )
    #ball is to the left
    elif(offset > offset_thresh):
        set_speed(-turn_speed, turn_speed)
        print "moving left"
        #time.sleep(.3 )
    #ball is to the right
    elif(offset < -offset_thresh):
        set_speed(turn_speed,-turn_speed)
        print "moving right"
        #time.sleep(.3 )
    
 
