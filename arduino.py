import serial
import time

#serial interface example
#written by Daniel Huang 

def SendSpeed(ser, steering, speed): #servo and motor interface
    adjusted_angle = 90 + steering
    if steering < -35:
        adjusted_angle = 55
    if steering > 35:
        adjusted_angle = 125
    checksum = (70+36+adjusted_angle+speed)%256 #calc 8bit checksum 
    try:
        ser.write((('F${}{}{}').format(chr(speed),chr(adjusted_angle),chr(checksum))).encode('utf-8')) #format into ascii string and then write to port
    except:
        pass
    
#max steering range is 125 to 55

def getSerialPort():
    ser = serial.Serial('/dev/ttyUSB0') #open serial port 
    return ser


if __name__ == "__main__":

    ser = serial.Serial('/dev/ttyUSB0') #open serial port 

    steering = 115 #sample values 
    speed = 90
    steering = -25

    while(True): #makes servo move back and forth and motor start and stop indefinitely 
        time.sleep(0.1);
        steering+=1
        speed +=1
        if steering > 35:
            steering = -35
        if speed > 95:
            speed = 90;
        print ("angle: ", steering)
        print ("speed: ", speed)
        SendSpeed(ser, steering, speed)

    ser.close() #close serial port
