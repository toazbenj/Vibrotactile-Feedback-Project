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

            If tolerance exceeded
                Find direction of max difference
                Modulate intensity
                Play haptics with given interval
                Record intensity and direction
            
            Display data at specified interval
            Record data
            
        Close devices

    Except KeyboardInterrupt
        Close devices


Created on Thu Nov 18 11:42:07 2021
@author: Ben Toaz
"""

from math import pi
import sensorVestMethods as sv
from time import perf_counter
import csv

# If stopped, sensors and files will still get closed
try:
    # Register haptic files
    sv.register(3)

    # Register and Tare Sensors
    teacher, student, dong = sv.getDevices()

    # Sentinels and Conditions
    time = 0
    start = perf_counter()
    reps = 0
    commandTime = 0
    tolerance = pi/12
    duration = 0.5
    file ='run2.csv'
    
    header = ['Time','Teacher-x','Teacher-y','Teacher-z','Student-x','Student-y',
              'Student-z','Difference-x','Difference-y','Difference-z','Intensity','Angle']
    
    # Open data file, write header
    with open(file, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(header)
    
    # Main Loop, 2 minute run time
    while time < 120:

        # Get batch of position data as (x,y,z) tuple, calculate difference
        tec_tup = teacher.getStreamingBatch()
        stu_tup = student.getStreamingBatch()
        diff_tup = (stu_tup[0]-tec_tup[0], stu_tup[1]-tec_tup[1],
                    stu_tup[2]-tec_tup[2])

        # Movement selection
        index = sv.getIndex(diff_tup, tolerance)

        # Play haptics, return values for recording
        angle, intensity, commandTime = sv.advancedPlay(index, diff_tup, 
                                                        start, commandTime)
        
        # Display Data
        if reps % 5 == 0:
            print('Error {}, {}, {}'.format(
                round(
                    diff_tup[0], 3), round(diff_tup[1], 3), round(
                        diff_tup[2], 3)))
        
        reps += 1
        time = perf_counter()-start
        sv.writeData(file,time,tec_tup,stu_tup,diff_tup,intensity,angle)

    sv.close([teacher, student, dong])

except KeyboardInterrupt:
    # Will execute if stopped manually
    sv.close([teacher, student, dong])
    print('All closed out.')
    
except NameError:
    # Will execute if setup not completed
    sv.close([dong])
    print('Dongle closed out.')
    