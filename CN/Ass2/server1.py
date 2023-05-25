import socket
import errno
import sys

if len(sys.argv) == 3:
    host = sys.argv[1]
    port = int(sys.argv[2])
    # AF_INET for ipv4 and SOCK_STREAM for TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            print("Server Started")
            s.bind((host, port))
            s.listen()
            print("Socket binded to port:", port)

            while True:
                print("Server Listening on {}:{}".format(host, port))
                # returns a new socket object and a tuple holding the (host, port) of the client
                conn, addr = s.accept()

                with conn:
                    print("Connected to {}".format(addr))
                    # Receiving data

                    while True:
                        try:
                            data = conn.recv(1024)
                            decodedData = data.decode()
                            if data:
                                print("Data received from : {} is : {}".format(addr,decodedData))
                            else:
                                break
                            try:
                                result = eval(data)
                            except SyntaxError:
                                conn.send("SyntaxError".encode())
                            conn.send(str(result).encode())
                        # Handling other possible errors
                        except (ZeroDivisionError):
                            conn.send("ZeroDiv".encode())
                        except (ArithmeticError):
                            conn.send("MathError".encode())
                        except (SyntaxError):
                            conn.send("SyntaxError".encode())
                        except (NameError):
                            conn.send("NameError".encode())

                        # Sending the result to the client
                        print("Response sent to {} = {}".format(addr, result))
                # Closing the connection
                conn.close()

        except socket.error as e:
            if e.errno == errno.EADDRINUSE:
                print("Port {} is already in use".format(port))
            else:
                # something else raised the socket.error exception
                print(e)
        # Exiting the program if Ctrl+C is pressed
        except KeyboardInterrupt:
            print("Ctrl C detected, Exiting..")
    s.close()

else:
    print("Invalid Arguments: python server1.py 'address' 'port'")
