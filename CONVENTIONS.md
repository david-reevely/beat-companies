# David Reevely — Tool Conventions

Reference doc for building/editing any tool in the beat-monitoring suite. Point Claude at this file at the start of a session ("follow CONVENTIONS.md") instead of re-explaining the stack.

## Environments

- **Raspberry Pi 5** (`raspberrypi`, user `davidreevely`) — primary home for scheduled tools. Accessed via Raspberry Pi Connect browser shell. Python 3.13, timezone `America/Toronto`.
- **Mac (MacBook Air)** — used for a few remaining launchd jobs and local CLI tools. Always use `/opt/homebrew/bin/python3` (Homebrew Python), never `/usr/bin/python3`. All launchd plists must point to the Homebrew binary.
- **GitHub Actions** — used for a few tools that don't need Pi-local state (lobbying digest, Court-checker, IPO watcher).

## Repo / folder layout

- Each tool lives in its own GitHub repo.
- On the Pi: `~/PythonScripts/<hyphen-folder>/`, each with its own venv, `env.sh` (chmod 600), cache/state file(s), and `cron.log`.
- On the Mac: scripts live in the shared `~/Desktop/PythonScripts/` folder — use descriptive, specific filenames (`notice_paper_monitor.py`, not `monitor.py`) to avoid collisions.
- Cron pattern:
  ```
  cd /full/path && . ./env.sh && ./venv/bin/python3 script.py >> cron.log 2>&1
  ```

## Secrets

- No shared secrets store — each repo gets its own secrets added fresh (`ANTHROPIC_API_KEY`, `GMAIL_APP_PASSWORD`, etc.).
- PATs used for GitHub Contents API pushes should be revoked after the session.
- PATs without the `workflow` scope can't touch `.github/workflows/` files — those changes go through the GitHub web UI, which is David's default way of handling workflow edits anyway.

## Caching / state

- Prefer key-based JSON caches (e.g. `owner_org|request_number`, entity name, normalized headline) over naive "last N" windows.
- Match cache lifetime to the data's actual shelf life: some things cache indefinitely (new registrations by entity name), some expire on a rolling basis (spikes/meetings, 30 days; ATI window, 6 months).
- Write cache updates *after* successful delivery (email/Slack), not before — avoids losing records on a mid-run failure.
- Permanent "union" caches are used where oscillating/flapping state would otherwise cause repeat alerts (e.g. Court-checker).

## Delivery channels

- Email digests via Gmail SMTP (`smtplib`), HTML formatted.
- Slack via webhooks for real-time/lower-latency alerts.
- Pick based on urgency: daily/weekly roundups → email; near-real-time or short-fuse items (e.g. bills ~48h before introduction) → Slack.

## Relevance filtering

- Claude API (currently `claude-sonnet-4-6` in most active tools) is the standard way to filter noisy feeds against David's actual beat, rather than hand-rolled keyword logic alone.
- Structured/tool-use output is preferred over free-text + regex JSON parsing where the model needs to return structured data (e.g. contracts monitor) — eliminates parse failures.
- Batch API calls where possible (e.g. parliamentary written questions monitor) rather than one call per item.

## Master company roster

- Single source of truth: `david-reevely/beat-companies` (public repo), `companies.toml`.
- Consumed via the `beat_companies` Python package, `for_tool("contracts"|"news_release"|"google_news"|"courts")`.
- Pi tools install it with `pip install -e` (editable); a 6:55 AM weekday `git pull` cron keeps it current.
- Deliberate exceptions: the insolvency monitor and the lobbying digest do **not** use this roster.

## Anti-blocking / scraping

- Sites with bot detection generally need a full/real browser UA, sometimes plus a `Referer` header, to avoid 403s or WAF blocks (CanadaBuys, AI Register CKAN API).
- Where Python's TLS stack gets reset by a GoC edge but curl doesn't: shell out via `subprocess curl` rather than fighting `requests`/`urllib3`.
- `curl_cffi` (Chrome TLS impersonation) is the tool of choice for sites with more serious bot detection on residential IPs (Notice Paper monitor).
- Headless-browser scraping (SEDAR+, insolvency firm sites) uses Playwright; on the Pi's ARM architecture this runs under Xvfb.
- `wait_for_network()`-style checks should confirm DNS readiness against a real external host (e.g. `hooks.slack.com`) rather than assuming network is up at boot.

## Known quirks to remember

- **Heredoc truncation**: pasting scripts into the Pi's browser shell via heredoc drops the final newline, merging the last line with the closing `PYEOF` marker. Always verify with `py_compile` after pasting; fix manually (`nano`) if it breaks.
- Ontario courts API has a 10,000-result cap — use exact-match searches for common/multinational company names to stay under it.
- Parliamentary recess handling: detect when `latest-sitting` resolves to Journals instead of the expected sitting page.

## Working style / process

- Verify page/API structure via Terminal commands *before* any code gets written — especially where sandbox network restrictions might hide a problem until deploy.
- Confirm full requirements before writing any script expected to exceed ~100 lines.
- Dry-run previews before any live write (emails sent, sheet writes, file pushes).
- Prefer one canonical version of shared assets (e.g. Ontario courts monitor's `signup.html`) and edit forward from it rather than letting forks drift.

## Colleague-facing tools

- Where a tool is shared with colleagues (Court-checker's per-user `.toml` watchlists, the ATIP Apps Script's `REQUESTOR_MAP`), keep per-user state fully isolated — independent config blocks or per-user row/column keys, never shared mutable state.
