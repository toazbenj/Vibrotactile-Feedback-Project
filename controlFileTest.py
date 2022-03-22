# -*- coding: utf-8 -*-
"""
Created on Thu Mar 17 14:33:16 2022

@author: Lynn
"""

import csv

def getRounds():

    file = 'controlFile.csv'
    # Open data file, write header
    with open(file, 'r', newline='') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)
        row = next(csvreader)
            
    pretest_rounds = row[0]
    training_rounds = row[1]
    posttest_rounds = row[2]
    training_type = row[3]
    
    return pretest_rounds, training_rounds, posttest_rounds, training_type

pretest_rounds, training_rounds, posttest_rounds, training_type = getRounds()

print(pretest_rounds)
print(training_rounds)
print(posttest_rounds)
print(training_type)
