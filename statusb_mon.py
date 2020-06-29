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
# TODO: logging?
# TODO: find out what pfsense does if serial console is enabled
# TODO: make configurable?
# TODO: handle more than one fit device (need to buy another one)
serialdev = '/dev/cuaU0'
serialargs = dict(
    port=serialdev,
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1
)

pulse = str('100')
# Purely for ease of typing
red = '#FF0000'
green = '#00FF00'
blue = '#0000FF'
yellow = '#FF4100'
orange = '#E00A00'
black = '#000000'
white = '#FFFFFF'
teal = '#00903F'
fuscia = '#FF0044'
purple = '#700070'

colorcode = dict(
    down=f'B{orange}-{pulse}{red}',
    up=f'B{orange}-{pulse}{green}',
    steady=f'B{orange}-{pulse}{yellow}'
)

# Some defaults
pollinterval = 1
duration = 1000
sockcon = None
# Startup assuming 100 percent loss
prev_loss = 100
diff_log = []

# Path to dpinger socket file
# TODO: What to do about multiple WANs?
# TODO: What if gateway changes?
sockpath = glob.glob('/var/run/dpinger_WAN_DHCP*.sock')


# Forgive me. I'm learning =)
class FitStatUSB:
    def __init__(self, ttyargs: dict, fade_dur: int = 1000):
        self.ttyargs = ttyargs
        self.cmd = None
        self.cmdstring = None
        self.color = None
        self.dur = None
        self.ser = None
        self.fit_id = None
        self.setfade(fade_dur)

    def getcolor(self):
        # TODO: get color from device 'G' command
        # This returns the last color that was SENT to the device.
        # This has no clue what the device is actually set to.
        return(self.color)

    def getid(self):
        # TODO: get ID from device '?' command
        # Could be useful if there are more than one fit devices, or to make sure
        # we don't interface with some other device that might have wound up on
        # the port we think the fit device is on.
        self.fit_id = "123dummy123"
        return(self.fit_id)

    def setcolor(self, color: str):
        if (color == self.color):
            return
        else:
            self.color = color
            self.sendcmd(color)
            return

    def sendcmd(self, cmd: str):
        self.cmd = cmd
        self.cmdstring = self.cmd+'\n'
        # Setup serial connection
        self.ser = serial.Serial()
        self.ser.port = self.ttyargs['port']
        self.ser.parity = self.ttyargs['parity']
        self.ser.baudrate = self.ttyargs['baudrate']
        self.ser.stopbits = self.ttyargs['stopbits']
        self.ser.timeout = self.ttyargs['timeout']
        self.ser.open()
        # Send binary of command string
        self.ser.write(self.cmdstring.encode())
        # flush for stability
        self.ser.flush()
        print(f'Sending command: {self.cmdstring}')
        # This seems to clear the input buffer so it doesn't freeze up
        self.ser.read_all()
        self.ser.close()
        return

    def setfade(self, dur: int):
        self.dur = 'F'+str(dur)
        self.sendcmd(self.dur)
        print(f'setfade: {self.dur}')
        return


count = 0
fit = FitStatUSB(serialargs, duration)


while True:
    time.sleep(pollinterval)

    # This try doesn't 'feel' right
    try:
        if os.path.exists(sockpath[0]):
            sockcon = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            # print(f'connecting to: {sockpath[0]}')
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
                cur_diff = []
                count = count + 1

                if (dping_loss > 0):
                    print(f"loss: {dping_res['loss']}, count: {count}")

                # fixme: smooth this out using cur_diff, diff_log
                cur_diff = prev_loss - dping_loss

                if (cur_diff > 0):
                    fit.setcolor(colorcode['up'])
                elif (cur_diff < 0):
                    fit.setcolor(colorcode['down'])
                elif (cur_diff == 0 and dping_loss == 0):
                    fit.setcolor(green)
                elif (cur_diff == 0 and dping_loss == 100):
                    fit.setcolor(red)
                elif (cur_diff == 0 and dping_loss != (0 or 100)):
                    fit.setcolor(colorcode['steady'])
                # print(f'Color: {fit.getcolor()}')
                # print(f'Count: {count}')
                prev_loss = dping_loss
                diff_log.append(cur_diff)
                if (len(diff_log) > 5):
                    diff_log.pop(0)

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
