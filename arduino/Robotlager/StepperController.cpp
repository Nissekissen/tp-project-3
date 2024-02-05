#include "StepperController.h"
#include <Arduino.h>

StepperController::StepperController(int dir, int stp, int delayTime, long int maxSteps, int directionOverride)
{
    
        _dir = dir;
    _stp = stp;
    _delayTime = delayTime;
    _maxSteps = maxSteps;
    _directionOverride = directionOverride;
}

void StepperController::init()
{
    pinMode(_dir, OUTPUT);
    pinMode(_stp, OUTPUT);
}

void StepperController::_step(bool dir)
{
    digitalWrite(_dir, _currentdir == 0 ? HIGH : LOW);
    digitalWrite(_stp, HIGH);
    delayMicroseconds(_delayTime);
    digitalWrite(_stp, LOW);
    delayMicroseconds(_delayTime);

    _currentSteps += _currentdir == 1 ? 1 : -1;
}

void StepperController::moveTo(long int steps)
{
    if (_isMoving)
    {
        return;
    }

    _isMoving = true;
    // Set _currentDir
    _currentdir = steps - _currentSteps > 0;
    _moveTo = steps;
}

int StepperController::movePercentage(int percentage)
{
    // Remap percentage (0-100) to steps (0-_maxSteps)
    long int steps = percentage * _maxSteps / 100;

    moveTo(steps * _directionOverride);
}

void StepperController::step()
{
    if (!_isMoving)
    {
        return;
    }

    if (_currentSteps == _moveTo)
    {
        _isMoving = false;
        return;
    }
    // Serial.println(_moveTo);
    _step(_currentdir);
}

void StepperController::calibrate()
{
    _currentSteps = 0;
}