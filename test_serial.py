import serial
ser = serial.Serial('/dev/ttyACM0', 9600)
while True:
    val = input()
    val = int(val)
    val = val.to_bytes(1, 'little')
    print(val)
    ser.write(val)
    print(ser.read())
