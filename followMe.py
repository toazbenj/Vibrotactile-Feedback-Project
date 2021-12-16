# -*- coding: utf-8 -*-
"""
Follow Me Algorthm

    Try
        Make haptic dictionaries
        Register haptics
        Register Sensors
        Set time record keeping

        Main Loop (60 second time sentinel)

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
    
    # Dict of file names matched with keystrokes
    haptic_dict = {'a': "MoveLeft", 'd': 'MoveRight', 'w': "MoveForward",
                   's': 'MoveBack', 'q': 'TurnCCW', 'e': 'TurnCW', 'x': "Jump",
                   'wa': 'ForwardLeft', 'wd': 'ForwardRight', 'sa': 'BackLeft',
                   'sd': 'BackRight', 'g': 'Gap'}

    # Numerical representation of direction for records
    angle_dict = {'a': pi, 'd': 2*pi, 'w': pi/2, 's': 3*pi/2}

    # Register haptic files
    sv.register(3)

    # Register and Tare Sensors
    teacher, student, dong = sv.getDevices()

    # Time recording values
    time = 0
    start = perf_counter()
    reps = 0
    commandTime = 0
    file ='demo.csv'
    
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

        # Movement Cases
        tolerance = pi/48
        index = ''

        # # Mixed Conditions => Still Need Refinement
        # # fix ForwardLeft and ForwardRight, switched?

        # # Forward Left (-y difference and -z differnce)
        # if diff_tup[1] <= -tolerance and diff_tup[2] <= -tolerance:
        #     index = 'wa'

        # # Forward Right (-z differnce and +y difference)
        # elif diff_tup[2] <= -tolerance and diff_tup[1] >= tolerance:
        #     index = 'wd'

        # # Back Right (+y difference +z difference)
        # elif diff_tup[1] >= tolerance and diff_tup[2] >= tolerance:
        #     index = 'sd'

        # # Back Left (+z difference and -y difference)
        # elif diff_tup[2] >= tolerance and diff_tup[1] <= -tolerance:
        #     index = 'sa'

        # Pure Directions
        # Forward (-z differnce)
        if diff_tup[2] <= -tolerance and abs(diff_tup[1]) < abs(diff_tup[2]):
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

        # Play haptics
        if index in haptic_dict:
            
            # Decide which axis to check based on bigger difference
            if abs(diff_tup[1]) > abs(diff_tup[2]):
                check_coord = 1
            else:
                check_coord = 2

            # Modulate intensity based on assumed max movement angle
            intensity = abs(diff_tup[check_coord])/(pi/8)
            # Can't exceed 1
            if intensity > 1:
                intensity = 1
            
            # Measures time since last buzz => maintains gap
            time  =  perf_counter()-start
            if time - commandTime > 0.5:
                commandTime = perf_counter()-start
                sv.play(index=index, intensity=intensity, duration=0.5)
            angle = angle_dict[index]

        else:
            # No haptics => Intensity=0, Angle=0
            angle = 0 
            intensity = 0
        
        # Display Data
        if reps % 5 == 0:
            print('Error {}, {}, {}'.format(
                round(
                    diff_tup[0], 3), round(diff_tup[1], 3), round(diff_tup[2], 3)))
        
        reps += 1
        time = perf_counter()-start
        sv.writeData(file,time,tec_tup,stu_tup,diff_tup,intensity,angle)

    sv.close([teacher, student, dong])

except KeyboardInterrupt:
    # Will execute if stopped manually
    sv.close([teacher, student, dong])
except  NameError:
    # Will execute if setup not completed
    sv.close([dong])
