# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 12:05:09 2016

@author: jtc9242
"""

import wx
import threading
import time
import numpy as np

import psutil
import wmi
import pythoncom

import win32gui
import win32ui 
import win32con

from PIL import Image
from PIL import ImageGrab

#Custom modules
import gui
import colorgradient
import motecore





###SETTINGS
VersionID = "Version 170129 - 1800"

#System settings
mode=0 #0=System, 1=Rainbow, 2=Cinema
userrgb=[0,255,0] #Default system RGB value

#Monitor mode settings
gradients = [
    ("DeepBlue_Red",['#0000ff','#ff3700','#ff0000']), 
    ("Blue_Red",['#0064FF','#0000ff']),
    ("Blue_Orange",['#0064FF','#0064FF','#FF2000','#FF2000']), #Doubled up for rapid change
    ("Cyan_Orange",['#00ffa0','#00cdff','#FF2000','#FF2000']), 
    ("Orange_Red",['#FF2000','#ff0000'])
]

monitorload=1 #Pulse speed by CPU load
monitortemp=1 #Pulse colour by CPU temp

defaultgradient=0 #Default CPU temp gradient

Tmin=30 #Minimum CPU temperature
Tmax=60 #Maximum CPU temperature

#Cinema mode settings
n_avg=10 #Number of frames to time-average
col_timeavg=[] #Initial empty time average list
cntrst=2.5 #Contrast factor
brtns=1.0
correction=[1.0,0.9,0.9]

"""
All saved preferences:
mode, userrgb, monitorload, monitortemp, defaultgradient, Tmin, Tmax, n_avg, col_timeavg, cntrst, brtns, correction
"""
import pickle

def load_prefs():
    global mode, userrgb, monitorload, monitortemp, defaultgradient, Tmin, Tmax, n_avg, col_timeavg, cntrst, brtns, correction
    mode, userrgb, monitorload, monitortemp, defaultgradient, Tmin, Tmax, n_avg, col_timeavg, cntrst, brtns, correction = pickle.load(open("prefs.pickle", "rb"))

def save_prefs():
    global mode, userrgb, monitorload, monitortemp, defaultgradient, Tmin, Tmax, n_avg, col_timeavg, cntrst, brtns, correction
    pickle.dump([mode, userrgb, monitorload, monitortemp, defaultgradient, Tmin, Tmax, n_avg, col_timeavg, cntrst, brtns, correction], open("prefs.pickle", "wb"))

try:
    print "Loading preferences..."
    load_prefs()
except (OSError, IOError) as e:
    print "No preferences file found. Creating one..."
    save_prefs()




###DATA

##Monitor Data
monrefresh=2
monitordata=[0,0,0,0]

gradstrings = [i[0] for i in gradients] #List of names of gradients
n=Tmax-Tmin #Number of discrete temperatures to consider
coldict=[] #Set up colour dictionary

##Cinema Data
hwnd=win32gui.GetDesktopWindow() #Set current win32 window to whole desktop
led_layout=[16,32,16] #Left, top, right




###FUNCTIONS

##Monitor Functions

def updateGradient(codes): #Update the colour dictionary of calculated gradient values
    global n
    global coldict
    coldict=[] #Clear colour dictionary
    values=colorgradient.polylinear_gradient(codes,n) #Create gradient with 'n' values
    coldict=[[values['r'][i],values['g'][i],values['b'][i]] for i in range(0,len(values['r'])) ] #Create colour dictionary as an array of [r,g,b] lists


def temp2rgb(T): #Calculate which entry to lookup from colour dictionary based on CPU temperature
    global Tmin
    global Tmax
    global coldict
    global userrgb
    global monitordata
    
    if T==0: #If T=0 this means monitor application is closed
        rgb=userrgb  #Set to user-defined rgb
    elif T<Tmin: #If T is lower than Tmin (but not zero)
        rgb=coldict[0] #Set to lowest value on gradient
    elif T>=Tmax: #If T is greater than or equal to Tmax
        rgb=coldict[-1] #Set to highest value on the gradient
    else: #If not zero and between Tmin and Tmax
        rgb=coldict[int(T)-Tmin] #Set to value calculated by position between Tmin and Tmax
    return rgb #Return calculated value
    

##Cinema functions

def getScreen(hwnd,mode=1):

    if mode==0: #If in PIL mode
        im = ImageGrab.grab()
        
    else: # If in win32 mode
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
    
    return im


def getCoords(image, led_layout, border_ratio=1, samples=4, scrollbar_width=17): #Samples gives number of checkerboard nodes to include in averaging
    width=image.size[0]
    height=image.size[1]

    vstep=int((height/led_layout[0])*border_ratio)
    hstep=int((width/led_layout[1])*border_ratio)
    
    cbv=int(vstep/(samples*border_ratio)) #Checkerboard size perpendicular
    cbh=int(hstep/(samples*border_ratio))

    l_coords=[ [[j,i] for i in range(height)[::cbv]] for j in range(vstep)[::cbv] ]
    t_coords=[ [[i,j] for i in range(width)[::cbh]] for j in range(hstep)[::cbh] ]
    r_coords=[ [[width-(1+j),i] for i in range(height)[::cbv]] for j in range(vstep)[::cbv] ]
    
    return [l_coords,t_coords,r_coords]




###STARTUP

##Monitor startup
updateGradient(gradients[defaultgradient][1]) #Update gradient to default on initialization

##Cinema startup
img_init=getScreen(hwnd) #Get initial screen
l_set, t_set, r_set = getCoords(img_init,led_layout) #Get initial coordinate list




###THREADS

##WORKER THREAD##
class WorkThread:
    event_system=threading.Event() #Event flag for first system info call
    event_cinema=threading.Event() #Event flag for first cinema info call
    event_finished=threading.Event() #Event flag for worker thread finished
    
    probeint=0.1 #Set time to probe CPU load over

    def __init__(self):
        self._running=False
        
        
    ##SYSTEM MONITOR FUNCTIONS

    def getTemps(self, w):
        names=[] #Clear core names
        temps=[] #Clear T data
        
        temperature_infos = w.Sensor() #Get sensor data
        
        for sensor in temperature_infos: #For all sensors
            if sensor.SensorType==u'Temperature': #If sensor if for temperature
                if 'CPU Core' in sensor.Name: #If sensor is for CPU Core
                    names.append(sensor.Name) #Add name to name list
                    temps.append(sensor.Value) #Add value to temperature list
                if 'CPU Package' in sensor.Name: #If sensor if for CPU Package
                    names.append(sensor.Name) #Add name to end of list
                    temps.append(sensor.Value) #Add value to end of temperature list
        return [names, temps] #Return names and temperatures

    def getInfo(self,w):
        coreloads=psutil.cpu_percent(interval=self.probeint, percpu=True) #Get usage for each core
        cpuload=round(np.mean(coreloads),3) #Get CPU usage from mean of cores
        mem=psutil.virtual_memory() #Get RAM info
        ssd=psutil.disk_usage('/')[3] #Get boot drive load
        cputemps=self.getTemps(w)[1] #Value at position 4 is the package temperature
        return [coreloads, cpuload, mem[2], ssd, cputemps]

    def getVals(self, w):
        info=self.getInfo(w) #Get all sys info
        if not info[4]: #If temperature array is empty
            cputemp=0 #Log T as zero
        else:
            cputemp=info[4][-1] #Log T as last value from T array (this is the package temperature)
        #CPU temperature, CPU load, RAM load, Storage load
        return [cputemp, info[1],info[2],info[3]]
    
    def updateMonitor(self,w):
        global monitordata
        monitordata=self.getVals(w)
        
        
    
    ##CINEMA MODE FUNCTIONS
    
    def getColours(self,image, coords): #Get colours from image at coordinates
        out=[image.getpixel((xy[0], xy[1])) for xy in coords]
        return out
      
    
    def boxColours(self,col_list, n): #Boxcar average a list of colours
        #n = number of steps/output entries
    
        out=[] #Empty output array, will be filles with [r,g,b] lists
        
        step=int(len(col_list)/n)
        
        for i in range(n): #For each "box"
            #print i
            start_px=step*i #Find start point ID
            #print "Start px: "+str(start_px)
            
            rav=np.mean([col_list[start_px+j][0] for j in range(step)])
            gav=np.mean([col_list[start_px+j][1] for j in range(step)])
            bav=np.mean([col_list[start_px+j][2] for j in range(step)])
            
            out.append([int(rav),int(gav),int(bav)])
        
        return out
    
    
    def avgLists(self,col_lists): #Average several lists of colours (used to average perpendicular to line)
        #navg=len(col_lists) #Number of lists being averaged over
        length=len(col_lists[0]) #Length of each list of colours
        
        out=[]
        
        for i in range(length): #For each pixel box
            val=[]
            for rgb in range(3):
                val.append(int(np.mean( [stack[i][rgb] for stack in col_lists ] )))
            
            out.append(val)
        
        return out
    
    
    def colChannels(self,l_avg,t_avg,r_avg): ##Convert colour lists to LED channels 16 long
        colours=[l_avg,t_avg[:16],t_avg[16:],r_avg]
        colours[0].reverse() #Reverse for orientation of LED bar
        colours[2].reverse() #Reverse for orientation of LED bar
        colours[3].reverse() #Reverse for orientation of LED bar
        
        return colours
        
        
    
    ##THREAD FUNCTIONS
    
    def stop(self): #Stop and clear
        print "Worker thread (monitor) stop initiated."
        self._running=False #Set terminate command

    def start(self): #Start and draw      
        self._running=True #Set start command
        thread1=threading.Thread(target=self.main) #Define thread
        thread1.daemon=True #Stop this thread when main thread closes
        thread1.start() #Start thread
        
    def main(self):
        #Monitor global variables
        global monitordata
        global monrefresh
        global monitorload
        global monitortemp
        
        #Cinema global variables
        global colours
        global img_init
        global hwnd
        global l_set, t_set, r_set
        
        #Timing flags
        self.event_system.clear()
        self.event_cinema.clear()
        self.event_finished.clear()
        
        #Monitor startup
        pythoncom.CoInitialize ()
        w = wmi.WMI(namespace="root\OpenHardwareMonitor")
        
        while self._running==True: #While terminate command not sent
        
        
            if mode==0: #If in system mode
                if monitorload==1 or monitortemp==1: #If monitoring either load or temperature
                    #print "Monitor data updated"
                    self.updateMonitor(w) #Update global monitor data
                #print "Monitor thread pass"
                self.event_system.set()
                time.sleep(monrefresh) #Rest for one monitor refresh period
                
                
            elif mode==2: #If in cinema mode
                img=getScreen(hwnd)
                
                if img.size!=img_init.size: #If resolution has changed
                    print "Updating resolution"
                    l_set, t_set, r_set = getCoords(img,led_layout) #Update coordinates
                    img_init = img #Update comparison image
                
                #Get colours for all pixels
                l_cols=[self.getColours(img, coords) for coords in l_set]
                t_cols=[self.getColours(img, coords) for coords in t_set]
                r_cols=[self.getColours(img, coords) for coords in r_set]
                
                #Boxcar average each row of colours
                l_box=[self.boxColours(lst,led_layout[0]) for lst in l_cols]
                t_box=[self.boxColours(lst,led_layout[1]) for lst in t_cols]
                r_box=[self.boxColours(lst,led_layout[2]) for lst in r_cols]
                
                #Perpendicular average all boxcar lists
                l_avg=self.avgLists(l_box)
                t_avg=self.avgLists(t_box)
                r_avg=self.avgLists(r_box)
                
                #Convert colour data to Mote data
                colours = self.colChannels(l_avg,t_avg,r_avg)
                
                #Set flag for first acquisition
                self.event_cinema.set()
                
                
        self.event_finished.set()
        print "Worker thread (monitor) main loop exited."






### DRAW THREAD ###
class DrawThread:
    #Initial empty variables for system mode
    rgb_old=[0,0,0] #Last RGB data (used for monitoring if static colour should redraw, and if pulse should fade)
    monitor_old=0 
    monitor_speed= 0
    
    #Initially empty variables for ambilight mode
    #Initially empty variables for rainbow mode
    
    event_finished=threading.Event() #Event flag for worker thread finished

    def __init__(self):
        self._running=False
    
    
    ##SYSTEM MONITOR FUNCTIONS
    
    def drawshotCPUPulse(self,monitordata,rgb): #Draw a single shot in CPU pulse mode
        if self.monitor_old[1]!=monitordata[1]: #If load has changed
            self.monitor_speed= 0.042*monitordata[1] + 1.8 #Recalculate pulse speed
            self.monitor_old=monitordata #Update 'monitorold' for future comparisons
            
        if rgb!=self.rgb_old: #If colour has changed based on temperature or user
            targetrgb=rgb #Set new colours to be pulse target
            pulsergb=self.rgb_old #Set pulse initial colour to be previous colour
            self.rgb_old=rgb #Update 'rgbold' for future comparisons
            
        else: #If colour has not changed
            targetrgb=0 #Clear target
            pulsergb=rgb #Send current colour to pulse
            
        motecore.pulseShot(pulsergb, targetrgb=targetrgb, base=0.7, speed=self.monitor_speed, sync=False) #Draw a pulse cycle
    
    def drawshotStatic(self,rgb): #Draw a single shot of static colour (ie includes fades when RGB is changed)
        if rgb!=self.rgb_old: #If colour has changed based on temperature or user
            targetrgb=rgb #Set new colours to be pulse target
            delta=np.subtract(targetrgb,self.rgb_old)
            print delta
            t0=time.time()
            while time.time()-t0<2:
                scale=(time.time()-t0)/2
                #print scale
                drawrgb=[int(self.rgb_old[i] + (scale*delta[i])) for i in range(3)]
                motecore.setAll(drawrgb)
                time.sleep(0.03)
                
        motecore.setAll(rgb) #Send new draw command to all pixels
        self.rgb_old=rgb #Update 'rgbold' for future comparisons
        time.sleep(1) #Rest for 1 second before recomparing
    
    
    ##CINEMA MODE FUNCTIONS
    def c_fn(self,x,n):
        val=x**n
        factor=0.5/(0.5**n)
        
        return factor*val
    
    def contrast(self,val,n):
        val=val/255.0
        
        if val<0.5:
            val=self.c_fn(val,n)
        else:
            val=1- self.c_fn(1-val,n)
        
        return int(val*255)
    
    
    ##THREAD FUNCTIONS    
    
    def stop(self): #Stop and clear
        print "Worker thread (draw) stop initiated."
        self._running=False #Set terminate command

    def start(self): #Start and draw      
        self._running=True #Set start command
        thread1=threading.Thread(target=self.main) #Define thread
        thread1.daemon=True #Stop this thread when main thread closes
        thread1.start() #Start thread
        
    def main(self):
        ##All user interaction is stored in global variables
        global mode #Current tab
        global userrgb #Current custom RGB
        
        global monitorload, monitortemp #Boolean, monitor cpu or not
        
        global correction, brtns, cntrst
        
        ##All monitor data from other thread stored globally
        global monitordata #Global variable containing all monitor data
        ##All hidden variables (ie used in calculation) stored locally

        time.sleep(1) #Let data be collected initially
        self.monitor_old=monitordata #Last monitor data set (used for monitoring if pulse rate should change)
        self.monitor_speed= 0.042*monitordata[1] + 1.8
        
        while self._running==True: #While terminate command not sent
        
            ##IF ON MONITOR PAGE##
            if mode==0:
                workthread.event_system.wait() #Wait for first data collection to complete
                ##Update colours
                if monitortemp==1: #If colour based on CPU temperature
                    rgb=temp2rgb(monitordata[0]) #Set local colour to calculated from global temperature
                else:
                    rgb=userrgb #Set local colour to global user-defined values
                
                ##Draw a shot based on animation mode
                if monitorload==1: #If pulsing based on CPU load
                    self.drawshotCPUPulse(monitordata,rgb)
                else: #If not pulsing
                    self.drawshotStatic(rgb)
                    
            
            ## IF ON RAINBOW PAGE##
            elif mode==1: #If rainbow
                motecore.rainbow(speed=1) #Draw a frame of rainbow
                
                
            elif mode==2: #If in cinema mode
                workthread.event_cinema.wait()
                
                #Time average as rapidly as possible
                col_timeavg.insert(0,colours)
                
                if len(col_timeavg)>=n_avg:
                    del col_timeavg[-1]
                
                #Draw to Mote
                for i in range(4):
                    for px in range(16):
                        r=int(np.mean([frame[i][px][0] for frame in col_timeavg]) *correction[0] *brtns)
                        g=int(np.mean([frame[i][px][1] for frame in col_timeavg]) *correction[1] *brtns)
                        b=int(np.mean([frame[i][px][2] for frame in col_timeavg]) *correction[2] *brtns)
                        
                        r=self.contrast(r,cntrst)
                        g=self.contrast(g,cntrst)
                        b=self.contrast(b,cntrst)
                        
                        motecore.mote.set_pixel(i+1, px, r, g, b)
                #print "Frame draw"
                motecore.mote.show()    
                
        self.event_finished.set()
        print "Worker thread (draw) main loop exited."









###TASKBAR ICON###

TRAY_TOOLTIP = 'Mote Monitor'
TRAY_ICON = 'icon.png'

class TaskBarIcon(wx.TaskBarIcon):
    ###SETUP###
    def __init__(self, frame):
        self.frame = frame
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.on_left_dclick)

    def set_icon(self, path):
        icon = wx.IconFromBitmap(wx.Bitmap(path))
        self.SetIcon(icon, TRAY_TOOLTIP)
        
        
    ###TASKBAR ICON GUI### 
        
    def CreatePopupMenu(self):
        #Create menu
        menu = wx.Menu()
        
        #Add menu items
        menuOpen =  menu.Append(-1, 'Open')
        menu.Bind(wx.EVT_MENU, self.on_left_dclick, menuOpen)

        menu.AppendSeparator()
        
        menuExit =  menu.Append(-1, 'Exit')
        menu.Bind(wx.EVT_MENU, self.on_exit, menuExit)
        
        #Return menu
        return menu


    ###BINDING FUNCTIONS###    

    def on_left_dclick(self, event):
        #UI interaction oneshot commands
        print 'Tray icon was left-clicked.'
        self.frame.Show(True)
        self.frame.Restore()

    def on_exit(self, event):
        self.frame.cleanExit()



###MAIN WINDOW###

class MyFrame(gui.MainFrame): #Instance of MainFrame class from 'gui'
    ###SETUP###

    def __init__(self, parent): 
        #Initialize from 'gui' MainFrame
        gui.MainFrame.__init__(self, parent)
        #Create taskbar icon
        self.taskbarIcon=TaskBarIcon(self)
        #Set window function bindings
        self.Bind(wx.EVT_CLOSE, self.onClose)
        
        ##SET GLOBAL UI VALUES
        #Set current tab to default mode
        self.notebookMain.SetSelection(mode)
        
        ##SET MONITOR UI VALUES
        #Update colour picker default appearance and abled (overrides rainbow override)
        self.pickerBaseColour.Colour = [userrgb[0],userrgb[1],userrgb[2],255]
        if monitortemp==1:
            self.pickerBaseColour.Disable()
            print "Static picker disabled"
            
        #Populate gradient choice options and select default
        self.menuGradChoice.SetItems(gradstrings)
        self.menuGradChoice.SetSelection(defaultgradient)
        
        #Populate T boxes
        self.spinTmin.SetValue(Tmin)
        self.spinTmax.SetValue(Tmax)
        
        #Update monitor T check box
        self.checkMonitorTemp.SetValue(monitortemp)
        #Update monitor load check box
        self.checkMonitorLoad.SetValue(monitorload)
        
        ##SET CINEMA UI VALUES
        self.sliderContrast.SetValue(int(10*cntrst))
        self.sliderBrightness.SetValue(int(100*brtns))
        
        
        
    ###BINDING FUNCTIONS###
        
    #On about binding show About dialog
    def OnAbout(self,e): 
        global VersionID
        dlg = wx.MessageDialog( self, VersionID, "About Mote Monitor", wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.
        
    #On exit binding, call cleanExit
    def OnExit(self,e): 
        self.cleanExit()  # Close the frame.    
        
    def OnColourChange(self,e): 
        global userrgb
        userrgb = self.pickerBaseColour.Colour[:3]
        print userrgb
        
    def onGradChoice(self,e):
        global defaultgradient
        print "Gradient selected:"
        selected = self.menuGradChoice.GetSelection()
        print selected
        updateGradient(gradients[selected][1])
        print "Updating preferences..."
        defaultgradient=selected
        
    def OnMonitorTempChange(self,e): 
        global monitortemp
        monitortemp = self.checkMonitorTemp.IsChecked()
        if monitortemp==0:
            self.menuGradChoice.Disable()
            self.pickerBaseColour.Enable()
        else:
            self.menuGradChoice.Enable()
            self.pickerBaseColour.Disable()
    
    def onTchange(self,e):
        global Tmin
        global Tmax
        global n
        global gradients
        
        Tmin=self.spinTmin.GetValue()
        Tmax=self.spinTmax.GetValue()
        n=Tmax-Tmin
        updateGradient(gradients[defaultgradient][1])
        
    def OnMonitorLoadChange(self,e): 
        global monitorload
        monitorload = self.checkMonitorLoad.IsChecked()
        
    def onContrastChange(self,e):
        global cntrst
        cntrst = self.sliderContrast.GetValue()/10.0
    
    def onBrightnessChange(self,e):
        global brtns
        brtns = self.sliderBrightness.GetValue()/100.0
    
    def onNotebookChange(self,e): #If tab changes
        global mode
        mode=self.notebookMain.GetSelection()
        print mode #Print tab ID
    
    
    
    
        
    ###CUSTOM CLOSE AND EXIT FUNCTIONS###
        
    #Override what happens when the frame is closed, either by frame.Close() or by close button
    def onClose(self, evt): 
        print "Custom close override started"
        self.Hide()
    #Clean exit sequence to be called by either icon Exit or menu Exit       
        
    def cleanExit(self): 
        print "Clean exiting..."
        #Run clean exit functions for closing threads etc
        #This will likely be a global function that cleans up all threads and runs as part of this cleanExit
        #SAVE SETTINGS
        print "Saving preferences..."
        save_prefs()
        #STOP THREADS
        workthread.stop()
        workthread.event_finished.wait()
        drawthread.stop()
        drawthread.event_finished.wait()
        motecore.clearAll()
        #CLOSE UI
        print "Removing taskbar icon..."
        self.taskbarIcon.RemoveIcon()
        print "Destroying taskbar icon..."
        self.taskbarIcon.Destroy()
        print "Destroying self..."
        self.Destroy()
        








###APP SETUP###

class App(wx.App):
    def OnInit(self):
        frame = MyFrame(None)
        self.SetTopWindow(frame)
        return True

#Threads
workthread=WorkThread()
drawthread=DrawThread()


def main():
    app = App(False)
    workthread.start()
    #time.sleep(1)
    drawthread.start()
    app.MainLoop()


if __name__ == '__main__':
    main()