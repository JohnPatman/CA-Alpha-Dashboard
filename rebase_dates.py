"""
rebase_dates.py
───────────────
Shifts all event dates in events.db forward so they are current relative
to today. Run this whenever the demo DB has aged out.

Usage:
    python3 rebase_dates.py

It calculates the gap between the DB reference date (2026-05-25) and today,
then adds that offset to every date column in the events table.
Preserves relative spacing between events — a 7-day deadline stays 7 days
out, a 14-day one stays 14 days out, etc.
"""

import sqlite3
from datetime import date, timedelta

DB_PATH       = "data/events.db"
DB_REF_DATE   = date(2026, 5, 25)   # original reference date used when DB was built
TARGET_DATE   = date.today()        # rebase so events are relative to today

offset_days   = (TARGET_DATE - DB_REF_DATE).days

if offset_days == 0:
    print("DB is already current — no rebase needed.")
    exit()

DATE_COLS = [
    ("events", "announcement_date"),
    ("events", "ex_date"),
    ("events", "record_date"),
    ("events", "election_deadline"),
    ("events", "payment_date"),
    ("events", "settlement_date"),
    ("merger_details", "court_sanction_date"),
    ("merger_details", "long_stop_date"),
]

conn = sqlite3.connect(DB_PATH)
c    = conn.cursor()

print(f"Rebasing: DB ref date {DB_REF_DATE} → today {TARGET_DATE} (+{offset_days} days)")

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

# Also update DB_REF_DATE so next rebase knows where to start from
# (store as a simple metadata table)
c.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
c.execute("INSERT OR REPLACE INTO meta VALUES ('ref_date', ?)", (TARGET_DATE.isoformat(),))

conn.commit()
conn.close()
print(f"\nDone. Re-run build_events_db_v2.py to regenerate from scratch instead.")
