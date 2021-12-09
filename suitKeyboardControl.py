# -*- coding: utf-8 -*-
"""
TactSuit Keyboard Control Program

    Construct File Dictionary
    Register Needed Haptic Files

    Play()
        Submit selected haptic file to player

    Active Session Loop
        Take Keyboard Input
        Sentinel
        Play()

Created on Thu Oct  7 10:30:20 2021
@author: Ben Toaz
"""

from bhaptics import better_haptic_player as player
import keyboard

# Picks Set of Haptic Feedback
iteration = 1

player.initialize()

# Dict of file names matched with keystrokes
haptic_dict = {'a': "MoveLeft", 'd': 'MoveRight', 'w': "MoveForward",
               's': 'MoveBack', 'q': 'TurnCCW', 'e': 'TurnCW', 'x': "Jump"}

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
