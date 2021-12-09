# -*- coding: utf-8 -*-
"""

Origin Finder Game 

    Search for docked IMUs
    Create sensor object
    Select position data for streaming
    
    Play()
        Submit selected haptic file to player
        Adjust intensity based on input
        
    testPos()
        Test for position close to origin within given tolerance
        Test if all positions pass tests
        Return true if close enough, false if too far
    
    Sensing Loop
        Get batch of position data, (x,y,z) tuple
        Display data
        Check with testPos()
            break
        Play()
        
    Close Sensor => Important

Created on Tue Nov  2 10:19:17 2021
@author: Ben Toaz
"""

from bhaptics import better_haptic_player as player
import keyboard
from time import sleep
import time
import threespace_api as ts_api

# Search for docked IMUs
tspace_port_lists = ts_api.getComPorts()

#Prints a tuple (PORT_NAME, FRIENDLY_NAME, DEV_TYPE)
print(tspace_port_lists[0]) 

# Create sensor object
new_sensor = ts_api.TSWLSensor(com_port=tspace_port_lists[0])

# Select position data for streaming
new_sensor.setStreamingSlots(slot0='getTaredOrientationAsEulerAngles')



# Picks Set of Haptic Feedback
iteration = 3

# Dict of file names matched with keystrokes
haptic_dict = {'a': "MoveLeft", 'd': 'MoveRight', 'w': "MoveForward",
               's': 'MoveBack', 'q': 'TurnCCW', 'e': 'TurnCW', 'x': "Jump"}

player.initialize()

# Load Tact files from directory
for value in haptic_dict.values():
    player.register(value+str(iteration), value+str(iteration)+".tact")


# Feedback options
def play(index, intensity=1):
    '''Takes keyboard input, intensity value; selects haptic file from dict;
    plays file with adjusted intensity, options for duration and rotation'''
    # Find indicated motion
    if index in haptic_dict:
        print('\n'+haptic_dict[index])
        
        # Adjust haptics in real time
        player.submit_registered_with_option(haptic_dict[index]+str(iteration), "alt",
                                             scale_option={"intensity": intensity, "duration": 1},
                                             rotation_option={"offsetAngleX": 0, "offsetY": 0})


def testPos(pos_tup, tolerance=0):
    '''Takes position tuple and margin of error tolerance, if position in each
    coordinate +/- toleance is less than 0.5 from 0, return true, else false'''
    
    # Default values
    x_test_bool = False
    y_test_bool = False
    z_test_bool = False
    decimals = 2
    
    # Test for position close to origin within given tolerance
    if (round(pos_tup[0], decimals) >= (0 - tolerance)) and (round(pos_tup[0], decimals) <= (0 + tolerance)):
        x_test_bool = True
        
    if  round(pos_tup[1], decimals) >= (0 - tolerance) and round(pos_tup[1], decimals) <= (0 + tolerance):
        y_test_bool = True
        
    if  round(pos_tup[2], decimals) >= (0 - tolerance) and round(pos_tup[2], decimals) <= (0 + tolerance):
        z_test_bool = True

    # Test if all positions pass tests
    if x_test_bool and y_test_bool and z_test_bool:
        return True
    else:
        return False


# Sensing Loop
#time.clock()
tolerance = 0.1
while True:
    
    # Get batch of position data, (x,y,z) tuple
    pos_tup = new_sensor.getStreamingBatch()
    
    # Display position vector of x, z, y
    print('Position: <{}, {}, {}>'.format(round(pos_tup[0],3),round(pos_tup[1],3),round(pos_tup[2],3)))
    print("======================\n")
    #print('Time: '+str(time.clock()))
    
    if testPos(pos_tup, tolerance):
        break
    
    play('w', 0.1)
    sleep(2)
    
    
print("\nOrigin Found")
new_sensor.close()