#!/bin/sh
# PROTOTYPE: script to manipulate fit-statusb usb led on pfSense
# #dirtyhack
# some code jacked from "/var/db/rrd/updaterrd.sh" on pfSense
# TODO:
#   Figure out where how to start this 'gracefully' on pfsense
#   Save some kind of stat to avoid re-sending same command

# This may collide with serial port used to access console over serial.
# Don't have hardware to check.
$serial=/dev/cuaU0

$red=FF0000
$green=00FF00
$blue=0000FF
$off=000000
$white=FFFFFF

echo "#000000" > $serial
while true; do
        sleep 5
        # This loop won't work well if there are two gateways (might include ipv4/6)
        for sock in /var/run/dpinger_*.sock; do
                echo "entering loop"
        #       sock=$(/var/run/dpinger_*.sock)

                if [ ! -S "$sock" ]; then
                        echo "no-s: $sock"
                        echo "B#ff0000-0100#ffff00" > $serial
                        continue
                fi

                t=$(/usr/bin/nc -U $sock)

                if [ -z "$t" ]; then
                        echo "-z $t"
                        continue
                fi

                loss=$(echo "$t" | awk '{ print $4 }')

                echo "setloss: $loss"
                if echo "$loss" | grep -Eqv '^[0-9]+$'; then
                        loss="U"
                        echo "#ffff00" > $serial
                else
                        echo "Loss: $loss"
                        if [ $loss -lt 10 ]; then
                                echo "#00ff00" > $serial
                        else
                                echo "#ff0000" > $serial
                        fi
                fi
        done

done
