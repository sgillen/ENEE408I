#define BUFFER_SIZE 32

char buffer[BUFFER_SIZE];
uint16_t bufferPosition;

void setup() {
  Serial.begin(9600);
  bufferPosition = 0;
}

void loop() {
  if (Serial.available() > 0) {
    
    // Read next byte from serial into buffer
    buffer[bufferPosition] = Serial.read();

    // Check if we've reached exclamation
    if (buffer[bufferPosition] == '!') {
      
      // Left motor string is before comma, right before exclamation
      char* leftMotorString = strtok(buffer, ",");
      char* rightMotorString = strtok(NULL, "!");
  
      // Convert strings to integers
      int leftMotor = atoi(leftMotorString);
      int rightMotor = atoi(rightMotorString);
  
      /* Speed control code here... */
      Serial.print(leftMotor);
      Serial.print(",");
      Serial.println(rightMotor);
      
      // Reset buffer position
      bufferPosition = 0;
    } else {
      bufferPosition++;
    }
  }
}
