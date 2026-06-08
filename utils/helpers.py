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
