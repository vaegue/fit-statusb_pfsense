Dirty hack. Work in progress.

Hopefully the start of a working [fit-statusb](https://fit-iot.com/web/product/fit-statusb/) plugin(ish) for pfSense.

This currently functions, but it is ugly.<br>
- no graceful start
- still sends command to serial device every second, whether the color needs to change or not
- requires `pkg install py37-serial`