#include <MPU6050_tockn.h>
#include <PID_v1.h>
#include <Wire.h>
#include <AFMotor.h>


MPU6050 mpu(Wire);

//PID
double originalSetpoint = 175.8;
double setpoint = originalSetpoint;
double movingAngleOffset = 0.1;
double input, output;
//int moveState=0; //0 = balance; 1 = back; 2 = forth
double Kp = 50;
double Kd = 1.4;
double Ki = 60;
PID pid(&input, &output, &setpoint, Kp, Ki, Kd, DIRECT);

AF_DCMotor LMotor(1);
AF_DCMotor RMotor(2);

void setup() { 
  LMotor.setSpeed(200);
  LMotor.run(RELEASE);
  RMotor.setSpeed(200);
  RMotor.run(RELEASE);

  Serial.begin(9600);
  Wire.begin();
  mpu.begin();
  mpu.calcGyroOffsets(true);
}

void loop() {
  mpu.update();
  Serial.print("anggleX : ");
  input = mpu.getAngleX();
  Serial.print(input);
}
