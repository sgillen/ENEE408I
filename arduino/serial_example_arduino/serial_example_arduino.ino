#include "DualMC33926MotorShield.h"
#define BUFFER_SIZE 32


DualMC33926MotorShield md;


char buffer[BUFFER_SIZE];
uint16_t bufferPosition;

void setup() {
  Serial.begin(9600);
  bufferPosition = 0;


   pinMode(LED_BUILTIN, OUTPUT);
   digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)

   md.init();
}

void loop() {
  if (Serial.available() > 0) {
    
    // Read next byte from serial into buffer
    buffer[bufferPosition] = Serial.read();

    // Check if we've reached exclamation
    if (buffer[bufferPosition] == '!') {
        char* prot = strtok(buffer, ",");
        if(!prot){ 
                Serial.println("B");
                }
                
         else if(prot[0] == 'p'){
              char* leftMString = strtok(buffer, ",");
              char* rightMString = strtok(NULL, "!");

               
              md.setM1Speed(100);
              md.setM2Speed(100);
              delay(50);

              Serial.println("P");
         }
         else if(prot[0] == 's'){
              //TODO send pings
              Serial.println("S");
          
         }
         else{Serial.println("B");}

      // Reset buffer position
      bufferPosition = 0;
    } else {
      
      bufferPosition++;
    }
  }
}


void stopIfFault()
{
  if (md.getFault())
  {
    Serial.println("fault");
    while(1);
  }
}

void forward(){
  md.setM1Speed(100);
  md.setM2Speed(100);
  delay(50);
}

void backward(){
  md.setM1Speed(-100);
  md.setM2Speed(-100);
  delay(50);
}

void right(){
  md.setM1Speed(100);
  md.setM2Speed(-100);
  delay(50);
}

void left(){
  md.setM1Speed(-100);
  md.setM2Speed(100);
  delay(50);
}

void stop(){
  md.setM1Speed(0);
  md.setM2Speed(0);
}
