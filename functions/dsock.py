# client.py
import socket

# create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# get local machine name
host = 'localhost'

port = 1995

# connection to hostname on the port.
s.connect((host, port))

# Receive no more than 1024 bytes
while True:
    data = s.recv(1024)
    if len(data) > 0:
        print data

s.close()
