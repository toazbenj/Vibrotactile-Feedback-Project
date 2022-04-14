# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 15:04:31 2022

@author: Lynn
"""
import utilitiesMethods as utilities

# Get blocks, units and training mode
parameters_lst, units_lst, blocks_lst= utilities.getAutoSetup()
 
# Number of round units times number of blocks is number of times through 
# each sequence
pretest_rounds = units_lst[0] * blocks_lst[0]
training_one_rounds = units_lst[1] * blocks_lst[1]
midtest_rounds = units_lst[2] * blocks_lst[2]
training_two_rounds = units_lst[3] * blocks_lst[3]
posttest_rounds = units_lst[4] * blocks_lst[4]

round_lst = [pretest_rounds, training_one_rounds, midtest_rounds, 
         training_two_rounds, posttest_rounds]

pause_sentinel_lst = [sum(round_lst[0:1])-1, sum(round_lst[0:2])-1, sum(round_lst[0:3])-1, 
         sum(round_lst[0:4])-1, sum(round_lst[0:5])-1]

for rounds in range(sum(round_lst)):
    isTest = utilities.getRoundType(rounds, round_lst)
    
    print(rounds, isTest)
    
    if rounds in pause_sentinel_lst:
        print('pause')
    
    print()
    
# 2p, 7p
# 24p, 104p, 128p, 208p, 232p 