#!/bin/sh
# prototype. needs revision and cleanup
# TODO:
#   Figure out where how to start this 'gracefully' on pfsense

echo "#000000" > /dev/cuaU0
while true; do
        sleep 5
        for sock in /var/run/dpinger_*.sock; do
                echo "entering loop"
        #       sock=$(/var/run/dpinger_*.sock)

                if [ ! -S "$sock" ]; then
                        echo "no-s: $sock"
                        echo "B#ff0000-0100#ffff00" > /dev/cuaU0
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
                        echo "#ffff00" > /dev/cuaU0
                else
                        echo "Loss: $loss"
                        if [ $loss -lt 10 ]; then
                                echo "#00ff00" > /dev/cuaU0
                        else
                                echo "#ff0000" > /dev/cuaU0
                        fi
                fi
        done

done
