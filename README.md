# uptime-monitor

Checks your websites on a timer and sends a Discord alert when one goes down, plus another when it recovers. Standard library only, no installs.

## Setup

1. In Discord: **Server Settings > Integrations > Webhooks > New Webhook > Copy Webhook URL**
2. Save it as an environment variable (never commit it):

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
```

## Usage

```bash
# quick check of a few sites, every 60s
python uptime_monitor.py https://example.com https://mysite.dev

# use a config file (copy sites.example.json to sites.json)
python uptime_monitor.py --config sites.json --interval 30

# single pass, for cron / scheduled tasks
python uptime_monitor.py --config sites.json --once
```

## Options

| Flag | Default | What it does |
|------|---------|--------------|
| `--interval` | 60 | Seconds between checks |
| `--timeout` | 10 | Seconds before a request counts as failed |
| `--failures` | 2 | Failed checks in a row before alerting (avoids false alarms) |
| `--once` | off | Check once and exit |
| `--webhook` | `$DISCORD_WEBHOOK_URL` | Discord webhook URL |

Alerts only fire when the state changes, so you get one message when a site goes down and one when it's back, not a spam stream.

Built by [NANTHEDU](https://nanthedu.dpdns.org).
