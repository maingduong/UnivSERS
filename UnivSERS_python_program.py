# -*- coding: utf-8 -*-
"""
Created on Tue Feb  4 09:59:04 2020

@author: Ngoc Mai DUONG

"""
# spec.close()



import numpy as np
import pandas as pd
import time
import datetime
from statistics import mean 

from Fluigent_ess.ESS import Switchboard
from Fluigent_FRP.FRP import Flowboard
from Fluigent.SDK import fgt_init, fgt_close
from Fluigent.SDK import fgt_set_pressure, fgt_get_pressure, fgt_get_pressureRange

import usb.core
import seabreeze.spectrometers as sb

# Clear all
# from IPython import get_ipython
# get_ipython().magic('reset -sf')

## Set INPUT 
my_ESS_input = np.array([1])
my_compounds = ['Oil','NPs','CrosLIn','Water','Titrant']
my_ini_pressures = [380,240,330,263,255]
my_gates = [0,1,2,4,5]

t_integration_s = 15 #s
t_step_min = 3 #min
delta_P = 20
cycles = 5 

## Calculate n from inputs
P_Oil_in = my_ini_pressures[0]
P_NPs_in = my_ini_pressures[1]
P_CrosLIn_in = my_ini_pressures[2]
P_Water_in = my_ini_pressures[3]
P_Titrant_in = my_ini_pressures[4]

gate_Oil = my_gates[0]
gate_NPs = my_gates[1]
gate_CrosLIn = my_gates[2]
gate_Water = my_gates[3]
gate_Titrant = my_gates[4]

t_each_step = t_step_min*60 #s
t_integration = t_integration_s*(1e6) #1e6 = 1s
n = t_each_step/(t_integration/1e6)


# k = delay_time/t_integration_s

print('my ESS input = ', my_ESS_input)
print('my compounds = ', my_compounds)
print('my initial pressures = ', my_ini_pressures)
print('t_integration_s = ', t_integration_s)
print('delta_P = ', delta_P)
print('cycles = ', cycles)
print('n = ', n)


## Estimate the experiment time
n_SW = my_ESS_input.size
t_exp_estimated = n_SW*t_step_min*10*cycles # in min
t_exp_estimated_hour = round(t_exp_estimated/60, 2)
print('Experiment estimated time = ', t_exp_estimated_hour, ' (hours)')

def Average(lst): 
    return mean(lst) 

def stablize_to_balance_state(t=10):
    print('stablizing ...')
    fgt_set_pressure(gate_Oil, P_Oil_in)
    fgt_set_pressure(gate_NPs, P_NPs_in)
    fgt_set_pressure(gate_CrosLIn, P_CrosLIn_in)
    fgt_set_pressure(gate_Water, P_Water_in)
    fgt_set_pressure(gate_Titrant, P_Titrant_in)
    time.sleep(t) #sec

def close():
    print('closing (take about 1 min)')
    spec.close()
    fgt_set_pressure(gate_Oil, 0)
    for i in np.arange(60):
        time.sleep(1)
        P_Oil = fgt_get_pressure(gate_Oil)
        fgt_set_pressure(gate_NPs, P_Oil)
        fgt_set_pressure(gate_CrosLIn, P_Oil)
        fgt_set_pressure(gate_Water, P_Oil)
        fgt_set_pressure(gate_Titrant, P_Oil)
    fgt_set_pressure(gate_NPs, 0)
    fgt_set_pressure(gate_CrosLIn, 0)
    fgt_set_pressure(gate_Water, 0)
    fgt_set_pressure(gate_Titrant, 0)


def sweep_pressures():
    global plus_minus,step_index,df_info,dfIntensity
    cycle = 0 # first haft of the period
    P_Water_temp = P_Water_in - delta_P
    P_Titrant_temp = P_Titrant_in + delta_P
    for item in np.arange(50):
        Q_NPs = flowboard.get_flowrate(available_FRP_ports[0])
        Q_CrosLIn = flowboard.get_flowrate(available_FRP_ports[1])
        Q_Water = flowboard.get_flowrate(available_FRP_ports[2])
        Q_Titrant = flowboard.get_flowrate(available_FRP_ports[3])
        # if Q1 > 1 and Q2 > 1 and Q1 < 54 and Q2 < 54 and count < replicates:
        # step_index = 0
        if cycle <= cycles:
            P_Water_temp = P_Water_temp + (plus_minus)*delta_P
            P_Titrant_temp = P_Titrant_temp - (plus_minus)*delta_P
            fgt_set_pressure(gate_Water, P_Water_temp)
            fgt_set_pressure(gate_Titrant, P_Titrant_temp)
            time.sleep(10)
            print('Applying =  {},{},{},{},{}'.format(P_Oil_in,P_NPs_in,P_CrosLIn_in,P_Water_temp,P_Titrant_temp))
            df_info =  pd.DataFrame(columns=df_info.columns)
            dfIntensity = pd.DataFrame(columns=dfIntensity.columns)
            step_index = step_index + 1
            
            for i in range(int(n)): 
                Q_NPs = flowboard.get_flowrate(available_FRP_ports[0])
                Q_CrosLIn = flowboard.get_flowrate(available_FRP_ports[1])
                Q_Water = flowboard.get_flowrate(available_FRP_ports[2])
                Q_Titrant = flowboard.get_flowrate(available_FRP_ports[3])
                if Q_NPs > 2 and Q_CrosLIn > 2 and  Q_Water > 2 and Q_Titrant > 2 and Q_Water < 80 and Q_Titrant <80:
                    P_Oil_m = fgt_get_pressure(gate_Oil)
                    P_NPs_m = fgt_get_pressure(gate_NPs)
                    P_CrosLIn_m = fgt_get_pressure(gate_CrosLIn)
                    P_Water_m = fgt_get_pressure(gate_Water)
                    P_Titrant_m = fgt_get_pressure(gate_Titrant)
                    time_string = datetime.datetime.now().strftime("%H:%M:%S.%f")
                    intensities = spec.intensities()
                    dfIntensity.loc[len(dfIntensity)] = intensities
                    df_info.loc[len(df_info)] = [time_string, cycle, port_I, port_II, step_index,
                                            P_Oil_in, P_NPs_in, P_CrosLIn_in, P_Water_in, P_Titrant_in, 
                                            round(P_Oil_m,2),round(P_NPs_m,2), round(P_CrosLIn_m,2),
                                            round(P_Water_m,2), round(P_Titrant_m,2),
                                            round(Q_NPs,2),round(Q_CrosLIn,2), round(Q_Water,2),round(Q_Titrant,2)]
                    df_raw_data = pd.concat([df_info,dfIntensity], axis=1, sort=False)
                else:
                    plus_minus = plus_minus*(-1)
                    cycle = cycle + 1
                    print('cycle no = ', cycle)
                    print('plus_minus= ', plus_minus)
                    break
            df_raw_data.to_csv('Data\d_{}.csv'.format(today), mode='a', header=False, index=True, sep=';')
            df_raw_data = pd.DataFrame(columns=df_raw_data.columns)
        else: 
            break
    
## Set up ESS
ESS_serial_numbers = Switchboard.detect()
switchboard = Switchboard(ESS_serial_numbers[0])

## Set up FRP
FRP_serial_numbers = Flowboard.detect()
flowboard = Flowboard(FRP_serial_numbers[0])
flowboard.set_calibration(1, "Water")
flowboard.set_calibration(2, "Water")
flowboard.set_calibration(3, "Water")
flowboard.set_calibration(4, "Water")
available_FRP_ports = flowboard.get_available_ports()

## Initialize Spectrometer
usb.core.find()
devices = sb.list_devices()
spec = sb.Spectrometer(devices[0])
spec.integration_time_micros(t_integration) 
wl = spec.wavelengths()
# wl_index = np.arange(len(wl))

## Create a Dataframe
t = np.array(['t(s)'])
switch = np.array(['SW_I', 'SW_II'])
SW_step = np.array(['Cycle'])
step = np.array(['step'])
pressure = np.array(['P_Oil', 'P_NPs', 'P_CrosLIn', 'P_Water','P_Titrant',
                     'P_Oil_m', 'P_NPs_m', 'P_CrosLIn_m', 'P_Water_m', 'P_Titrant_m'])
FRP = np.array(['Q_NPs', 'Q_CrosLIn', 'Q_Water', 'Q_Titrant'])

dftime = pd.DataFrame(columns = t)
dfSW_step = pd.DataFrame(columns = SW_step)
dfSwitch = pd.DataFrame(columns = switch)
dfStep = pd.DataFrame(columns = step)
dfPressure = pd.DataFrame(columns = pressure)
dfFRP = pd.DataFrame(columns = FRP)
dfIntensity = pd.DataFrame(columns = wl)
df_info = pd.concat([dftime,dfSW_step,dfSwitch,dfStep,dfPressure,dfFRP], axis=1, sort=False)

my_file = pd.concat([df_info,dfIntensity], axis=1, sort=False)
today = datetime.datetime.today().strftime('%Y%m%d-%H%M')
my_file.to_csv('Data\d_{}.csv'.format(today), index=True, sep=';')

time_start_tuple = time.localtime() # get struct_time
time_start = time.strftime("%H:%M:%S", time_start_tuple)
print('Start experiment at ', time_start)
switchboard.set_position("A", my_ESS_input[0])
switchboard.set_position("B", my_ESS_input[0])
print("Switch on port A is at position {}".format(switchboard.get_position('A')))
print("Switch on port B is at position {}".format(switchboard.get_position('B')))

stablize_to_balance_state(t=60)
         
step_index = 0
plus_minus = 1
sw_step = 0

for item in my_ESS_input:
    sw_step = sw_step + 1
    port_I = item
    port_II = item

    # print('Start pumping air')
    # switchboard.set_position("A", 10) # for pumping air
    # switchboard.set_position("B", 10) # for pumping air
    # fgt_set_pressure(1, 500) # for pumping air
    # time.sleep(2)
    # for i in np.arange(300):
    #     time.sleep(0.5)
    #     if flowboard.get_flowrate(available_FRP_ports[0]) < 1:
    #         print('air starting in flow unit')
    #         break
    # t0 = time.time()
    switchboard.set_position("A", port_I)
    switchboard.set_position("B", port_II)
    print("Switch on port A is at position {}".format(switchboard.get_position('A')))
    print("Switch on port B is at position {}".format(switchboard.get_position('B')))

    # for i in np.arange(300):
    #     flow_list = []
    #     for j in np.arange(1,11):
    #         time.sleep(0.5)
    #         flow_list.append(flowboard.get_flowrate(available_FRP_ports[0]))
    #     if Average(flow_list) > 50:  #(= after x seconds, there is no air flow)
    #         break
    # print('Stop pumping air')
    # stablize_to_balance_state(t=15)
    # t1 = time.time()
    sweep_pressures()
    # stablize_to_balance_state(t=1)
    # print('Recording spectra during delay time')
    # df_info_delay =  pd.DataFrame(columns=df_info.columns)
    # dfIntensity_delay = pd.DataFrame(columns=dfIntensity.columns)
    
    # t_delay = t1 - t0 + 30
    # print('t_delay = ', t_delay)
    # k = 60/t_integration_s
    
    # for i in range(int(k)):
    #     time_string = datetime.datetime.now().strftime("%H:%M:%S.%f")
    #     intensities = spec.intensities()
    #     P1_delay = fgt_get_pressure(0)
    #     P2_delay = fgt_get_pressure(1)
    #     P3_delay = fgt_get_pressure(2)
    #     P4_delay = fgt_get_pressure(3)
    #     QA_delay = flowboard.get_flowrate(available_FRP_ports[0])
    #     QB_delay = flowboard.get_flowrate(available_FRP_ports[1])
    #     dfIntensity_delay.loc[len(dfIntensity_delay)] = intensities
    #     step_index = step_index+1
    #     df_info_delay.loc[len(df_info_delay)] = [time_string, sw_step, port_I, port_II, step_index,
    #                                                       P1_in, P2_in, P3_in, P4_in, 
    #                   round(P1_delay,2), round(P2_delay,2), round(P3_delay,2), round(P4_delay,2),
    #                                                       round(QA_delay,2),round(QB_delay,2)]
    #     df_delay = pd.concat([df_info_delay,dfIntensity_delay], axis=1, sort=False)
    # df_delay.to_csv('Data\d_{}.csv'.format(today), mode='a', header=False, index=True, sep=';')    
    # df_delay = pd.DataFrame(columns=df_delay.columns)    
        
close()
                