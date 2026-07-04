"""
rebase_dates.py
───────────────
Keeps all event dates in events.db current relative to today.

How it works. On first run (fresh source build) it snapshots every date into a
date_base table. On every run it recomputes each date from that immutable base:

    shifted = base_date + (today - BUILD_REF)

then snaps weekend landings to a business day. Early-cycle dates (announcement,
ex, record) snap back to Friday; late-cycle dates (deadline, payment,
settlement, court sanction, long stop) snap forward to Monday. Snapping
backward for early and forward for late means an early date can never cross
its late counterpart, so date ordering is preserved.

Because every run derives from the base rather than the previous run's output,
the result depends only on today's date. Running twice on the same day is a
no-op. The previous incremental version shifted yesterday's dates by one day
and then snapped Saturday back to Friday, so a Friday date shifted to Saturday
snapped straight back: a net move of zero. Under a daily cron every date
eventually migrated to a Friday and froze there while today kept moving.

Usage:
    python3 rebase_dates.py

The snapshot is only valid against a fresh source build (dates anchored at
BUILD_REF). A known-anchor check refuses to snapshot anything else.
"""

import sqlite3
import sys
from datetime import date, timedelta

DB_PATH   = "data/events.db"
BUILD_REF = date(2026, 5, 25)   # anchor used by build_events_db_v2.py (its TODAY)

# Known-original anchor used to validate a fresh build before snapshotting:
# E007 (NG.L) is created as d(2) from BUILD_REF.
ANCHOR_EVENT    = "E007"
ANCHOR_ORIGINAL = (BUILD_REF + timedelta(days=2)).isoformat()   # 2026-05-27

EARLY_COLS = [
    ("events", "announcement_date"),
    ("events", "ex_date"),
    ("events", "record_date"),
]
LATE_COLS = [
    ("events", "election_deadline"),
    ("events", "payment_date"),
    ("events", "settlement_date"),
    ("merger_details", "court_sanction_date"),
    ("merger_details", "long_stop_date"),
]
DATE_COLS = EARLY_COLS + LATE_COLS


def _snap(d, early):
    wd = d.weekday()                       # Mon=0 .. Sun=6
    if wd == 5:                            # Saturday
        return d - timedelta(days=1) if early else d + timedelta(days=2)
    if wd == 6:                            # Sunday
        return d - timedelta(days=2) if early else d + timedelta(days=1)
    return d


def rebase(today=None):
    today = today or date.today()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)")
    c.execute(
        "CREATE TABLE IF NOT EXISTS date_base ("
        "tbl TEXT, row_id INTEGER, col TEXT, value TEXT, "
        "PRIMARY KEY (tbl, row_id, col))"
    )

    # ── First run: snapshot originals, but only from a verified fresh build ──
    if c.execute("SELECT COUNT(*) FROM date_base").fetchone()[0] == 0:
        row = c.execute(
            "SELECT election_deadline FROM events WHERE event_id=?",
            (ANCHOR_EVENT,),
        ).fetchone()
        if not row or row[0] != ANCHOR_ORIGINAL:
            conn.close()
            sys.exit(
                f"date_base is empty but {ANCHOR_EVENT} deadline is "
                f"{row[0] if row else 'missing'}, expected {ANCHOR_ORIGINAL}. "
                f"Rebuild the DB from source (build_events_db_v2.py + "
                f"add_past_urgent_events.py) before first rebase."
            )
        for tbl, col in DATE_COLS:
            c.execute(
                f"INSERT INTO date_base (tbl, row_id, col, value) "
                f"SELECT '{tbl}', rowid, '{col}', {col} FROM {tbl} "
                f"WHERE {col} IS NOT NULL"
            )
        n = c.execute("SELECT COUNT(*) FROM date_base").fetchone()[0]
        print(f"Snapshotted {n} original dates (base ref {BUILD_REF}).")

    # ── Every run: recompute all dates from base + total offset, snap once ──
    offset = (today - BUILD_REF).days
    early_set = set(EARLY_COLS)
    updated = 0
    for tbl, col in DATE_COLS:
        early_col = (tbl, col) in early_set
        for row_id, base_val in c.execute(
            "SELECT row_id, value FROM date_base WHERE tbl=? AND col=?",
            (tbl, col),
        ).fetchall():
            base = date.fromisoformat(base_val)
            # Dates seeded before the build anchor are intentionally past
            # (P-series "recently closed"); snap them backward so they can
            # never land on today and flicker onto the live scanners.
            early = early_col or base < BUILD_REF
            new = _snap(base + timedelta(days=offset), early)
            c.execute(
                f"UPDATE {tbl} SET {col}=? WHERE rowid=? AND {col} IS NOT ?",
                (new.isoformat(), row_id, new.isoformat()),
            )
            updated += c.rowcount

    c.execute("INSERT OR REPLACE INTO meta VALUES ('ref_date', ?)", (today.isoformat(),))
    conn.commit()
    conn.close()
    print(f"Rebased to {today} (offset +{offset}d from {BUILD_REF}); "
          f"{updated} dates changed.")


if __name__ == "__main__":
    rebase()
