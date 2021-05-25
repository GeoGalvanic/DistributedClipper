######
#
# Client-Side script that gathers tasks from server and distributes them for processing to the cores on the client machine
#
#####

import zmq
from random import randrange
from time import sleep

#Functions that we will want to run once connected to server
def createList():
    list = []
    for number in range(10):
        list.append(randrange(10))
    return list

def evenCalculator(i):
    if i %2 == 0:
        return True
    else:
        return False

context = zmq.Context()

#  Sockets to talk to server
print("Connecting to server...")
receiver = context.socket(zmq.PULL)
receiver.connect("tcp://10.0.2.2:5555")

sender = context.socket(zmq.PUSH)
sender.connect("tcp://10.0.2.2:5555")

while True:
    #Collect tasks from the server
    s = receiver.recv()

    # Simple progress indicator for the viewer
    sys.stdout.write('.')
    sys.stdout.flush()

    print(f"Received {s} from the server.")
    #Determine which task should be run
    if s[0] == "createList":
        sender.send(createList)
        print("Successfully sent task list.") 
    elif s[0] == "evenCalculator":
        sender.send(evenCalculator(s[1]))
        print("Sent evenCalculator return.")
    elif s[0] == "wait":
        sleep(5)
        continue
    elif s[0] == "stop":
        break

print("All tasks completed successfully...")
