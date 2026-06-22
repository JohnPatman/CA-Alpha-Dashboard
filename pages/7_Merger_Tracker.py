import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3
from datetime import date
from utils.helpers import sf, fmt_date, days_to, tdot, ann_ret, ann_colour, spread_colour, risk_colour, reg_colour
from utils.ui import apply_theme, dark_table

st.set_page_config(page_title="Merger & Scheme Tracker · CA Alpha", page_icon="◆", layout="wide", initial_sidebar_state="expanded")
apply_theme()

DB = "data/events.db"; TODAY = date.today()

def implied_prob(spread_pct, break_pct):
    """
    If deal completes: gain = spread_pct
    If deal breaks:    loss = break_pct (negative)
    At fair value: p*spread + (1-p)*break = 0
    => p = |break| / (spread + |break|)
    """
    if spread_pct is None or break_pct is None: return None
    b = abs(break_pct)
    s = abs(spread_pct)
    return b / (s + b) * 100 if (s + b) > 0 else None

@st.cache_data(ttl=300)
def load_mergers():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("""
        SELECT e.event_id, e.ticker, e.company_name, e.country, e.currency,
               e.event_type, e.status, e.election_deadline,
               m.merger_type, m.acquirer, m.acquirer_ticker,
               m.consideration_type, m.cash_per_share, m.share_ratio,
               m.current_price, m.spread_to_terms_pct,
               m.court_sanction_date, m.long_stop_date,
               m.regulatory_status, m.break_risk
        FROM events e JOIN merger_details m ON e.event_id=m.event_id
        WHERE e.event_type IN ('scheme_of_arrangement','merger')
        AND e.status IN ('LIVE','UPCOMING')
        AND (e.election_deadline IS NULL OR m.long_stop_date >= date('now'))
        AND (e.election_deadline IS NULL OR e.election_deadline >= date('now'))
    """, conn)
    conn.close()
    return df

df = load_mergers()
if df.empty:
    st.title("◆ Merger & Scheme Tracker")
    st.info("No live merger/scheme events.")
    st.stop()

# ── sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("### ◆ M&A Tracker")
risk_filter = st.sidebar.selectbox("Break Risk", ["All","Low","Medium","High"])
df_filt = df if risk_filter=="All" else df[df["break_risk"].str.upper()==risk_filter.upper()]
if df_filt.empty: df_filt = df

def ev_label(r):
    d = days_to(r["court_sanction_date"] or r["election_deadline"])
    sp = sf(r["spread_to_terms_pct"])
    return f"{tdot(d)} {r['ticker']} · {r['merger_type']} · {f'{sp:+.2f}%' if sp else '—'}"

labels  = [ev_label(r) for _,r in df_filt.iterrows()]
sel_idx = st.sidebar.selectbox("Event", range(len(labels)), format_func=lambda i: labels[i])
sel_idx = min(sel_idx, max(0, len(df_filt)-1))
ev = df_filt.iloc[sel_idx]

st.sidebar.markdown("---")
st.sidebar.markdown("### ◆ Assumptions")
pos_shares   = st.sidebar.number_input("Shares held", min_value=0, value=10000, step=1000)
break_assume = st.sidebar.number_input("Break scenario (%)", min_value=-50, max_value=0, value=-15, step=1,
                                        help="Expected fall if deal fails. Typical UK scheme: -10% to -20%")
days_to_comp = st.sidebar.number_input("Days to completion", min_value=1, value=90, step=10,
                                        help="Your estimate, drives annualised return calc")

cash_ps  = sf(ev["cash_per_share"])
cur_px   = sf(ev["current_price"])
spread   = sf(ev["spread_to_terms_pct"])
brk      = str(ev["break_risk"]).strip() if ev["break_risk"] and str(ev["break_risk"])!='nan' else "MEDIUM"
reg_stat = str(ev["regulatory_status"]).strip() if ev["regulatory_status"] and str(ev["regulatory_status"])!='nan' else "PENDING"
sanction = fmt_date(ev["court_sanction_date"])
longstop = fmt_date(ev["long_stop_date"])
consid   = str(ev["consideration_type"]).strip().upper() if ev["consideration_type"] else "CASH"
is_cash  = consid in ("CASH","")
is_shares = consid == "SHARES"
is_mixed  = consid == "MIXED"
ddl_days = days_to(ev["court_sanction_date"] or ev["election_deadline"])
dot      = tdot(ddl_days)

# Derived
ann_days_actual = ddl_days if ddl_days and ddl_days > 0 else days_to_comp
ann_ret_pct = spread / ann_days_actual * 365 if spread and ann_days_actual > 0 else None
imp_prob    = implied_prob(spread, break_assume)
# Express R/R as "making X% to risk Y%", standard arb desk framing
rr_display  = f"{spread:.2f}% : {abs(break_assume):.0f}%" if spread and break_assume else "—"
rr_ratio    = abs(spread / break_assume) if spread and break_assume else None

# ── page header ───────────────────────────────────────────────────────────────
st.title("◆ Merger & Scheme Tracker")
st.markdown(
    f"<div style='font-family:IBM Plex Mono;font-size:0.72rem;color:#6a8090;"
    f"padding:0.4rem 0 0.6rem;border-bottom:1px solid #182436;margin-bottom:0.9rem'>"
    f"{dot} &nbsp;<span style='color:#c8d8e8;font-weight:500'>{ev['ticker']}</span>"
    f" &nbsp;·&nbsp; {ev['company_name']} &nbsp;·&nbsp; {ev['country']}"
    f" &nbsp;·&nbsp; {ev['merger_type']}"
    f" &nbsp;·&nbsp; Acquirer: <span style='color:#c8d8e8'>{ev['acquirer'] if ev['acquirer'] and str(ev['acquirer'])!='nan' else 'TBC'}</span>"
    f" &nbsp;·&nbsp; <span style='color:{reg_colour(reg_stat)}'>{reg_stat}</span>"
    f" &nbsp;·&nbsp; Break risk: <span style='color:{risk_colour(brk)}'>{brk}</span>"
    f"</div>",
    unsafe_allow_html=True
)

k1,k2,k3,k4,k5,k6 = st.columns(6)
k1.metric("Terms",          f"{ev['currency']} {cash_ps:.2f}" if cash_ps else (str(ev["share_ratio"]) if ev["share_ratio"] and str(ev["share_ratio"])!='nan' else "—"))
k2.metric("Current Px",     f"{ev['currency']} {cur_px:.2f}" if cur_px else "—")
k3.metric("Spread",         f"{spread:+.2f}%" if spread else "—",
          delta=f"{ann_ret_pct:.1f}% ann" if ann_ret_pct else None,
          delta_color="normal" if ann_ret_pct and ann_ret_pct > 5 else "off")
k4.metric("Implied Prob",
          f"{imp_prob:.1f}%" if imp_prob else "—",
          help=f"p = |break {break_assume}%| / (spread + |break|)")
k5.metric("Reward : Risk",
          rr_display,
          help=f"Making {spread:.2f}% to risk {abs(break_assume):.0f}% · ratio = {rr_ratio:.2f}x" if rr_ratio else "")
k6.metric("Sanction Date",  sanction)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1, DEAL SCANNER
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  Deal Scanner · All Live M&A  ·  Ranked by Risk-Adjusted Return", expanded=True):
    s1,s2,s3,s4 = st.columns(4)
    cleared_n  = len(df[df["regulatory_status"].apply(lambda x: str(x).upper()=="CLEARED")])
    low_risk_n = len(df[df["break_risk"].apply(lambda x: str(x).upper()=="LOW")])
    high_sp_n  = len(df[df["spread_to_terms_pct"].apply(sf).apply(lambda x: x is not None and x>2)])
    shares_n   = len(df[df["consideration_type"].apply(lambda x: str(x).upper()=="SHARES")])
    s1.metric("Reg Cleared",     cleared_n, delta="✓ Low risk" if cleared_n>0 else None, delta_color="normal")
    s2.metric("Low Break Risk",  low_risk_n)
    s3.metric("Spread >2%",      high_sp_n, delta="Alpha" if high_sp_n>0 else None, delta_color="normal")
    s4.metric("Share Deals",     shares_n,  help="Share consideration, hedge ratio applies")

    scan_rows=[]; scan_hl={}
    # Sort by implied probability desc (highest conviction first)
    df_scan = df.copy()
    df_scan["_prob"] = df_scan["spread_to_terms_pct"].apply(lambda x: implied_prob(sf(x), break_assume) or 0)
    df_scan = df_scan.sort_values("_prob", ascending=False)

    for i,(_,r) in enumerate(df_scan.iterrows()):
        d     = days_to(r["court_sanction_date"] or r["election_deadline"])
        sp    = sf(r["spread_to_terms_pct"])
        cps   = sf(r["cash_per_share"])
        cur   = sf(r["current_price"])
        brk_r = str(r["break_risk"]).strip() if r["break_risk"] and str(r["break_risk"])!='nan' else "—"
        reg_r = str(r["regulatory_status"]).strip() if r["regulatory_status"] and str(r["regulatory_status"])!='nan' else "—"
        consid_r = str(r["consideration_type"]).strip() if r["consideration_type"] else "CASH"
        terms  = f"{r['currency']} {cps:.2f}" if cps else (str(r["share_ratio"]) if r["share_ratio"] and str(r["share_ratio"])!='nan' else "—")
        ann_d  = d if d and d > 0 else days_to_comp
        ann_   = sp/ann_d*365 if sp and ann_d>0 else None
        # Flag deals where court sanction date has passed (d <= 0), in settlement
        is_settling = d is not None and d <= 0
        ann_display = "SETTLING" if is_settling else (f"{ann_:.1f}%" if ann_ else "—")
        prob_  = implied_prob(sp, break_assume)
        rr_    = abs(sp/break_assume) if sp and break_assume else None

        row = [
            f"{tdot(d)} {r['ticker']}",
            r['company_name'][:20],
            r['country'],
            r['merger_type'],
            consid_r,
            str(r['acquirer'])[:16] if r['acquirer'] and str(r['acquirer'])!='nan' else "—",
            terms,
            f"{r['currency']} {cur:.2f}" if cur else "—",
            f"{sp:+.2f}%" if sp is not None else "—",
            ann_display,
            f"{prob_:.0f}%" if prob_ else "—",
            reg_r,
            brk_r,
        ]
        scan_rows.append(row)
        scan_hl[i] = {
            8:  spread_colour(sp),
            9:  '#00d4aa' if is_settling else ann_colour(ann_),
            10: '#00d4aa' if prob_ and prob_>85 else '#d4c200' if prob_ and prob_>70 else '#f5a623',
            11: reg_colour(reg_r),
            12: risk_colour(brk_r),
        }

    dark_table(scan_rows,
               ["Ticker","Company","Country","Type","Consid.","Acquirer","Terms","Current","Spread","Ann Ret","Impl Prob","Reg","Break Risk"],
               scan_hl)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2, DEAL DEEP-DIVE + P&L
# ═════════════════════════════════════════════════════════════════════════════
with st.expander(f"◆  Deal Analysis · {ev['ticker']} / {ev['company_name']}", expanded=True):
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("<p style='font-size:0.58rem;letter-spacing:0.12em;text-transform:uppercase;color:#304050;margin-bottom:0.4rem'>Deal summary</p>", unsafe_allow_html=True)
        deal_rows = [
            ("Target",           ev['company_name'],                                    ev['ticker']),
            ("Acquirer",         str(ev['acquirer']) if ev['acquirer'] and str(ev['acquirer'])!='nan' else "—",
                                 str(ev['acquirer_ticker']) if ev['acquirer_ticker'] and str(ev['acquirer_ticker'])!='nan' else ""),
            ("Structure",        ev['merger_type'],                                     consid),
            ("Consideration",    f"{ev['currency']} {cash_ps:.2f}/sh" if cash_ps else str(ev["share_ratio"]) if ev["share_ratio"] and str(ev["share_ratio"])!='nan' else "—", ""),
            ("Current price",    f"{ev['currency']} {cur_px:.2f}" if cur_px else "—",  ""),
            ("Spread to terms",  f"{spread:+.2f}%" if spread else "—",                  "Gross upside"),
            ("Annualised return",f"{ann_ret_pct:.1f}%" if ann_ret_pct else "—",         f"@ {ann_days_actual}d to completion ({'actual' if ddl_days and ddl_days>0 else 'assumed'})"),
            ("Implied prob",     f"{imp_prob:.1f}%" if imp_prob else "—",               f"Break scenario: {break_assume}%"),
            ("Risk/reward",      rr_display,                                                    f"Making {spread:.2f}% to risk {abs(break_assume):.0f}%"),
            ("Break risk",       brk,                                                    ""),
            ("Regulatory",       reg_stat,                                               ""),
            ("Sanction date",    sanction,                                               ""),
            ("Long-stop",        longstop,                                               "Deal must complete by"),
        ]
        hl = {5:{1:spread_colour(spread)},
              6:{1:ann_colour(ann_ret_pct)},
              7:{1:'#00d4aa' if imp_prob and imp_prob>85 else '#d4c200' if imp_prob and imp_prob>70 else '#f5a623'},
              8:{1:'#00d4aa' if rr_ratio and rr_ratio>0.2 else '#6a8090'},
              9:{1:risk_colour(brk)},
              10:{1:reg_colour(reg_stat)}}
        dark_table(deal_rows, ["Parameter","Value","Detail"], hl, height=505)

    with col_r:
        st.markdown("<p style='font-size:0.58rem;letter-spacing:0.12em;text-transform:uppercase;color:#304050;margin-bottom:0.4rem'>Position P&L · {:,.0f} shares</p>".format(pos_shares), unsafe_allow_html=True)
        if pos_shares > 0 and cur_px and spread:
            mkt_val    = pos_shares * cur_px
            if cash_ps:
                deal_val   = pos_shares * cash_ps
                gross_pnl  = deal_val - mkt_val
                gross_pct  = gross_pnl/mkt_val*100
                break_px   = cur_px * (1 + break_assume/100)
                break_loss = pos_shares * (break_px - cur_px)
                rr_money   = abs(gross_pnl / break_loss) if break_loss != 0 else 0

                pnl_rows = [
                    ("Shares",                f"{pos_shares:,}",                          ""),
                    ("Current value",         f"{ev['currency']} {mkt_val:,.2f}",         f"@ {ev['currency']} {cur_px:.2f}"),
                    ("Deal value",            f"{ev['currency']} {deal_val:,.2f}",        f"@ {ev['currency']} {cash_ps:.2f}/sh"),
                    ("Gross P&L (deal)",      f"{ev['currency']} {gross_pnl:+,.2f}",      f"{gross_pct:+.2f}%"),
                    ("Annualised return",      f"{ann_ret_pct:.1f}%" if ann_ret_pct else "—", f"@ {ann_days_actual}d ({'actual' if ddl_days and ddl_days>0 else 'assumed'})"),
                    (f"Break P&L ({break_assume}%)",f"{ev['currency']} {break_loss:+,.2f}",f"If deal fails"),
                    ("Risk/reward (money)",   f"{rr_money:.2f}x",                         "Profit / potential loss"),
                    ("Implied prob",          f"{imp_prob:.1f}%" if imp_prob else "—",     f"At market spread"),
                ]
                hl2 = {3:{1:'#00d4aa' if gross_pnl>0 else '#ff3355'},
                       4:{1:ann_colour(ann_ret_pct)},
                       5:{1:'#ff3355'},
                       6:{1:'#00d4aa' if rr_money>0.25 else '#6a8090'},
                       7:{1:'#00d4aa' if imp_prob and imp_prob>85 else '#d4c200'}}
                dark_table(pnl_rows, ["Metric","Value","Detail"], hl2, height=310)

            # Share deal hedge ratio
            if is_shares and ev["share_ratio"] and str(ev["share_ratio"])!='nan':
                st.markdown(
                    f"<div style='border-left:2px solid #f5a623;background:#f5a62310;padding:0.35rem 0.7rem;"
                    f"font-family:IBM Plex Mono;font-size:0.68rem;color:#f5a623;margin-top:0.4rem'>"
                    f"Share consideration deal. Ratio: {ev['share_ratio']}, "
                    f"short acquirer shares to hedge. Ratio = target shares × exchange ratio.</div>",
                    unsafe_allow_html=True
                )

            if spread and spread > 0:
                st.success(f"◆  {spread:.2f}% spread · {ann_ret_pct:.1f}% ann · {imp_prob:.0f}% implied completion · {brk} break risk")

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3, RETURN vs PROBABILITY CHART (Bubble)
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  Deal Universe · Spread vs Implied Probability", expanded=True):
    chart_data = []
    for _,r in df.iterrows():
        sp  = sf(r["spread_to_terms_pct"])
        d   = days_to(r["court_sanction_date"] or r["election_deadline"])
        if sp is None: continue
        ann_= sp/(d if d and d>0 else days_to_comp)*365 if sp and days_to_comp>0 else 0
        prob_ = implied_prob(sp, break_assume) or 50
        brk_r = str(r["break_risk"]).upper() if r["break_risk"] and str(r["break_risk"])!='nan' else "MEDIUM"
        reg_r = str(r["regulatory_status"]).upper() if r["regulatory_status"] and str(r["regulatory_status"])!='nan' else "PENDING"
        sz    = {"LOW":10,"MEDIUM":18,"HIGH":28}.get(brk_r,15)
        col   = {"CLEARED":"#00d4aa","PENDING":"#f5a623"}.get(reg_r,"#ff3355")
        chart_data.append({"ticker":r["ticker"],"spread":sp,"prob":prob_,"ann":ann_,"size":sz,"color":col,"brk":brk_r,"reg":reg_r})

    if chart_data:
        fig = go.Figure()
        for reg_s, col, name in [("CLEARED","#00d4aa","Reg Cleared"),("PENDING","#f5a623","Reg Pending")]:
            pts = [p for p in chart_data if p["reg"]==reg_s]
            if not pts: continue
            fig.add_trace(go.Scatter(
                x=[p["prob"] for p in pts],
                y=[p["spread"] for p in pts],
                mode="markers+text",
                name=name,
                text=[p["ticker"] for p in pts],
                textposition="top center",
                textfont=dict(family="IBM Plex Mono",size=8,color="#6a8090"),
                marker=dict(size=[p["size"] for p in pts], color=col, opacity=0.85,
                            line=dict(color="#182436",width=1)),
                hovertemplate="<b>%{text}</b><br>Impl prob: %{x:.1f}%<br>Spread: %{y:+.2f}%<extra></extra>",
            ))
        # Quadrant lines
        fig.add_hline(y=2.0, line_color="#0e1825", line_width=1, line_dash="dot")
        fig.add_vline(x=85,  line_color="#0e1825", line_width=1, line_dash="dot")
        fig.add_annotation(x=90,y=max(sp for p in chart_data if (sp:=p.get("spread",0)) is not None)*0.95 if chart_data else 3,
                           text="High prob + high spread → alpha",
                           font=dict(color="#304050",size=8,family="IBM Plex Mono"),
                           showarrow=False)
        fig.update_layout(
            paper_bgcolor="#04060a", plot_bgcolor="#080c12",
            font=dict(family="IBM Plex Mono",size=10,color="#6a8090"),
            height=320, margin=dict(l=8,r=8,t=20,b=30),
            legend=dict(font=dict(color="#6a8090",size=9),bgcolor="rgba(0,0,0,0)"),
        )
        fig.update_xaxes(title_text=f"Implied completion probability (break={break_assume}%)",gridcolor="#0e1825",tickfont=dict(size=9),range=[50,102])
        fig.update_yaxes(title_text="Spread to terms (%)",gridcolor="#0e1825",tickfont=dict(size=9))
        st.plotly_chart(fig, width='stretch')
        st.markdown(
            f"<p style='font-family:IBM Plex Mono;font-size:0.62rem;color:#304050'>"
            f"Bubble size = break risk (larger = higher risk)  ·  Teal = reg cleared  ·  Amber = reg pending  ·  "
            f"Break scenario: {break_assume}%  ·  p = |break| / (spread + |break|)</p>",
            unsafe_allow_html=True
        )

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 4, RISK SCENARIOS
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  Scenario Analysis & CA Desk Actions", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        if spread and cur_px:
            st.markdown("<p style='font-size:0.58rem;letter-spacing:0.12em;text-transform:uppercase;color:#304050;margin-bottom:0.4rem'>P&L at different break scenarios</p>", unsafe_allow_html=True)
            scen_rows=[]; scen_hl={}
            for k,b_pct in enumerate([-5,-10,-15,-20,-25,-30]):
                b_px  = cur_px*(1+b_pct/100)
                b_pnl = pos_shares*(b_px-cur_px) if pos_shares else 0
                d_pnl = pos_shares*(cash_ps-cur_px) if (cash_ps and pos_shares) else 0
                prob_ = implied_prob(spread, b_pct)
                ev_   = prob_/100*d_pnl + (1-prob_/100)*b_pnl if prob_ else 0
                is_cur = abs(b_pct-break_assume)<1
                scen_rows.append([
                    f"{'→ ' if is_cur else '  '}{b_pct}%",
                    f"{ev['currency']} {b_px:.2f}",
                    f"{ev['currency']} {b_pnl:+,.0f}",
                    f"{prob_:.0f}%" if prob_ else "—",
                    f"{ev['currency']} {ev_:+,.0f}",
                ])
                scen_hl[k] = {0:'#c8d8e8' if is_cur else '#6a8090',
                              2:'#ff3355',
                              3:'#00d4aa' if prob_ and prob_>80 else '#d4c200',
                              4:'#00d4aa' if ev_>0 else '#ff3355'}
            dark_table(scen_rows, ["Break Scen","Break Px","Break P&L","Impl Prob","Exp Value"], scen_hl, height=238)

    with col_b:
        st.markdown(f"""<div style='font-family:IBM Plex Mono;font-size:0.7rem;color:#6a8090;line-height:1.9'>
<span style='color:#c8d8e8;font-size:0.62rem;letter-spacing:0.1em;text-transform:uppercase'>CA Desk Actions</span><br><br>
<strong style='color:#c8d8e8'>Election deadline:</strong> {fmt_date(ev.get('election_deadline','—'))}<br>
<strong style='color:#c8d8e8'>Court sanction:</strong> {sanction}<br>
<strong style='color:#c8d8e8'>Long-stop:</strong> {longstop}<br>
<strong style='color:#c8d8e8'>Regulatory:</strong> <span style='color:{reg_colour(reg_stat)}'>{reg_stat}</span><br>
<strong style='color:#c8d8e8'>Break risk:</strong> <span style='color:{risk_colour(brk)}'>{brk}</span><br><br>
1. Set election to <strong style='color:#c8d8e8'>ACCEPT</strong> before deadline<br>
2. Verify no stock on loan over record date<br>
3. Monitor regulatory/court announcements<br>
{'4. <strong style="color:#f5a623">Share deal</strong>, calculate hedge ratio: short acquirer shares × exchange ratio<br>' if is_shares else ''}
5. Update spread model on material news<br>
6. Review if spread widens materially (market pricing in risk)
</div>""", unsafe_allow_html=True)

        if brk.upper()=="LOW" and spread and spread>0:
            st.success(f"◆  LOW risk + {spread:.2f}% spread + {imp_prob:.0f}% implied prob = strong risk/reward")
        elif brk.upper()=="HIGH":
            st.markdown(f"<div style='border-left:2px solid #ff3355;background:#ff335508;padding:0.3rem 0.7rem;font-family:IBM Plex Mono;font-size:0.66rem;color:#ff3355;margin-top:0.4rem'>🔴  HIGH break risk, size position accordingly. Wide spread compensates but deal failure is material risk.</div>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# METHODOLOGY
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  Methodology & Formulas", expanded=False):
    st.markdown("""<div style='font-family:IBM Plex Mono;font-size:0.7rem;color:#6a8090;line-height:2.0'>
<span style='color:#c8d8e8;font-size:0.62rem;letter-spacing:0.12em;text-transform:uppercase'>Merger Arbitrage Analytics</span><br><br>
<strong style='color:#c8d8e8'>Implied completion probability</strong><br>
&nbsp;&nbsp;&nbsp;Key assumption: market prices the deal at fair value → EV = 0<br>
&nbsp;&nbsp;&nbsp;i.e. p × Spread + (1−p) × Break = 0<br>
&nbsp;&nbsp;&nbsp;Solving: p = |Break%| ÷ (Spread% + |Break%|)<br>
&nbsp;&nbsp;&nbsp;Example: spread 2%, break −15% → p = 15 ÷ (2+15) = 88.2%<br>
&nbsp;&nbsp;&nbsp;Limitation: assumes linear payoff, single break scenario, no partial outcomes<br><br>
<strong style='color:#c8d8e8'>Annualised return</strong><br>
&nbsp;&nbsp;&nbsp;Ann_return = Spread% ÷ Days_to_completion × 365<br>
&nbsp;&nbsp;&nbsp;Days_to_completion is user-input (not from DB), affects ann return but not implied prob<br><br>
<strong style='color:#c8d8e8'>Expected value per share</strong><br>
&nbsp;&nbsp;&nbsp;EV = p × (Deal_px − Current_px) + (1−p) × (Break_px − Current_px)<br>
&nbsp;&nbsp;&nbsp;Where Break_px = Current_px × (1 + Break%), assumed fall on deal failure<br>
&nbsp;&nbsp;&nbsp;At market price, EV = 0 by construction (the implied prob is derived from this)<br><br>
<strong style='color:#c8d8e8'>Reward : Risk framing</strong><br>
&nbsp;&nbsp;&nbsp;Expressed as Spread% : |Break%|, standard arb desk convention<br>
&nbsp;&nbsp;&nbsp;A ratio of 2%:15% means risking 15 to make 2, gross R/R = 0.13×<br>
&nbsp;&nbsp;&nbsp;Low R/R is acceptable when implied probability is very high (e.g. 90%+)<br><br>
<strong style='color:#c8d8e8'>Share deal hedge ratio</strong><br>
&nbsp;&nbsp;&nbsp;For stock consideration deals: short acquirer shares × exchange_ratio per target share<br>
&nbsp;&nbsp;&nbsp;This locks in the spread and hedges out market directional risk
</div>""", unsafe_allow_html=True)
