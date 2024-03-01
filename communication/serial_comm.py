# File for handling communication with the Arduino over serial

import serial, sys, time, models

class SerialComm:
    def __init__(self, port, baudrate):
        self.ser = serial.Serial(port, baudrate, timeout=0.1)
        time.sleep(2)

    # Send the position as X, Y and Z values where one coordinate takes one byte.
    def send(self, data):
        print(data.decode())
        self.ser.write(data)
        # for i in data:
        #     print("Sending:", i)
        #     self.ser.write(i)
        #     time.sleep(0.01)
    
    def send_instruction(self, instruction: models.Instruction, cursor: models.RealDictCursor):
        test = instruction.to_bytes(cursor)
        print("test:", b''.join([test, b'\n']))
        self.send(b''.join([test, b'\n']))
    
    def get_status(self):
        self.ser.write(0x53) # Status command (S)
        return self.ser.readline()

    # Read the serial port
    def read(self):
        return self.ser.readline()