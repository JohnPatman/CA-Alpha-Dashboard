"""
utils/helpers.py
----------------
Pure-Python helpers shared across all CA Alpha Dashboard page modules.
No Streamlit imports — safe to import at module level without side effects.
"""
from datetime import date


# ── Type-safe converters ─────────────────────────────────────────────────────

def sf(v, d=None):
    """Safe float conversion. Returns d (default None) on any failure."""
    try:
        if v is None or str(v) == 'nan':
            return d
        return float(v)
    except Exception:
        return d


def fmt_date(d):
    """Return YYYY-MM-DD string or '—' for None/nan/unparseable."""
    if not d or str(d) == 'nan':
        return '—'
    return str(d)[:10]


def days_to(d):
    """
    Days from today to a date string/value.
    Returns None on parse failure, negative int for past dates.
    """
    try:
        return (date.fromisoformat(str(d)[:10]) - date.today()).days
    except Exception:
        return None


# ── Traffic-light urgency ────────────────────────────────────────────────────

def tdot(days):
    """
    Emoji traffic-light for deadline urgency.
    ⚫ = passed  🔴 = ≤3d  🟠 = ≤7d  🟡 = ≤14d  🟢 = >14d  ⚪ = no date
    """
    if days is None: return '⚪'
    if days < 0:     return '⚫'
    if days <= 3:    return '🔴'
    if days <= 7:    return '🟠'
    if days <= 14:   return '🟡'
    return '🟢'


# ── Financial calculation helpers ────────────────────────────────────────────

import re


def parse_ratio(s):
    """Parse an 'N per M' (scrip) or 'N for M' (rights) ratio string into (N, M)
    ints, or (None, None). Single source of truth for both event families."""
    if not s or str(s) == 'nan':
        return None, None
    m = re.search(r'(\d+)\s+(?:per|for)\s+(\d+)', str(s), re.I)
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)


def calc_scrip_prem(cash, scrip_px, ratio, wht=0.0, inferred_px=None):
    """
    Canonical scrip-vs-cash decision metric — the single source of truth shared
    by the Scrip Arbitrage page, the Priority Briefing, and the Home Top-Opps card.

    Returns (scrip_prem_pct, cash_net, scrip_val, optimal) — all per share.

    scrip_prem_pct  > 0  → scrip worth more than cash net of WHT → optimal SCRIP
    The premium is computed against the current market price (inferred_px) when
    supplied, falling back to the issue/reference price.
    """
    rn, rd = parse_ratio(ratio)
    if not rn or not rd or not cash:
        return None, None, None, "—"
    cur_px = inferred_px or scrip_px
    if not cur_px:
        return None, None, None, "—"
    cash_net  = cash * (1 - (wht or 0.0) / 100)
    scrip_val = (rn / rd) * cur_px
    prem      = (scrip_val - cash_net) / cash_net * 100 if cash_net else 0
    opt       = "SCRIP" if prem > 0 else "CASH"
    return prem, cash_net, scrip_val, opt


def scrip_decision(cash_amount, scrip_issue_price, scrip_ratio,
                   scrip_discount_pct, withholding_tax_pct, election_default):
    """
    Wrapper that takes raw scrip_details fields and returns the full decision
    tuple: (prem_pct, optimal_election, action_required, inferred_current_px).

    `scrip_discount_pct` is the stored issue-price-to-market figure used ONLY to
    infer the current market price (P_inferred = issue_px / (1 + disc/100)); it is
    NOT the scrip premium. The premium and optimal election are computed here so
    every page agrees. action_required is True when the company default differs
    from the computed optimal election.
    """
    cash = sf(cash_amount)
    sp   = sf(scrip_issue_price)
    disc = sf(scrip_discount_pct)
    wht  = sf(withholding_tax_pct, 0.0)
    inferred = sp / (1 + disc / 100) if (sp and disc is not None and (1 + disc / 100) != 0) else sp
    prem, _, _, opt = calc_scrip_prem(cash, sp, scrip_ratio, wht, inferred)
    default = str(election_default).upper() if election_default and str(election_default) != 'nan' else "CASH"
    action_req = (default != opt) if opt != "—" else False
    return prem, opt, action_req, inferred


def ann_ret(prem_pct, days):
    """
    Annualised return from a percentage spread over N calendar days.
    Returns None if inputs are missing or days <= 0.
    """
    if prem_pct is None or not days or days <= 0:
        return None
    return prem_pct / days * 365


# ── Colour helpers ───────────────────────────────────────────────────────────
# All return hex colour strings for use inside dark_table highlight dicts.

def pct_colour(v):
    """Green if v > 0, red if v < -1, amber otherwise. Used for scrip premium."""
    if v is None: return '#6a8090'
    if v > 0:     return '#00d4aa'
    if v < -1:    return '#ff3355'
    return '#f5a623'


def arb_colour(v):
    """Green for high arb (>2%), yellow for mid (>0.5%), grey for low/zero."""
    if v is None: return '#6a8090'
    if v > 2.0:   return '#00d4aa'
    if v > 0.5:   return '#d4c200'
    if v > 0:     return '#6a8090'
    return '#ff3355'


def disc_colour(v):
    """Red for deep discount (<-25%), amber for moderate (<-15%), yellow otherwise."""
    if v is None: return '#6a8090'
    if v < -25:   return '#ff3355'
    if v < -15:   return '#f5a623'
    return '#d4c200'


def prem_colour(v):
    """Green for high tender premium (≥10%), yellow for moderate (≥5%)."""
    if v is None: return '#6a8090'
    if v >= 10:   return '#00d4aa'
    if v >= 5:    return '#d4c200'
    return '#6a8090'


def ann_colour(v):
    """Green for ≥100% ann return, yellow for ≥30%, grey below."""
    if v is None: return '#6a8090'
    if v >= 100:  return '#00d4aa'
    if v >= 30:   return '#d4c200'
    return '#6a8090'


def spread_colour(v):
    """Green for spread >3%, yellow for >1%, grey below."""
    if v is None: return '#6a8090'
    if v > 3:     return '#00d4aa'
    if v > 1:     return '#d4c200'
    return '#6a8090'


def risk_colour(v):
    """Green = LOW break risk, amber = MEDIUM, red = HIGH."""
    if not v or str(v) == 'nan': return '#6a8090'
    v = str(v).upper()
    if v == 'LOW':    return '#00d4aa'
    if v == 'MEDIUM': return '#f5a623'
    if v == 'HIGH':   return '#ff3355'
    return '#6a8090'


def reg_colour(v):
    """Green = CLEARED regulatory status, amber = anything else."""
    if not v or str(v) == 'nan': return '#6a8090'
    return '#00d4aa' if str(v).upper() == 'CLEARED' else '#f5a623'
