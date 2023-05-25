# import necessary libraries
import threading
import time
import math
import sys
from queue import Queue
import copy

# helper function to get the numerical value of a character
def get_ord(name):
    return (ord(name) - 65)

# helper function to get the character value of a numerical value
def get_char(num):
    return chr(num + 65)

# router class
class router:
    def __init__(self, name):
        self.name = name
        self.id = get_ord(name)  # unique identifier for the router
        self.fwd = dict([(i, math.inf) for i in range(no_of_nodes)]) # routing table initialized with infinite values
        self.fwd[self.id] = -1 # distance to self is 0, marked with -1
        self.next_hop = [-1 for i in range(no_of_nodes)] 
        self.neighbors = [] # list of neighboring routers
        self.updated = [] # list of routers whose distance values have been updated
        self.lock = threading.Lock() # lock for concurrency

# Bellman-Ford algorithm to calculate shortest paths for router i
def Bellman_Ford(routers, i):
    # Create a copy of the router's forwarding table
    temp_fwd = copy.deepcopy(routers[i].fwd)
    
    # continue updating routing table while there are entries in the queue
    while not queueList[i].empty():
        next_fwd = queueList[i].get() # get the next entry in the queue
        received_from = -1

        # find the router from which the update was received
        for j in range(no_of_nodes):
            if next_fwd[j] == -1:
                received_from = j

        # update distance values for all routers in the routing table
        for j in range(no_of_nodes):
            if j != received_from:
                routers[i].lock.acquire() # acquire lock
                if temp_fwd[j] > routers[i].fwd[received_from] + next_fwd[j]:
                    temp_fwd[j] = routers[i].fwd[received_from] + next_fwd[j]
                    routers[i].next_hop[j] = received_from
                routers[i].lock.release() # release lock

        # add routers whose distance values have changed to the updated list
        for j in range(no_of_nodes):
            if routers[i].fwd[j] != temp_fwd[j]:
                routers[i].updated.append(j)
    routers[i].lock.acquire() # acquire lock
    routers[i].fwd = dict(temp_fwd)    # update the router's routing table
    routers[i].lock.release() # release lock

# function to propagate routing updates to neighboring routers of router i
def Propagate(routers, i):
    # send a copy of the router's routing table to all neighboring routers
    for nei in routers[i].neighbors:
        queueList[nei].put(copy.deepcopy(routers[i].fwd))

    # wait for all neighboring routers to receive the update
    while True:
        if queueList[i].full():
            break

    locks = [routers[j].lock for j in routers[i].neighbors] #locks of all the neighbor routers of a router specified by the index i.
    for lock in locks:
        lock.acquire()

    # update the router's routing table using Bellman-Ford algorithm
    Bellman_Ford(routers, i)

    for lock in locks:
        lock.release()

    # clear the queue of received updates
    queueList[i].queue.clear()

    # wait for 2 seconds before propagating next update
    time.sleep(2)

# main function
if __name__ == '__main__':
    inp = sys.argv[1] # get the input file name from command line argument
    with open(inp, "r") as f:
        no_of_nodes = int(f.readline()) # read the number of nodes from input file
        nodes = f.readline().split() # read the node names from input file
        routers = [router(node) for node in nodes] # create a router object for each node
        
        line = f.readline()
        while line != "EOF":
            from_edge, to_edge, weight = line.split()
            routers[get_ord(from_edge)].fwd[get_ord(to_edge)] = int(weight)
            routers[get_ord(from_edge)].neighbors.append(get_ord(to_edge))
            routers[get_ord(from_edge)].next_hop[get_ord(to_edge)] = get_ord(to_edge)
            sorted(routers[get_ord(from_edge)].neighbors)

            routers[get_ord(to_edge)].fwd[get_ord(from_edge)] = int(weight)
            routers[get_ord(to_edge)].neighbors.append(get_ord(from_edge))
            routers[get_ord(to_edge)].next_hop[get_ord(from_edge)] = get_ord(from_edge)
            sorted(routers[get_ord(to_edge)].neighbors)
            line = f.readline()
    queueList = [Queue(maxsize = len(routers[i].neighbors)) for i in range(no_of_nodes)]

    # Printing initial routing table for each router
    print("\nInitialised input:")
    print_str = ""
    for i in range(no_of_nodes):
        print_str += f"\nRouting table of router {routers[i].name}:"
        for key, item in routers[i].fwd.items():
            if key != i:
                print_str += "\n" + str(get_char(key)) + " -- " + str(item)
    print(print_str)

    iter = int(input("enter No of iterations: "))
    # Run iterations of the distributed Bellman-Ford algorithm
    for k in range(iter):
        for i in range(no_of_nodes):
            # Create a thread for propagating routing information to neighbors of the current router
            thread = threading.Thread(target = Propagate, args = (routers, i))
            thread.start()
        # Wait for all threads to finish executing before moving on to the next iteration
        thread.join()

        itrLock = threading.Lock()
        itrLock.acquire()
        # Print the current iteration number
        print("==================================================")
        print("                  Iteration " + str(k + 1))
        print("==================================================")
        itrLock.release()

        # Print the updated routing table for each router
        print_str = ""
        for i in range(no_of_nodes):
            print_str += f"\nRouting table of router {routers[i].name} with next hop:"
            for key, item in routers[i].fwd.items():
                if key != i:
                    print_str += "\n"
                    if key in routers[i].updated:
                        # Add a marker (*) to indicate that this entry has been updated during the current iteration
                        print_str += "  *"
                    print_str += "\t" + str(get_char(key)) + " -- " + str(item)
                    print_str += " -- " + str(get_char(routers[i].next_hop[key]))
            routers[i].updated.clear()
            # Print the final routing table for this iteration
        print(print_str + "\n\n")