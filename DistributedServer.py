#####
#
# Server-Side task distributor
#
#####

import time
import zmq

print(f"Start: {time.time}")

context = zmq.Context()

#Sockets to talk with workers
sender = context.socket(zmq.PUSH)
sender.bind("tcp://*:5555")

receiver = context.socket(zmq.PULL)
receiver.bind("tcp://*:5556")

#Send and receive the tasklist from first worker
sender.send(["createList"])
taskList = reciever.recv()
print(f"Returned tasklist: {taskList}")
taskLen = len(taskList)

#send all tasks to works
while taskList:
    sender.send(["evenCalculator",taskList.pop(0)])

#process the returned results
numEven = 0
for taskNum in range(taskLen):
    s = receiver.recv()

    if s == True:
        numEven += 1

print(f"Found {numEven} even numbers")

sender.send(["stop"])

print(f"Script completed at {time.time}")
