# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 20:19:39 2022

@author: Lynn
"""

import socket
from bhaptics import better_haptic_player as player

# Initialize s to socket
s = socket.socket()
 
# Initialize the host
host = "35.20.240.53"
 
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

# Feedback options
def play(index):

    # Find indicated motion
    if index in rvs_haptic_dict:
        print('\n'+rvs_haptic_dict[index])
        player.submit_registered(rvs_haptic_dict[index]+str(iteration))
        
while(True):
    # receive the command from master program
    command = s.recv(1024)
    command = command.decode()
    play(command)