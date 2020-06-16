#!/usr/bin/env python3

# Initial Python 3 version, now using UDP
# Remember to change remote monitor to UDP on 192.168.0.20
# Fails on encode line (but still runs on Python 2)

import socket
import time
import sys

HOST = ''
PORT = 5433
max_bind_count = 20
get_try_count = 90

s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
print('Socket created')
sys.stdout.flush()

#Bind socket to local host and port
bind_count = 0
while bind_count < max_bind_count:
    try:
        s.bind((HOST, PORT))
        break
    except socket.error as msg:
        print(time.strftime("%c ") + 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1])
        sys.stdout.flush()
        time.sleep(10.0)
        bind_count += 1

if bind_count == max_bind_count:
    print(time.strftime("%c ") + 'Too many bind failures - exiting script')
    sys.exit()
     
print('Socket bind complete')
sys.stdout.flush()
 
# Now keep talking with the client but stop after a given number of goes
# (something hangs after 600-odd)
msg_count = 0
while msg_count < get_try_count:
    #wait to accept a connection - blocking call
    buf, addr = s.recvfrom(1024)
    print(time.strftime("%c %s "))
    # Python 2
    # print(str(':'.join(b.encode('hex') for b in buf)))
    # Python 3
    print("".join(":{:02x}".format(x) for x in buf)[1:])
    sys.stdout.flush()
    addr = None
    msg_count += 1
     
s.close()
