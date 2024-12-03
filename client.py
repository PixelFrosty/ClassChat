from socket import socket, AF_INET, SOCK_STREAM
from re import match
from sys import stdin, exit
from datetime import datetime
import threading
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

serverName = 'localhost'
serverPort = 12000

try:
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
except:
    print("Unable to connect to server.\nTry again later.")
    exit()

stop = True

def outgoingData():
    global username
    global signedIn
    global clientSocket
    global stop
    try:
        while stop:
            rawdata = clientSocket.recv(1024)
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
                if sts == '2':
                    if msg == 'shutdown':
                        print("\nServer is shutting down.")
                        print("Press \"Enter\" to exit.")
                        stop = False
                        clientSocket.close()
                        break
                    elif msg == 'kick':
                        print("\nYou have been kicked from the server.")
                        print("Press \"Enter\" to exit.")
                        stop = False
                        clientSocket.close()
                        break

                if sts == '3':
                    print(msg)
            except json.JSONDecodeError:
                print("not json data")
                clientSocket.close()
    except:
        pass

def incomingData():
    global username
    global stop
    while stop:
        data = stdin.readline()
        if stop == False:
            break
        if data:
            if signedIn == False:
                # name not set yet
                username = data.strip()
                if bool(match(r"^[a-zA-Z0-9-_'\s]+$", username)):
                    if username.lower() == 'all':
                        print("Invalid username.\nPlease enter a different one: ", end="")
                        continue
                    clientSocket.send(toJson(0, username).encode())
                else:
                    print("Invalid.\nUsername must only contain letters, numbers, -, _, ', and spaces.\nPlease enter a different one: ", end="")
            else:
                if data[0] == "/":
                    cmd = data[1:].strip().lower()
                    match cmd:
                        case "exit":
                            print("\nDisconnecting from server")
                            clientSocket.send(toJson(3, "exit").encode())
                            stop = False
                            clientSocket.close()
                            break
                        case "list":
                            clientSocket.send(toJson(3, "list").encode())
                        case "help":
                            print(
                                    "\nList of commands:\n"
                                    "- /help | Shows list of commands.\n"
                                    "- /list | Shows list of online users.\n"
                                    "- /exit | Disconnect from the server.\n\n"
                                    "Send messages by specifying a user followed by : and your message.\n"
                                    "Example: \"John Doe: Hey there John.\"\n"
                                    "\nTo send messages to all, put \"all\" as your recipient"
                                  )
                        case _:
                            print("Invalid command, check /help")
                else:
                    i = data.find(':')
                    if i != -1:
                        rec = data[:i]
                        msg = data[i + 2:]
                        if rec.lower() == username.lower():
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] [Echoing to self] {msg}", end="")
                        else:
                            clientSocket.send(toJson(1, msg, rec).encode())
                    else:
                        print("Invalid input, specify a user followed by : to send a message.")
                        print("Alternatively, check /help for commands.")

try:
    inputHandler = threading.Thread(target=outgoingData)
    serverDataHandler = threading.Thread(target=incomingData)

    inputHandler.start()
    serverDataHandler.start()

    inputHandler.join()
    serverDataHandler.join()

    exit()

except Exception as e:
    print("\nDisconnecting from server due to error")
    clientSocket.send(toJson(3, "exit").encode())
    clientSocket.close()
    exit()

except KeyboardInterrupt as e:
    print("\nProcess interrupted. Disconnecting from server.")
    clientSocket.send(toJson(3, "exit").encode())
    clientSocket.close()
    exit()
