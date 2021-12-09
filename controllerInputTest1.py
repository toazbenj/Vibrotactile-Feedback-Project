# -*- coding: utf-8 -*-
"""
Controller Input Test 1
From Stack Overflow

Created on Mon Oct 18 11:23:17 2021

@author: Lynn
"""

import pygame
pygame.init()
joysticks = []
clock = pygame.time.Clock()
keepPlaying = True

# for al the connected joysticks
for i in range(0, pygame.joystick.get_count()):
    # create an Joystick object in our list
    joysticks.append(pygame.joystick.Joystick(i))
    # initialize them all (-1 means loop forever)
    joysticks[-1].init()
    # print a statement telling what the name of the controller is
    print ("Detected joystick "),joysticks[-1].get_name(),"'"
while keepPlaying:
    clock.tick(60)
    for event in pygame.event.get():
        # The 0 button is the 'a' button, 1 is the 'b' button, 2 is the 'x' button, 3 is the 'y' button
        if event.button == 0:
            print ("A Has Been Pressed")