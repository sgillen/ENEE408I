import socket
import select

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 5000              # Arbitrary non-privileged port
NUM_CLIENTS = 2
MAX_TEAM_NO = 2

TEAM_NO = 0

# message format
DELIM = ","
MSG_END = "!"
MSG_TEMP = "%s" + DELIM + "%s" + MSG_END

BUF_SIZE = 1024

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_list = [None]*MAX_TEAM_NO
client_states = [None]*MAX_TEAM_NO

s.bind((HOST, PORT))
s.listen(1)


def recv_and_parse(sock):
	try:
		data = sock.recvfrom(BUF_SIZE)[0]
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
def send_stop(sock):
        print "hello"
	sock.send(MSG_TEMP % (TEAM_NO, "STOP"))

# call to broadcast FOUND command
def send_found(sock):
	sock.send(MSG_TEMP % (TEAM_NO, "FOUND"))

            
##handshake
print "listening for connections"
for i in range(0,NUM_CLIENTS):
    conn, addr = s.accept()
    #print conn
    team_no = conn.recv(1024)
    print 'Connected by', addr, team_no
    client_list[int(team_no)] = (conn)
    client_states[int(team_no)] = 'WAIT'
    if not team_no:
        print "no data"
        
    conn.sendall(team_no)


while True:
    # this will block until at least one socket is ready
    print client_list
    ready_socks,_,_ = select.select(client_list, [], []) 
    for sock in ready_socks:
        # data[0] should be the team number, data[1] should be the data
        msg = recv_and_parse(sock) # This is will not block
        print "received message:", msg
        for data in msg:
            print data[1]
            if data[1] == "STOP":
                send_stop(sock)
        
        
    
    
    
conn.close()
