# -*- coding: utf-8 -*-
"""
Tandem Control Game

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
                Speed limit
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
        
Reference: http://anh.cs.luc.edu/handsonPythonTutorial/graphics.html

Created on Thu Dec 23 08:19:17 2021
@author: Ben Toaz
"""

import graphics
import utilitiesMethods as utilities
from math import pi
from time import perf_counter
from random import randint
import csv
from math import sin
from math import cos
import socket

theta_lst = [0, pi/4, pi/2, 3*pi/4, pi, 5*pi/4, 3*pi/2, 7*pi/4]
rand_lst = []

try:
    # Link to 2nd computer
    socket = socket.socket()
    port = 8080

    socket.bind(('', port))
    print("waiting for connections...")
    socket.listen()
    connection, address = socket.accept()
    print(address, "is connected to server")

    # Make Window
    x_bounds = 650
    y_bounds = 650
    window = graphics.GraphWin(width=x_bounds, height=y_bounds)

    # Register haptic files
    iteration = 4
    utilities.register(iteration)

    percent_teacher, percent_student = utilities.getPercent()

    # Register and Tare Sensors
    teacher, student, dongle, = utilities.getDevices()

    # Sentinels/Conditions
    time = 0
    start = perf_counter()
    commandTime = 0
    tolerance = pi/48
    miss_margin = 10
    speed_limit = 15
    score = 0
    radius = 3/10*x_bounds
    index = ''
    file = 'gameDemo.csv'

    header = ['Time', 'Teacher-x', 'Teacher-y', 'Teacher-z', 'Student-x',
              'Student-y', 'Student-z', 'Difference-x', 'Difference-y',
              'Difference-z', 'Intensity', 'Angle Teacher', 'Angle Student',
              'Ball-x', 'Ball-y', 'Target-x', 'Target-y', 'Score']

    # Open data file, write header
    with open(file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(header)

    # Generates random list of rotation angles
    for i in theta_lst:
        position = randint(0, 8)
        try:
            move = rand_lst[position]
            rand_lst[position] = i
            rand_lst.append(move)
        except IndexError:
            rand_lst.append(i)

    # Main Loop, generates 8 targets from rotation angles
    for i in rand_lst:
        # Make target
        x_coord = x_bounds * (1/2) + radius * (cos(i))
        y_coord = x_bounds * (1/2) + radius * (sin(i))

        point = graphics.Point(x_coord, y_coord)
        target = graphics.Circle(point, 30)
        target.setOutline('red')
        target.draw(window)

        # Make Ball
        point = graphics.Point(x_bounds/2, y_bounds/2)
        ball = graphics.Circle(point, 25)
        ball.setOutline('blue')
        ball.setFill('blue')
        ball.draw(window)

        # Movement Loop
        while True:

            # Get position data
            teacher_tup = teacher.getStreamingBatch()
            student_tup = student.getStreamingBatch()
            difference_tup = difference_tup = (student_tup[0]-teacher_tup[0],
                                               student_tup[1]-teacher_tup[1],
                                               student_tup[2]-teacher_tup[2])

            # Select haptics direction
            index = utilities.getIndex(difference_tup, tolerance)

            # Play haptics, return values for recording
            angle, intensity, commandTime = utilities.advancedPlay(
                index, difference_tup, start, commandTime, iteration, connection)

            # Convert sensor angle movement to ball movement
            if utilities.checkTolerance(teacher_tup, tolerance) or\
                    utilities.checkTolerance(student_tup, tolerance):
                
                # Scaling factors subjective for moderate difficulty
                x_move = (percent_teacher*teacher_tup[1]+percent_student
                          * student_tup[1]) / (2*pi/4) * 10
                
                y_move = (percent_teacher*teacher_tup[2]+percent_student
                          * student_tup[2]) / (2*pi/4) * 10

                # print('{},{}'.format(round(x_move,2),round(y_move,2)))
                
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
            if ball.getCenter().x > x_bounds or ball.getCenter().y > y_bounds\
                    or ball.getCenter().x < 0 or ball.getCenter().y < 0:

                point.undraw()
                ball.undraw()

                pt = graphics.Point(x_bounds/2, y_bounds/2)
                ball = graphics.Circle(pt, 25)
                ball.setOutline('blue')
                ball.setFill('blue')
                ball.draw(window)

            # Checks if target is hit
            x_diff = abs(ball.getCenter().x-target.getCenter().x)
            y_diff = abs(ball.getCenter().y-target.getCenter().y)

            if x_diff < miss_margin and y_diff < miss_margin:
                target.undraw()
                score += 1
                ball.undraw()
                break

            time = perf_counter()-start
            utilities.writeData(file, time, teacher_tup, student_tup,
                                difference_tup, intensity, angle, score, ball,
                                target, 2)
            
    connection.close()
    window.close()
    utilities.close(dongle)
    print('\nYour time is {}.'.format(round(time, 2)))
    
except KeyboardInterrupt:
    # For manual shutdown
    connection.close()
    window.close()
    utilities.close(dongle)
    print('Manual shutdown')
    print('\nYour time is {}.'.format(round(time, 2)))
        
except NameError:
    # Will execute if setup not completed
    connection.close()
    window.close()
    utilities.close(dongle)
    print('Setup incomplete')
    
except PermissionError:
    # Forgot to close the CSV
    connection.close()
    window.close()
    utilities.close(dongle)
    print('Close CSV')
