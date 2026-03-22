---
name: kisstalon
description: Manage KISStalon periodic agent tasks (talons)
triggers:
  - talon
  - kisstalon
  - add a hook
  - check hook
  - periodic task
  - scheduled agent
---

# KISStalon Skill

You can manage KISStalon talons — periodic tasks run by Claude via cron.

## Talon file format

Talons live in `~/.kisstalon/talons/` as markdown files with YAML frontmatter:

```markdown
---
id: example-task
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

## Commands

- `kisstalon init` — Set up ~/.kisstalon/ and crontab
- `kisstalon create --id NAME --schedule "every 12h" --prompt "Do the thing"` — Create a talon
- `kisstalon list` — Show all talons
- `kisstalon show ID` — Show talon details and recent invocations
- `kisstalon tick` — Run any due talons (called by cron every 10 min)

## Schedule formats

- `every Xh` — every X hours
- `every Xm` — every X minutes
- `daily` — once per day
- `nightly` — once per day, between 1am-5am

## When creating a talon

1. Pick a descriptive ID (kebab-case)
2. Choose a schedule
3. Write a clear prompt describing the task
4. Choose permissions (default is read-only + web access)
5. Use `kisstalon create` or write the .md file directly to `~/.kisstalon/talons/`
