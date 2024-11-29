from socket import socket, AF_INET, SOCK_STREAM
from select import select
from sys import stdin, stdout, exit
from datetime import datetime
import json

def sout(msg): # ease
    stdout.write(f"[{datetime.now().strftime('%I:%M:%S %p')}] {msg}")
    stdout.flush()

def toJson(status: int, message: str, receiver: str = "", sender: str = ""):
    # quick function to convert data to json format
    # status guide:
        # 0 = name request, only send status and message (the name)
        # 1 = message
        # 2 = command request, only send status and message (the command)
    data = {"status": str(status)}
    data["time"] = datetime.now().strftime('%Y-%-m-%-d | %H:%M:%S')
    if status == 1:
        data["receiver"] = receiver
        data["sender"] = sender
    data["message"] = message
    # time seperated by pipe

    return json.dumps(data)

serverName = ''
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_STREAM)
try:
    clientSocket.connect((serverName, serverPort))
except Exception:
    sout("Connection was unsuccesful, please try again later.")
    exit()

acknowledgement = clientSocket.recv(1024).decode()
sout(f"{acknowledgement}")

user = ""
# username

sockets = [clientSocket, stdin]

while True:
    readable, writeable, exceptional = select(sockets, sockets, [])

    for s in readable:
        if s == clientSocket:
            data = s.recv(1024).decode()
            if data:
                if data.strip().lower() == '/exit':
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
                clientSocket.send(toJson(0, user).encode())
                # clientSocket.send(("%try_user%" + user).encode())
            else:
                data = stdin.readline()
                # clientSocket.send(message.encode())
                m = data.find(":")
                if m != -1:
                    receiver = data[:m] # everthing before :
                    message = data[m+2:] # everything after :
                    clientSocket.send(toJson(1, message, receiver, user).encode())
                    sout(f"[{user}] {message}")
