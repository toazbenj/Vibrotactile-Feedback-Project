# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 12:13:53 2022

@author: toazbenj
"""
import graduatedTest as u
# Main
    
isAuto = True
mode = 3

# Get blocks, units and training mode
parameters_lst, units_lst, blocks_lst, round_control_lst = u.getAutoSetup()

# Device setup
training_mode = parameters_lst[0]
teacher_sensor = parameters_lst[1]
student_sensor = parameters_lst[2]
file = parameters_lst[3]

rounds = 0
for index in range(len(units_lst)):
    
    for block in range(blocks_lst[index]):
        for unit in range(units_lst[index]):
            rounds += 1
            print(rounds)
            