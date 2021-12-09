# -*- coding: utf-8 -*-
"""
Intensity Change Test

Created on Thu Oct 21 11:46:37 2021

@author: Lynn
"""
from bhaptics import better_haptic_player as player
import keyboard
from time import sleep

# Picks Set of Haptic Feedback
iteration = 3

player.initialize()

# Dict of file names matched with keystrokes
haptic_dict = {'a': "MoveLeft", 'd': 'MoveRight', 'w': "MoveForward",
               's': 'MoveBack', 'q': 'TurnCCW', 'e': 'TurnCW', 'x': "Jump"}

# Load Tact files from directory
for value in haptic_dict.values():
    player.register(value+str(iteration), value+str(iteration)+".tact")


# Feedback options
def play(index, intensity):

    # Find indicated motion
    if index in haptic_dict:
        print('\n'+haptic_dict[index])
        #player.submit_registered(haptic_dict[index]+str(iteration))
        
        player.submit_registered_with_option(haptic_dict[index]+str(iteration), "alt",
                                              scale_option={"intensity": intensity, "duration": 1},
                                              rotation_option={"offsetAngleX": 0, "offsetY": 0})

sleep(3)
for i in range(1,5):
    play('a',1/i)
    sleep(2)
