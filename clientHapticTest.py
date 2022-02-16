# -*- coding: utf-8 -*-
"""
Client Haptic Test

Created on Wed Feb 16 13:17:03 2022
@author: toazbenj
"""

import socket
from bhaptics import better_haptic_player as player
import utilitiesMethods as utility

# Initialize s to socket
s = socket.socket()
 
# Initialize the host
host = "35.12.209.242"
 
# Initialize the port
port = 8080
 
# bind the socket with port and host
s.connect((host, port))
 
print("Connected to Server.")
 

rvs_haptic_dict = {'d': "MoveLeft", 'a': 'MoveRight', 's': "MoveForward",
                'w': 'MoveBack', '4': 'ForwardLeft', '3': 'ForwardRight', 
                '2': 'BackLeft','1': 'BackRight'}

# Picks Set of Haptic Feedback
iteration = 4

player.initialize()
# Load Tact files from directory
for value in rvs_haptic_dict.values():
    player.register(value+str(iteration), value+str(iteration)+".tact")
        
while(True):
    # receive the command from master program
    command = s.recv(1024)
    command = command.decode()
    utility.play(command)