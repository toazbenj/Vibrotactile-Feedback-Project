# -*- coding: utf-8 -*-
"""
Wireless Position Data Test

Created on Mon Nov 15 11:27:53 2021
@author: Ben Toaz
"""


import time
import sensorVestMethods as sv

# Register Sensors
sensor1, sensor2, dong = sv.getTwoDevices()

# Timed Sensing Loop
start_time = time.process_time()
while time.process_time() - start_time < 100:
    
    # Get batch of position data, (x,z,y) tuple plus 4th value
    pos_tup1 = sensor1.getStreamingBatch()
    pos_tup2 = sensor2.getStreamingBatch()
    
    # Display position vector of x, y, z
    print('Sensor 1: <{}, {}, {}>'.format(round(pos_tup1[0],3),round(pos_tup1[1],3),round(pos_tup1[2],3)))
    print('Sensor 2: <{}, {}, {}>'.format(round(pos_tup2[0],3),round(pos_tup2[1],3),round(pos_tup2[2],3)))
    #print('Time: {}'.format(time.process_time()-start_time))
    print("=======================\n")
    
    if sv.testPos(pos_tup1,pos_tup2,0.3):
        print('Position Found')
        break
    
sv.close(sensor1, sensor2, dong)

