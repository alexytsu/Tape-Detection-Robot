import serial
import time

#serial interface example
#written by Daniel Huang 

def SendSpeed(ser, steering, speed): #servo and motor interface
    adjusted_angle = 85
    if steering < 0:
        adjusted_angle = 60
    else:
        adjusted_angle = 115
    print(f"adjusted angle: {adjusted_angle}")
    checksum = (70+36+steering+speed)%256 #calc 8bit checksum 
    ser.write((('F${}{}{}').format(chr(speed),chr(adjusted_angle),chr(checksum))).encode('utf-8')) #format into ascii string and then write to port
    
#max steering range is 115 to 60

def getSerialPort():
    ser = serial.Serial('/dev/ttyUSB0') #open serial port 
    return ser


if __name__ == "__main__":

    ser = serial.Serial('/dev/ttyACM0') #open serial port 

    steering = 115 #sample values 
    speed = 90
    steering = 60

    while(True): #makes servo move back and forth and motor start and stop indefinitely 
        time.sleep(0.1);
        steering+=1
        speed +=1
        if steering > 115:
            steering = 60
        if speed > 95:
            speed = 90;
        print ("angle: ", steering)
        print ("speed: ", speed)
        SendSpeed(steering, speed)

    ser.close() #close serial port
