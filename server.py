from socket import SO_REUSEADDR, SOL_SOCKET, socket, AF_INET, SOCK_STREAM
from select import select
from sys import stdin, stdout, exit

# 12000 = TCP socket
# AF_INET for IPV4 address family, SOCK_STREAM for TCP

serverPort = 12000 
serverName = ''

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1) # without this, socket takes time before usable
serverSocket.bind((serverName,serverPort))

sockets = [serverSocket, stdin]
user_list = {1:"ethan"}

serverSocket.listen(1)
print(f"---    The server is ready to recieve on \033[34m{serverName if serverName != '' else serverSocket.getsockname()[0]} : {serverPort}\033[0m    ---")

while True:
    readable, writable, exceptional = select(sockets, [], [])

    for s in readable:
        if s == serverSocket:
            clientSocket, clientAddr = serverSocket.accept()
            stdout.write(f"---     \033[32m{clientAddr}\033[0m has connected to the server.    ---\n")
            stdout.flush()
            clientSocket.send("Connection successful.\nEnter your username: ".encode())
            sockets.append(clientSocket)

        elif s == stdin:
            message = stdin.readline()
            for c in sockets:
                if c != serverSocket and c != stdin:
                    if message.strip().lower() == "exit":
                        c.send(message.encode())
                    else:
                        c.send(("[Server]" + message).encode())
            stdout.write(f"[Server] {message}")
            stdout.flush()
            if message.strip().lower() == "exit":
                stdout.write("Closing Server")
                stdout.flush()
                for c in sockets:
                    if c != serverSocket and c != stdin:
                        c.close()
                        del user_list[c]
                        sockets.remove(c)
                s.close()
                exit()
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
                            stdout.write(f"---    User \033[33m{data}\033[0m entered the chat.    ---\n")
                            stdout.flush()
                            # TODO: setup disconnecting users, and also do the logic for this on the client side 

                    elif data.strip().lower() == "exit":
                        stdout.write(f"\033[33m{user_list[s]}\033[0m has \033[31mdisconnected.\033[0m\n")
                        stdout.flush
                        del user_list[s]
                        sockets.remove(s)
                        continue

                    else:
                        stdout.write(f"[{user_list[s]}] {data}")
                        stdout.flush
                        # s.send("Message received\n".encode())
            except Exception:
                continue

    for s in exceptional:
        print(f"\033[31mDisconnecting\033[0m {user_list[s]} for exception\n")
        del user_list[s]
        sockets.remove(s)

