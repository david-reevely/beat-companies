# beat-companies

One master roster for the four company-driven beat monitors. Add a company
once in `companies.toml`; every tool sees it on its next run.

## What's here
- `companies.toml` — the single source of truth (96 records). Hand-edit this.
- `beat_companies/` — loader that projects the master into each tool's shape.
- `pyproject.toml` — lets you `pip install -e` it into each tool's venv.
- `snippets/` — the exact edit for each of the four tools.

## The model
The master holds **identity + attributes** (id, canonical name, beats,
canada_gate, a default `match` list) plus the **curated per-tool specifics**
that already existed (courts' exact/contains searches, news-release's
url/feed/terms, google-news search phrases). Match *strings* are deliberately
NOT unified — each tool queries a different corpus (vendor legal names, court
party names, news headlines), so each keeps its own match basis. What's shared
is the roster and the per-company attributes.

`for_tool(name)` returns the shape that tool already consumes:
- `for_tool("contracts")`    -> {name, match}
- `for_tool("news_release")` -> {name, sector, color, terms, url?, feed?}
- `for_tool("google_news")`  -> {name, search, canada_gate}
- `for_tool("courts")`       -> {name, searches:[{term, type}]}

Insolvency-monitor and lobbying-digest are intentionally NOT consumers — they
catch everything / use Claude guidance, so they import nothing.

## Coverage rule
Every private company appears in all four tools. Public bodies are scoped:
commercial Crown corps (OPG, Hydro One/Québec, BC Hydro, AECL) go universal;
CSA and the universities are courts-only; the port authorities and Invest
Ottawa keep their current narrower scope. Scope lives in each record's `tools`
list (absent = all four).

## Deploy on the Pi
    # one-time: clone beside the other tools
    cd ~/PythonScripts
    git clone <your-repo-url> beat-companies

    # install into each consuming tool's venv (editable -> reads the one
    # canonical companies.toml at runtime, so an edit is picked up everywhere)
    for tool in contract-monitor news-release-scan google-news-roundup; do
        ~/PythonScripts/$tool/venv/bin/pip install -e ~/PythonScripts/beat-companies
    done
    # courts monitor: same, once you migrate it off GitHub Actions

Optionally point every tool at one shared file regardless of where it's checked
out, via env var in each tool's env.sh:
    export BEAT_COMPANIES_TOML=$HOME/PythonScripts/beat-companies/companies.toml

Keep it fresh by pulling before the daily runs (or right after you push an
edit):
    cd ~/PythonScripts/beat-companies && git pull --quiet

## Adding a company later
Append one block to companies.toml:

    [[company]]
    id    = "acme-robotics"
    name  = "Acme Robotics"
    beats = ["defence"]
    # match defaults to ["Acme Robotics"]; add a [company.courts] block etc.
    # only if you need non-default per-tool behaviour.

Distinctive names need nothing else. Common-word names want a `match` override
(qualified name or legal entities) to avoid false positives.

## Notes / things that changed behaviour
- OPG was double-listed in news-release (Nuclear + Energy). It's now one record
  with beats=["nuclear","energy"] and appears once, under its primary beat
  (Nuclear). If you'd rather it show under Energy there, reorder its beats.
- The two TOML syntax errors in the old news-release file (Shearwater, Marshall
  missing a `[`) and the Mondata string-vs-list bug are fixed here by
  construction.
- Aramis is "Aramis Biotechnologies"; Aspartes is a separate record. Both
  health, both universal.
