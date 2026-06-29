# ── news-release-scan / news_release_scan.py ─────────────────────────────────
# DELETE the local companies.toml load (the [[companies]] + [sector_colors]
# parsing). REPLACE with for_tool("news_release"), which returns the same
# per-company shape the scanner already iterates: name, sector, color, terms,
# and optional url / feed.

from beat_companies import for_tool

COMPANIES = for_tool("news_release")
# Each entry:
#   {"name": str, "sector": str, "color": "#rrggbb", "terms": [str, ...],
#    "url": str (optional), "feed": str (optional)}

# Sector -> colour is now carried per-company (entry["color"]), so any prior
# SECTOR_COLORS dict lookup can read entry["color"] directly. If you still want
# the standalone map (e.g. for a legend), pull it from the master meta:
#
#   import tomllib, beat_companies
#   with open(beat_companies.COMPANIES_TOML, "rb") as f:
#       SECTOR_COLORS = tomllib.load(f)["meta"]["news_release_colors"]
#
# Iteration is otherwise unchanged, e.g.:
#   for c in COMPANIES:
#       fetch_feed(c["feed"]) if c.get("feed") else scrape(c.get("url")) ...
#       tag_section(c["sector"], c["color"])
