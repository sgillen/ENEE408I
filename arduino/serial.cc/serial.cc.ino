void setup() {
 Serial.begin(9600);
 while(!Serial){
  //just hang out
 }
  establishContact();

}

void loop() {
  int inByte = Serial.read();
  Serial.write(inByte);
  

}


void establishContact() {
  while (Serial.available() <= 0) {
    Serial.print('A');   // send a capital A
    delay(300);
  }
}
