#!/usr/bin/env python3
"""Keep a free Render service awake by pinging it every 14 minutes
from start until midnight SGT, then 8:00-23:52 SGT daily. Standard library only; needs Python 3.8+.

Usage:
    python3 pinger.py          # run the scheduler (keep it running)
    python3 pinger.py --once   # ping once and exit
"""

import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone

TARGET = os.environ.get("RENDER_URL", "https://vocabpractice-hfrv.onrender.com")
INTERVAL_MIN = 14
START_HOUR = 8  # SGT, first ping
END_HOUR = 24  # SGT midnight, no pings at or after this hour
SGT = timezone(timedelta(hours=8))
TIMEOUT_S = 180  # a cold Render service can take minutes to wake


def ping():
    start = time.monotonic()
    stamp = datetime.now(SGT).strftime("%Y-%m-%d %H:%M:%S SGT")
    try:
        req = urllib.request.Request(f"{TARGET}/health", headers={"User-Agent": "render-pinger/1.0"})
        with urllib.request.urlopen(req, timeout=TIMEOUT_S) as res:
            status = res.status
        result = f"OK {status}"
    except urllib.error.HTTPError as err:
        result = f"FAIL {err.code}"
    except Exception as err:
        result = f"ERROR {err}"
    print(f"{stamp} {result} {int((time.monotonic() - start) * 1000)}ms", flush=True)


def next_end(after):
    """First END_HOUR SGT strictly after `after`."""
    end = after.replace(hour=END_HOUR % 24, minute=0, second=0, microsecond=0)
    return end if end > after else end + timedelta(days=1)


def schedule(start):
    """Ping times from `start`: every INTERVAL_MIN until the next END_HOUR SGT,
    then every INTERVAL_MIN from START_HOUR to END_HOUR each day."""
    slot = start.astimezone(SGT)
    end = next_end(slot)
    while True:
        yield slot
        slot += timedelta(minutes=INTERVAL_MIN)
        if slot >= end:
            slot = end.replace(hour=START_HOUR)
            if slot < end:
                slot += timedelta(days=1)
            end = next_end(slot)


def main():
    if "--once" in sys.argv:
        ping()
        return
    slots = schedule(datetime.now(SGT))
    slot = next(slots)
    while True:
        # Sleep in short chunks against the wall clock: time.sleep pauses
        # while the machine sleeps, so one long sleep can overshoot by hours.
        while (remaining := (slot - datetime.now(SGT)).total_seconds()) > 0:
            time.sleep(min(remaining, 30))
        ping()
        now = datetime.now(SGT)
        slot = next(slots)
        while slot <= now:  # skip slots missed while asleep
            slot = next(slots)
        print(f"Next ping at {slot:%Y-%m-%d %H:%M} SGT", flush=True)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
