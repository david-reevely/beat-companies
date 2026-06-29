"""beat_companies — one master roster, projected into each tool's shape.

Usage
-----
    from beat_companies import for_tool, companies, fold

    for c in for_tool("contracts"):      # {"name", "match"}
        ...
    for c in for_tool("google_news"):    # {"name", "search", "canada_gate"}
        ...
    for c in for_tool("news_release"):   # {"name","sector","color","terms","url","feed"}
        ...
    for c in for_tool("courts"):         # {"name","searches":[{"term","type"}]}
        ...

The TOML at COMPANIES_TOML is the single source of truth. Add a company by
appending one [[company]] block there; every tool picks it up on next run.
"""
from __future__ import annotations
import tomllib, unicodedata, re
from pathlib import Path

# Portable path: the master sits next to this package by default, but an env
# override lets the Pi point all tools at one shared checkout.
import os
COMPANIES_TOML = Path(
    os.environ.get("BEAT_COMPANIES_TOML")
    or Path(__file__).resolve().parent.parent / "companies.toml"
)

ALL_TOOLS = ("contracts", "news_release", "google_news", "courts")

_cache: dict | None = None


def fold(s: str) -> str:
    """Accent/punctuation-folding normaliser for substring matching.
    Folds Hydro-Québec -> 'hydro quebec', collapsing the accent/hyphen alias
    burden. Used by the contracts/insolvency-style matchers, NOT by courts
    (which preserves exact/contains semantics verbatim)."""
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub(r"[^a-z0-9]+", " ", s.lower())
    return s.strip()


def _load() -> dict:
    global _cache
    if _cache is None:
        with open(COMPANIES_TOML, "rb") as f:
            _cache = tomllib.load(f)
    return _cache


def _meta() -> dict:
    return _load()["meta"]


def companies() -> list[dict]:
    """All records with defaults applied (private, canada_gate, match, tools)."""
    out = []
    for c in _load()["company"]:
        r = dict(c)
        r.setdefault("private", True)
        r.setdefault("canada_gate", False)
        r.setdefault("match", [r["name"]])
        r.setdefault("tools", list(ALL_TOOLS))
        out.append(r)
    return out


def _in(tool: str, c: dict) -> bool:
    return tool in c.get("tools", ALL_TOOLS)


def for_tool(tool: str) -> list[dict]:
    if tool == "contracts":
        return [{"name": c["name"], "match": c["match"]}
                for c in companies() if _in(tool, c)]

    if tool == "google_news":
        out = []
        for c in companies():
            if not _in(tool, c):
                continue
            gn = c.get("google_news", {})
            out.append({
                "name": gn.get("display", c["name"]),
                "search": gn.get("search", c["match"]),
                "canada_gate": c["canada_gate"],
            })
        return out

    if tool == "news_release":
        sectors = _meta()["news_release_sectors"]
        colors = _meta()["news_release_colors"]
        out = []
        for c in companies():
            if not _in(tool, c):
                continue
            nr = c.get("news_release", {})
            sector = nr.get("sector") or sectors.get(c["beats"][0], "Other")
            rec = {
                "name": nr.get("display", c["name"]),
                "sector": sector,
                "color": colors.get(sector, colors.get("Other", "#888888")),
                "terms": nr.get("terms", c["match"]),
            }
            if "url" in nr:
                rec["url"] = nr["url"]
            if "feed" in nr:
                rec["feed"] = nr["feed"]
            out.append(rec)
        return out

    if tool == "courts":
        out = []
        for c in companies():
            if not _in(tool, c):
                continue
            ct = c.get("courts", {})
            searches = ct.get("searches") or [
                {"term": m, "type": "contains"} for m in c["match"]
            ]
            out.append({"name": ct.get("display", c["name"]), "searches": searches})
        return out

    raise ValueError(f"unknown tool {tool!r}; expected one of {ALL_TOOLS}")
