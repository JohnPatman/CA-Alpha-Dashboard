import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
from utils.helpers import sf, fmt_date, days_to, ann_ret, pct_colour, spread_colour, risk_colour, scrip_decision
from utils.ui import apply_theme, dark_table

st.set_page_config(page_title="Closed Events · CA Alpha", page_icon="◆", layout="wide", initial_sidebar_state="expanded")
apply_theme()
DB    = "data/events.db"
TODAY = date.today()

# ═════════════════════════════════════════════════════════════════════════════
# DATA, events with passed deadlines (the closed pipeline)
# ═════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def get_closed():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c    = conn.cursor()
    today = TODAY.isoformat()

    # All events whose election deadline has passed
    base = c.execute("""
        SELECT e.*, julianday(?) - julianday(e.election_deadline) AS days_ago
        FROM events e
        WHERE e.election_deadline < ? AND e.status='LIVE'
        ORDER BY e.election_deadline DESC
    """, (today, today)).fetchall()

    # Enrich with detail tables
    enriched = []
    for r in base:
        eid = r["event_id"]
        det = {}
        if r["event_type"] in ("scrip_dividend","fx_election"):
            sd = c.execute(
                "SELECT * FROM scrip_details WHERE event_id=?", (eid,)
            ).fetchone()
            if sd:
                det = dict(sd)
        elif r["event_type"] == "rights_issue":
            rd = c.execute(
                "SELECT * FROM rights_details WHERE event_id=?", (eid,)
            ).fetchone()
            if rd:
                det = dict(rd)
        elif r["event_type"] in ("tender_offer","dutch_auction"):
            td = c.execute(
                "SELECT * FROM tender_details WHERE event_id=?", (eid,)
            ).fetchone()
            if td:
                det = dict(td)
        elif r["event_type"] in ("scheme_of_arrangement","merger"):
            md = c.execute(
                "SELECT * FROM merger_details WHERE event_id=?", (eid,)
            ).fetchone()
            if md:
                det = dict(md)
        enriched.append((dict(r), det))

    conn.close()
    return enriched

rows = get_closed()

# ── Compute synthetic outcomes ────────────────────────────────────────────────
def scrip_outcome(ev, det):
    """Was the optimal election made? Was deadline met? What alpha was captured?"""
    default_ = (det.get("election_default") or "").upper() or "CASH"

    if ev["event_type"] == "fx_election":
        arb = sf(det.get("fx_arbitrage_pct"))
        opt = (det.get("optimal_election") or "").upper()
        if opt and opt != default_:
            return ("ELECTED " + opt, "alpha",
                    f"{arb:+.2f}% / {int(abs(arb or 0)*100)}bps CCY arb captured" if arb else "Arb captured")
        return ("DEFAULT ACCEPTED", "neutral", "Default was optimal, no action needed")

    # scrip_dividend, compute the premium canonically (net of WHT) so a small
    # negative gross that WHT turns net-positive is recognised, and a genuinely
    # negative premium is never shown as captured alpha.
    prem, opt, action_req, _ = scrip_decision(
        det.get("cash_amount"), det.get("scrip_issue_price"), det.get("scrip_ratio"),
        det.get("scrip_discount_pct"), det.get("withholding_tax_pct"), det.get("election_default"))
    if action_req and prem is not None and prem > 0:
        return ("ELECTED " + opt, "alpha", f"{prem:+.2f}% scrip premium captured")
    return ("DEFAULT ACCEPTED", "neutral", "Default was optimal, no action needed")

def rights_outcome(ev, det):
    sub = sf(det.get("subscription_price"))
    cur = sf(det.get("current_price"))
    nil = sf(det.get("nil_paid_value"))
    disc = sf(det.get("discount_to_terp_pct"))
    if sub and cur and cur > sub:
        return ("RIGHTS TAKEN UP", "alpha",
                f"Subscribed at {ev['currency']} {sub:.2f}  ·  nil-paid value {ev['currency']} {nil:.2f}/right" if nil else
                f"Subscribed at {ev['currency']} {sub:.2f}")
    elif nil and nil > 0:
        return ("NIL-PAID SOLD", "alpha",
                f"Sold rights at {ev['currency']} {nil:.2f}/right  ·  disc to TERP {disc:.1f}%" if disc else
                f"Nil-paid rights sold in market")
    else:
        return ("LAPSED, RIGHTS FORFEITED", "loss", "Subscription price exceeded market, rights worthless")

def tender_outcome(ev, det):
    tp   = sf(det.get("tender_price"))
    cur  = sf(det.get("current_price"))
    prem = sf(det.get("premium_to_mkt_pct"))
    pro  = sf(det.get("estimated_proration_pct"))
    odd  = sf(det.get("odd_lot_threshold"))
    guar = det.get("odd_lot_guaranteed")
    if tp and cur:
        eff_prem = prem * (pro/100) if pro else prem
        ann_r    = eff_prem/max(sf(det.get("days_ago_approx",14)),1)*365 if eff_prem else None
        note = (f"Full fill, guaranteed (odd lot ≤{int(odd)})" if odd and guar==1
                else f"~{pro:.0f}% fill accepted at tender price" if pro else "Shares accepted at tender price")
        return ("SETTLED AT TENDER PRICE", "alpha",
                f"{ev['currency']} {tp:.2f} tender price  ·  +{prem:.1f}% premium  ·  {note}")
    return ("TENDER COMPLETED", "neutral", "Settlement processing")

def merger_outcome(ev, det):
    spread = sf(det.get("spread_to_terms_pct"))
    brk    = str(det.get("break_risk","")).upper()
    reg    = str(det.get("regulatory_status","")).upper()
    cps    = sf(det.get("cash_per_share"))
    acq    = det.get("acquirer","")
    if reg == "CLEARED":
        return ("REGULATORY CLEARED", "alpha",
                f"Awaiting court sanction  ·  spread +{spread:.2f}%  ·  {acq}" if spread else f"Reg cleared  ·  {acq}")
    else:
        return ("SCHEME PENDING", "neutral",
                f"Break risk {brk}  ·  spread +{spread:.2f}%  ·  {acq}" if spread else f"{acq}")

# Determine outcome for each event
def get_outcome(ev, det):
    t = ev["event_type"]
    if t in ("scrip_dividend","fx_election"): return scrip_outcome(ev, det)
    if t == "rights_issue":                   return rights_outcome(ev, det)
    if t in ("tender_offer","dutch_auction"): return tender_outcome(ev, det)
    if t in ("scheme_of_arrangement","merger"): return merger_outcome(ev, det)
    return ("COMPLETED", "neutral", "")

outcomes = [(ev, det, *get_outcome(ev, det)) for ev, det in rows]
n_alpha   = sum(1 for *_, outcome_type, _ in outcomes if outcome_type == "alpha")
n_neutral = sum(1 for *_, outcome_type, _ in outcomes if outcome_type == "neutral")
n_loss    = sum(1 for *_, outcome_type, _ in outcomes if outcome_type == "loss")

# ── Header ────────────────────────────────────────────────────────────────────
st.title("◆ Closed Events · Trade Outcomes")
st.markdown(
    f"<div style='font-family:IBM Plex Mono;font-size:0.70rem;color:#6a8090;"
    f"padding:0.3rem 0 0.7rem;border-bottom:1px solid #182436;margin-bottom:0.8rem'>"
    f"Elections that have closed, deadline passed, payment pending or settled. "
    f"Shows whether the model recommendation was actionable and what outcome was achieved."
    f"</div>",
    unsafe_allow_html=True
)

k1,k2,k3,k4 = st.columns(4)
k1.metric("Closed Events",    len(outcomes))
k2.metric("Alpha Captured",   n_alpha,   delta=f"{n_alpha/max(len(outcomes),1)*100:.0f}%")
k3.metric("Neutral / Default",n_neutral)
k4.metric("Rights Lapsed",    n_loss)

# ── Event type breakdown ──────────────────────────────────────────────────────
type_map = {"scrip_dividend":"Scrip Dividend","fx_election":"CCY Election",
            "rights_issue":"Rights Issue","tender_offer":"Tender Offer",
            "dutch_auction":"Dutch Auction","scheme_of_arrangement":"Scheme","merger":"Merger"}

st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1, OUTCOME CARDS (most recent first)
# ═════════════════════════════════════════════════════════════════════════════
def outcome_card(ev, det, outcome_label, outcome_type, outcome_detail):
    o_col  = {"alpha":"#00d4aa","neutral":"#6a8090","loss":"#ff3355"}.get(outcome_type,"#6a8090")
    o_icon = {"alpha":"✓","neutral":"—","loss":"✗"}.get(outcome_type,"")
    days_ago = int(sf(ev.get("days_ago")) or 0)
    e_label  = type_map.get(ev["event_type"], ev["event_type"])
    return (
        f"<div style='background:#080c12;border:1px solid #182436;border-top:2px solid {o_col};"
        f"padding:0.5rem 0.75rem;font-family:IBM Plex Mono;"
        f"height:100%;box-sizing:border-box'>"
        f"<div style='display:flex;justify-content:space-between;align-items:baseline'>"
        f"<span style='font-size:0.75rem;color:#c8d8e8;font-weight:500'>{ev['ticker']}</span>"
        f"<span style='font-size:0.55rem;color:#304050'>{days_ago}d ago</span></div>"
        f"<div style='font-size:0.58rem;color:#304050;margin:0.1rem 0'>"
        f"{e_label} &nbsp;·&nbsp; {ev['company_name'][:24]} &nbsp;·&nbsp; {ev['country']}</div>"
        f"<div style='font-size:0.62rem;color:{o_col};font-weight:500;margin-top:0.2rem'>"
        f"{o_icon} &nbsp;{outcome_label}</div>"
        f"<div style='font-size:0.60rem;color:#6a8090;margin-top:0.1rem'>{outcome_detail}</div>"
        f"<div style='font-size:0.55rem;color:#304050;margin-top:0.2rem'>"
        f"Deadline: {ev['election_deadline']} &nbsp;·&nbsp; Payment: {fmt_date(ev.get('payment_date'))}</div>"
        f"</div>"
    )

# Show all closed events in a 3-column grid (align-items:stretch equalises row heights)
if outcomes:
    cards = [outcome_card(ev, det, label, o_type, detail)
             for (ev, det, label, o_type, detail) in outcomes]
    st.markdown(
        "<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:0.4rem'>"
        + "".join(cards) + "</div>",
        unsafe_allow_html=True,
    )
else:
    st.info("No closed events found.")

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2, CLOSED EVENTS TABLE (sortable)
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  Closed Events · Full Table", expanded=False):
    table_rows = []
    hl = {}
    for i, (ev, det, label, o_type, detail) in enumerate(outcomes):
        days_ago = int(sf(ev.get("days_ago")) or 0)
        e_lbl    = type_map.get(ev["event_type"],ev["event_type"])
        row = [
            ev["ticker"],
            ev["company_name"][:22],
            ev["country"],
            e_lbl,
            ev["election_deadline"] or "—",
            f"{days_ago}d ago",
            label,
            detail[:40] + ("…" if len(detail)>40 else ""),
        ]
        table_rows.append(row)
        o_col = {"alpha":"#00d4aa","neutral":"#6a8090","loss":"#ff3355"}.get(o_type,"#6a8090")
        hl[i]  = {6: o_col}

    if table_rows:
        dark_table(table_rows,
                   ["Ticker","Company","Country","Type","Deadline","Closed","Outcome","Detail"],
                   hl)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3, LIFECYCLE NOTE
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  How this module works", expanded=False):
    st.markdown(
        "<div style='font-family:IBM Plex Mono;font-size:0.70rem;color:#6a8090;line-height:1.9'>"
        "<strong style='color:#c8d8e8'>Election lifecycle</strong><br>"
        "Corporate action elections run from announcement to election deadline. "
        "After the deadline, the event enters a settlement/payment period before closing. "
        "This module shows events in that post-deadline window: the election is closed, "
        "the outcome is determined, but the event remains LIVE until payment date passes.<br><br>"
        "<strong style='color:#c8d8e8'>Outcome classification</strong><br>"
        "<span style='color:#00d4aa'>✓ Alpha Captured</span>: the model's non-default recommendation "
        "was available to act on, resulting in a better outcome than the default election.<br>"
        "<span style='color:#6a8090'>— Neutral</span>: default election was optimal, "
        "or no actionable spread above friction costs.<br>"
        "<span style='color:#ff3355'>✗ Loss / Forfeit</span>: rights lapsed, "
        "or election deadline missed (instructive: shows cost of inaction).<br><br>"
        "<strong style='color:#c8d8e8'>Feedback loop</strong><br>"
        "As events close and new ones open, this module tracks whether the signal "
        "generation logic produces actionable recommendations. With live data, "
        "outcomes would be compared to actual settlement prices to measure model accuracy."
        "</div>",
        unsafe_allow_html=True
    )
