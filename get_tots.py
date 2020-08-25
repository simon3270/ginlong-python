#!/usr/bin/env python3
# Reads solar log files as parameters, and gets the daily totals.
# Each ouput line has:
# Date, time of first entry, time of last entry, number of entries, daily total kwH

# Supports UDP and TCP data

import sys
import os
import time
import re
from datetime import date
import fileinput

# WiFi TCP has one message type, and reports TCP connection being made
# Socket created
# Socket bind complete
# Wed Sep  2 08:03:21 2015 Socket now listening
# Connected with 192.168.0.20:40007
# Wed Sep  2 08:05:50 2015 1441177550 
# 68:59:51:b0:7b:ec:3e:24:7b:ec:3e:24:81:01:05:30:30:30:36:30:38:31:30:33:35:34:37:2d:30:30:31:00:fc:07:87:09:56:00:00:00:30:00:2b:00:00:00:4e:00:00:00:00:09:7c:00:00:00:00:13:8a:07:65:00:00:00:00:00:0a:04:6a:00:78:00:00:62:98:00:00:00:00:00:00:00:00:be:36:04:01:00:0d:00:00:01:39:00:00:00:00:00:00:00:00:dd:16
# Connected with 192.168.0.20:47875
# Wed Sep  2 08:11:14 2015 1441177874 
# 68:59:51:b0:7b:ec:3e:24:7b:ec:3e:24:81:01:05:30:30:30:36:30:38:31:30:33:35:34:37:2d:30:30:31:01:07:07:ae:09:17:00:00:00:32:00:30:00:00:00:53:00:00:00:00:09:74:00:00:00:00:13:82:07:d8:00:00:00:00:00:0a:04:6a:00:8c:00:00:62:98:00:00:00:00:00:00:00:00:be:36:04:01:00:0d:00:00:01:39:00:00:00:00:00:00:00:00:54:16
# Connected with 192.168.0.20:17516

# WiFi UDP has 2 message types (long and short), and dones't report a connection
# Socket created
# Socket bind complete
# Wed Jun 10 13:04:03 2020 1591790643 
# 68:59:51:b0:7b:ec:3e:24:7b:ec:3e:24:81:01:05:30:30:30:36:30:38:31:30:33:35:34:37:2d:30:30:31:01:22:09:54:09:1a:00:00:00:14:00:11:00:00:00:25:00:00:00:00:09:7c:00:00:00:00:13:90:03:82:00:00:00:00:00:0a:04:88:02:94:00:02:7e:98:00:00:00:00:00:00:00:00:be:36:04:01:00:8a:00:00:02:1b:00:00:00:00:00:00:00:00:11:16
# Wed Jun 10 13:04:06 2020 1591790646 
# 68:29:51:b1:7b:ec:3e:24:7b:ec:3e:24:80:01:48:34:2e:30:31:2e:35:31:59:34:2e:30:2e:30:32:57:31:2e:30:2e:35:37:28:47:4c:31:37:2d:30:37:2d:32:36:31:2d:44:29:56:00:45:16

# The TCP and the long UDP messages are the same, the short UDP is very different (firmware?)
# Long has 0x81 in byte 12, short has 0x80

# LAN Logging Stick has 2 messages (UDP) to. Each is sent twice (cf. ping gets 2 responses)
# Thu Aug 20 12:58:31 2020 1597924711 
# a5:01:00:10:47:68:3d:8a:1e:ca:71:00:e0:15
# Thu Aug 20 12:58:32 2020 1597924712 
# a5:5c:00:10:02:68:3e:8a:1e:ca:71:01:01:05:85:97:00:00:9b:07:00:00:e3:cd:3d:5f:01:00:a5:00:00:00:30:30:31:39:30:39:30:37:31:34:39:38:2d:30:30:31:cc:01:96:08:82:08:37:00:34:00:59:00:00:00:00:00:b6:09:00:00:00:00:8d:13:a4:08:00:00:46:05:00:00:96:a3:02:00:00:00:00:00:00:00:00:00:00:00:be:01:04:e0:00:b3:01:36:0a:bd:15

prev_date = "25/11/2014"
prev_dlin = "Tue Nov 25"
first_tim = "00:00:00"
last_time = "23:59:59"
last_secs = 0
prev_power = 0.0
last_power = 0.0
prev_count = 0
prev_time = last_time
same_secs = False

def get_byte(line, offset):
    rval = 0
    try:
        rval = int(line[3*offset:2+3*offset], 16)
    except:
        if 2+3*offset > len(line):
            print("GetByte: Err at offset %d, too bg for line length %d" % (offset, len(line)))
            sys.exit(1)
        else:
            print("GetByte: Err at offset %d, chars %s in line %s" % (offset, line[3*offset:2+3*offset], line))
            sys.exit(1)
    return rval

def get_float2(line, offset, bigend, divis=10.0):
    rval = 0.0
    try:
        if bigend:
            rval = float(256 * get_byte(line, offset) + get_byte(line, offset+1)) / divis
        else:
            rval = float(256 * get_byte(line, offset+1) + get_byte(line, offset)) / divis
    except:
        if 2+3*(offset+1) > len(line):
            print("GetFloat: Err at offset %d, too bg for line length %d" % (offset, len(line)))
            sys.exit(1)
        else:
            print("GetFloat: Err at offset %d, chars %s in line %s" % (offset, line[3*offset:2+3*(offset+1)], line))
            sys.exit(1)
    return rval

def get_float4(line, offset, bigend):
    if bigend:
        return float(65536*get_float2(line, offset, bigend, divis=1.0) +
                     get_float2(line, offset+2, bigend, divis=1.0)) / 10.0
    else:
        return float(65536*get_float2(line, offset+2, bigend, divis=1.0) +
                     get_float2(line, offset, bigend, divis=1.0)) / 10.0


def proc_line(line):
    global prev_date, prev_dlin, prev_power, last_power
    global prev_count, first_tim, last_time, last_secs, same_secs
    if re.match("^\S\S\S \S\S\S [ 1-3][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9] [0-9][0-9][0-9][0-9] [0-9]", line):
        # Got a date - if not same as previous, print previous power value.
        if prev_dlin != line[0:10]:
            if prev_power > 0:
                print("%s\t%s\t%s\t%d\t%.1f\t%.1f" % (prev_date, first_tim, last_time, prev_count, prev_power, prev_power-last_power))

            # Then remember date
            line_splt = line.strip().split()
            prev_date = date.fromtimestamp(float(line_splt[-1])).strftime("%d/%m/%Y")
            prev_dlin = line[0:10]
            first_tim = line[11:19]
            last_power = prev_power
            prev_count = 0
        # See whether this time is same as last - if so, skip adding next power entry
        same_secs = last_secs == line[25:]
        last_time = line[11:19]
        last_secs = line[25:]
    elif len(line) > 50 and re.match("^[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:", line) and not same_secs:
        # Remember power
        # Only process TCP records or long UDP ones
        byte0 = get_byte(line, 0)
        if (byte0 == 0x68 and get_byte(line, 12) == 0x81) or (byte0 == 0xa5):
            try:
                if byte0 == 0x68:
                    bigend = True
                    prev_power = get_float4(line, 71, bigend)
                # Power entry is bytes 71 to 74, but byte 71 will be 0 for years to come!
                #prev_power = float(65536 * int(line[3*72:2+3*72], 16) + 256 * int(line[3*73:2+3*73], 16) + int(line[3*74:2+3*74], 16)) / 10.0
                else:
                    bigend = False
                    prev_power = get_float4(line, 80, bigend)
                prev_count += 1
                if last_power == 0:
                    # if not yet read any power,  set previous day's power
                    # to first reading today, since we have no records for then
                    last_power = prev_power
            except:
                pass

for line in fileinput.input():
    proc_line(line)

# Print the last value
print("%s\t%s\t%s\t%d\t%.1f\t%.1f" % (prev_date, first_tim, last_time, prev_count, prev_power, prev_power-last_power))
