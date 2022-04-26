# -*- coding: utf-8 -*-
"""
Created on Tue Apr 26 11:11:35 2022

@author: toazbenj
"""
import csv
import utilitiesMethods as utilities

def getAutoSetup():
    '''Reads control file, gathers number of rounds and mode for each target sequence'''
    file = 'controlFile2.csv'
    parameters_lst = []
    units_lst = []
    blocks_lst = []
    round_control_lst = []
    
    # Open data file, write header
    with open(file, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        
        # 1st line of parameters, skip header lines
        next(csvreader)
        next(csvreader)
        parameters = next(csvreader)
        
        # 2nd line of units
        next(csvreader)
        next(csvreader)
        next(csvreader)
        units = next(csvreader)
        
        # 3rd line of blocks
        next(csvreader)
        next(csvreader)
        next(csvreader)
        blocks = next(csvreader)
        
        # 4th line of Training Round Control Values
        next(csvreader)
        next(csvreader)
        next(csvreader)
        controls = next(csvreader)
    
    for i in parameters:
        if i != "":
            try:
                parameters_lst.append(int(i))
            except ValueError:
                parameters_lst.append(i)
        
    for i in units:
        if i != "":
            units_lst.append(int(i))
       
    for i in blocks:
        if i != "":
            blocks_lst.append(int(i))
            
    for i in controls:
        if i != "":
            round_control_lst.append(float(i))
    
    return parameters_lst, units_lst, blocks_lst, round_control_lst


def getControl(round_lst, round_control_lst, units_lst, blocks_lst, rounds, mode=1):
    
    """
    Receive/calculate the amount of cursor control and intensity for
    student/teacher
    """
        
    isGraduated = round_control_lst[0]
    
    # Increased control for student after each unit (target sequence)
    if isGraduated:
        # Training 1 number of units in a block
        if rounds < sum(round_lst[0:1]):
            units = round_lst[1]/blocks_lst[1]
        
        # Training 2
        else:
            units = round_lst[3]/blocks_lst[3]
            
        start  = int(10 * round_control_lst[1])
        stop = int(10 * round_control_lst[2])
        interval = int((stop-start)/(units-1))
        stop += interval
        
        training_control_lst = []
        for i in range(start, stop, interval):
            training_control_lst.append(i/10)
            
    # Increased student control after each block
    else:
        # Training 1 blocks
        if rounds < round_lst[0:1]:
            units = blocks_lst[1]
        
        # Training 2
        else:
            units = blocks_lst[3]
            
        start = round_control_lst[1]
        stop = round_control_lst[2]
        interval = (stop-start)/(units-1)
        stop += interval
        
        training_control_lst = []
        for i in range(float(start), float(stop), float(interval)):
            training_control_lst.append(i/100)

    return training_control_lst


def getSharing(isTest, round_lst, training_control_lst, units_lst, blocks_lst, mode=1, rounds=0):
    
    """
    Receive/calculate the amount of cursor control and intensity for
    student/teacher
    """
    
    # Increasing amount of student control for each round, must be 5 rounds
    # round_control_dict = {0:0.1, 1:0.25, 2:0.50, 3:0.75, 4:0.90}
    
    isGraduated = round_control_lst[0]
    
        
    # No Teacher, No Haptics
    if mode == 1 or isTest:
        teacher_control = 0
        student_control = 1
        teacher_intensity = 0
        student_intensity = 0

    # Teacher, No Haptics
    elif not isTest and mode == 2:
            
        if isGraduated:
            student_control = training_control_lst.pop(0)
        else:
            student_control = block_control                    
        
        teacher_control = 1-student_control

        # No haptics
        student_intensity = 0
        teacher_intensity = 0
                
    #  Teacher, Haptics
    elif not isTest and mode == 3:

        if isGraduated:
            student_control = training_control_lst.pop(0)
        else:
            student_control = block_control  
            
        teacher_control = 1-student_control

        # Amount of intensity is inverse of amount of control
        student_intensity = teacher_control
        teacher_intensity = student_control

    return teacher_control, student_control, teacher_intensity, \
        student_intensity, training_control_lst

# Main
    
isAuto = True
mode = 3

# Get blocks, units and training mode
parameters_lst, units_lst, blocks_lst, round_control_lst = getAutoSetup()

# Device setup
training_mode = parameters_lst[0]
teacher_sensor = parameters_lst[1]
student_sensor = parameters_lst[2]
file = parameters_lst[3]

# Calculate number of each type of rounds
pretest_rounds = units_lst[0] * blocks_lst[0]
training_one_rounds = units_lst[1] * blocks_lst[1]
midtest_rounds = units_lst[2] * blocks_lst[2]
training_two_rounds = units_lst[3] * blocks_lst[3]
posttest_rounds = units_lst[4] * blocks_lst[4]

round_lst = [pretest_rounds, training_one_rounds, midtest_rounds, 
             training_two_rounds, posttest_rounds]


for rounds in range(sum(round_lst)):
    isTest = utilities.getRoundType(rounds, round_lst)        


    if isTest:
        training_control_lst = []
    else:
        training_control_lst, block_control = getControl(round_lst, round_control_lst, units_lst, blocks_lst, rounds, mode=1)
        print(training_control_lst)
     
    teacher_control, student_control, teacher_intensity, student_intensity, training_control_lst\
    = getSharing(isTest, round_lst, training_control_lst, units_lst, blocks_lst, mode, rounds, isAuto)

   

    print(rounds)