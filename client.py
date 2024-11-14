from socket import socket, AF_INET, SOCK_STREAM

serverName = ''
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

while True:
    message = input("[You] ")


    clientSocket.send(message.encode())

    confirmation = clientSocket.recv(1024)
    print("[Server] " + confirmation.decode())


    if message.lower() == "exit":
        break

clientSocket.close()
