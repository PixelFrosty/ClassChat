# ClassChat
## Ethan Gretna C00530445
## CMPS 413 Semester Project

This version of my classchat program comes with a GUI, and a Windows compatible client (Server must be run from UNIX based system).

### Dependencies and Running
PyQt5 must be installed for GUI client to run.
Can be done by creating a virtual python environment using the following:

#### Client.py

For the non GUI version, simply run navigate to the file in your terminal and run `python3 client.py`
(NOT COMPATIBLE WITH WINDOWS DUE TO `select()` FUNCTION)

##### Windows

Open PowerShell
`cd` to the location of the GUI client

`python -m venv myenv`
To create the environment

`Set-ExecutionPolicy Unrestricted -Scope Process`
To allow for activation of the environment

`.\winenv\Scripts\Activate.ps1`
To activate the environment

`pip install PyQt5`
To install the dependencies

And finally: `python client.py` to run the client.

##### UNIX:

Open the Terminal
`cd` to the location of the GUI client

`python3 -m venv myenv`
To create the environment

`source myenv/bin/activate`
To activate the environment

`pip3 install PyQt5`
To install the dependencies
(pip required for this step)

And finally: `python3 client.py` to run the client.

#### Server.py:
For the non GUI version, simply run navigate to the file in your terminal and run `python3 server.py`
(NOT COMPATIBLE WITH WINDOWS DUE TO `select()` FUNCTION)

IP can be specified when starting program using `--ip {custom IP}`

### Usage:

A list of commands can be found using `/help`
- List all users: `/List`
- Exit all users: `/Exit`
- Kick users: `/Kick {username}` (Server Exclusive Command)

When starting the client, you must pick a name.
Your name cannot be the same as another's (case insensitive)
The program will alert you if you pick an invalid name or duplicate name.

To message specific users, type their `name` followed immediately by a `:`, a space, and then your message.
Example: `Bob: Hey bob!`
Will send a message privately to Bob.
To broadcast a message to everyone, put `all` as the recipient
