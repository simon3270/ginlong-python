#!/usr/bin/env python3

# Initial Python 3 version
# Fails on encode line (but still runs on Python 2)

import socket
import time
import sys

HOST = ''
PORT = 5432
max_bind_count = 20
get_try_count = 45

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
 
#Start listening on socket
s.listen(10)
print(time.strftime("%c ") + 'Socket now listening')
sys.stdout.flush()
 
# Now keep talking with the client but stop after a given number of goes
# (something hangs after 600-odd)
conn_count = 0
while conn_count < get_try_count:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    print('Connected with ' + addr[0] + ':' + str(addr[1]))
    buf = conn.recv(1024)
    print(time.strftime("%c %s "))
    # Python 2
    # print(str(':'.join(b.encode('hex') for b in buf)))
    # Python 3
    print("".join(":{:02x}".format(x) for x in buf)[1:])
    sys.stdout.flush()
    conn = None
    addr = None
    conn_count += 1
     
s.close()
