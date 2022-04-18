"""
MultiRound Tandem Control Game

    Try
        Link to 2nd computer
        Make graphics window
        Register and tare sensors
        Register haptic files
        Make ball graphic
        Set conditions

        Main loop
            Spawn target

            Movement loop
                Get position data
                Select haptics direction
                Play haptics, return recorded values
                Convert sensor angle movement to ball movement
                Respawn ball if out of bounds
                Checks for hit target

        Close window
        Close sensors
        Display Score
        Cut client connection

    Except KeyboadInterrupt
        Cut client connection
        Close window
        Close sensors
        Display message

    Except NameError
        Cut client connection
        Close window
        Close dongle
        Display message

    Except PermissionError
        Cut client connection
        Close window
        Close dongle
        Display message
        
    except AttributeError:
        Display message
        
    except serial.SerialException:
        Display message
        
    except OSError:
        Display message
        
Reference: http://anh.cs.luc.edu/handsonPythonTutorial/graphics.html

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

# Graphics/Gaming
isAuto = True
isEasyMode = True

time = 0
target_time = 0
previous_target_time = 0
target_achieved_start = 0
reconnect_time = 0

pause = 1

tolerance = pi/48
miss_margin = 20
speed_limit = 15

score = 0
targets = 0
max_score = 100

training_lst = [2*pi, pi/4, pi/2, 3*pi/4, pi, 5*pi/4, 3*pi/2, 7*pi/4]
testing_lst = [2*pi, pi/2, pi, 3*pi/2]

bounds = 600
radius = 3/10*bounds
isCenter = False

position_offset = randint(10,30) * pi/180
text = graphics.Point(0,0)

# Haptics
max_movement_angle = pi/8
index = ''
iteration = 4
commandTime = 0

# Data
header = ['Time', 'Teacher-x', 'Teacher-y', 'Teacher-z', 'Student-x',
          'Student-y', 'Student-z', 'Difference-x', 'Difference-y',
          'Difference-z', 'Teacher Intensity', 'Student Intensity',
          'Angle Teacher', 'Angle Student', 'Ball-x', 'Ball-y', 'Target-x',
          'Target-y', 'Score','Target Duration', 'Training Mode', 'Is Testing Boolean']
isFollowMe = False
intermission_time = 0

# Pre Game start setup
try:
    # Get blocks, units and training mode
    parameters_lst, units_lst, blocks_lst= utilities.getAutoSetup()
    
    # Device setup
    training_mode = parameters_lst[0]
    teacher_sensor = parameters_lst[1]
    student_sensor = parameters_lst[2]
    file = parameters_lst[3]

    # Calculate number of each type of rounds
    pretest_rounds = units_lst[0] * blocks_lst[0]
    training_one_rounds = units_lst[1] * blocks_lst[1]
    midtest_rounds = units_lst[2] * blocks_lst[2]
    training_two_rounds = units_lst[3] * blocks_lst[3]
    posttest_rounds = units_lst[4] * blocks_lst[4]
    
    round_lst = [pretest_rounds, training_one_rounds, midtest_rounds, 
                 training_two_rounds, posttest_rounds]
    
    # Round numbers after which block gaps occur
    pause_sentinel_lst = [sum(round_lst[0:1])-1, sum(round_lst[0:2])-1, 
                          sum(round_lst[0:3])-1, sum(round_lst[0:4])-1]
    
    overall_score = 100 * (16 * (
        pretest_rounds + posttest_rounds + midtest_rounds) + 
        8 * (training_one_rounds + training_two_rounds))
    
    if training_mode == 3:
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
    window = graphics.GraphWin(width=bounds, height=bounds)
    window.setBackground('black')

    # Register haptic files
    utilities.register(iteration)

    # Register and Tare Sensors
    if training_mode == 1:
        student, dongle, = utilities.getDevices(
            training_mode, isAuto, teacher_sensor, student_sensor)
    else:
        teacher, student, dongle, = utilities.getDevices(
            training_mode, isAuto, teacher_sensor, student_sensor)
        
    start = perf_counter()
    
    # Write new header
    with open(file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(header)
        
    # Make Ball
    point = graphics.Point(bounds/2, bounds/2)
    ball = graphics.Circle(point, 25)
    ball.setOutline('white')
    ball.setFill('white')
    ball.draw(window)
    
    # Pause before start
    intermission_time += utilities.intermission(time, window)

    
    # Main loop, iterate through each round
    for rounds in range(sum(round_lst)):
        
        # Pre round setup
        # Find which type of target sequence is being fielded
        
        isTest = utilities.getRoundType(rounds, round_lst)
        
        # For testing
        if isEasyMode:
            print(rounds + 1, isTest)
        
        # Generates random list of rotation angles
        rand_lst = []
        if not isTest:
             # 4 Targets for training
            for i in testing_lst:
                position = randint(0, 4)
                try:
                    move = rand_lst[position]
                    rand_lst[position] = i
                    rand_lst.append(move)
                except IndexError:
                    rand_lst.append(i)
            
            if isEasyMode:
                rand_lst = [0,0,0,0]
            
        else:
            # 8 Targets for testing
            for i in training_lst:
                position = randint(0, 8)
                try:
                    move = rand_lst[position]
                    rand_lst[position] = i
                    rand_lst.append(move)
                except IndexError:
                    rand_lst.append(i)
                    
            if isEasyMode:
                rand_lst = [0,0,0,0,0,0,0,0]
                
        # Puts center targets in between random targets
        count = 0
        for t in rand_lst:
            if count%2 != 0:
                rand_lst[count] = 0
                rand_lst.append(t)
                 
            count += 1
            
        rand_lst.append(0)
        
        # Control and intensity ratios
        teacher_control, student_control, teacher_intensity, student_intensity\
            = utilities.getSharing(round_lst, rounds, isAuto)

        # Pause for break in between testing and training blocks
        if rounds in pause_sentinel_lst:
            intermission_time += utilities.intermission(time, window)
            
            if isEasyMode:
                print()
            
        time = perf_counter() - start - intermission_time - reconnect_time

        target_count = 1
        # Iterate through each target attempt
        for i in rand_lst:
            # Make target
            
            # Reach target
            if i != 0:
                x_coord = bounds * (1/2) + radius * (cos(i))
                y_coord = bounds * (1/2) + radius * (sin(i))
            # Center reset target
            else:
                x_coord = bounds/2
                y_coord = bounds/2
                
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
                    student_tup = student.getStreamingBatch()
                    
                    # Switches coordinates for left/right and up/down
                    # Originally +z forward and +y left
                    # Now -y forward and +z left
                    try:
                        student_tup = (student_tup[0], student_tup[2], student_tup[1])
                        
                    except TypeError:
                        student_tup = (0,0,0)
                        drop_start_time = time
                        utilities.close(dongle)
                        print("Student read failed")
                        
                        # Register and Tare Sensors
                        if training_mode == 1:
                            student, dongle, = utilities.getDevices(
                                training_mode, isAuto, teacher_sensor, student_sensor)
                        else:
                            teacher, student, dongle, = utilities.getDevices(
                                training_mode, isAuto, teacher_sensor, student_sensor)
                            
                        time = perf_counter() - start - intermission_time - reconnect_time
                        drop_end_time = time
                        reconnect_time += drop_end_time - drop_start_time
                    
                    teacher_tup = (0, 0, 0)
                    difference_tup = (0, 0, 0)
    
                else:
                    teacher_tup = teacher.getStreamingBatch()
                    
                    # Signal drop reconnect
                    try:
                        teacher_tup = (teacher_tup[0], teacher_tup[2], teacher_tup[1])
                    except TypeError:
                        teacher_tup = (0,0,0)
                        print("Teacher read failed")
                        
                        utilities.close(dongle)
                        
                        # Register and Tare Sensors
                        if training_mode == 1:
                            student, dongle, = utilities.getDevices(
                                training_mode, isAuto, teacher_sensor, student_sensor)
                        else:
                            teacher, student, dongle, = utilities.getDevices(
                                training_mode, isAuto, teacher_sensor, student_sensor)
                            
                        time = perf_counter() - start - intermission_time - reconnect_time
                        drop_end_time = time
                        reconnect_time += drop_end_time - drop_start_time
                        
                    student_tup = student.getStreamingBatch()
                    
                    # Signal drop reconnect
                    try:
                        student_tup = (student_tup[0], student_tup[2], student_tup[1])
                    except TypeError:
                        student_tup = (0,0,0)
                        print("Student read failed")
                        
                        utilities.close(dongle)
                        
                        # Register and Tare Sensors
                        if training_mode == 1:
                            student, dongle, = utilities.getDevices(
                                training_mode, isAuto, teacher_sensor, student_sensor)
                        else:
                            teacher, student, dongle, = utilities.getDevices(
                                training_mode, isAuto, teacher_sensor, student_sensor)
                            
                        time = perf_counter() - start - intermission_time - reconnect_time
                        drop_end_time = time
                        reconnect_time += drop_end_time - drop_start_time
                        
                    difference_tup = (student_tup[0]-teacher_tup[0],
                                      student_tup[1]-teacher_tup[1],
                                      student_tup[2]-teacher_tup[2])
    
                # Select haptics direction
                index = utilities.getIndex(difference_tup, tolerance)
    
                # Play haptics, return values for recording
                angle, raw_intensity, commandTime = utilities.advancedPlay(
                    index, difference_tup, start, commandTime, iteration,
                    connection, teacher_intensity, student_intensity, training_mode)
    
                # Move ball
                utilities.positionMove(window, bounds,
                                       max_movement_angle, ball, teacher_tup,
                                       student_tup, teacher_control,
                                       student_control)

                # Check if target is hit
                x_diff = abs(ball.getCenter().x-target.getCenter().x)
                y_diff = abs(ball.getCenter().y-target.getCenter().y)
                    
                if x_diff < miss_margin and y_diff < miss_margin:
                    target.setOutline('green')

                    # First hit
                    if target_achieved_start == 0:
                        target_achieved_start = time
                    
                    # Kept within target
                    elif time - target_achieved_start > 0.5:
                        
                    
                        target.undraw()
                        text.undraw()
    
                        # Calculate time taken and calculate score for attempt
                        target_time = time - previous_target_time
                        round_score, text = utilities.displayScore(bounds, window, 
                                                        target_time, max_score)
                        score += round_score
                        previous_target_time += target_time
                        targets += 1
                        
                        # Record data
                        time = perf_counter() - start - intermission_time - reconnect_time
                        utilities.writeData(file, time, teacher_tup, student_tup,
                                            difference_tup, raw_intensity,
                                            teacher_intensity, student_intensity, 
                                            angle, score, target_time, ball,
                                            target, training_mode,
                                            isTest, isFollowMe)
                        
                        if isEasyMode:
                            print('Target {}'.format(target_count))
                        
                        # Exit move loop
                        target_count += 1
                        break
                        
                # Reset when target overshot
                else:
                    target.setOutline('red')
                    target_achieved_start = 0 
                
                # Set to 0 for recording purposes
                target_time = 0
                
                # Record data
                # print("Signal strength: {}".format(dongle.getSignalStrength()))
                time = perf_counter() - start - intermission_time - reconnect_time
                
                print(time)
                
                utilities.writeData(file, time, teacher_tup, student_tup,
                                    difference_tup, raw_intensity,
                                    teacher_intensity, student_intensity, 
                                    angle, score, target_time, ball, target,
                                    training_mode, isTest, isFollowMe)
                
    # Display Results
    print('\nYour time is {}.'.format(round(time, 2)))
    print('\nYour score is {} out of {}.'.format(score, (overall_score)))

# Note: the following except statements handle common errors that occur when 
# the program runs properly but user error causes issues. If problem persists,
# comment out except clauses to see the actual error

# For manual shutdown
except KeyboardInterrupt:
    print('\nManual shutdown')
    print('\nYour time is {}.'.format(round(time, 2)))
    print('\nYour score is {} out of {}.'.format(score, (overall_score)))

# Setup incomplete
except NameError:
    print('Setup incomplete')

# Forgot to close the CSV file
except PermissionError:
    print('Close CSV File')

# Motion sensors not on or need to be charged
except AttributeError:
    print('Turn on motion sensors')

# # Dongle wasn't closed properly or open in another program
except serial.SerialException:
    print('Refresh kernal or check dongle connection')

# Client connection needs to refresh
except OSError:
    print('Run again to refresh client connection')

# No matter what, close peripherals
finally:
    if training_mode == 3:
        connection.close()
    window.close()
    utilities.close(dongle)
