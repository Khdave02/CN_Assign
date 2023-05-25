import socket
import sys

# Checking if correct number of arguments are passed in command line
if len(sys.argv) == 3:
    # Setting the HOST IP address from command line argument
    HOST = sys.argv[1]
    # Setting the port number from command line argument
    PORT = int(sys.argv[2])

    # Creating an IPv4 TCP socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Client times out if connection is not accepted within 4 seconds
        s.settimeout(4)
        try:
            s.connect((HOST, PORT))
        except ConnectionRefusedError:
            print('Server not running')
        # Attempting to connect to the server
        else:
            print("Connected to {}:{}".format(HOST, PORT))
            try:
                while True:

                    # Prompt user for calculation request
                    request = input('Enter a calculation: ')

                    # Send request to server
                    s.sendall(request.encode())
                    print("Sending {} to {}:{}".format(request, HOST, PORT))

                    # Receive response from server
                    try:
                        # recv() takes buffersize as argument
                        data = s.recv(1024).decode()

                    except socket.timeout:
                        print('Server busy, please try again later')
                        s.close()
                        break
                    # Handling errors returned by the server
                    if data == "ZeroDiv":
                        print("You can't divide by 0, try again")
                    elif data == "MathError":
                        print("There is an error with your math, try again")
                    elif data == "SyntaxError":
                        print("There is a syntax error, please try again")
                    elif data == "NameError":
                        print("You did not enter an equation, try again")
                    else:
                        # Printing the received data from the server
                        print("Received : {} from {}:{}".format(
                            repr(data), HOST, PORT))
                # Closing the socket and printing message
                s.close()
                print("Connection closed to {}:{}".format(HOST, PORT))
            # Handling Keyboard interrupt exception
            except KeyboardInterrupt:
                print('Client terminated')
                request = 'close'
                s.sendall(request.encode('utf-8'))
                s.close()
            except (IndexError, ValueError):
                print("You did not specify a correct IP address or PORT number")

else:
    print("Invalid Arguments: python client.py 'HOST' 'PORT' 'equation'")
