# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 09:46:09 2016

@author: jtc9242
"""

import psutil
import numpy as np
import wmi

import pythoncom 

#Time to probe CPU load over
probeint=0.1

#pythoncom.CoInitialize () 

#Connect to CPUThermometer
w = wmi.WMI(namespace="root\OpenHardwareMonitor")

def getTemps():
    names=[] #Clear core names
    temps=[] #Clear T data
    
    temperature_infos = w.Sensor() #Get sensor data
    
    for sensor in temperature_infos: #For all sensors
        if sensor.SensorType=='Temperature': #If sensor if for temperature
            if 'CPU Core' in sensor.Name: #If sensor is for CPU Core
                names.append(sensor.Name) #Add name to name list
                temps.append(sensor.Value) #Add value to temperature list
            if 'CPU Package' in sensor.Name: #If sensor if for CPU Package
                names.append(sensor.Name) #Add name to end of list
                temps.append(sensor.Value) #Add value to end of temperature list
    
    return [names, temps] #Return names and temperatures
    
def getInfo():
    coreloads=psutil.cpu_percent(interval=probeint, percpu=True) #Get usage for each core
    cpuload=round(np.mean(coreloads),3) #Get CPU usage from mean of cores
    mem=psutil.virtual_memory() #Get RAM info
    ssd=psutil.disk_usage('/')[3] #Get boot drive load
    cputemps=getTemps()[1] #Value at position 4 is the package temperature
    return [coreloads, cpuload, mem[2], ssd, cputemps]


def getVals():
    info=getInfo() #Get all sys info
    if not info[4]: #If temperature array is empty
        cputemp=0 #Log T as zero
    else:
        cputemp=info[4][-1] #Log T as last value from T array (this is the package temperature)
    #CPU temperature, CPU load, RAM load, Storage load
    return [cputemp, info[1],info[2],info[3]]


#DEFINE FUNCTION THAT PERFORMS A "ONE-SHOT" DRAW OF THE DATA OVER A USER DEFINED TIME
#This user defined time dictates the rate of smoothing (should be some fraction of the define time so it's fast compared to data aquisition)
#and also the rate of warning pulsing (probably say 2 pulses per aquisition time? Look into functions for this, sawtooth using jump to value and linear decrease)



#Draw functions:
#Both a function of offset, which is calculated before the functions are called
#offset goes from 0 to 1, where 0 is start of cycle and 1 is end of cycle
#both return a 16 element array corresponding to pixel values

#warningpulse(offset, hue, basehue)
#return 16 element array of pixel values

#bar(normalised_value, offset, hue, basehue)
#return 16 element array of pixel values



#Find a way to have CPU temperature monitor pulse (blue to dark?) if no information is available
#If parameters reach a "critical" value, bar will pulse red

#Avoid loads of threads!!!
#Main loop will likely have to be in a thread saparate to the GUI though
#Main script will iterate across each bar and redraw in turn
#Generally this is simple as it just changes the levels
#Pulsing and smoothing will require more thought
#Maybe pulse and smooth at frequency of redraws?

#Ie.
#Reset 't'
#Update data
#Process all data, calculate what each bar should aim for
#Start timed draw routine that goes through each bar and works out values as a function of 't'
#Once 't' hits threshold, restart loop 