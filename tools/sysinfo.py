# -*- coding: utf-8 -*-
import os
import psutil
import numpy as np
import wmi
import pythoncom

def get_ohm(sensor_list):
    
    pythoncom.CoInitialize()

    # Connect to OpenHardwareMonitor
    w = wmi.WMI(namespace="root\OpenHardwareMonitor")
    
    data = {}
    
    # Get sensor data. Note: This totally rebuilds the sensor array, so targetting below is required at each run
    data_all = w.Sensor()
    if len(data_all) > 0:
        for d in data_all:
            for s in sensor_list:
                if d.Name == s[0] and d.SensorType == s[1]:
                    data["{0}/{1}".format(d.Name, d.SensorType)] = round(d.Value,2)
    else:
        for s in sensor_list:
            data["{0}/{1}".format(s[0], s[1])] = None
    
    return data



def get_status():
    data = {
        'CPU Package/Temperature': None,
        'CPU Total/Load': None,
    }

    # If running Windows and OHM
    if os.name == 'nt':
        ohm_data = get_ohm([
            ('CPU Package', 'Temperature'),
            ('CPU Total', 'Load'),
            ])
        
        for key, value in ohm_data.items():
            data[key] = value  # Replace return data with OHM data

    # If no CPU load was obtained (either no Win, or no OHM)
    if data['CPU Total/Load'] == None:
        core_loads = psutil.cpu_percent(interval=0.1, percpu=True)
        data['CPU Total/Load'] = round(np.mean(core_loads), 3)  # Get CPU usage from mean of cores
    
    # If no CPU temp was obtained (either no Win, or no OHM)
    if data['CPU Package/Temperature'] == None:
        data['CPU Package/Temperature'] = 0.
    # TODO: Method to get CPU temperature in Linux

    return data