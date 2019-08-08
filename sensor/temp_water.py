##File name        : temp_water.py                                                            #
##Function         : water temperature reading                                                       #
##Created by       : Wedar Panji
##Accomplishments  : 1. DSB1820                                                                                                
##References       :                                                                       
##======================================= LIBRARIES =======================================

import os
import glob
import time

# ======================================= INITIALIZATION ================================= #

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

# ======================================= DEFINITION ====================================== #

def read_temp_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp():
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        temp_f = temp_c * 9.0 / 5.0 + 32.0
        return temp_c, temp_f

# ======================================= MAIN PROGRAM  ================================== #
if __name__ == "__main__":

    while True:
            print(read_temp())	
            time.sleep(1)
