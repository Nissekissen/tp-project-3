import serial, time


import serial.tools.list_ports
ports = serial.tools.list_ports.comports()
print(ports)

for port, desc, hwid in sorted(ports):
        print("{}: {} [{}]".format(port, desc, hwid))

serial_conn = serial_comm.SerialComm('COM8', 9600)

serial_conn.send(f'{0x64}{0x64}{0x64}{0x32}{0x32}{0x64}'.encode())