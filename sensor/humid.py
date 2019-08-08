##File name        : humid.py                                                            #
##Function         : humidity and air temperature reading                                                 #
##Created by       : Wedar Panji
##Accomplishments  : 1. DHT22                                                                                                   
##References       :                                                                       
##======================================= LIBRARIES =======================================

import Adafruit_DHT
import time

# ======================================= GLOBAL VARIABLE ================================= #
pin = 17

# ======================================= MAIN PROGRAM  ================================== #
if __name__ == "__main__":
    
    while True:
        sensor = Adafruit_DHT.DHT22
        
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        print(humidity,temperature)

