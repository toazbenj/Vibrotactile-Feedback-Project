# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 20:19:19 2022

@author: Lynn
"""

import socket
from bhaptics import better_haptic_player as player
import keyboard

haptic_dict = {'a': "MoveLeft", 'd': 'MoveRight', 'w': "MoveForward",
                's': 'MoveBack', '1': 'ForwardLeft', '2': 'ForwardRight', 
                '3': 'BackLeft','4': 'BackRight'}

# Initialize s to socket
s = socket.socket()
 
# Initialize the host
host = socket.gethostname()
 
# Initialize the port
port = 8080
 
# Bind the socket with port and host
s.bind(('', port))
 
print("waiting for connections...")
 
# listening for connections
s.listen()

# accepting the incoming connections
conn, addr = s.accept()
print(addr, "is connected to server")
 

# Picks Set of Haptic Feedback
iteration = 4

player.initialize()


# Load Tact files from directory
for value in haptic_dict.values():
    player.register(value+str(iteration), value+str(iteration)+".tact")


# Feedback options
def play(index):

    # Find indicated motion
    if index in haptic_dict:
        print('\n'+haptic_dict[index])
        player.submit_registered(haptic_dict[index]+str(iteration))

# Active Session Loop
print("Press '.' to quit")
while True:

    # User Input
    key = keyboard.read_key()
    index = key.lower()

    # Sentinel Value
    if index == '.':
        print("End Sequence")
        break

    # Access File
    play(index)
    
    # take command as input
    command = str(index)
    conn.send(command.encode())

