# -*- coding: utf-8 -*-
"""

Haptic Play Method
    
    Play()
        Construct File Dictionary
        Register Needed Haptic Files
        Submit selected haptic file to player
        Adjust intensity based on input

Created on Tue Nov  2 13:06:00 2021

@author: Ben Toaz
"""

from bhaptics import better_haptic_player as player

# Feedback options
def play(index, intensity=1, iteration=3):
    '''Takes keyboard input, intensity value; selects haptic file from dict;
    plays file with adjusted intensity, options for duration and rotation'''

    # Dict of file names matched with keystrokes
    haptic_dict = {'a': "MoveLeft", 'd': 'MoveRight', 'w': "MoveForward",
                   's': 'MoveBack', 'q': 'TurnCCW', 'e': 'TurnCW', 'x': "Jump"}

    player.initialize()

    # Load Tact files from directory
    for value in haptic_dict.values():
        player.register(value+str(iteration), value+str(iteration)+".tact")
        
    # Find indicated motion
    if index in haptic_dict:
        print('\n'+haptic_dict[index])
        
        # Adjust haptics in real time
        player.submit_registered_with_option(haptic_dict[index]+str(iteration), "alt",
                                             scale_option={"intensity": intensity, "duration": 1},
                                             rotation_option={"offsetAngleX": 0, "offsetY": 0})
