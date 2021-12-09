# -*- coding: utf-8 -*-
"""
Base Position Finder
    
    Search for docked IMUs
    Create sensor object
    Select position data for streaming
    
    Construct File Dictionary
    Register Needed Haptic Files

    play()
        Submit selected haptic file to player
        Adjust intensity based on input
        
    testPos()
        Test for position close to origin within given tolerance
        Test if all positions pass tests
        Return true if close enough, false if too far

    Movement loop
        Take Movement Keyboard Input
        Sentinel
            
            Sensing Loop
                Get batch of position data, (x,y,z) tuple
                Display data
                Modulate Intensity    
                play()
                Check with testPos()

    Close sensor
    
Created on Mon Nov  8 11:59:05 2021
@author: Ben Toaz
"""

from bhaptics import better_haptic_player as player
import keyboard
import time
from time import sleep
import threespace_api as ts_api

#==============================================================================

# Search for docked IMUs
tspace_port_lists = ts_api.getComPorts()

#Prints a tuple (PORT_NAME, FRIENDLY_NAME, DEV_T`YPE)
print(tspace_port_lists[0]) 

# Create sensor object
new_sensor = ts_api.TSWLSensor(com_port=tspace_port_lists[0])

# Select position data for streaming
new_sensor.setStreamingSlots(slot0='getTaredOrientationAsEulerAngles')

#==============================================================================

# Picks Set of Haptic Feedback, margin of error for base positions
iteration = 3
tolerance = 0.3

# Dict of lists with file names and base positions matched with keystrokes
haptic_dict = {'a': ["MoveLeft",(-0.75,0.3,-0.3)], 'd': ['MoveRight',(0.45,-0.25,0)], 
               'w': ["MoveForward",(1.1,2.3,-3.1)],'s': ['MoveBack',(-0.25,0,-0.4)],
               'x': ['Jump',(0,0,0)]}
 
player.initialize()

# Load Tact files from directory
for value in haptic_dict.values():
    player.register(value[0]+str(iteration), value[0]+str(iteration)+".tact")

#==============================================================================

# Feedback options
def play(index, intensity=1, duration=1):
    '''Takes keyboard input, intensity value; selects haptic file from dict;
    plays file with adjusted intensity, options for duration and rotation'''
    # Find indicated motion
    if index in haptic_dict:
        print('\n'+haptic_dict[index][0])
        
        # Adjust haptics in real time
        player.submit_registered_with_option(haptic_dict[index][0]+str(iteration), "alt",
                                             scale_option={"intensity": intensity, "duration": duration},
                                             rotation_option={"offsetAngleX": 0, "offsetY": 0})

#==============================================================================

def testPos(pos_tup, base_pos_tup=(0,0,0), tolerance=0):
    '''Takes position tuple and margin of error tolerance, if position in each
    coordinate +/- toleance is less than 0.5 from 0, return true, else false'''
    
    # Default values
    x_test_bool = False
    y_test_bool = False
    z_test_bool = False
    decimals = 2
    
    # Test for position close to origin within given tolerance
    if (round(pos_tup[0], decimals) >= (base_pos_tup[0] - tolerance)) and (round(pos_tup[0], decimals) <= (base_pos_tup[0] + tolerance)):
        x_test_bool = True
        
    if  round(pos_tup[1], decimals) >= (base_pos_tup[1] - tolerance) and round(pos_tup[1], decimals) <= (base_pos_tup[1] + tolerance):
        y_test_bool = True
        
    if  round(pos_tup[2], decimals) >= (base_pos_tup[2] - tolerance) and round(pos_tup[2], decimals) <= (base_pos_tup[2] + tolerance):
        z_test_bool = True

    # Test if all positions pass tests
    if x_test_bool and y_test_bool and z_test_bool:
        return True
    else:
        return False

#==============================================================================

# Start clock
time.process_time()

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
            pos_tup = new_sensor.getStreamingBatch()
            
            # Display position vector of x, z, y
            print('\nPosition: <{}, {}, {}>'.format(
                round(pos_tup[0],3),round(pos_tup[1],3),round(pos_tup[2],3)))
            print("======================\n")
            
            # Play haptics with modulated intensity
            intensity = 1
            duration = 0.5
            
            # Record time
            start = time.process_time()
            play(index, intensity,duration)
            sleep(1.5)
            
            # Test if position is at the base position
            if testPos(pos_tup, haptic_dict[index][1], tolerance):
                print('\nMovement Complete')
                
                # Calculate response time
                end = time.process_time()
                # Add sleep time => not measured by clock
                elapsed = end-start+buzz_num*1.5
                print('Time: '+ str(elapsed))
                break
            
            else:
                print('\nKeep going!')
    
    
print("\nEnd Instructions")
new_sensor.close()

