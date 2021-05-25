######
#
# Client-Side script that gathers tasks from server and distributes them for processing to the cores on the client machine
#
#####

import zmq
import sys
from random import randrange, randint
from time import sleep

def set_id(zsocket):
    """Set simple random printable identity on socket"""
    identity = u"%04x-%04x" % (randint(0, 0x10000), randint(0, 0x10000))
    zsocket.setsockopt_string(zmq.IDENTITY, identity)

#Functions that we will want to run once connected to server
def createList():
    list = []
    for number in range(15):
        list.append(randrange(10))
    return list

def evenCalculator(i):
    sleep(4)
    if i %2 == 0:
        return True
    else:
        return False

def randMultiplier(i):
    sleep(2)
    return i * randrange(5)

context = zmq.Context()

#  Sockets to talk to server
print("Connecting to server...")
receiver = context.socket(zmq.REQ)
set_id(receiver)
receiver.connect("tcp://localhost:5555")

while True:
    #Tell server we are ready to collect something new
    receiver.send_pyobj(["ready"])

    #Collect tasks from the server
    s = receiver.recv_pyobj()

    # Simple progress indicator for the viewer
    sys.stdout.write('.')
    sys.stdout.flush()

    print(f"Received {s} from the server.")
    #Determine which task should be run
    if s[0] == "createList":
        receiver.send_pyobj(createList())
        print("Successfully sent task list.")
        receiver.recv()
    elif s[0] == "evenCalculator":
        receiver.send_pyobj( ["process",evenCalculator(s[1])] )
        print("Sent evenCalculator return.")
        receiver.recv()
    elif s[0] == "randMultiplier":
        receiver.send_pyobj( ["task",randMultiplier(s[1])] )
        print("Sent random multiplier return.")
        receiver.recv()
    elif s[0] == "wait":
        sleep(5)
        continue
    elif s[0] == "stop":
        break

print("All tasks completed successfully...")
