# -*- coding: utf-8 -*-
"""
Sensor and Vest Methods


Created on Thu Nov 18 10:58:51 2021

@author: Ben Toaz
"""

from bhaptics import better_haptic_player as player
import threespace_api as ts_api
import keyboard

# Dict of file names matched with keystrokes
haptic_dict = {'a': "MoveLeft", 'd': 'MoveRight', 'w': "MoveForward",
               's': 'MoveBack', 'q': 'TurnCCW', 'e': 'TurnCW', 'x': "Jump",
               'wa': 'ForwardLeft','wd': 'ForwardRight','sa': 'BackLeft',
               'sd': 'BackRight'}

#==============================================================================

def getDevices():
    ''' Search for docked devices, make list, assign names and orientation, return devices'''
    
    device_list = ts_api.getComPorts()
    com_port, friendly_name, device_type = device_list[0]
    dng_device = ts_api.TSDongle(com_port=com_port)
    
    device_dict = {1:dng_device[0],3:dng_device[1],4:dng_device[2]}
    
    key = input('Select teacher (1,3,4)>>')
    device1 = device_dict[int(key)]
    
    key = input('Select student (1,3,4)>>')
    device2 = device_dict[int(key)]
    
    device1.setStreamingSlots(slot0='getTaredOrientationAsEulerAngles')
    device2.setStreamingSlots(slot0='getTaredOrientationAsEulerAngles')
    
    return device1, device2, dng_device

#==============================================================================

def register(iteration):
    ''' Turn on haptic player, register all haptic files in dictionary 
    (letters = keys, names = values)'''
    
    player.initialize()
    # Load Tact files from directory
    for value in haptic_dict.values():
        player.register(value+str(iteration), value+str(iteration)+".tact")

#==============================================================================

def play(index, intensity=1, duration=0.5, iteration=3):
    '''Takes keyboard input, intensity value; selects haptic file from dict;
    plays file with adjusted intensity, options for duration and rotation'''
    
    # Find indicated motion
    if index in haptic_dict:
        print('\n'+haptic_dict[index])
        
        # Adjust haptics in real time
        player.submit_registered_with_option(haptic_dict[index]+str(iteration), "alt",
                                             scale_option={"intensity": intensity, "duration": duration},
                                             rotation_option={"offsetAngleX": 0, "offsetY": 0})

#==============================================================================

def testPos(pos_tup1, pos_tup2, tolerance=0):
    '''Takes position tuple and margin of error tolerance, if position in each
    coordinate +/- toleance is less than 0.5 from 0, return true, else false'''
    
    # Default values
    x_test_bool = False
    # y_test_bool = False
    z_test_bool = False
    decimals = 2
    
    # Test for position close to origin within given tolerance
    if (round(pos_tup1[0], decimals) >= (pos_tup2[0] - tolerance)) and (round(pos_tup1[0], decimals) <= (pos_tup2[0] + tolerance)):
        x_test_bool = True
        
    # if  round(pos_tup1[1], decimals) >= (pos_tup2[1] - tolerance) and round(pos_tup1[1], decimals) <= (pos_tup2[1] + tolerance):
    #     y_test_bool = True
        
    if  round(pos_tup1[2], decimals) >= (pos_tup2[2] - tolerance) and round(pos_tup1[2], decimals) <= (pos_tup2[2] + tolerance):
        z_test_bool = True

    # Test if all positions pass tests
    # if x_test_bool and z_test_bool and y_test_bool:
    if x_test_bool and z_test_bool:
        return True
    else:
        return False

#==============================================================================

def close(device_lst):
    'Close all devices so next program can run'
    for d in device_lst:
        d.close()

