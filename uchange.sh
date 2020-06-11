#!/bin/sh
# prototype. needs revision and cleanup
# TODO:
#   Figure out where how to start this 'gracefully' on pfsense
$serial=/dev/cuaU0

echo "#000000" > $serial
while true; do
        sleep 5
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
