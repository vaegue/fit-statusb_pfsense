# create pseudo-socket to send specific data to statusb_mon for testing
# This script is for testing the main 'statusb_mon.py' with consistent, predictable patterns of ping loss
# it creates a unix socket (./sock_test.sock) that outputs in the same format as dpinger.
# You can connect to it by changing the 'sockpath' variable in 'statusb_mon.py' to point to this test socket.
#
# Run script with '[pythonexe] pseudosock.py {up, down, updown, steady, off, on, 50}
# example on pfSense: python37 pseudosock.py updown

import socket
import sys
import os
import random

if (len(sys.argv) >= 2):
    arg = sys.argv[1]
    sarg = None
    if (arg == 'steady' or 'flat'):
        sarg = 50
        if (len(sys.argv) == 3):
            sarg = int(sys.argv[2])

else:
    raise SystemExit('Invalid arguments.\n Valid options [ up, down, updown, steady {percent}, flat {percent}, off, on, 50 ]')

host = './sock_test.sock'


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


try:
    os.unlink(host)
except OSError:
    if os.path.exists(host):
        raise

sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

eprint(f'starting up on {host}')

sock.bind(host)
sock.listen(1)
count = 0


# Generator for testing against loss trends
def downgen(pattern: str = '50', perc: int = 50):
    if (perc is not None):
        title = f'{pattern} {str(perc)}'
    else:
        title = pattern
    print(f'----------------\n{title}\n----------------')
    # I know. I also don't care.
    # fixme: after this cycles, it exits on 'else'
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
    elif (pattern == 'flat'):
        while True:
            yield(perc)
    elif (pattern == 'off'):
        while True:
            yield (100)
    elif (pattern == 'on'):
        while True:
            yield (0)
    elif (pattern == '50'):
        while True:
            yield (50)
    else:
        # this seems to fix weird exit with 'updown'
        yield (100)


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
