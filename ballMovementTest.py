# -*- coding: utf-8 -*-
"""
Ball Movement Test

Created on Tue Mar  1 14:24:14 2022
@author: toazbenj
"""

import graphics
import utilitiesMethods as utilities
from math import pi

# Make Window
x_bounds = 650
y_bounds = 650
window = graphics.GraphWin(width=x_bounds, height=y_bounds)

# Register and Tare Sensors
teacher, student, dongle, = utilities.getDevices()

# Sentinels/Conditions
speed_limit = 15

# Make Ball
point = graphics.Point(x_bounds/2, y_bounds/2)
ball = graphics.Circle(point, 25)
ball.setOutline('blue')
ball.setFill('blue')
ball.draw(window)

# Movement Loop
while True:

    # Get position data
    teacher_tup = teacher.getStreamingBatch()
   
    # Convert sensor angle movement to ball movement
    x_move = teacher_tup[1] / (2*pi/4) * 10
    y_move = teacher_tup[2] / (2*pi/4) * 10

    # print('{},{}'.format(round(x_move,2),round(y_move,2)))

    # If speed limit exceeded, sets speed to limit in same direction
    if abs(x_move) > speed_limit:
        x_move = speed_limit * (x_move/x_move)
    if abs(y_move) > speed_limit:
        y_move = speed_limit * (y_move/y_move)

    # Move ball, record motion within object
    ball.move(-x_move, -y_move)
    ball.x_center += x_move
    ball.y_center += y_move

    # Respawns ball in center of window if out of bounds
    if ball.getCenter().x > x_bounds or ball.getCenter().y > y_bounds\
            or ball.getCenter().x < 0 or ball.getCenter().y < 0:

        point.undraw()
        ball.undraw()

        pt = graphics.Point(x_bounds/2, y_bounds/2)
        ball = graphics.Circle(pt, 25)
        ball.setOutline('blue')
        ball.setFill('blue')
        ball.draw(window)
   