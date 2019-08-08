##File name        : ph.py                                                            #
##Function         : read pH value                                                       #
##Created by       : Wedar Panji
##Accomplishments  : 1. pH                                                                                            
##References       :                                                                       
##======================================= LIBRARIES =======================================

import time
import Adafruit_ADS1x15

# ======================================= GLOBAL VARIABLE ================================= #

adc = Adafruit_ADS1x15.ADS1115()
GAIN = 1

# ======================================= DEFINITION ====================================== #

def create_file(fname):
    file = open(fname,"w")
    file.write("==========This is the beginning==========\n")
    file.write("Log started at "+"\n")
    file.write("File format is :\n")
    file.write("CH0,CH1,CH2,CH3,PH,temp\n")
    file.close()

def write_to_file(CH0,CH1,CH2,CH3,PH,temp,fname):
    # Open file and append data
    file = open(fname,"a+")
    file.write(str(CH0) + "," + str(CH1) + "," +  str(CH2) + ","  + str(CH3)+","  + str(PH)+","  + str(temp)+"\n")
    file.close()
    return 1

# ======================================= INITIALIZATION ================================= #
    
create_file('Predict.csv')
j=1

# ======================================= MAIN PROGRAM  ================================== #

if __name__ == "__main__":
    
    print('Reading ADS1x15 values, press Ctrl-C to quit...')
    # Print nice channel column headers.
    print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*range(4)))
    print('-' * 37)
    
    # Main loop.
    while True:
        # Read all the ADC channel values in a list.
        values = [0]*4
        
        for i in range(4):
            # Read the specified ADC channel using the previously set gain value.
            values[i] = adc.read_adc(i, gain=GAIN)

            # convert ADC value to Rasp Pi value range
            values[i] = (values[i]*4.096)/32767.0
            
        # Print the ADC values.
        print('| {0:>6} | {1:>6} | {2:>6} | {3:>6} |'.format(*values))

        # pH calculation
        pH= (-5.559*values[0])+21.24

        # Write to file
        write_to_file(values[0],values[1],values[2],values[3],pH,TEMP,'Predict.csv')
        
        print(j)
        print(pH)
        j=j+1
        
        # Pause for half a second.
        time.sleep(0.5)
