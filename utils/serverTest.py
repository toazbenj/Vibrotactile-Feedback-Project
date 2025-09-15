# -*- coding: utf-8 -*-
"""
Created on Mon Feb 14 20:03:41 2022

@author: Lynn
"""

import time
import socket
import sys
import os
 
# Initialize s to socket
s = socket.socket()
 
# Initialize the host
host = socket.gethostname()
 
# Initialize the port
port = 8080
 
# Bind the socket with port and host
s.bind(('', port))
 
print("waiting for connections...")
 
# listening for connections
s.listen()
 
# accepting the incoming connections
conn, addr = s.accept()
 
print(addr, "is connected to server")
 
# take command as input
command = input(str("Enter Command :"))

conn.send(command.encode())
 
print("Command has been sent successfully.")
 
# receive the confirmation
data = conn.recv(1024)
 
if data:
    print("command received and executed successfully.")