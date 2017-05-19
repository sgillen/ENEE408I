##this code is meant to test host.py

import socket
import sys
import time
# server info
#SERVER_IP = "10.104.127.127" # might need to change based on the server's ip
SERVER_IP = "127.0.0.1"
PORT = 5000
 
# commands
STOP = "STOP"
FOUND = "FOUND"

# message format
DELIM = ","
MSG_END = "!"
MSG_TEMP = "%s" + DELIM + "%s" + MSG_END

# misc.
TEAM_NO = 2
BUF_SIZE = 1024
sock = None

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
def recv_parse():
	try:
		data = sock.recv(BUF_SIZE)
		msgs = data.strip(MSG_END).split(MSG_END) 	# split messages
		ret_msgs = list()
		for msg in msgs:
			s = msg.split(DELIM) 					# split team num and command
			ret_msgs.append((s[0],s[1])) 			# packed into tuples
		return ret_msgs
	except socket.error:
		print("No data found")
		return None

# call to broadcast STOP command
def send_stop():
        print "hello"
	sock.send(MSG_TEMP % (TEAM_NO, STOP))

# call to broadcast FOUND command
def send_found():
	sock.send(MSG_TEMP % (TEAM_NO, FOUND))

# call on exit
def close():
	sock.close()

handshake(TEAM_NO,SERVER_IP)
handshake(1, SERVER_IP)
while 1:
        send_stop()
        #send_found()
        
        
	data = recv_parse()
        print data
        time.sleep(1)
