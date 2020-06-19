#!/usr/local/bin/python3.7

# Monitor and control script to utilize fit-statusb device on pfSense.
# Initially to monitor 'loss' from dpinger, and give simple visual
# indiciator of WAN status.
#
# fit-statusb is a very inexpensive ($9~$12) RGB LED 'blinker' that
# can be controlled by sending simple commands to a serial port.
# fit-statusb can be found at https://fit-iot.com/web/product/fit-statusb/

import os
import time
import socket
import glob

import serial

# define serial device.
# TODO: find out what pfsense does if serial console is enabled
# TODO: make configurable?
serialdev = '/dev/cuaU0'

# Path to dpinger socket file
# TODO: What to do about multiple WANs?
sockpath = glob.glob('/var/run/dpinger_WAN_DHCP*.sock')

pollinterval = 1

while True:
    time.sleep(pollinterval)
    if os.path.exists(sockpath[0]):
        sock_con = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    else:
        msg = f'Could not connect to {sockpath[0]}'
        print(msg)
        raise SystemExit(msg)

    try:
        sock_con.connect(sockpath[0])
        while True:
            sockdata = sock_con.recv(64)
            if sockdata:
                # {gw_name} {lat_ave} {lat_std_dev} {loss}
                # WAN_DHCP 1168 613 0
                # b'WAN_DHCP 1168 613 0\n'
                dping_res = dict(zip(('gw', 'lat_ave', 'stdev', 'loss'), sockdata.decode().split()))
                # TODO: do something. remove test print
                for k in dping_res:
                    print(f'{k}: {dping_res[k]}')
            else:
                # No data, move along
                break

    except socket.error as msg:
        print(f'Socket error:\n\t{msg}')

    finally:
        sock_con.close()