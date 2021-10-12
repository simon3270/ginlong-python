
# ginlong-python Support scripts
These scripts support the running of the ginlong-python scripts to gather Solis 2G data.

As before, I use the src/ginserv\_poller directory to store my scripts and log files.

Note that all scripts here use Bash.

## runginservpoller

Runs the poller (the `ginserv.py` Python 3 program) in a loop.

- It changes directory to the one with this code and the log files.

- If the poller is already running when the script starts, it kills it and waits 5 minutes.

- It renames any ginserv.log file to ginserv.log\_YYYYMMDD\_HHMMSS.

- It then starts the poller, logging to a ginserv.log\_YYYYMMDD\_HHMMS file.

- When that poller dies, it waits 5 minutes and loops round again.

I start this script at boot time (see `crontab` below).

## killginservpoller

This looks for the ginserv.py process and kills it.
Called from various places.

## killiflogempty

This script is used to kill off a poller program if it seems to be stuck
in the startup sequence (more of a problem with the TCP-based poller,
but does sometimes happen with the UDP one).

It looks for the most recent ginserv.log\* file. if it only contains the
startup sequence, the `killginservpoller` script is called.
The `runginservpoller` loop will restart it 5 minutes later.

## midnightcheck\_ginservpoller

This is run just before midnight (when, in much of the world, there is little sunlight!).

It kills the currently-running poller, then gathers together all of the log files for today.
If there are fewer than 50 records from today,
the script has a place to alert someone (e.g. to send an email).

By default there is no alerting, but this script does have the effect of keeping all of today's logs having today's date.

Since this runs just before midnight, the 5-minute delay in runginservpoller
means that the next run starts the next day.

# Crontab entries

You may want a different approach, but I find that these crontab entries work well.
I run them as my normal user (no need to run them as root).

    # Start the ginservpoller at boot time
    @reboot $HOME/src/ginlong_poller/runginservpoller

    # Stop the ginserv poller just before midnight, and check that some entries were written today
    57 23 * * * $HOME/src/ginlong_poller/midnightcheck_ginservpoller

    # Kill the ginserv poller if it hasn't written data by lunchtime
    2 10,11,12,13 * * * $HOME/src/ginlong_poller/killiflogempty
