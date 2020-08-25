# ginlong-python
Get data from Solis 2G Inverter and log to file, then scripts to show data, or
get daily totals (4G inverter has a different format)

Note that all scripts use Python 3

The scripts will process data from the WiFi and LAN Data Logger Sticks (they have very different data formats!).

## ginserv.py

Script to receive data from a Ginlong Data Logger (wireless or LAN) and
write it to a log file

It uses UDP rather than TCP, as this suffers less from locked binds
(e.g. if a TCP receiver fails, it may hold onto the receive port for
extended periods).

A WiFi TCP connection will receive only the long (103-byte) messages, containing
performance data for the Inverter.

A WiFi UDP connection will receive the same 103-byte message, and a 55-byte message
with firmare information about the inverter.

A LAN UDP connection receives a 105-byte message containing the voltage and power information every 5 minutes, and a 14-byte message (of unknown contents) every minute. It might be my network, but each message gets sent twice at exactly the same time.

To configure, go to the Solis Data Logger web interface, then "Advanced" and
"Remote Monitoring" (on the WiFi stick), or just "Manual" (LAN Stick).
Leave the first entry ("Default") alone, and on the second
line enter the IP address of the machine running this script, with Port 5433
and Connection UDP. With this script running, click "Test" and see the tick.

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
