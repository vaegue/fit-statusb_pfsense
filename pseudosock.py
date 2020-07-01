# create pseudo-socket to send specific data to statusb_mon for testing

import socket
import sys
import os
import random

if (len(sys.argv) == 2):
    arg = sys.argv[1]
elif (len(sys.argv) < 2):
    raise SystemExit(f'No arguments.\n Valid options [ up, down, updown, steady, off, on, 50 ]')
else:
    raise SystemExit(f'Invalid number of args ({len(sys.argv)-1}).\n Valid options [ up, down, updown, steady, off, on, 50 ]')

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
def downgen(pattern: str = '50'):
    print(f'----------------\n{pattern}\n----------------')
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
        stpm = stp+5
        retvar = 0
        while (retvar < 100):
            retvar = stp = random.randint(stp, stpm)
            stpm = stp+5
            if (retvar > 100):
                yield(100)
            else:
                yield(retvar)
    elif (pattern == 'up'):
        stp = 100
        stpm = stp - 5
        retvar = 100
        while (retvar > 0):
            retvar = stp = random.randint(stpm, stp)
            stpm = stp - 5
            if (retvar < 0):
                yield(0)
            else:
                yield(retvar)
    elif (pattern == 'steady'):
        stp = 50
        while True:
            choice = random.choice([1, -1, 0, 0])
            retvar = stp + choice
            if (retvar > 0 or retvar < 100):
                yield(retvar)
            elif (retvar > 100):
                yield(100)
            elif (retvar < 0):
                yield(0)
    elif (pattern == 'off'):
        while True:
            yield(100)
    elif (pattern == 'on'):
        while True:
            yield(0)
    elif (pattern == '50'):
        while True:
            yield(50)
    else:
        # this seems to fix weird exit with 'updown'
        yield(100)


while True:
    eprint('Waiting for connection')
    while True:

        for loss in downgen(arg):
            count = count + 1

            connection, client = sock.accept()
            # eprint(f'connection from {client}')
            # WAN_DHCP 1168 613 0
            message = f'WAN_DHCP 1234 567 {loss}'
            # eprint(f'sending {message}')
            eprint(f'loss: {loss} ({count})')
            connection.sendall(message.encode())
            connection.close()
