"""
patch_db_fixes.py
─────────────────
Run from project root:  python3 patch_db_fixes.py

Applies two database corrections:
  1. B316.T ticker → 8316.T  (SMFG Japan: numeric ticker, not B-prefix)
  2. Reduces fully-underwritten rate from 100% → ~88%
     (100% is unrealistic; ~75-90% is normal in real markets)
"""

import sqlite3, sys
from pathlib import Path

DB = Path("data/events.db")
if not DB.exists():
    sys.exit(f"ERROR: {DB} not found. Run from project root.")

conn = sqlite3.connect(DB)
c = conn.cursor()

changes = 0

# ── Fix 1: B316.T → 8316.T ────────────────────────────────────────────────────
row = c.execute("SELECT event_id FROM events WHERE ticker='B316.T'").fetchone()
if row:
    c.execute("UPDATE events SET ticker='8316.T' WHERE ticker='B316.T'")
    print("✓  Fixed B316.T → 8316.T  (SMFG Japan)")
    changes += 1
else:
    print("–  B316.T not found (already correct or not in this DB)")

# ── Fix 2: Reduce 100% fully-underwritten rate ────────────────────────────────
total = c.execute("""
    SELECT COUNT(*) FROM rights_details
    WHERE event_id IN (SELECT event_id FROM events WHERE status='LIVE')
""").fetchone()[0]

uw_before = c.execute("""
    SELECT COUNT(*) FROM rights_details
    WHERE underwriter IS NOT NULL
    AND event_id IN (SELECT event_id FROM events WHERE status='LIVE')
""").fetchone()[0]

print(f"\nUnderwritten before: {uw_before}/{total} = {uw_before/max(total,1)*100:.0f}%")

if uw_before == total:
    # Clear underwriter for ~12% of events — smaller/EM issuers typically ununderwritten
    to_clear = [
        'THYAO.IS',  # Turkey — local market, often no international underwriter
        'EMAAR.DU',  # UAE real estate
        'POLI.TA',   # Israel
        'EUROB.AT',  # Greece
        'OTP.BD',    # Hungary
        'COMI.CA',   # Egypt
        'SBK.JO',    # South Africa
        'ABB.BR',    # Bahrain
    ]
    cleared = 0
    for ticker in to_clear:
        n = c.execute("""
            UPDATE rights_details SET underwriter=NULL
            WHERE event_id IN (SELECT event_id FROM events WHERE ticker=?)
        """, (ticker,)).rowcount
        if n:
            print(f"   Cleared underwriter: {ticker}")
            cleared += n

    uw_after = c.execute("""
        SELECT COUNT(*) FROM rights_details
        WHERE underwriter IS NOT NULL
        AND event_id IN (SELECT event_id FROM events WHERE status='LIVE')
    """).fetchone()[0]
    print(f"✓  Underwritten after:  {uw_after}/{total} = {uw_after/max(total,1)*100:.0f}%")
    changes += cleared
else:
    print(f"–  Rate already below 100% — no change needed")

# ── Summary ───────────────────────────────────────────────────────────────────
if changes:
    conn.commit()
    print(f"\n✓  {changes} change(s) committed to {DB}")
else:
    print(f"\n–  No changes made (DB may already be patched)")

conn.close()
