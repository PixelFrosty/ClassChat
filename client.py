from socket import socket, AF_INET, SOCK_STREAM
from re import match
from sys import stdin, exit, argv
from datetime import datetime
from time import sleep
from PyQt5.QtWidgets import QApplication, QDialog, QHBoxLayout, QLabel, QWidget, QVBoxLayout, QTextEdit, QLineEdit, QPushButton, QMessageBox
from PyQt5.QtCore import QObject, QThread, pyqtSignal, Qt
import json

class classChat(QWidget):
    def __init__(self):
        super().__init__()

        self.quit = False

        self.inputThread = incomingData()
        self.serverThread = outgoingData()

        self.senderObj = senderEmitter()

        self.nameSelectInit()

        # Events to update the GUI elements
        self.serverThread.layoutChanged.connect(self.welcomeInit)
        self.serverThread.invalidName.connect(self.invalidNameNoti)
        self.serverThread.textUpdate.connect(self.send)
        self.serverThread.kicked.connect(self.kicked)

        self.senderObj.invalidName.connect(self.invalidNameNoti)
        self.senderObj.textUpdate.connect(self.send)

    def setMyStyle(self):
        self.setStyleSheet('''
                           QWidget#inputDiv, QWidget#nameInputDiv{
                               background: #aaaaaa;
                               padding: 0.5em;
                               border-radius: 0.5em
                               }

                           QWidget{
                               background: #eeeeee;
                               padding: 0.5em;
                               border-radius: 0.5em
                               }

                           QPushButton{
                               background: #888888;
                               padding: 0.5em;
                               border-radius: 0.2em;
                               }

                           QTextEdit{
                               background: transparent;
                               border: none;
                               color: black;
                               }

                           QLineEdit{
                               background: transparent;
                               border: none;
                               color: black;
                               }

                           * {
                               font-family: Verdana;
                               font-size: 18px;
                               font-weight: 300;
                           }

                           ''')

    def nameSelectInit(self):

        self.setWindowTitle('CMPS 413 ClassChat')
        self.setGeometry(300, 300, 400, 200)

        # Layout for name declaration
        nameLayout = QVBoxLayout()

        namelabel = QLabel("Please enter your name:")
        nameLayout.addWidget(namelabel)

        self.nameInputDivQW = QWidget()
        self.nameInputDiv = QHBoxLayout(self.nameInputDivQW)
        self.nameInputDivQW.setObjectName("nameInputDiv")

        self.nameinput = QLineEdit(self)
        self.nameinput.setPlaceholderText("Your name")
        self.nameInputDiv.addWidget(self.nameinput)
        nameLayout.addWidget(self.nameInputDivQW)

        sendB = QPushButton('Check Name', self)
        sendB.clicked.connect(self.sendPressed)
        nameLayout.addWidget(sendB)

        self.setLayout(nameLayout)

        self.setMyStyle()
        QMessageBox.information(
                self,
                "Welcome",
                "Welcome to Classchat.\n"
                "A CMPS 413 Project by Ethan Gretna.\n"
                "C00530445\n"
                "Please start by entering your name."
                )

    def invalidNameNoti(self, taken):
        if taken == 0:
            QMessageBox.warning(
                    self,
                    "Invalid Username\n",
                    "Username must only contain:\n"
                    "letters, numbers, -, _, ', and spaces."
                    )
            self.setMyStyle()
        else:
            QMessageBox.warning(
                    self,
                    "Invalid Username\n",
                    "That username was already taken.\n"
                    "Please try another."
                    )
            self.setMyStyle()

    def kicked(self):
        self.quit = True
        self.inputDivQW.setParent(None)

    def welcomeInit(self):
        global username
        global clientSocket

        # Primary Layout
        self.mainlayout = QVBoxLayout()

        self.messages = QTextEdit(self)
        self.messages.setReadOnly(True)
        self.mainlayout.addWidget(self.messages)

        self.inputDivQW = QWidget()
        self.inputDiv = QHBoxLayout(self.inputDivQW)
        self.inputDivQW.setObjectName("inputDiv")

        inputLayout = QHBoxLayout()

        self.input = QLineEdit(self)
        self.input.setPlaceholderText("recipient: message OR /help for command list")
        self.input.setObjectName("inputBox")
        inputLayout.addWidget(self.input)

        self.sendB = QPushButton('Send', self)
        self.sendB.clicked.connect(self.sendPressed)
        inputLayout.addWidget(self.sendB)

        self.inputDiv.addLayout(inputLayout)
        self.mainlayout.addWidget(self.inputDivQW)

        QWidget().setLayout(self.layout())
        self.resize(600,700)

        QMessageBox.information(
                self,
                "Accepted",
                "Username successfully set.\nWelcome!"
                )
        self.setWindowTitle(f'CMPS 413 ClassChat | Logged in as: {username}')
        self.setLayout(self.mainlayout)
        self.setMyStyle()


    def closeEvent(self, event):
        if self.quit == True:
            event.accept()
        else:
            confirm = QMessageBox.question(self,
                                                "Close ClassChat?",
                                           "We're sorry to see you leave.\nAre you sure you want to go? :(",
                                                QMessageBox.Yes | QMessageBox.No)
            self.setMyStyle()
            try:
                if confirm == QMessageBox.Yes:
                    clientSocket.send(toJson(3, "exit").encode())
                    print("Closed using GUI")
                    clientSocket.close()
                    event.accept()
                else:
                    event.ignore()
            except:
                print("Forcefully exited")
                event.accept()
                pass

    def sendPressed(self):
        if signedIn:
            data = self.input.text()
            if data:
                self.senderObj.sendData(data)
                self.input.clear()
        else:
            data = self.nameinput.text()
            if data:
                self.senderObj.sendData(data)

    def send(self, msg):
        if msg:
            self.messages.append(msg)
            self.input.clear()

    def receive(self, msg):
        if msg:
            self.messages.append(msg)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.sendPressed()

        super().keyPressEvent(event)




def toJson(status, message, receiver = ""):
    data = {
            "status": str(status),
            "message": message,
            "receiver": receiver,
            "sender": username,
            "time": datetime.now().strftime('%H:%M:%S'),
            }
    return json.dumps(data)

class senderEmitter(QObject):
    invalidName = pyqtSignal(int)
    textUpdate = pyqtSignal(str)
    def sendData(self, data):
        global username
        global stop
        global signedIn
        if data:
            if signedIn == False:
                # name not set yet
                username = data.strip()
                if bool(match(r"^[a-zA-Z0-9-_'\s]+$", username)):
                    if username.lower() == 'all':
                        print("Invalid username.\nPlease enter a different one: ", end="")
                        return True
                    clientSocket.send(toJson(0, username).encode())
                else:
                    print("Invalid.\nUsername must only contain letters, numbers, -, _, ', and spaces.\nPlease enter a different one: ", end="")
                    self.invalidName.emit(0)
            else:
                if data[0] == "/":
                    cmd = data[1:].strip().lower()
                    match cmd:
                        case "exit":
                            print("\nDisconnecting from server")
                            clientSocket.send(toJson(3, "exit").encode())
                            stop = False
                            clientSocket.close()
                            return False
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
                            self.textUpdate.emit(
                                    "\nList of commands:\n"
                                    "- /help | Shows list of commands.\n"
                                    "- /list | Shows list of online users.\n"
                                    "- /exit | Disconnect from the server.\n\n"
                                    "Send messages by specifying a user followed by : and your message.\n"
                                    "Example: \"John Doe: Hey there John.\"\n"
                                    "\nTo send messages to all, put \"all\" as your recipient\n"
                                  )
                        case _:
                            print("Invalid command, check /help")
                            self.textUpdate.emit("Invalid command, check /help")
                else:
                    i = data.find(':')
                    if i != -1:
                        rec = data[:i]
                        msg = data[i + 2:]
                        if rec.lower() == username.lower():
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] [Echoing to self] {msg}", end="")
                            self.textUpdate.emit(f"[{datetime.now().strftime('%H:%M:%S')}] [Echoing to self] {msg}")
                        else:
                            clientSocket.send(toJson(1, msg, rec).encode())
                    else:
                        self.textUpdate.emit(
                                "Invalid input, specify a user followed by : to send a message.\n"
                                "Alternatively, check /help for commands."
                                )
        return True

class outgoingData(QThread):
    layoutChanged = pyqtSignal()
    textUpdate = pyqtSignal(str)
    invalidName = pyqtSignal(int)
    kicked = pyqtSignal()

    def run(self):
        global username
        global signedIn
        global clientSocket
        global stop
        global myChat
        try:
            while stop:
                if not stop:
                    break
                rawdata = clientSocket.recv(1024)
                try:
                    data = json.loads(rawdata.decode())
                    sts = data["status"]
                    msg = data["message"]
                    if sts == '0':
                        if msg == 'retry':
                            print(f"The username \"{username}\" was already taken.\nPlease enter a different one: ", end="")
                            self.invalidName.emit(1)
                        elif msg == 'accept':
                            print(f"Welcome to the server {username}!")
                            self.layoutChanged.emit()
                            signedIn = True
                        else:
                            print(msg, end="")
                    if sts == '1':
                        sndr = data["sender"]
                        rec = data["receiver"]
                        time = data["time"]
                        print(f"[{time}] [{sndr} to {rec}] {msg}", end="")
                        self.textUpdate.emit(f"[{time}] [{sndr} to {rec}] {msg}")
                    if sts == '2':
                        if msg == 'shutdown':
                            print("\nServer is shutting down.")
                            print("Press \"Enter\" to exit.")
                            self.kicked.emit()
                            self.textUpdate.emit("\n\n\nThe server has been shutdown.\nFeel free to close the app.")
                            stop = False
                            clientSocket.close()
                            break
                        elif msg == 'kick':
                            print("\nYou have been kicked from the server.")
                            self.kicked.emit()
                            self.textUpdate.emit("\n\n\nYou have been kicked from the server.\nFeel free to close the app.")
                            print("Press \"Enter\" to exit.")
                            stop = False
                            clientSocket.close()
                            break

                    if sts == '3':
                        print(msg)
                        self.textUpdate.emit(msg)
                except json.JSONDecodeError:
                    print("not json data")
                    clientSocket.close()
        except:
            pass

class incomingData(QThread):
    def run(self):
        global stop
        while stop:
            data = stdin.readline()
            if stop == False:
                break
            if self.parent().senderObj.sendData(data) == False:
                break

app = QApplication(argv)


username = ""
signedIn = False

serverName = 'localhost'
serverPort = 12000

try:
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
except:
    print("Unable to connect to server.\nTry again later.")
    exit()

stop = True

myChat = classChat()
myChat.show()

try:
    myChat.inputThread.start()
    myChat.serverThread.start()

except Exception as e:
    print("\nDisconnecting from server due to error")
    clientSocket.send(toJson(3, "exit").encode())
    clientSocket.close()

except KeyboardInterrupt as e:
    print("\nProcess interrupted. Disconnecting from server.")
    clientSocket.send(toJson(3, "exit").encode())
    clientSocket.close()

finally:
    exit(app.exec_())
