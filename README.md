# ginlong-python
Get data from Solis 4.6K 2G Single Phase Inverter and log to file, with scripts to show data, or
get daily totals (4G inverter has acompletely different format).
It doesn't yet cope with the Solis Mini 1000 2G invertor - I'll try to add decoding for that if I get some data!
Other 2G invertors may also work - please let me know if the data output from yours doesn't look right,
and I can try to improve the data analysis.

When configured correctly (see below), Solis invertors will send data about their performance every 5 minutes
to code waiting to receive the data.
This is the same data as can be sent to the ginlogmonitoring.com website for centralised data collection.

Note that all scripts use Python 3

The scripts will process data from the WiFi and LAN Data Logger Sticks (they have very different data formats!).

## ginserv.py & ginserv_tcp.py

Scripts to receive data from a Ginlong Data Logger (wireless or LAN) and write it to a log file.
It doesn't worry about data formats - it just writes each record out as it is received, but in ASCII rather than binary.

Note that these scripts are designed to run for a while, then terminate.
You should write a wrapper script which starts this script in a loop, so that when it stops it is automatically restarted.
This could be as simple as this (which logs to files with the current date and time in the name):

    while true; do
      python3 ginserv.py > gindata.log_$(date '+%Y%m%d_%H%M%S')
      sleep 30
    done
    
There are UDP and TCP versions. I prefer the UDP, as this suffers less from locked binds
(e.g. if a TCP receiver fails, it may hold onto the receive port for
extended periods, blocking any more data being received).

A WiFi TCP connection will receive only the long (103-byte) messages, containing
performance data for the Inverter.

A WiFi UDP connection will receive the same 103-byte message, and a 55-byte message
with firmare information about the inverter.

A LAN UDP connection receives a 105-byte message containing the voltage and power information every 5 minutes,
and a 14-byte message (of unknown contents) every minute.
It might be my network, but each message gets sent twice at exactly the same time.

To configure, go to the Solis Data Logger web interface, then "Advanced" and
"Remote Monitoring" (on the WiFi stick), or just "Manual" (LAN Stick).
Leave the first entry ("Default") alone, and on the second
line enter the IP address of the machine running this script, with Port 5433
and Connection UDP or TCP.
With the appropriate (UDP or TCP) script running, click "Test" and see the tick.

## get_data.py

Prints out information from log files named on the command line. It prints out
the data for each data line in the log file. It reports:

Date,Time,VDC1,VDC2,IDC1,IDC2,VAC1,CurrW,TodaykW,TotalkW

## get_tots.py

Prints out daily totals for log files named on the command line.

This runs through the files, noting the first and last entries for each day,
and the total KwH for that day. It counts the number of records each day
(only counting the duplicated mesasges from the LAN stick once).

Each day has:

Date, Time of first reading, Time of last, Number of readings,
Total kWH for invertor, Difference from previous day

## gindata.txt

A text description of the records available.

# Support files

The `support` directory contains scripts to support running of the above logging programs,
and `crontab` entries to run the scripts.
