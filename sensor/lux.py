##File name        : lux.py                                                            #
##Function         : read lux sensor                                                       #
##Created by       : Wedar Panji Mardyaningsih
##Accomplishments  : 1. Read lux sensor                                     
##References       : https://www.controleverything.com/products                                                                      
##======================================= LIBRARIES =======================================

import smbus
import time

# ======================================= DEFINITION ====================================== #
def get_lux():
    
    #print(ADDR_Lux)
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

# ======================================= INITIALIZATION ================================= #
# Get I2C bus
bus = smbus.SMBus(1)

# ======================================= MAIN PROGRAM  ================================== #
if __name__ == "__main__":

    while True:
        lux = get_lux()
        
        # Output data to screen
        print "Ambient Light luminance : %.2f lux" %lux

        # Sampling time
        time.sleep(2)
