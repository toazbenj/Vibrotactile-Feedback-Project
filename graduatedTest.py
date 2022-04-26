# -*- coding: utf-8 -*-
"""
Created on Thu Apr 21 14:34:52 2022

@author: toazbenj
"""
import csv
import utilitiesMethods as utilities


def getControl(rounds, round_lst, round_control_lst, units_lst, blocks_lst):
    """ Generate dictionary of student control values for training"""
    isGraduated = round_control_lst[0]
    # Increased control for student after each unit (target sequence)
    if isGraduated:
        # Training 1 number of units in a block
        if rounds < sum(round_lst[0:2]):
            units = round_lst[1]/blocks_lst[1]
        
        # Training 2
        else:
            units = round_lst[3]/blocks_lst[3]
            
        start  = int(10 * round_control_lst[1])
        stop = int(10 * round_control_lst[2])
        interval = int((stop-start)/(units-1))
        stop += 1
        
        count = 0
        round_control_dict = {}
        for i in range(start, stop, interval):
            round_control_dict[count] = i/10
            count += 1
            
    # Increased student control after each block
    else:
        # Training 1 blocks
        if rounds < sum(round_lst[0:2]):
            units = blocks_lst[1]
        
        # Training 2
        else:
            units = blocks_lst[3]
            
        start = int(100 * round_control_lst[1])
        stop = int(100 * round_control_lst[2])
        interval = int((stop-start)/(units-1))
        stop += 1
        
        count = 0
        round_control_dict = {}
        for i in range(start, stop, interval):
            round_control_dict[count] = i/100
            count += 1
        
        # print(round_control_dict)
    return round_control_dict


def getSharing(round_control_dict, isTest, round_lst, round_control_lst, units_lst, blocks_lst, 
               block, index, mode=1, rounds=0, isAuto=True):
    
    """
    Receive/calculate the amount of cursor control and intensity for
    student/teacher
    """
    
    round_control_dict = getControl(rounds, round_lst, round_control_lst, units_lst, blocks_lst)
    
    # No Teacher, No Haptics
    if mode == 1 or isTest:
        teacher_control = 0
        student_control = 1
        teacher_intensity = 0
        student_intensity = 0
            
    # Teacher
    else:
        # Control changes for each training round
        if isGraduated:
            # Training 1
            if index < 2:
                student_control = round_control_dict[
                    rounds-round_lst[0]-block*units_lst[1]]
            # Training 2
            else:
                student_control = round_control_dict[
                    rounds-sum(round_lst[0:3])-block*units_lst[3]]
    
            teacher_control = 1-student_control
        
        # Control changes for each training block
        else:
            # Training 1
            if index < 2:
                student_control = round_control_dict[block]
            # Training 2
            else:
                student_control = round_control_dict[block]
    
            teacher_control = 1-student_control
            
        # No haptics
        if mode == 2:
            student_intensity = 0
            teacher_intensity = 0
        # Haptics
        else:
            # Amount of intensity is inverse of amount of control
            student_intensity = teacher_control
            teacher_intensity = student_control
  
    return teacher_control, student_control, teacher_intensity, \
        student_intensity
        
        
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
        


# Main
isAuto = True

# Get blocks, units and training mode
parameters_lst, units_lst, blocks_lst, round_control_lst = getAutoSetup()
isGraduated = round_control_lst[0]

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


rounds = 0
for index in range(len(units_lst)):
    print()
    
    for block in range(blocks_lst[index]):
        print()
        # round_control_dict = getControl(rounds, round_lst, round_control_lst, units_lst, blocks_lst)

        if not isGraduated:
            isTest = utilities.getRoundType(rounds, round_lst)
            teacher_control, student_control, teacher_intensity, student_intensity\
                = getSharing(rounds, isTest, round_lst, round_control_lst, units_lst,
                             blocks_lst, block, index, training_mode, rounds, isAuto)
        
        for unit in range(units_lst[index]):
            isTest = utilities.getRoundType(rounds, round_lst)        
            
            if isGraduated:
                teacher_control, student_control, teacher_intensity, student_intensity\
                    = getSharing(rounds, isTest, round_lst, round_control_lst, units_lst,
                                 blocks_lst, block, index, training_mode, rounds, isAuto)
            
            print(student_control)
            rounds += 1
            