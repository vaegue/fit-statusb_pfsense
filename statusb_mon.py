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
# TODO: handle more than one fit device (need to buy another one)
serialdev = '/dev/cuaU0'
serialargs = dict(
    port=serialdev,
    baudrate=9600,
    parity=serial.PARITY_EVEN,
    timeout=1
)
# Path to dpinger socket file
# TODO: What to do about multiple WANs?
sockpath = glob.glob('/var/run/dpinger_WAN_DHCP*.sock')

pollinterval = 1
sockcon = None


# Forgive me. I'm learning =)
class FitStatUSB:
    def __init__(self, ttyargs):
        self.ttyargs = ttyargs
        self.color = None
        self.colorstring = None
        self.ser = None

    def getcolor(self):
        return self.color

    def setcolor(self, color):
        if (color == self.color):
            # print("no change")
            return
        else:
            self.color = color
            self.colorstring = self.color+'\n'
            # Setup serial connection
            self.ser = serial.Serial()
            self.ser.port = self.ttyargs['port']
            self.ser.parity = self.ttyargs['parity']
            self.ser.baudrate = self.ttyargs['baudrate']
            self.ser.timeout = self.ttyargs['timeout']
            self.ser.open()
            # Send binary of command string
            self.ser.write(self.colorstring.encode())
            print(f'Changing color to: {self.colorstring}')
            # This seems to clear the input buffer so it doesn't freeze up
            self.ser.read_all()
            self.ser.close()
            return


count = 0
fit = FitStatUSB(serialargs)

while True:
    time.sleep(pollinterval)

    # This try doesn't 'feel' right
    try:
        if os.path.exists(sockpath[0]):
            sockcon = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sockcon.connect(sockpath[0])
        else:
            print(f'Could not connect to {sockpath[0]}')
            continue

        while True:
            sockdata = sockcon.recv(64)
            if sockdata:
                # {gw_name} {lat_ave} {lat_std_dev} {loss}
                # WAN_DHCP 1168 613 0
                # b'WAN_DHCP 1168 613 0\n'
                dping_res = dict(zip(('gw', 'lat_ave', 'stdev', 'loss'), sockdata.decode().split()))
                # We only really care about loss for now
                dping_loss = int(dping_res['loss'])
                if(dping_loss > 0):
                    print(f"loss: {dping_res['loss']}")

                # TODO: check trend and react accordingly
                if (dping_loss == 0):
                    fit.setcolor('#00ff00')
                elif(1 < dping_loss <= 10):
                    fit.setcolor('#da1600')
                elif(10 < dping_loss <= 30):
                    fit.setcolor('#da0800')
                elif(dping_loss > 30):
                    fit.setcolor('#ff0000')
                else:
                    fit.setcolor('#0000ff')
                count = count + 1
                # print(f'Color: {fit.getcolor()}')
                # print(f'Count: {count}')
            else:
                # No data, move along
                break

    # Just catch it all for now.
    except Exception as msg:
        if hasattr(msg, 'message'):
            print(msg.message)
            continue
        else:
            print(msg)
            continue
    finally:
        if(sockcon):
            sockcon.close()
