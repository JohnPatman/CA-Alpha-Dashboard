"""
rebase_dates.py
───────────────
Shifts all event dates in events.db forward so they remain current relative
to today. Safe to run repeatedly — each run calculates only the INCREMENTAL
gap since the last run, not the full gap from the original build date.

Usage:
    python3 rebase_dates.py

On first run after a fresh build, uses DB_ORIGINAL_REF as the baseline.
On subsequent runs, uses the ref_date stored in the meta table.
"""

import sqlite3
from datetime import date

DB_PATH           = "data/events.db"
DB_ORIGINAL_REF   = date(2026, 5, 25)   # reference date used when DB was built
TARGET_DATE       = date.today()

conn = sqlite3.connect(DB_PATH)
c    = conn.cursor()

# ── Read last-run ref_date from meta, or fall back to original build date ─────
c.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
row = c.execute("SELECT value FROM meta WHERE key='ref_date'").fetchone()
if row and row[0]:
    last_ref = date.fromisoformat(row[0])
else:
    last_ref = DB_ORIGINAL_REF

offset_days = (TARGET_DATE - last_ref).days

if offset_days == 0:
    print(f"DB already current (ref_date={last_ref}) — no rebase needed.")
    conn.close()
    exit()

DATE_COLS = [
    ("events",         "announcement_date"),
    ("events",         "ex_date"),
    ("events",         "record_date"),
    ("events",         "election_deadline"),
    ("events",         "payment_date"),
    ("events",         "settlement_date"),
    ("merger_details", "court_sanction_date"),
    ("merger_details", "long_stop_date"),
]

print(f"Rebasing: {last_ref} → {TARGET_DATE} (+{offset_days} days incremental)")

for table, col in DATE_COLS:
    try:
        c.execute(f"""
            UPDATE {table}
            SET {col} = date({col}, '+{offset_days} days')
            WHERE {col} IS NOT NULL
        """)
        n = c.rowcount
        if n > 0:
            print(f"  ✓ {table}.{col}: {n} rows updated")
    except Exception as e:
        print(f"  ✗ {table}.{col}: {e}")

# Update stored ref_date so next run is incremental
c.execute("INSERT OR REPLACE INTO meta VALUES ('ref_date', ?)", (TARGET_DATE.isoformat(),))

# ── Snap any date that landed on a weekend to the nearest business day ─────────
# Corporate action dates (ex, record, deadline, payment, etc.) fall on business
# days; a fixed-offset shift can land them on a Saturday or Sunday. strftime('%w')
# gives 0=Sun..6=Sat, so Sat→Fri (−1) and Sun→Mon (+1), the nearest weekday.
print("\nSnapping weekend dates to business days:")
for table, col in DATE_COLS:
    try:
        c.execute(f"""
            UPDATE {table}
            SET {col} = CASE strftime('%w', {col})
                WHEN '6' THEN date({col}, '-1 day')
                WHEN '0' THEN date({col}, '+1 day')
                ELSE {col} END
            WHERE {col} IS NOT NULL
              AND strftime('%w', {col}) IN ('0','6')
        """)
        if c.rowcount > 0:
            print(f"  ✓ {table}.{col}: {c.rowcount} weekend dates snapped")
    except Exception as e:
        print(f"  ✗ {table}.{col}: {e}")

conn.commit()
conn.close()
print(f"\nDone. Next rebase will shift from {TARGET_DATE}.")
