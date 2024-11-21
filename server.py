from socket import SO_REUSEADDR, SOL_SOCKET, socket, AF_INET, SOCK_STREAM
from select import select
from sys import stdin, stdout, exit
from datetime import datetime

serverPort = 12000 
serverName = ''

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind((serverName,serverPort))

sockets = [serverSocket, stdin]
user_list = {}

def getUsers():
    if len(user_list) == 0:
        return "No users currently online.\n"
        
    i = 1
    result = "List of online users:\n"
    for u in user_list.values():
        result += f"[{i}] {u}\n"
        i += 1
    return result

def sout(msg): # ease
    stdout.write(f"[{datetime.now().strftime('%I:%M:%S %p')}] {msg}")
    stdout.flush()

def getKey(v):
    v = v.lower()
    values = list(map(lambda u: u.lower(), user_list.values()))
    keys = list(user_list.keys())

    return keys[values.index(v)]

def removeUser(socket, e):
    try:
        if e == 1:
            pass
        elif e == 0:
            sendToAll(f"---    \033[33m{user_list[socket]}\033[0m has \033[31mdisconnected.\033[0m    ---\n", socket, 1)
        elif e == "":
            sendToAll(f"---    \033[31mDisconnecting\033[0m {user_list[socket]} for exception    ---\n", socket, 1)
        else:
            sendToAll(f"---    \033[31mDisconnecting\033[0m {user_list[socket]} for exception {e}    ---\n", socket, 1)
        del user_list[socket]
    except Exception as e:
         sendToAll("---   A user was \033[31mdisconnected\033[0m for an exception    ---\n", socket, 1)
    sockets.remove(socket)
    socket.close()

def sendToAll(data, sender=serverSocket, echo=0):
    for c in sockets:
        try:
            if c != serverSocket and c != stdin and c != sender:
                c.send(data.encode())
        except Exception as e:
            removeUser(c, e)
    if echo == 1:
        sout(data)

serverSocket.listen(5)
sout(f"\n---    The server is ready to recieve on \033[34m{serverName if serverName != '' else serverSocket.getsockname()[0]} : {serverPort}\033[0m    ---\n\n")

while True:
    readable, writable, exceptional = select(sockets, [], sockets)

    for s in readable:
        try:
            if s == serverSocket:
                clientSocket, clientAddr = serverSocket.accept()
                sout(f"---    \033[32m{clientAddr}\033[0m has connected to the server.    ---\n")
                sendToAll("---    A new user has \033[32mconnected\033[0m    ---\n")
                clientSocket.send("Connection successful.\nEnter your username: ".encode())
                sockets.append(clientSocket)

            elif s == stdin:
                message = stdin.readline()
                if message[:1] == "/":
                    parse =  message.strip().lower()[1:]
                    if parse == "exit":
                        sendToAll(message)
                        sout("Closing Server\n")
                        for c in sockets:
                            if c != serverSocket and c != stdin:
                                removeUser(c, 1)
                        s.close()
                        exit()
                    elif parse == "help":
                        sout("List of commands:\n/help - Show a list of commands.\n/ls - Show all online users.\n/exit - Disconnect all users and close the server.\n")
                    elif parse == "ls":
                        sout(getUsers())
                    else:
                        sout("Invalid command. Try /help for command list\n")
            else:
                try:
                    data = s.recv(1024).decode()
                    if data:
                        if data[:10] == "%try_user%":
                            data = data[10:].strip()
                            if data.lower() in list(map(lambda u: u.lower(),user_list.values())):
                                s.send("%0%".encode()) # tell client to retry
                            else:
                                user_list[s] = data
                                s.send(f"Welcome to the server {data}!\n".encode())
                                sendToAll(f"---    User \033[33m{data}\033[0m entered the chat.    ---\n", s, 1)

                        elif data[:1] == "/":
                            match data[1:].strip().lower():
                                case "exit":
                                    removeUser(s, 0)
                                case "ls":
                                    s.send(getUsers().encode())
                                case "help":
                                    s.send("List of commands:\n/help - Show a list of commands.\n/ls - Show all online users.\n/exit - Disconnect from the server.\n".encode())
                                case _:
                                    s.send("Invalid command. Try /help for command list\n".encode())

                        elif data[:data.find(":")].lower() in list(map(lambda u: u.lower(),user_list.values())):
                            receiver = data[:data.find(":")].strip()
                            getKey(receiver).send(f"[{user_list[s]} to {receiver}] {data[data.strip().find(":") + 1:]}".encode())
                            s.send(f"[{user_list[s]} to {receiver}] {data[data.strip().find(":") + 1:]}".encode())
                            sout(f"[{user_list[s]} to {receiver}] {data[data.strip().find(":") + 1:]}")

                        else:
                            sendToAll(f"[{user_list[s]}] {data}", serverSocket, 1)
                except Exception:
                    continue
        except Exception as e:
            removeUser(s,e)


    for s in exceptional:
        removeUser(s, "")
