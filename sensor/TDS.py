##File name        : TDS.py                                                            #
##Function         : TDS reading                                                 #
##Created by       : Wedar Panji
##Accomplishments  : 1. TDS                                                                                                   
##References       :                                                                       
##======================================= LIBRARIES =======================================

import os
import glob
import time
import Adafruit_ADS1x15
import RPi.GPIO as GPIO

# ======================================= INITIALIZATION ================================= #

adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1

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

    return temp_c

def get_ec():
    #ADC Reading
    averageVoltage = adc.read_adc(1, gain=GAIN)
   
    #ADC Value Conversion
    averageVoltage = (averageVoltage*4096)/32767.0
    
    #Temperature Compensation
    compensationCoefficient=1.0+0.0185*(Temperature-25.0);    
    CoefficientVolatge=averageVoltage/compensationCoefficient;  
    
    #TDS Calculation
    tdsValue=(133.42*compensationVolatge*compensationVolatge*compensationVolatge - 255.86*compensationVolatge*compensationVolatge + 857.39*compensationVolatge)*0.5; 
    
    #PPM Conversion
    ppm = (0.8094*tdsValue)+14.98

    return ECvalue


if __name__ == "__main__":

    while True:
        Temperature = read_temp()
        TDS = get_ec()
        print(Temperature,TDS)
        time.sleep(1)
