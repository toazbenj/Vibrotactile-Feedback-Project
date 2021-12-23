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


try:
    bounds = 500
    win = g.GraphWin(width = bounds, height = bounds)
    
    # Register and Tare Sensors
    teacher, student, dong = sv.getDevices()
    
    pt = g.Point(bounds/2, bounds/2)
    
    cir = g.Circle(pt, 25)
    cir.setOutline('blue')
    cir.setFill('blue')
    cir.draw(win)
    
    # Time recording values
    time = 0
    start = perf_counter()
    tolerance = pi/48
    
    # Main Loop, 2 minute run time
    while time < 120:
        
        tec_tup = teacher.getStreamingBatch()
        if tec_tup[1] > tolerance or tec_tup[1] < -tolerance\
            or tec_tup[2] > tolerance or tec_tup[2] < -tolerance:
                
            x = tec_tup[1] / (pi/4) 
            y = tec_tup[2] / (pi/4)
        else:
            x = 0 
            y = 0
        
        print('{}, {}'.format(round(pt.x,3),round(pt.y,3)))
        
        pt.move(-x,-y)
        cir.move(-x,-y)
        
        time = perf_counter()-start
        
        if cir.getCenter().x > bounds or cir.getCenter().y > bounds\
            or cir.getCenter().x < 0 or cir.getCenter().y < 0:
            
            pt.undraw()
            cir.undraw()
            
            pt = g.Point(bounds/2, bounds/2)
            cir = g.Circle(pt, 25)
            cir.setOutline('blue')
            cir.setFill('blue')
            cir.draw(win)
            
    win.close()
    sv.close([teacher, student, dong])
    
except KeyboardInterrupt:
    win.close()
    sv.close([teacher, student, dong])
    
except  NameError:
    # Will execute if setup not completed
    sv.close([dong])
    