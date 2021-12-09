# -*- coding: utf-8 -*-
"""
Range Finder Test

    Make haptic dictionary
    Set movement threshold values
    Register haptics
    Register Sensors
    
    Main Loop 
        Teacher Loop
            Get teacher position data
            Display Data
            Check ambiguous cases
                Break
            Check satisfied cases
                Set index
            Set haptic qualities
            Student Loop
                Play haptics
                Check student position
                    Break
                Sleep
                
    Close devices

Created on Thu Nov 18 11:42:07 2021
@author: Ben Toaz
"""

from time import perf_counter
from math import pi
import sensorVestMethods as sv
from time import sleep

# Open file for recoding data
file = open('sessionScratchWork.txt','w')

# Dict of file names matched with keystrokes
haptic_dict = {'a': "MoveLeft", 'd': 'MoveRight', 'w': "MoveForward",'s': 'MoveBack'}

# Threshold radian values for each movement in order
left_y_thresh = pi/10
right_y_thresh = -pi/10
forward_z_thresh = pi/10
backward_z_thresh = -pi/12

# Register haptic files
sv.register(3, haptic_dict)

# Register Sensors
sensor1, sensor2, dong = sv.getDevices()

# Main Loop
while True:
        
        # Teacher Loop
        print('\nTeacher, make your move.')
        while True:
  
            # Get batch of position data as (x,y,z) tuple
            pos_tup1 = sensor1.getStreamingBatch()
            
            # Display position vector of x, z, y
            print('Sensor 1: <{}, {}, {}>'.format(
                round(pos_tup1[0],3),round(pos_tup1[1],3),round(pos_tup1[2],3)))
            
            file.write('\n1: <{}, {}, {}>'.format(
                round(pos_tup1[0],3),round(pos_tup1[1],3),round(pos_tup1[2],3)))
            
            index = ''
            # Satisfied Cases
            if pos_tup1[1] >= left_y_thresh:
                index = 'a'
                file.write('\n')
            elif pos_tup1[2] >= forward_z_thresh:
                index = 'w'
                file.write('\n')
            elif pos_tup1[1] <= right_y_thresh:
                index = 'd'
                file.write('\n')
            elif pos_tup1[2] <= backward_z_thresh:
                index = 's'
                file.write('\n')
            else:
                break
            
            # Record number of feedback hits
            buzz_num = 0
            file.write('\n')
            
            # Student Loop
            while True:
                buzz_num += 1
                file.write('\n'+haptic_dict[index])
                
                print('\nStudent, make your move.')
                # Record start time
                start = perf_counter()
                
                pos_tup2 = sensor2.getStreamingBatch()
                print('Sensor 2: <{}, {}, {}>'.format(
                    round(pos_tup2[0],3),round(pos_tup2[1],3),round(pos_tup2[2],3)))
                
                file.write('\n2: <{}, {}, {}>'.format(
                    round(pos_tup2[0],3),round(pos_tup2[1],3),round(pos_tup2[2],3)))
                
                sv.play(index=index, duration=0.5)
                
                if pos_tup2[1] >= left_y_thresh and index == 'a':
                    
                    print('\nMovement complete.')
                    # Calculate response time
                    end = perf_counter()
                    # Add sleep time => not measured by clock
                    elapsed = end-start+buzz_num*1.5
                    print('Time: '+ str(round(elapsed,3)))
                    file.write('\nTime: '+ str(round(elapsed,3)))
                    break
                
                elif pos_tup2[2] >= forward_z_thresh and index == 'w':
                   
                    print('\nMovement complete.')
                    # Calculate response time
                    end = perf_counter()
                    # Add sleep time => not measured by clock
                    elapsed = end-start+buzz_num*1.5
                    print('Time: '+ str(round(elapsed,3)))
                    file.write('\nTime: '+ str(round(elapsed,3)))
                    break
                
                elif pos_tup2[1] <= right_y_thresh  and index == 'd':
                   
                    print('\nMovement complete.')
                    # Calculate response time
                    end = perf_counter()
                    # Add sleep time => not measured by clock
                    elapsed = end-start+buzz_num*1.5
                    print('Time: '+ str(round(elapsed,3)))
                    file.write('\nTime: '+ str(round(elapsed,3)))
                    break
                
                elif pos_tup2[2] <= backward_z_thresh and index == 's':
                    
                    print('\nMovement complete.')
                    # Calculate response time
                    end = perf_counter()
                    # Add sleep time => not measured by clock
                    elapsed = end-start+buzz_num*1.5
                    print('Time: '+ str(round(elapsed,3)))
                    file.write('\nTime: '+ str(round(elapsed,3)))
                    break
                
                # Gap between haptic hits
                sleep(1.5)
                file.write('\n')

device_lst = sensor1, sensor2, dong
sv.close(device_lst)

