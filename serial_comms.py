"""
Header values:
36, 70, 42, 100

send values
0-255

"""

import sys
import glob
import serial

def send_header(ser_port):
    header_packet = bytes([100, 42, 70, 36])
    ser_port.write(header_packet)



def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')


    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


if __name__ == "__main__":
    print(serial_ports())
    #port_name = input("Port name: ")

    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

    while True:
        
        while ser.inWaiting():
            print("echo:", ser.readline())

        speed = int(input("speed: ")).to_bytes(1, 'little')
        angle = int(input("angle: ")).to_bytes(1, 'little')
        print(speed, angle)

        send_header(ser)
        ser.write(speed)
        ser.write(angle)
        ser.write(b'\x00')


