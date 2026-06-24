import streamlit as st
import sqlite3
from datetime import date, timedelta
from utils.helpers import sf, fmt_date, days_to, tdot, ann_ret, scrip_decision
from utils.ui import apply_theme

st.set_page_config(page_title="Priority Briefing · CA Alpha", page_icon="◆", layout="wide", initial_sidebar_state="expanded")
apply_theme()
DB    = "data/events.db"
TODAY = date.today()

# ═════════════════════════════════════════════════════════════════════════════
# DATA, pull top alpha opportunities cross-module
# ═════════════════════════════════════════════════════════════════════════════
@st.cache_data(ttl=300)
def get_briefing():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    today = TODAY.isoformat()

    # ── Scrip / CCY: pulled raw; scrip optimality computed in Python so the
    #    briefing always agrees with the Scrip Arbitrage module (single source
    #    of truth). The stored optimal_election / scrip_discount_pct are NOT
    #    trusted for scrip rows. ──────────────────────────────────────────────
    scrip = c.execute("""
        SELECT e.event_id, e.ticker, e.company_name, e.country, e.currency,
               e.election_deadline, julianday(e.election_deadline)-julianday(?) AS days,
               s.scrip_discount_pct, s.election_default, s.optimal_election,
               s.withholding_tax_pct AS wht, s.fx_arbitrage_pct AS ccy_arb,
               s.cash_amount, s.scrip_issue_price, s.scrip_ratio,
               e.event_type
        FROM events e JOIN scrip_details s ON e.event_id=s.event_id
        WHERE e.status='LIVE'
        AND e.election_deadline IS NOT NULL AND e.election_deadline >= ?
    """, (today, today)).fetchall()

    # ── Rights: take-up events with upcoming deadlines ────────────────────────
    rights = c.execute("""
        SELECT e.event_id, e.ticker, e.company_name, e.country, e.currency,
               e.election_deadline, julianday(e.election_deadline)-julianday(?) AS days,
               r.subscription_price AS sub, r.current_price AS cur, r.nil_paid_value AS nil_pd,
               r.discount_to_terp_pct AS disc, r.rights_ratio, r.gross_proceeds_mn AS proceeds
        FROM events e JOIN rights_details r ON e.event_id=r.event_id
        WHERE e.status='LIVE' AND e.event_type='rights_issue'
        AND e.election_deadline IS NOT NULL AND e.election_deadline >= ?
        AND r.subscription_price IS NOT NULL AND r.current_price IS NOT NULL
        AND r.current_price > r.subscription_price
        ORDER BY days ASC
        LIMIT 6
    """, (today, today)).fetchall()

    # ── Tenders: highest annualised return with upcoming deadline ─────────────
    tenders = c.execute("""
        SELECT e.event_id, e.ticker, e.company_name, e.country, e.currency,
               e.election_deadline, julianday(e.election_deadline)-julianday(?) AS days,
               t.tender_price AS tp, t.current_price AS cur, t.premium_to_mkt_pct AS prem,
               t.estimated_proration_pct AS pro, t.max_value_mn AS size,
               t.odd_lot_threshold AS odd_thresh, t.odd_lot_guaranteed AS odd_guar,
               t.tender_type
        FROM events e JOIN tender_details t ON e.event_id=t.event_id
        WHERE e.status='LIVE' AND e.event_type='tender_offer'
        AND (e.election_deadline IS NULL OR e.election_deadline >= ?)
        AND t.premium_to_mkt_pct IS NOT NULL AND t.tender_type='FIXED'
        ORDER BY CASE WHEN e.election_deadline IS NOT NULL
                 THEN t.premium_to_mkt_pct/MAX(julianday(e.election_deadline)-julianday(?),1)
                 ELSE 0 END DESC
        LIMIT 6
    """, (today, today, today)).fetchall()

    # ── Mergers: best risk-adjusted, LOW risk first, highest spread ──────────
    mergers = c.execute("""
        SELECT e.event_id, e.ticker, e.company_name, e.country, e.currency,
               m.spread_to_terms_pct AS spread, m.break_risk, m.regulatory_status AS reg,
               m.court_sanction_date, m.long_stop_date, m.acquirer,
               m.consideration_type AS consid, m.cash_per_share AS cps,
               julianday(COALESCE(m.court_sanction_date, m.long_stop_date, e.election_deadline))
                   - julianday(?) AS days_to_close
        FROM events e JOIN merger_details m ON e.event_id=m.event_id
        WHERE e.status='LIVE'
        AND (m.long_stop_date IS NULL OR m.long_stop_date >= ?)
        ORDER BY CASE m.break_risk WHEN 'LOW' THEN 0 WHEN 'MEDIUM' THEN 1 ELSE 2 END,
                 m.spread_to_terms_pct DESC
        LIMIT 6
    """, (today, today)).fetchall()

    conn.close()

    # Post-process scrip/CCY rows: compute scrip optimality canonically and keep
    # only events where the company default is suboptimal (action required).
    scrip_out = []
    for r in scrip:
        d = dict(r)
        if d["event_type"] == "scrip_dividend":
            prem, opt, action_req, _ = scrip_decision(
                d["cash_amount"], d["scrip_issue_price"], d["scrip_ratio"],
                d["scrip_discount_pct"], d["wht"], d["election_default"])
            if not action_req:
                continue
            d["prem"] = prem
            d["optimal_election"] = opt
        else:  # fx_election, CCY arb logic already correct in the module
            deflt = str(d["election_default"]).upper() if d["election_default"] else ""
            opt   = str(d["optimal_election"]).upper() if d["optimal_election"] else ""
            if deflt == opt:
                continue
            d["prem"] = d["ccy_arb"]
        scrip_out.append(d)

    scrip_out.sort(key=lambda x: (
        sf(x["days"]) if x["days"] is not None else 9e9,
        -abs((sf(x["prem"]) or 0) + (sf(x["ccy_arb"]) or 0))))
    scrip_out = scrip_out[:10]

    return (scrip_out,
            [dict(r) for r in rights],
            [dict(r) for r in tenders],
            [dict(r) for r in mergers])

scrip_rows, rights_rows, tender_rows, merger_rows = get_briefing()

# Total alpha at risk (cost of doing nothing today across all action-required events)
total_scrip_alpha   = sum((abs(sf(r["prem"]) or 0)) for r in scrip_rows if r["prem"])
total_ccy_alpha_bps = sum((abs(sf(r["ccy_arb"]) or 0)*100) for r in scrip_rows
                          if r["event_type"]=="fx_election" and r["ccy_arb"])
n_critical  = sum(1 for r in scrip_rows + tender_rows + rights_rows
                  if r["days"] is not None and r["days"] <= 3)
n_this_week = sum(1 for r in scrip_rows + tender_rows + rights_rows
                  if r["days"] is not None and 3 < r["days"] <= 7)

# ── Header ────────────────────────────────────────────────────────────────────
st.title("◆ Priority Briefing")
st.markdown(
    f"<div style='font-family:IBM Plex Mono;font-size:0.70rem;color:#6a8090;"
    f"padding:0.3rem 0 0.7rem;border-bottom:1px solid #182436;margin-bottom:0.8rem'>"
    f"Cross-module alpha summary &nbsp;·&nbsp; {TODAY.isoformat()} "
    f"&nbsp;·&nbsp; <span style='color:#c8d8e8'>{n_critical} critical</span> (≤3d) "
    f"&nbsp;·&nbsp; <span style='color:#d4c200'>{n_this_week} this week</span> (4–7d) "
    f"&nbsp;·&nbsp; action required on all flagged events below"
    f"</div>",
    unsafe_allow_html=True
)

# ── KPI strip ─────────────────────────────────────────────────────────────────
k1,k2,k3,k4 = st.columns(4)
k1.metric("Critical ≤3d",  n_critical,  help="Events where election deadline is 3 days or fewer")
k2.metric("This Week 4–7d",n_this_week, help="Elections closing in 4–7 days")
k3.metric("Actionable Scrip/CCY", len(scrip_rows), help="Events where default ≠ optimal election")
k4.metric("Live M&A Deals", len(merger_rows), help="Active merger/scheme positions")

st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1, CRITICAL: ≤3d
# ═════════════════════════════════════════════════════════════════════════════
def urgency_badge(days):
    if days is None: return ""
    d = int(days)
    if d <= 1: return f"<span style='background:#ff335520;color:#ff3355;padding:1px 6px;font-size:0.55rem;border:1px solid #ff335540'>TODAY</span>"
    if d <= 3: return f"<span style='background:#ff335510;color:#ff3355;padding:1px 6px;font-size:0.55rem;border:1px solid #ff335530'>{d}d</span>"
    if d <= 7: return f"<span style='background:#d4c20010;color:#d4c200;padding:1px 6px;font-size:0.55rem;border:1px solid #d4c20030'>{d}d</span>"
    return f"<span style='color:#6a8090;font-size:0.60rem'>{d}d</span>"

def event_card(ticker, company, etype, days, action_text, value_text, note="", currency=""):
    badge   = urgency_badge(days)
    e_color = {"scrip_dividend":"#00d4aa","fx_election":"#d4c200","rights_issue":"#f5a623",
               "tender_offer":"#00b4d8","scheme_of_arrangement":"#c8d8e8","merger":"#c8d8e8"
               }.get(etype, "#6a8090")
    e_label = {"scrip_dividend":"SCRIP","fx_election":"CCY","rights_issue":"RIGHTS",
               "tender_offer":"TENDER","scheme_of_arrangement":"SCHEME","merger":"MERGER"
               }.get(etype, etype.upper()[:6])
    return (
        f"<div style='background:#080c12;border:1px solid #182436;border-left:3px solid {e_color};"
        f"padding:0.5rem 0.75rem;margin-bottom:0.4rem;font-family:IBM Plex Mono;"
        f"min-height:5.9rem;box-sizing:border-box'>"
        f"<div style='display:flex;justify-content:space-between;align-items:baseline'>"
        f"<span style='font-size:0.75rem;color:#c8d8e8;font-weight:500'>{ticker}</span>"
        f"<span>{badge}</span></div>"
        f"<div style='font-size:0.58rem;color:#304050;margin:0.1rem 0'>"
        f"<span style='color:{e_color};font-size:0.48rem;letter-spacing:0.1em'>{e_label}</span>"
        f" &nbsp;{company[:28]}</div>"
        f"<div style='font-size:0.65rem;color:#6a8090;margin-top:0.2rem'>"
        f"<span style='color:#c8d8e8'>Action:</span> {action_text}</div>"
        f"<div style='font-size:0.70rem;color:{e_color};font-weight:500;margin-top:0.1rem'>{value_text}</div>"
        f"{'<div style=\"font-size:0.58rem;color:#304050;margin-top:0.1rem\">' + note + '</div>' if note else ''}"
        f"</div>"
    )

# Collect all critical items (≤3d)
critical_items = []
for r in scrip_rows:
    d = sf(r["days"])
    if d is None or d > 3: continue
    prem  = sf(r["prem"])
    arb   = sf(r["ccy_arb"])
    wht   = sf(r["wht"]) or 0
    if r["event_type"]=="scrip_dividend":
        opt = str(r.get("optimal_election","")).upper()
        if wht > 0 and opt == "SCRIP" and (prem is None or prem < 1.0):
            val = f"WHT {wht:.0f}% uplift, elect scrip for full dividend value"
        else:
            val = f"{prem:+.2f}% scrip premium" if prem is not None else "Scrip premium"
    elif r["event_type"]=="fx_election" and arb:
        val = f"{arb:+.2f}% / {int(abs(arb or 0)*100)}bps CCY arb"
    else:
        val = "—"
    action = f"Elect {r['optimal_election']} (default is {r['election_default']})"
    wht_note = "" if val.startswith("WHT") else (f"WHT {wht:.0f}% drag on cash div" if wht > 0 else "")
    critical_items.append((d, event_card(r["ticker"],r["company_name"],r["event_type"],d,action,val,wht_note)))

for r in tender_rows:
    d = sf(r["days"])
    if d is None or d > 3: continue
    prem = sf(r["prem"])
    ann  = prem/max(d,1)*365 if prem and d and d>0 else None
    val  = f"{ann:.0f}% ann  (+{prem:.1f}% · {int(d)}d)" if ann else f"{prem:+.1f}% spread"
    odd  = f"Odd lot ≤{int(r['odd_thresh'])} guaranteed fill" if r["odd_thresh"] and r["odd_guar"]==1 else ""
    critical_items.append((d, event_card(r["ticker"],r["company_name"],"tender_offer",d,
                            "Tender shares before deadline",val,odd)))

for r in rights_rows:
    d = sf(r["days"])
    if d is None or d > 3: continue
    nil = sf(r["nil_pd"])
    val = f"Nil-paid = {r['currency']} {nil:.2f}/right" if nil else "Take up or sell nil-paid rights"
    critical_items.append((d, event_card(r["ticker"],r["company_name"],"rights_issue",d,
                            "Subscribe or sell nil-paid before deadline",val)))

if critical_items:
    critical_items.sort(key=lambda x: x[0])
    st.markdown(
        "<p style='font-size:0.52rem;letter-spacing:0.16em;text-transform:uppercase;"
        "color:#ff3355;margin-bottom:0.4rem'>🔴  Critical: deadline ≤3 days</p>",
        unsafe_allow_html=True
    )
    cols = st.columns(min(len(critical_items), 3))
    for i, (_, card_html) in enumerate(critical_items):
        cols[i % 3].markdown(card_html, unsafe_allow_html=True)
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2, THIS WEEK: 4–7d
# ═════════════════════════════════════════════════════════════════════════════
week_items = []
for r in scrip_rows:
    d = sf(r["days"])
    if d is None or d <= 3 or d > 7: continue
    prem  = sf(r["prem"]); arb = sf(r["ccy_arb"])
    wht_w = sf(r["wht"]) or 0
    if r["event_type"]=="scrip_dividend":
        opt = str(r.get("optimal_election","")).upper()
        val = f"WHT {wht_w:.0f}% uplift, elect scrip" if (wht_w > 0 and opt == "SCRIP" and (prem is None or prem < 1.0)) else (f"{prem:+.2f}% scrip premium" if prem is not None else "Scrip premium")
    elif r["event_type"]=="fx_election" and arb:
        val = f"{arb:+.2f}% / {int(abs(arb or 0)*100)}bps CCY arb"
    else:
        val = "—"
    action = f"Elect {r['optimal_election']}, default {r['election_default']}"
    week_items.append((d, event_card(r["ticker"],r["company_name"],r["event_type"],d,action,val)))

for r in tender_rows:
    d = sf(r["days"])
    if d is None or d <= 3 or d > 7: continue
    prem = sf(r["prem"])
    ann  = prem/max(d,1)*365 if prem and d and d>0 else None
    val  = f"{ann:.0f}% ann  (+{prem:.1f}% · {int(d)}d)" if ann else f"{prem:+.1f}%"
    week_items.append((d, event_card(r["ticker"],r["company_name"],"tender_offer",d,
                        "Tender before deadline",val)))

for r in rights_rows:
    d = sf(r["days"])
    if d is None or d <= 3 or d > 7: continue
    nil = sf(r["nil_pd"])
    val = f"Nil-paid = {r['currency']} {nil:.2f}/right  ·  disc {r['disc']:.1f}% to TERP" if nil else "Take up or sell nil-paid"
    week_items.append((d, event_card(r["ticker"],r["company_name"],"rights_issue",d,
                        "Subscribe or sell nil-paid before deadline",val)))

if week_items:
    week_items.sort(key=lambda x: x[0])
    st.markdown(
        "<p style='font-size:0.52rem;letter-spacing:0.16em;text-transform:uppercase;"
        "color:#d4c200;margin-bottom:0.4rem'>🟡  This week: deadline 4–7 days</p>",
        unsafe_allow_html=True
    )
    cols = st.columns(min(len(week_items), 3))
    for i, (_, card_html) in enumerate(week_items):
        cols[i % 3].markdown(card_html, unsafe_allow_html=True)
    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3, ACTIVE MONITORING: M&A positions
# ═════════════════════════════════════════════════════════════════════════════
if merger_rows:
    st.markdown(
        "<p style='font-size:0.52rem;letter-spacing:0.16em;text-transform:uppercase;"
        "color:#00d4aa;margin-bottom:0.4rem'>🟢  Active M&A monitoring</p>",
        unsafe_allow_html=True
    )
    m_cols = st.columns(min(len(merger_rows), 3))
    for i, r in enumerate(merger_rows):
        spread = sf(r["spread"])
        d_close = sf(r["days_to_close"])
        ann_m  = spread/max(d_close,1)*365 if spread and d_close and d_close>0 else None
        risk_col = {"LOW":"#00d4aa","MEDIUM":"#d4c200","HIGH":"#ff3355"}.get(
            str(r["break_risk"]).upper(),"#6a8090")
        reg_txt = str(r["reg"]).upper() if r["reg"] and str(r["reg"])!="nan" else "PENDING"
        action  = "Monitor spread, no election required" if str(r["consid"])=="CASH" else \
                  "Consider share/mixed election optimisation"
        val_txt = (f"{spread:+.2f}% spread  ·  {ann_m:.0f}% ann" if ann_m
                   else f"{spread:+.2f}% spread") if spread else "—"
        note_txt = (f"Reg: {reg_txt}  ·  Break risk: {str(r['break_risk']).upper()}  "
                    f"·  Acquirer: {str(r['acquirer'])[:16] if r['acquirer'] else '—'}")
        card = event_card(r["ticker"], r["company_name"],
                          "scheme_of_arrangement" if str(r["consid"] or "CASH")=="CASH" else "merger",
                          int(d_close) if d_close and d_close>0 else None,
                          action, val_txt, note_txt)
        m_cols[i % 3].markdown(card, unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 4, ALPHA SUMMARY TABLE (all action items ranked by urgency)
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  Full Action List · All Events Requiring Instruction", expanded=False):
    all_items = []
    for r in scrip_rows:
        d   = sf(r["days"])
        prem = sf(r["prem"]); arb = sf(r["ccy_arb"])
        val  = prem if r["event_type"]=="scrip_dividend" else arb
        etype = "SCRIP" if r["event_type"]=="scrip_dividend" else "CCY"
        all_items.append([
            r["ticker"], r["company_name"][:22], etype,
            f"{int(d)}d" if d is not None else "—",
            f"{r['election_deadline']}",
            f"Elect {r['optimal_election']}",
            f"{val:+.2f}%" if val else "—",
            r["currency"],
        ])
    for r in tender_rows:
        d    = sf(r["days"])
        prem = sf(r["prem"])
        ann  = prem/max(d,1)*365 if prem and d and d>0 else None
        all_items.append([
            r["ticker"], r["company_name"][:22], "TENDER",
            f"{int(d)}d" if d is not None else "—",
            f"{r['election_deadline'] or '—'}",
            "Tender shares",
            f"{ann:.0f}% ann" if ann else f"{prem:+.1f}%" if prem else "—",
            r["currency"],
        ])
    for r in rights_rows:
        d   = sf(r["days"])
        nil = sf(r["nil_pd"])
        all_items.append([
            r["ticker"], r["company_name"][:22], "RIGHTS",
            f"{int(d)}d" if d is not None else "—",
            f"{r['election_deadline']}",
            "Subscribe / sell nil-paid",
            f"Nil-paid {r['currency']} {nil:.2f}" if nil else "—",
            r["currency"],
        ])

    all_items.sort(key=lambda x: (int(x[3].replace("d","")) if x[3]!="—" else 999))

    from utils.ui import dark_table
    if all_items:
        hl = {}
        for i,row in enumerate(all_items):
            days_n = int(row[3].replace("d","")) if row[3]!="—" else 999
            hl[i] = {0: '#ff3355' if days_n<=1 else '#d4c200' if days_n<=3 else '#f5a623' if days_n<=7 else '#6a8090'}
        dark_table(all_items, ["Ticker","Company","Type","Days","Deadline","Action","Alpha / Value","CCY"], hl)
    else:
        st.info("No action-required events found.")

st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
st.markdown(
    "<p style='font-family:IBM Plex Mono;font-size:0.55rem;color:#304050'>"
    "Priority Briefing pulls live data across all nine modules. Urgency is determined by "
    "election deadline proximity. Alpha estimates assume default position size, "
    "navigate to individual modules for position-specific P&L. All data synthetic.</p>",
    unsafe_allow_html=True
)
