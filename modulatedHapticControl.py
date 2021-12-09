# -*- coding: utf-8 -*-
"""
Modulated Haptic Control

    Register Needed Haptic Files

    Active Session Loop
        Take Keyboard Input
        Sentinel
        Movement loop
            Modulate Intensity    
            Play()
            

Created on Thu Oct 21 11:05:11 2021
@author: Ben Toaz
"""

# from bhaptics import better_haptic_player as player
import keyboard
from time import sleep
import sensorVestMethods as sv

# Dict of file names matched with keystrokes
haptic_dict = {'a': "MoveLeft", 'd': 'MoveRight', 'w': "MoveForward",
               's': 'MoveBack', 'q': 'TurnCCW', 'e': 'TurnCW', 'x': "Jump"}

sv.register(3, haptic_dict)

# Active Session Loop
print("Press '.' to quit")
while True:

    # User Input
    print('\nInput key command >>')
    key =  keyboard.read_key()
    index = key.lower()

    # Stop session
    if index == '.':
        print("\nEnd Instructions")
        break
    
    elif index in haptic_dict:
        
        # Subject movement loop
        # 3 haptic hits at 100%, 60%, and 20% intensity
        for times in range(3):
            intensity = 1-0.4*times
            duration = 0.5
            sv.play(index, intensity, duration)
            sleep(1.5) 
    
