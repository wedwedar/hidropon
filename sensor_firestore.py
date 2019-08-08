##File name        : sensorreading_firestore.py                                                       #
##Function         : BACA SENSOR DAN KIRIM KE CLOUD FIRESTORE (dari kode GABUNGAN.py)                 #
##Created by       : Mokhamad Arfan Wicaksono, Wedar Panji                                            #
##Accomplishments  : 1. DT22                                                                          #
##                   2. pH                                                                 
##                   3. DSB                                                                
##                   4. Lux sensor                                                         
##                   5. Send data to realtime firebase                                     
##References       :                                                                       
##======================================= LIBRARIES =======================================

import Adafruit_DHT
import time
import Adafruit_ADS1x15
import smbus
import os
import glob
import math
import datetime
from google.cloud import firestore
import os
import subprocess
import re

# ======================================= GLOBAL VARIABLE ================================= #

AirTemp_pin = 17
WaterTemp_pin = 4
AirTemp_sensor = Adafruit_DHT.DHT22
adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1
user_id = u'prototype'
ADDR_Lux = 0x4A

# ======================================= DEFINITION ====================================== #
def create_file(fname):
    #Prosedur untuk membuat file
    file = open(fname,"w")
    file.write("==========This is the beginning==========\n")
    file.write("Log started at "+"\n")
    file.write("File format is :\n")
    file.write("humidity,air_temperature,light_intensity,pH,water_temperature\n")
    file.close()

def write_to_file(humidity,air_temperature,light_intensity,pH,water_temperature,TDS,fname):
    # Open file and append data
    file = open(fname,"a+")
    file.write(str(humidity) + "," + str(air_temperature) + "," +  str(light_intensity) + ","  + str(pH)+","  + str(water_temperature)+","  + str(TDS)+"\n")
    file.close()
    return 1

def round_down(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n * multiplier) / multiplier

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
    
def get_lux():  
    
    # Read byte data 
    bus.write_byte_data(ADDR_Lux, 0x02, 0x40)
    time.sleep(0.5)

    # Read data back from 0x03(03), 2 bytes
    data = bus.read_i2c_block_data(ADDR_Lux, 0x03, 2)

    # Convert the data to lux
    exponent = (data[0] & 0xF0) >> 4
    mantissa = ((data[0] & 0x0F) << 4) | (data[1] & 0x0F)
    luminance = ((2 ** exponent) * mantissa) * 0.045

    #Reset data
    data=0

    return luminance

def get_ec(water_temperature):
    averageVoltage = adc.read_adc(1, gain=GAIN)
    averageVoltage = (averageVoltage*5.0)/32767.0
    averageVoltage = (averageVoltage)
    compensationCoefficient=1.0+0.0185*(water_temperature-25.0);    
    compensationVolatge=averageVoltage/compensationCoefficient;  
    tdsValue=(133.42*compensationVolatge*compensationVolatge*compensationVolatge - 255.86*compensationVolatge*compensationVolatge + 857.39*compensationVolatge)*0.5; 
    ppm=tdsValue/500
    #ppm = (0.8094*tdsValue)+14.98
    #print(averageVoltage, CoefficientVolatge)
    #if(CoefficientVolatge<150):
    #    print("No solution!")
    #elif(CoefficientVolatge>3300):
    #    print("Out of the range!")
    #else:
    #    if(CoefficientVolatge<=448):
    #        ECvalue=0.684*CoefficientVolatge+54.32
    #    elif(CoefficientVolatge<=1457):
    #        ECvalue=6.98*CoefficientVolatge-127
    #    else:
    #        ECvalue=1.3*CoefficientVolatge+428

    #ECvalueRaw = ECvalue/1000.0
    #ECvalue = ECvalue/1/1000.0

    #PPM = ECvalue*500

    return ppm

def read_sensor():
    # Read all the ADC channel values in a list.
    values = [0]*4

    # Read air humidity & temperature
    humidity, air_temperature = Adafruit_DHT.read_retry(AirTemp_sensor, AirTemp_pin)

    # Read pH from adc reading
    pH_voltage = ((adc.read_adc(0, gain=GAIN))*4.096)/32767.0
    pH = (-5.7*pH_voltage)+20.44

    # Read water temperature (call procedure read_temp())
    water_temperature = read_temp()

    # Read light intensity (call procedure get_lux())
    light_intensity = get_lux()

    # Read water nutrition (call procedure get_ec())
    TDS = get_ec(water_temperature)

    # Rounding
    humidity = round_down(humidity, 2)
    air_temperature = round_down(air_temperature, 2)
    pH = round_down(pH, 2)
    water_temperature = round_down(water_temperature, 2)
    light_intensity = round_down(light_intensity, 2)
    TDS = round_down(TDS, 2)
    
    return humidity, air_temperature, pH, water_temperature, light_intensity, TDS

def update_firebase(humidity,air_temperature,light_intensity,pH,water_temperature,TDS):
    #get date timestamp
    dates = datetime.datetime.now()
    datess = dates.strftime("%d-%m-%Y")
    
    #declaration
    db = firestore.Client()
    doc_ref = db.collection(u'basics').document(user_id)

    doc_ref.set({
        u'humidity':humidity,
        u'light':light_intensity,
        u'ph':pH,
        u'tds':TDS,
        u'tempe':air_temperature,
        u'tempk':water_temperature
    })
    
    hist_ref = doc_ref.collection(u'history').document(datess).collection(u'detail').document(dates.strftime("%d-%m-%Y %H:%M:%S"))
    hist_ref.set({
        u'humidity':humidity,
        u'light':light_intensity,
        u'ph':pH,
        u'tds':TDS,
        u'tempe':air_temperature,
        u'tempk':water_temperature,
        u'timestamp':dates.strftime("%d-%m-%Y %H:%M:%S")
    })

# ======================================= INITIALIZATION ================================= #
# Get I2C bus
bus = smbus.SMBus(3)
time.sleep(1)

# Water temperature
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
 
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

create_file('Log.csv')
j=1
a=1


# ======================================= MAIN PROGRAM  ================================== #
if __name__ == "__main__":

    while True:
        # Read sensor value
        humidity, air_temperature, pH, water_temperature, light_intensity, TDS = read_sensor()
        
        # Write to file
        write_to_file(humidity,air_temperature,light_intensity,pH,water_temperature,TDS,'Log.csv')

        # Print output
        print(humidity,air_temperature,light_intensity,pH,water_temperature,TDS)

        # Update firebase
        update_firebase(humidity,air_temperature,light_intensity,pH,water_temperature,TDS)

        # Sampling time
        time.sleep(2)


