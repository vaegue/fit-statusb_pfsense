Dirty hack. Work in progress. _don't hurt me, I'm learning._<br />
Hopefully the start of a working [fit-statusb](https://fit-iot.com/web/product/fit-statusb/) plugin(ish) for pfSense.

This is the first time I've interacted with FreeBSD ports. I may have done something horribly wrong.
Use this at your own risk.

The script currently sort of functions (pfSense 2.4.5), but it is ugly.
- Starts by itself, but system can't seem to shut it down or restart
- UI non-functional (WIP I suck at php)
- User has to either clone it into pfSense's FreeBSD-ports or manually place the files for now
    - On FreeBSD dev box
        - `git clone https://github.com/pfsense/FreeBSD-ports.git`
        - `cd {PFS_FBSD_PORTD_DIR}/sysutils/`
        - `git clone https://github.com/vaegue/fit-statusb_pfsense.git pfSense-pkg-statusb_mon`
        - `cd pfSense-pkg-statusb_mon`
        - `git checkout plugin`
        - `make package`
        - `scp work/pkg/pfSense-pkg-statusb_mon* root@{firewall_ip}:/root`
    - On Firewall
        - `pkg add pfSense-pkg-statusb_mon*.txz`
    
- no graceful error handling (good LUCK!)
- requires pyserial, which should be pulled in as a dependancy
- requires dpinger, which is installed on pfSense by default, but should also be pulled in as a dependancy if you aren't using this on pfSense