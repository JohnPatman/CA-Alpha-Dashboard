import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3
from datetime import date
from utils.helpers import sf, fmt_date, days_to, tdot, ann_ret, prem_colour, ann_colour
from utils.ui import apply_theme, dark_table

st.set_page_config(page_title="Tender Tracker · CA Alpha", page_icon="◆", layout="wide", initial_sidebar_state="expanded")
apply_theme()

DB = "data/events.db"; TODAY = date.today()

@st.cache_data(ttl=300)
def load_tenders():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("""
        SELECT e.event_id, e.ticker, e.company_name, e.country, e.currency,
               e.event_type, e.status, e.election_deadline,
               t.tender_type, t.tender_price, t.tender_price_low, t.tender_price_high,
               t.current_price, t.premium_to_mkt_pct, t.max_shares_sought,
               t.max_value_mn, t.proration_expected, t.estimated_proration_pct,
               t.odd_lot_threshold, t.odd_lot_guaranteed
        FROM events e JOIN tender_details t ON e.event_id=t.event_id
        WHERE e.event_type IN ('tender_offer','dutch_auction')
        AND e.status IN ('LIVE','UPCOMING')
        AND (e.election_deadline IS NULL OR e.election_deadline >= date('now'))
    """, conn)
    conn.close()
    # Compute days and annualised return
    df["_days"]    = df["election_deadline"].apply(days_to)
    df["_ann_ret"] = df.apply(lambda r: ann_ret(sf(r["premium_to_mkt_pct"]), r["_days"]), axis=1)
    # Sort: by annualised return desc (highest alpha first)
    df = df.sort_values("_ann_ret", ascending=False, na_position="last")
    return df

df = load_tenders()
if df.empty:
    st.title("◆ Tender Tracker")
    st.info("No live tender events.")
    st.stop()

st.sidebar.markdown("### ◆ Tender Tracker")
type_opts = ["All","Fixed Price","Dutch Auction"]
sel_type  = st.sidebar.selectbox("Type", type_opts)
df_filt   = df
if sel_type=="Fixed Price":    df_filt = df[df["tender_type"]=="FIXED"]
elif sel_type=="Dutch Auction": df_filt = df[df["tender_type"]=="DUTCH_AUCTION"]
if df_filt.empty: df_filt = df  # fallback

def ev_label(r):
    d   = r["_days"]
    ann = r["_ann_ret"]
    tp  = sf(r["tender_price"]) or ((sf(r["tender_price_low"],0)+sf(r["tender_price_high"],0))/2)
    return f"{tdot(d)} {r['ticker']} · {r['tender_type'][:5]} · {f'{ann:.0f}%ann' if ann else '—'}"

labels  = [ev_label(r) for _,r in df_filt.iterrows()]
sel_idx = st.sidebar.selectbox("Event", range(len(labels)), format_func=lambda i: labels[i])
sel_idx = min(sel_idx, max(0, len(df_filt)-1))
ev = df_filt.iloc[sel_idx]

st.sidebar.markdown("---")
st.sidebar.markdown("### ◆ Position")
pos_shares = st.sidebar.number_input("Shares held", min_value=0, value=10000, step=1000)
bid_price  = st.sidebar.number_input("Dutch bid (0 = midpoint)", min_value=0.0, value=0.0, step=0.5)

is_fixed  = ev["tender_type"]=="FIXED"
is_dutch  = ev["tender_type"]=="DUTCH_AUCTION"
tp        = sf(ev["tender_price"])
tp_lo     = sf(ev["tender_price_low"])
tp_hi     = sf(ev["tender_price_high"])
cur_px    = sf(ev["current_price"])
prem      = sf(ev["premium_to_mkt_pct"])
max_val   = sf(ev["max_value_mn"])
proration = sf(ev["estimated_proration_pct"])
pro_exp   = ev["proration_expected"]
ddl_days  = ev["_days"]
ann       = ev["_ann_ret"]
dot       = tdot(ddl_days)

# ── page header ───────────────────────────────────────────────────────────────
st.title("◆ Tender Tracker")
st.markdown(
    f"<div style='font-family:IBM Plex Mono;font-size:0.72rem;color:#6a8090;"
    f"padding:0.4rem 0 0.6rem;border-bottom:1px solid #182436;margin-bottom:0.9rem'>"
    f"{dot} &nbsp;<span style='color:#c8d8e8;font-weight:500'>{ev['ticker']}</span>"
    f" &nbsp;·&nbsp; {ev['company_name']} &nbsp;·&nbsp; {ev['country']}"
    f" &nbsp;·&nbsp; {'Fixed Price Tender' if is_fixed else 'Dutch Auction'}"
    f" &nbsp;·&nbsp; Deadline: <span style='color:#c8d8e8'>{fmt_date(ev['election_deadline'])}"
    f" ({ddl_days}d)</span>"
    f"</div>",
    unsafe_allow_html=True
)

# ── KPIs ──────────────────────────────────────────────────────────────────────
k1,k2,k3,k4,k5 = st.columns(5)
if is_fixed and tp and cur_px:
    spread = tp - cur_px
    k1.metric("Tender Price",    f"{ev['currency']} {tp:.2f}")
    k2.metric("Current Price",   f"{ev['currency']} {cur_px:.2f}")
    k3.metric("Spread",          f"{ev['currency']} {spread:.2f}  ({prem:+.1f}%)" if prem else f"{ev['currency']} {spread:.2f}")
    k4.metric("Annualised Ret",
              f"{ann:.0f}%" if ann else "—",
              delta="◆ Alpha" if ann and ann > 30 else None,
              delta_color="normal")
    k5.metric("Days to Deadline", f"{ddl_days}d" if ddl_days is not None else "—",
              delta="Urgent" if ddl_days is not None and ddl_days<=7 else None,
              delta_color="inverse" if ddl_days is not None and ddl_days<=7 else "off")
elif is_dutch and tp_lo and tp_hi:
    mid = (tp_lo+tp_hi)/2
    k1.metric("Range",           f"{ev['currency']} {tp_lo:.2f} – {tp_hi:.2f}")
    k2.metric("Midpoint",        f"{ev['currency']} {mid:.2f}")
    k3.metric("Current Price",   f"{ev['currency']} {cur_px:.2f}" if cur_px else "—")
    k4.metric("Max Size",        f"{ev['currency']} {max_val:,.0f}m" if max_val else "—")
    k5.metric("Days to Deadline",f"{ddl_days}d" if ddl_days is not None else "—")

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1 — SCANNER (sorted by annualised return)
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  Tender Scanner — Ranked by Annualised Return", expanded=True):
    s1,s2,s3,s4 = st.columns(4)
    fixed_n   = len(df[df["tender_type"]=="FIXED"])
    dutch_n   = len(df[df["tender_type"]=="DUTCH_AUCTION"])
    best_ann  = df["_ann_ret"].dropna().max()
    best_tick = df.loc[df["_ann_ret"].idxmax(),"ticker"] if not df["_ann_ret"].dropna().empty else "—"
    urgent_n  = len(df[(df["_days"].apply(lambda x: x is not None and 0<=x<=7))])
    s1.metric("Fixed Tenders",     fixed_n)
    s2.metric("Dutch Auctions",    dutch_n)
    s3.metric("Best Ann Return",   f"{best_ann:.0f}%" if best_ann else "—",
              delta=f"{best_tick}" if best_tick!="—" else None, delta_color="normal")
    s4.metric("Deadline ≤7d",      urgent_n, delta="Urgent" if urgent_n>0 else None, delta_color="inverse" if urgent_n>0 else "off")

    scan_rows=[]; scan_hl={}
    for i,(_,r) in enumerate(df.iterrows()):
        d    = r["_days"]
        ann_ = r["_ann_ret"]
        prem_= sf(r["premium_to_mkt_pct"])
        tp_  = sf(r["tender_price"])
        tlo_ = sf(r["tender_price_low"]); thi_ = sf(r["tender_price_high"])
        cur_ = sf(r["current_price"])
        pro_ = sf(r["estimated_proration_pct"])
        mv_  = sf(r["max_value_mn"])
        t_str = f"{r['currency']} {tp_:.2f}" if tp_ else (f"{r['currency']} {tlo_:.0f}–{thi_:.0f}" if tlo_ else "—")

        row = [
            f"{tdot(d)} {r['ticker']}",
            r['company_name'][:20],
            r['country'],
            r['tender_type'].replace('_',' ').title() if r['tender_type'] else '—',
            f"{d}d" if d is not None and d>=0 else "—",
            t_str,
            f"{r['currency']} {cur_:.2f}" if cur_ else "—",
            f"{prem_:+.1f}%" if prem_ is not None else "—",
            f"{ann_:.0f}%" if ann_ else "—",
            f"{r['currency']} {mv_:,.0f}m" if mv_ else "—",
            f"~{pro_:.0f}%" if r["proration_expected"]==1 and pro_ else "None",
        ]
        scan_rows.append(row)
        scan_hl[i] = {
            7: prem_colour(prem_),
            8: ann_colour(ann_),
            10: '#f5a623' if r["proration_expected"]==1 else '#304050',
        }

    dark_table(scan_rows,
               ["Ticker","Company","Country","Type","Days","Tender Px","Current","Prem %","Ann Ret","Size","Proration"],
               scan_hl)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2 — ECONOMICS DEEP-DIVE
# ═════════════════════════════════════════════════════════════════════════════
with st.expander(f"◆  Analysis — {ev['ticker']} / {ev['company_name']}", expanded=True):
    col_l, col_r = st.columns(2)
    with col_l:
        st.markdown("<p style='font-size:0.58rem;letter-spacing:0.12em;text-transform:uppercase;color:#304050;margin-bottom:0.4rem'>Economics</p>", unsafe_allow_html=True)

        if is_fixed and tp and cur_px:
            spread_abs = tp - cur_px
            spread_pct = spread_abs / cur_px * 100
            econ_rows = [
                ("Type",              "Fixed Price Tender",                      ""),
                ("Tender price",      f"{ev['currency']} {tp:.2f}",             "Company will buy at this price"),
                ("Current price",     f"{ev['currency']} {cur_px:.2f}",         "Last traded"),
                ("Spread (abs)",      f"{ev['currency']} {spread_abs:.2f}",     "Gross upside"),
                ("Spread (%)",        f"{prem:+.1f}%",                           ""),
                ("Annualised return", f"{ann:.0f}%  ({prem:.1f}% / {ddl_days}d × 365)" if ann and ddl_days else "—", "Key metric for arb desks"),
                ("Max tender size",   f"{ev['currency']} {max_val:,.0f}m" if max_val else "—", ""),
                ("Proration expected","Yes" if pro_exp==1 else "No",             ""),
                ("Est. proration",    f"~{proration:.0f}%" if proration else "—","% of tendered shares bought"),
                ("Days to deadline",  f"{ddl_days}d" if ddl_days is not None else "—", fmt_date(ev["election_deadline"])),
            ]
            hl = {4:{1:prem_colour(prem)},
                  5:{1:'#00d4aa' if ann and ann>30 else '#d4c200',2:'#00d4aa' if ann and ann>30 else '#6a8090'},
                  8:{1:'#f5a623' if proration else '#6a8090'}}
            dark_table(econ_rows, ["Parameter","Value","Note"], hl, height=390)

        elif is_dutch and tp_lo and tp_hi:
            mid  = (tp_lo+tp_hi)/2
            my_bid = bid_price if bid_price>0 else mid
            econ_rows = [
                ("Type",           "Dutch Auction",                             ""),
                ("Range low",      f"{ev['currency']} {tp_lo:.2f}",            "Min clearing price"),
                ("Range high",     f"{ev['currency']} {tp_hi:.2f}",            "Max clearing price"),
                ("Midpoint",       f"{ev['currency']} {mid:.2f}",              "Expected clearing"),
                ("Current price",  f"{ev['currency']} {cur_px:.2f}" if cur_px else "—", ""),
                ("Prem at mid",    f"{((mid/cur_px)-1)*100:+.1f}%" if cur_px else "—", ""),
                ("Ann ret at mid", f"{ann_ret(((mid/cur_px)-1)*100 if cur_px else 0, ddl_days):.0f}%" if cur_px and ddl_days and ddl_days>0 else "—", ""),
                ("Your bid",       f"{ev['currency']} {my_bid:.2f}",           "Set in sidebar"),
                ("Max size",       f"{ev['currency']} {max_val:,.0f}m" if max_val else "—",""),
                ("Est. proration", f"~{proration:.0f}%" if proration else "—", ""),
                ("Days to close",  f"{ddl_days}d" if ddl_days else "—",        fmt_date(ev["election_deadline"])),
            ]
            hl = {7:{1:'#00d4aa' if my_bid>=tp_lo else '#ff3355'}}
            dark_table(econ_rows, ["Parameter","Value","Note"], hl, height=425)

    with col_r:
        st.markdown("<p style='font-size:0.58rem;letter-spacing:0.12em;text-transform:uppercase;color:#304050;margin-bottom:0.4rem'>Position P&L — {:,.0f} shares</p>".format(pos_shares), unsafe_allow_html=True)
        if pos_shares > 0 and cur_px:

            if is_fixed and tp:
                mkt_val    = pos_shares * cur_px
                deal_val   = pos_shares * tp
                gross_pnl  = deal_val - mkt_val
                gross_pct  = gross_pnl / mkt_val * 100

                if pro_exp==1 and proration:
                    pro_rate  = proration/100
                    accepted  = int(pos_shares * pro_rate)
                    remaining = pos_shares - accepted
                    pro_pnl   = accepted * (tp - cur_px)
                    eff_px    = (accepted*tp + remaining*cur_px) / pos_shares
                    eff_prem  = (eff_px/cur_px - 1)*100
                    eff_ann   = ann_ret(eff_prem, ddl_days)

                    pnl_rows = [
                        ("Shares tendered",      f"{pos_shares:,}",                    "Full position"),
                        ("Est. proration",        f"~{proration:.0f}%",                ""),
                        ("Shares accepted",       f"{accepted:,}",                     f"@ {ev['currency']} {tp:.2f}"),
                        ("Shares returned",       f"{remaining:,}",                    "Continue at market"),
                        ("P&L on accepted",       f"{ev['currency']} {pro_pnl:+,.2f}", f"{ev['currency']} {tp-cur_px:.2f}/sh"),
                        ("Effective price",       f"{ev['currency']} {eff_px:.2f}",    f"{eff_prem:+.2f}% vs market"),
                        ("Eff. annualised ret",   f"{eff_ann:.0f}%" if eff_ann else "—","After proration adjustment"),
                    ]
                    hl2 = {4:{1:'#00d4aa' if pro_pnl>0 else '#ff3355'},
                           6:{1:ann_colour(eff_ann)}}
                else:
                    pnl_rows = [
                        ("Shares tendered",   f"{pos_shares:,}",                       "Full position"),
                        ("Market value",      f"{ev['currency']} {mkt_val:,.2f}",      f"@ {ev['currency']} {cur_px:.2f}"),
                        ("Tender proceeds",   f"{ev['currency']} {deal_val:,.2f}",     f"@ {ev['currency']} {tp:.2f}"),
                        ("Gross P&L",         f"{ev['currency']} {gross_pnl:+,.2f}",  f"{gross_pct:+.2f}%"),
                        ("Annualised return",  f"{ann:.0f}%" if ann else "—",           f"{prem:.1f}% in {ddl_days}d"),
                    ]
                    hl2 = {3:{1:'#00d4aa' if gross_pnl>0 else '#ff3355'},
                           4:{1:ann_colour(ann)}}
                dark_table(pnl_rows, ["Metric","Value","Detail"], hl2, height=220)

            elif is_dutch and tp_lo and tp_hi:
                my_bid = bid_price if bid_price>0 else (tp_lo+tp_hi)/2
                pro_r  = (proration or 80)/100
                accepted = int(pos_shares * pro_r)
                pnl_r  = accepted * (my_bid - cur_px) if cur_px else 0
                pnl_rows = [
                    ("Shares tendered",   f"{pos_shares:,}",                           ""),
                    ("Your bid",          f"{ev['currency']} {my_bid:.2f}",            "Set in sidebar"),
                    ("Est. proration",    f"~{proration:.0f}%" if proration else "~80%",""),
                    ("Est. accepted",     f"{accepted:,}",                             ""),
                    ("Est. proceeds",     f"{ev['currency']} {accepted*my_bid:,.2f}",  ""),
                    ("Est. P&L",          f"{ev['currency']} {pnl_r:+,.2f}",           "If clears at bid"),
                ]
                hl2 = {5:{1:'#00d4aa' if pnl_r>0 else '#ff3355'}}
                dark_table(pnl_rows, ["Metric","Value","Detail"], hl2, height=240)

            # Alpha callout
            if is_fixed and ann and ann > 50:
                st.success(f"◆  {ev['ticker']}: {prem:.1f}% spread / {ddl_days}d = {ann:.0f}% annualised")
            elif is_fixed and ann:
                st.markdown(f"<div style='border-left:2px solid #d4c200;background:#d4c20010;padding:0.3rem 0.6rem;font-family:IBM Plex Mono;font-size:0.66rem;color:#d4c200'>{prem:.1f}% spread / {ddl_days}d = {ann:.0f}% annualised</div>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3 — PRORATION ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
if is_fixed and pro_exp==1 and proration and tp and cur_px:
    with st.expander("◆  Proration Modelling — P&L at All Fill Rates", expanded=True):
        col_pt, col_pc = st.columns([2,3])
        with col_pt:
            spread_abs = tp - cur_px
            pro_rows=[]; pro_hl={}
            for i,pct in enumerate([10,20,30,40,50,60,70,80,90,100]):
                pr    = pct/100
                acc   = int((pos_shares or 10000) * pr)
                pnl   = acc * spread_abs
                eff   = (acc*tp + ((pos_shares or 10000)-acc)*cur_px)/(pos_shares or 10000)
                eff_p = (eff/cur_px-1)*100
                eff_a = ann_ret(eff_p, ddl_days)
                is_est = abs(pct-proration)<5
                pro_rows.append([
                    f"{'→ ' if is_est else '  '}{pct}%",
                    f"{acc:,}",
                    f"{ev['currency']} {pnl:+,.0f}",
                    f"{ev['currency']} {eff:.2f}",
                    f"{eff_a:.0f}%" if eff_a else "—",
                ])
                pro_hl[i] = {0:'#c8d8e8' if is_est else '#6a8090',
                             2:'#00d4aa' if pnl>0 else '#ff3355',
                             4:ann_colour(eff_a)}
            dark_table(pro_rows, ["Fill Rate","Accepted","P&L","Eff Px","Ann Ret"], pro_hl, height=375)

        with col_pc:
            pcts  = list(range(10,101,5))
            pnls  = [(pos_shares or 10000)*p/100*(tp-cur_px) for p in pcts]
            fig   = go.Figure()
            fig.add_trace(go.Bar(x=[f"{p}%" for p in pcts], y=pnls,
                marker_color=["#00d4aa" if abs(p-proration)<3 else "#243548" for p in pcts],
                marker_line_width=0,
                hovertemplate="Fill: %{x}<br>P&L: %{y:,.0f}<extra></extra>"))
            fig.update_layout(
                paper_bgcolor="#04060a", plot_bgcolor="#080c12",
                font=dict(family="IBM Plex Mono",size=10,color="#6a8090"),
                height=310, margin=dict(l=8,r=8,t=20,b=30),
                showlegend=False
            )
            fig.update_xaxes(title_text="Proration fill rate",gridcolor="#0e1825",tickfont=dict(size=8,color="#6a8090"))
            fig.update_yaxes(title_text=f"P&L ({ev['currency']})",gridcolor="#0e1825",tickfont=dict(size=9))
            st.plotly_chart(fig, use_container_width=True)
            st.markdown(
                f"<p style='font-family:IBM Plex Mono;font-size:0.66rem;color:#6a8090'>"
                f"Est. fill ~{proration:.0f}% · Spread {ev['currency']} {spread_abs:.2f}/sh ({prem:.1f}%) · "
                f"{ann:.0f}% ann · P&L at ~{proration:.0f}%: "
                f"<span style='color:#00d4aa'>{ev['currency']} {int((pos_shares or 10000)*proration/100)*spread_abs:,.0f}</span>"
                f"</p>",
                unsafe_allow_html=True
            )

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 4 — DUTCH AUCTION BID STRATEGY
# ═════════════════════════════════════════════════════════════════════════════
if is_dutch and tp_lo and tp_hi:
    with st.expander("◆  Dutch Auction Bid Strategy", expanded=True):
        col_dc, col_dt = st.columns([3,2])
        with col_dc:
            cp = cur_px or (tp_lo+tp_hi)/2
            clearing_prices = [tp_lo + (tp_hi-tp_lo)*i/100 for i in range(101)]
            values = [p * (pos_shares or 10000) for p in clearing_prices]
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=clearing_prices, y=values, name="Proceeds if cleared at X",
                line=dict(color="#00d4aa",width=2.5),
                hovertemplate=f"Clearing: {ev['currency']}%{{x:.2f}}<br>Proceeds: {ev['currency']}%{{y:,.0f}}<extra></extra>"))
            if cp:
                fig.add_hline(y=cp*(pos_shares or 10000), line_color="#304050", line_width=1, line_dash="dot",
                    annotation_text="Market value", annotation_font=dict(color="#304050",size=9,family="IBM Plex Mono"))
            fig.add_vline(x=(tp_lo+tp_hi)/2, line_color="#6a8090", line_width=1, line_dash="dot",
                annotation_text=f"Mid {(tp_lo+tp_hi)/2:.0f}",
                annotation_font=dict(color="#6a8090",size=9,family="IBM Plex Mono"))
            fig.update_layout(
                paper_bgcolor="#04060a", plot_bgcolor="#080c12",
                font=dict(family="IBM Plex Mono",size=10,color="#6a8090"),
                height=260, margin=dict(l=8,r=8,t=20,b=30),
                showlegend=False
            )
            fig.update_xaxes(title_text=f"Clearing price ({ev['currency']})",gridcolor="#0e1825",tickfont=dict(size=9))
            fig.update_yaxes(title_text="Proceeds",gridcolor="#0e1825",tickfont=dict(size=9))
            st.plotly_chart(fig, use_container_width=True)

        with col_dt:
            bid_levels = [
                (tp_lo,                        "Floor",     "Fill only if low clears",   '#f5a623'),
                (tp_lo+(tp_hi-tp_lo)*0.25,     "Low (25%)", "",                          '#d4c200'),
                ((tp_lo+tp_hi)/2,              "Mid (50%)", "Balanced risk/reward",      '#c8d8e8'),
                (tp_lo+(tp_hi-tp_lo)*0.75,     "High (75%)","Higher fill probability",   '#00d4aa'),
                (tp_hi,                        "Ceiling",   "Max fill probability",      '#00d4aa'),
            ]
            bid_rows = [(f"{ev['currency']} {px:.2f}", lbl, note) for px,lbl,note,_ in bid_levels]
            hl3 = {i:{0:col,1:col} for i,(_,_,_,col) in enumerate(bid_levels)}
            dark_table(bid_rows, ["Bid","Level","Note"], hl3, height=205)
            st.markdown(
                f"<p style='font-family:IBM Plex Mono;font-size:0.64rem;color:#6a8090;margin-top:0.3rem'>"
                f"Range: {ev['currency']} {tp_lo:.2f}–{tp_hi:.2f} · "
                f"Bid at or above mid to maximise fill probability. "
                f"Company sets clearing price = lowest accepted bid.</p>",
                unsafe_allow_html=True
            )
