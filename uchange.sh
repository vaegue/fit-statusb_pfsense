#!/bin/sh
# PROTOTYPE: script to manipulate fit-statusb usb led on pfSense
# #dirtyhack
# some code jacked from "/var/db/rrd/updaterrd.sh" on pfSense
# TODO:
#   Figure out where how to start this 'gracefully' on pfsense
#   Save some kind of stat to avoid re-sending same command
#   find way to purge input buffer to prevent freezing ~763 commands in

# This may collide with serial port used to access console over serial.
# Don't have hardware to check.
serial=/dev/cuaU0

red="#FF0000"
green="#00FF00"
blue="#0000FF"
off="#000000"
white="#FFFFFF"

set_color() {
        inarg=$1
        echo "$inarg to led"
        echo "$inarg" > $serial
}

while true; do
        if [ ! -c "$serial" ]; then
                continue
        fi

        sleep 5
        # This loop won't work well if there are two gateways (might include ipv4/6)
        for sock in /var/run/dpinger_*.sock; do
                echo "entering loop"
        #       sock=$(/var/run/dpinger_*.sock)

                # Is the dpinger file there and a socket?
                if [ ! -S "$sock" ]; then
                        echo "no dpinger file: $sock"
                        set_color "B#$white-0100#ffff00"
                        continue
                fi

                t=$(/usr/bin/nc -U $sock)

                # Nothing in the socket, move along.
                if [ -z "$t" ]; then
                        echo "nothing in socket $t"
                        continue
                fi

                loss=$(echo "$t" | awk '{ print $4 }')

                # is loss a number?
                if echo "$loss" | grep -Eqv '^[0-9]+$'; then
                        loss="U"
                        set_color "B#ffff00-0100#00ffff"
                else
                        echo "Loss: $loss"
                        if [ "$loss" -lt 10 ]; then
                                set_color "$green"
                        else
                                set_color "$red"
                        fi
                fi
        done

done
