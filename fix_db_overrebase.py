"""
fix_db_overrebase.py
--------------------
Corrects the cumulative rebase drift: the weekly GitHub Actions job was
applying the full offset from the original 2026-05-25 reference each run
instead of the incremental delta, causing dates to drift progressively
further into the future.

This script detects the current drift and shifts ALL dates backwards by the
excess amount so the DB is aligned to today. Run once, then the fixed
rebase_dates.py will maintain it correctly going forward.

Run from project root:  python3 fix_db_overrebase.py
"""
import sqlite3
from datetime import date, timedelta

DB_PATH          = "data/events.db"
DB_ORIGINAL_REF  = date(2026, 5, 25)

conn = sqlite3.connect(DB_PATH)
c    = conn.cursor()

# ── Detect current effective reference date from NG.L (E007) ─────────────────
# E007 was created as d(2) from original ref = 2026-05-27
row = c.execute("SELECT election_deadline FROM events WHERE event_id='E007'").fetchone()
if not row or not row[0]:
    print("Cannot detect drift — E007 not found.")
    conn.close()
    exit(1)

ORIGINAL_E007  = date(2026, 5, 27)      # d(2) from 2026-05-25
current_E007   = date.fromisoformat(row[0])
effective_ref  = DB_ORIGINAL_REF + (current_E007 - ORIGINAL_E007)
today          = date.today()
over_rebase    = (effective_ref - today).days

print(f"Effective DB reference date : {effective_ref}")
print(f"Today                       : {today}")
print(f"Over-rebase drift           : +{over_rebase} days")

if over_rebase <= 0:
    print("\nDB is not over-rebased — no correction needed.")
    conn.close()
    exit(0)

print(f"\nShifting ALL dates back by {over_rebase} days to align with today...")

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

for table, col in DATE_COLS:
    try:
        c.execute(f"""
            UPDATE {table}
            SET {col} = date({col}, '-{over_rebase} days')
            WHERE {col} IS NOT NULL
        """)
        n = c.rowcount
        if n > 0:
            print(f"  ✓ {table}.{col}: {n} rows corrected")
    except Exception as e:
        print(f"  ✗ {table}.{col}: {e}")

# Update meta so rebase_dates.py uses today as the new baseline
c.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
c.execute("INSERT OR REPLACE INTO meta VALUES ('ref_date', ?)", (today.isoformat(),))
conn.commit()

# Verify
verify = c.execute("SELECT election_deadline FROM events WHERE event_id='E007'").fetchone()[0]
days_out = (date.fromisoformat(verify) - today).days
print(f"\n✓  NG.L (E007) deadline: {verify}  ({days_out}d from today) — expected ~2d")

# Count urgents and passed
urgent = c.execute(
    "SELECT COUNT(*) FROM events WHERE election_deadline BETWEEN ? "
    "AND date(?, '+7 days') AND status='LIVE'",
    (today.isoformat(), today.isoformat())
).fetchone()[0]
passed = c.execute(
    "SELECT COUNT(*) FROM events WHERE election_deadline < ? AND status='LIVE'",
    (today.isoformat(),)
).fetchone()[0]
print(f"   Deadlines ≤7d : {urgent}")
print(f"   Passed ddl    : {passed}")
print(f"\nDone. Run rebase_dates.py going forward to maintain alignment.")
conn.close()
