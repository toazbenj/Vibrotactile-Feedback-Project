# -*- coding: utf-8 -*-
"""
2nd Vest Client

    Initiazlize host and port
    Bind to socket
    Load tact files

    Haptics loop
        Receive command
        Try
            1 character index slicing
        Except
            2 character index slicing
        Play haptics

Created on Mon Feb 14 20:19:39 2022
@author: Ben Toaz
"""

import socket
from bhaptics import better_haptic_player as player
import utilitiesMethods as utility

rvs_haptic_dict = {'d': "MoveLeft", 'a': 'MoveRight', 's': "MoveForward",
                   'w': 'MoveBack', 'sd': 'ForwardLeft', 'sa': 'ForwardRight',
                   'wd': 'BackLeft', 'wa': 'BackRight'}

# Switches index key to new index value
rvs_index_dict = {'d': "a", 'a': 'd', 's': "w", 'w': 's', 'sd': 'wa',
                  'sa': 'wd', 'wd': 'sa', 'wa': 'sd'}

# Initialize host and port
host = "35.12.209.238"
port = 8080

# Bind socket with port and host
s = socket.socket()
s.connect((host, port))
print("Connected to Server.")

# Picks Set of Haptic Feedback
iteration = 4
player.initialize()

# Load Tact files from directory
for value in rvs_haptic_dict.values():
    player.register(value+str(iteration), value+str(iteration)+".tact")

# Haptics loop
while(True):
    # Receive command from master program
    command = s.recv(1024)
    # Command is string of 1-2 letters and intensity float
    command = command.decode()

    command = command.split('-')
    raw_intensity = float(command[0])
    index = command[1]
    teacher_intensity = float(command[2])

    utility.play(index=rvs_index_dict[index], intensity=raw_intensity*teacher_intensity)
