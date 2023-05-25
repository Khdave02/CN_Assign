import socket
import errno
import sys
import select

if len(sys.argv) == 3:
    s = socket.socket
    host = sys.argv[1]
    port = int(sys.argv[2])
    selectBuffer = []
    # AF_INET for ipv4 and SOCK_STREAM for TCP
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # s.setblocking(0)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            s.bind((host, port))
            print("Server started")
            print("Socket binded to port:", port)

            selectBuffer.append(s)

            # listen() enables a server to accept() connections.
            # It makes it a “listening” socket
            s.listen()
            print("Listening at {}:{}".format(host, port))

            while True:
                r_sockets, w_sockets, e_sockets = select.select(selectBuffer, [], [])
                for soc in r_sockets:
                    if soc is s:
                        conn, addr = soc.accept()
                        print("Received request from {}".format(addr))
                        selectBuffer.append(conn)
                    elif soc != -1:
                        data = soc.recv(1024)
                        decodedData = data.decode()
                        if data:
                            print("Data received: {}".format(decodedData))
                        else:
                            selectBuffer.remove(soc)
                            soc.close()
                            break

                        # send back string to client
                        soc.send(decodedData.encode())
                        print("Echo Server Response sent = {}".format(decodedData))

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
