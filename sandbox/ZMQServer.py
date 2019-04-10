import zmq
import random
import sys
import time

port = "8888"
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:%s" % port)
topic = "PIDData"
while True:
    messagedata = random.randrange(1,215)
    print ("{} {}".format(topic, messagedata))
    socket.send_string("{} {}".format(topic, messagedata))

socket.close(port)
