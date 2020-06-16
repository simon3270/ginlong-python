#!/usr/bin/env python3
# Reads solar log files as parameters, and prints off (some of) the data in each entry
# Each ouput line has:
# Date, time of first entry, time of last entry, number of entries, daily total kwH
import sys
import os
import time
import re
from datetime import date

# TCP has one message type, and reports TCP connection being made
# Socket created
# Socket bind complete
# Wed Sep  2 08:03:21 2015 Socket now listening
# Connected with 192.168.0.20:40007
# Wed Sep  2 08:05:50 2015 1441177550 
# 68:59:51:b0:7b:ec:3e:24:7b:ec:3e:24:81:01:05:30:30:30:36:30:38:31:31:31:31:31:31:2d:30:30:31:00:fc:07:87:09:56:00:00:00:30:00:2b:00:00:00:4e:00:00:00:00:09:7c:00:00:00:00:13:8a:07:65:00:00:00:00:00:0a:04:6a:00:78:00:00:62:98:00:00:00:00:00:00:00:00:be:36:04:01:00:0d:00:00:01:39:00:00:00:00:00:00:00:00:dd:16
# Connected with 192.168.0.20:47875
# Wed Sep  2 08:11:14 2015 1441177874 
# 68:59:51:b0:7b:ec:3e:24:7b:ec:3e:24:81:01:05:30:30:30:36:30:38:31:31:31:31:31:31:2d:30:30:31:01:07:07:ae:09:17:00:00:00:32:00:30:00:00:00:53:00:00:00:00:09:74:00:00:00:00:13:82:07:d8:00:00:00:00:00:0a:04:6a:00:8c:00:00:62:98:00:00:00:00:00:00:00:00:be:36:04:01:00:0d:00:00:01:39:00:00:00:00:00:00:00:00:54:16
# Connected with 192.168.0.20:17516

# UDP has 2 message types (long and short), and dones't report a connection
# Socket created
# Socket bind complete
# Wed Jun 10 13:04:03 2020 1591790643 
# 68:59:51:b0:7b:ec:3e:24:7b:ec:3e:24:81:01:05:30:30:30:36:30:38:31:31:31:31:31:31:2d:30:30:31:01:22:09:54:09:1a:00:00:00:14:00:11:00:00:00:25:00:00:00:00:09:7c:00:00:00:00:13:90:03:82:00:00:00:00:00:0a:04:88:02:94:00:02:7e:98:00:00:00:00:00:00:00:00:be:36:04:01:00:8a:00:00:02:1b:00:00:00:00:00:00:00:00:11:16
# Wed Jun 10 13:04:06 2020 1591790646 
# 68:29:51:b1:7b:ec:3e:24:7b:ec:3e:24:80:01:48:34:2e:30:31:2e:35:31:59:34:2e:30:2e:30:32:57:31:2e:30:2e:35:37:28:47:4c:31:37:2d:30:37:2d:32:36:31:2d:44:29:56:00:45:16

# The TCP and the long UDP messages are the same, the short UDP is very different (firmware?)
# Long has 0x81 in byte 12, short has 0x80

import fileinput

curr_date = "25/11/2014"
curr_tim = "00:00:00"

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

def get_float2(line, offset, divis=10.0):
    rval = 0.0
    try:
        rval = float(256 * int(line[3*offset:2+3*offset], 16) + int(line[3*(offset+1):2+3*(offset+1)], 16)) / divis
    except:
        if 2+3*(offset+1) > len(line):
            print("GetFloat: Err at offset %d, too bg for line length %d" % (offset, len(line)))
            sys.exit(1)
        else:
            print("GetFloat: Err at offset %d, chars %s in line %s" % (offset, line[3*offset:2+3*(offset+1)], line))
            sys.exit(1)
    return rval

def get_float4(line, offset):
    return float(65536*get_float2(line, offset, divis=1.0) + get_float2(line, offset+2, divis=1.0)) / 10.0

def proc_line(line):
    global curr_date, curr_tim
    if re.match("^\S\S\S \S\S\S [ 1-3][0-9] [0-9][0-9]:[0-9][0-9]:[0-9][0-9] [0-9][0-9][0-9][0-9] [0-9]", line):
        # Got a date - remember it
        line_splt = line.strip().split()
        curr_date = date.fromtimestamp(float(line_splt[-1])).strftime("%d/%m/%Y")
        curr_tim = line[11:19]
    elif re.match("^[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:", line):
        # Got a data entry - report values
        # Only use if byte 12 is 0x81 (ox80 implies a short non-data message)
        if get_byte(line, 12) == 0x81:
            try:
                # vdc1+2 33 35 , idc1+2 39 41, w 73
                print("%s,%s,%.1f,%.1f,%.1f,%.1f,%.1f,%.0f,%.1f,%.1f" % (curr_date, curr_tim, get_float2(line, 33),
                                 get_float2(line, 35), get_float2(line, 39), get_float2(line, 41),
                                 get_float2(line, 51), get_float2(line, 59, 1.0), get_float2(line, 69)/10.0, get_float4(line, 71)))
            except:
                print("Error reading entry at %s %s: %s" % (curr_date, curr_tim, line))
                sys.exit(1)
                pass

print("Date,Time,VDC1,VDC2,IDC1,IDC2,VAC1,CurrW,TodaykW,TotalkW")

for line in fileinput.input():
    proc_line(line)

# Print the last value
