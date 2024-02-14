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

#define ELECTROMAGNET 8

int STATUS = WAITING;
int lastStatus = WAITING; // To detect when status changes

bool electroMagnetEnabled = false;

bool calibrated = false;

StepperController stepperX(X_DIR, X_STP, 30, 48000, 1);
StepperController stepperY(Y_DIR, Y_STP, 15, 30000, 1); // TODO: Fix max steps
StepperController stepperZ(Z_DIR, Z_STP, 30, 25000, 1); // TODO: Fix max steps

uint8_t *data = (uint8_t *)malloc(7 * sizeof(uint8_t));
int currentPos = 0;

Vector3D positions[2];

uint8_t tempData = 0xC0; // 11000000

void setup()
{
  Serial.begin(115200);
  stepperX.init();
  stepperY.init();
  stepperZ.init();
}

void loop()
{

  if (!calibrated)
  {
  }

  if (Serial.available() > 0 && Serial.read() == 'S') {
    Serial.println(STATUS);
  }

  if (Serial.available() > 0 && STATUS == WAITING)
  {

    // Format: One byte per axis, 3 bytes per position

    String _data = Serial.readString();
    char buf[7];
    _data.toCharArray(buf, 7);

    data = (uint8_t *)buf;

    positions[0] = Vector3D(data[0], data[1], data[2]);
    positions[1] = Vector3D(data[3], data[4], data[5]);

    stepperX.movePercentage(positions[0].x);
    stepperY.movePercentage(positions[0].y);
    STATUS = MOVING_X_Y;
    currentPos = 0;

    Serial.print("Moving to position ");
    Serial.print(positions[0].x);
    Serial.print(";");
    Serial.println(positions[0].y);

    return;
  }

  if (STATUS == MOVING_X_Y)
  {
    moveXY();
  }

  // If moveZ is done
  if (STATUS == MOVING_Z && !stepperZ.isMoving())
  {

    checkZ();

    // Check if we are done or if we need to pick up the box
  }

  if (electroMagnetEnabled)
  {
    // digitalWrite(ELECTROMAGNET, HIGH);
  }
  else
  {
    // digitalWrite(ELECTROMAGNET, LOW);
  }

  stepperX.step();
  stepperY.step();
  stepperZ.step();

  lastStatus = STATUS;
}

void moveXY()
{
  if (stepperX.isMoving() || stepperY.isMoving())
  {
    return;
  }

  // If we are at fromX;fromY, move Z to fromZ, otherwise move Z to toZ
  if (electroMagnetEnabled)
  {
    stepperZ.movePercentage(positions[1].z);
  }
  else
  {
    stepperZ.movePercentage(positions[0].z);
  }

  STATUS = MOVING_Z;
}

void checkZ()
{
  if (stepperZ.getCurrentPercentage() == 0)
  {
    if (electroMagnetEnabled)
    {
      // move to toX;toY
      stepperX.movePercentage(positions[1].x);
      stepperY.movePercentage(positions[1].y);
      STATUS = MOVING_X_Y;
    }
    else
    {
      STATUS = WAITING;
    }
    return;
  }

  if (stepperX.getCurrentPercentage() == positions[1].x && stepperY.getCurrentPercentage() == positions[1].y)
  {
    // Done, move Z to 0 and go back to waiting.
    // Disable electromagnet
    electroMagnetEnabled = false;
  }
  else
  {
    // Enable electromagnet
    // Move Z to 0
    electroMagnetEnabled = true;
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