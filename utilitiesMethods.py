# -*- coding: utf-8 -*-
"""
Utilities Methods for Yost Labs Sensors, bHaptics Tactsuit, and Graphics

    getControl
        Generate dictionary of student control values for training

    getSharing
        Receive/calculate the amount of cursor control and intensity for
        student/teacher

    getDevices
        Search for docked devices, make list, assign names and orientation,
        display battery levels, tare countdown, return devices

    close
        Close all devices so next program can run

    getAutoSetup
            Reads control file, gathers number of rounds and mode for each
            target sequence

    intermission
        Pauses game in loop until user clicks to continue

    getRoundType
        Find which type of target sequence is being fielded, test or training

    signalReconnect
            Handles exception when IMU signal is lost. Runs through connection
            and callibration again automaticaly, factors out lost time

    positionMove
        Calculate poition of ball object in graphics window based on weighted
        average of teacher and student movements. Limit movement to within
        graphics window, move ball to new position

    displayScore
        Calculate target round score, display text

    register
        Turn on haptic player, register all haptic files in dictionary
        (letters = keys, names = values)

    play
        Takes keyboard input, intensity value; selects haptic file from dict;
        plays file with adjusted intensity, options for duration and rotation

    advancedPlay
        Scale haptic intensity, play haptics, maintain distance between buzzes,
        return values for recording, send command to teacher client

    getIndex
        Select index for given direction moved beyond tolerance

    writeData
        Take timestamp, position data, haptics data, write to csv file.
        Overloaded so parameter of 1 for mode will write without a score
        (followMe) and anything else will result in writing with score
        (tandemControlGame)

Created on Thu Nov 18 10:58:51 2021
@author: Ben Toaz
"""

from bhaptics import better_haptic_player as player
import threespace_api as ts_api
import csv
from math import pi
from math import exp
from time import perf_counter
from time import sleep
import graphics

# Dict of file names matched with keystrokes
haptic_dict = {'a': "MoveLeft", 'd': 'MoveRight', 'w': "MoveForward",
               's': 'MoveBack', 'wa': 'ForwardLeft', 'wd': 'ForwardRight',
               'sa': 'BackLeft', 'sd': 'BackRight'}

# Numerical representation of direction for records
angle_dict = {'a': pi, 'wd': pi/4, 'd': 2*pi, 'wa': 3*pi/4, 'w': pi/2,
              'sa': 5*pi/4, 's': 3*pi/2, 'sd': 7*pi/4}


def getControl(round_lst, round_control_lst):
    """Generate dictionary of student control values for training"""
    count = 0
    round_control_dict = {}
    for i in round_control_lst[1:]:
        round_control_dict[count] = i
        count += 1

    return round_control_dict


def getSharing(round_control_dict, isTest, round_lst, round_control_lst,
               sequence_lst, blocks_lst, block, master_index, training_mode=1,
               rounds=0):
    """
    Receive/calculate the amount of cursor control and intensity for
    student/teacher
    """
    isGraduated = round_control_lst[0]

    round_control_dict = getControl(round_lst, round_control_lst)
    # print(round_control_dict)

    # No Teacher, No Haptics
    if training_mode == 1 or isTest:
        teacher_control = 0
        student_control = 1
        teacher_intensity = 0
        student_intensity = 0

    # Teacher
    else:
        # Control changes for each training round
        if isGraduated:
            # Training 1
            if master_index < 2:
                student_control = round_control_dict[
                    rounds-round_lst[0]-block*sequence_lst[1]]
            # Training 2
            else:
                student_control = round_control_dict[
                    rounds-sum(round_lst[0:3])-block*sequence_lst[3]]

            teacher_control = 1-student_control

        # Control changes for each training block
        else:
            # Training 1
            if master_index < 2:
                student_control = round_control_dict[block]
            # Training 2
            else:
                student_control = round_control_dict[block]

            teacher_control = 1-student_control

        # No haptics
        if training_mode == 2:
            student_intensity = 0
            teacher_intensity = 0
        # Haptics
        else:
            # Amount of intensity is inverse of amount of control
            student_intensity = teacher_control
            teacher_intensity = student_control

    return teacher_control, student_control, teacher_intensity,\
        student_intensity


def getDevices(training_mode=1, teacher_number=1, student_number=4):
    """
    Search for docked devices, make list, assign names and orientation,
    display battery levels, tare countdown, return devices
    """

    device_list = ts_api.getComPorts()
    com_port, friendly_name, device_type = device_list[0]
    dng_device = ts_api.TSDongle(com_port=com_port)

    # Key is order listed in dongle settings, values are devices
    device_dict = {1: dng_device[0], 3: dng_device[1],
                   4: dng_device[2]}

    # No teacher, no haptics
    if training_mode == 1:

        device1 = device_dict[int(student_number)]

        percent1 = device1.getBatteryPercentRemaining()
        print('Student battery at {}%'.format(percent1))

        device1.setStreamingSlots(slot0='getTaredOrientationAsEulerAngles')

        print("Taring in 5\n")
        for i in reversed(range(0, 5)):
            sleep(1)
            print(i)
            print('\n')

        device1.tareWithCurrentOrientation()
        print('GO!\n')

        return device1, dng_device

    # Teacher, with and without haptics
    else:

        device1 = device_dict[int(teacher_number)]
        device2 = device_dict[int(student_number)]

        # Display Battery Levels
        percent1 = device1.getBatteryPercentRemaining()
        percent2 = device2.getBatteryPercentRemaining()

        print('Teacher battery at {}%'.format(percent1))
        print('Student battery at {}%'.format(percent2))

        # Tare and start data streaming
        device1.setStreamingSlots(slot0='getTaredOrientationAsEulerAngles')
        device2.setStreamingSlots(slot0='getTaredOrientationAsEulerAngles')

        # Tare and start countdown
        print("Taring in 5\n")
        for i in reversed(range(0, 5)):
            sleep(1)
            print(i)
            print('\n')

        device1.tareWithCurrentOrientation()
        device2.tareWithCurrentOrientation()
        print('GO!\n')

        return device1, device2, dng_device


def close(device):
    """Close device so next program can run"""
    device.close()
    print('\nDevices closed')


def getAutoSetup():
    '''
    Reads control file, gathers number of rounds and mode for each target
    sequence
    '''

    file = 'controlFile.csv'
    parameters_lst = []
    sequence_lst = []
    blocks_lst = []
    round_control_lst = []

    # Open data file, write header
    with open(file, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)

        # 1st line of parameters, skip header lines
        next(csvreader)
        next(csvreader)
        parameters = next(csvreader)

        # 2nd line of sequences
        next(csvreader)
        next(csvreader)
        next(csvreader)
        sequences = next(csvreader)

        # 3rd line of blocks
        next(csvreader)
        next(csvreader)
        next(csvreader)
        blocks = next(csvreader)

        # 4th line of Training Round Control Values
        next(csvreader)
        next(csvreader)
        next(csvreader)
        controls = next(csvreader)

    # Turn strings to integers
    for i in parameters:
        if i != "":
            try:
                parameters_lst.append(int(i))
            except ValueError:
                parameters_lst.append(i)

    for i in sequences:
        if i != "":
            sequence_lst.append(int(i))

    for i in blocks:
        if i != "":
            blocks_lst.append(int(i))

    for i in controls:
        if i != "":
            round_control_lst.append(float(i))

    return parameters_lst, sequence_lst, blocks_lst, round_control_lst


def intermission(time, window):
    '''Pauses game in loop until user clicks to continue'''
    intermission_start = perf_counter()
    isPaused = True
    click = None

    # Format text
    labelText = 'Click anywhere to continue.'
    entryCenterPt = graphics.Point(100, 10)
    labelCenter = entryCenterPt.clone()
    labelCenter.move(0, 10)

    # Display directions
    text = graphics.Text(labelCenter, labelText)
    text.setFill('white')
    text.draw(window)

    while isPaused:
        click = window.getMouse()
        if click:
            isPaused = False
            intermission_end = perf_counter()

    text.undraw()
    intermission_time = intermission_end - intermission_start

    return intermission_time


def getRoundType(rounds, round_lst):
    """Find which type of target sequence is being fielded, test or training"""

    isTest = False

    # is Test
    if rounds < round_lst[0] or\
        (rounds >= sum(round_lst[0:2]) and rounds < sum(round_lst[0:3]))\
            or rounds >= sum(round_lst[0:4]):

        isTest = True

    return isTest


def signalReconnect(time, dongle, training_mode, teacher_number,
                    student_number, start_time, intermission_time,
                    reconnect_time):
    """
    Handles exception when IMU signal is lost. Runs through connection and
    callibration again automaticaly, factors out lost time
    """

    drop_start_time = time
    close(dongle)

    # Register and Tare Sensors
    if training_mode == 1:
        student_sensor, dongle, = getDevices(
            training_mode, teacher_number, student_number)
    else:
        teacher_sensor, student_sensor, dongle, = getDevices(
            training_mode, teacher_number, student_number)

    # Factor out time to reconnect
    time = perf_counter() - start_time - intermission_time - reconnect_time
    drop_end_time = time
    reconnect_time += drop_end_time - drop_start_time

    return student_sensor, teacher_sensor, dongle, reconnect_time


def positionMove(window, window_bounds, max_movement_angle, ball,
                 teacher_tup=0, student_tup=0, teacher_control=0,
                 student_control=0):
    """
    Calculate poition of ball object in graphics window based on weighted
    average of teacher and student movements. Limit movement to within graphics
    window, move ball to new position.
    """

    # Convert sensor angle movement to ball movement
    x_pos = -((teacher_tup[1]*teacher_control+student_tup[1]*student_control)
              / max_movement_angle * window_bounds) + window_bounds/2
    y_pos = -((teacher_tup[2]*teacher_control+student_tup[2]*student_control)
              / max_movement_angle * window_bounds) + window_bounds/2

    # Graphics window barrier
    if x_pos > window_bounds:
        x_pos = window_bounds

    if x_pos < 0:
        x_pos = 0

    if y_pos > window_bounds:
        y_pos = window_bounds

    if y_pos < 0:
        y_pos = 0

    # Move ball between current position and next calculated position
    ball.move(x_pos-ball.x_center, y_pos-ball.y_center)
    ball.x_center = x_pos
    ball.y_center = y_pos


def displayScore(window, target_time, max_score):
    '''Calculate target round score, display text'''

    scaling = 0.1
    if target_time < 1:
        target_score = max_score
    else:
        # Exponential decay over time
        target_score = int(max_score * exp(-scaling * target_time))

    # Format text
    labelText = 'Round score: {}'.format(target_score)
    entryCenterPt = graphics.Point(75, 10)
    labelCenter = entryCenterPt.clone()
    labelCenter.move(0, 30)

    # Display score briefly, then erase text and resume play
    text = graphics.Text(labelCenter, labelText)
    text.setFill('white')
    text.draw(window)

    return target_score, text


def register(haptic_iteration):
    """
    Turn on haptic player, register all haptic files in dictionary
    (letters = keys, names = values)
    """

    player.initialize()
    # Load Tact files from directory
    for value in haptic_dict.values():
        player.register(value+str(haptic_iteration), value+str(
            haptic_iteration)+".tact")


def play(haptic_index='w', intensity=1, duration=0.5, haptic_iteration=4):
    """
    Takes string input, intensity value; selects haptic file from dict;
    plays file with adjusted intensity, options for duration and rotation
    """

    # Find indicated motion
    if haptic_index in haptic_dict:
        print('\n'+haptic_dict[haptic_index]+'\n')

        # Adjust haptics in real time
        player.submit_registered_with_option(
            haptic_dict[haptic_index]+str(haptic_iteration), "alt",
            scale_option={"intensity": intensity, "duration": duration},
            rotation_option={"offsetAngleX": 0, "offsetY": 0})


def advancedPlay(haptic_index, difference_tup, start_time, haptic_interval,
                 haptic_iteration, connection, teacher_intensity,
                 student_intensity, training_mode):
    """
    Scale haptic intensity, maintain time between buzzes, return values
    for recording, send index and intesity to teacher client.
    """
    intensity_scale = pi/6
    frequency_interval = 0.5

    if haptic_index in haptic_dict:

        # Decide which axis to check based on bigger difference
        if abs(difference_tup[1]) > abs(difference_tup[2]):
            check_coord = 1
        else:
            check_coord = 2

        # Modulate intensity based on assumed max movement angle
        raw_intensity = abs(difference_tup[check_coord])/intensity_scale
        # Can't exceed 1
        if raw_intensity > 1:
            raw_intensity = 1

        # Measures time since last buzz => maintains gap
        time = perf_counter()-start_time

        # replace interval with variable
        if time - haptic_interval > frequency_interval:
            haptic_interval = perf_counter()-start_time

            # Play for student
            play(haptic_index=haptic_index,
                 intensity=(raw_intensity * student_intensity),
                 duration=frequency_interval,
                 haptic_iteration=haptic_iteration)

            # Generate command, send to client
            if training_mode == 3:
                command = str(teacher_intensity)+'-'+str(haptic_index)+'-'+str(
                    raw_intensity)

                # Play for teacher
                connection.send(command.encode())

        angle = angle_dict[haptic_index]

    else:
        # No haptics => Intensity=0, Angle=0
        angle = 0
        raw_intensity = 0

    return angle, raw_intensity, haptic_interval


def getIndex(difference_tup, haptic_tolerance):
    """Select index for given direction moved beyond tolerance."""

    # Forward Left (-y difference and -z differnce)
    if difference_tup[1] <= -haptic_tolerance and\
            difference_tup[2] <= -haptic_tolerance:
        haptic_index = 'wa'

    # Forward Right (-z differnce and +y difference)
    elif difference_tup[2] <= -haptic_tolerance and\
            difference_tup[1] >= haptic_tolerance:
        haptic_index = 'wd'

    # Back Right (+y difference +z difference)
    elif difference_tup[1] >= haptic_tolerance and\
            difference_tup[2] >= haptic_tolerance:
        haptic_index = 'sd'

    # Back Left (+z difference and -y difference)
    elif difference_tup[2] >= haptic_tolerance and\
            difference_tup[1] <= -haptic_tolerance:
        haptic_index = 'sa'

    # Forward (-z differnce)
    elif difference_tup[2] <= -haptic_tolerance and\
            abs(difference_tup[1]) < abs(difference_tup[2]):
        haptic_index = 'w'

    # Left (-y difference)
    elif difference_tup[1] <= -haptic_tolerance and\
            abs(difference_tup[1]) > abs(difference_tup[2]):
        haptic_index = 'a'

    # Right (+y difference)
    elif difference_tup[1] >= haptic_tolerance and\
            abs(difference_tup[1]) > abs(difference_tup[2]):
        haptic_index = 'd'

    # Back (+z difference)
    elif difference_tup[2] >= haptic_tolerance and\
            abs(difference_tup[1]) < abs(difference_tup[2]):
        haptic_index = 's'

    return haptic_index


def writeData(file, time, teacher_tup, student_tup, difference_tup,
              raw_intensity, teacher_intensity, student_intensity,
              angle, score, target_time, ball, target, target_number,
              training_mode, round_type):
    """
    Take timestamp, position data, haptics data, write to csv file
    """

    # Teacher's haptics is always 180 degrees opposite student
    if angle > 0 and angle <= pi:
        angle_teacher = angle + pi
    elif angle > pi:
        angle_teacher = angle - pi
    else:
        angle_teacher = 0

    # Write to file
    with open(file, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
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
                            str(round(raw_intensity*teacher_intensity, 3)),
                            str(round(raw_intensity*student_intensity, 3)),
                            str(round((angle_teacher), 2)),
                            str(round(angle, 2)),
                            str(round(ball.x_center)),
                            str(round(ball.y_center)),
                            str(round(target.x_center)),
                            str(round(target.y_center)),
                            str(target_number),
                            str(score),
                            str(round(target_time, 3)), str(training_mode),
                            str(round_type)])
