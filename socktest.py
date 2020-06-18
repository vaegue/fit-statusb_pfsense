import socket
import os
import time

sockpath = "/var/run/dpinger_test.sock"
print("Connecting")
while True:
    time.sleep(5)
    if os.path.exists(sockpath):
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    else:
        print("couldn't connect")
        raise SystemExit("whatever")

    try:
        print("Trying to connect")
        client.connect(sockpath)

        while True:
            print("receiving...")
            data = client.recv(32)
            if data:
        #        print(f'received: {}'.format(data))
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
   
