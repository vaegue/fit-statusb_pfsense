import socket
import os
import time
import glob

polltime = 1
sockpath = glob.glob('/var/run/dpinger_WAN_DHCP*.sock')

# sockpath = "/var/run/dpinger_test.sock"
print("Connecting")
while True:
    time.sleep(polltime)
    if os.path.exists(sockpath[0]):
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    else:
        print("couldn't connect")
        raise SystemExit("whatever")

    try:
        # print("Trying to connect")
        client.connect(sockpath[0])

        while True:
            # print("receiving...")
            data = client.recv(32)
            if data:
                # {gw_name} {lat_ave} {lat_std_dev} {loss}
                # WAN_DHCP 1168 613 0
                # b'WAN_DHCP 1168 613 0\n'
                result = dict(zip(('gw_name', 'lat_ave', 'stdev', 'loss'), data.decode().split()))
                for k in result:
                    print(f'{k}: {result[k]}')
            else:
                print("No data")
                break

    except socket.error as msg:
        print("UhOh")
        print(msg)
        raise SystemExit(1)
    finally:
        print("closing connection")
        client.close()

