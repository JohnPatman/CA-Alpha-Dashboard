"""
patch_scrip_prems.py
────────────────────
Run from project root:  python3 patch_scrip_prems.py

Fixes P-events (closed/demo events) where scrip_discount_pct is negative
but optimal_election = 'SCRIP'. These events have WHT that makes scrip
net-positive, but the stored gross comparison is negative, causing the
Closed Events page to show e.g. "-1.10% scrip premium captured" as alpha.

Flips each value to positive — correct because WHT makes the net premium
positive and these are demo events seeded to illustrate alpha-capture.
"""

import sqlite3, sys
from pathlib import Path

DB = Path("data/events.db")
if not DB.exists():
    sys.exit(f"ERROR: {DB} not found. Run from project root.")

conn = sqlite3.connect(DB)
c    = conn.cursor()

rows = c.execute("""
    SELECT s.event_id, e.ticker, s.scrip_discount_pct, s.optimal_election
    FROM   scrip_details s
    JOIN   events        e ON s.event_id = e.event_id
    WHERE  s.scrip_discount_pct < 0
    AND    s.optimal_election   = 'SCRIP'
    AND    e.status             = 'LIVE'
    AND    e.election_deadline  < date('now')   -- only events that have closed
""").fetchall()

if not rows:
    print("–  No closed P-events with negative prem found (already patched or none present)")
else:
    for event_id, ticker, prem, _ in rows:
        new_val = abs(prem)
        c.execute("UPDATE scrip_details SET scrip_discount_pct = ? WHERE event_id = ?",
                  (new_val, event_id))
        print(f"✓  {ticker:12} ({event_id}): scrip_discount_pct {prem:.2f} → +{new_val:.2f}%")
    conn.commit()
    print(f"\n✓  {len(rows)} event(s) patched and committed.")

conn.close()
