#! /usr/bin/env python3
# Author: Ondrej Sluka
# This code is made for Python3
# Features:
# * control VLC Media player via IR remote
#
# See:
# * https://wiki.videolan.org/index.php?title=VLC_HTTP_requests
# * https://github.com/z3t0/Arduino-IRremote
# * https://semver.org/


import serial
import signal
import sys
import requests
import re
import datetime

COM_PORT_DEFAULT = 'COM11'

PORT = 8080
IP = 'localhost'
URL = 'http://{}:{}/requests/status.xml'.format(IP, PORT)
VLC_PASSWORD = '1234'

KEY_DICT = {
    'NEC: 5EA110EF': 'pl_play',
    'NEC: 5EA1906F': 'pl_pause',
    # 'NEC: 5EA1906F': 'pl_stop',
    'NEC: 5EA150AF': 'pl_next',
    'NEC: 5EA1D02F': 'pl_previous',
    }

KEY_REPEAT_TIMEOUT = 2.5  # or 5 s


def sigint_handler(signum, frame):  # ctrl+c
    ser.close()
    sys.exit(0)


def get_key_id(message):
    try:
        id = re.search('Decoded (.*) \(32 bits\)', message).group(1)
    except AttributeError:
        id = None

    return id


def match_key(id):
    if id in KEY_DICT:
        command = KEY_DICT[id]
        print('Key matched: {}'.format(command))
        requests.get(url=URL, params={'command': command}, auth=('', VLC_PASSWORD))
        return True
    else:
        return False


if __name__ == '__main__':
    signal.signal(signal.SIGINT, sigint_handler)
    port = input('Enter serial port: ')
    if port == '':
        port = COM_PORT_DEFAULT
        print('Defaulting to {}'.format(COM_PORT_DEFAULT))

    ser = serial.Serial(port=port, baudrate=9600)

    last_received_time = datetime.datetime.now()
    last_received_key_id = None

    while(True):
        if ser.in_waiting > 0:
            message = str(ser.read_until())  # wait for newline
            print('Message got: {}'.format(message))

            time_delta = datetime.datetime.now() - last_received_time

            id = get_key_id(message)
            print('ID got: {}'.format(id))

            if id is not None:
                if time_delta.total_seconds() > KEY_REPEAT_TIMEOUT or (not id == last_received_key_id and time_delta.total_seconds() > (KEY_REPEAT_TIMEOUT / 5)):
                    match_key(id)

                last_received_time = datetime.datetime.now()
                last_received_key_id = id
