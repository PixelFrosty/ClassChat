from socket import SO_REUSEADDR, SOL_SOCKET, socket, AF_INET, SOCK_STREAM
from select import select
from sys import stdin, stdout, exit

# 12000 = TCP socket
# AF_INET for IPV4 address family, SOCK_STREAM for TCP

serverPort = 12000 
serverName = ''

serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
serverSocket.bind((serverName,serverPort))

sockets = [serverSocket, stdin]

serverSocket.listen(1)
print(f"The server is ready to recieve on {serverName if serverName != '' else 'localhost'} : {serverPort}")

while True:
    readable, writable, exceptional = select(sockets, [], [])

    for s in readable:
        if s == serverSocket:
            clientSocket, clientAddr = serverSocket.accept()
            stdout.write(f"\n{clientAddr} has connected to the server.\n\n")
            stdout.flush()
            clientSocket.send("Connection successful\n".encode())

            sockets.append(clientSocket)
        elif s == stdin:
            message = stdin.readline()
            for c in sockets:
                if c != serverSocket and c != stdin:
                    c.send(message.encode())
            stdout.write(f"[Server] {message}")
            stdout.flush()
            if message.strip().lower() == "exit":
                stdout.write("Closing Server")
                stdout.flush()
                for c in sockets:
                    if c != serverSocket and c != stdin:
                        c.close()
                        sockets.remove(c)
                s.close()
                exit()
        else:
            try:
                data = s.recv(1024).decode()
                if data:
                    if data.strip().lower() == "exit":
                        stdout.write(f"{s.getpeername()} is disconnecting\n")
                        stdout.flush
                        sockets.remove(s)
                        continue
                    stdout.write(f"[Client] {data}")
                    stdout.flush
                    s.send("Message received\n".encode())
            except Exception:
                continue

    for s in exceptional:
        print(f"Disconnecting {s.getpeername()} for exception")
        sockets.remove(s)

