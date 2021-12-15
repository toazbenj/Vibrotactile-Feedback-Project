# -*- coding: utf-8 -*-
"""
Follow Me Threaded

Created on Wed Dec 15 11:56:30 2021
@author: Ben Toaz
"""

from math import pi
import sensorVestMethods as sv
from time import sleep
from time import perf_counter
import csv
import threading

# If stopped, sensors and files will still get closed
try:
    
    def data(reps,file,time,intensity,angle):
        # Get batch of position data as (x,y,z) tuple, calculate difference
        tec_tup = teacher.getStreamingBatch()
        stu_tup = student.getStreamingBatch()
        diff_tup = (stu_tup[0]-tec_tup[0], stu_tup[1]-tec_tup[1],
                    stu_tup[2]-tec_tup[2])
        
        # Display Data
        if reps % 5 == 0:
            print('Position Error {}, {}, {}'.format(
                round(
                    diff_tup[0], 3), round(diff_tup[1], 3), round(diff_tup[2], 3)))

        sv.writeData(file,time,tec_tup,stu_tup,diff_tup,intensity,angle)
         
    def haptics(diff_tup):
        # Movement Cases
        tolerance = pi/24
        index = ''

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
            angle = angle_dict[index]
            sleep(bedtime)

        else:
            # No haptics => Intensity=0, Angle=0
            angle = 0 
            intensity = 0
    
    if __name__ == "__main__":
        
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
        buzzes = 0
        bedtime = 1.5
        reps = 0
        
        file ='csvTest.csv'
        header = ['Time','Teacher-x','Teacher-y','Teacher-z','Student-x','Student-y',
          'Student-z','Difference-x','Difference-y','Difference-z','Intensity','Angle']

        with open(file, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(header)
            

        while time < 120:
            data = threading.Thread(target=data, args=(
                reps,file,time,intensity,angle,))
            haptics = threading.Thread(target=haptics, args=(diff_tup,))
          
            # starting thread 1
            data.start()
            # starting thread 2
            haptics.start()
          
            # wait until thread 1 is completely executed
            data.join()
            # wait until thread 2 is completely executed
            haptics.join()
            
            reps += 1
            time = perf_counter()-start

    sv.close([teacher, student, dong])

except KeyboardInterrupt:
    # Will execute if stopped manually
    sv.close([teacher, student, dong])
