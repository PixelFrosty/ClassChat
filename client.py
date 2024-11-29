from socket import socket, AF_INET, SOCK_STREAM
from select import select
from sys import stdin, stdout, exit
from datetime import datetime
import json

username = ""
signedIn = False

def toJson(status, message, receiver = ""):
    data = {
            "status": str(status),
            "message": message,
            "receiver": receiver,
            "sender": username,
            "time": datetime.now().strftime('%H:%M:%S'),
            }
    return json.dumps(data)


serverName = ''
serverPort = 12000

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverName, serverPort))

sockets = [clientSocket, stdin]

while True:
    readable, writeable, exceptional = select(sockets, [], [])

    for s in readable:
        if s == clientSocket:
            rawdata = s.recv(1024)
            try:
                data = json.loads(rawdata.decode())
                sts = data["status"]
                msg = data["message"]
                if sts == '0':
                    if msg == 'retry':
                        print(f"The username \"{username}\" was already taken.\nPlease enter a different one: ", end="")
                    elif msg == 'accept':
                        print(f"Welcome to the server {username}!")
                        signedIn = True
                    else:
                        print(msg, end="")
                if sts == '1':
                    sndr = data["sender"]
                    rec = data["receiver"]
                    time = data["time"]
                    print(f"[{time}] [{sndr} to {rec}] {msg}", end="")
                if sts == '3':
                    print(msg)
            except json.JSONDecodeError:
                print("not json data")
                s.close()
        elif s == stdin:
            data = stdin.readline()
            if signedIn == False:
                # name not set yet
                username = data.strip()
                clientSocket.send(toJson(0, username).encode())
            else:
                i = data.find(':')
                if i != -1:
                    rec = data[:i]
                    msg = data[i + 2:]
                    clientSocket.send(toJson(1, msg, rec).encode())
                else:
                    print("invalid command")
