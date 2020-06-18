import socket
import os

sockpath = "/var/run/dpinger_test.sock"
print("Connecting")
if os.path.exists(sockpath):
    client = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    client.connect(sockpath)
    print("connected")
else:
    print("couldn't connect")
