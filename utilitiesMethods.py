# -*- coding: utf-8 -*-
"""
Utility Methods for Yosh Labs Sensors and bHaptics Tactsuit
    userInput
            User input loop to handle incorrect entries
    getMode
        rompts user to select participant and haptic configuration

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

    getSharing
        Receive/calculate the amount of cursor control and intensity for
        student/teacher

    getDevices
        Search for docked devices, make list, assign names and orientation,
        display battery levels, tare countdown, return devices

    velocityMove
        Calculate pixel velocity of ball object based on weighted average
        of teacher and student movements. Limit movement based on speed limit,
        respawn ball in center if out of bounds

    positionMove
        Calculate poition of ball object in graphics window based on weighted
        average of teacher and student movements. Limit movement to within
        graphics window, move ball to new position

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
from math import exp
from time import perf_counter
from time import sleep
import graphics

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


def getMode():
    """Prompts user to select participant and haptic configuration"""

    options = "Modes: \
        \n(1) No Teacher, No Haptics \
        \n(2) Teacher, No Haptics \
        \n(3) Teacher, Haptics"

    print(options)

    mode = userInput('Select mode >>')

    return mode


def userInput(prompt):
    """User input loop to handle incorrect entries"""

    isCorrect = False

    while not isCorrect:

        string = input(prompt)

        try:
            num = int(string)
            isCorrect = True

        except TypeError:
            continue

        except ValueError:
            continue

    return num


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


def advancedPlay(index, difference_tup, start, commandTime, iteration,
                 connection, teacher_intensity, student_intensity, mode):
    """
    Scale haptic intensity, maintain time between buzzes, return values
    for recording, send index and intesity to teacher client.
    """
    intensity_scale = pi/6
    frequency_interval = 0.5

    if index in haptic_dict:

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
        time = perf_counter()-start

        # replace interval with variable
        if time - commandTime > frequency_interval:
            commandTime = perf_counter()-start

            # Play for student
            play(index=index, intensity=(raw_intensity*student_intensity),
                 duration=frequency_interval, iteration=iteration)

            # Generate command, send to client
            if mode == 3:
                command = str(teacher_intensity)+'-'+str(index)+'-'+str(
                    raw_intensity)

                # Play for teacher
                connection.send(command.encode())

        angle = angle_dict[index]

    else:
        # No haptics => Intensity=0, Angle=0
        angle = 0
        raw_intensity = 0

    return angle, raw_intensity, commandTime


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


<<<<<<< HEAD
def getSharing(mode, rounds, isAuto, pretest_rounds, training_rounds, 
               posttest_rounds):
=======
>>>>>>> 556be1723355dc5bc9da4156e4252d04065b16cc
    """
    Receive/calculate the amount of cursor control and intensity for
    student/teacher
    """
    
    
    # Need to revamp for pretest, training and post test rounds
    
    
    
    # Increasing amount of student control for each round
    round_control_dict = {1:0.1, 2:0.25, 3:0.50, 4:0.75, 5:0.90}
    
    isTest = rounds < pretest_rounds or rounds >= posttest_rounds + training_rounds
    
    # No Teacher, No Haptics
    if isTest:
        teacher_control = 0
        student_control = 1
        teacher_intensity = 0
        student_intensity = 0

    # Teacher, No Haptics
    elif not isTest and mode == 2:
        if isAuto:
            student_control = round_control_dict[rounds-pretest_rounds]
            teacher_control = 1-student_control
    
            # No haptics
            student_intensity = 0
            teacher_intensity = 0
            
        else:
            
            key = userInput('Enter student control proportion(%)>>')
            student_control = float(key)*0.01
            teacher_control = 1-student_control
    
            # No haptics
            student_intensity = 0
            teacher_intensity = 0

    #  Teacher, Haptics
    else:
        if isAuto:

            student_control = round_control_dict[rounds-pretest_rounds]
            teacher_control = 1-student_control
    
            # Amount of intensity is inverse of amount of control
            student_intensity = teacher_control
            teacher_intensity = student_control
        
        else:
            key = userInput('Enter student control proportion(%)>>')
            student_control = float(key)*0.01
            teacher_control = 1-student_control
    
            # Amount of intensity is inverse of amount of control
            student_intensity = teacher_control
            teacher_intensity = student_control

    return teacher_control, student_control, teacher_intensity, \
        student_intensity


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
    
    if isAuto:
        # No teacher, no haptics
        if mode == 1:
    
            device1 = device_dict[int(student_sensor)]
    
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
    
            device1 = device_dict[int(teacher_sensor)]
            device2 = device_dict[int(student_sensor)]
    
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
    else:
    # No teacher, no haptics
        if mode == 1:
    
            key = userInput('Select student (1,3,4)>>')
            device1 = device_dict[int(key)]
    
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
    
            key = userInput('Select teacher (1,3,4)>>')
            device1 = device_dict[int(key)]
    
            key = userInput('Select student (1,3,4)>>')
            device2 = device_dict[int(key)]
    
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


def velocityMove(ball, teacher_tup, student_tup, teacher_control,
                 student_control, tolerance, window, speed_limit, bounds):
    """
    Calculate pixel velocity of ball object based on weighted average
    of teacher and student movements. Limit movement based on speed limit,
    respawn ball in center if out of bounds.
    """
    # Euler angles to pixels
    scaling_factor = 10/(2*pi/4)

    # Convert sensor angle movement to ball movement
    if checkTolerance(teacher_tup, tolerance) or\
            checkTolerance(student_tup, tolerance):

        # Scaling factors subjective for moderate difficulty
        x_move = (teacher_control*teacher_tup[1]+student_control
                  * student_tup[1]) / scaling_factor

        y_move = (teacher_control*teacher_tup[2]+student_control
                  * student_tup[2]) / scaling_factor

        #  y_move = (teacher_control*teacher_tup[2]+student_control
                  # * student_tup[2]) / (2*pi/4) * 10

    else:
        x_move = 0
        y_move = 0

    # If speed limit exceeded, sets speed to limit in same direction
    if abs(x_move) > speed_limit:
        x_move = speed_limit * (x_move/x_move)
    if abs(y_move) > speed_limit:
        y_move = speed_limit * (y_move/y_move)

    # Move ball, record motion within object
    ball.move(-x_move, -y_move)
    ball.x_center += x_move
    ball.y_center += y_move

    # Respawns ball in center of window if out of bounds
    if ball.getCenter().x > bounds or ball.getCenter().y > bounds\
            or ball.getCenter().x < 0 or ball.getCenter().y < 0:

        ball.undraw()

        pt = graphics.Point(bounds/2, bounds/2)
        ball = graphics.Circle(pt, 25)
        ball.setOutline('blue')
        ball.setFill('blue')
        ball.draw(window)


def positionMove(window, bounds, max_movement_angle, ball, teacher_tup=0,
                 student_tup=0, teacher_control=0, student_control=0):
    """
    Calculate poition of ball object in graphics window based on weighted
    average of teacher and student movements. Limit movement to within graphics
    window, move ball to new position.
    """

    # Convert sensor angle movement to ball movement
    x_pos = -((teacher_tup[1]*teacher_control+student_tup[1]*student_control)
              / max_movement_angle * bounds) + bounds/2
    y_pos = -((teacher_tup[2]*teacher_control+student_tup[2]*student_control)
              / max_movement_angle * bounds) + bounds/2

    # print('\n')
    # print('{},{}'.format(round(x_pos,2),round(y_pos,2)))
    # print('\n')
    # print('{},{}'.format(round(student_tup[1],2),round(student_tup[2],2)))

    # Graphics window barrier
    if x_pos > bounds:
        x_pos = bounds

    if x_pos < 0:
        x_pos = 0

    if y_pos > bounds:
        y_pos = bounds

    if y_pos < 0:
        y_pos = 0

    # Move ball between current position and next calculated position
    ball.move(x_pos-ball.x_center, y_pos-ball.y_center)
    ball.x_center = x_pos
    ball.y_center = y_pos


def displayScore(bounds, window, target_time, pause, max_score):
    '''
    Calculate target round score, briefly display text and resume play
    '''
    # Calcuate score based on exponenital decay over time
    scaling = 0.1
    
    if target_time < 1:
        target_score = 100
    else:
        target_score = int(max_score * exp(-scaling * target_time))

    # Format text
    labelText = 'Round score: {}'.format(target_score)
    entryCenterPt = graphics.Point(75,10)
    labelCenter = entryCenterPt.clone()
    labelCenter.move(0, 30)
    
    # Display score briefly, then erase text and resume play
    text = graphics.Text(labelCenter,labelText)
    text.setFill('white')
    text.draw(window)
    sleep(pause)
    text.undraw()
        
    return target_score
    

def checkTolerance(check_tup, tolerance):
    """Determine if coordinates exceed tolerance."""
    if check_tup[1] > tolerance or check_tup[1] < -tolerance\
            or check_tup[2] > tolerance or check_tup[2] < -tolerance:

        return True

    else:

        return False


def close(device):
    """Close device so next program can run"""
    device.close()
    print('\nDevices closed')


def writeData(file, time, teacher_tup, student_tup, difference_tup,
              raw_intensity, teacher_intensity, student_intensity,
              angle, score, target_time, ball, target,  training_mode,
              round_type, isFollowMe):
    """
    Take timestamp, position data, haptics data, write to csv file. Overloaded
    so parameter of true for isFollowMe will write without a score (followMe)
    and anything else will result in writing with score (tandemControlGame)
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

        # Demo program with just haptics, no graphics
        if isFollowMe:
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
                                str(round(raw_intensity, 3)),
                                str(round(angle, 2))])

        # Tandem control program
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
                                str(round(raw_intensity*teacher_intensity, 3)),
                                str(round(raw_intensity*student_intensity, 3)),
                                str(round((angle_teacher), 2)),
                                str(round(angle, 2)),
                                str(round(ball.x_center)),
                                str(round(ball.y_center)),
                                str(round(target.x_center)),
                                str(round(target.y_center)),
                                str(score),
                                str(round(target_time, 3)), str(training_mode),
                                str(round_type)])

# Currently not in use, made for test programs
def testPos(pos_tup1, pos_tup2, tolerance=0):
    """
    Takes position tuple and margin of error tolerance, if position in each
    coordinate +/- toleance is less than 0.5 from 0, return true, else false
    """

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


def getAutoSetup():
    '''Reads control file, gathers number of rounds and mode for each target sequence'''
    file = 'controlFile2.csv'
    # Open data file, write header
    with open(file, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        row = next(csvreader)
            
    pretest_rounds = int(row[0])
    training_rounds = int(row[1])
    posttest_rounds = int(row[2])
    mode = int(row[3])
    teacher_sensor = int(row[4])    
    student_sensor = int(row[5])
    
    return pretest_rounds, training_rounds, posttest_rounds, mode,\
        teacher_sensor, student_sensor


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
    text = graphics.Text(labelCenter,labelText)
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
