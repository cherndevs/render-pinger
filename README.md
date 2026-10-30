# Render Pinger

Pings `RENDER_URL/health` every 14 minutes, starting as soon as it runs and continuing until midnight SGT, then from 8:00 to 23:52 SGT each day, to keep a free Render service awake. Standard library only; needs Python 3.8+.

```
python3 pinger.py          # run the scheduler (keep it running)
python3 pinger.py --once   # ping once and exit
```

`RENDER_URL` defaults to `https://vocabpractice-hfrv.onrender.com`. Each ping waits up to 3 minutes for a cold start.

If you see `CERTIFICATE_VERIFY_FAILED` on macOS with the python.org installer, run
`/Applications/Python 3.x/Install Certificates.command` once.
