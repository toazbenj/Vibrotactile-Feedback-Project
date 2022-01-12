# -*- coding: utf-8 -*-
"""
Sensor and Vest Methods

    getDevices
        Search for docked devices, make list, assign names and orientation,
        display battery levels, return devices
        
    register
        Turn on haptic player, register all haptic files in dictionary
        (letters = keys, names = values)
        
     play
        Takes keyboard input, intensity value; selects haptic file from dict;
        plays file with adjusted intensity, options for duration and rotation
        
    testPos
        Takes position tuple and margin of error tolerance, if position in each
        coordinate +/- toleance is less than 0.5 from 0, return true, else false
        
    play
        Takes keyboard input, intensity value; selects haptic file from dict;
        plays file with adjusted intensity, options for duration and rotation
        
    close
        Close all devices so next program can run
    
    writeData
        Take timestamp, position data, haptics data, write to csv file
    
Created on Thu Nov 18 10:58:51 2021
@author: Ben Toaz
"""

from bhaptics import better_haptic_player as player
import threespace_api as ts_api
import csv
from math import pi
from time import perf_counter

# Dict of file names matched with keystrokes, all files and then only cardinal directions
haptic_dict = {'a': "MoveLeft", 'd': 'MoveRight', 'w': "MoveForward",
                's': 'MoveBack', 'q': 'TurnCCW', 'e': 'TurnCW', 'x': "Jump",
                'wa': 'ForwardLeft', 'wd': 'ForwardRight', 'sa': 'BackLeft',
                'sd': 'BackRight'}

# Numerical representation of direction for records
angle_dict = {'a': pi, 'wd': pi/4, 'd': 2*pi, 'wa': 3*pi/4, 'w': pi/2,'sa': 5*pi/4, 
              's': 3*pi/2, 'sd': 7*pi/4}

def getDevices():
    ''' Search for docked devices, make list, assign names and orientation,
    display battery levels, return devices'''

    device_list = ts_api.getComPorts()
    com_port, friendly_name, device_type = device_list[0]
    dng_device = ts_api.TSDongle(com_port=com_port)

    device_dict = {1: dng_device[0], 3: dng_device[1], 4: dng_device[2]}

    key = input('Select teacher (1,3,4)>>')
    device1 = device_dict[int(key)]

    key = input('Select student (1,3,4)>>')
    device2 = device_dict[int(key)]
    
    percent1 = device1.getBatteryPercentRemaining()
    percent2 = device2.getBatteryPercentRemaining()
    
    print('Teacher battery at {}%'.format(percent1))
    print('Student battery at {}%'.format(percent2))

    device1.setStreamingSlots(slot0='getTaredOrientationAsEulerAngles')
    device2.setStreamingSlots(slot0='getTaredOrientationAsEulerAngles')

    while True:
        key = input('Press T to tare>>')    
        if key.lower() == 't':
            break
    
    device1.tareWithCurrentOrientation()
    device2.tareWithCurrentOrientation()

    return device1, device2, dng_device


def register(iteration):
    ''' Turn on haptic player, register all haptic files in dictionary
    (letters = keys, names = values)'''

    player.initialize()
    # Load Tact files from directory
    for value in haptic_dict.values():
        player.register(value+str(iteration), value+str(iteration)+".tact")


def play(index='w', intensity=1, duration=0.5, iteration=3):
    '''Takes keyboard input, intensity value; selects haptic file from dict;
    plays file with adjusted intensity, options for duration and rotation'''

    # Find indicated motion
    if index in haptic_dict:
        print('\n'+haptic_dict[index]+'\n')

        # Adjust haptics in real time
        player.submit_registered_with_option(
            haptic_dict[index]+str(iteration), "alt",
            scale_option={"intensity": intensity, "duration": duration},
            rotation_option={"offsetAngleX": 0, "offsetY": 0})


def testPos(pos_tup1, pos_tup2, tolerance=0):
    
    # Currently not in use

    '''Takes position tuple and margin of error tolerance, if position in each
    coordinate +/- toleance is less than 0.5 from 0, return true, else false'''
    
    # Default values
    x_test_bool = False
    # y_test_bool = False
    z_test_bool = False
    decimals = 2

    # Test for position close to origin within given tolerance
    if ((round(pos_tup1[0], decimals) >= (pos_tup2[0] - tolerance))
        and (round(pos_tup1[0], decimals) <= (pos_tup2[0] + tolerance))):
        x_test_bool = True

    # if (round(pos_tup1[1], decimals) >= (pos_tup2[1] - tolerance)
        # and round(pos_tup1[1], decimals) <= (pos_tup2[1] + tolerance)):
    #     y_test_bool = True

    if (round(pos_tup1[2], decimals) >= (pos_tup2[2] - tolerance)
        and round(pos_tup1[2], decimals) <= (pos_tup2[2] + tolerance)):
        z_test_bool = True

    # Test if all positions pass tests
    # if x_test_bool and z_test_bool and y_test_bool:
    if x_test_bool and z_test_bool:
        return True
    else:
        return False


def close(device_lst):
    '''Close all devices so next program can run'''
    for d in device_lst:
        d.close()
        

def writeData(file,time,tec_tup,stu_tup,diff_tup,intensity,angle):
    '''Take timestamp, position data, haptics data, write to csv file'''
    with open(file, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        
        csvwriter.writerow([str(round(time,3)), str(round(tec_tup[0], 3)), 
            str(round(tec_tup[1], 3)), str(round(tec_tup[2], 3)), 
            str(round(stu_tup[0], 3)), str(round(stu_tup[1], 3)), 
            str(round(stu_tup[2], 3)), str(round(diff_tup[0], 3)), 
            str(round(diff_tup[1], 3)), str(round(diff_tup[2], 3)),
            str(round(intensity, 3)), str(round(angle, 2))])    
    

def checkTolerance(check_tup, tolerance):
    if check_tup[1] > tolerance or check_tup[1] < -tolerance\
        or check_tup[2] > tolerance or check_tup[2] < -tolerance:
        
        return True 
    else:
        return False
    

def getIndex(diff_tup, tolerance):
    index = ''
    
    # Forward Left (-y difference and -z differnce)
    if diff_tup[1] <= -tolerance and diff_tup[2] <= -tolerance:
        index = 'wa'

    # Forward Right (-z differnce and +y difference)
    elif diff_tup[2] <= -tolerance and diff_tup[1] >= tolerance:
        index = 'wd'

    # Back Right (+y difference +z difference)
    elif diff_tup[1] >= tolerance and diff_tup[2] >= tolerance:
        index = 'sd'

    # Back Left (+z difference and -y difference)
    elif diff_tup[2] >= tolerance and diff_tup[1] <= -tolerance:
        index = 'sa'
        
    # Forward (-z differnce)
    elif diff_tup[2] <= -tolerance and abs(diff_tup[1]) < abs(diff_tup[2]):
        index = 'w'
    
    # Left (-y difference)
    elif diff_tup[1] <= -tolerance and abs(diff_tup[1]) > abs(diff_tup[2]):
        index = 'a'

    # Right (+y difference)
    elif diff_tup[1] >= tolerance and abs(diff_tup[1]) > abs(diff_tup[2]):
        index = 'd'

    # Back (+z difference)
    elif diff_tup[2] >= tolerance and abs(diff_tup[1]) < abs(diff_tup[2]):
        index = 's'
        
    return index


def advancedPlay(index, diff_tup, start, commandTime):
    if index in haptic_dict:
        
        # Decide which axis to check based on bigger difference
        if abs(diff_tup[1]) > abs(diff_tup[2]):
            check_coord = 1
        else:
            check_coord = 2

        # Modulate intensity based on assumed max movement angle
        intensity = abs(diff_tup[check_coord])/(pi/2)
        # Can't exceed 1
        if intensity > 1:
            intensity = 1
        
        # Measures time since last buzz => maintains gap
        time  =  perf_counter()-start
        if time - commandTime > 0.5:
            commandTime = perf_counter()-start
            play(index=index, intensity=intensity, duration=0.5,iteration=3)
        angle = angle_dict[index]

    else:
        # No haptics => Intensity=0, Angle=0
        angle = 0 
        intensity = 0
        
    return angle, intensity, commandTime
