import serial

ser = serial.Serial('/dev/cu.usbmodem1421',9600)


while(ser.read() != 'A'):
    wait(10)


ser.write('hello!');
