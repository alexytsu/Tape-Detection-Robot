import sys
import zmq

port = "8888"

# Socket to talk to server
context = zmq.Context()
socket = context.socket(zmq.SUB)

print ("Collecting updates from weather server...")
socket.connect ("tcp://localhost:%s" % port)

if len(sys.argv) > 2:
    socket.connect ("tcp://localhost:%s" % port1)


topicfilter = "PIDData"
socket.setsockopt_string(zmq.SUBSCRIBE, topicfilter)

# Process 5 updates
total_value = 0
val = 0
while(1):
    string = socket.recv()
    topic, messagedata = string.split()
    val = int(messagedata)
    print (topic, messagedata)

print ("Average messagedata value for topic '%s' was %dF" % (topicfilter, total_value / update_nbr))
