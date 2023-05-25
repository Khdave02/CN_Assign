import socket
import errno
import sys
import select

# Check if both IP address and port are passed as command line arguments
if len(sys.argv) == 3:
    # Create a new socket object
    s = socket.socket
    # Extract IP address and port from command line arguments
    host = sys.argv[1]
    port = int(sys.argv[2])
    selectBuffer = []
    # AF_INET for ipv4 and SOCK_STREAM for TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Set socket to reuse the address and prevent the "address already in use" error
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, port))
            print("Server started")
            print("Socket binded to port:", port)

            selectBuffer.append(s)

            s.listen()
            print("Listening at {}:{}".format(host, port))

            while True:
                #rlist: wait until ready for reading
                # wlist: wait until ready for writing
                # xlist: wait for an “exceptional condition” 
                # Use the select function to wait for incoming data on the selectBuffer
                r_sockets, w_sockets, e_sockets = select.select(selectBuffer, [], [])

                for soc in r_sockets:
                    # Check if the incoming connection is from the server socket
                    if soc is s:
                        conn, addr = soc.accept()
                        # conn.setblocking(0)
                        print("Received request from {}".format(addr))
                        # Add the new client socket to the select buffer
                        selectBuffer.append(conn)
                    
                    elif soc != -1:
                        data = soc.recv(1024)
                        decodedData = data.decode()
                        # print(data)
                        if data:
                            print("Data received: {}".format(decodedData))
                        else:
                            # If the client socket is closed, remove it from the select buffer and close the socket
                            selectBuffer.remove(soc)
                            soc.close()
                            break
                        # Evaluate the mathematical expression received from the client
                        try:
                            result = str(eval(decodedData))
                        
                        except (ZeroDivisionError):
                            result = "ZeroDiv"
                        except (ArithmeticError):
                            result = "MathError"
                        except (SyntaxError):
                            result = "SyntaxError"
                        except (NameError):
                            result = "NameError"
                        # send back string to client
                        soc.send(result.encode())
                        print("Response sent = {}".format(result))

                    # connection closed

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
    print("Invalid Arguments: python server4.py 'address' 'port'")
