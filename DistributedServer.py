#####
#
# Server-Side task distributor
#
#####

import time
import zmq
import asyncio
import zmq.asyncio
from zmq.error import ZMQError

print(f"Start: {str(time.time)}")

context = zmq.Context()

#Sockets to talk with workers
sender = context.socket(zmq.PUSH)
sender.bind("tcp://*:5555")

receiver = context.socket(zmq.PULL)
receiver.bind("tcp://*:5556")

#Send and receive the tasklist from first worker
sender.send_pyobj(["createList"])
taskList = receiver.recv_pyobj()
print(f"Returned tasklist: {taskList}")
taskLen = len(taskList)
processList= []
processCheckout = False
results = []

while len(results) != taskLen:

    #First check for any recieved messages
    try:
        returnMsg = receiver.recv_pyobj(flags=NOBLOCK)
        if returnMsg[0] == "task":
            processList.append(returnMsg[1])
            print(f"{p} has been returned and added to process list")
        elif returnMsg[0] == "process":
            results.append(returnMsg[1])
            processCheckout = False

        #continue to keep checking for receipts before pushing more work
        continue
    except ZMQError:
        pass
    
    #Set a worker on processing results if available
    if processList and not processCheckout:
        try:
            processCheckout = True
            sender.send_pyobj(["evenCalculator",processList.pop(0)],flags=NOBLOCK)
        except ZMQError:
            continue

    #Assign a worker to a task if there is nothing else to do
    if taskList:
        try:
            sender.send_pyobj(["randMultiplier",taskList.pop(0)],flags=NOBLOCK)
        except ZMQError:
            continue


print(f"Found {results.count(True)} even numbers")

sender.send_pyobj(["stop"],flags=NOBLOCK)

print(f"Script completed at {str(time.time)}")
