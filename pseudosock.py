# create pseudo-socket to send specific data to statusb_mon for testing

import socket
import sys
import os

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

while True:
    eprint('Waiting for connection')
    while True:
        count = count + 1
        connection, client = sock.accept()
        eprint(f'connection from {client}')
        # WAN_DHCP 1168 613 0
        message = b'WAN_DHCP 1234 567 90'
        eprint(f'sending {message.decode()}')
        connection.sendall(message)
        connection.close()
        eprint(f'cnt: {count}')
