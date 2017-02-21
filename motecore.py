# -*- coding: utf-8 -*-
"""
Created on Thu Aug 11 21:38:29 2016

@author: jtc9242
"""

import time
import numpy as np
from colorsys import hsv_to_rgb

from mote import Mote

mote = Mote()

mote.configure_channel(1, 16, False)
mote.configure_channel(2, 16, False)
mote.configure_channel(3, 16, False)
mote.configure_channel(4, 16, False)

tst=1/30.0

###CORE FUNCTIONS###

def setPixid(ch,n,rgb):
    if ch==0:
        if n <=15:
            mote.set_pixel(1, n, rgb[0], rgb[1], rgb[2])
        elif n <=31:
            mote.set_pixel(2, n-16, rgb[0], rgb[1], rgb[2])
        else:
            print "Pixel must be between 0 and 31"
    elif ch==1:
        if n <=15:
            mote.set_pixel(3, n, rgb[0], rgb[1], rgb[2])
        elif n <=31:
            mote.set_pixel(4, n-16, rgb[0], rgb[1], rgb[2])
        else:
            print "Pixel must be between 0 and 31"
    else:
        print "Channel must be 0 or 1"
    mote.show()

def setChannel(ch, rgb):
    for pixel in range(16):
        mote.set_pixel(ch, pixel, rgb[0], rgb[1], rgb[2])
    mote.show()
    
def setAll(rgb):
    for channel in range(4):
        setChannel(channel + 1, rgb)

def clearAll():
    mote.clear()
    mote.show()

clearAll()



###MATH FUNCTIONS###
def gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))
    


###MODE FUNCTIONS###

def rainbow(speed=1, sync=False, mode=1):
    h = time.time() * 50 * speed
    if sync==False:
        for channel in range(4):
            for pixel in range(16):
                hue = (h + (channel * 64) + (pixel * 4)) % 360
                r, g, b = [int(c * 255) for c in hsv_to_rgb(hue/360.0, 1.0, 1.0)]
                
                if mode==1: #If in back-of-monitor mode
                    if channel==2 or channel==3: #If top right or right sticks
                        pixel=15-pixel #Flip pixels due to bar orientation
                        
                mote.set_pixel(channel + 1, pixel, r, g, b)
    else:
        for channel in range(2):
            for pixel in range(16):
                hue = (h + (channel * 64) + (pixel * 4)) % 360
                r, g, b = [int(c * 255) for c in hsv_to_rgb(hue/360.0, 1.0, 1.0)]
                mote.set_pixel(channel + 1, pixel, r, g, b)
                mote.set_pixel(channel + 3, pixel, r, g, b)
    mote.show()
    time.sleep(0.03)


def pulseShot(rgb, targetrgb=0, base=0.5, speed=1, phase=120, sync=True, mode=1):
    t_init=time.time()
    h = (time.time()-t_init) * 50 * speed + 360
    delta=[0,0,0]
    rgb0=rgb #Record initial RGB
    if targetrgb: #If colour should change during pulse
        delta=np.subtract(targetrgb,rgb) #Calculate change over the course of one pulse
        
    if sync==True: #If top and bottom and synchronised
        channels=range(2)
    else:
        channels=range(4)
    
    while h<720: #Stop pulse after 1 cycle
    
        if targetrgb: #If colour should change during pulse
            t=(h % 360)/360 #Calculate a scale from time throughout pulse
            rgb=[int(rgb0[i] + (t*delta[i])) for i in range(3)] #Replace rgb with new values based on fade
            
        for channel in channels: #For used channels
            for pixel in range(16): #For all pixels in one channel
                theta = (h + (channel * 64) + (pixel * 4) + phase) % 360 #Calculate angle
                scale = hsv_to_rgb(theta/360.0, 1.0, 1.0)[0] * (1.0-base) #Calculate brightness based on angle and base value
                r,g,b=[int(col*scale +col*base) for col in rgb] #Calculate rgb values for pixel
				
                if mode==1: #If in back-of-monitor mode
                    if channel==2 or channel==3: #If top right or right sticks
                        pixel=15-pixel #Flip pixels due to bar orientation
                
                mote.set_pixel(channel + 1, pixel, r, g, b) #Set pixel on bottom
                if sync==True:
                    mote.set_pixel(channel + 3, pixel, r, g, b) #Set pixel on top
                
        mote.show() #Draw
        time.sleep(0.03) #Rest
        h = (time.time()-t_init) * 50 * speed +360 #Calculate h based on new time


##UNUSED

def warning(rgb, base=0.2, speed=1):
    h = time.time() * 200 * speed
    theta = h % 360
    scale = (1.0-base)*(360-theta)/360.0
    for channel in range(4):
        for pixel in range(16):
            r,g,b=[int(col*scale +col*base) for col in rgb]
            mote.set_pixel(channel + 1, pixel, r, g, b)
    mote.show()
    time.sleep(0.03)


def pulse(rgb, base=0.5, speed=1, sync=False):
    h = time.time() * 50 * speed
    if sync==False:
        for channel in range(4):
            for pixel in range(16):
                theta = (h + (channel * 64) + (pixel * 4)) % 360
                scale = hsv_to_rgb(theta/360.0, 1.0, 1.0)[0] * (1.0-base)
                r,g,b=[int(col*scale +col*base) for col in rgb]
                mote.set_pixel(channel + 1, pixel, r, g, b)
    else:
        for channel in range(2):
            for pixel in range(16):
                theta = (h + (channel * 64) + (pixel * 4)) % 360
                scale = hsv_to_rgb(theta/360.0, 1.0, 1.0)[0] * (1.0-base)
                r,g,b=[int(col*scale +col*base) for col in rgb]
                mote.set_pixel(channel + 1, pixel, r, g, b)
                mote.set_pixel(channel + 3, pixel, r, g, b)
    mote.show()
    time.sleep(0.03)