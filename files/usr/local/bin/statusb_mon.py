#!/usr/local/bin/python3.7
#
# Monitor and control script to utilize fit-statusb device on pfSense.
# Initially to monitor 'loss' from dpinger, and give simple visual
# indiciator of WAN status.
#
# fit-statusb is a very inexpensive ($9~$12) RGB LED 'blinker' that
# can be controlled by sending simple commands to a serial port.
# fit-statusb can be found at https://fit-iot.com/web/product/fit-statusb/
#
# TODO: find out what pfsense does if serial console is enabled
# TODO: make configurable?
# TODO: handle more than one fit device (need to buy another one)

import os
import time
import socket
import glob
import logging
import argparse

from collections import deque

import serial

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--log', help='set logging.level (debug, info ...)', type=str)
args = parser.parse_args()
if args.log:
    logpart = args.log
    print(f'Loglevel set to {logpart.upper()}')
else:
    logpart = 'WARNING'

num_loglevel = getattr(logging, logpart.upper(), None)
if not isinstance(num_loglevel, int):
    raise ValueError(f'Invalid log level: {logpart.upper()}')

# TODO: logging to file?
logging.basicConfig(format='%(levelname)s:\t%(message)s', level=num_loglevel)

# define serial device.
serialdev = '/dev/cuaU0'
serialargs = dict(
    port=serialdev,
    baudrate=115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1
)

# fixme: organize these
pulse = '100'
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

colorseq = dict(
    down=f'B{yellow}-{pulse}{red}',
    up=f'B{yellow}-{pulse}{green}',
    steady=f'B{teal}-{pulse}{yellow}'
)

# Some defaults
pollinterval = 1
duration = 1000
sensitivity = .5
sockcon = None
# Startup assuming 100 percent loss
prev_loss = 100
diff_log = deque([])
ave_diff = 0
# Loss threshholds for full-up/down
# fixme: does not work as intended
high_thresh = 100
low_thresh = 0

pid = str(os.getpid())
pidfile = '/var/run/statusb_mon.pid'
try:
    open(pidfile, 'w').write(pid)
except Exception as msg:
    logging.warning(f'Cannot open pid file: {pidfile}\n\t{msg}')
    raise SystemExit

# Path to dpinger socket file
# TODO: What to do about multiple WANs?
# TODO: What if gateway changes?
if os.path.exists('./sock_test.sock'):
    sockpath = ['./sock_test.sock']
    logging.info(f'using debug/test socket {sockpath[0]}')
else:
    sockpath = glob.glob('/var/run/dpinger_WAN_DHCP*.sock')
    logging.info(f'Found dpinger socket: {sockpath[0]}')


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
        # Moved tihs check outside of class
        # if (color == self.color):
        #     return
        # else:
        logging.info(f'Setcolor: {color}')
        self.color = color
        self.sendcmd(color)
        return

    def sendcmd(self, cmd: str):
        self.cmd = cmd
        self.cmdstring = self.cmd+'\n'
        # Setup serial connection
        self.ser = serial.Serial()
        if os.path.exists(self.ttyargs['port']):
            self.ser.port = self.ttyargs['port']
        else:
            logging.warning(f'Serial port not found: {self.ttyargs["port"]}')
            return
        self.ser.parity = self.ttyargs['parity']
        self.ser.baudrate = self.ttyargs['baudrate']
        self.ser.stopbits = self.ttyargs['stopbits']
        self.ser.timeout = self.ttyargs['timeout']
        try:
            self.ser.open()
        except Exception as msg:
            logging.warning(f'Could not open serial port: {self.ttyargs["port"]}\n{msg}')
            return
        # Send binary of command string
        self.ser.write(self.cmdstring.encode())
        # flush for stability
        self.ser.flush()
        logging.debug(f'Sending command: {self.cmdstring.strip()}')
        # This seems to clear the input buffer so it doesn't freeze up
        self.ser.read_all()
        self.ser.close()
        return

    def setfade(self, dur: int):
        self.dur = 'F'+str(dur)
        self.sendcmd(self.dur)
        logging.debug(f'setfade: {self.dur}')
        return


count = 0
fit = FitStatUSB(serialargs, duration)

try:
    while True:
        time.sleep(pollinterval)

        # This try doesn't 'feel' right
        try:
            if os.path.exists(sockpath[0]):
                sockcon = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
                logging.debug(f'connecting to: {sockpath[0]}')
                sockcon.connect(sockpath[0])
            else:
                logging.error(f'Could not connect to {sockpath[0]}')
                continue

            while True:
                sockdata = sockcon.recv(64)
                if sockdata:
                    logging.debug(f'sockdata: {sockdata.decode()}')
                    # {gw_name} {lat_ave} {lat_std_dev} {loss}
                    # WAN_DHCP 1168 613 0
                    # b'WAN_DHCP 1168 613 0\n'
                    dping_res = dict(zip(('gw', 'lat_ave', 'stdev', 'loss'), sockdata.decode().split()))
                    # We only really care about loss for now
                    dping_loss = int(dping_res['loss'])
                    count = count + 1
                    cur_diff = prev_loss - dping_loss
                    prev_loss = dping_loss
                    diff_log.append(cur_diff)
                    if (len(diff_log) > 6):
                        diff_log.popleft()

                    ave_diff = sum(diff_log)/len(diff_log)
                    if (dping_loss > 0):
                        msg = f"loss: {dping_res['loss']}\tcur_diff: {cur_diff}\tave_diff: {ave_diff} ({count})"
                        logging.info(msg)

                    setcolor = None
                    if (ave_diff >= sensitivity):
                        setcolor = colorseq['up']
                    elif (ave_diff <= -sensitivity):
                        setcolor = colorseq['down']
                    elif ((ave_diff == 0) and (dping_loss <= low_thresh)):
                        setcolor = green
                    elif ((ave_diff == 0) and (dping_loss >= high_thresh)):
                        setcolor = red
                    elif ((-sensitivity < ave_diff < sensitivity) and (dping_loss < high_thresh or dping_loss > low_thresh)):
                        setcolor = colorseq['steady']
                    else:  # Dunno!
                        msg = f'ave_diff: {ave_diff}\n' \
                              f'dping_loss: {dping_loss}\n' \
                              f'high_thresh: {high_thresh}\n' \
                              f'low_thresh: {low_thresh}'
                        logging.warning(f'======== CODE FUSCIA! ========\n{msg}')
                        setcolor = fuscia

                    if (setcolor != fit.getcolor()):
                        fit.setcolor(setcolor)

                else:
                    # No data, move along
                    break

        # Just catch it all for now.
        except Exception as msg:
            if hasattr(msg, 'message'):
                logging.error(msg.message)
                continue
            else:
                logging.error(msg)
                continue
        finally:
            if(sockcon):
                logging.debug(f'Closing connection {sockpath}')
                sockcon.close()

except Exception as msg:
    if hasattr(msg, 'message'):
        logging.error(msg.message)
    else:
        logging.error(msg)
finally:
    logging.info(f'Removing pidfile: {pidfile}')
    os.unlink(pidfile)
