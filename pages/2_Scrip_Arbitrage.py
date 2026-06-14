import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3, re
from datetime import date
from utils.helpers import (sf, fmt_date, days_to, tdot, pct_colour,
                           parse_ratio, calc_scrip_prem, scrip_decision)
from utils.ui import apply_theme, dark_table

st.set_page_config(page_title="Scrip Arbitrage · CA Alpha", page_icon="◆", layout="wide", initial_sidebar_state="expanded")
apply_theme()

DB = "data/events.db"; TODAY = date.today()

@st.cache_data(ttl=300)
def load_scrip():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("""
        SELECT e.event_id, e.ticker, e.company_name, e.country, e.currency,
               e.event_type, e.status, e.election_deadline, e.ex_date,
               e.payment_date, e.notes,
               s.cash_amount, s.cash_currency, s.scrip_issue_price,
               s.scrip_ratio, s.scrip_discount_pct, s.election_default,
               s.withholding_tax_pct, s.optimal_election
        FROM events e JOIN scrip_details s ON e.event_id=s.event_id
        WHERE e.event_type='scrip_dividend'
        AND e.status IN ('LIVE','UPCOMING')
        AND (e.election_deadline IS NULL OR e.election_deadline >= date('now'))
        ORDER BY e.election_deadline ASC NULLS LAST
    """, conn)
    conn.close()
    return df

df = load_scrip()
if df.empty:
    st.title("◆ Scrip Arbitrage Engine")
    st.info("No live scrip dividend events found.")
    st.stop()

# Pre-calculate scrip premium and action required for ALL events
def enrich_row(r):
    return scrip_decision(r["cash_amount"], r["scrip_issue_price"], r["scrip_ratio"],
                          r["scrip_discount_pct"], r["withholding_tax_pct"], r["election_default"])

enrich = [enrich_row(r) for _,r in df.iterrows()]
df["_prem"]       = [e[0] for e in enrich]
df["_opt"]        = [e[1] for e in enrich]
df["_action_req"] = [e[2] for e in enrich]
df["_inferred_px"]= [e[3] for e in enrich]

# ── sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("### ◆ Scrip Engine")
country_opts = ["All"] + sorted(df["country"].unique().tolist())
sel_country  = st.sidebar.selectbox("Country", country_opts)
action_filter = st.sidebar.checkbox("Action Required only", value=False)
df_filt = df if sel_country=="All" else df[df["country"]==sel_country]
if action_filter: df_filt = df_filt[df_filt["_action_req"]==True]

def ev_label(r):
    d    = days_to(r["election_deadline"])
    prem = r["_prem"]
    req  = "⚡" if r["_action_req"] else " "
    return f"{tdot(d)} {req} {r['ticker']} · {r['company_name'][:18]} · {f'{prem:+.2f}%' if prem else '—'}"

labels  = [ev_label(r) for _,r in df_filt.iterrows()]
sel_idx = st.sidebar.selectbox("Event", range(len(labels)), format_func=lambda i: labels[i])
sel_idx = min(sel_idx, max(0, len(df_filt)-1))
ev = df_filt.iloc[sel_idx]

st.sidebar.markdown("---")
st.sidebar.markdown("### ◆ Position")
pos_shares = st.sidebar.number_input("Shares held", min_value=0, value=10000, step=1000)
pos_price  = st.sidebar.number_input("Current px (0 = auto)", min_value=0.0, value=0.0, step=0.5)

# Derived values for selected event
cash_amt   = sf(ev["cash_amount"])
scrip_px   = sf(ev["scrip_issue_price"])
disc_pct   = sf(ev["scrip_discount_pct"])
wht        = sf(ev["withholding_tax_pct"], 0.0)
rn, rd     = parse_ratio(ev["scrip_ratio"]); rn = rn or 1
default_el = str(ev["election_default"]).upper() if ev["election_default"] and str(ev["election_default"])!='nan' else "CASH"
inferred   = ev["_inferred_px"]
current_px = pos_price if pos_price > 0 else (inferred or 0)
ddl_days   = days_to(ev["election_deadline"])
dot        = tdot(ddl_days)

prem, cash_net, scrip_val, calc_opt = calc_scrip_prem(
    cash_amt, scrip_px, ev["scrip_ratio"], wht, current_px
)
action_req = (default_el != calc_opt) if calc_opt != "—" else False

# ── page header ───────────────────────────────────────────────────────────────
st.title("◆ Scrip Arbitrage Engine")

action_count = int(df["_action_req"].sum())
st.markdown(
    f"<div style='font-family:IBM Plex Mono;font-size:0.72rem;color:#6a8090;"
    f"padding:0.35rem 0.6rem;border:1px solid {'#ff3355' if action_count>0 else '#182436'};"
    f"background:{'#ff335508' if action_count>0 else '#080c12'};"
    f"margin-bottom:0.8rem'>"
    f"{'⚡' if action_count>0 else '·'} &nbsp;"
    f"<span style='color:{'#ff3355' if action_count>0 else '#304050'}'>"
    f"<strong style='color:{'#c8d8e8' if action_count>0 else '#304050'}'>{action_count} events</strong>"
    f" default to CASH but scrip election gives higher value — active instruction required"
    f"</span></div>",
    unsafe_allow_html=True
)

st.markdown(
    f"<div style='font-family:IBM Plex Mono;font-size:0.72rem;color:#6a8090;"
    f"padding:0.4rem 0 0.6rem;border-bottom:1px solid #182436;margin-bottom:0.9rem'>"
    f"{dot} &nbsp;<span style='color:#c8d8e8;font-weight:500'>{ev['ticker']}</span>"
    f" &nbsp;·&nbsp; {ev['company_name']} &nbsp;·&nbsp; {ev['country']}"
    f" &nbsp;·&nbsp; Ex-date: <span style='color:#c8d8e8'>{fmt_date(ev['ex_date'])}</span>"
    f" &nbsp;·&nbsp; Deadline: <span style='color:#{'ff3355' if ddl_days is not None and ddl_days<=3 else 'f5a623' if ddl_days is not None and ddl_days<=7 else 'c8d8e8'}'>{fmt_date(ev['election_deadline'])} ({ddl_days}d)</span>"
    f" &nbsp;·&nbsp; Default: <span style='color:{'ff3355' if action_req else '6a8090'}'>{default_el}</span>"
    f" &nbsp;·&nbsp; {'⚡ ACTION REQUIRED — elect ' + calc_opt if action_req else 'No action required'}"
    f"</div>",
    unsafe_allow_html=True
)

# ── KPIs ──────────────────────────────────────────────────────────────────────
k1,k2,k3,k4,k5,k6 = st.columns(6)
k1.metric("Cash Div (gross)",  f"{ev['cash_currency']} {cash_amt:.4f}" if cash_amt else "—")
k2.metric("Cash (net WHT)",    f"{ev['cash_currency']} {cash_net:.4f}" if cash_net else "—",
          delta=f"-{wht:.0f}% WHT" if wht > 0 else None,
          delta_color="inverse" if wht > 0 else "off")
k3.metric("Scrip Value",       f"{ev['currency']} {scrip_val:.4f}" if scrip_val else "—")
k4.metric("Scrip vs Cash",
          f"{prem:+.2f}%" if prem is not None else "—",
          delta="SCRIP BETTER ◆" if prem and prem>0 else ("CASH BETTER" if prem is not None else None),
          delta_color="normal" if prem and prem>0 else "inverse")
k5.metric("Election Default",  default_el,
          delta="⚡ Must Elect" if action_req else None,
          delta_color="inverse" if action_req else "off")
k6.metric("Ratio",             str(ev["scrip_ratio"]) if ev["scrip_ratio"] and str(ev["scrip_ratio"])!='nan' else "—")

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1 — OPPORTUNITY SCANNER
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  Opportunity Scanner — All Live Scrip Events", expanded=True):
    sc1,sc2,sc3,sc4 = st.columns(4)
    must_elect_n = int(df["_action_req"].sum())
    wht_n = len(df[df["withholding_tax_pct"].apply(sf).apply(lambda x: x is not None and x>0)])
    urgent_n = len(df[df["election_deadline"].apply(lambda d: days_to(d) is not None and 0<=days_to(d)<=7)])
    high_prem = len(df[df["_prem"].apply(lambda x: x is not None and x > 0.5)])
    sc1.metric("Must Elect Actively", must_elect_n, delta="⚡ Urgent" if must_elect_n>0 else None, delta_color="inverse" if must_elect_n>0 else "off")
    sc2.metric("Events with WHT",     wht_n,       delta="Tax alpha" if wht_n>0 else None, delta_color="normal" if wht_n>0 else "off")
    sc3.metric("Deadline ≤7d",        urgent_n,    delta="Urgent" if urgent_n>0 else None, delta_color="inverse" if urgent_n>0 else "off")
    sc4.metric("Scrip Premium >0.5%", high_prem)

    scan_rows=[]; scan_hl={}
    for i,(_,r) in enumerate(df.iterrows()):
        d       = days_to(r["election_deadline"])
        prem    = r["_prem"]
        opt     = r["_opt"]
        act_req = r["_action_req"]
        default = str(r["election_default"]).upper() if r["election_default"] and str(r["election_default"])!='nan' else "CASH"
        wht_v   = sf(r["withholding_tax_pct"], 0.0)
        cash    = sf(r["cash_amount"])

        row = [
            f"{tdot(d)} {'⚡' if act_req else ' '} {r['ticker']}",
            r['company_name'][:22],
            r['country'],
            fmt_date(r["election_deadline"]),
            f"{d}d" if d is not None and d>=0 else ("Passed" if d is not None else "—"),
            f"{r['cash_currency']} {cash:.4f}" if cash else "—",
            str(r["scrip_ratio"]) if r["scrip_ratio"] and str(r["scrip_ratio"])!='nan' else "—",
            f"{wht_v:.0f}%" if wht_v > 0 else "0%",
            f"{prem:+.2f}%" if prem is not None else "—",
            default,
            f"◆ {opt}" if opt=="SCRIP" else (opt if opt else "—"),
            "⚡ ELECT" if act_req else ("✓" if opt=="SCRIP" else "—"),
        ]
        scan_rows.append(row)
        scan_hl[i] = {
            8:  pct_colour(prem),
            10: '#00d4aa' if opt=="SCRIP" else '#6a8090',
            11: '#ff3355' if act_req else ('#00d4aa' if opt=="SCRIP" else '#304050'),
        }

    dark_table(scan_rows,
               ["Ticker","Company","Country","Deadline","Days","Cash Div","Ratio","WHT","Scrip vs Cash","Default","Optimal","Action"],
               scan_hl)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2 — ECONOMICS DEEP-DIVE
# ═════════════════════════════════════════════════════════════════════════════
with st.expander(f"◆  Economics — {ev['ticker']} / {ev['company_name']}", expanded=True):
    if cash_amt and scrip_px and rd and current_px > 0:
        nshares_per = rn / rd
        be_price    = cash_net / nshares_per if (cash_net and nshares_per) else 0

        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("<p style='font-size:0.58rem;letter-spacing:0.12em;text-transform:uppercase;color:#304050;margin-bottom:0.4rem'>Per-share economics</p>", unsafe_allow_html=True)
            econ_rows = [
                ("Gross cash dividend",  f"{ev['cash_currency']} {cash_amt:.4f}",    "Declared dividend"),
                ("Withholding tax",      f"{wht:.0f}%",                               f"→ net {ev['cash_currency']} {cash_net:.4f}"),
                ("Scrip ratio",          str(ev["scrip_ratio"]),                       f"{nshares_per:.6f} new sh per existing sh"),
                ("Scrip issue price",    f"{ev['currency']} {scrip_px:.2f}",          "Reference price"),
                ("Current price",        f"{ev['currency']} {current_px:.2f}",        "Inferred from issue px + disc%"),
                ("Scrip value (market)", f"{ev['currency']} {scrip_val:.4f}",         f"{nshares_per:.6f} × {current_px:.2f}"),
                ("Cash net of WHT",      f"{ev['cash_currency']} {cash_net:.4f}",     "What you actually receive"),
                ("Scrip premium",        f"{prem:+.2f}%" if prem else "—",            "◆ SCRIP BETTER" if prem and prem>0 else "CASH BETTER"),
                ("Break-even price",     f"{ev['currency']} {be_price:.2f}" if be_price else "—", "Below this → take CASH"),
                ("Election default",     default_el,                                  "If no instruction received"),
                ("Action required",      "YES — elect SCRIP" if action_req else "No — default is optimal", ""),
            ]
            hl = {7:{1:pct_colour(prem),2:'#00d4aa' if prem and prem>0 else '#f5a623'},
                  10:{1:'#ff3355' if action_req else '#00d4aa', 2:'#ff3355' if action_req else '#304050'}}
            dark_table(econ_rows, ["Parameter","Value","Note"], hl, height=420)

        with col_r:
            st.markdown("<p style='font-size:0.58rem;letter-spacing:0.12em;text-transform:uppercase;color:#304050;margin-bottom:0.4rem'>Position P&L — {:,.0f} shares</p>".format(pos_shares), unsafe_allow_html=True)
            if pos_shares > 0:
                total_cash  = pos_shares * cash_net if cash_net else 0
                new_shares  = pos_shares * nshares_per
                total_scrip = new_shares * current_px
                delta       = total_scrip - total_cash
                delta_pct   = delta / total_cash * 100 if total_cash else 0

                pnl_rows = [
                    ("Existing shares",      f"{pos_shares:,}",                            f"@ {ev['currency']} {current_px:.2f}"),
                    ("Cash election",        f"{ev['cash_currency']} {total_cash:,.2f}",   f"{ev['cash_currency']} {cash_net:.4f}/sh net WHT"),
                    ("Scrip election",       f"{ev['currency']} {total_scrip:,.2f}",       f"{new_shares:,.4f} new shares"),
                    ("Δ Scrip vs Cash",      f"{ev['currency']} {delta:+,.2f}",            f"{delta_pct:+.2f}%"),
                    ("New shares received",  f"{new_shares:,.4f}",                         "From scrip election"),
                    ("New shares (rounded)", f"{int(new_shares):,}",                       "Actual allotment (fractional may be cashed)"),
                ]
                hl2 = {3:{1:'#00d4aa' if delta>0 else '#f5a623', 2:'#00d4aa' if delta>0 else '#f5a623'}}
                dark_table(pnl_rows, ["Metric","Value","Detail"], hl2, height=240)

                if action_req:
                    st.markdown(
                        f"<div style='border-left:2px solid #ff3355;background:#ff335508;"
                        f"padding:0.35rem 0.7rem;font-family:IBM Plex Mono;font-size:0.68rem;"
                        f"color:#ff3355;margin-top:0.4rem'>"
                        f"⚡  Election default is {default_el} — you will leave "
                        f"{ev['currency']} {abs(delta):,.2f} on the table if no instruction sent. "
                        f"Instruct SCRIP before {fmt_date(ev['election_deadline'])}.</div>",
                        unsafe_allow_html=True
                    )
                elif prem and prem > 0:
                    st.success(f"◆  Scrip premium {prem:.2f}% — elect SCRIP for +{ev['currency']} {delta:,.2f}")
            else:
                st.markdown("<p style='color:#304050;font-size:0.7rem'>Enter position size in sidebar.</p>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3 — WHT IMPACT ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
if wht > 0:
    with st.expander(f"◆  Withholding Tax Impact — {wht:.0f}% WHT applies", expanded=True):
        st.markdown(
            f"<div style='font-family:IBM Plex Mono;font-size:0.7rem;color:#6a8090;line-height:1.8;margin-bottom:0.6rem'>"
            f"This event carries <span style='color:#ff3355'>{wht:.0f}% WHT</span> on cash dividends. "
            f"In most jurisdictions, <strong style='color:#c8d8e8'>scrip dividends are WHT-exempt</strong> — making the tax advantage of electing scrip material at this rate."
            f"</div>",
            unsafe_allow_html=True
        )
        col_a, col_b = st.columns(2)
        with col_a:
            # Show after-tax comparison at different WHT rates
            if cash_amt and scrip_val:
                wht_rows = []
                for test_wht in [0, 5, 10, 15, 20, 25, 30, 35]:
                    cn    = cash_amt * (1 - test_wht/100)
                    prem_ = (scrip_val - cn) / cn * 100 if cn else 0
                    opt_  = "◆ SCRIP" if prem_ > 0 else "CASH"
                    is_cur = abs(test_wht - wht) < 0.1
                    wht_rows.append([
                        f"{'→ ' if is_cur else '  '}{test_wht:.0f}%",
                        f"{ev['cash_currency']} {cn:.4f}",
                        f"{ev['currency']} {scrip_val:.4f}",
                        f"{prem_:+.2f}%",
                        opt_,
                    ])
                hl3 = {}
                for i,tr in enumerate(wht_rows):
                    if "→" in str(tr[0]):
                        hl3[i] = {j:'#c8d8e8' for j in range(5)}
                        hl3[i][3] = pct_colour(float(tr[3].replace('%','').replace('+','')))
                dark_table(wht_rows, ["WHT Rate","Cash Net","Scrip Value","Scrip Premium","Optimal"], hl3, height=300)
        with col_b:
            if cash_amt and scrip_val and pos_shares > 0:
                wht_pos_rows = []
                for test_wht in [0, 10, 20, 30, 35]:
                    cn      = cash_amt * (1 - test_wht/100)
                    total_c = pos_shares * cn
                    total_s = pos_shares * nshares_per * current_px
                    delta_  = total_s - total_c
                    wht_pos_rows.append([
                        f"{test_wht:.0f}%",
                        f"{ev['currency']} {total_c:,.2f}",
                        f"{ev['currency']} {total_s:,.2f}",
                        f"{ev['currency']} {delta_:+,.2f}",
                    ])
                hl4 = {i:{3:'#00d4aa' if '+' in r[3] else '#f5a623'} for i,r in enumerate(wht_pos_rows)}
                dark_table(wht_pos_rows, ["WHT","Cash Total","Scrip Total","Δ P&L"], hl4, height=200)
                if wht >= 30:
                    st.success(f"◆  At {wht:.0f}% WHT, scrip advantage on {pos_shares:,} shares is {ev['currency']} {pos_shares*nshares_per*current_px - pos_shares*cash_net:,.2f}")
else:
    with st.expander("◆  Withholding Tax — 0% WHT applies", expanded=False):
        st.markdown(
            f"<div style='font-family:IBM Plex Mono;font-size:0.7rem;color:#6a8090;line-height:1.8'>"
            f"<strong style='color:#c8d8e8'>0% withholding tax</strong> applies to this event. "
            f"Cash and scrip elections are compared on a gross basis — no tax drag on the cash alternative. "
            f"The scrip premium shown in Section 1 reflects the pure economic difference with no WHT adjustment.<br><br>"
            f"Countries with significant WHT typically include: France (30%), Switzerland (35%), "
            f"Belgium (30%), Spain (19%), Germany (26.375%). "
            f"UK, Australia, and Gulf domiciles commonly apply 0%."
            f"</div>",
            unsafe_allow_html=True
        )


# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  Break-even Analysis", expanded=True):
    if cash_amt and rd and current_px > 0:
        nshares_per = rn / rd
        be_price    = cash_net / nshares_per if (cash_net and nshares_per) else 0
        lo = min(scrip_px or current_px, current_px) * 0.70
        hi = current_px * 1.30
        prices = [lo + (hi-lo)*i/300 for i in range(301)]
        sv = [p * nshares_per for p in prices]
        cv = [cash_net] * len(prices)

        fig = go.Figure()
        # Shade alpha region (above break-even)
        above = [p for p in prices if p >= be_price]
        if above:
            above_sv = [p*nshares_per for p in above]
            fig.add_trace(go.Scatter(
                x=above+above[::-1], y=above_sv+[cash_net]*len(above),
                fill='toself', fillcolor='rgba(0,212,170,0.06)',
                line=dict(color='rgba(0,0,0,0)'), showlegend=False, hoverinfo='skip'
            ))
        fig.add_trace(go.Scatter(x=prices, y=sv, name="Scrip value",
            line=dict(color="#00d4aa", width=2.5),
            hovertemplate=f"Price: %{{x:.2f}}<br>Scrip: %{{y:.4f}}<extra></extra>"))
        fig.add_trace(go.Scatter(x=prices, y=cv, name=f"Cash net of {wht:.0f}% WHT",
            line=dict(color="#f5a623", width=2, dash="dash"),
            hovertemplate=f"Cash: {cash_net:.4f}<extra></extra>"))

        for vx, col, label in [
            (be_price, "#243548", f"B/E {ev['currency']}{be_price:.2f}"),
            (current_px, "#6a8090", f"Now {ev['currency']}{current_px:.2f}"),
        ]:
            if vx: fig.add_vline(x=vx, line_color=col, line_width=1, line_dash="dot",
                annotation_text=label, annotation_font=dict(color=col, size=9, family="IBM Plex Mono"))

        fig.update_layout(
            paper_bgcolor="#04060a", plot_bgcolor="#080c12",
            font=dict(family="IBM Plex Mono", size=10, color="#6a8090"),
            height=295, margin=dict(l=8,r=8,t=20,b=30),
            legend=dict(font=dict(color="#6a8090",size=9), bgcolor="rgba(0,0,0,0)"),
        )
        fig.update_xaxes(title_text=f"Share price ({ev['currency']})", gridcolor="#0e1825", tickfont=dict(size=9))
        fig.update_yaxes(title_text="Value per share", gridcolor="#0e1825", tickfont=dict(size=9))
        st.plotly_chart(fig, use_container_width=True)
        verdict_col = "#00d4aa" if current_px > be_price else "#f5a623"
        st.markdown(
            f"<p style='font-family:IBM Plex Mono;font-size:0.68rem;color:#6a8090'>"
            f"Break-even: <span style='color:#c8d8e8'>{ev['currency']} {be_price:.2f}</span>"
            f" &nbsp;·&nbsp; Current is <span style='color:{verdict_col}'>{'above' if current_px>be_price else 'below'} break-even</span>"
            f" &nbsp;·&nbsp; <span style='color:{verdict_col}'>Elect {'SCRIP' if current_px>be_price else 'CASH'}</span>"
            f"{'  ·  ' + '<span style=\"color:#ff3355\">⚡ Must actively instruct — default is ' + default_el + '</span>' if action_req else ''}"
            f"</p>",
            unsafe_allow_html=True
        )

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 5 — LENDER CONFLICT & RECALL
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  Lender Conflict & Recall Assessment", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown(f"""<div style='font-family:IBM Plex Mono;font-size:0.7rem;color:#6a8090;line-height:1.9'>
<span style='color:#c8d8e8;font-size:0.62rem;letter-spacing:0.12em;text-transform:uppercase'>Mechanics</span><br><br>
Shares on loan over record date (<span style='color:#c8d8e8'>{fmt_date(ev["ex_date"])}</span>): borrower receives the dividend.
Lender receives a <strong style='color:#f5a623'>manufactured dividend</strong> equal to cash amount — <strong style='color:#f5a623'>scrip election unavailable on lent stock</strong>.<br><br>
If scrip election is optimal and stock is lent, every basis point of premium is a direct cost to the lender.
</div>""", unsafe_allow_html=True)

    with col_b:
        cost_per_share = (scrip_val - cash_net) if scrip_val and cash_net else 0
        # Calculate T+2 recall deadline dynamically from record date
        _recall_by = "—"
        _rec_str = fmt_date(ev.get("record_date") or ev.get("ex_date"))
        if _rec_str != "—":
            try:
                from datetime import date as _d, timedelta as _td
                _rec = _d.fromisoformat(_rec_str)
                _count, _rb = 0, _rec
                while _count < 2:
                    _rb -= _td(days=1)
                    if _rb.weekday() < 5:
                        _count += 1
                _recall_by = _rb.isoformat()
            except Exception:
                _recall_by = "T−2 from record date"
        st.markdown(f"""<div style='font-family:IBM Plex Mono;font-size:0.7rem;color:#6a8090;line-height:1.9'>
<span style='color:#c8d8e8;font-size:0.62rem;letter-spacing:0.12em;text-transform:uppercase'>Recall Decision</span><br><br>
Scrip premium per share: <span style='color:#{"00d4aa" if cost_per_share>0 else "6a8090"}'>{ev["currency"]} {cost_per_share:.4f}</span><br>
On {pos_shares:,} shares: <span style='color:#{"00d4aa" if cost_per_share*pos_shares>0 else "6a8090"}'>{ev["currency"]} {cost_per_share*pos_shares:,.4f}</span><br>
Record date: <span style='color:#c8d8e8'>{fmt_date(ev.get("record_date") or ev.get("ex_date"))}</span><br>
Recall by: <span style='color:#{"ff3355" if _recall_by not in ("—","T−2 from record date") else "6a8090"}'>{_recall_by}</span>  <span style='color:#304050'>(T−2 business days)</span><br><br>
<strong style='color:#c8d8e8'>Recall if:</strong> scrip premium × position &gt; lending income to record date
</div>""", unsafe_allow_html=True)

    if prem and prem > 0 and pos_shares > 0:
        alpha_val = (scrip_val - cash_net) * pos_shares if scrip_val and cash_net else 0
        st.success(f"◆  RECALL WARRANTED — scrip premium {prem:.2f}% · Alpha: {ev['currency']} {alpha_val:,.4f} on {pos_shares:,} sh · Deadline: {fmt_date(ev['election_deadline'])}")
    if ddl_days is not None and 0 <= ddl_days <= 3:
        st.markdown(f"<div style='border-left:2px solid #ff3355;background:#ff335508;padding:0.3rem 0.7rem;font-family:IBM Plex Mono;font-size:0.66rem;color:#ff3355;margin-top:0.3rem'>🔴  URGENT — election deadline {ddl_days}d. Recall settlement window closing.</div>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# METHODOLOGY
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  Methodology & Formulas", expanded=False):
    st.markdown("""<div style='font-family:IBM Plex Mono;font-size:0.7rem;color:#6a8090;line-height:2.0'>
<span style='color:#c8d8e8;font-size:0.62rem;letter-spacing:0.12em;text-transform:uppercase'>Scrip Dividend Valuation</span><br><br>
<strong style='color:#c8d8e8'>Scrip value per share</strong><br>
&nbsp;&nbsp;&nbsp;Scrip_val = (N_new ÷ N_existing) × P_current<br>
&nbsp;&nbsp;&nbsp;Where ratio = "N_new per N_existing" (e.g. 1 per 60 → 0.01667 new shares per existing share)<br><br>
<strong style='color:#c8d8e8'>Cash net of withholding tax</strong><br>
&nbsp;&nbsp;&nbsp;Cash_net = Cash_gross × (1 − WHT%)<br>
&nbsp;&nbsp;&nbsp;Assumption: scrip dividends are WHT-exempt (typical in most jurisdictions)<br><br>
<strong style='color:#c8d8e8'>Scrip premium (decision metric)</strong><br>
&nbsp;&nbsp;&nbsp;Premium% = (Scrip_val − Cash_net) ÷ Cash_net × 100<br>
&nbsp;&nbsp;&nbsp;If Premium% > 0 → elect SCRIP; if < 0 → take CASH<br><br>
<strong style='color:#c8d8e8'>Break-even price</strong><br>
&nbsp;&nbsp;&nbsp;B/E = Cash_net ÷ (N_new ÷ N_existing)<br>
&nbsp;&nbsp;&nbsp;At P_current = B/E, Scrip_val = Cash_net exactly (indifferent between elections)<br>
&nbsp;&nbsp;&nbsp;If P_current > B/E → SCRIP better; if P_current < B/E → CASH better<br><br>
<strong style='color:#c8d8e8'>Action required flag</strong><br>
&nbsp;&nbsp;&nbsp;Action_required = (election_default ≠ optimal_election)<br>
&nbsp;&nbsp;&nbsp;i.e. the company's default election is suboptimal — instruction must be sent<br><br>
<strong style='color:#c8d8e8'>Inferred market price</strong><br>
&nbsp;&nbsp;&nbsp;P_inferred = Scrip_issue_price ÷ (1 + discount%)<br>
&nbsp;&nbsp;&nbsp;Used when no live market price is available (reverse-engineered from issue discount)
</div>""", unsafe_allow_html=True)
