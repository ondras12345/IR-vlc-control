#Author: Ondrej Sluka
#This code is meant to be run with Python 3
#Features: 

import serial
import signal
import sys

def sigint_handler(signum, frame):   #ctrl+c
    ser.close()
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint_handler) 
    
    ser = serial.Serial(
                port='COM10',
                baudrate=9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS
                )
                

