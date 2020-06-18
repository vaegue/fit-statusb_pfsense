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
        print("Trying to connect")
        client.connect(sockpath[0])

        while True:
            print("receiving...")
            data = client.recv(32)
            if data:
                # print(f'received: {}'.format(data))
                print(len(data))
                print(data)
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

