"""
patch_review5.py — idempotent cleanup from the fifth review pass.

Two changes:

1. Remove ES003 (IBE.MC). Iberdrola already carries a well-specified scrip
   dividend (E074: realistic issue price, 19% Spanish withholding). ES003 was a
   second, weaker scrip record for the same name that was priced in the previous
   pass; it duplicated E074 and carried 0% withholding on a Spanish dividend,
   which is wrong. Removing it leaves Iberdrola represented once, correctly.

2. Realistic withholding on the European scrips priced last pass. They were
   seeded with 0% withholding, which is wrong for those jurisdictions and
   understated the scrip premium (the scrip's edge over cash comes largely from
   avoiding the cash-dividend withholding drag). Set to standard statutory
   non-resident dividend rates, consistent with how E074 uses 19% for Spain.
   Hong Kong (HK003) has no dividend withholding and stays at 0%.

Safe to run repeatedly. The source builder carries the same rates and omits
ES003, so a full rebuild stays consistent.
"""
import sqlite3, os

DB = os.path.join(os.path.dirname(__file__), "data", "events.db")

WHT = {
    "IE001": 25,  # CRH.L      Ireland
    "FI001": 30,  # NESTE.HE   Finland
    "NL003": 15,  # ASML.AS    Netherlands
    "SE003": 30,  # ERIC-B.ST  Sweden
    "BE003": 30,  # UCB.BR     Belgium
    "IT003": 26,  # UCG.MI     Italy
}


def main():
    con = sqlite3.connect(DB)
    cur = con.cursor()

    cur.execute("DELETE FROM scrip_details WHERE event_id = 'ES003'")
    removed = cur.execute("DELETE FROM events WHERE event_id = 'ES003'").rowcount

    wht_set = 0
    for eid, rate in WHT.items():
        wht_set += cur.execute(
            "UPDATE scrip_details SET withholding_tax_pct = ? "
            "WHERE event_id = ? AND COALESCE(withholding_tax_pct, 0) = 0",
            (rate, eid),
        ).rowcount

    con.commit()
    con.close()
    print(f"ES003 duplicate removed: {removed}")
    print(f"Withholding rates set: {wht_set}")


if __name__ == "__main__":
    main()
