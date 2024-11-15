from socket import socket, AF_INET, SOCK_STREAM

# 12000 = TCP socket
# AF_INET for IPV4 address family, SOCK_STREAM for TCP

serverPort = 12000 
serverName = ''

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((serverName,serverPort))

serverSocket.listen(1)
print("The server is ready to recieve")

while True:
        clientSocket, clientAddr = serverSocket.accept()

        print("[Client] ", clientSocket.recv(1024).decode())
        clientSocket.send("Message received".encode())

        clientSocket.close()
