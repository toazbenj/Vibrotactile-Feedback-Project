# -*- coding: utf-8 -*-
"""
Ball Movement Test

Created on Tue Mar  1 14:24:14 2022
@author: toazbenj
"""

import graphics
import utilitiesMethods as utilities
from math import pi
from time import sleep
import threespace_api as ts_api

# Make Window
x_bounds = 650
y_bounds = 650
max_movement_angle = pi/4
window = graphics.GraphWin(width=x_bounds, height=y_bounds)

# Register and Tare Sensors
offset = 5

device_list = ts_api.getComPorts()
com_port, friendly_name, device_type = device_list[0]
dng_device = ts_api.TSDongle(com_port=com_port)

device_dict = {1: dng_device[0+offset], 3: dng_device[1+offset],
               4: dng_device[2+offset]}

key = input('Select device (1,3,4)>>')
device1 = device_dict[int(key)]

device1.setStreamingSlots(slot0='getTaredOrientationAsEulerAngles')
device1.tareWithCurrentOrientation()

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
    teacher_tup = device1.getStreamingBatch()
   
    # Convert sensor angle movement to ball movement
    x_pos = teacher_tup[1] / (max_movement_angle) * x_bounds
    y_pos = teacher_tup[2] / (max_movement_angle) * y_bounds

    print('{},{}'.format(round(x_pos,2),round(y_pos,2)))

    # # If speed limit exceeded, sets speed to limit in same direction
    # if abs(x_move) > speed_limit:
    #     x_move = speed_limit * (x_move/x_move)
    # if abs(y_move) > speed_limit:
    #     y_move = speed_limit * (y_move/y_move)

    # Move ball, record motion within object
    # ball.move(-x_move, -y_move)
    
    if x_pos > x_bounds:
        x_pos = x_bounds
        
    if x_pos < -x_bounds:
       x_pos = -x_bounds
       
    if y_pos > y_bounds:
        y_pos = y_bounds
        
    if y_pos < -y_bounds:
       y_pos = -y_bounds
       
    point = graphics.Point(x_pos, y_pos)
    ball = graphics.Circle(point, 25)
    ball.draw(window)
   