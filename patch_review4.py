"""
patch_review4.py — idempotent cleanup from the fourth review pass.

Two changes:

1. Scrip reference prices. Eight live scrip dividends carried an announced ratio
   and discount but no scrip_issue_price, so they could not be valued and showed
   no premium. Given the announced ratio (1 per N) and cash dividend, the
   cash-neutral reference price is N x cash, which is how the other scrip events
   in the set are built. Setting it here lets them compute a premium in line with
   the rest (small, driven by their discount, since all eight are zero-WHT).

2. Duplicate currency elections. Three fx_election records (E004 HSBC, E006 RIO,
   E113 BHP.AX) duplicated a dividend the same ticker already carries as a
   separate, correctly-typed currency election (U006/E014/E115), with identical
   cash and currency. They were originally mislabelled scrip dividends; retyping
   them to fx_election made the duplication visible (two currency elections per
   name, one near, one ~5 weeks later). The near-term twin is kept; these later
   redundant records are removed.

Safe to run repeatedly. The source builder (build_events_db_v2.py) carries the
same prices and omits these three records, so a full rebuild stays consistent.
"""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), "data", "events.db")

ISSUE_PRICES = {
    "IE001": 176.00,  # CRH.L     1 per 55 x EUR 3.20
    "FI001": 40.80,   # NESTE.HE  1 per 48 x EUR 0.85
    "NL003": 209.00,  # ASML.AS   1 per 38 x EUR 5.50
    "SE003": 74.40,   # ERIC-B.ST 1 per 62 x SEK 1.20
    "BE003": 92.40,   # UCB.BR    1 per 44 x EUR 2.10
    "ES003": 34.08,   # IBE.MC    1 per 71 x EUR 0.48
    "IT003": 59.40,   # UCG.MI    1 per 36 x EUR 1.65
    "HK003": 16.24,   # 2388.HK   1 per 58 x HKD 0.28
}

REDUNDANT = ["E004", "E006", "E113"]


def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    priced = 0
    for eid, px in ISSUE_PRICES.items():
        priced += cur.execute(
            "UPDATE scrip_details SET scrip_issue_price = ? "
            "WHERE event_id = ? AND scrip_issue_price IS NULL",
            (px, eid),
        ).rowcount

    qs = ",".join("?" * len(REDUNDANT))
    cur.execute(f"DELETE FROM scrip_details WHERE event_id IN ({qs})", REDUNDANT)
    removed = cur.execute(f"DELETE FROM events WHERE event_id IN ({qs})", REDUNDANT).rowcount

    con.commit()
    con.close()
    print(f"Scrip issue prices set: {priced}")
    print(f"Redundant duplicate events removed: {removed}")


if __name__ == "__main__":
    main()
