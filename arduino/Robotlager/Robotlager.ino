#include "StepperController.h"
#include "Vector3D.h"

#define X_DIR 5
#define Y_DIR 6
#define Z_DIR 7

#define X_STP 2
#define Y_STP 3
#define Z_STP 4

#define WAITING 0
#define MOVING_X_Y 1
#define MOVING_Z 2
#define CALIBRATING 3

#define ELECTROMAGNET 22

#define CALIBRATION_X 24
#define CALIBRATION_Y 25

int STATUS = WAITING;

bool electroMagnetEnabled = false;
bool lastElectroMagnet = false;

bool calibrated = true;
bool calibratedX = false;
bool calibratedY = false;

const uint8_t MAX_MESSAGE_LENGTH = 8;

int currentPos = 0;

StepperController stepperX(X_DIR, X_STP, 30, 48000, 1);
StepperController stepperY(Y_DIR, Y_STP, 15, 28500, -1); // TODO: Fix max steps
StepperController stepperZ(Z_DIR, Z_STP, 40, 30000, 1);  // TODO: Fix max steps

uint8_t *data = (uint8_t *)malloc(7 * sizeof(uint8_t));

Vector3D positions[2];

void setup()
{
  Serial.begin(9600);
  stepperX.init();
  stepperY.init();
  stepperZ.init();

  pinMode(ELECTROMAGNET, OUTPUT);
}

void loop()
{

  while (Serial.available() > 0)
  {
    static char message[MAX_MESSAGE_LENGTH];
    static uint8_t messagePos = 0;

    char inByte = Serial.read();

    if (inByte == '\n' || messagePos >= MAX_MESSAGE_LENGTH)
    {
      message[messagePos] = '\0';
      messagePos = 0;

      Serial.println(message);

      positions[0] = Vector3D(message[0], message[1], message[2]);
      positions[1] = Vector3D(message[3], message[4], message[5]);

      Serial.print("Moving to position ");
      Serial.print(positions[0].x);
      Serial.print(";");
      Serial.print(positions[0].y);
      Serial.print(";");
      Serial.println(positions[0].z);
      Serial.print(positions[1].x);
      Serial.print(";");
      Serial.print(positions[1].y);
      Serial.print(";");
      Serial.println(positions[1].z);

      // break;
      stepperX.movePercentage(positions[0].x);
      stepperY.movePercentage(positions[0].y);
      STATUS = MOVING_X_Y;

      currentPos = 0;

      break;
    }

    message[messagePos] = inByte;
    messagePos++;
  }

  if (!calibrated)
  {

    if (digitalRead(CALIBRATION_X)) {
      stepperX.setCurrentSteps(0);
      Serial.println("Calibrated X");
      calibratedX = true;
    }

    if (digitalRead(CALIBRATION_Y)) {
      stepperY.setCurrentSteps(0);
      Serial.println("Calibrated Y");
      calibratedY = true;
    }
    
    if (calibratedX && calibratedY) {
      calibrated = true;
      Serial.println("Calibrated");
    }

    if (!calibratedX) {
      stepperX.moveTo(stepperX.getCurrentSteps() - 1);
      stepperX.step();
    }

    if (!calibratedY) {
      stepperY.moveTo(stepperY.getCurrentSteps() - 1);
      stepperY.step();
    }

    return;
  }

  if (STATUS == MOVING_X_Y)
  {
    if (moveXY()) {
      return;
    }
  }

  // If moveZ is done
  if (STATUS == MOVING_Z && !stepperZ.isMoving())
  {

    checkZ();

    // Check if we are done or if we need to pick up the box
  }

  stepperX.step();
  stepperY.step();
  stepperZ.step();

  if (electroMagnetEnabled != lastElectroMagnet) {
    // electromagnet changed
    digitalWrite(ELECTROMAGNET, electroMagnetEnabled);
    delay(1000);
  }

  lastElectroMagnet = electroMagnetEnabled;
}

int moveXY()
{
  if (stepperX.isMoving() || stepperY.isMoving())
  {
    return 0;
  }

  // If we are at fromX;fromY, move Z to fromZ, otherwise move Z to toZ
  if (currentPos == 0) {
    // We are at fromX;fromY
    stepperZ.movePercentage(positions[0].z);
    STATUS = MOVING_Z;
    currentPos = 1;
    return 1;
  }

  if (currentPos == 1) {
    // We are at toX;toY
    stepperZ.movePercentage(positions[1].z);
    STATUS = MOVING_Z;
    currentPos = 2;
    return 1;
  }

  // Done
  STATUS = WAITING;
  Serial.println("Done!");
}

void checkZ()
{
  if (stepperZ.getCurrentSteps() == 0 && !stepperZ.isMoving())
  {

    // If we are at fromX;fromY, move to toX;toY, otherwise move to 0 and wait
    if (currentPos == 1) {
      // We are at fromX;fromY, move to toX;toY
      stepperX.movePercentage(positions[1].x);
      stepperY.movePercentage(positions[1].y);
      STATUS = MOVING_X_Y;
      return;
    }

    if (currentPos == 2) {
      // We are at toX;toY, move to 0
      // stepperX.movePercentage(0);
      // stepperY.movePercentage(0);
      // STATUS = MOVING_X_Y;
      STATUS = WAITING;
      Serial.println("Done!");
      return;
    }

    return;
  }

  if (currentPos == 1) {
    // We are at fromX;fromY, enable electromagnet and move to z=0
    electroMagnetEnabled = true;
  } else if (currentPos == 2) {
    // Enable electromagnet
    // Move Z to 0
    electroMagnetEnabled = false;
  }

  stepperZ.movePercentage(0);
  STATUS = MOVING_Z;
}

// void loop() {
//   if (Serial.available() > 0) {
//     String data = Serial.readString();
//     int percentage = data.toInt();
//     Serial.println(percentage);

//     stepperX.movePercentage(percentage);
//     stepperY.movePercentage(percentage);
//   }

//   if (stepperY.isMoving()) {
//     stepperY.step();
//   }

//   if (stepperX.isMoving()) {

//     stepperX.step();
//   }
// }