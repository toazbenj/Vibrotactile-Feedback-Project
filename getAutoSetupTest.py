# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 14:00:32 2022

@author: Lynn
"""

import csv

def getAutoSetup():
    '''Reads control file, gathers number of rounds and mode for each target sequence'''
    file = 'controlFile2.csv'
    parameters_lst = []
    units_lst = []
    blocks_lst = []
    
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
    
    
    for i in parameters:
        if i != "":
            parameters_lst.append(int(i))
        
    for i in units:
        if i != "":
            units_lst.append(int(i))
       
    for i in blocks:
        if i != "":
            blocks_lst.append(int(i))
    
    return parameters_lst, units_lst, blocks_lst
            

parameters, units, blocks = getAutoSetup()

for i in parameters:
    print(i)

for i in units:
    print(i)

for i in blocks:
    print(i)

# print(training_mode)
# print(student_sensor)
# print(teacher_sensor)

# print()

# print(pretest_units)
# print(training_one_units)
# print(midtest_units)
# print(training_two_units)
# print(posttest_units)

# print()

# print(pretest_blocks)
# print(training_one_blocks)
# print(midtest_blocks)
# print(training_two_blocks)
# print(posttest_blocks)




