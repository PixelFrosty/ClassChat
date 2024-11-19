from socket import socket, AF_INET, SOCK_STREAM
from select import select
from sys import stdin, stdout, exit
from datetime import datetime

def sout(msg): # ease
    stdout.write(f"[{datetime.now().strftime('%I:%M:%S %p')}] {msg}")
    stdout.flush()

serverName = ''
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_STREAM)
try:
    clientSocket.connect((serverName, serverPort))
except Exception:
    sout("Connection was unsuccesful, ceasing process.")
    exit()

acknowledgement = clientSocket.recv(1024).decode()
sout(f"{acknowledgement}")

user = ""

sockets = [clientSocket, stdin]

while True:
    readable, writeable, exceptional = select(sockets, sockets, [])

    for s in readable:
        if s == clientSocket:
            data = s.recv(1024).decode()
            if data:
                if data.strip().lower() == 'exit':
                    sout("Server closed, shutting down app")
                    exit()
                elif data == '%0%':
                    sout(f"\"{user}\" was already taken, please pick another name: ")
                    user = ""
                elif user != "":
                    sout(f"{data}")
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
                    sout(f"Disconnecting from {clientSocket.getpeername()} \n")
                    clientSocket.close()
                    exit()
                sout(f"[{user}] {message}")
