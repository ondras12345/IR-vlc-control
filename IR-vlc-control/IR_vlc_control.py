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
import time
import datetime
import argparse
import logging
from builtins import input

COM_PORT_DEFAULT = 'COM11'

PORT = 8080
IP = 'localhost'
URL = 'http://{}:{}/requests/status.xml'.format(IP, PORT)
VLC_PASSWORD = '1234'  # nosec

KEY_DICT = {
    'NEC: 5EA110EF': 'pl_play',
    'NEC: 5EA1906F': 'pl_pause',
    # 'NEC: 5EA1906F': 'pl_stop',
    'NEC: 5EA150AF': 'pl_next',
    'NEC: 5EA1D02F': 'pl_previous',
    }

KEY_REPEAT_TIMEOUT = 0.5


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

    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--COM', type=str, help='COM port the Arduino is connected to')
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    port = args.COM
    if port is False:
        port = input('Enter serial port [{}]: '.format(COM_PORT_DEFAULT))

    if port == '':
        port = COM_PORT_DEFAULT
        logging.info('Defaulting to {}'.format(COM_PORT_DEFAULT))

    ser = serial.Serial(port=port, baudrate=9600)

    logging.info('Listening on port {}'.format(port))

    last_received_time = datetime.datetime.now()
    last_received_key_id = None

    while(True):
        if ser.in_waiting > 0:
            message = str(ser.read_until())  # wait for newline
            logging.debug('Message got: {}'.format(message))

            time_delta = datetime.datetime.now() - last_received_time

            id = get_key_id(message)
            logging.debug('ID got: {}'.format(id))

            if id is not None:
                if time_delta.total_seconds() > KEY_REPEAT_TIMEOUT or not id == last_received_key_id:
                    match_key(id)

                last_received_time = datetime.datetime.now()
                last_received_key_id = id
        else:
            time.sleep(0.2)
