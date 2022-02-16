# -*- coding: utf-8 -*-
"""
Utilities Methods for Yosh Labs Sensors and bHaptics Tactsuit

    register
        Turn on haptic player, register all haptic files in dictionary
        (letters = keys, names = values)

    play
        Takes keyboard input, intensity value; selects haptic file from dict;
        plays file with adjusted intensity, options for duration and rotation

    advancedPlay
        Scale haptic intensity, play haptics, maintain distance between buzzes,
        return values for recording

    getIndex
        Select index for given direction moved beyond tolerance

    getDevices
        Search for docked devices, make list, assign names and orientation,
        display battery levels, tare countdown, return devices

    checkTolerance
        Determine if coordinates exceed tolerance

    close
        Close all devices so next program can run

    writeData
        Take timestamp, position data, haptics data, write to csv file.
        Overloaded so parameter of 1 for mode will write without a score
        (followMe) and anything else will result in writing with score
        (tandemControlGame)

    testPos-Ignore this one
        Takes position tuple and margin of error tolerance, if position in each
        coordinate +/- tolerance < 0.5 from 0, return true, else false

Created on Thu Nov 18 10:58:51 2021
@author: Ben Toaz
"""

from bhaptics import better_haptic_player as player
import threespace_api as ts_api
import csv
from math import pi
from time import perf_counter
from time import sleep

# Dict of file names matched with keystrokes
# Version 3
# haptic_dict = {'a': "MoveLeft", 'd': 'MoveRight', 'w': "MoveForward",
#                 's': 'MoveBack', 'q': 'TurnCCW', 'e': 'TurnCW', 'x': "Jump",
#                 'wa': 'ForwardLeft', 'wd': 'ForwardRight', 'sa': 'BackLeft',
#                 'sd': 'BackRight'}

# Version 4
haptic_dict = {'a': "MoveLeft", 'd': 'MoveRight', 'w': "MoveForward",
               's': 'MoveBack', 'wa': 'ForwardLeft', 'wd': 'ForwardRight',
               'sa': 'BackLeft', 'sd': 'BackRight'}

# Numerical representation of direction for records
angle_dict = {'a': pi, 'wd': pi/4, 'd': 2*pi, 'wa': 3*pi/4, 'w': pi/2,
              'sa': 5*pi/4, 's': 3*pi/2, 'sd': 7*pi/4}


def register(iteration):
    """
    Turn on haptic player, register all haptic files in dictionary
    (letters = keys, names = values)
    """

    player.initialize()
    # Load Tact files from directory
    for value in haptic_dict.values():
        player.register(value+str(iteration), value+str(iteration)+".tact")


def play(index='w', intensity=1, duration=0.5, iteration=4):
    """
    Takes keyboard input, intensity value; selects haptic file from dict;
    plays file with adjusted intensity, options for duration and rotation
    """

    # Find indicated motion
    if index in haptic_dict:
        print('\n'+haptic_dict[index]+'\n')

        # Adjust haptics in real time
        player.submit_registered_with_option(
            haptic_dict[index]+str(iteration), "alt",
            scale_option={"intensity": intensity, "duration": duration},
            rotation_option={"offsetAngleX": 0, "offsetY": 0})


def advancedPlay(index, difference_tup, start, commandTime, iteration, conn):
    """
    Scale haptic intensity, maintain time between buzzes, return values
    for recording, send index and intesity to teacher client.
    """
    if index in haptic_dict:

        # Decide which axis to check based on bigger difference
        if abs(difference_tup[1]) > abs(difference_tup[2]):
            check_coord = 1
        else:
            check_coord = 2

        # Modulate intensity based on assumed max movement angle
        intensity = abs(difference_tup[check_coord])/(pi/2)
        # Can't exceed 1
        if intensity > 1:
            intensity = 1

        # Measures time since last buzz => maintains gap
        time = perf_counter()-start
        if time - commandTime > 0.5:
            commandTime = perf_counter()-start
            play(index=index, intensity=intensity,
                 duration=0.5, iteration=iteration)
            
            # Generate command, send to client
            command = str(index)+str(intensity)
            conn.send(command.encode())
            
        angle = angle_dict[index]

    else:
        # No haptics => Intensity=0, Angle=0
        angle = 0
        intensity = 0

    return angle, intensity, commandTime


def getIndex(difference_tup, tolerance):
    """Select index for given direction moved beyond tolerance."""
    index = ''

    # Forward Left (-y difference and -z differnce)
    if difference_tup[1] <= -tolerance and difference_tup[2] <= -tolerance:
        index = 'wa'

    # Forward Right (-z differnce and +y difference)
    elif difference_tup[2] <= -tolerance and difference_tup[1] >= tolerance:
        index = 'wd'

    # Back Right (+y difference +z difference)
    elif difference_tup[1] >= tolerance and difference_tup[2] >= tolerance:
        index = 'sd'

    # Back Left (+z difference and -y difference)
    elif difference_tup[2] >= tolerance and difference_tup[1] <= -tolerance:
        index = 'sa'

    # Forward (-z differnce)
    elif difference_tup[2] <= -tolerance and\
            abs(difference_tup[1]) < abs(difference_tup[2]):
        index = 'w'

    # Left (-y difference)
    elif difference_tup[1] <= -tolerance and\
            abs(difference_tup[1]) > abs(difference_tup[2]):
        index = 'a'

    # Right (+y difference)
    elif difference_tup[1] >= tolerance and\
            abs(difference_tup[1]) > abs(difference_tup[2]):
        index = 'd'

    # Back (+z difference)
    elif difference_tup[2] >= tolerance and\
            abs(difference_tup[1]) < abs(difference_tup[2]):
        index = 's'

    return index


def getPercent():
    " Receive/calculate the amount of cursor control for student/teacher"
    key = input('Enter teacher control proportion(%)>>')
    percent_teacher = float(key)*0.01
    percent_student = 1-percent_teacher
    
    return  percent_teacher, percent_student


def getDevices():
    """
    Search for docked devices, make list, assign names and orientation,
    display battery levels, tare countdown, return devices
    """
    # Move slot selected within dongle to make room for other projects
    # Slots 0-4 for robot project, 5-7 for vibrotactile feedback
    offset = 5

    device_list = ts_api.getComPorts()
    com_port, friendly_name, device_type = device_list[0]
    dng_device = ts_api.TSDongle(com_port=com_port)

    device_dict = {1: dng_device[0+offset], 3: dng_device[1+offset],
                   4: dng_device[2+offset]}

    key = input('Select teacher (1,3,4)>>')
    device1 = device_dict[int(key)]

    key = input('Select student (1,3,4)>>')
    device2 = device_dict[int(key)]

    # Display Battery Levels
    percent1 = device1.getBatteryPercentRemaining()
    percent2 = device2.getBatteryPercentRemaining()

    print('Teacher battery at {}%'.format(percent1))
    print('Student battery at {}%'.format(percent2))
    
    # Tare and start data streaming
    device1.setStreamingSlots(slot0='getTaredOrientationAsEulerAngles')
    device2.setStreamingSlots(slot0='getTaredOrientationAsEulerAngles')

    print("Taring in 5\n")

    for i in reversed(range(0, 5)):
        sleep(1)
        print(i)
        print('\n')

    device1.tareWithCurrentOrientation()
    device2.tareWithCurrentOrientation()

    print('GO!\n')

    return device1, device2, dng_device


def checkTolerance(check_tup, tolerance):
    """Determine if coordinates exceed tolerance."""
    if check_tup[1] > tolerance or check_tup[1] < -tolerance\
            or check_tup[2] > tolerance or check_tup[2] < -tolerance:

        return True
    else:
        return False


def close(device_lst):
    """Close all devices so next program can run"""
    for d in device_lst:
        d.close()
    print('Devices closed.')


def writeData(file, time, teacher_tup, student_tup, difference_tup, intensity,
              angle, score, ball, target, mode):
    """
    Take timestamp, position data, haptics data, write to csv file. Overloaded
    so parameter of 1 for mode will write without a score (followMe) and
    anything else will result in writing with score (followMeGame)
    """
    # Teacher's haptics is always 180 degrees opposite student
    if angle > 0:
        angle_teacher = angle +pi
    else:
        angle_teacher = 0
        
    with open(file, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)

        if mode == 1:
            csvwriter.writerow([str(round(time, 3)),
                                str(round(teacher_tup[0], 3)),
                                str(round(teacher_tup[1], 3)),
                                str(round(teacher_tup[2], 3)),
                                str(round(student_tup[0], 3)),
                                str(round(student_tup[1], 3)),
                                str(round(student_tup[2], 3)),
                                str(round(difference_tup[0], 3)),
                                str(round(difference_tup[1], 3)),
                                str(round(difference_tup[2], 3)),
                                str(round(intensity, 3)),
                                str(round(angle, 2))])

        else:
            csvwriter.writerow([str(round(time, 3)),
                                str(round(teacher_tup[0], 3)),
                                str(round(teacher_tup[1], 3)),
                                str(round(teacher_tup[2], 3)),
                                str(round(student_tup[0], 3)),
                                str(round(student_tup[1], 3)),
                                str(round(student_tup[2], 3)),
                                str(round(difference_tup[0], 3)),
                                str(round(difference_tup[1], 3)),
                                str(round(difference_tup[2], 3)),
                                str(round(intensity, 3)),
                                str(round((angle_teacher), 2)),
                                str(round(angle, 2)),
                                str(round(ball.x_center)),
                                str(round(ball.y_center)),
                                str(round(target.x_center)),
                                str(round(target.y_center)),
                                str(score)])


def testPos(pos_tup1, pos_tup2, tolerance=0):
    """
    Takes position tuple and margin of error tolerance, if position in each
    coordinate +/- toleance is less than 0.5 from 0, return true, else false
    """
    # Currently not in use

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
