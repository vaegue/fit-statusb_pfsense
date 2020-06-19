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

pass
