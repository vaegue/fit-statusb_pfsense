#!/usr/bin/env python3.7
#
# create pseudo-socket to send specific data to statusb_mon for testing
# This script is for testing the main 'statusb_mon.py' with consistent, predictable patterns of ping loss
# it creates a unix socket (./sock_test.sock) that outputs in the same format as dpinger.
# You can connect to it by changing the 'sockpath' variable in 'statusb_mon.py' to point to this test socket.
#
# Run script with '[pythonexe] pseudosock.py [ up, down, updown, off, on, steady {percent}, flat {percent}, {percent} ]
# example on pfSense: python3.7 pseudosock.py updown

import argparse
import logging
import os
import random
import socket


logging.basicConfig(format='%(levelname)s:\t%(message)s', level=logging.INFO)

parser = argparse.ArgumentParser(
    description='This script creates a unix socket file with simulated output similar to dpinger socket')
parser.add_argument('pattern', nargs='+', type=str,
                    help='up, down, updown, off, on, steady {percent}, flat {percent}, {percent}')
parser.add_argument('-s', '--sockfile', default='/var/run/pseudosock.sock', type=str,
                    help='Socket file to create (defaults to /var/run/pseudosock.sock')
args = parser.parse_args()
if args.sockfile:
    sockfile = args.sockfile
else:
    sockfile = '/var/run/pseudosock.sock'


if args.pattern:
    logging.debug('pattern called')
    if isinstance(args.pattern, str):
        logging.debug('string')
        arg = args.pattern
        sarg = None
        logging.info(arg)
    elif isinstance(args.pattern, list):
        logging.debug(f'list {args.pattern}')
        arg = str(args.pattern[0])
        sarg = None
        if ((arg == 'steady') or (arg == 'flat')):
            logging.debug('steadyflat?')
            sarg = 50
            if (len(args.pattern) == 2):
                sarg = int(args.pattern[1])
    else:
        raise SystemExit('Invalid arguments.\nValid options [ up, down, updown, off, on, steady {percent}, flat {percent}, {percent} ]')

# def eprint(*args, **kwargs):
#     print(*args, file=sys.stderr, **kwargs)

# Clean potentially stale sockfile
try:
    os.unlink(sockfile)
except OSError:
    if os.path.exists(sockfile):
        raise

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

logging.info(f'starting up on {sockfile}')

sock.bind(sockfile)
sock.listen(1)
count = 0


# Generator for testing against loss trends
def downgen(pattern: str = 'updown', perc: int = None):
    logging.debug(f'pattern = {pattern}, perc = {perc}')
    if (perc is not None):
        title = f'{pattern} {str(perc)}'
    else:
        title = pattern
    logging.info('----------------')
    logging.info(title)
    logging.info('----------------')
    # I know. I also don't care.
    # OUTPUT: Invalid argument (updown).
    if (pattern == 'updown'):
        # UP
        logging.debug('UPDOWN')
        logging.info('----------------')
        logging.info('TREND UP')
        logging.info('----------------')
        stp = 100
        stpm = stp - 5
        retvar = 100
        while (retvar > 0):
            retvar = stp = random.randint(stpm, stp)
            stpm = stp - 5
            if (retvar < 0):
                yield (0)
            else:
                yield (retvar)
        logging.info('----------------')
        logging.info('15 at 0')
        logging.info('----------------')
        for i in range(0, 15):
            yield (0)

        # DOWN
        logging.info('----------------')
        logging.info('TREND DN')
        logging.info('----------------')
        stp = 0
        stpm = stp + 5
        retvar = 0
        while (retvar < 100):
            retvar = stp = random.randint(stp, stpm)
            stpm = stp + 5
            if (retvar > 100):
                yield (100)
            else:
                yield (retvar)
        logging.info('----------------')
        logging.info('15 at 100')
        logging.info('----------------')
        for i in range(0, 15):
            yield (100)

    if (pattern == 'down'):
        logging.debug('DOWN')
        stp = 0
        stpm = stp + 5
        retvar = 0
        while (retvar < 100):
            retvar = stp = random.randint(stp, stpm)
            stpm = stp + 5
            if (retvar > 100):
                yield (100)
            else:
                yield (retvar)
    elif (pattern == 'up'):
        logging.debug('UP')
        stp = 100
        stpm = stp - 5
        retvar = 100
        while (retvar > 0):
            retvar = stp = random.randint(stpm, stp)
            stpm = stp - 5
            if (retvar < 0):
                yield (0)
            else:
                yield (retvar)
    elif (pattern == 'steady'):
        logging.debug('STEADY')
        stp = perc
        while True:
            choice = random.choice([1, -1, 0, 0])
            retvar = stp + choice
            if (retvar > 0 or retvar < 100):
                yield (retvar)
            elif (retvar > 100):
                yield (100)
            elif (retvar < 0):
                yield (0)
    elif (pattern.isnumeric()):
        logging.debug('ISNUMERIC')
        yield (int(pattern))
    else:
        # this seems to fix weird exit with 'updown'
        yield (100)


while True:
    logging.info('Waiting for connection')
    logging.debug(f'arg = {arg}, sarg = {sarg}')
    while True:
        for loss in downgen(arg, sarg):
            count = count + 1
            try:
                connection, client = sock.accept()
                # eprint(f'connection from {client}')
                # WAN_DHCP 1168 613 0
                message = f'WAN_DHCP 1234 567 {loss}'
                # eprint(f'sending {message}')
                logging.info(f'loss: {loss} ({count})')
                connection.sendall(message.encode())
                connection.close()

            except BrokenPipeError as msg:
                logging.warning(f'Broken Pipe\n{msg}')
                continue
            finally:
                os.unlink(sockfile)
                logging.info(f'cleaning up {sockfile}')