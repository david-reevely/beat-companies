# ── google-news-roundup / google_news_roundup.py ─────────────────────────────
# DELETE the COMPANIES dict AND the CANADA_GATED set.
# REPLACE both with the projection below. The gate flag now travels per-record,
# so collect_by_company() reads c["canada_gate"] instead of doing a set lookup.

from beat_companies import for_tool

_PROJECTION = for_tool("google_news")
# Each item: {"name": str, "search": [str, ...], "canada_gate": bool}

# Preserve the old {display_name: [terms]} structure the rest of the script uses:
COMPANIES = {c["name"]: c["search"] for c in _PROJECTION}
# Gate lookup by display name (mirrors the old CANADA_GATED membership test):
CANADA_GATED = {c["name"] for c in _PROJECTION if c["canada_gate"]}

# In collect_by_company(), the existing line
#     gated = company in CANADA_GATED
# keeps working unchanged. (CANADA_TERMS / BLOCKED_SOURCES stay as-is — they're
# not company data.)
