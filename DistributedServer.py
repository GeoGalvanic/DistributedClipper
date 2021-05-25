#####
#
# Server-Side task distributor
#
#####

import time
import zmq
from zmq.error import ZMQError

print(f"Start: {str(time.time)}")

context = zmq.Context()

#Sockets to talk with workers
sender = context.socket(zmq.ROUTER)
sender.bind("tcp://*:5555")

#Send and receive the tasklist from first worker
address, empty, ready = sender.recv(), sender.recv(), sender.recv()

sender.send(address,flags=2)
sender.send(b"",flags=2)
sender.send_pyobj(["createList"])

address, empty, taskList = sender.recv(), sender.recv(), sender.recv_pyobj()
#release the worker back to ready status
sender.send(address,flags=2)
sender.send(b"",flags=2)
sender.send_pyobj(b"Return to Ready")

#Define extra variables for list logic
taskLen = len(taskList)
processList= []
processCheckout = False
results = []

while len(results) != taskLen:
    #Find workers looking for the server and determine if they have results or need to be assigned work
    address, empty, message = sender.recv(), sender.recv(), sender.recv_pyobj()

    if message[0] == "ready":
        #Set a worker on processing results if available
        if processList and not processCheckout:
            processCheckout = True
            sender.send(address,flags=2)
            sender.send(b"",flags=2)
            sender.send_pyobj(["evenCalculator",processList.pop(0)])
            continue
        
        #Assign to do a task if there are any left
        if taskList:
            sender.send(address,flags=2)
            sender.send(b"",flags=2)
            sender.send_pyobj(["randMultiplier",taskList.pop(0)])
            continue

        #Tell the worker to wait if we have nothing for it to do
        sender.send(address,flags=2)
        sender.send(b"",flags=2)
        sender.send_pyobj(["wait"])
        continue

    if message[0] == "process":
        #check for processing workers that are returning results
        results.append(message[1])
        processCheckout = False

        #release the worker back to ready status
        sender.send(address,flags=2)
        sender.send(b"",flags=2)
        sender.send_pyobj(b"Return to Ready")
        continue

    if message[0] == "task":
        #check for tasked workers returning data that needs to be processed
        processList.append(message[1])
        print(f"{message[1]} has been returned and added to process list")
        #release the worker back to ready status
        sender.send(address,flags=2)
        sender.send(b"",flags=2)
        sender.send_pyobj(b"Return to Ready")

#Print our result
print(f"Found {results.count(True)} even numbers")

#Close out workers
time.sleep(5)
while True:
    try:
        address, empty, ready = sender.recv(flags=1), sender.recv(flags=1), sender.recv(flags=1)
    except ZMQError:
        break

    sender.send(address,flags=2)
    sender.send(b"",flags=2) 
    sender.send_pyobj(["stop"])


print(f"Script completed at {str(time.time)}")
