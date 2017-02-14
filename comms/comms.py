#definitions so far:

#computer sends "s,l_num,r_num!" is going to mean set left motor to l_num and right motor to righ_nu
# the arduino will send back a "A\n" to acknowledge this command

#computer sends "p!" and will get the ping sensor data in the form p,l_sense,r_sense,fsense


#In all cases the arduino will return B if it could not parse the input
import serial
import time




ser = serial.Serial('/dev/tty.usbmodem1411',9600, timeout=3)
time.sleep(3)
print "serial port established (probably)"

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
        


#set_speed(100,100)
#set_speed(100,200)



#TODO make sure the arduino is listening! 


while(True):
    set_speed(100,100)
    #pings = get_pings()


 
