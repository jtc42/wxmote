# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 12:05:09 2016

@author: jtc9242
"""

import wx
from wx import adv
import threading
import time
import numpy as np

import psutil
import wmi
import pythoncom

from PIL import Image


import glob
import os


#Custom modules
import gui
import cinema
import motecore
import sysinfo


"""
TODO: Shift global variables into a class.
On startup, create class instance. That object gets passed to the 2 threads as
an argument. Both threads then operate on that object to read/write variables.

"""


###SETTINGS
VersionID = "Version 3.20170326.1200"

# System settings
mode=0 # 0=System, 1=Rainbow, 2=Cinema
userrgb=[0,255,0] #Default system RGB value

# Monitor mode settings

# Load gradient maps
# TODO: Roll into function
mapfiles = glob.glob('gradients/*.bmp')

maps = []

for file in mapfiles:
    img = Image.open(file)
    nme = os.path.basename(file)[:-4]
    maps.append( (nme, np.array(img).astype(int)) )

# TODO: Refactor for more sensible names
monitorload = 1 # Pulse speed by CPU load
monitortemp = 1 # Pulse colour by CPU temp
monrefresh = 2 # Time between probing system

defaultgradient=0 # Default CPU temp gradient

T_minmax = [30, 60] # Min and max CPU temperatures

           
# Cinema mode settings
# TODO: Refactor for more sensible names
n_avg = 10 # Number of frames to time-average
col_timeavg = [] # Initial empty time average list
cntrst=2.5 # Contrast factor
brtns = 1.0
correction = [1.0,0.9,0.9]

"""
All saved preferences:
mode, userrgb, monitorload, monitortemp, defaultgradient, T_minmax, cntrst, brtns
"""
# TODO: Tidy up, fix line length
import pickle

def load_prefs():
    global mode, userrgb, monitorload, monitortemp, defaultgradient, T_minmax, cntrst, brtns
    mode, userrgb, monitorload, monitortemp, defaultgradient, T_minmax, cntrst, brtns = pickle.load(open("prefs.pickle", "rb"))

def save_prefs():
    global mode, userrgb, monitorload, monitortemp, defaultgradient, T_minmax, cntrst, brtns
    pickle.dump([mode, userrgb, monitorload, monitortemp, defaultgradient, T_minmax, cntrst, brtns], open("prefs.pickle", "wb"))

try:
    print("Loading preferences...")
    load_prefs()
except (OSError, IOError) as e:
    print("No preferences file found. Creating one...")
    save_prefs()




###DATA

##Monitor Data
# TODO: Monitor data to named dictionary
monitordata = [0,0,0,0]
mapstrings = [i[0] for i in maps] # List of names of gradients

              
## Cinema Data
led_layout=[16,32,16] #Left, top, right




###FUNCTIONS

##Monitor Functions
def temp2rgbs(T):
    # TODO: Refactor for more sensible names
    global T_minmax
    global defaultgradient
    p = maps[defaultgradient][1] # Load in gradient from current default
    
    T = np.clip(T, T_minmax[0], T_minmax[1]-1) # Bound to range of temperatures
    
    T_rel = (T-T_minmax[0])/(T_minmax[1]-T_minmax[0]) # Calculate 0-1 scalar of temperature
    n_grads = np.shape(p)[0] # Number of temperature-based gradients in map
    
    grad_id = int(T_rel*n_grads) # Calculate ID of gradient to be used
    
    return p[grad_id]



###THREADS

##WORKER THREAD##
class WorkThread:
    
    event_system=threading.Event() #Event flag for first system info call
    event_cinema=threading.Event() #Event flag for first cinema info call
    event_finished=threading.Event() #Event flag for worker thread finished
    
    # TODO: Refactor for more sensible names
    def __init__(self):
        self._running=False

    # TODO: Do something to replace this mess
    def updateMonitor(self, w):
        global monitordata
        monitordata=sysinfo.getVals(w)
        

    ##THREAD FUNCTIONS
    
    def stop(self): #Stop and clear
        print("Worker thread (monitor) stop initiated.")
        self._running=False #Set terminate command

    def start(self): #Start and draw      
        self._running=True #Set start command
        thread1=threading.Thread(target=self.main) #Define thread
        thread1.daemon=True #Stop this thread when main thread closes
        thread1.start() #Start thread
        
    def main(self):
        #Monitor global variables
        # TODO: Try to shift out of global namespace and into object/functions. After splitting functions into files.
        global monitordata
        global monrefresh
        global monitorload
        global monitortemp
        
        #Cinema global variables
        global colours
        global l_set, t_set, r_set
        
        #Timing flags
        self.event_system.clear() # Event for first data acquisition
        self.event_cinema.clear() # Event for first data acquisition
        self.event_finished.clear() # Event for thread ending (used for program exit)
        
        #Monitor startup
        pythoncom.CoInitialize()
        # TODO: Redefine sysinfo.w here (see launchpad script)
        sysinfo.w = wmi.WMI(namespace="root\OpenHardwareMonitor")
        
        while self._running==True: #While terminate command not sent
        
            if mode==0: #If in system mode
                if monitorload==1 or monitortemp==1: #If monitoring either load or temperature
                    #print "Monitor data updated"
                    self.updateMonitor(sysinfo.w) #Update global monitor data
                #print "Monitor thread pass"
                self.event_system.set()
                time.sleep(monrefresh) #Rest for one monitor refresh period
                
            elif mode==2: #If in cinema mode
                img = cinema.get_screen(cinema.hwnd, mode = 'win32')
                
                #Convert colour data to Mote data
                colours = cinema.get_channels(img, led_layout)
                
                #Set flag for first acquisition
                self.event_cinema.set()
                
                
        self.event_finished.set()
        print("Worker thread (monitor) main loop exited.")






### DRAW THREAD ###
class DrawThread:
    #Initial empty variables for system mode
    rgbs = [[0,0,0]]*64
    rgbs_old = [[0,0,0]]*64 # Last RGB data (used for monitoring if static colour should redraw, and if pulse should fade)
    monitor_old=0 # Old CPU load
    monitor_speed= 0 # Old pulse speed

    
    # TODO: Change to self.event_finished
    event_finished=threading.Event() # Event for thread ending (used for program exit)

    def __init__(self):
        self._running=False
    
    
    ##SYSTEM MONITOR FUNCTIONS
    
    def drawshotCPUPulse(self): #Draw a single shot in CPU pulse mode
        global monitordata
    
        if self.monitor_old[1]!=monitordata[1]: #If load has changed
            self.monitor_speed= 0.042*monitordata[1] + 1.8 #Recalculate pulse speed
            self.monitor_old=monitordata #Update 'monitorold' for future comparisons
           
        motecore.pulseShot(self.rgbs_old, self.rgbs, base=0.7, speed=self.monitor_speed) #Draw a pulse cycle
        self.rgbs_old=self.rgbs #Update 'rgbold' for future comparisons
    
    def drawshotStatic(self): #Draw a single shot of static colour (ie includes fades when RGB is changed)
        motecore.drawGradient(self.rgbs_old, self.rgbs)
        self.rgbs_old=self.rgbs #Update 'rgbold' for future comparisons
    
    
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
        print("Worker thread (draw) stop initiated.")
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
        
        global colours, col_timeavg, n_avg
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
                    self.rgbs=temp2rgbs(monitordata[0]) #Set local colour to calculated from global temperature
                else:
                    self.rgbs=[userrgb]*64 #Set local colour to global user-defined values
                
                ##Draw a shot based on animation mode
                if monitorload==1: #If pulsing based on CPU load
                    self.drawshotCPUPulse()
                else: #If not pulsing
                    self.drawshotStatic()
                    
            
            ## IF ON RAINBOW PAGE##
            elif mode==1: #If rainbow
                motecore.rainbow(speed=1) #Draw a frame of rainbow
                
                
            elif mode==2: #If in cinema mode
                workthread.event_cinema.wait() # Wait for first acquisition on worker thread, by listening for flag
                time.sleep(1.0/240) #Lock at 120fps ish

                col_timeavg.insert(0,colours)
                
                if len(col_timeavg)>=n_avg:
                    del col_timeavg[-1]
                    
                
                #Draw to Mote

                for px in range(64):
                    r=int(np.mean([frame[px][0] for frame in col_timeavg]) *correction[0] *brtns)
                    g=int(np.mean([frame[px][1] for frame in col_timeavg]) *correction[1] *brtns)
                    b=int(np.mean([frame[px][2] for frame in col_timeavg]) *correction[2] *brtns)
                    
                    r=self.contrast(r,cntrst)
                    g=self.contrast(g,cntrst)
                    b=self.contrast(b,cntrst)
                
                    motecore.smart_set(px, [r,g,b])
                
                motecore.mote.show()    
                
        self.event_finished.set()
        print("Worker thread (draw) main loop exited.")









###TASKBAR ICON###

TRAY_TOOLTIP = 'Mote Monitor'
TRAY_ICON = 'icon.png'

class TaskBarIcon(adv.TaskBarIcon):
    ###SETUP###
    def __init__(self, frame):
        self.frame = frame
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        self.Bind(adv.EVT_TASKBAR_LEFT_DCLICK, self.on_left_dclick)

    def set_icon(self, path):
        icon = wx.Icon(wx.Bitmap(path))
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
        print('Tray icon was left-clicked.')
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
            print("Static picker disabled")
            
        #Populate gradient choice options and select default
        self.menuGradChoice.SetItems(mapstrings)
        self.menuGradChoice.SetSelection(defaultgradient)
        
        #Populate T boxes
        self.spinTmin.SetValue(T_minmax[0])
        self.spinTmax.SetValue(T_minmax[1])
        
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
        save_prefs() #Update preferences file
        
    def onGradChoice(self,e):
        global defaultgradient
        selected = self.menuGradChoice.GetSelection()
        print("Gradient selected: {}".format(selected))
        print("Updating preferences...")
        defaultgradient=selected
        save_prefs() #Update preferences file
        
    def OnMonitorTempChange(self,e): 
        global monitortemp
        monitortemp = self.checkMonitorTemp.IsChecked()
        if monitortemp==0:
            self.menuGradChoice.Disable()
            self.pickerBaseColour.Enable()
        else:
            self.menuGradChoice.Enable()
            self.pickerBaseColour.Disable()
        save_prefs() #Update preferences file
    
    def onTchange(self,e):
        global T_minmax
        T_minmax = [self.spinTmin.GetValue(), self.spinTmax.GetValue()]
        save_prefs() #Update preferences file
        
    def OnMonitorLoadChange(self,e): 
        global monitorload
        monitorload = self.checkMonitorLoad.IsChecked()
        save_prefs() #Update preferences file
        
    def onContrastChange(self,e):
        global cntrst
        cntrst = self.sliderContrast.GetValue()/10.0
        save_prefs() #Update preferences file
    
    def onBrightnessChange(self,e):
        global brtns
        brtns = self.sliderBrightness.GetValue()/100.0
        save_prefs() #Update preferences file
    
    def onNotebookChange(self,e): #If tab changes
        global mode
        mode=self.notebookMain.GetSelection()
        print(mode) #Print tab ID
        save_prefs() #Update preferences file
    
    
    
    
        
    ###CUSTOM CLOSE AND EXIT FUNCTIONS###
        
    #Override what happens when the frame is closed, either by frame.Close() or by close button
    def onClose(self, evt): 
        print("Custom close override started")
        self.Hide()
    #Clean exit sequence to be called by either icon Exit or menu Exit       
        
    def cleanExit(self): 
        print("Clean exiting...")
        #Run clean exit functions for closing threads etc
        #This will likely be a global function that cleans up all threads and runs as part of this cleanExit
        #SAVE SETTINGS
        print("Saving preferences...")
        save_prefs() #Update preferences file
        #STOP THREADS
        workthread.stop()
        workthread.event_finished.wait()
        drawthread.stop()
        drawthread.event_finished.wait()
        motecore.clearAll()
        #CLOSE UI
        print("Removing taskbar icon...")
        self.taskbarIcon.RemoveIcon()
        print("Destroying taskbar icon...")
        self.taskbarIcon.Destroy()
        print("Destroying self...")
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