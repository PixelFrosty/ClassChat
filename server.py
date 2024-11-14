from socket import socket, AF_INET, SOCK_STREAM
from select import select

# 12000 = TCP socket
# AF_INET for IPV4 address family, SOCK_STREAM for TCP

serverPort = 12000 
serverName = ''

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((serverName,serverPort))

serverSocket.listen(1)
print("The server is ready to recieve")
serverSocket.setblocking(False)

read = [serverSocket]
write = []
exc = []

# main loop to keep server alive

try:
    while True:

        readable, writable, exceptional = select(read, write, exc)

        for s in readable:
            if s == serverSocket:
                clientSocket, clientAddr = serverSocket.accept()
                clientSocket.setblocking(False)
                print(str(clientAddr) + " just connected")
                read.append(clientSocket)
            else:
                try:
                    message = s.recv(1024).decode()
                    if message:
                        print("[" + str(s.getpeername()) + "] " + message)
                        s.sendall("received".encode())
                    else:
                        print("[" + str( s.getpeername() ) + "] disconnected")
                        read.remove(s)
                        s.close()
                except Exception as e:
                    print( str( s.getpeername() ) + " had an error: " + str(e))
                    read.remove(s)
                    s.close()
        for s in exceptional:
            print( str( s.getpeername() ) + " had an error: ")
            read.remove(s)
            s.close()
except KeyboardInterrupt:
    print(" [Closing server]")
    serverSocket.close()

