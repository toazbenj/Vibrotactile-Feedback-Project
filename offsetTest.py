# -*- coding: utf-8 -*-
"""
Created on Thu Apr  7 13:08:53 2022

@author: Lynn
"""

import utilitiesMethods as utilities
import graphics
from math import pi
from random import randint

bounds = 600

# position_offset = randint(10,30) * pi/180
position_offset = 0

# Register and Tare Sensors
student, dongle, = utilities.getDevices()

# Make Graphics Window
window = graphics.GraphWin(width=bounds, height=bounds)
window.setBackground('black')

  # Make Ball
point = graphics.Point(bounds/2, bounds/2)
ball = graphics.Circle(point, 25)
ball.setOutline('white')
ball.setFill('white')
ball.draw(window)

try:
     # Movement Loop
    while True:
    
        student_tup = student.getStreamingBatch()
        
        
        # student_tup = (position_offset+student_tup[0], position_offset+student_tup[1],
        #     position_offset+student_tup[2])
        
        student_tup = (student_tup[0], student_tup[2], student_tup[1])
        
        print(str(round(student_tup[0], 3)),
                                str(round(student_tup[1], 3)),
                                str(round(student_tup[2], 3)))
        
        # Move ball
        utilities.positionMove(window, bounds, pi/4, ball, student_tup, student_tup, 1/2,1/2)
finally:
    window.close()
    utilities.close(dongle)