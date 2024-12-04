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
        if type(user) == str:
            lowernames = list(map(lambda u: u.lower(), names))
            i = lowernames.index(user.lower())
            return names[i]
        elif type(user) == socket:
            socks = list(users.values())
            i = socks.index(user)
            return names[i]
        return "-1"
    except:
        return "-1"

def removeUser(socket):
    user = name(socket)
    del users[user]
    sockets.remove(socket)

def listUsers():
    if len(users) == 0:
        return "\nNo users currently online.\n"
    lu = "\nList of currently online users:"
    i = 1
    for c in users.keys():
        lu += f"\n[{i}] {c}"
        i += 1
    return lu + "\n"
 
serverPort = 12000 
serverName = ''

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind((serverName,serverPort))

sockets = [serverSocket, stdin]
user_list = {}

users = {}
# dictionary of users "username": socket

serverSocket.listen(5)
print(f"The server is ready to recieve on {serverName if serverName != '' else 'localhost'} : {serverPort}")

try:
    while True:
        readable, writable, exceptional = select(sockets, [], sockets)

        for s in readable:
            if s == serverSocket:
                clientSocket, clientAddr = serverSocket.accept()
                print(f"--- {clientAddr} has connected to the server. ---")
                clientSocket.send(toJson(0, "Connection successful\nEnter your name: ").encode())

                sockets.append(clientSocket)
            elif s == stdin:
                data = stdin.readline()
                if data[0] == "/":
                    cmd = data[1:].strip().lower()
                    match cmd:
                        case "exit":
                            print("\nDisconnecting all clients...")
                            for c in users.copy():
                                sock = users[c]
                                sock.send(toJson(2, "shutdown").encode())
                                removeUser(sock)
                            print("\nAll users disconnected, shutting down.")
                            serverSocket.close()
                            exit()
                        case "list":
                            print(listUsers())
                        case "help":
                            print(
                                    "\nList of commands:\n"
                                    "- /help | Shows list of commands.\n"
                                    "- /list | Shows list of online users.\n"
                                    "- /kick | Kick the specified user\n"
                                    "- /exit | Shutdown the server.\n"
                                  )
                        case _:
                            if cmd[:4] == 'kick':
                                try:
                                    user = name(cmd[5:].strip())
                                    sock = users[user]
                                    print(f"Kicked {sock.getpeername()} aka {user} from the server.")
                                    sock.send(toJson(2, "kick").encode())
                                    removeUser(sock)
                                except:
                                    print("Cannot kick, invalid user.\nUsage of /kick | /kick {username}")
                            else:
                                print("Invalid command, check /help")
                else:
                    print("Invalid command, check /help")
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
                                if rec.lower() == 'all':
                                    newdata = toJson(1, msg, time, "all users", sndr)
                                    for c in users.values():
                                        c.send(newdata.encode())
                                    print(f"[{time}] [{sndr} to all users] {msg}", end="")
                                else:
                                    newdata = toJson(1, msg, time, name(rec), sndr)
                                    users[name(rec)].send(newdata.encode())
                                    s.send(newdata.encode())
                                    print(f"[{time}] [{sndr} to {name(rec)}] {msg}", end="")
                            except Exception as e:
                                print(f"[{time}] Failed to forward message from {sndr} to {rec}. (Recipient not online)")
                                s.send(toJson(3, f"Failed to send message, {rec} is not currently online.").encode())
                                continue
                        if sts == '0':
                            if name(msg) in users.keys():
                                s.send(toJson(0, "retry").encode())
                                # name already taken
                            else:
                                s.send(toJson(0, "accept").encode())
                                users[msg] = s
                                print(f"--- User {s.getpeername()} has joined as \"{msg}\" ---")
                                # add user to list
                                # dictionary element "username": socket
                        if sts == '3':
                            if msg[:4] == 'exit':
                                print(f"User {s.getpeername()} aka {sndr} has disconnected", end="")
                                s.send(toJson(2, "exit").encode())
                                removeUser(s)
                                if msg[4:] == '_error':
                                    print("due to an error")
                                else:
                                    print()
                            if msg == 'list':
                                s.send(toJson(3, listUsers()).encode())
                                print(f"Listing all users for {sndr}")
                    except json.JSONDecodeError:
                        print("not json data")
except Exception as e:
    print("\nError occured, disconnecting all clients...")
    for c in users.copy():
        sock = users[c]
        sock.send(toJson(2, "shutdown").encode())
        removeUser(sock)
    print("\nAll users disconnected, shutting down.")
    serverSocket.close()
    exit()
except KeyboardInterrupt as e:
    print("\nProcess interrupted. Disconnecting all clients...")
    for c in users.copy():
        sock = users[c]
        sock.send(toJson(2, "shutdown").encode())
        removeUser(sock)
    print("\nAll users disconnected, shutting down.")
    serverSocket.close()
    exit()
