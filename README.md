# KISStalon

A lightweight agent orchestrator that uses cron and the Claude CLI to run periodic tasks.

Each task is a **talon** — a markdown file with YAML frontmatter describing its schedule, permissions, and prompt. Every 10 minutes, cron runs `kisstalon tick`, which checks what's due and spawns Claude to execute each task. Results are appended directly to the talon file under an `# Invocations` heading, building up a running log. Urgent findings trigger macOS notifications or ntfy.sh webhooks.

## Quick start

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -e .
kisstalon init      # creates ~/.kisstalon/, adds crontab entry
kisstalon create --id check-site --schedule "every 12h" --prompt "Check example.com for downtime"
kisstalon tick      # run manually, or wait for cron
kisstalon list      # see all talons and their status
kisstalon show check-site  # see recent invocations
```

## Schedule formats

- `every Xh` — every X hours
- `every Xm` — every X minutes
- `daily` — once per day
- `nightly` — once per day, between 1am–5am

## Talon file format

```markdown
---
id: check-site
created: 2026-03-22T10:00:00
schedule: every 12h
notify: osascript
permissions:
  - Bash(read_only)
  - WebFetch
  - WebSearch
  - Read
---

Check example.com for downtime and report any issues.

# Invocations
```

## Configuration

Copy `config.example.toml` to `~/.kisstalon/config.toml` and edit as needed. Supports ntfy.sh for push notifications and extra Claude CLI flags.

## Requirements

- Python 3.10+
- [Claude CLI](https://claude.ai/download) installed and on PATH
- macOS (for osascript notifications; ntfy works anywhere)
