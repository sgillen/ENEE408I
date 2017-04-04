  #include "DualMC33926MotorShield.h"
#define BUFFER_SIZE 32


DualMC33926MotorShield md;
int lPin = 2;
int rPin = 3;
int fPin = 5;

char buffer[BUFFER_SIZE];
uint16_t bufferPosition;

void setup() {
  Serial.begin(115200);
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
                char* leftMString = strtok(NULL, ",");
                char* rightMString = strtok(NULL, "!");
    

                int leftM = atoi(leftMString);
                int rightM = atoi(rightMString);

                md.setM1Speed(leftM);
                md.setM2Speed(rightM);


                Serial.println("P");
         }
         else if(prot[0] == 's'){
              int fDist = ping(fPin);
              int lDist = ping(lPin);
              int rDist = ping(rPin);

               fDist = microsecondsToCentimeters(fDist);
               lDist = microsecondsToCentimeters(lDist);
               rDist = microsecondsToCentimeters(rDist);

              String comma = ","; //I'm not happy about this
              String S_comma = "S,";
              
              Serial.println(S_comma + fDist + comma + lDist + comma + rDist );
          
         }
         else{Serial.println("B");}

      // Reset buffer position
      bufferPosition = 0;
    } else {
      
      bufferPosition++;
    }
  }
}


long ping(int in){
  pinMode(in, OUTPUT);
  digitalWrite(in, LOW);
  delayMicroseconds(2);
  digitalWrite(in, HIGH);
  delayMicroseconds(5);
  digitalWrite(in, LOW);

  pinMode(in, INPUT);
  long duration = pulseIn(in, HIGH, 4000);
  return duration;
}


void stopIfFault()
{
  if (md.getFault())
  {
    Serial.println("fault");
    while(1);
  }
}


long microsecondsToCentimeters(long microseconds) {
  // The speed of sound is 340 m/s or 29 microseconds per centimeter.
  // The ping travels out and back, so to find the distance of the
  // object we take half of the distance travelled.
  return microseconds / 29 / 2;
}
