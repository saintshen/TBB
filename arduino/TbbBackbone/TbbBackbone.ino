#include <AFMotor.h>

AF_DCMotor motor3(3, MOTOR12_64KHZ);
AF_DCMotor motor4(4, MOTOR12_64KHZ);

String inputString = "";
bool stringComplete = false;

void setup() {
  Serial.begin(9600);
  motor3.setSpeed(255);
  motor4.setSpeed(255);
  inputString.reserve(200);
  Serial.println("Hello From Arduino!");
}

void loop() {
  if (stringComplete) {
    if (inputString=="Go Forward"){
      goForward(1);
    }
    inputString = "";
    stringComplete = false;
  }
  
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputString += inChar;
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}

void turnLeft(){
  Serial.print("turn left");

  motor3.run(FORWARD);
  motor4.run(RELEASE);
  delay(2000);
}

void turnRight(){
  Serial.print("turn right");

  motor3.run(RELEASE);
  motor4.run(FORWARD);
  delay(2000);
}

void goForward(int seconds){
  Serial.print("go forward");

  motor3.run(FORWARD);
  motor4.run(FORWARD);
  delay(seconds*1000);
}

void goBackward(int seconds){
  Serial.print("go backward");

  motor3.run(BACKWARD);
  motor4.run(BACKWARD);
  delay(seconds*1000);
}

void stop(int seconds){
  Serial.print("stop");

  motor3.run(RELEASE);
  motor4.run(RELEASE);
  delay(seconds*1000);
}
