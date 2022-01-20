# -*- coding: utf-8 -*-
"""
Follow Me Algorthm

    Try
        Make haptic dictionaries
        Register haptics
        Register Sensors
        Set time record keeping

        Main Loop (time sentinel)

            Get teacher and student position data
            Calculate difference
            Select haptics index
            Play haptics, return values for recording
            Display data at specified interval
            Record data

        Close devices

    Except KeyboadInterrupt
        Try
            Close sensors
        Except NameError
            Close dongle

Created on Thu Nov 18 11:42:07 2021
@author: Ben Toaz
"""

from math import pi
import utilitiesMethods as utilities
from time import perf_counter
import csv

# If stopped, sensors and files will still get closed
try:
    # Register haptic files
    iteration = 4
    utilities.register(iteration)

    # Register and Tare Sensors
    teacher, student, dongle = utilities.getDevices()

    # Sentinels and Conditions
    time = 0
    start = perf_counter()
    reps = 0
    commandTime = 0
    tolerance = pi/12
    file = 'run2.csv'

    header = ['Time', 'Teacher-x', 'Teacher-y', 'Teacher-z', 'Student-x',
              'Student-y', 'Student-z', 'Difference-x', 'Difference-y',
              'Difference-z', 'Intensity', 'Angle']

    # Open data file, write header
    with open(file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(header)

    # Main Loop, 2 minute run time
    while time < 120:

        # Get batch of position data as (x,y,z) tuple, calculate difference
        teacher_tup = teacher.getStreamingBatch()
        student_tup = student.getStreamingBatch()
        difference_tup = (student_tup[0]-teacher_tup[0],
                          student_tup[1]-teacher_tup[1],
                          student_tup[2]-teacher_tup[2])

        # Movement selection
        index = utilities.getIndex(difference_tup, tolerance)

        # Play haptics, return values for recording
        angle, intensity, commandTime = utilities.advancedPlay(
            index, difference_tup, start, commandTime, iteration)

        # Display Data
        if reps % 5 == 0:
            print('Error {}, {}, {}'.format(
                round(
                    difference_tup[0], 3), round(difference_tup[1], 3), round(
                        difference_tup[2], 3)))

        reps += 1
        time = perf_counter()-start
        utilities.writeData(file, time, teacher_tup, student_tup,
                            difference_tup, intensity, angle, 0, 1)

    utilities.close([teacher, student, dongle])

except KeyboardInterrupt:
    # For manual shutdown
    try:
        utilities.close([teacher, student, dongle])

    except NameError:
        # Will execute if setup not completed
        utilities.close([dongle])
