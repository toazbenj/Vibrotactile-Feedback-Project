"""
Tandem Control Game

    Sentinels and Conditions

    Try
        Get numbers of round types
        Set up devices
        Link to 2nd computer
        Make graphics window
        Register and tare sensors
        Register haptic files
        Make ball graphics

        Main loop
            Pause before block start
            For each block
                If control changes by block
                    Get round type
                    Get control sharing

                For each sequence
                    Get round type
                    If control changes by round
                        Get control sharing

                    If not testing
                        Randomly generate list of 8 angles
                    Else testing
                        Randomly generate list of 4 angles

                    Intersperse center target angles (0) in between angles

                    For each angle
                        Create target at that angle and predetermined radius

                        While target not reached
                            Get position data
                            If no data
                                Handle signal drop
                                Reconnect

                            Select haptics
                            Play haptics
                            Invert motion sensor directions
                            Move ball object

                            If target is hit
                                Record first hit

                                If within target for full duration
                                    Undraw target
                                    Calculate score
                                    Record data
                                    Break while loop

                            Record data
        Display Score

    Except KeyboardInterrupt (Manual shutdown)
    Except NameError (Setup incomplete)
    Except PermissionError (CSV is open)
    Except AttributeError (Motion sensor is off)
    Except serial.SerialException (Previous error, must refresh)
    Except OSError (Old client connection)

    Finally (no matter what)
        Cut client connection
        Close Window
        Close Dongle

Created on Thu Dec 23 08:19:17 2021
@author: Ben Toaz
"""

import serial
import graphics
import utilitiesMethods as utilities
from math import pi
from time import perf_counter
from random import randint
import csv
from math import sin
from math import cos
import socket

# Sentinels/Conditions

# Turn on for testing, activates printouts, targets all spawn in center
isEasyMode = False

# Time
time = 0
target_time = 0
target_achieved_interval = 0.5
previous_target_time = 0
target_achieved_start_time = 0
reconnect_time = 0
intermission_time = 0

# Gameplay
target_miss_margin = 20
score = 0
max_score = 100

# Graphics
training_lst = [2*pi, pi/4, pi/2, 3*pi/4, pi, 5*pi/4, 3*pi/2, 7*pi/4]
testing_lst = [2*pi, pi/2, pi, 3*pi/2]
target_number_dict = {0: 0, pi/4: 1, pi/2: 6, 3*pi/4: 3, pi: 4, 5*pi/4: 5,
                      3*pi/2: 2, 7*pi/4: 7, 2*pi: 8}
window_bounds = 600
target_reach_radius = 3/10*window_bounds
score_text = graphics.Point(0, 0)

# Haptics
max_movement_angle = pi/8
haptic_index = ''
haptic_iteration = 4
haptic_interval = 0
haptic_tolerance = pi/48

# Data
header = ['Time', 'Teacher-x', 'Teacher-y', 'Teacher-z', 'Student-x',
          'Student-y', 'Student-z', 'Difference-x', 'Difference-y',
          'Difference-z', 'Teacher Intensity', 'Student Intensity',
          'Angle Teacher', 'Angle Student', 'Ball-x', 'Ball-y', 'Target-x',
          'Target-y', 'Target Number', 'Score', 'Target Duration',
          'Training Mode', 'Is Testing Boolean']

# Pre Game start setup
try:
    # Get blocks, sequences and training mode
    parameters_lst, sequence_lst, blocks_lst, round_control_lst =\
        utilities.getAutoSetup()
    isGraduated = round_control_lst[0]

    # Device setup
    training_mode = parameters_lst[0]
    teacher_number = parameters_lst[1]
    student_number = parameters_lst[2]
    file = parameters_lst[3]
    isSecondComputer = parameters_lst[4]

    # Calculate number of each type of rounds
    pretest_rounds = sequence_lst[0] * blocks_lst[0]
    training_one_rounds = sequence_lst[1] * blocks_lst[1]
    midtest_rounds = sequence_lst[2] * blocks_lst[2]
    training_two_rounds = sequence_lst[3] * blocks_lst[3]
    posttest_rounds = sequence_lst[4] * blocks_lst[4]

    round_lst = [pretest_rounds, training_one_rounds, midtest_rounds,
                 training_two_rounds, posttest_rounds]

    overall_score = 100 * (16 * (
        pretest_rounds + posttest_rounds + midtest_rounds) +
        8 * (training_one_rounds + training_two_rounds))

    if training_mode == 3 and isSecondComputer:
        # Link to 2nd computer
        socket = socket.socket()
        port = 8080

        socket.bind(('', port))
        print("waiting for connections...")
        socket.listen()
        connection, address = socket.accept()
        print(address, "is connected to server")
    else:
        connection = 0

    # Make Graphics Window
    window = graphics.GraphWin(width=window_bounds, height=window_bounds)
    window.setBackground('black')

    # Register haptic files
    utilities.register(haptic_iteration)

    # Register and Tare Sensors
    if training_mode == 1:
        student_sensor, dongle, = utilities.getDevices(
            training_mode, teacher_number, student_number)
    else:
        teacher_sensor, student_sensor, dongle, = utilities.getDevices(
            training_mode, teacher_number, student_number)

    start_time = perf_counter()

    # Write new header
    with open(file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(header)

    # Make Ball
    point = graphics.Point(window_bounds/2, window_bounds/2)
    ball = graphics.Circle(point, 25)
    ball.setOutline('white')
    ball.setFill('white')
    ball.draw(window)

    # Main loop, iterate through each round
    rounds = 0
    for master_index in range(len(sequence_lst)):
        # Pause for break in between testing and training blocks
        intermission_time += utilities.intermission(time, window)

        if isEasyMode:
            print()

        for block in range(blocks_lst[master_index]):

            if not isGraduated:
                isTest = utilities.getRoundType(rounds, round_lst)
                teacher_control, student_control, teacher_intensity,\
                    student_intensity = utilities.getSharing(rounds, isTest,
                                                             round_lst,
                                                             round_control_lst,
                                                             sequence_lst,
                                                             blocks_lst, block,
                                                             master_index,
                                                             training_mode,
                                                             rounds)
            if isEasyMode:
                print()

            for sequence in range(sequence_lst[master_index]):
                isTest = utilities.getRoundType(rounds, round_lst)

                if isGraduated:
                    teacher_control, student_control, teacher_intensity,\
                        student_intensity = utilities.getSharing(
                            rounds,
                            isTest,
                            round_lst,
                            round_control_lst,
                            sequence_lst,
                            blocks_lst,
                            block,
                            master_index,
                            training_mode,
                            rounds)

                if isEasyMode:
                    print(student_control)

                # For testing
                # if isEasyMode:
                #     print("Round: {}, Testing: {}".format(rounds + 1,
                #           isTest))

                # Generates random list of rotation angles
                angle_lst = []
                if not isTest:
                    # 4 Targets for training
                    for i in testing_lst:
                        position = randint(0, 4)
                        try:
                            move_angle = angle_lst[position]
                            angle_lst[position] = i
                            angle_lst.append(move_angle)
                        except IndexError:
                            angle_lst.append(i)

                    if isEasyMode:
                        angle_lst = [0, 0, 0, 0]

                else:
                    # 8 Targets for testing
                    for i in training_lst:
                        position = randint(0, 8)
                        try:
                            move_angle = angle_lst[position]
                            angle_lst[position] = i
                            angle_lst.append(move_angle)
                        except IndexError:
                            angle_lst.append(i)

                    if isEasyMode:
                        angle_lst = [0, 0, 0, 0, 0, 0, 0, 0]

                # Puts center targets in between random targets
                count = 0
                for t in angle_lst:
                    if count % 2 != 0:
                        angle_lst[count] = 0
                        angle_lst.append(t)

                    count += 1

                angle_lst.append(0)

                time = (perf_counter() - start_time - intermission_time
                        - reconnect_time)

                target_count = 1
                # Iterate through each target attempt
                for i in angle_lst:
                    # Make target
                    target_number = target_number_dict[i]
                    # Reach target
                    if i != 0:
                        x_coord = window_bounds * (1/2) + (target_reach_radius
                                                           * (cos(i)))
                        y_coord = window_bounds * (1/2) + (target_reach_radius
                                                           * (sin(i)))
                    # Center reset target
                    else:
                        x_coord = window_bounds/2
                        y_coord = window_bounds/2

                    count += 1

                    point = graphics.Point(x_coord, y_coord)
                    target = graphics.Circle(point, 35)
                    target.setOutline('red')
                    target.setWidth(5)
                    target.draw(window)

                    # Movement Loop
                    while True:

                        # Get position data
                        if training_mode == 1:
                            student_tup = student_sensor.getStreamingBatch()

                            # Signal Drop Handling
                            if student_tup is None:
                                student_tup = (0, 0, 0)
                                print("Student read failed")

                                student_sensor, teacher_sensor, dongle,\
                                    reconnect_time = utilities.signalReconnect(
                                        time, dongle, training_mode,
                                        teacher_number, student_number,
                                        start_time, intermission_time,
                                        reconnect_time)

                            teacher_tup = (0, 0, 0)
                            difference_tup = (0, 0, 0)

                        else:
                            teacher_tup = teacher_sensor.getStreamingBatch()

                            # Signal drop handling
                            if teacher_tup is None:
                                teacher_tup = (0, 0, 0)
                                print("Teacher read failed")

                                student_sensor, teacher_sensor, dongle,\
                                    reconnect_time = utilities.signalReconnect(
                                        time, dongle, training_mode,
                                        teacher_number, student_number,
                                        start_time, intermission_time,
                                        reconnect_time)

                            student_tup = student_sensor.getStreamingBatch()

                            # Signal drop handling
                            if student_tup is None:
                                student_tup = (0, 0, 0)
                                print("Student read failed")

                                student_sensor, teacher_sensor, dongle,\
                                    reconnect_time = utilities.signalReconnect(
                                        time, dongle, training_mode,
                                        teacher_number, student_number,
                                        start_time, intermission_time,
                                        reconnect_time)

                            difference_tup = (student_tup[0]-teacher_tup[0],
                                              student_tup[1]-teacher_tup[1],
                                              student_tup[2]-teacher_tup[2])

                        # Select haptics direction
                        haptic_index = utilities.getIndex(difference_tup,
                                                          haptic_tolerance)

                        # Play haptics, return values for recording
                        angle, raw_intensity, haptic_interval = \
                            utilities.advancedPlay(haptic_index,
                                                   difference_tup, start_time,
                                                   haptic_interval,
                                                   haptic_iteration,
                                                   connection,
                                                   teacher_intensity,
                                                   student_intensity,
                                                   training_mode,
                                                   isSecondComputer)

                        # Invert y and z angles to switch x and y for ball
                        student_tup = (student_tup[0], student_tup[2],
                                       student_tup[1])

                        if not isTest and training_mode != 1:
                            teacher_tup = (teacher_tup[0], teacher_tup[2],
                                           teacher_tup[1])

                        # Move ball
                        utilities.positionMove(window, window_bounds,
                                               max_movement_angle, ball,
                                               teacher_tup, student_tup,
                                               teacher_control,
                                               student_control)

                        # Check if target is hit
                        x_diff = abs(ball.getCenter().x-target.getCenter().x)
                        y_diff = abs(ball.getCenter().y-target.getCenter().y)

                        time = (perf_counter() - start_time -
                                intermission_time - reconnect_time)

                        if x_diff < target_miss_margin and \
                                y_diff < target_miss_margin:

                            target.setOutline('green')
                            time = (perf_counter() - start_time -
                                    intermission_time - reconnect_time)

                            # First hit
                            if target_achieved_start_time == 0:
                                target_achieved_start_time = time

                            # Kept within target
                            elif time - target_achieved_start_time\
                                    > target_achieved_interval:

                                target.undraw()
                                score_text.undraw()

                                # Calculate time taken and score for attempt
                                target_time = time - previous_target_time
                                round_score, score_text = \
                                    utilities.displayScore(window,
                                                           target_time,
                                                           max_score)

                                score += round_score
                                previous_target_time += target_time

                                # Record data
                                time = (perf_counter() - start_time -
                                        intermission_time - reconnect_time)
                                utilities.writeData(file, time, teacher_tup,
                                                    student_tup,
                                                    difference_tup,
                                                    raw_intensity,
                                                    teacher_intensity,
                                                    student_intensity,
                                                    angle, score, target_time,
                                                    ball, target,
                                                    target_number,
                                                    training_mode,
                                                    isTest)

                                if isEasyMode:
                                    # print('Target {}'.format(target_count))
                                    pass

                                # Exit move loop
                                target_count += 1

                                # If last target in round increase round count
                                if angle_lst.index(i) == len(angle_lst) - 1:
                                    rounds += 1

                                # Exit target loop
                                break

                        # Reset when target overshot
                        else:
                            target.setOutline('red')
                            target_achieved_start_time = 0

                        # Set to 0 for recording purposes
                        target_time = 0

                        # Record data
                        time = (perf_counter() - start_time -
                                intermission_time - reconnect_time)
                        utilities.writeData(file, time, teacher_tup,
                                            student_tup, difference_tup,
                                            raw_intensity, teacher_intensity,
                                            student_intensity, angle, score,
                                            target_time, ball, target,
                                            target_number, training_mode,
                                            isTest)
                rounds += 1

    # Display Results
    print('\nYour time is {}.'.format(round(time, 2)))
    print('\nYour score is {} out of {}.'.format(score, (overall_score)))

# Note: the following except statements handle common errors that occur when
# the program runs properly but user error causes issues. If problem persists,
# comment out except clauses to see the actual error.

# For manual shutdown
except KeyboardInterrupt:
    print('\nManual shutdown')
    print('\nYour time is {}.'.format(round(time, 2)))
    print('\nYour score is {} out of {}.'.format(score, (overall_score)))

# Setup incomplete
except NameError:
    print('\nSetup incomplete')

# Forgot to close the CSV file
except PermissionError:
    print('\nClose CSV File')

# Motion sensors not on or need to be charged
except AttributeError:
    print('\nTurn on motion sensors')

# Dongle wasn't closed properly or open in another program
except serial.SerialException:
    print('\nRefresh kernal or check dongle connection')

# Client connection needs to refresh
except OSError:
    print('\nRun again to refresh client connection')

except KeyError:
    print('\nCheck that student control values in control file match number',
          'of rounds/blocks')

# No matter what, close peripherals
finally:
    try:
        if training_mode == 3:
            connection.close()
        window.close()
        utilities.close(dongle)

    # If setup not complete and issues, ignore issues
    except:
        pass
