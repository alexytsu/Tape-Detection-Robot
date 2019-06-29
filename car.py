import serial
import time


class Car():

    def __init__(self):
        self.found = 0
        pass
    
    def setThrottle(self,ser):
        self.Throttle = ser
        print("set Throttle")

    def setSteering(self,ser):
        self.Steering = ser
        print("set Steering")
        pass

    def findHeader(self,ser):
        print("findHeader")
        out = ''
        while(True):
            if(ser.inWaiting()>0):
                inVal = ser.read(1)
                #print(inVal)
                if(chr(inVal[0]) == '$'):
                    break
                out += str(chr(inVal[0]))
                print(out[len(out)-3:len(out)-1])
            if(out[len(out)-3:len(out)-1]=="ST"):
                #print(out)
                self.setSteering(ser)
                return
            elif(out[len(out)-3:len(out)-1]=="AF"):
                #print(out)
                self.setThrottle(ser)
                return


    def write(self,val,ser):
        byteL = val & 0xFF
        byteH = (val >> 8) & 0xFF
        checksum = (70+36+byteL+byteH)%256 #calc 8bit checksum 
        ser.write((('F${}{}{}').format(chr(byteH),chr(byteL),chr(checksum))).encode('utf-8')) #format into ascii string and then write to port

    def SendThrottle(self,val):
        self.write(val,self.Throttle)

    def SendSteering(self,val):
        angle = 90 + val
        angle = max(60, angle)
        angle = min(125, angle)
        self.write(angle,self.Steering)

    def Sync(self):
        counter = 0
        for val in range(100):
            if(val%2==0):
                test = '/dev/ttyUSB{}'
            else:
                test = '/dev/ttyACM{}'
            input = test.format(counter)
            if(val%2==1):
                counter+=1
            try:
                ser = serial.Serial(input)
                print("connected to", input)
                self.findHeader(ser)
                self.found+=1
                if(self.found >= 2):
                    return 
            except Exception as e:
                print(e)
                print("Trying: ", input)
                time.sleep(1)
    
    def everything(self):
        print("Send Everything")
        flagSteering = 0
        steering = 90
        flagSpeed = 1
        speed = 26000
        while(True):
            self.SendSteering(steering)
            self.SendThrottle(speed)

            print(steering)
            if(steering >= 115):
                flagSteering = 0
            elif(steering <= 60):
                flagSteering = 1
            if(flagSteering == 0):
                steering+=-1
            elif(flagSteering == 1):
                steering+=1

            if(speed >= 26500):
                flagSpeed = 0
            elif(speed <= 26000):
                flagSpeed = 1
            if(flagSpeed == 0):
                speed+=-1
            elif(flagSpeed == 1):
                speed += 1
