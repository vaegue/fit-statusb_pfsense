Dirty hack. Work in progress. _don't hurt me, I'm learning._<br>
Hopefully the start of a working [fit-statusb](https://fit-iot.com/web/product/fit-statusb/) plugin(ish) for pfSense.

This currently functions (pfSense 2.4.5), but it is ugly.
- up to user how to start it for now (still under development)
- git clone into ports, make package and transfer to firewall. install with `pkg add`
- no graceful error handling (good LUCK!)
- requires pyserial, which should be pulled in as a dependancy