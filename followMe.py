# -*- coding: utf-8 -*-
"""
Follow Me Algorthm

    Try
        Begin Writing to data file
        Make haptic dictionaries
        Register haptics
        Register Sensors
        Set time record keeping
        
        Main Loop (60 second time sentinel)
    
            Get teacher and student position data
            Calculate difference
            Display data
            Record data
            Select haptics index
            
            If tolerance exceeded
                Find direction of max difference
                Modulate intensity
                Play haptics
                Sleep
                Record intensity and direction
                
        Close devices
        Close file
        
    Except
        Close devices
        Close file
        Timestamp
        
Created on Thu Nov 18 11:42:07 2021
@author: Ben Toaz
"""

from math import pi
import sensorVestMethods as sv
from time import sleep
from time import perf_counter

# If any errors or crashes, sensors and files will still get closed
try:
    # Open file for recoding data
    file = open('sessionScratchWork.txt','w')
    
    # Dict of file names matched with keystrokes
    haptic_dict = {'a': "MoveLeft", 'd': 'MoveRight', 'w': "MoveForward",
                   's': 'MoveBack', 'q': 'TurnCCW', 'e': 'TurnCW', 'x': "Jump",
                   'wa': 'ForwardLeft','wd': 'ForwardRight','sa': 'BackLeft',
                   'sd': 'BackRight'}
    
    # Numerical representation of direction for records
    angle_dict = {'a': pi, 'd': 2*pi, 'w': pi/2,'s': 3*pi/2}
    
    # Register haptic files
    sv.register(3)
    
    # Register and Tare Sensors
    teacher, student, dong = sv.getDevices()
    teacher.tareWithCurrentOrientation()
    student.tareWithCurrentOrientation()
    
    # Time recording values
    time = 0
    start = perf_counter()
    buzzes = 0
    
    # Main Loop, 1 minute run time
    while time - start < 60:
            
            # Get batch of position data as (x,y,z) tuple, calculate difference
            tec_tup = teacher.getStreamingBatch()
            stu_tup = student.getStreamingBatch()
            diff_tup = (stu_tup[0]-tec_tup[0],stu_tup[1]-tec_tup[1],
                        stu_tup[2]-tec_tup[2])
            
            # Display and Record Data
            print('Position Error {}, {}, {}'.format(
                round(diff_tup[0],3),round(diff_tup[1],3),round(diff_tup[2],3)))
            
            # Timestamp, teacher, student, position error
            file.write('\n'+str(time-start))
            file.write('\n\n{},{},{}'.format(
              round(tec_tup[0],3),round(tec_tup[1],3),round(tec_tup[2],3)))
            file.write('\n{},{},{}'.format(
              round(stu_tup[0],3),round(stu_tup[1],3),round(stu_tup[2],3)))
            file.write('\n{},{},{}'.format(
              round(diff_tup[0],3),round(diff_tup[1],3),round(diff_tup[2],3)))
        
            # Movement Cases
            tolerance = pi/24
            index = ''
            
            # # Mixed Conditions
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
            # Left (-y difference)
            if diff_tup[1] <= -tolerance:
                index = 'a'
                
            # Forward (-z differnce)
            elif diff_tup[2] <= -tolerance:
                index = 'w'
                
            # Right (+y difference)
            elif diff_tup[1] >= tolerance:
                index = 'd'
    
            # Back (+z difference)
            elif diff_tup[2] >= tolerance:
                index = 's'
            
            # Play haptics
            if index in haptic_dict:
                # Decide which axis to check based on bigger difference
                if abs(diff_tup[1]) > abs(diff_tup[2]):
                    check_coord = 1
                elif abs(diff_tup[1]) < abs(diff_tup[2]):
                    check_coord = 2
                
                # Modulate intensity based on assumed max movement angle
                intensity = abs(diff_tup[check_coord])/(pi/4)
                # Can't exceed 1
                if intensity > 1:
                    intensity = 1
                
                sv.play(index=index, intensity=intensity, duration=0.5)
                sleep(1.5)
                buzzes += 1
                
                # Record intensity and direction (angle)
                file.write('\n{},{}'.format(
                    round(intensity,3),round(angle_dict[index],2)))
            
            else:
                # No haptics => Intensity=0, Angle=0
                file.write('\n{},{}'.format(0,0))
            
            # time = perf_counter()+0.1*buzzes
            time = perf_counter()
            
    sv.close([teacher, student, dong])
    file.close()
    
except:
    # Will execute no matter what
    sv.close([teacher, student, dong])
    file.close()
    file.write('\n'+str(time-start))
    
