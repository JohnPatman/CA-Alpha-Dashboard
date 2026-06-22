"""
patch_review2.py — idempotent cleanup from the second deep review.

1. Removes P009 (AAL.L fx_election), a past-urgent seed that duplicated the
   existing E083 (same ticker, type, and ex-date). P010/P011 still provide
   past-urgent FX-election examples, so nothing illustrative is lost.
2. Removes 7 orphaned tender_details rows (E051-E054, E058-E060) whose parent
   events were never present, so they could never render.

Safe to run repeatedly. Source scripts (add_past_urgent_events.py,
build_events_db_v2.py) have been corrected too, so a full rebuild stays clean.
"""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), "data", "events.db")


def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    # 1. Remove the duplicate P009 event and any of its detail rows
    detail_tables = ["scrip_details", "rights_details", "tender_details",
                     "merger_details", "spinoff_details", "split_details"]
    for t in detail_tables:
        cur.execute(f"DELETE FROM {t} WHERE event_id = 'P009'")
    p009 = cur.execute("DELETE FROM events WHERE event_id = 'P009'").rowcount

    # 2. Remove any orphaned detail rows across all detail tables (event_id not in events)
    orphans_removed = 0
    for t in detail_tables:
        orphans_removed += cur.execute(
            f"DELETE FROM {t} WHERE event_id NOT IN (SELECT event_id FROM events)"
        ).rowcount

    con.commit()
    con.close()
    print(f"Removed P009 event rows: {p009}")
    print(f"Removed orphaned detail rows: {orphans_removed}")


if __name__ == "__main__":
    main()
