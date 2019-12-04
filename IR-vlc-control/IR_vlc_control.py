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
import re
import time
import datetime
import argparse
import logging
from builtins import input
from PyVLChttp.pyvlchttp import VLCHTTPAPI


class KeyAction(object):
    def __init__(self, action, name):
        self.action = action
        self.name = name


# Settings:
COM_PORT_DEFAULT = 'COM11'

PORT = '8080'
IP = 'localhost'
VLC_PASSWORD = '1234'  # nosec

vlc = VLCHTTPAPI(IP, PORT, VLC_PASSWORD)

KEY_DICT = {
    'NEC: 5EA110EF': KeyAction(vlc.play, 'play'),
    # 'NEC: 5EA1906F': KeyAction(vlc.pause, 'pause'),
    'NEC: 5EA1906F': KeyAction(vlc.stop, 'stop'),
    'NEC: 5EA150AF': KeyAction(vlc.play_next, 'next'),
    'NEC: 5EA1D02F': KeyAction(vlc.play_previous, 'previous'),
    }

KEY_REPEAT_TIMEOUT = 0.5
LOGGING_INTERVAL = 30


def sigint_handler(signum, frame):  # ctrl+c
    if args.logfile:
        args.logfile.close()

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
        print('Key matched: {}'.format(command.name))
        command.action()
        return True
    else:
        return False


def main():
    signal.signal(signal.SIGINT, sigint_handler)

    parser = argparse.ArgumentParser()
    parser.add_argument('-C', '--COM', type=str, help='COM port the Arduino is connected to')
    parser.add_argument('-l', '--logfile', type=argparse.FileType('a', encoding='UTF-8'), help='File to log playing songs into')
    parser.add_argument('-v', '--verbose', action='store_true')
    global args
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    port = args.COM
    if port is False or port is None:
        port = input('Enter serial port [{}]: '.format(COM_PORT_DEFAULT))

    if port == '':
        port = COM_PORT_DEFAULT
        logging.info('Defaulting to {}'.format(COM_PORT_DEFAULT))

    global ser
    ser = serial.Serial(port=port, baudrate=9600)

    logging.info('Listening on port {}'.format(port))

    if args.logfile:
        logging.info('Logging playing songs to {}'.format(str(args.logfile)))
        last_playing = ""
        last_log_time = datetime.datetime(2000, 1, 1, 0, 0, 0, 0)

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
            if args.logfile:
                if (datetime.datetime.now() - last_log_time).total_seconds() > LOGGING_INTERVAL:
                    try:
                        logging.debug('Getting currently playing song')
                        response = vlc.get_status()
                        now_playing = response['information']['category']['meta']['now_playing']
                        stream = response['information']['category']['meta']['filename']
                        logging.info('Now playing: {}'.format(now_playing))
                        if now_playing != last_playing:
                            last_playing = now_playing
                            logging.debug('Writing to logfile')
                            args.logfile.write('{};{};{}\n'.format(datetime.datetime.now(), stream, last_playing))
                            args.logfile.flush()
                            logging.info('Logfile write complete')

                    except Exception as e:
                        logging.info('Exception in playing song logging: {}'.format(str(e)))

                    finally:
                        last_log_time = datetime.datetime.now()  # to prevent loop when an exception occurs (nothing playing, etc.)


if __name__ == '__main__':
    main()
