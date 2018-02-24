# -*- coding: utf-8 -*-
import psutil
import numpy as np
import wmi
import pythoncom

# TODO: Refactor for snake-case function names
def getTemps():
    pythoncom.CoInitialize()
    # Connect to OpenHardwareMonitor
    w = wmi.WMI(namespace="root\OpenHardwareMonitor")
    
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


def getInfo(interval=0.1):
    coreloads=psutil.cpu_percent(interval=interval, percpu=True) #Get usage for each core
    cpuload=round(np.mean(coreloads),3) #Get CPU usage from mean of cores
    mem=psutil.virtual_memory() #Get RAM info
    ssd=psutil.disk_usage('/')[3] #Get boot drive load
    cputemps=getTemps()[1] #Value at position 4 is the package temperature
    return [coreloads, cpuload, mem[2], ssd, cputemps]


def getVals():
    info = getInfo() #Get all sys info
    if not info[4]: #If temperature array is empty
        cputemp=0 #Log T as zero
    else:
        cputemp=info[4][-1] #Log T as last value from T array (this is the package temperature)
    #CPU temperature, CPU load, RAM load, Storage load
    return [cputemp, info[1],info[2],info[3]]