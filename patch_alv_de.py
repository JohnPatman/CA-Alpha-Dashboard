"""
patch_alv_de.py
───────────────
Run from project root: python3 patch_alv_de.py

Fixes ALV.DE (Allianz SE) P-event scrip_discount_pct value.
The value was stored as -1.20 (cash better than scrip) but the event
was seeded with optimal_election=SCRIP, which requires a positive premium.
Corrects to +1.20 (scrip 1.20% better than cash after WHT adjustment).
"""
import sqlite3, sys
from pathlib import Path

DB = Path("data/events.db")
if not DB.exists():
    sys.exit(f"ERROR: {DB} not found. Run from project root.")

conn = sqlite3.connect(DB)
c = conn.cursor()

# Find ALV.DE event(s) where scrip_discount_pct is negative but optimal=SCRIP
rows = c.execute("""
    SELECT s.event_id, e.ticker, s.scrip_discount_pct, s.optimal_election, s.election_default
    FROM scrip_details s JOIN events e ON s.event_id=e.event_id
    WHERE e.ticker='ALV.DE' AND s.scrip_discount_pct < 0 AND s.optimal_election='SCRIP'
""").fetchall()

if rows:
    for row in rows:
        new_val = abs(row[2])   # flip negative to positive
        c.execute("UPDATE scrip_details SET scrip_discount_pct=? WHERE event_id=?",
                  (new_val, row[0]))
        print(f"✓  Fixed ALV.DE ({row[0]}): scrip_discount_pct {row[2]:.2f} → +{new_val:.2f}%")
    conn.commit()
else:
    # Check if already correct
    check = c.execute("""
        SELECT s.event_id, s.scrip_discount_pct FROM scrip_details s
        JOIN events e ON s.event_id=e.event_id WHERE e.ticker='ALV.DE'
    """).fetchall()
    if check:
        for row in check:
            print(f"–  ALV.DE ({row[0]}): scrip_discount_pct={row[1]} — already correct or different issue")
    else:
        print("–  ALV.DE not found in DB")

conn.close()
