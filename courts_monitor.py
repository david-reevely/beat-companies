# ── ontario-courts-monitor / monitor.py ──────────────────────────────────────
# This tool currently lives on GitHub and loads its own companies.toml. When you
# move it to the Pi, DELETE that load and REPLACE with for_tool("courts"), which
# returns the identical {name, searches:[{term,type}]} shape — exact/contains
# semantics preserved verbatim for every company that had a curated block, and a
# synthesized {contains} search for the newly-universal companies.

from beat_companies import for_tool

COMPANIES = for_tool("courts")
# Each entry: {"name": str, "searches": [{"term": str, "type": "exact"|"contains"}]}
#
# The [reporter] table (name/email) is NOT company data — keep it wherever the
# per-reporter config lives (it's per-user, and you have Claire as a second
# reporter). The master only supplies the shared company roster; reporter
# identity stays in each reporter's own config.
#
# Iteration is unchanged, e.g.:
#   for c in COMPANIES:
#       for s in c["searches"]:
#           query_courts(s["term"], exact=(s["type"] == "exact"))
