"""
test_consistency.py — cross-page invariant guard
─────────────────────────────────────────────────
Run:  python3 tests/test_consistency.py      (plain, prints PASS/FAIL)
 or:  pytest tests/test_consistency.py        (CI-style)

These tests lock in the invariants fixed during the project review. The core
class of bug was several pages computing "is scrip optimal?" differently — some
from the canonical calc, some from the stored scrip_discount_pct field (which is
an issue-price input, not the premium). If a future edit reintroduces a direct
read of the stored field for a display/decision, or breaks a data invariant,
these tests fail.
"""

import sqlite3, importlib.util, re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB   = ROOT / "data" / "events.db"

# Load helpers without importing the streamlit-dependent utils package.
_spec = importlib.util.spec_from_file_location("helpers", ROOT / "utils" / "helpers.py")
H = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(H)


def _conn():
    c = sqlite3.connect(DB); c.row_factory = sqlite3.Row
    return c


# ── Data invariants ───────────────────────────────────────────────────────────

def test_no_gbx_event_labelled_gbp_cash():
    """Pence-quoted (GBX) events must not carry a GBP cash_currency (unit mismatch)."""
    c = _conn()
    n = c.execute("""SELECT COUNT(*) FROM scrip_details s JOIN events e ON s.event_id=e.event_id
                     WHERE e.currency='GBX' AND s.cash_currency='GBP'""").fetchone()[0]
    c.close()
    assert n == 0, f"{n} GBX events still labelled GBP cash_currency"


def test_event_type_agrees_with_rights_type():
    """An OPEN_OFFER rights_type must not be tagged event_type='rights_issue'."""
    c = _conn()
    n = c.execute("""SELECT COUNT(*) FROM events e JOIN rights_details r ON e.event_id=r.event_id
                     WHERE e.event_type='rights_issue' AND r.rights_type='OPEN_OFFER'""").fetchone()[0]
    c.close()
    assert n == 0, f"{n} open offers mis-tagged as rights_issue"


def test_open_offers_have_no_nil_paid():
    """Open offers are non-renounceable — they must carry no tradeable nil-paid line."""
    c = _conn()
    n = c.execute("""SELECT COUNT(*) FROM rights_details
                     WHERE rights_type='OPEN_OFFER'
                     AND (nil_paid_value IS NOT NULL OR nil_paid_ticker IS NOT NULL)""").fetchone()[0]
    c.close()
    assert n == 0, f"{n} open offers carry a nil-paid value/ticker (non-renounceable)"


def test_open_offer_counts_reconcile():
    """event_type count of open offers must equal rights_type OPEN_OFFER count."""
    c = _conn()
    by_type = c.execute("SELECT COUNT(*) FROM events WHERE event_type='open_offer'").fetchone()[0]
    by_rtyp = c.execute("""SELECT COUNT(*) FROM events e JOIN rights_details r ON e.event_id=r.event_id
                           WHERE r.rights_type='OPEN_OFFER'""").fetchone()[0]
    c.close()
    assert by_type == by_rtyp, f"open-offer counts disagree: event_type={by_type}, rights_type={by_rtyp}"


# ── Scrip decision invariants (the centerpiece consistency fix) ────────────────

def _scrip_rows():
    c = _conn()
    rows = c.execute("""SELECT e.ticker, s.cash_amount, s.scrip_issue_price, s.scrip_ratio,
                          s.scrip_discount_pct, s.withholding_tax_pct, s.election_default
                        FROM scrip_details s JOIN events e ON s.event_id=e.event_id
                        WHERE e.event_type='scrip_dividend' AND e.status='LIVE'""").fetchall()
    c.close()
    return rows


def test_scrip_decision_resolves_or_degrades_gracefully():
    """Events with complete scrip terms resolve to CASH/SCRIP; events missing
       terms degrade to '—' without error (never a false CASH/SCRIP call)."""
    for r in _scrip_rows():
        complete = r["scrip_issue_price"] is not None and r["scrip_ratio"] is not None and r["cash_amount"] is not None
        _, opt, _, _ = H.scrip_decision(r["cash_amount"], r["scrip_issue_price"], r["scrip_ratio"],
                                         r["scrip_discount_pct"], r["withholding_tax_pct"], r["election_default"])
        if complete:
            assert opt in ("CASH", "SCRIP"), f"{r['ticker']} has full terms but resolved to '{opt}'"
        else:
            assert opt == "—", f"{r['ticker']} missing terms but resolved to '{opt}' (should degrade to '—')"


def test_negative_premium_is_never_scrip_optimal():
    """A non-positive net premium must never recommend electing scrip."""
    for r in _scrip_rows():
        prem, opt, _, _ = H.scrip_decision(r["cash_amount"], r["scrip_issue_price"], r["scrip_ratio"],
                                           r["scrip_discount_pct"], r["withholding_tax_pct"], r["election_default"])
        if prem is not None and prem <= 0:
            assert opt == "CASH", f"{r['ticker']} prem={prem:.2f}% but optimal={opt}"


def test_known_cases_locked():
    """Specific events from the review: regression anchors."""
    want = {"LAND.L": "CASH", "SMDS.L": "CASH", "LMP.L": "SCRIP", "GSK.L": "SCRIP"}
    got = {}
    for r in _scrip_rows():
        if r["ticker"] in want:
            _, opt, _, _ = H.scrip_decision(r["cash_amount"], r["scrip_issue_price"], r["scrip_ratio"],
                                            r["scrip_discount_pct"], r["withholding_tax_pct"], r["election_default"])
            got[r["ticker"]] = opt
    for k, v in want.items():
        assert got.get(k) == v, f"{k}: expected {v}, got {got.get(k)}"


# ── ADR friction invariant ─────────────────────────────────────────────────────

def test_adr_friction_erodes_toward_zero():
    """Friction must pull net arb TOWARD zero, never away. For positive gross
       net<=gross; for negative gross net>=gross. (The original bug pushed
       negative 'buy ADR' arbs further from zero.)"""
    import math
    def net(gross, fr):  # mirrors pages/9_ADR_Pricing.py
        return gross - math.copysign(fr, gross) if gross else -fr
    for gross in (0.516, -0.447, -0.351, 0.166, 3.034):
        for fr in (0.20, 0.25, 0.35):
            n = net(gross, fr)
            if gross >= 0:
                assert n <= gross + 1e-9, f"gross={gross} fr={fr}: net {n} moved away from zero"
            else:
                assert n >= gross - 1e-9, f"gross={gross} fr={fr}: net {n} moved away from zero"


# ── Source guard: scrip consumers must use the canonical helper ────────────────

def test_scrip_consumers_use_canonical_helper():
    """Pages that decide/display scrip optimality must import scrip_decision, so
       none silently revert to reading the stored scrip_discount_pct as a premium."""
    consumers = ["Home.py", "pages/1_Event_Pipeline.py", "pages/2_Scrip_Arbitrage.py",
                 "pages/7_Closed_Events.py", "pages/8_Priority_Briefing.py"]
    for rel in consumers:
        src = (ROOT / rel).read_text()
        assert "scrip_decision" in src, f"{rel} no longer imports/uses scrip_decision"


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    passed = 0
    for fn in fns:
        try:
            fn(); print(f"  PASS  {fn.__name__}"); passed += 1
        except AssertionError as e:
            print(f"  FAIL  {fn.__name__}: {e}")
        except Exception as e:  # noqa
            print(f"  ERROR {fn.__name__}: {e}")
    print(f"\n{passed}/{len(fns)} checks passed.")
    return passed == len(fns)


if __name__ == "__main__":
    import sys
    sys.exit(0 if _run_all() else 1)
