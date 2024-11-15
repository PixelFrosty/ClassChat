from socket import socket, AF_INET, SOCK_STREAM
from select import select
from sys import stdin, stdout, exit

serverName = ''
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

sockets = [clientSocket, stdin]

while True:
    readable, writeable, exceptional = select(sockets, sockets, [])

    for s in readable:
        if s == clientSocket:
            data = s.recv(1024).decode()
            if data:
                if data.strip().lower() == 'exit':
                    stdout.write("Server closed, shutting down app")
                    stdout.flush()
                    exit()
                stdout.write(f"[Server] {data}")
                stdout.flush()
            else:
                s.close()
        elif s == stdin:
            message = stdin.readline()
            clientSocket.send(message.encode())
            stdout.write(f"[Client] {message}")
            stdout.flush()
            if message.strip().lower() == "exit":
                stdout.write(f"Disconnecting from {clientSocket.getpeername()}")
                stdout.flush()
                clientSocket.close()
                exit()
