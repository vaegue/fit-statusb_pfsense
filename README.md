Dirty hack. Work in progress. _don't hurt me, I'm learning._<br />
Hopefully the start of a working [fit-statusb](https://fit-iot.com/web/product/fit-statusb/) plugin(ish) for pfSense.

This is the first time I've interacted with FreeBSD ports. I may have done something horribly wrong.
Use this at your own risk.

The script currently sort of functions (pfSense 2.4.5), but it is ugly.
- Seems to start and stop correctly (needs more testing)
- Minimal UI (enable/disable service and service with logging /var/log/statusb_mon.log)
- User has to either clone it into pfSense's FreeBSD-ports or manually place the files for now
    - On FreeBSD dev box
        - `git clone https://github.com/pfsense/FreeBSD-ports.git`
        - `cd {PFS_FBSD_PORTS_DIR}/sysutils/`
        - `git clone https://github.com/vaegue/fit-statusb_pfsense.git pfSense-pkg-statusb_mon`
        - `cd pfSense-pkg-statusb_mon`
        - `make package`
        - `scp work/pkg/pfSense-pkg-statusb_mon* root@{firewall_ip}:/root`
    - On Firewall
        - requires pyserial, `pkg install py37-serial`
        - `pkg add pfSense-pkg-statusb_mon*.txz`
    
- no graceful error handling (good LUCK!)
- pulling dependancies isn't working
- requires dpinger, which is installed on pfSense by default, ~~but should also be pulled in as a dependancy if you aren't using this on pfSense~~