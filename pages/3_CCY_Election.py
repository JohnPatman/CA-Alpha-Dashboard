import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3
from datetime import date
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="CCY Election Optimiser · CA Alpha", page_icon="◆", layout="wide", initial_sidebar_state="expanded")

CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&display=swap');
:root{--bg:#04060a;--bg-card:#080c12;--accent:#00d4aa;--accent-dim:#00d4aa12;--red:#ff3355;--amber:#f5a623;--yellow:#d4c200;--border:#0e1825;--border-mid:#182436;--border-bright:#243548;--text-primary:#c8d8e8;--text-secondary:#6a8090;--text-muted:#304050;--font-mono:'IBM Plex Mono',monospace;}
html,body,.stApp,[class*="css"]{background:var(--bg)!important;color:var(--text-primary)!important;}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"]{display:none!important;}
.main .block-container{padding:1rem 2rem 3rem!important;max-width:100%!important;}
section[data-testid="stSidebar"],section[data-testid="stSidebar"]>div:first-child{background:var(--bg)!important;border-right:1px solid var(--border-mid)!important;width:220px!important;min-width:220px!important;max-width:220px!important;}
section[data-testid="stSidebar"] *{font-family:var(--font-mono)!important;color:var(--text-secondary)!important;}
section[data-testid="stSidebar"] [aria-current="page"]{color:var(--accent)!important;background:var(--accent-dim)!important;border-radius:0!important;border:none!important;}
section[data-testid="stSidebar"] [aria-current="page"] *{color:var(--accent)!important;background:transparent!important;}
section[data-testid="stSidebar"] a,section[data-testid="stSidebar"] li{border-radius:0!important;border:none!important;}
section[data-testid="stSidebar"] label{font-size:0.58rem!important;letter-spacing:0.14em!important;text-transform:uppercase!important;}
section[data-testid="stSidebar"] .stMarkdown p{font-size:0.58rem!important;letter-spacing:0.14em!important;text-transform:uppercase!important;border-bottom:1px solid var(--border-mid)!important;padding-bottom:0.25rem!important;margin-bottom:0.4rem!important;}
[data-testid="stSidebarCollapseButton"],[data-testid="collapsedControl"]{display:none!important;opacity:0!important;pointer-events:none!important;}
html body section[data-testid="stSidebar"] *::before,html body section[data-testid="stSidebar"] *::after{content:none!important;display:none!important;}
h1{font-family:var(--font-mono)!important;font-size:0.82rem!important;font-weight:500!important;color:var(--accent)!important;letter-spacing:0.18em!important;text-transform:uppercase!important;padding:0.5rem 0 0.4rem!important;border-bottom:1px solid var(--border-mid)!important;margin-bottom:0.8rem!important;}
h2{font-family:var(--font-mono)!important;font-size:0.55rem!important;font-weight:600!important;letter-spacing:0.2em!important;text-transform:uppercase!important;color:var(--text-muted)!important;margin-top:1.4rem!important;margin-bottom:0.4rem!important;padding-bottom:0.25rem!important;border-bottom:1px solid var(--border)!important;}
p{color:var(--text-secondary)!important;font-size:0.72rem!important;font-family:var(--font-mono)!important;line-height:1.5!important;}
strong{color:var(--text-primary)!important;font-weight:500!important;}
[data-testid="stMetric"]{background:var(--bg-card)!important;border:1px solid var(--border-mid)!important;border-top:1px solid var(--border-bright)!important;border-radius:0!important;padding:0.5rem 0.8rem!important;}
[data-testid="stMetric"] label{font-family:var(--font-mono)!important;font-size:0.52rem!important;letter-spacing:0.16em!important;text-transform:uppercase!important;color:var(--text-muted)!important;}
[data-testid="stMetric"] [data-testid="stMetricValue"]{font-family:var(--font-mono)!important;font-size:1.2rem!important;font-weight:400!important;color:var(--text-primary)!important;line-height:1.1!important;}
[data-testid="stMetricDelta"] svg{display:none!important;}[data-testid="stMetricDelta"]{font-family:var(--font-mono)!important;font-size:0.6rem!important;}
[data-testid="stSelectbox"]>div>div{background:var(--bg-card)!important;border:1px solid var(--border-mid)!important;border-radius:0!important;color:var(--text-primary)!important;font-family:var(--font-mono)!important;font-size:0.72rem!important;}
[data-testid="stNumberInput"]>div>div>input{background:var(--bg-card)!important;border:1px solid var(--border-mid)!important;border-radius:0!important;color:var(--text-primary)!important;font-family:var(--font-mono)!important;font-size:0.8rem!important;padding:0.3rem 0.5rem!important;}
[data-testid="stExpander"]{background:transparent!important;border:1px solid var(--border-mid)!important;border-radius:0!important;margin-bottom:0.4rem!important;}
[data-testid="stExpander"] summary{font-family:var(--font-mono)!important;font-size:0.62rem!important;font-weight:600!important;letter-spacing:0.16em!important;text-transform:uppercase!important;color:var(--text-secondary)!important;padding:0.45rem 0.7rem!important;background:var(--bg-card)!important;border-radius:0!important;}
[data-testid="stExpander"] summary:hover{color:var(--text-primary)!important;}
[data-testid="stExpander"][open]>summary{color:var(--accent)!important;border-bottom:1px solid var(--border-mid)!important;}
[data-testid="stExpander"] [data-testid="stExpanderDetails"]{background:var(--bg)!important;padding:0.7rem 0.8rem!important;}
[data-testid="stAlert"],.stAlert{font-family:var(--font-mono)!important;font-size:0.66rem!important;border-radius:0!important;border:0!important;border-left:2px solid var(--accent)!important;background:var(--accent-dim)!important;color:var(--accent)!important;padding:0.3rem 0.6rem!important;}
hr{border-color:var(--border-mid)!important;margin:0.5rem 0!important;}
::-webkit-scrollbar{width:3px;height:3px;}::-webkit-scrollbar-track{background:var(--bg);}::-webkit-scrollbar-thumb{background:var(--border-bright);}
</style>"""
st.markdown(CSS, unsafe_allow_html=True)

import streamlit.components.v1 as _c
_c.html("""<script>(function(){function k(){try{var d=window.parent.document;['stSidebarCollapseButton','collapsedControl'].forEach(function(id){d.querySelectorAll('[data-testid="'+id+'"]').forEach(function(el){el.style.cssText='display:none!important';});});}catch(e){}}k();[100,500,1500].forEach(function(t){setTimeout(k,t);});try{new MutationObserver(k).observe(window.parent.document.body,{childList:true,subtree:true});}catch(e){}})();</script>""", height=1)

DB = "data/events.db"; TODAY = date.today()

def sf(v,d=None):
    try:
        if v is None or str(v)=='nan': return d
        return float(v)
    except: return d

def fmt_date(d):
    if not d or str(d)=='nan': return '—'
    return str(d)[:10]

def days_to(d):
    try: return (date.fromisoformat(str(d)[:10]) - TODAY).days
    except: return None

def tdot(days):
    if days is None: return '⚪'
    if days < 0: return '⚫'
    if days <= 3: return '🔴'
    if days <= 7: return '🟠'
    if days <= 14: return '🟡'
    return '🟢'

def arb_colour(v):
    if v is None: return '#6a8090'
    if v > 2.0: return '#00d4aa'
    if v > 0.5: return '#d4c200'
    if v > 0:   return '#6a8090'
    return '#ff3355'

def dark_table(rows, headers, highlights=None, height=None):
    th = ''.join(f'<th style="padding:0.3rem 0.7rem;font-size:0.52rem;letter-spacing:0.1em;text-transform:uppercase;color:#304050;background:#04060a;border-bottom:1px solid #243548;text-align:left;white-space:nowrap">{h}</th>' for h in headers)
    tbody = ''
    for i,row in enumerate(rows):
        bg = '#080c12' if i%2==0 else '#04060a'
        hl = (highlights or {}).get(i,{})
        cells = ''.join(f'<td style="padding:0.28rem 0.7rem;color:{hl.get(j,"#c8d8e8")};font-size:0.7rem;background:{bg};border-bottom:1px solid #0e1825;white-space:nowrap">{str(v) if v is not None else "—"}</td>' for j,v in enumerate(row))
        tbody += f'<tr>{cells}</tr>'
    h_px = height or min(len(rows)*32+52, 560)
    _c.html(f'<!DOCTYPE html><html><head><link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet"><style>*{{box-sizing:border-box;margin:0;padding:0;}}html,body{{background:#04060a;font-family:"IBM Plex Mono",monospace;}}table{{width:100%;border-collapse:collapse;}}tr:hover td{{background:#0e1825!important;}}</style></head><body><table><thead><tr>{th}</tr></thead><tbody>{tbody}</tbody></table></body></html>', height=h_px, scrolling=True)

@st.cache_data(ttl=300)
def load_ccy():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("""
        SELECT e.event_id, e.ticker, e.company_name, e.country, e.currency,
               e.status, e.election_deadline, e.ex_date, e.payment_date,
               s.cash_amount, s.cash_currency, s.dividend_currency_opts,
               s.company_fx_rate, s.market_fx_rate, s.fx_arbitrage_pct,
               s.election_default, s.withholding_tax_pct, s.optimal_election
        FROM events e JOIN scrip_details s ON e.event_id=s.event_id
        WHERE e.event_type='fx_election'
        AND e.status IN ('LIVE','UPCOMING')
        AND s.rate_pre_deadline=1
        ORDER BY s.fx_arbitrage_pct DESC NULLS LAST
    """, conn)
    conn.close()
    return df

@st.cache_data(ttl=300)
def load_excluded_count():
    conn = sqlite3.connect(DB)
    n = conn.execute("SELECT COUNT(*) FROM events e JOIN scrip_details s ON e.event_id=s.event_id WHERE e.event_type='fx_election' AND e.status IN ('LIVE','UPCOMING') AND s.rate_pre_deadline=0").fetchone()[0]
    conn.close()
    return n

df = load_ccy()
excluded_n = load_excluded_count()

if df.empty:
    st.title("◆ CCY Election Optimiser")
    total_ccy = excluded_n
    st.markdown(
        f"<div style='font-family:IBM Plex Mono;font-size:0.7rem;color:#6a8090;"
        f"border:1px solid #182436;background:#080c12;padding:0.7rem 1rem;margin-top:0.5rem'>"
        f"<strong style='color:#c8d8e8'>No confirmed pre-deadline fixed rate events in dataset.</strong><br><br>"
        f"This module only shows CCY elections where the company announces a fixed FX reference rate "
        f"before the election deadline — creating a genuine arb vs spot. "
        f"<br><span style='color:#304050'>{total_ccy} events excluded — rate set at or after deadline (no locked-in arb).</span>"
        f"</div>",
        unsafe_allow_html=True
    )
    st.stop()

# Pre-compute action_required: default != optimal
def _action(r):
    dflt = str(r["election_default"]).upper().strip() if r["election_default"] and str(r["election_default"])!='nan' else "CASH"
    opt  = str(r["optimal_election"]).upper().strip() if r["optimal_election"] and str(r["optimal_election"])!='nan' else "USD"
    base = str(r["cash_currency"]).upper().strip() if r["cash_currency"] else "USD"
    # Action required if optimal is a non-default currency
    return dflt != opt and opt != base

df["_action"] = [_action(r) for _,r in df.iterrows()]

# ── sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("### ◆ CCY Optimiser")
action_only = st.sidebar.checkbox("Action Required only", value=False)
df_filt = df[df["_action"]] if action_only else df

def ev_label(r):
    d   = days_to(r["election_deadline"])
    arb = sf(r["fx_arbitrage_pct"])
    req = "⚡" if r["_action"] else " "
    return f"{tdot(d)} {req} {r['ticker']} · {r['company_name'][:16]} · {f'{arb:+.2f}%' if arb else '—'}"

labels  = [ev_label(r) for _,r in df_filt.iterrows()]
sel_idx = st.sidebar.selectbox("Event", range(len(labels)), format_func=lambda i: labels[i])
sel_idx = min(sel_idx, max(0, len(df_filt)-1))
ev = df_filt.iloc[sel_idx]

st.sidebar.markdown("---")
st.sidebar.markdown("### ◆ Position")
pos_shares = st.sidebar.number_input("Shares held", min_value=0, value=50000, step=5000)

cash_amt   = sf(ev["cash_amount"])
co_rate    = sf(ev["company_fx_rate"])
mkt_rate   = sf(ev["market_fx_rate"])
arb_pct    = sf(ev["fx_arbitrage_pct"])
wht        = sf(ev["withholding_tax_pct"], 0.0)
optimal    = str(ev["optimal_election"]).strip() if ev["optimal_election"] and str(ev["optimal_election"])!='nan' else "—"
default_el = str(ev["election_default"]).strip() if ev["election_default"] and str(ev["election_default"])!='nan' else "CASH"
base_ccy   = str(ev["cash_currency"]).strip() if ev["cash_currency"] else "USD"
currencies = [c.strip() for c in str(ev["dividend_currency_opts"]).split("|")] if ev["dividend_currency_opts"] and str(ev["dividend_currency_opts"])!='nan' else [base_ccy]
ddl_days   = days_to(ev["election_deadline"])
dot        = tdot(ddl_days)
action_req = ev["_action"]

# Compute per-share values
co_gbp  = cash_amt * co_rate  * (1-wht/100) if cash_amt and co_rate  else None
mkt_gbp = cash_amt * mkt_rate * (1-wht/100) if cash_amt and mkt_rate else None
uplift  = co_gbp - mkt_gbp if co_gbp and mkt_gbp else None
uplift_bps = uplift / mkt_gbp * 10000 if uplift and mkt_gbp else None

# ── page header ───────────────────────────────────────────────────────────────
st.title("◆ CCY Election Optimiser")

# Pre-deadline filter banner
total_ccy = len(df) + excluded_n
st.markdown(
    f"<div style='font-family:IBM Plex Mono;font-size:0.68rem;color:#6a8090;"
    f"border:1px solid #182436;background:#080c12;padding:0.35rem 0.8rem;margin-bottom:0.6rem'>"
    f"◆ &nbsp;Showing <strong style='color:#c8d8e8'>{len(df)} of {total_ccy} CCY elections</strong> where the company"
    f" <strong style='color:#c8d8e8'>fixes the FX reference rate before the election deadline</strong>"
    f" — genuine arb vs spot. "
    f"<span style='color:#304050'>{excluded_n} events excluded (rate set at/after deadline — no locked-in arb).</span>"
    f"</div>",
    unsafe_allow_html=True
)

# Action required banner
action_n = int(df["_action"].sum())
if action_n > 0:
    st.markdown(
        f"<div style='font-family:IBM Plex Mono;font-size:0.72rem;color:#ff3355;"
        f"padding:0.35rem 0.6rem;border:1px solid #ff335540;background:#ff335508;margin-bottom:0.8rem'>"
        f"⚡ &nbsp;<strong style='color:#c8d8e8'>{action_n} events</strong> default to wrong currency — "
        f"alpha is forfeited unless you actively elect. Check Action column below.</div>",
        unsafe_allow_html=True
    )

st.markdown(
    f"<div style='font-family:IBM Plex Mono;font-size:0.72rem;color:#6a8090;"
    f"padding:0.4rem 0 0.6rem;border-bottom:1px solid #182436;margin-bottom:0.9rem'>"
    f"{dot} &nbsp;<span style='color:#c8d8e8;font-weight:500'>{ev['ticker']}</span>"
    f" &nbsp;·&nbsp; {ev['company_name']} &nbsp;·&nbsp; {ev['country']}"
    f" &nbsp;·&nbsp; Currencies: <span style='color:#c8d8e8'>{ev['dividend_currency_opts']}</span>"
    f" &nbsp;·&nbsp; Default: <span style='color:{'#ff3355' if action_req else '#6a8090'}'>{default_el}</span>"
    f" &nbsp;·&nbsp; Optimal: <span style='color:#00d4aa'>{optimal}</span>"
    f" &nbsp;·&nbsp; Deadline: <span style='color:#c8d8e8'>{fmt_date(ev['election_deadline'])} ({ddl_days}d)</span>"
    f"</div>",
    unsafe_allow_html=True
)

# ── KPIs ──────────────────────────────────────────────────────────────────────
k1,k2,k3,k4,k5,k6 = st.columns(6)
k1.metric("Gross Div",        f"{base_ccy} {cash_amt:.4f}/sh" if cash_amt else "—")
k2.metric("Company FX Rate",  f"{co_rate:.4f}" if co_rate else "—", help="Fixed at announcement")
k3.metric("Market FX Rate",   f"{mkt_rate:.4f}" if mkt_rate else "—", help="Current spot")
k4.metric("Arb (% vs cash)",
          f"{arb_pct:+.2f}%" if arb_pct is not None else "—",
          delta=f"{uplift_bps:.0f}bps" if uplift_bps else None,
          delta_color="normal" if arb_pct and arb_pct > 0 else "off")
k5.metric("Optimal Election",  optimal,
          delta="⚡ Must Elect" if action_req else None,
          delta_color="inverse" if action_req else "off")
k6.metric("Cost of Inaction",
          f"GBP {uplift*pos_shares:,.4f}" if uplift and pos_shares > 0 else "—",
          help=f"Lost on {pos_shares:,} shares if default ({default_el}) kept")

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1 — ARB SCANNER
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  Arb Scanner — All Live CCY Elections", expanded=True):
    sc1,sc2,sc3,sc4 = st.columns(4)
    action_n  = int(df["_action"].sum())
    high_arb  = len(df[df["fx_arbitrage_pct"].apply(sf).apply(lambda x: x is not None and x>2.0)])
    mid_arb   = len(df[df["fx_arbitrage_pct"].apply(sf).apply(lambda x: x is not None and 0.5<x<=2.0)])
    urgent_n  = len(df[df["election_deadline"].apply(lambda d: days_to(d) is not None and 0<=days_to(d)<=7)])
    sc1.metric("Action Required",  action_n, delta="⚡ Elect now" if action_n>0 else None, delta_color="inverse" if action_n>0 else "off")
    sc2.metric("High Arb (>2%)",   high_arb, delta="Alpha ◆" if high_arb>0 else None, delta_color="normal")
    sc3.metric("Mid Arb (0.5–2%)", mid_arb)
    sc4.metric("Deadline ≤7d",     urgent_n, delta="Urgent" if urgent_n>0 else None, delta_color="inverse" if urgent_n>0 else "off")

    scan_rows=[]; scan_hl={}
    # Sort: action required first, then by arb desc
    df_scan = df.sort_values(["_action","fx_arbitrage_pct"], ascending=[False,False])
    for i,(_,r) in enumerate(df_scan.iterrows()):
        d       = days_to(r["election_deadline"])
        arb     = sf(r["fx_arbitrage_pct"])
        co      = sf(r["company_fx_rate"])
        mkt     = sf(r["market_fx_rate"])
        cash    = sf(r["cash_amount"])
        opt     = str(r["optimal_election"]).strip() if r["optimal_election"] and str(r["optimal_election"])!='nan' else "—"
        dflt    = str(r["election_default"]).strip() if r["election_default"] and str(r["election_default"])!='nan' else "USD"
        act     = r["_action"]
        bps     = arb * 100 if arb else None
        # Cost of inaction at 50k shares
        wh      = sf(r["withholding_tax_pct"],0.0)
        c_gbp   = cash * co  * (1-wh/100) if cash and co  else None
        m_gbp   = cash * mkt * (1-wh/100) if cash and mkt else None
        uplift_ = (c_gbp - m_gbp) * 50000 if c_gbp and m_gbp else None

        row = [
            f"{tdot(d)} {'⚡' if act else ' '} {r['ticker']}",
            r['company_name'][:20],
            r['country'],
            fmt_date(r["election_deadline"]),
            f"{d}d" if d is not None and d>=0 else "—",
            f"{r['cash_currency']} {cash:.4f}" if cash else "—",
            str(r["dividend_currency_opts"]) if r["dividend_currency_opts"] and str(r["dividend_currency_opts"])!='nan' else "—",
            f"{arb:+.2f}%" if arb is not None else "—",
            f"{bps:.0f}bps" if bps else "—",
            dflt,
            f"◆ {opt}" if act else opt,
            "⚡ ELECT" if act else ("✓ default ok" if opt==dflt or opt=="—" else "—"),
        ]
        scan_rows.append(row)
        scan_hl[i] = {
            7:  arb_colour(arb),
            8:  arb_colour(arb),
            10: '#00d4aa' if arb and arb>0 else '#6a8090',
            11: '#ff3355' if act else ('#00d4aa' if opt==dflt else '#6a8090'),
        }

    dark_table(scan_rows,
               ["Ticker","Company","Country","Deadline","Days","Gross Div","Currencies","Arb %","Arb BPS","Default","Optimal","Action"],
               scan_hl)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2 — CURRENCY ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
with st.expander(f"◆  Currency Analysis — {ev['ticker']} / {ev['company_name']}", expanded=True):
    if cash_amt and co_rate and mkt_rate:
        # Identify which non-base currency has a stored rate (GBP)
        gbp_ccy = "GBP" if "GBP" in currencies else (next((c for c in currencies if c != base_ccy), None))

        col_l, col_r = st.columns([3,2])
        with col_l:
            st.markdown("<p style='font-size:0.58rem;letter-spacing:0.12em;text-transform:uppercase;color:#304050;margin-bottom:0.4rem'>Per-share comparison</p>", unsafe_allow_html=True)

            ccy_rows=[]; ccy_hl={}; bar_ccys=[]; bar_co=[]; bar_mkt=[]
            for j,ccy in enumerate(currencies):
                is_base = (ccy == base_ccy)
                is_gbp  = (ccy == gbp_ccy)
                is_est  = (not is_base and not is_gbp)

                if is_base:
                    co_val, mkt_val = cash_amt, cash_amt
                    arb_c = 0.0
                else:
                    co_val  = cash_amt * co_rate
                    mkt_val = cash_amt * mkt_rate
                    arb_c   = (co_val/mkt_val - 1)*100 if mkt_val else 0

                co_net  = co_val  * (1-wht/100)
                mkt_net = mkt_val * (1-wht/100)
                uplift_ = co_net - mkt_net
                bps_    = arb_c * 100
                is_opt  = (ccy == optimal or (is_est and ccy.rstrip("*") == optimal))
                ccy_disp = f"{ccy}*" if is_est else ccy

                row = [
                    f"{'◆ ' if is_opt else '  '}{ccy_disp}",
                    f"{base_ccy} {cash_amt:.4f}",
                    f"{co_val:.4f}",
                    f"{mkt_val:.4f}",
                    f"{co_net:.4f}",
                    f"{uplift_:+.5f}",
                    f"{arb_c:+.2f}%",
                    f"{bps_:.0f}bps",
                    "◆ ELECT" if is_opt and action_req else ("✓ default" if ccy==default_el else "—"),
                ]
                ccy_rows.append(row)
                ccy_hl[j] = {k:'#00d4aa' for k in range(9)} if is_opt else {6:arb_colour(arb_c),7:arb_colour(arb_c),8:'#ff3355' if (is_opt and action_req) else '#6a8090'}
                bar_ccys.append(ccy_disp); bar_co.append(co_net); bar_mkt.append(mkt_net)

            dark_table(ccy_rows,
                       ["Currency","Gross Div","@ Co Rate","@ Mkt Rate","Net (post-WHT)","Uplift/sh","Arb %","Arb BPS","Action"],
                       ccy_hl, height=max(len(currencies)*36+55,130))

            if any("*" in c for c in bar_ccys):
                st.markdown("<p style='font-family:IBM Plex Mono;font-size:0.6rem;color:#304050;margin-top:0.2rem'>* Rate estimated — only USD/GBP rate stored. Treat non-GBP values as proxy.</p>", unsafe_allow_html=True)

        with col_r:
            colours_co  = ["#00d4aa" if c.rstrip("*")==optimal else "#243548" for c in bar_ccys]
            fig = go.Figure()
            fig.add_trace(go.Bar(x=bar_ccys, y=bar_co,  name="Company rate", marker_color=colours_co, marker_line_width=0,
                text=[f"{v:.4f}" for v in bar_co], textposition="outside",
                textfont=dict(family="IBM Plex Mono",size=9,color="#6a8090")))
            fig.add_trace(go.Bar(x=bar_ccys, y=bar_mkt, name="Market rate",  marker_color=["#0a2e24" if c.rstrip("*")==optimal else "#182436" for c in bar_ccys], marker_line_width=0))
            fig.update_layout(
                paper_bgcolor="#04060a", plot_bgcolor="#080c12",
                font=dict(family="IBM Plex Mono",size=10,color="#6a8090"),
                height=280, margin=dict(l=8,r=8,t=20,b=30), barmode="group", bargap=0.3,
                legend=dict(font=dict(color="#6a8090",size=9), bgcolor="transparent"),
                xaxis=dict(gridcolor="#0e1825",linecolor="#182436",tickfont=dict(size=11,color="#c8d8e8")),
                yaxis=dict(title="Div/sh (net WHT)",gridcolor="#0e1825",linecolor="#182436",tickfont=dict(size=9)),
            )
            st.plotly_chart(fig, use_container_width=True)

        if action_req:
            inaction_cost = uplift * pos_shares if uplift and pos_shares > 0 else None
            st.markdown(
                f"<div style='border-left:2px solid #ff3355;background:#ff335508;padding:0.35rem 0.7rem;"
                f"font-family:IBM Plex Mono;font-size:0.68rem;color:#ff3355;margin-top:0.3rem'>"
                f"⚡  Default is <strong>{default_el}</strong> — you must actively elect <strong style='color:#c8d8e8'>{optimal}</strong>. "
                f"{'Cost of inaction on ' + str(pos_shares) + ' shares: GBP ' + f'{inaction_cost:,.4f}' if inaction_cost else 'Set position size for cost calculation.'}"
                f"</div>",
                unsafe_allow_html=True
            )
        elif arb_pct and arb_pct > 0:
            st.success(f"◆  Elect {optimal} — {arb_pct:.2f}% / {arb_pct*100:.0f}bps arb vs {base_ccy} at spot")

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3 — FX SENSITIVITY
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  FX Sensitivity Analysis", expanded=True):
    if cash_amt and co_rate and mkt_rate:
        col_t, col_c = st.columns([2,3])
        with col_t:
            st.markdown("<p style='font-size:0.58rem;letter-spacing:0.12em;text-transform:uppercase;color:#304050;margin-bottom:0.4rem'>Arb at different spot rates</p>", unsafe_allow_html=True)
            moves = [-5,-3,-2,-1,0,+1,+2,+3,+5]
            sens_rows=[]; sens_hl={}
            for k,mv in enumerate(moves):
                new_mkt = mkt_rate * (1+mv/100)
                co_val  = cash_amt * co_rate
                mv_val  = cash_amt * new_mkt
                new_arb = (co_val/mv_val - 1)*100 if mv_val else 0
                new_bps = new_arb * 100
                is_cur  = (mv == 0)
                dirn    = "GBP weakens" if mv>0 else ("GBP strengthens" if mv<0 else "Current")
                row = [
                    f"{'→ ' if is_cur else '  '}{mv:+.0f}%" if mv!=0 else "  Current",
                    f"{new_mkt:.4f}",
                    f"{new_arb:+.2f}%",
                    f"{new_bps:.0f}bps",
                    dirn,
                ]
                sens_rows.append(row)
                if is_cur:
                    sens_hl[k] = {j:'#c8d8e8' for j in range(5)}
                    sens_hl[k][2] = arb_colour(new_arb)
                    sens_hl[k][3] = arb_colour(new_arb)
                else:
                    sens_hl[k] = {2:arb_colour(new_arb),3:arb_colour(new_arb),4:'#304050'}
            dark_table(sens_rows, ["Spot Move","New Rate","Arb %","Arb BPS","Direction"], sens_hl, height=len(moves)*33+52)
            st.markdown(
                f"<p style='font-family:IBM Plex Mono;font-size:0.64rem;color:#6a8090;margin-top:0.3rem'>"
                f"Break-even rate: <span style='color:#c8d8e8'>{co_rate:.4f}</span> (= company rate). "
                f"Arb disappears if spot reaches this level.</p>",
                unsafe_allow_html=True
            )

        with col_c:
            spot_range = [mkt_rate*(1+i/200) for i in range(-50,51)]
            arb_range  = [(cash_amt*co_rate/(cash_amt*s)-1)*100 if s else 0 for s in spot_range]
            fig2 = go.Figure()
            pos_x = [s for s,a in zip(spot_range,arb_range) if a>=0]
            pos_y = [a for a in arb_range if a>=0]
            if pos_x:
                fig2.add_trace(go.Scatter(x=pos_x+pos_x[::-1], y=pos_y+[0]*len(pos_y),
                    fill='toself', fillcolor='rgba(0,212,170,0.06)',
                    line=dict(color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'))
            fig2.add_trace(go.Scatter(x=spot_range, y=arb_range, name="Arb %",
                line=dict(color="#00d4aa",width=2.5),
                hovertemplate="Spot: %{x:.4f}<br>Arb: %{y:.2f}%<extra></extra>"))
            # BPS axis annotation
            fig2.add_hline(y=0, line_color="#243548", line_width=1)
            fig2.add_vline(x=mkt_rate, line_color="#6a8090", line_width=1, line_dash="dot",
                annotation_text=f"Spot {mkt_rate:.4f}", annotation_font=dict(color="#6a8090",size=9,family="IBM Plex Mono"))
            fig2.add_vline(x=co_rate, line_color="#304050", line_width=1, line_dash="dot",
                annotation_text=f"Co rate {co_rate:.4f}", annotation_font=dict(color="#304050",size=9,family="IBM Plex Mono"))
            fig2.update_layout(
                paper_bgcolor="#04060a", plot_bgcolor="#080c12",
                font=dict(family="IBM Plex Mono",size=10,color="#6a8090"),
                height=280, margin=dict(l=8,r=8,t=20,b=30),
                xaxis=dict(title="USD/GBP Spot",gridcolor="#0e1825",linecolor="#182436",tickfont=dict(size=9)),
                yaxis=dict(title="Arb % vs USD",gridcolor="#0e1825",linecolor="#182436",tickfont=dict(size=9)),
                showlegend=False
            )
            st.plotly_chart(fig2, use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 4 — POSITION P&L
# ═════════════════════════════════════════════════════════════════════════════
with st.expander(f"◆  Position P&L — {pos_shares:,} shares", expanded=True):
    if pos_shares > 0 and cash_amt and co_rate and mkt_rate:
        co_tot  = pos_shares * cash_amt * co_rate  * (1-wht/100)
        mkt_tot = pos_shares * cash_amt * mkt_rate * (1-wht/100)
        usd_tot = pos_shares * cash_amt * (1-wht/100)
        uplift_tot = co_tot - mkt_tot
        bps_tot    = (co_tot/mkt_tot-1)*10000 if mkt_tot else 0

        pnl_rows = [
            ("Position",             f"{pos_shares:,} shares",               ""),
            (f"{base_ccy} (default base)", f"{base_ccy} {usd_tot:,.4f}",   f"{base_ccy} {cash_amt:.4f}/sh net WHT"),
            ("GBP @ company rate",   f"GBP {co_tot:,.4f}",                  f"@ {co_rate:.4f} fixed"),
            ("GBP @ market rate",    f"GBP {mkt_tot:,.4f}",                 f"@ {mkt_rate:.4f} spot"),
            ("Arb uplift",           f"GBP {uplift_tot:+,.4f}",             f"{arb_pct:+.2f}% / {bps_tot:.0f}bps"),
            ("Uplift per share",     f"GBP {uplift_tot/pos_shares:.6f}",    ""),
            ("Cost of inaction",     f"GBP {uplift_tot:+,.4f}" if action_req else "N/A — default is optimal", "If no election made"),
        ]
        hl = {4:{1:'#00d4aa' if uplift_tot>0 else '#f5a623',2:'#00d4aa' if uplift_tot>0 else '#f5a623'},
              6:{1:'#ff3355' if action_req else '#304050',2:'#ff3355' if action_req else '#304050'}}
        dark_table(pnl_rows, ["Metric","Total","Detail"], hl, height=265)

        if action_req:
            st.markdown(
                f"<div style='border-left:2px solid #ff3355;background:#ff335508;padding:0.35rem 0.7rem;"
                f"font-family:IBM Plex Mono;font-size:0.68rem;color:#ff3355;margin-top:0.3rem'>"
                f"⚡  Must elect {optimal} by <strong>{fmt_date(ev['election_deadline'])}</strong>. "
                f"Forfeited alpha: <strong style='color:#c8d8e8'>GBP {uplift_tot:,.4f} ({bps_tot:.0f}bps)</strong> on {pos_shares:,} shares.</div>",
                unsafe_allow_html=True
            )
        else:
            st.success(f"◆  Elect {optimal} — GBP {uplift_tot:,.4f} ({bps_tot:.0f}bps) captured on {pos_shares:,} shares")

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 5 — PORTFOLIO AGGREGATOR
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  Portfolio Alpha Aggregator — All CCY Elections", expanded=False):
    st.markdown("<p style='font-size:0.7rem;color:#6a8090;margin-bottom:0.5rem'>Aggregate arb across the universe at a uniform position. Action-required events listed first.</p>", unsafe_allow_html=True)
    agg_shares = st.number_input("Uniform position (shares)", min_value=0, value=100000, step=10000, key="agg")

    if agg_shares > 0:
        agg_rows=[]; agg_hl={}; total_uplift=0.0; total_action_cost=0.0
        df_agg = df.sort_values(["_action","fx_arbitrage_pct"], ascending=[False,False])
        for i,(_,r) in enumerate(df_agg.iterrows()):
            ca  = sf(r["cash_amount"])
            cor = sf(r["company_fx_rate"])
            mkr = sf(r["market_fx_rate"])
            wh  = sf(r["withholding_tax_pct"],0.0)
            arb = sf(r["fx_arbitrage_pct"])
            opt = str(r["optimal_election"]).strip() if r["optimal_election"] and str(r["optimal_election"])!='nan' else "—"
            dflt= str(r["election_default"]).strip() if r["election_default"] and str(r["election_default"])!='nan' else "USD"
            act = r["_action"]
            d   = days_to(r["election_deadline"])

            if ca and cor and mkr:
                co_v  = agg_shares * ca * cor * (1-wh/100)
                mk_v  = agg_shares * ca * mkr * (1-wh/100)
                uplift_ = co_v - mk_v
            else:
                uplift_ = 0.0
            total_uplift += uplift_
            if act: total_action_cost += uplift_

            row = [
                f"{'⚡ ' if act else '  '}{tdot(d)} {r['ticker']}",
                r['company_name'][:20],
                fmt_date(r["election_deadline"]),
                f"{d}d" if d is not None and d>=0 else "—",
                f"{arb:+.2f}%" if arb else "—",
                dflt,
                opt,
                f"GBP {uplift_:+,.4f}",
                "⚡ ELECT" if act else "✓",
            ]
            agg_rows.append(row)
            agg_hl[i] = {4:arb_colour(arb),7:'#00d4aa' if uplift_>0 else '#6a8090',8:'#ff3355' if act else '#304050'}

        # Totals row
        agg_rows.append(["TOTAL","","","","","","",f"GBP {total_uplift:+,.4f}",""])
        last = len(agg_rows)-1
        agg_hl[last] = {j:'#c8d8e8' for j in range(9)}
        agg_hl[last][7] = '#00d4aa' if total_uplift>0 else '#f5a623'

        dark_table(agg_rows, ["Ticker","Company","Deadline","Days","Arb %","Default","Optimal","Uplift","Action"], agg_hl)

        st.markdown(
            f"<p style='font-family:IBM Plex Mono;font-size:0.68rem;color:#6a8090;margin-top:0.4rem'>"
            f"Total available arb: <span style='color:#00d4aa'>GBP {total_uplift:,.4f}</span>"
            f" &nbsp;·&nbsp; At-risk from inaction: <span style='color:#ff3355'>GBP {total_action_cost:,.4f}</span>"
            f" &nbsp;·&nbsp; {action_n} events require active election"
            f"</p>",
            unsafe_allow_html=True
        )
