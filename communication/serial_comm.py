# File for handling communication with the Arduino over serial

import serial

class SerialComm:
    def __init__(self, port, baudrate):
        self.ser = serial.Serial(port, baudrate, timeout=0.1)

    # Send the position as X, Y and Z values where one coordinate takes one byte.
    def send(self, data):
        self.ser.write(data)
    
    def get_status(self):
        self.ser.write(0x53) # Status command (S)
        return self.ser.readline()

    # Read the serial port
    def read(self):
        return self.ser.readline()