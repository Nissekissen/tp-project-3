import serial, time


def main():
    while True:
        ser = serial.Serial('COM4', 115200, timeout=0.1)
        x = input("Enter X position: ")
        y = input("Enter Y position: ")
        z = input("Enter Z position: ")
		
		# Send the X, Y, Z position to the Arduino as one byte, where the first two bits are empty, the next two are X, the next two are Y, and the last two are Z
        ser.write(bytes(0b00000000 | int(x) << 4 | int(y) << 2 | int(z)))
        time.sleep(0.1)
        print(ser.readline())

if __name__ == "__main__":
	main()