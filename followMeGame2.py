# -*- coding: utf-8 -*-
"""
Follow Me Game Visualization

Reference: http://anh.cs.luc.edu/handsonPythonTutorial/graphics.html

Created on Thu Dec 23 08:19:17 2021
@author: Ben Toaz
"""

import graphics as g
import sensorVestMethods as sv
from math import pi
from time import perf_counter
from random import randint

angle_dict = {'a': pi, 'wd': pi/4, 'd': 2*pi, 'wa': 3*pi/4, 'w': pi/2,'sa': 5*pi/4, 
              's': 3*pi/2, 'sd': 7*pi/4}


try:
    x_bounds = 1000 
    y_bounds = 500
    win = g.GraphWin(width = x_bounds, height = y_bounds)
    
    # Register and Tare Sensors
    teacher, student, dong = sv.getDevices()
    
    pt = g.Point(x_bounds/2, y_bounds/2)
    
    ball = g.Circle(pt, 25)
    ball.setOutline('blue')
    ball.setFill('blue')
    ball.draw(win)
    
    # Sentinels/Conditions
    time = 0
    start = perf_counter()
    commandTime = 0
    tolerance = pi/96
    miss_margin = 10
    speed_limit = 15
    score = 0
    index = ''
    
    # Main Loop, 1 minute run time
    while time < 60:
        # Remake Target
        x_coord = x_bounds * randint(2, 9)/10
        y_coord = y_bounds * randint(2, 9)/10
        
        pt = g.Point(x_coord,y_coord)
        target = g.Circle(pt,30)
        target.setOutline('red')
        target.draw(win)        
        
        # Movement Loop
        while True:    
            
            tec_tup = teacher.getStreamingBatch()
            stu_tup = student.getStreamingBatch()
            diff_tup = diff_tup = (stu_tup[0]-tec_tup[0], stu_tup[1]-tec_tup[1],
                    stu_tup[2]-tec_tup[2])
            
            # Select haptics direction, play, return values for writing
            index = sv.getIndex(diff_tup,tolerance)
            # angle, intensity, commandTime = sv.advancedPlay(index, diff_tup,
            #                                                 start, commandTime)
                
            
            if index != '':
        
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
                
                
            if sv.checkTolerance(tec_tup,tolerance) and\
                sv.checkTolerance(stu_tup,tolerance):
                    
                x = (tec_tup[1]+stu_tup[1]) / (2*pi/4) * 10
                y = (tec_tup[2]+stu_tup[2]) / (2*pi/4) * 10                
            else:
                x = 0 
                y = 0
            
            # print('{}, {}'.format(round(pt.x,3),round(pt.y,3)))
            
            # If speed limit exceeded, sets speed to limit in same direction
            if abs(x) > speed_limit:
                x = speed_limit * x/x
            if abs(y) > speed_limit:
                y = speed_limit * y/y
            
            ball.move(-x,-y)
            
            # Respawns ball in center of window if out of bounds
            if ball.getCenter().x > x_bounds or ball.getCenter().y > y_bounds\
                or ball.getCenter().x < 0 or ball.getCenter().y < 0:
                
                pt.undraw()
                ball.undraw()
                
                pt = g.Point(x_bounds/2, y_bounds/2)
                ball = g.Circle(pt, 25)
                ball.setOutline('blue')
                ball.setFill('blue')
                ball.draw(win)
            
            time = perf_counter()-start
            
            # Checks if target is hit
            x_diff = abs( ball.getCenter().x-target.getCenter().x)
            y_diff = abs( ball.getCenter().y-target.getCenter().y)
            
            if x_diff < miss_margin and y_diff < miss_margin:
                target.undraw()
                score += 1
                break
            
    win.close()
    sv.close([teacher, student, dong])
    print('\nYour score is {}.'.format(score))
    
except KeyboardInterrupt:
    # For manual shutdown
    win.close()
    sv.close([teacher, student, dong])
    print('\nYour score is {}.'.format(score))
    
# except NameError:
#     # Will execute if setup not completed
#     sv.close([dong])
#     print('\nYour score is {}.'.format(score))
