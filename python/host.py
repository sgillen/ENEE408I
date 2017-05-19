#this is meant to act as the server for the whole class, tested on Sean's computer (MacOS) not sure if it will work on windows..


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

client_list = [0]*(MAX_TEAM_NO+1)
client_states = [0]*(MAX_TEAM_NO+1)

s.bind((HOST, PORT))
s.listen(1)


def recv_and_parse(sock):
    try:
        data = sock.recvfrom(BUF_SIZE)[0]
        msgs = data.strip(MSG_END).split(MSG_END) 	# split messages
	ret_msgs = list()
	for msg in msgs:
            s = msg.split(DELIM) 					# split team num and command
            if len(s) != 2:
                print "packet malformed: " , s
                continue
            
            ret_msgs.append((s[0],s[1])) 			# packed into tuples
        return ret_msgs
            
    except socket.error:
	print("No data found")
	return None

def check_socks(socks):
    print socks
    for sock in socks:
        r,_,_ = select.select([sock],[],[],0)
        print r
        if r:
            print "found dead socket: ", r ," removing now"
            socks.remove(r)
                    


# call to broadcast STOP command
def send_stop(sock):
    try:
        sock.send(MSG_TEMP % (TEAM_NO, "STOP"))
    except socket.error:
        print "send stop failed"

# call to broadcast FOUND command
def send_found(sock):
    try:
        sock.send(MSG_TEMP % (TEAM_NO, "FOUND"))
    except socket.error:
        print "send found failed"

            
##handshake
print "listening for connections"
for i in range(0,NUM_CLIENTS):
    conn, addr = s.accept()
    #print conn
    team_no = conn.recv(1024)
    print "Connected by", addr, team_no
    
    try:
        client_list[int(team_no)] = (conn)
        client_states[int(team_no)] = "WAIT"
    except IndexError:
        print "team number given: " , team_no, " out of range "
        continue
        
        
    if not team_no:
        print "no data"
        
    conn.sendall(team_no)

    

while True:
    # this will block until at least one socket is ready
    #print client_list

    
    #check_socks(client_list)
    
    r_ready_socks,_,_ = select.select(client_list, [], [])
    #print "read ready - ", r_ready_socks
    #print "write ready - ",  w_ready_socks
    for sock in r_ready_socks:
        # data[0] should be the team number, data[1] should be the data
        msgs = recv_and_parse(sock) # This is will not block
        print "received message:", msgs, "from: ", sock
        if msgs is None:
            print "received empty packet"
            continue
        
        for data in msgs:
           # print data[1]

            if data[1] == "FOUND":
                client_states[int(data[0])] = "FOUND"
                print "team " , data[0], "found something, sending everyone else stops"
                for i in range(1, len(r_ready_socks)+1):
                    if i != int(data[0]):
                        print "sending"
                        client_states[i] = "STOP"
                        send_stop(client_list[i])
        
        
    
    
    
conn.close()
