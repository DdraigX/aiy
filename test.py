#!/usr/bin/env python3
#coding=utf-8  

import pygame
import time

pygame.mixer.init()
pygame.init()

pygame.mixer.music.load('output.mp3')
pygame.mixer.music.play()
pygame.event.wait()



#from pygame import mixer
#pygame.mixer.init()
#pygame.init()





#pygame.mixer.music.load('output.mp3')

#sound = mixer.Sound('/home/pi/AIY-projects-python/src/examples/voice/output.mp3')
#print("length",sound.get_length())

#pygame.mixer.music.play()

#sound = mixer.Sound('/home/pi/AIY-projects-python/src/examples/voice/output.mp3');
#sound = mixer.music.load('output.mp3')
#sound.music.play(0)
#time.sleep(20)
