import socket
from _thread import *
import threading
import sys
import errno


def threaded(c, addr,count_of_threads):
    while True:
        try:
            data = c.recv(1024)
            decodedData = data.decode()
            # print(data)
            if data:
                print("Data received: {}".format(decodedData))
            else:
                # print_lock.release()
                break
            if decodedData == "close":
                    print(f'Connection closed by {addr}')
                    print(f"Thread {count_of_threads} closed")
                    with threading.Lock():
                        count_of_threads-=1
                    break
            # DO MATHS HERE
            try:
                result = str(eval(decodedData))
            except SyntaxError:
                c.send("SyntaxError".encode())
            c.send(str(result).encode())
        except (ZeroDivisionError):
            c.send("ZeroDiv".encode())
        except (ArithmeticError):
            c.send("MathError".encode())
        except (SyntaxError):
            c.send("SyntaxError".encode())
        except (NameError):
            c.send("NameError".encode())
        except KeyboardInterrupt:
            print("Ctrl C detected, Exiting..")
                

    # connection closed
    c.close()

if len(sys.argv) == 3:
    s = socket.socket
    host = sys.argv[1]
    port = int(sys.argv[2])
    count_of_threads = 0 # count of threads

    # AF_INET for ipv4 and SOCK_STREAM for TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:

        try:
            print("Server Started")
            s.bind((host, port))
            
            print("Socket binded to port:", port)
            s.listen()
            print("{}:{} is listening".format(host, port))

            # a forever loop until client wants to exit
            while True:
                # returns a new socket object and a tuple holding the (host, port) of the client
                c, addr = s.accept()
                print('Connected to: ' + addr[0] + ':' + str(addr[1]))
                threading.Thread(target=threaded, args=(c, addr,count_of_threads)).start()
                count_of_threads += 1
                print('Thread Number: ' + str(count_of_threads))

        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                print("Port {} is already in use".format(port))
            else:
                # something else raised the socket.error exception
                print(e)
        except KeyboardInterrupt:
            print("Ctrl C detected, Exiting..")

    s.close()
else:
    print("Invalid Arguments: python server2.py 'address' 'port'")

