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
    tolerance = pi/96
    miss_margin = 5
    speed_limit = 15
    score = 0 
    
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
            if tec_tup[1] > tolerance or tec_tup[1] < -tolerance\
                or tec_tup[2] > tolerance or tec_tup[2] < -tolerance:
                    
                x = tec_tup[1] / (pi/4) * 10
                y = tec_tup[2] / (pi/4) * 10
            else:
                x = 0 
                y = 0
            
            # print('{}, {}'.format(round(pt.x,3),round(pt.y,3)))
            
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
    # For manual shutdownf
    win.close()
    sv.close([teacher, student, dong])
    print('\nYour score is {}.'.format(score))
    
except NameError:
    # Will execute if setup not completed
    sv.close([dong])
    print('\nYour score is {}.'.format(score))
