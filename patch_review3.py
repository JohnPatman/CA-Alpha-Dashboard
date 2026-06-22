"""
patch_review3.py — idempotent cleanup from the third deep review.

Retypes events that are labelled `scrip_dividend` but carry only currency-election
data (cash amount, company/market FX rates, dividend currency options, a computed
fx_arbitrage_pct and a currency optimal_election) and NO scrip terms (no ratio, no
issue price). Their data shape is unambiguously an FX election, so they were showing
"—" on the Scrip scanner (nothing to compute) instead of rendering on the CCY
Election scanner. This corrects the label to match the data; nothing is fabricated.

A genuine scrip dividend that also happens to carry FX data but HAS a scrip ratio
is left untouched (the WHERE clause requires both scrip fields to be NULL).

"DRP" flavour notes on the affected rows are realigned to describe a currency
election so the note no longer contradicts the corrected type.

Safe to run repeatedly. The source builder (build_events_db_v2.py) is corrected too,
so a full rebuild stays consistent.
"""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), "data", "events.db")

SIGNATURE = """
    event_type = 'scrip_dividend'
    AND event_id IN (
        SELECT event_id FROM scrip_details
        WHERE scrip_ratio IS NULL AND scrip_issue_price IS NULL
          AND company_fx_rate IS NOT NULL AND dividend_currency_opts IS NOT NULL
    )
"""


def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    retyped = cur.execute(
        f"UPDATE events SET event_type = 'fx_election' WHERE {SIGNATURE}"
    ).rowcount

    # Realign any "DRP" flavour notes on the now-corrected rows
    notes = cur.execute(
        """UPDATE events SET notes = REPLACE(REPLACE(notes, ' DRP', ' currency election'), 'DRP', 'currency election')
           WHERE event_type = 'fx_election' AND notes LIKE '%DRP%'"""
    ).rowcount

    con.commit()
    con.close()
    print(f"Retyped scrip_dividend -> fx_election: {retyped}")
    print(f"DRP notes realigned: {notes}")


if __name__ == "__main__":
    main()
