#!/usr/bin/env python3.7
#
# create pseudo-socket to send specific data to statusb_mon for testing
# This script is for testing the main 'statusb_mon.py' with consistent, predictable patterns of ping loss
# it creates a unix socket (./sock_test.sock) that outputs in the same format as dpinger.
# You can connect to it by changing the 'sockpath' variable in 'statusb_mon.py' to point to this test socket.
#
# Run script with '[pythonexe] pseudosock.py [ up, down, updown, off, on, steady {percent}, flat {percent}, {percent} ]
# example on pfSense: python3.7 pseudosock.py updown

import socket
import sys
import os
import random

if (len(sys.argv) >= 2):
    arg = sys.argv[1]
    sarg = None
    print(arg)
    if (arg is ('steady' or 'flat')):
        sarg = 50
        if (len(sys.argv) == 3):
            sarg = int(sys.argv[2])
else:
    raise SystemExit('Invalid arguments.\n Valid options [ up, down, updown, off, on, steady {percent}, flat {percent}, {percent} ]')

sockfile = './sock_test.sock'


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


try:
    os.unlink(sockfile)
except OSError:
    if os.path.exists(sockfile):
        raise

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

eprint(f'starting up on {sockfile}')

sock.bind(sockfile)
sock.listen(1)
count = 0


# Generator for testing against loss trends
def downgen(pattern: str = 'updown', perc: int = None):
    if (perc is not None):
        title = f'{pattern} {str(perc)}'
    else:
        title = pattern
    print(f'----------------\n{title}\n----------------')
    # I know. I also don't care.
    # OUTPUT: Invalid argument (updown).
    if (pattern == 'updown'):
        # UP
        print('----------------\nTREND UP\n----------------')
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

        print('----------------\n15 at 0\n----------------')
        for i in range(0, 15):
            yield (0)

        # DOWN
        print('----------------\nTREND DN\n----------------')
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

    print('----------------\n15 at 100\n----------------')
    for i in range(0, 15):
        yield (100)

    if (pattern == 'down'):
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
        yield (int(pattern))
    else:
        # this seems to fix weird exit with 'updown'
        yield (100)


try:
    while True:
        eprint('Waiting for connection')
        while True:
            for loss in downgen(arg, sarg):
                count = count + 1

                connection, client = sock.accept()
                # eprint(f'connection from {client}')
                # WAN_DHCP 1168 613 0
                message = f'WAN_DHCP 1234 567 {loss}'
                # eprint(f'sending {message}')
                eprint(f'loss: {loss} ({count})')
                connection.sendall(message.encode())
                connection.close()
finally:
    os.unlink(sockfile)
    print(f'cleaning up {sockfile}')