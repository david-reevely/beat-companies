# ── contract-monitor / monitor.py ────────────────────────────────────────────
# DELETE the entire TRACKED_COMPANIES list (the ~88-line block).
# REPLACE the matches_tracked() function with the version below.
# Everything else is untouched. SECTOR_KEYWORDS stays — it is the beat-keyword
# net for non-tracked vendors, not company data.

from beat_companies import for_tool, fold

# Each item: {"name": <canonical>, "match": [substrings]}
TRACKED = for_tool("contracts")

def matches_tracked(vendor: str) -> tuple[bool, str]:
    """Return (matched, canonical_company_name).
    Accent/hyphen folding + word boundaries: 'Hydro-Québec' matches
    'hydro quebec', and bare needles no longer match inside longer words
    (no more 'Bell' in 'Campbell')."""
    v = f" {fold(vendor)} "
    for company in TRACKED:
        if any(f" {fold(n)} " in v for n in company["match"]):
            return True, company["name"]
    return False, ""
