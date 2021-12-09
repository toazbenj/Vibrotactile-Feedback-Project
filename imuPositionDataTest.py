# -*- coding: utf-8 -*-
"""
IMU Position Data Test
    
    Search for docked IMUs
    Create sensor object
    Select position data for streaming
    
    Timed Sensing Loop
        Get batch of position data, (x,y,z) tuple
        Display data
    
    Close Sensor => Important


Created on Mon Nov  1 11:11:32 2021
@author: Ben Toaz
"""

import time
import threespace_api as ts_api

# Search for docked IMUs
tspace_port_lists = ts_api.getComPorts()

#Prints a tuple (PORT_NAME, FRIENDLY_NAME, DEV_TYPE)
print(tspace_port_lists[0]) 

# Create sensor object
new_sensor = ts_api.TSWLSensor(com_port=tspace_port_lists[0])

# Select position data for streaming
new_sensor.setStreamingSlots(slot0='getTaredOrientationAsEulerAngles')

# Timed Sensing Loop
start_time = time.clock()
while time.clock() - start_time < 100:
    
    # Get batch of position data, (x,z,y) tuple plus 4th value
    pos_tup = new_sensor.getStreamingBatch()
    
    # Display position vector of x, y, z
    print('<{}, {}, {}>'.format(round(pos_tup[0],3),round(pos_tup[1],3),round(pos_tup[2],3)))
    print("=======================\n")

   
new_sensor.close()