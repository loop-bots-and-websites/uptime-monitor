# uptime-monitor

A small Python script that watches your websites and sends you a **Discord message** when one goes down, and another when it comes back up.

No packages to install. You only need Python 3.8 or newer.

This is how to run it on your computer/device. If you want to run it 24/7, you need to find a hoster (ie HeavenCloud, no I am not advertising them) and upload the files there.

## How it works

1. You give it a list of websites.
2. It visits each one every 60 seconds.
3. If a site fails 2 checks in a row, it posts a red "is down" message in your Discord channel.
4. When the site works again, it posts a green "is back up" message.

You only get a message when something changes, so there's no spam while a site stays down.

## Setup (one time)

### 1. Make a Discord webhook

A webhook is a link that lets the script post messages in one of your channels.

1. Open your Discord server
2. Go to **Server Settings > Integrations > Webhooks**
3. Click **New Webhook**, pick the channel for alerts
4. Click **Copy Webhook URL**

Keep this URL private. Anyone who has it can post in your channel.

### 2. Give the script your webhook URL

Open a terminal in the project folder and run the line for your system, pasting your URL inside the quotes.

**Windows (PowerShell):**
```powershell
$env:DISCORD_WEBHOOK_URL="paste-your-url-here"
```

**Mac / Linux:**
```bash
export DISCORD_WEBHOOK_URL="paste-your-url-here"
```

This only lasts for that terminal window. If you close it, run the line again.

## Running it

**Check one or more sites:**
```bash
python uptime_monitor.py https://example.com https://mysite.dev
```

**Check a list of sites from a file:**

1. Copy `sites.example.json` and name the copy `sites.json`
2. Put your own sites in it
3. Run:
```bash
python uptime_monitor.py --config sites.json
```

The script keeps running and checking until you press **Ctrl+C**.

**Check once and exit** (useful for scheduled tasks):
```bash
python uptime_monitor.py --config sites.json --once
```

## Test that alerts work

Run it on a site that doesn't exist and you should get a red alert in Discord right away:

```bash
python uptime_monitor.py https://thisdoesnotexist12345.com --failures 1
```

## Options

Add these after the command, for example `python uptime_monitor.py --config sites.json --interval 30`.

| Option | Default | What it does |
|--------|---------|--------------|
| `--interval` | 60 | Seconds to wait between checks |
| `--timeout` | 10 | Seconds to wait for a site before counting it as failed |
| `--failures` | 2 | How many failed checks in a row before sending an alert |
| `--once` | off | Check once and exit instead of looping |
| `--webhook` | your saved URL | Webhook URL, if you'd rather not use the saved one |

Built by [NANTHEDU](https://nanthedu.dpdns.org).
