#!/usr/bin/env python3
"""
uptime_monitor.py - check if your websites are up and get a Discord alert when one goes down
(and another when it comes back).

No third-party packages needed, just Python 3.8+.

Setup:
    1. In Discord: Server Settings > Integrations > Webhooks > New Webhook > Copy URL
    2. Put the URL in an environment variable (keeps it out of your code and out of git):
         Linux/macOS:  export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
         Windows:      setx DISCORD_WEBHOOK_URL "https://discord.com/api/webhooks/..."

Usage:
    python uptime_monitor.py https://example.com https://mysite.dev
    python uptime_monitor.py --config sites.json --interval 60
    python uptime_monitor.py --config sites.json --once        # single pass, good for cron

sites.json can be a list of URLs or a list of {"name": "...", "url": "..."} objects.
"""

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

UA = "uptime-monitor/1.0"


def check(url, timeout):
    """Return {'up': bool, 'status': int|None, 'ms': int, 'error': str|None}."""
    start = time.monotonic()
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    status, err = None, None
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            status = r.status
    except urllib.error.HTTPError as e:
        status, err = e.code, f"HTTP {e.code}"
    except Exception as e:
        err = str(getattr(e, "reason", e))
    ms = int((time.monotonic() - start) * 1000)
    up = status is not None and status < 400
    return {"up": up, "status": status, "ms": ms, "error": None if up else (err or f"HTTP {status}")}


def send_discord(webhook, title, description, color):
    payload = {
        "embeds": [{
            "title": title,
            "description": description,
            "color": color,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }]
    }
    req = urllib.request.Request(
        webhook,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "User-Agent": UA},
    )
    try:
        urllib.request.urlopen(req, timeout=10).read()
    except Exception as e:
        print(f"  ! couldn't send Discord alert: {e}", file=sys.stderr)


def load_sites(args):
    sites = []
    if args.config:
        with open(args.config, encoding="utf-8") as f:
            for item in json.load(f):
                if isinstance(item, str):
                    sites.append({"name": item, "url": item})
                else:
                    sites.append({"name": item.get("name") or item["url"], "url": item["url"]})
    for url in args.urls:
        sites.append({"name": url, "url": url})
    for s in sites:
        if not s["url"].startswith(("http://", "https://")):
            s["url"] = "https://" + s["url"]
    return sites


def load_state(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def save_state(path, state):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


def run_pass(sites, state, args, webhook):
    for site in sites:
        res = check(site["url"], args.timeout)
        st = state.setdefault(site["url"], {"failures": 0, "alerted": False})
        stamp = datetime.now().strftime("%H:%M:%S")

        if res["up"]:
            print(f"[{stamp}] UP    {site['name']}  {res['status']}  {res['ms']}ms")
            if st["alerted"]:
                if webhook:
                    send_discord(webhook, f"✅ {site['name']} is back up",
                                 f"{site['url']}\nStatus {res['status']} in {res['ms']}ms.", 0x2ECC71)
                st["alerted"] = False
            st["failures"] = 0
        else:
            st["failures"] += 1
            print(f"[{stamp}] DOWN  {site['name']}  {res['error']}  (fail {st['failures']}/{args.failures})")
            if st["failures"] >= args.failures and not st["alerted"]:
                if webhook:
                    send_discord(webhook, f"🔴 {site['name']} is down",
                                 f"{site['url']}\nReason: {res['error']}", 0xE74C3C)
                st["alerted"] = True
    save_state(args.state, state)


def main():
    p = argparse.ArgumentParser(description="Website uptime monitor with Discord alerts.")
    p.add_argument("urls", nargs="*", help="URLs to monitor")
    p.add_argument("--config", help="JSON file with sites to monitor")
    p.add_argument("--webhook", default=os.environ.get("DISCORD_WEBHOOK_URL"),
                   help="Discord webhook URL (default: $DISCORD_WEBHOOK_URL)")
    p.add_argument("--interval", type=int, default=60, help="seconds between checks (default 60)")
    p.add_argument("--timeout", type=int, default=10, help="request timeout in seconds (default 10)")
    p.add_argument("--failures", type=int, default=2,
                   help="consecutive failures before alerting (default 2, avoids false alarms)")
    p.add_argument("--state", default=".uptime_state.json", help="where to remember up/down state")
    p.add_argument("--once", action="store_true", help="check once and exit (for cron)")
    args = p.parse_args()

    sites = load_sites(args)
    if not sites:
        p.error("give at least one URL or --config sites.json")
    if not args.webhook:
        print("No webhook set, printing to console only.", file=sys.stderr)

    state = load_state(args.state)
    try:
        while True:
            run_pass(sites, state, args, args.webhook)
            if args.once:
                break
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nstopped.")


if __name__ == "__main__":
    main()
