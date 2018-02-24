# -*- coding: utf-8 -*-

import time
import numpy as np
from colorsys import hsv_to_rgb

from mote import Mote

mote = Mote()

mote.configure_channel(1, 16, False)
mote.configure_channel(2, 16, False)
mote.configure_channel(3, 16, False)
mote.configure_channel(4, 16, False)

N = 64

# CORE SETTINGS #
display_mode = True


# CORE FUNCTIONS #

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

# START SET PIXEL # 
def smart_set(pixel, rgb):
    global display_mode
    # Natural position with no modifiers
    ch = pixel//16 +1
    px = pixel%16
    
    rgb = [int(c) for c in rgb]
    
    #Apply modifiers
    if display_mode:
        if ch == 3 or ch == 4:  # If top right or right sticks
            px = 15-px  # Flip pixels due to bar orientation
    
    # Send to mote
    mote.set_pixel(ch, px, *rgb)


# MATH FUNCTIONS #
def gaussian(x, mu, sig):
    return np.exp(-np.power(x - mu, 2.) / (2 * np.power(sig, 2.)))


# MODE FUNCTIONS #
def rainbow(speed=1):
    h = time.time() * 50 * speed
                 
    for pixel in range(N):
        hue = (h + (pixel * 4)) % 360
        rgb = [int(c * 255) for c in hsv_to_rgb(hue/360.0, 1.0, 1.0)]

        smart_set(pixel, rgb)

    mote.show()
    time.sleep(0.03)


def drawGradient(rgbs, target_rgbs):
    t_init = time.time() # Get start time
    
    deltas = [np.subtract(target_rgbs[i], rgbs[i]) for i,_ in enumerate(rgbs)]  # Calculate change over the course of one pulse

    while time.time()-t_init < 2:
        t = (time.time()-t_init)/2 # Calculate a scale from time throughout fade
        draw_rgbs = [np.add(rgbs[i], t*deltas[i]) for i,_ in enumerate(rgbs)] # Calculate RGBs from colour fade

        for pixel in range(N):
            smart_set(pixel, draw_rgbs[pixel])  # Set pixel on bottom
            
        mote.show()  # Draw


def pulseShot(rgbs, target_rgbs, base=0.5, speed=1, phase=120):
    """
    rgbs and target_rgbs are a 64 long array of [r,g,b] lists, corresponding to the 64 LEDs
    """
    
    t_init = time.time()
    h = (time.time()-t_init) * 50 * speed + 360
        
    deltas = [np.subtract(target_rgbs[i], rgbs[i]) for i,_ in enumerate(rgbs)]  # Calculate change over the course of one pulse
    
    while h < 720:  # Stop pulse after 1 cycle
    
        t = (h % 360)/360  # Calculate a scale from time throughout pulse
        
        draw_rgbs = [np.add(rgbs[i], t*deltas[i]) for i,_ in enumerate(rgbs)] # Calculate RGBs from colour fade

        for pixel in range(N):  # For all pixels in one channel
        
            theta = (h + (pixel * 4) + phase) % 360  # Calculate angle
            scale = hsv_to_rgb(theta/360.0, 1.0, 1.0)[0] * (1.0 - base)  # Calculate brightness based on angle and base value
                              
            rgb = [ int(col*scale + col*base) for col in draw_rgbs[pixel] ]  # Calculate rgb values for pixel

            smart_set(pixel, rgb)  # Set pixel on bottom

                
        mote.show()  # Draw
        time.sleep(0.03)  # Rest
        h = (time.time()-t_init) * 50 * speed +360  # Calculate h based on new time