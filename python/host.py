import socket

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 5000              # Arbitrary non-privileged port
NUM_CLIENTS = 3
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

client_list = {}

s.bind((HOST, PORT))
s.listen(1)


##handshake
print "listening for connections"
for i in range(1,NUM_CLIENTS):
    conn, addr = s.accept()
    team_no = conn.recv(1024)
    print 'Connected by', addr, team_no
    client_list[team_no] = (conn,addr)
    if not team_no:
        print "no data"
        
    conn.sendall(team_no)


while 1:
    
    
   conn.close()
