from socket import SO_REUSEADDR, SOL_SOCKET, socket, AF_INET, SOCK_STREAM
from select import select
from sys import stdin, stdout, exit
from datetime import datetime
import json

def toJson(status, message, time = "", receiver = "", sender = ""):
    data = {
            "status": str(status),
            "message": message,
            "receiver": receiver,
            "sender": sender,
            }
    if time == "":
        data["time"] = datetime.now().strftime('%H:%M:%S')
    else:
        data["time"] = time
    return json.dumps(data)

def name(user):
    try:
        names = list(users.keys())
        lowernames = list(map(lambda u: u.lower(), names))
        i = lowernames.index(user.lower())
        return names[i]
    except:
        return "-1"

serverPort = 12000 
serverName = ''

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind((serverName,serverPort))

sockets = [serverSocket, stdin]

users = {}
# dictionary of users "username": socket

serverSocket.listen(5)
print(f"The server is ready to recieve on {serverName if serverName != '' else 'localhost'} : {serverPort}")

while True:
    readable, writable, exceptional = select(sockets, [], [])

    for s in readable:
        if s == serverSocket:
            clientSocket, clientAddr = serverSocket.accept()
            print(f"--- {clientAddr} has connected to the server. ---")
            clientSocket.send(toJson(0, "Connection successful\nEnter your name: ").encode())

            sockets.append(clientSocket)
        elif s == stdin:
            data = stdin.readline()
        else:
            rawdata = s.recv(1024)
            if rawdata:
                try:
                    data = json.loads(rawdata.decode())
                    sts = data["status"]
                    msg = data["message"]
                    sndr = data["sender"]
                    rec = data["receiver"]
                    time = data["time"]

                    if sts == '1':
                        try:
                            newdata = toJson(1, msg, time, name(rec), sndr)
                            users[name(rec)].send(newdata.encode())
                            s.send(newdata.encode())
                            print(f"[{time}] [{sndr} to {name(rec)}] {msg}", end="")
                        except Exception as e:
                            print(f"invalid user, cannot send \"{msg.strip()}\" by \"{sndr}\" to \"{rec}\" ")
                            s.send(toJson(3, "Unable to send message, user not online or doesn't exist.").encode())
                            continue
                    if sts == '0':
                        if name(msg) in users.keys():
                            s.send(toJson(0, "retry").encode())
                            # name already taken
                        else:
                            s.send(toJson(0, "accept").encode())
                            users[msg] = s
                            print(f"--- User {s.getsockname()} has joined as \"{msg}\" ---")
                            # add user to list
                            # dictionary element "username": socket
                except json.JSONDecodeError:
                    print("not json data")

