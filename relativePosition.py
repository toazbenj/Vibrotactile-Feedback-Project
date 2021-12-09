# -*- coding: utf-8 -*-
"""
Relative Position Finder
   
    Register Needed Haptic Files
    Register sensors

    Movement loop
        Take Movement Keyboard Input
        Sentinel
            
            Sensing Loop
                Get batch of position data, (x,y,z) tuple
                Display data
                Modulate Intensity    
                play()
                Check with testPos()

    Close sensors
"""

import keyboard
from time import perf_counter
from time import sleep
import sensorVestMethods as sv

# Dict of file names matched with keystrokes
haptic_dict = {'a': "MoveLeft", 'd': 'MoveRight', 'w': "MoveForward",
               's': 'MoveBack', 'q': 'TurnCCW', 'e': 'TurnCW', 'x': "Jump"}

# Register haptic files
sv.register(3, haptic_dict)

# Register Sensors
sensor1, sensor2, dong = sv.getDevices()

# Movement Loop
while True:
    
    # User Input
    print('\nInput key command >>')
    key =  keyboard.read_key()
    index = key.lower()
    
    # Sentinel Value
    if index == '.':
        print("\nEnd Instructions")
        break
    
    elif index in haptic_dict:
        
        # Record number of feedback hits
        buzz_num = 0
        
        # Sensing loop
        while True:
            buzz_num += 1
            # Get batch of position data as (x,y,z) tuple
            pos_tup1 = sensor1.getStreamingBatch()
            pos_tup2 = sensor2.getStreamingBatch()
            
            # Display position vector of x, z, y
            print('Sensor 1: <{}, {}, {}>'.format(
                round(pos_tup1[0],3),round(pos_tup1[1],3),round(pos_tup1[2],3)))
            print('Sensor 2: <{}, {}, {}>'.format(
                round(pos_tup2[0],3),round(pos_tup2[1],3),round(pos_tup2[2],3)))
            
            # Play haptics with modulated intensity
            intensity = 1
            duration = 0.5
            tolerance = 0.3
            
            # Record time, play haptics
            start = perf_counter()
            sv.play(index, intensity, duration)
            sleep(1.5)
            
            # Test if positions match
            if sv.testPos(pos_tup1, pos_tup2, tolerance):
                print('\nMovement Complete')
                
                # Calculate response time
                end = perf_counter()
                # Add sleep time => not measured by clock
                elapsed = end-start+buzz_num*1.5
                print('Time: '+ str(round(elapsed,3)))
                break
            
            else:
                print('\nKeep going!')
    
sv.close(sensor1, sensor2, dong)

