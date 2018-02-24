# -*- coding: utf-8 -*-

import wx
from wx import adv

import pickle

import threading
import time
import numpy as np
from PIL import Image

import glob
import os
from copy import copy

# Local modules
import gui
from tools import cinema
from tools import motecore
from tools import sysinfo
from tools import contrast


MODES = ['system', 'rainbow', 'cinema']


# Convert between mode names and IDs
def mode2int(mode):
    global MODES
    return MODES.index(mode)


def int2mode(id):
    global MODES
    return MODES[id]


# Load gradient maps
def get_maps(reg_expression):
    mapfiles = glob.glob(reg_expression)
    maps = []
    for file in mapfiles:
        img = Image.open(file)
        nme = os.path.basename(file).split(".")[0]
        maps.append((nme, np.array(img).astype(int)))
    return maps

MAPS = get_maps('gradients/*.bmp')

# SETTINGS
VersionID = "Version 18.02.24"

PREFS = {
    'led_layout': [16, 32, 16],
    'mode': 'system',
    'user_rgb': [0, 255, 0],
    'monitor_load': True,
    'monitor_temp': True,
    'monitor_interval': 2,
    'default_gradient': 0,
    'T_minmax': [30, 60],
    'cinema_averages': 10,
    'cinema_contrast': 2.5,
    'cinema_brightness': 1.0,
    'cinema_correction': [1.0, 0.9, 0.9],
}


def load_prefs():
    global PREFS
    PREFS = pickle.load(open("prefs.pickle", "rb"))


def save_prefs():
    global PREFS
    pickle.dump(PREFS, open("prefs.pickle", "wb"))

try:
    print("Loading preferences...")
    load_prefs()
except (OSError, IOError) as e:
    print("No preferences file found. Creating one...")
    save_prefs()


# WORKER THREAD
class WorkThread:
    def __init__(self):
        self._running = False

        self.monitor_data = {
            'CPU Package/Temperature': 0.,
            'CPU Total/Load': 0.,
            'Memory/Load': 0.,
            'Storage/Load': 0.,
        }

        # Event flag for first system info call
        self.event_system = threading.Event()
        # Event flag for first cinema info call
        self.event_cinema = threading.Event()
        # Event flag for worker thread finished
        self.event_finished = threading.Event()

    # THREAD FUNCTIONS

    def stop(self):  # Stop and clear
        print("Worker thread (monitor) stop initiated.")
        self._running = False  # Set terminate command

    def start(self):  # Start and draw
        self._running = True  # Set start command
        thread1 = threading.Thread(target=self.main)  # Define thread
        thread1.daemon = True  # Stop this thread when main thread closes
        thread1.start()  # Start thread

    def main(self):

        # Timing flags
        self.event_system.clear()  # Event flag for first system info call
        self.event_cinema.clear()  # Event flag for first cinema info call
        self.event_finished.clear()  # Event flag for worker thread finished

        # Monitor startup
        while self._running is True:  # While terminate command not sent

            if PREFS['mode'] == 'system':  # If in system mode
                # If monitoring either load or temperature
                if PREFS['monitor_load'] or PREFS['monitor_temp']:
                    self.monitor_data = sysinfo.get_status()

                # Set flag for first acquisition
                if not self.event_system.is_set():
                    self.event_system.set()

                # Rest for one monitor refresh period
                time.sleep(PREFS['monitor_interval'])  

            elif PREFS['mode'] == 'cinema':  # If in cinema mode
                img = cinema.get_screen(cinema.hwnd)

                # Convert colour data to Mote data
                self.cinema_colour_data = cinema.get_channels(img, PREFS['led_layout'])

                # Set flag for first acquisition
                if not self.event_cinema.is_set():
                    self.event_cinema.set()

        self.event_finished.set()
        print("Worker thread (monitor) main loop exited.")


# DRAW THREAD
class DrawThread:
    def __init__(self, attached_worker):
        self._running = False
        self.attached_worker = attached_worker

        # Initial array of RGB values
        self.rgbs = [[0, 0, 0]] * sum(PREFS['led_layout'])
        # Last RGB data (used for monitoring if static colour should redraw)
        self.rgbs_old = [[0, 0, 0]] * sum(PREFS['led_layout'])
        # Initial CPU load
        self.monitor_old = self.attached_worker.monitor_data
        # Initial pulse speed
        self.pulse_speed = self.load2speed(self.attached_worker.monitor_data['CPU Total/Load'])
        # Array to store cinema data used in time averaging
        self.cinema_timeavg = []
        # Event for thread ending (used for program exit)
        self.event_finished = threading.Event()

    # SYSTEM MONITOR FUNCTIONS

    # Convert system temperature into RGB array, from MAP
    def temp2rgbs(self, temp):
        global PREFS, MAPS

        # Load in gradient from current default
        p = MAPS[PREFS['default_gradient']][1] 
        # Bound to range of temperatures
        temp = np.clip(temp, PREFS['T_minmax'][0], PREFS['T_minmax'][1]-1)
        # Calculate 0-1 scalar of temperature
        temp_rel = (temp - PREFS['T_minmax'][0])/(PREFS['T_minmax'][1] - PREFS['T_minmax'][0]) 
        # Number of temperature-based gradients in map
        n_grads = np.shape(p)[0] 
        # Calculate ID of gradient to be used
        grad_id = int(temp_rel*n_grads)

        return p[grad_id]

    # Convert a CPU load (pc) into a breathing pulse speed
    def load2speed(self, load):
        return 0.042 * load + 1.8 

    # Draw a single shot in CPU pulse mode
    def drawshotCPUPulse(self): 
        # If load has changed
        if self.monitor_old['CPU Total/Load'] != self.attached_worker.monitor_data['CPU Total/Load']:
            # Recalculate pulse speed
            self.pulse_speed = self.load2speed(self.attached_worker.monitor_data['CPU Total/Load'])
            # Update 'monitorold' for future comparisons
            self.monitor_old = self.attached_worker.monitor_data
   
        motecore.pulseShot(self.rgbs_old, self.rgbs, base=0.7, speed=self.pulse_speed)  # Draw a pulse cycle
        self.rgbs_old = self.rgbs  # Update 'rgbold' for future comparisons

    # Draw a single shot of static colour (ie includes fades when RGB is changed)
    def drawshotStatic(self): 
        motecore.drawGradient(self.rgbs_old, self.rgbs)
        self.rgbs_old = self.rgbs  # Update 'rgbold' for future comparisons

    # THREAD FUNCTIONS

    def stop(self):  # Stop and clear
        print("Draw thread stop initiated.")
        self._running = False  # Set terminate command

    def start(self):  # Start and draw      
        self._running = True  # Set start command
        thread1 = threading.Thread(target=self.main)  # Define thread
        thread1.daemon = True  # Stop this thread when main thread closes
        thread1.start()  # Start thread

    def main(self):
        while self._running:  # While terminate command not sent

            # IF ON MONITOR PAGE
            if PREFS['mode'] == 'system':
                # Wait for first acquisition on worker thread, by listening for flag
                self.attached_worker.event_system.wait() 

                # Update colours
                if PREFS['monitor_temp']:  # If colour based on CPU temperature
                    # Set local colour to calculated from global temperature
                    self.rgbs = self.temp2rgbs(self.attached_worker.monitor_data['CPU Package/Temperature']) 
                else:
                    # Set local colour to global user-defined values
                    self.rgbs = [PREFS['user_rgb']] * sum(PREFS['led_layout'])

                # Draw a shot based on animation mode
                if PREFS['monitor_load']:  # If pulsing based on CPU load
                    self.drawshotCPUPulse()
                else:  # If not pulsing
                    self.drawshotStatic()

            # IF ON RAINBOW PAGE
            elif PREFS['mode'] == 'rainbow':  # If rainbow
                motecore.rainbow(speed=1)  # Draw a frame of rainbow

            elif PREFS['mode'] == 'cinema':  # If in cinema mode

                # Wait for first acquisition on worker thread
                self.attached_worker.event_cinema.wait()

                # 120fps ish
                time.sleep(1.0/240)

                self.cinema_timeavg.insert(0, self.attached_worker.cinema_colour_data)

                if len(self.cinema_timeavg) >= PREFS['cinema_averages']:
                    del self.cinema_timeavg[-1]

                # Draw to Mote
                for px in range(sum(PREFS['led_layout'])):
                    # Get initial RGB array from time-averaging
                    rgb = np.mean([frame[px] for frame in self.cinema_timeavg], axis=0)
                    # Apply colour correction
                    rgb = np.multiply(rgb, PREFS['cinema_correction'])
                    # Apply total brightness
                    rgb = np.multiply(rgb, PREFS['cinema_brightness'])
                    # Apply contrast
                    rgb = contrast.apply_contrast(rgb, PREFS['cinema_contrast'])

                    # Smart-set based on pixel number
                    motecore.smart_set(px, rgb)

                motecore.mote.show()    

        self.event_finished.set()
        print("Worker thread (draw) main loop exited.")


# TASKBAR ICON

TRAY_TOOLTIP = 'Mote Monitor'
TRAY_ICON = 'icon.png'


class TaskBarIcon(adv.TaskBarIcon):
    def __init__(self, frame):
        self.frame = frame
        super(TaskBarIcon, self).__init__()
        self.set_icon(TRAY_ICON)
        self.Bind(adv.EVT_TASKBAR_LEFT_DCLICK, self.on_left_dclick)

    def set_icon(self, path):
        icon = wx.Icon(wx.Bitmap(path))
        self.SetIcon(icon, TRAY_TOOLTIP)

    # TASKBAR ICON GUI

    def CreatePopupMenu(self):
        # Create menu
        menu = wx.Menu()

        # Add menu items
        menuOpen = menu.Append(-1, 'Open')
        menu.Bind(wx.EVT_MENU, self.on_left_dclick, menuOpen)

        menu.AppendSeparator()

        menuExit = menu.Append(-1, 'Exit')
        menu.Bind(wx.EVT_MENU, self.on_exit, menuExit)

        # Return menu
        return menu


    # BINDING FUNCTIONS

    def on_left_dclick(self, event):
        # UI interaction oneshot commands
        print('Tray icon was left-clicked.')
        self.frame.Show(True)
        self.frame.Restore()

    def on_exit(self, event):
        self.frame.cleanExit()

# MAIN WINDOW


# Instance of MainFrame class from 'gui'
class MyFrame(gui.MainFrame):  
    def __init__(self, parent): 
        global PREFS, MAPS
        # Initialize from 'gui' MainFrame
        gui.MainFrame.__init__(self, parent)
        # Create taskbar icon
        self.taskbarIcon = TaskBarIcon(self)
        # Set window function bindings
        self.Bind(wx.EVT_CLOSE, self.onClose)

        # Set current tab to default mode
        self.notebookMain.SetSelection(mode2int(PREFS['mode']))

        # Update colour picker default appearance and abled
        self.pickerBaseColour.Colour = [*PREFS['user_rgb'], 255]
        if PREFS['monitor_temp']:
            self.pickerBaseColour.Disable()
            print("Static picker disabled")

        # Populate gradient choice options and select default
        self.menuGradChoice.SetItems([i[0] for i in MAPS])
        self.menuGradChoice.SetSelection(PREFS['default_gradient'])

        # Populate T boxes
        self.spinTmin.SetValue(PREFS['T_minmax'][0])
        self.spinTmax.SetValue(PREFS['T_minmax'][1])

        # Update monitor T check box
        self.checkMonitorTemp.SetValue(PREFS['monitor_temp'])
        # Update monitor load check box
        self.checkMonitorLoad.SetValue(PREFS['monitor_load'])

        # SET CINEMA UI VALUES
        self.sliderContrast.SetValue(int(10*PREFS['cinema_contrast']))
        self.sliderBrightness.SetValue(int(100*PREFS['cinema_brightness']))

    # BINDING FUNCTIONS

    # On about binding show About dialog
    def OnAbout(self, e):
        global VersionID
        dlg = wx.MessageDialog(self, VersionID, "About Mote Monitor", wx.OK)
        dlg.ShowModal()  # Show it
        dlg.Destroy()  # finally destroy it when finished.

    # On exit binding, call cleanExit
    def OnExit(self, e):
        self.cleanExit()  # Close the frame.    

    def OnColourChange(self, e):
        global PREFS
        PREFS['user_rgb'] = self.pickerBaseColour.Colour[:3]
        save_prefs()  # Update preferences file

    def onGradChoice(self, e):
        global PREFS
        PREFS['default_gradient'] = self.menuGradChoice.GetSelection()
        save_prefs()  # Update preferences file

    def OnMonitorTempChange(self, e):
        global PREFS
        PREFS['monitor_temp'] = self.checkMonitorTemp.IsChecked()
        if PREFS['monitor_temp']:
            self.menuGradChoice.Enable()
            self.pickerBaseColour.Disable()
        else:
            self.menuGradChoice.Disable()
            self.pickerBaseColour.Enable()
        save_prefs()  # Update preferences file

    def onTchange(self, e):
        global PREFS
        PREFS['T_minmax'] = [self.spinTmin.GetValue(), self.spinTmax.GetValue()]
        save_prefs()  # Update preferences file
        
    def OnMonitorLoadChange(self, e):
        global PREFS
        PREFS['monitor_load'] = self.checkMonitorLoad.IsChecked()
        save_prefs()  # Update preferences file
        
    def onContrastChange(self, e):
        global PREFS
        PREFS['cinema_contrast'] = self.sliderContrast.GetValue()/10.0
        save_prefs()  # Update preferences file
    
    def onBrightnessChange(self, e):
        global PREFS
        PREFS['cinema_brightness'] = self.sliderBrightness.GetValue()/100.0
        save_prefs()  # Update preferences file
    
    def onNotebookChange(self, e):  # If tab changes
        global PREFS
        PREFS['mode'] = int2mode(self.notebookMain.GetSelection())
        save_prefs()  # Update preferences file

    # CUSTOM CLOSE AND EXIT FUNCTIONS

    # Override what happens when the frame is closed, either by frame.Close() or by close button
    def onClose(self, evt):
        print("Custom close override started")
        self.Hide()

    # Clean exit sequence, to be called by either icon Exit or menu Exit
    def cleanExit(self):
        print("Clean exiting...")
        print("Saving preferences...")
        save_prefs()  # Update preferences file

        # STOP THREADS
        workthread.stop()
        workthread.event_finished.wait()
        drawthread.stop()
        drawthread.event_finished.wait()
        motecore.clearAll()

        # CLOSE UI
        print("Removing taskbar icon...")
        self.taskbarIcon.RemoveIcon()
        print("Destroying taskbar icon...")
        self.taskbarIcon.Destroy()
        print("Destroying self...")
        self.Destroy()


# APP SETUP
class App(wx.App):
    def OnInit(self):
        frame = MyFrame(None)
        self.SetTopWindow(frame)
        return True


# Create thread objects
workthread = WorkThread()
drawthread = DrawThread(workthread)


def main():
    app = App(False)
    workthread.start()
    drawthread.start() 
    app.MainLoop()


if __name__ == '__main__':
    main()
