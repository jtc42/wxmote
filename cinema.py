# -*- coding: utf-8 -*-
import numpy as np

from PIL import Image
import os

if os.name == 'nt':
	OS_WIN = True
	import win32gui
	import win32ui 
	import win32con
else:
	OS_WIN = False
	import mss

hwnd=win32gui.GetDesktopWindow() #Set current win32 window to whole desktop

## General useful functions
def mesh(xy, span, step):
    """
    mesh(tuple, int, int)
    Generates a list of 2d grid coordinates, starting at coordinates of 'xy',
    extending by 'span' elements
    in steps of 'step'
    """
    grid = []
    
    for i in range(xy[0], xy[0]+span, step):
        for j in range(xy[1], xy[1]+span, step):
            grid.append((i, j))
    
    return np.array(grid)


##Cinema functions
def get_screen(hwnd):
    global OS_WIN
	
    if OS_WIN:
        # Get bitmap data from win32
        wDC = win32gui.GetWindowDC(hwnd)
        dcObj=win32ui.CreateDCFromHandle(wDC)
        cDC=dcObj.CreateCompatibleDC()
        
        dataBitMap = win32ui.CreateBitmap()
        
        # Calculate dimensions
        l,t,r,b=win32gui.GetWindowRect(hwnd)
        h=b-t
        w=r-l
        
        # Create bitmap from data
        dataBitMap.CreateCompatibleBitmap(dcObj, w, h)
        cDC.SelectObject(dataBitMap)
        cDC.BitBlt((0,0),(w, h) , dcObj, (0,0), win32con.SRCCOPY)
    
        
        # Convert to PIL
        bmpinfo = dataBitMap.GetInfo()
        bmpstr = dataBitMap.GetBitmapBits(True)
        im = Image.frombuffer(
            'RGB',
            (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
            bmpstr, 'raw', 'BGRX', 0, 1)
        
        
        # Free Resources
        dcObj.DeleteDC()
        cDC.DeleteDC()
        win32gui.ReleaseDC(hwnd, wDC)
        win32gui.DeleteObject(dataBitMap.GetHandle())
		
    else:
        with mss.mss() as sct:
            sct_img = sct.grab(sct.monitors[1])
            im = Image.frombytes('RGB', sct_img.size, sct_img.rgb)

    return im


def get_coords(image, led_layout, samples=4): #Samples gives number of checkerboard nodes to include in averaging
    # TODO: Refactor for more sensible names
    width  = image.size[0]
    height = image.size[1]

    # Calculate size of vertical and horizontal boxes to average within
    vstep = height//led_layout[0]
    hstep = width //led_layout[1]
    
    # Calculate size of coordinate grid within boxes
    cbv=int(vstep/samples) #Checkerboard size perpendicular
    cbh=int(hstep/samples)

    # Create lists of coordinate meshes (1 mesh per grid square)
    # Cut by LED layout to ensure no overhang
    coordinates = {
    'left' : [ mesh((0, i), vstep, cbv) for i in range(0, height, vstep) ][:led_layout[0]],
    'top'  : [ mesh((i, 0), hstep, cbh) for i in range(0, width, hstep) ][:led_layout[1]],
    'right': [ mesh((width-vstep, i), vstep, cbv) for i in range(0, height, vstep) ][:led_layout[0]],
    }
    
    return coordinates


def get_rgb(image, xy): #Get colours from image at coordinates
    """
    Get RGB tuple from 'image', for a particular x, y coordinate 'xy'
    """
    return image.getpixel((int(xy[0]), int(xy[1])))
    

def average_rgb(image, coordinates):
    """
    Get average RGB from 'image', for a list of coordinates
    """
    return np.mean([get_rgb(image, xy) for xy in coordinates], axis=0).astype(int)


def rgb_array(image, mesh_list):
    """
    Return a list of RGB values, 
    each element is an RGB average of the coordinates in that element
    """
    return [average_rgb(image, coordinates) for coordinates in mesh_list]
  
    
def coordict_to_rgbdict(image, coordict):
    """
    Converts left/top/right coordinate dictionary into rgb dictionary
    """
    rgbdict = {}
    for key, mesh_list in coordict.items():
        rgbdict[key] = rgb_array(image, mesh_list)
    
    return rgbdict


def rgbdict_to_channels(left_top_right_dict): #Convert colour lists to single 64 long list
    # Reverse left side so zero starts at bottom, and line follows screen around from there
    l_avg = np.flip(left_top_right_dict['left'], 0)
    t_avg = left_top_right_dict['top']
    r_avg = left_top_right_dict['right']
    # Concatenate to get 64-wide colour list
    cols=np.concatenate( (l_avg, t_avg[:16], t_avg[16:], r_avg) )
    
    return cols


def get_channels(img, led_layout):
    coordict = get_coords(img, led_layout) #Update coordinates
    rgbdict = coordict_to_rgbdict(img, coordict)
    
    return rgbdict_to_channels(rgbdict)


if __name__ == "__main__":
    for i in range(50): # Loop 100 times for profiling
        led_layout=[16,32,16] #Left, top, right
        img = get_screen(hwnd, mode = 'pil')
        colours = get_channels(img, led_layout)
        
    for i in range(50): # Loop 100 times for profiling
        led_layout=[16,32,16] #Left, top, right
        img = get_screen(hwnd, mode = 'mss')
        colours = get_channels(img, led_layout)
        
    for i in range(50): # Loop 100 times for profiling
        led_layout=[16,32,16] #Left, top, right
        img = get_screen(hwnd, mode = 'win32')
        colours = get_channels(img, led_layout)