"""Filter S&P 500 headlines that reveal same-day market outcomes.

These articles are market-recap pieces published after the close (or during
the session) that describe what the market actually did that day.  Keeping
them would constitute data leakage: the model would be trained on
information that was not available at the prediction time (before market
open or at open).

Two categories of leakage are removed:
  A. Daily market-recap articles — identified by their title prefix:
       "Stock market today:", "Wall Street today:", "World markets today:",
       "Finance & Markets -- Monday's Markets:", etc.
  B. Same-day outcome articles — headlines that name the S&P 500 and use a
       present/past-tense verb to describe what the index DID that session:
       rises, rose, falls, fell, gains, gained, drops, dropped, closes at,
       ends at, hits record, hit record, logs, logged, …

Forward-looking, analytical, or predictive headlines (e.g.
"S&P 500 could soar …", "S&P 500 nears record highs — analysts say …") are
intentionally kept: they reflect pre-market or general market sentiment, not
revealed outcomes.

Usage (from project root, with .venv activated):
    python scripts/filter_sp500_headlines.py
"""

import re
from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).parent.parent
INPUT_PATH  = PROJECT_ROOT / "data" / "processed" / "wsj_sp500_proquest.csv"
OUTPUT_PATH = PROJECT_ROOT / "data" / "processed" / "wsj_sp500_proquest_filtered.csv"
REMOVED_PATH = PROJECT_ROOT / "data" / "processed" / "wsj_sp500_removed_headlines.csv"

# ---------------------------------------------------------------------------
# Category A: daily recap title prefixes (case-insensitive)
# ---------------------------------------------------------------------------
RECAP_PREFIXES = [
    r"stock market today",
    r"wall street today",
    r"world markets today",
    r"markets & finance\s*--\s*(monday|tuesday|wednesday|thursday|friday)'?s markets",
    r"markets\s*--\s*(monday|tuesday|wednesday|thursday|friday)'?s markets",
    r"finance & markets\s*--\s*(monday|tuesday|wednesday|thursday|friday)'?s markets",
    r"exchange\s*---\s*(friday|monday|tuesday|wednesday|thursday)'?s markets",
]
RECAP_PREFIX_RE = re.compile(
    "|".join(RECAP_PREFIXES),
    flags=re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Category B: same-day outcome phrases linked to the S&P 500 / Dow / Nasdaq
# (only flag if they appear to describe a same-day event, not a prediction)
# ---------------------------------------------------------------------------
# These match headlines where a known index name is combined with a
# present/past-tense verb describing the outcome of that session.
OUTCOME_PATTERNS = [
    # "S&P 500 rises / fell / soars / drops today"
    r"s&p\s*500\b.{0,80}?\b(rose|rises|soared|soars|surged|surges|"
    r"jumped|jumps|climbed|climbs|gained|gains|"
    r"fell|falls|dropped|drops|tumbled|tumbles|plunged|plunges|"
    r"sank|sinks|slid|slides|slumped|slumps|retreated|retreats|"
    r"closed at|closes at|ends at|ended at|"
    r"hits record|hit record|notched record|caps off|logged|logs|"
    r"finishes|finished)\b",
    # "Dow Falls / gains X points"
    r"\b(dow|nasdaq)\b.{0,50}?\b(falls|fell|rose|rises|gained|gains|"
    r"drops|dropped|surged|surges|tumbled|tumbles|"
    r"closes at|closed at|hits record|hit record)\b",
    # "Wall Street rises / falls"
    r"\bwall street\b.{0,50}?\b(rises|rose|falls|fell|gains|gained|"
    r"drops|dropped|surged|tumbled|plunged)\b",
    # Explicit "S&P 500 up / down X%" style
    r"s&p\s*500\b.{0,30}?\b(up|down)\s+\d+",
]
OUTCOME_RE = re.compile(
    "|".join(OUTCOME_PATTERNS),
    flags=re.IGNORECASE,
)

# ---------------------------------------------------------------------------
# Safe-phrase whitelist — even if the above patterns match, headlines
# containing these phrases are KEPT because they are clearly forward-looking
# or analytical (not reporting today's outcome).
# ---------------------------------------------------------------------------
SAFE_PHRASES = [
    r"\bcould\b",
    r"\bwould\b",
    r"\bmight\b",
    r"\bmay\b",
    r"\bcan\b",
    r"\bexpect",
    r"\bforecast",
    r"\bpredict",
    r"\bhistory (says|shows|suggest)",
    r"\banalysts? say",
    r"\bstrategist",
    r"\byear.end target",
    r"\bprice target",
    r"\boutlook",
    r"\bin \d{4}\b",         # "S&P 500 in 2025"
    r"\bnext year\b",
    r"\bby year.end\b",
    r"\bthis year\b.*\btarget\b",
    r"\bif\b",
    r"\bshould\b",
    r"\bhow .{0,40} performed\b",   # historical look-back, not today
    r"\bfirst term\b",
    r"\bObama\b",
    r"\b20\d\d.s?\b",       # decade references
]
SAFE_RE = re.compile(
    "|".join(SAFE_PHRASES),
    flags=re.IGNORECASE,
)


def is_leakage(headline: str) -> tuple[bool, str]:
    """Return (True, reason) if the headline likely reveals same-day market outcome."""
    h = str(headline)

    # Category A: unambiguous recap prefixes
    if RECAP_PREFIX_RE.search(h):
        return True, "daily market recap"

    # Category B: outcome verb pattern — but only if NOT in the safe-phrase list
    if OUTCOME_RE.search(h):
        if SAFE_RE.search(h):
            return False, ""
        return True, "same-day outcome phrase"

    return False, ""


def main() -> None:
    df = pd.read_csv(INPUT_PATH)
    print(f"Loaded {len(df)} headlines from {INPUT_PATH.name}")

    leakage_flags  = []
    leakage_reasons = []
    for _, row in df.iterrows():
        flag, reason = is_leakage(row["headline"])
        leakage_flags.append(flag)
        leakage_reasons.append(reason)

    df["leakage"]        = leakage_flags
    df["leakage_reason"] = leakage_reasons

    removed = df[df["leakage"]].copy()
    clean   = df[~df["leakage"]].drop(columns=["leakage", "leakage_reason"])

    print(f"\nHeadlines flagged for removal : {len(removed)}")
    print(f"Headlines retained            : {len(clean)}")
    print(f"Unique dates retained         : {clean['date'].nunique()}")

    # Show every removed headline (encode safely for Windows terminal)
    print("\n--- REMOVED HEADLINES ---")
    for _, row in removed.iterrows():
        safe_headline = str(row['headline']).encode('ascii', errors='replace').decode('ascii')
        print(f"  [{row['date']}] ({row['leakage_reason']})")
        print(f"    {safe_headline}")

    clean.to_csv(OUTPUT_PATH, index=False)
    removed[["date", "headline", "leakage_reason"]].to_csv(REMOVED_PATH, index=False)

    print(f"\nFiltered dataset saved to : {OUTPUT_PATH}")
    print(f"Removed headlines saved to: {REMOVED_PATH}")


if __name__ == "__main__":
    main()
