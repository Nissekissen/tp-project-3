

class StepperController
{

private:
    int _dir;
    int _stp;
    int _delayTime = 30;
    long int _currentSteps = 0;
    bool _isMoving = false;
    bool _currentdir = false;
    long int _moveTo = 0;
    long int _maxSteps;
    int _directionOverride;

    void _step(bool dir);

public:
    StepperController(int dir, int stp, int delayTime, long int maxSteps, int directionOverride);
    void init();

    void moveTo(long int steps);
    int movePercentage(int percentage);
    void step();

    void calibrate();

    bool isMoving() { return _isMoving; };
    int getCurrentPercentage() { return _currentSteps * 100 / _maxSteps; }
};