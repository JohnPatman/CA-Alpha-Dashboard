"""
patch_review_fixes.py
─────────────────────
Run from project root:  python3 patch_review_fixes.py

Idempotent data fixes from the full-project review. Safe to run repeatedly.

1. Currency-unit mislabel: pence-quoted UK scrip events (event currency GBX)
   had cash_currency='GBP' while the dividend amount is stored in pence. This
   made the Scrip card compare e.g. cash "GBP 3.05" to scrip "GBX 3.13". GBX and
   GBP are the same currency; only the unit was wrong. Aligns cash_currency to
   the trading currency for the GBX/GBP case only — genuine cross-currency
   dividends (GBX stock paying USD, etc.) are left untouched.

2. Event-type / rights-type mismatch: EMAAR.DU (Emaar Properties) was tagged
   event_type='rights_issue' but rights_type='OPEN_OFFER', with no tradeable
   nil-paid line — i.e. a non-renounceable open offer. This made the Home
   by-type count (4 open offers) disagree with the Rights page (5). Aligns
   event_type to 'open_offer'.
"""

import sqlite3, sys
from pathlib import Path

DB = Path("data/events.db")
if not DB.exists():
    sys.exit(f"ERROR: {DB} not found. Run from project root.")

conn = sqlite3.connect(DB)
c = conn.cursor()

# ── Fix 1: GBX/GBP cash_currency unit ─────────────────────────────────────────
rows = c.execute("""
    SELECT s.event_id, e.ticker, s.cash_amount
    FROM   scrip_details s JOIN events e ON s.event_id = e.event_id
    WHERE  e.currency = 'GBX' AND s.cash_currency = 'GBP'
""").fetchall()
if rows:
    for eid, ticker, cash in rows:
        c.execute("UPDATE scrip_details SET cash_currency='GBX' WHERE event_id=?", (eid,))
        print(f"✓  {ticker:8} cash_currency GBP → GBX  (div {cash:g}p)")
    print(f"   {len(rows)} cash_currency row(s) fixed.")
else:
    print("–  cash_currency: no GBX/GBP mismatches (already patched).")

# ── Fix 2: EMAAR.DU open-offer classification ─────────────────────────────────
n = c.execute("""
    UPDATE events SET event_type='open_offer'
    WHERE event_id IN (
        SELECT e.event_id FROM events e JOIN rights_details r ON e.event_id=r.event_id
        WHERE e.event_type='rights_issue' AND r.rights_type='OPEN_OFFER'
    )
""").rowcount
print(f"✓  event_type rights_issue → open_offer: {n} row(s) fixed."
      if n else "–  event_type: no rights/open_offer mismatches (already patched).")

conn.commit()
conn.close()
print("\n✓  Review data fixes committed.")
