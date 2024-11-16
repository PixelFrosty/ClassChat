from socket import socket, AF_INET, SOCK_STREAM
from select import select
from sys import stdin, stdout, exit

serverName = ''
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

acknowledgement = clientSocket.recv(1024).decode()
stdout.write(f"{acknowledgement}")

user = ""

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
                elif data == '%0%':
                    stdout.write(f"\"{user}\" was already taken, please pick another name: ")
                    stdout.flush()
                    user = ""
                # elif user != "":
                else:
                    stdout.write(f"{data}")
                    stdout.flush()
            else:
                s.close()
        elif s == stdin:
            if user == "":
                user = stdin.readline().strip()
                # TODO: check for valid username
                clientSocket.send(("%try_user%" + user).encode())
            else:
                message = stdin.readline()
                clientSocket.send(message.encode())
                if message.strip().lower() == "exit":
                    stdout.write(f"Disconnecting from {clientSocket.getpeername()} \n")
                    stdout.flush()
                    clientSocket.close()
                    exit()
                stdout.write(f"[{user}] {message}")
                stdout.flush()
