#!/usr/bin/env python3.7
#
# statusb_mon.py v%%PKGVERSION%%
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

import argparse
import glob
import logging
import os
import socket
import time
from collections import deque
from signal import signal, SIGINT

import serial

__version__ = "%%PKGVERSION%%"

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--loglevel', help='set logging.level (debug, info ...)', type=str)
parser.add_argument('-f', '--logfile', help='logfile', type=str)
parser.add_argument('-s', '--socketfile', help='socket file to poll for info', type=str)
parser.add_argument('-d', '--device', help='serial device (default: /dev/cuaU0)', type=str)
parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')
args = parser.parse_args()
if args.loglevel:
    logpart = args.loglevel
    # print(f'Loglevel set to {logpart.upper()}')
else:
    logpart = 'ERROR'

num_loglevel = getattr(logging, logpart.upper(), None)
if not isinstance(num_loglevel, int):
    raise ValueError(f'Invalid log level: {logpart.upper()}')

if args.logfile:
    logging.basicConfig(format='%(levelname)s:\t%(message)s', level=num_loglevel, filename=args.logfile)
    logging.info(f'logging {logpart.upper()} to logfile: {args.logfile}')
else:
    logging.basicConfig(format='%(levelname)s:\t%(message)s', level=num_loglevel)
    logging.info(f'Showing output at {logpart.upper()} or higher.')

logging.info(time.strftime('%c', time.gmtime()))

# define serial device.
if args.device:
    if os.path.exists(args.device):
        serialdev = args.device
    else:
        logging.warning(f'Could not find serial device: {args.device}')
        raise SystemExit(1)
else:
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
    steady=f'B{teal}-{pulse}{yellow}',
    end=f'B{blue}-{pulse}{purple}'
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

reset_on_loop = None


def sighandler(sig_received, frame):
    if os.path.exists(pidfile):
        logging.info(f'\n---\nSignal {sig_received} received. Shutting down.\n---\n')
        if os.path.exists(pidfile):
            os.unlink(pidfile)
            logging.info(f'Removing pidfile: {pidfile}\n')
    raise SystemExit(0)


signal(SIGINT, sighandler)

pid = str(os.getpid())
pidfile = '/var/run/statusb_mon.pid'

try:
    open(pidfile, 'w').write(pid)
except Exception as msg:
    logging.warning(f'Cannot open pid file: {pidfile}\n\t{msg}')
    raise SystemExit(1)

# TODO: What to do about multiple WANs?
# TODO: What if gateway changes?

# Try using user-supplied socket file. If that doesn't exist, try psuedosock file (created by the pseudosock test script
# If neither of those work out. Search for dpinger socket.
if args.socketfile:
    sockpath = [args.socketfile]
    if os.path.exists(sockpath[0]):
        logging.info(f'Using user passed socket: {sockpath[0]}')
    else:
        logging.warning(f'socket ({sockpath[0]}) does not exist.')
elif os.path.exists('/var/run/pseudosock.sock'):
    sockpath = ['/var/run/pseudosock.sock']
    logging.info(f'using debug/test socket {sockpath[0]}')
else:
    sockpath = glob.glob('/var/run/dpinger_WAN_DHCP*.sock')
    logging.info(f'Found dpinger socket: {sockpath[0]}')


# TODO: add initial debug dump 'somewhere'

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
        return self.color

    def getid(self):
        # TODO: get ID from device '?' command
        # Could be useful if there are more than one fit devices, or to make sure
        # we don't interface with some other device that might have wound up on
        # the port we think the fit device is on.
        self.fit_id = "123dummy123"
        return self.fit_id

    def setcolor(self, color: str):
        logging.info(f'Setcolor: {color}')
        self.color = color
        try:
            self.sendcmd(color)
        except ValueError:
            logging.warning(f'Unable to set color: {color} on {self.ttyargs["port"]}')
            raise ValueError
            # return(1)
        return 0

    def pulse(self):
        # This doesn't actually pulse the LED. it sets the LED without manipulatig cur_color so it gets set right back
        # to cur_color in the main loop.
        # cur_color = self.getcolor()

        try:
            self.setcolor(purple)
            # time.sleep(2)
            # self.setcolor(cur_color)
        except Exception as msg:
            logging.warning(f'Unable to pulse LED.\n{msg}')
            raise ValueError
        return 0

    def sendcmd(self, cmd: str):
        self.cmd = cmd
        self.cmdstring = self.cmd + '\n'
        # Setup serial connection
        self.ser = serial.Serial()
        if os.path.exists(self.ttyargs['port']):
            self.ser.port = self.ttyargs['port']
        else:
            logging.warning(f'Serial port not found: {self.ttyargs["port"]}')
            raise ValueError
        self.ser.parity = self.ttyargs['parity']
        self.ser.baudrate = self.ttyargs['baudrate']
        self.ser.stopbits = self.ttyargs['stopbits']
        self.ser.timeout = self.ttyargs['timeout']
        try:
            self.ser.open()
        except Exception as emsg:
            logging.warning(f'Could not open serial port: {self.ttyargs["port"]}\n{emsg}')
            raise ValueError
        # Send binary of command string
        self.ser.write(self.cmdstring.encode())
        # flush for stability
        self.ser.flush()
        logging.debug(f'Sending command: {self.cmdstring.strip()}')
        # This seems to clear the input buffer so it doesn't freeze up
        self.ser.read_all()
        self.ser.close()
        return 0

    def setfade(self, dur: int):
        self.dur = 'F' + str(dur)
        self.sendcmd(self.dur)
        logging.debug(f'setfade: {self.dur}')
        return 0


count = 0
fit = FitStatUSB(serialargs, duration)

try:
    while True:
        time.sleep(pollinterval)
        logging.debug(f' - SLEEP ({pollinterval})')

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
                    if len(diff_log) > 6:
                        diff_log.popleft()

                    ave_diff = sum(diff_log) / len(diff_log)
                    logging.debug(f'Count: {count}')

                    # Send purple to the LED for a short time for visual verification it's still working during debug
                    if str(logpart.lower()) == 'debug':
                        if (str(count)[-1] == '0') and (logpart.lower() == 'debug'):
                            logging.debug(f'PULSE: {count} - {duration}')
                            fit.pulse()
                            time.sleep(1)
                            logging.debug(f' - SLEEP (1)')

                    if dping_loss > 0:
                        msg = f"loss: {dping_res['loss']}\tcur_diff: {cur_diff}\tave_diff: {ave_diff} ({count})"
                        logging.info(msg)

                    setcolor = None
                    if ave_diff >= sensitivity:
                        setcolor = colorseq['up']
                    elif ave_diff <= -sensitivity:
                        setcolor = colorseq['down']
                    elif (ave_diff == 0) and (dping_loss <= low_thresh):
                        setcolor = green
                    elif (ave_diff == 0) and (dping_loss >= high_thresh):
                        setcolor = red
                    elif ((-sensitivity < ave_diff < sensitivity) and (
                            dping_loss < high_thresh or dping_loss > low_thresh)):
                        setcolor = colorseq['steady']
                    else:  # Dunno!
                        msg = f'ave_diff: {ave_diff}\n' \
                              f'dping_loss: {dping_loss}\n' \
                              f'high_thresh: {high_thresh}\n' \
                              f'low_thresh: {low_thresh}'
                        logging.warning(f'======== CODE FUSCIA! ========\n{msg}')
                        setcolor = fuscia

                    if (setcolor != fit.getcolor()) or (reset_on_loop is True):
                        try:
                            fit.setcolor(setcolor)
                        except ValueError as msg:
                            logging.debug('Setting reset_on_loop to catch up serial device if it comes back.')
                            reset_on_loop = True

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
            if sockcon:
                logging.debug(f'Closing connection {sockpath}')
                sockcon.close()

except Exception as msg:
    if hasattr(msg, 'message'):
        logging.error(msg.message)
    else:
        logging.error(msg)
finally:
    if os.path.exists(pidfile):
        logging.info(f'\nRemoving pidfile: {pidfile}\n')
        os.unlink(pidfile)
    time.sleep(1)
    try:
        fit.setcolor(colorseq['end'])
    except Exception:
        logging.warning('Could not set exit color')
    raise SystemExit(0)
