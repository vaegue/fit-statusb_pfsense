#!/bin/sh
# junk

ser=/dev/ttyACM0

set_color() {
    inarg=$1
    echo "$inarg to led"
    echo "$inarg" > $ser
}

curcolor="#ff0000"
set_color "$curcolor"

counter=0
while true; do
    if [ ! -c "$ser" ]; then
        continue
    fi

    #sleep 5

    if [ "$curcolor" = "#00ff00" ]; then
        set_color "#ff0000"
        curcolor="#ff0000"
    elif [ "$curcolor" = "#ff0000" ]; then
        set_color "#0000ff"
        curcolor="#0000ff"
    elif [ "$curcolor" = "#0000ff" ]; then
        set_color "#00ff00"
        curcolor="#00ff00"
    fi
    echo "$counter"
    counter=$((counter+1))
done
