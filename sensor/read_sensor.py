# File name        : read_sensor.py                                                            #
# Function         : read all sensor                                                            #
# Created by       : Wedar Panji Mardyaningsih                                              #
# Accomplishments  : 1. DHT22                                                                #
#                    2. pH                                                                  #
#                    3. DSB                                                                 #
#                    4. Lux sensor                                                          #                                   #
# References       :                                                                        #
# ======================================= LIBRARIES ======================================= #

import Adafruit_DHT
import time
import Adafruit_ADS1x15
import smbus
import os
import glob
import math

# ======================================= GLOBAL VARIABLE ================================= #

AirTemp_pin = 17
WaterTemp_pin = 4
AirTemp_sensor = Adafruit_DHT.DHT22
adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1
ADDR_Lux = 0x4a

# ======================================= DEFINITION ====================================== #
def create_file(fname):
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
    # Read ADC value
    averageVoltage = adc.read_adc(1, gain=GAIN)

    # ADC value conversion
    averageVoltage = (averageVoltage*5.0)/32767.0

    # Temperature compensation
    compensationCoefficient=1.0+0.0185*(water_temperature-25.0);    
    compensationVolatge=averageVoltage/compensationCoefficient;

    # TDS Calculation
    tdsValue=(133.42*compensationVolatge*compensationVolatge*compensationVolatge - 255.86*compensationVolatge*compensationVolatge + 857.39*compensationVolatge)*0.5; 

    # TDS to PPM conversion
    ppm=tdsValue/500

    return ppm

def read_sensor():
    # Read all the ADC channel values in a list.
    values = [0]*4

    # Sensor reading
    humidity, air_temperature = Adafruit_DHT.read_retry(AirTemp_sensor, AirTemp_pin)

    pH_voltage = ((adc.read_adc(0, gain=GAIN))*4.096)/32767.0
    pH = (-5.7*pH_voltage)+20.44

    water_temperature = read_temp()

    light_intensity = get_lux()

    TDS = get_ec(water_temperature)

    # Rounding
    humidity = round_down(humidity, 2)
    air_temperature = round_down(air_temperature, 2)
    pH = round_down(pH, 2)
    water_temperature = round_down(water_temperature, 2)
    light_intensity = round_down(light_intensity, 2)
    TDS = round_down(TDS, 2)
    
    return humidity, air_temperature, pH, water_temperature, light_intensity, TDS
	
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

# ======================================= MAIN PROGRAM  ================================== #
if __name__ == "__main__":

    while True:
        # Read sensor value
        humidity, air_temperature, pH, water_temperature, light_intensity, TDS = read_sensor()
        
        # Write to file
        write_to_file(humidity,air_temperature,light_intensity,pH,water_temperature,TDS,'Log.csv')

        # Print output
        print(humidity,air_temperature,light_intensity,pH,water_temperature,TDS)

        # Sampling time
        time.sleep(10)

