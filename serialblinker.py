# troubleshoot blinker freezing.
# turns out you have to manually clear the input buffer
# otherwise it seems to fill up and causes device to stop working until unplug/plug

import serial
import time

# Windows machine
# device = 'COM3'
# Linux machine
# device = '/dev/ttyACM0'
# FreeBSD
device = '/dev/cuaU0'
ser = serial.Serial(device, 9600, parity=serial.PARITY_EVEN, timeout=5)

# output = ser.read(100)
# print(curcolor)


def setcolor(incolor):
    # print(incolor+b'\n')
    ser.write(incolor+b'\n')
    # time.sleep(.1)
    # This seems to be the only reliable way to clear the input buffer
    # Probably because it's a usb->serial
    ser.read_all()
    return(incolor)

curcolor = setcolor(b'#ff0000')
counter = 0
maxinwait = 0
while 1:
    # time.sleep(5)
    time.sleep(.1)
    if (curcolor == b'#00ff00'):
        curcolor = setcolor(b'#ff0000')
    elif (curcolor == b'#ff0000'):
        curcolor = setcolor(b'#0000ff')
    elif (curcolor == b'#0000ff'):
        curcolor = setcolor(b'#00ff00')
    else:
        setcolor(b'B#ffff00-0001#ff00ff')
    
    counter = counter + 1
    # print('IN: {inw}, OUT: {outw}, MAXIN: {maxin} CNT: {cnt}'.format(inw=ser.in_waiting,maxin=maxinwait,
    #                                                                  outw=ser.out_waiting, cnt=counter))
    if (ser.in_waiting > 0):
        if (ser.in_waiting > maxinwait):
            maxinwait = ser.in_waiting

        print('IN: {inw}, OUT: {outw}, MAXIN: {maxin} CNT: {cnt}'.format(inw=ser.in_waiting, maxin=maxinwait,
                                                                         outw=ser.out_waiting, cnt=counter))
        print(ser.readline())
        print('IN: {inw}, OUT: {outw}, MAXIN: {maxin} CNT: {cnt}'.format(inw=ser.in_waiting, maxin=maxinwait,
                                                                         outw=ser.out_waiting, cnt=counter))
