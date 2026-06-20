import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3, re
from datetime import date
from utils.helpers import sf, fmt_date, days_to, tdot, disc_colour, parse_ratio
from utils.ui import apply_theme, dark_table

st.set_page_config(page_title="Rights Issue Analyser · CA Alpha", page_icon="◆", layout="wide", initial_sidebar_state="expanded")
apply_theme()

DB = "data/events.db"; TODAY = date.today()

@st.cache_data(ttl=300)
def load_rights():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("""
        SELECT e.event_id, e.ticker, e.company_name, e.country, e.currency,
               e.event_type, e.status, e.election_deadline, e.ex_date, e.payment_date,
               r.rights_type, r.rights_ratio, r.subscription_price,
               r.current_price, r.terp, r.nil_paid_value, r.nil_paid_ticker,
               r.discount_to_terp_pct, r.underwriter, r.gross_proceeds_mn,
               r.fully_underwritten
        FROM events e JOIN rights_details r ON e.event_id=r.event_id
        WHERE e.event_type IN ('rights_issue','open_offer')
        AND e.status IN ('LIVE','UPCOMING')
        AND (e.election_deadline IS NULL OR e.election_deadline >= date('now'))
        ORDER BY
            julianday(e.election_deadline)-julianday('now') ASC,
            r.discount_to_terp_pct ASC
    """, conn)
    conn.close()
    return df

df = load_rights()
if df.empty:
    st.title("◆ Rights Issue Analyser")
    st.info("No live rights events.")
    st.stop()

st.sidebar.markdown("### ◆ Rights Analyser")
country_opts = ["All"] + sorted(df["country"].unique().tolist())
sel_country  = st.sidebar.selectbox("Country", country_opts)
type_opts    = ["All","Rights Issue","Open Offer"]
sel_type     = st.sidebar.selectbox("Type", type_opts)
df_filt = df if sel_country=="All" else df[df["country"]==sel_country]
if sel_type=="Rights Issue": df_filt = df_filt[df_filt["rights_type"]=="RIGHTS_ISSUE"]
elif sel_type=="Open Offer":  df_filt = df_filt[df_filt["rights_type"]=="OPEN_OFFER"]
if df_filt.empty: df_filt = df

def ev_label(r):
    d    = days_to(r["election_deadline"])
    disc = sf(r["discount_to_terp_pct"])
    return f"{tdot(d)} {r['ticker']} · {r['rights_type'].replace('_',' ').title() if r['rights_type'] else ''} · {disc:+.1f}%" if disc else f"{tdot(d)} {r['ticker']}"

labels  = [ev_label(r) for _,r in df_filt.iterrows()]
sel_idx = st.sidebar.selectbox("Event", range(len(labels)), format_func=lambda i: labels[i])
sel_idx = min(sel_idx, max(0, len(df_filt)-1))
ev = df_filt.iloc[sel_idx]

st.sidebar.markdown("---")
st.sidebar.markdown("### ◆ Position")
pos_shares = st.sidebar.number_input("Shares held", min_value=0, value=10000, step=1000)
pos_price  = st.sidebar.number_input("Current px (0 = auto)", min_value=0.0, value=0.0, step=0.5)

sub_px   = sf(ev["subscription_price"])
cur_px   = pos_price if pos_price > 0 else sf(ev["current_price"])
db_terp  = sf(ev["terp"])
db_npv   = sf(ev["nil_paid_value"])
is_open_offer = str(ev["rights_type"]).upper() == "OPEN_OFFER"  # non-renounceable: no tradeable nil-paid
disc_pct = sf(ev["discount_to_terp_pct"])
proceeds = sf(ev["gross_proceeds_mn"])
uw       = ev["fully_underwritten"]
ddl_days = days_to(ev["election_deadline"])
dot      = tdot(ddl_days)
_rn_raw, _rd_raw = parse_ratio(ev["rights_ratio"])
if (_rn_raw is None or _rd_raw is None) and ev["rights_ratio"] and str(ev["rights_ratio"]) != "nan":
    st.warning(f"Rights ratio '{ev['rights_ratio']}' could not be parsed, TERP, nil-paid, and dilution calculations use 1:1 fallback. Verify ratio format.")
rn, rd = _rn_raw or 1, _rd_raw or 1

# Calculate TERP from first principles
terp_calc = (rd*cur_px + rn*sub_px) / (rd+rn) if cur_px is not None and sub_px is not None else db_terp
nil_calc  = max(0, terp_calc - sub_px) if terp_calc and sub_px else max(0, db_npv or 0)
disc_calc = (sub_px/terp_calc - 1)*100 if terp_calc and sub_px else disc_pct
prem_terp = (cur_px/terp_calc - 1)*100 if cur_px and terp_calc else None

# ── page header ───────────────────────────────────────────────────────────────
st.title("◆ Rights Issue Analyser")
st.markdown(
    f"<div style='font-family:IBM Plex Mono;font-size:0.72rem;color:#6a8090;"
    f"padding:0.4rem 0 0.6rem;border-bottom:1px solid #182436;margin-bottom:0.9rem'>"
    f"{dot} &nbsp;<span style='color:#c8d8e8;font-weight:500'>{ev['ticker']}</span>"
    f" &nbsp;·&nbsp; {ev['company_name']} &nbsp;·&nbsp; {ev['country']}"
    f" &nbsp;·&nbsp; {ev['rights_type'].replace('_',' ').title() if ev['rights_type'] else '—'}"
    f" &nbsp;·&nbsp; Ratio: <span style='color:#c8d8e8'>{ev['rights_ratio']}</span>"
    f" &nbsp;·&nbsp; Sub deadline: <span style='color:#{'ff3355' if ddl_days is not None and ddl_days<=3 else 'f5a623' if ddl_days is not None and ddl_days<=7 else 'c8d8e8'}'>{fmt_date(ev['election_deadline'])} ({ddl_days}d)</span>"
    f"</div>",
    unsafe_allow_html=True
)

k1,k2,k3,k4,k5,k6 = st.columns(6)
k1.metric("Sub Price",      f"{ev['currency']} {sub_px:.2f}" if sub_px else "—")
k2.metric("Current Price",  f"{ev['currency']} {cur_px:.2f}" if cur_px else "—")
k3.metric("TERP",           f"{ev['currency']} {terp_calc:.2f}" if terp_calc else "—",
          help=f"({rd}×{cur_px:.0f} + {rn}×{sub_px:.0f}) / {rd+rn}" if cur_px and sub_px else "")
if is_open_offer:
    k4.metric("Nil-Paid Value", "N/A", delta="Non-renounceable", delta_color="off",
              help="Open offers are non-renounceable, the entitlement cannot be sold")
else:
    k4.metric("Nil-Paid Value", f"{ev['currency']} {nil_calc:.2f}" if nil_calc else "—",
              delta="Tradeable" if nil_calc and nil_calc>0 else None, delta_color="normal")
k5.metric("Disc to TERP",   f"{disc_calc:+.1f}%" if disc_calc is not None else "—",
          delta_color="inverse")
k6.metric("Proceeds",       f"{ev['currency']} {proceeds:,.0f}m" if proceeds else "—")

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1 — SCANNER
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  Rights Issue Scanner · All Live Events", expanded=True):
    s1,s2,s3,s4 = st.columns(4)
    deep_n   = len(df[df["discount_to_terp_pct"].apply(sf).apply(lambda x: x is not None and x<-25)])
    rights_n = len(df[df["rights_type"]=="RIGHTS_ISSUE"])
    open_n   = len(df[df["rights_type"]=="OPEN_OFFER"])
    uw_n     = len(df[df["fully_underwritten"]==1])
    s1.metric("Deep Discount (>25%)", deep_n, delta="Opportunity" if deep_n>0 else None, delta_color="normal")
    s2.metric("Rights Issues",        rights_n)
    s3.metric("Open Offers",          open_n)
    s4.metric("Fully Underwritten",   uw_n)

    scan_rows=[]; scan_hl={}
    for i,(_,r) in enumerate(df.iterrows()):
        d    = days_to(r["election_deadline"])
        sub  = sf(r["subscription_price"])
        cur  = sf(r["current_price"])
        disc = sf(r["discount_to_terp_pct"])
        proc = sf(r["gross_proceeds_mn"])
        trp  = sf(r["terp"])
        # Recalculate nil-paid
        rn_,rd_ = parse_ratio(r["rights_ratio"]); rn_=rn_ or 1; rd_=rd_ or 1
        t_calc = (rd_*cur + rn_*sub)/(rd_+rn_) if cur and sub else trp
        np_    = max(0, t_calc - sub) if t_calc and sub else 0

        row = [
            f"{tdot(d)} {r['ticker']}",
            r['company_name'][:22],
            r['country'],
            r['rights_type'].replace('_',' ').title() if r['rights_type'] else '—',
            str(r["rights_ratio"]) if r["rights_ratio"] and str(r["rights_ratio"])!='nan' else "—",
            fmt_date(r["election_deadline"]),
            f"{d}d" if d is not None and d>=0 else "—",
            f"{r['currency']} {sub:.2f}" if sub else "—",
            f"{r['currency']} {t_calc:.2f}" if t_calc else "—",
            f"{disc:+.1f}%" if disc is not None else "—",
            "N/A" if str(r["rights_type"]).upper()=="OPEN_OFFER" else (f"{r['currency']} {np_:.2f}" if np_ else "—"),
            f"{r['currency']} {proc:,.0f}m" if proc else "—",
            "✓" if r["fully_underwritten"]==1 else "—",
        ]
        scan_rows.append(row)
        scan_hl[i] = {9:disc_colour(disc), 10:'#304050' if str(r["rights_type"]).upper()=="OPEN_OFFER" else ('#00d4aa' if np_>0 else '#304050')}

    dark_table(scan_rows,
               ["Ticker","Company","Country","Type","Ratio","Deadline","Days","Sub Px","TERP","Disc%","Nil-Paid","Proceeds","UW"],
               scan_hl)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2 — TERP & POSITION ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
with st.expander(f"◆  TERP & Economics · {ev['ticker']} / {ev['company_name']}", expanded=True):
    if sub_px and cur_px:
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("<p style='font-size:0.58rem;letter-spacing:0.12em;text-transform:uppercase;color:#304050;margin-bottom:0.4rem'>TERP calculation</p>", unsafe_allow_html=True)
            econ_rows = [
                ("Rights ratio",          str(ev["rights_ratio"]),                           f"{rn} new per {rd} existing"),
                ("Current price",         f"{ev['currency']} {cur_px:.2f}",                 "Pre-rights cum price"),
                ("Subscription price",    f"{ev['currency']} {sub_px:.2f}",                 "Price to take up rights"),
                ("TERP (calculated)",     f"{ev['currency']} {terp_calc:.2f}",               f"({rd}×{cur_px:.2f} + {rn}×{sub_px:.2f}) / {rd+rn}"),
                ("Nil-paid value",        "N/A" if is_open_offer else f"{ev['currency']} {nil_calc:.2f}",  "Non-renounceable, cannot be sold" if is_open_offer else "TERP − sub price  (market value of right)"),
                ("Discount of sub to TERP",f"{disc_calc:+.1f}%",                             "How deep the issue is priced"),
                ("Current vs TERP",       f"{prem_terp:+.1f}%" if prem_terp else "—",       "Current price premium above TERP"),
                ("Underwriter",           str(ev["underwriter"]) if ev["underwriter"] and str(ev["underwriter"])!='nan' else "—", ""),
                ("Fully underwritten",    "Yes" if uw==1 else "No",                          "Protects against deal failure"),
                ("Gross proceeds",        f"{ev['currency']} {proceeds:,.0f}m" if proceeds else "—", ""),
                ("Nil-paid ticker",       "N/A" if is_open_offer else (str(ev["nil_paid_ticker"]) if ev["nil_paid_ticker"] and str(ev["nil_paid_ticker"])!='nan' else "Check prospectus"), "Non-renounceable" if is_open_offer else "Trade rights in market"),
            ]
            hl = {4:{1:'#00d4aa',2:'#00d4aa'},
                  5:{1:disc_colour(disc_calc)},
                  8:{1:'#00d4aa' if uw==1 else '#6a8090'}}
            dark_table(econ_rows, ["Parameter","Value","Note"], hl, height=430)

        with col_r:
            st.markdown("<p style='font-size:0.58rem;letter-spacing:0.12em;text-transform:uppercase;color:#304050;margin-bottom:0.4rem'>Position analysis · {:,.0f} shares</p>".format(pos_shares), unsafe_allow_html=True)
            if pos_shares > 0:
                new_ent    = int(pos_shares * rn / rd)
                sub_cost   = new_ent * sub_px
                nil_tot    = new_ent * nil_calc
                post_take  = (pos_shares + new_ent) * terp_calc
                post_lapse = pos_shares * terp_calc
                dilution   = rn / (rn + rd) * 100

                pnl_rows = [
                    ("Existing shares",     f"{pos_shares:,}",                            ""),
                    ("Rights entitlement",  f"{new_ent:,} rights",                        f"{rn}:{rd} ratio"),
                    ("Cost to take up",     f"{ev['currency']} {sub_cost:,.2f}",          f"@ {ev['currency']} {sub_px:.2f}/sh"),
                    ("Nil-paid value",      "N/A" if is_open_offer else f"{ev['currency']} {nil_tot:,.2f}",           "Non-renounceable" if is_open_offer else f"@ {ev['currency']} {nil_calc:.2f}/right"),
                    ("Post-TERP (take up)", f"{ev['currency']} {post_take:,.2f}",         f"{pos_shares+new_ent:,} sh × {terp_calc:.2f}"),
                    ("Post-TERP (lapse)",   f"{ev['currency']} {post_lapse:,.2f}",        f"{pos_shares:,} sh × {terp_calc:.2f}"),
                    ("Max dilution",        f"{dilution:.1f}%",                            "If you lapse, others take up"),
                ]
                hl2 = {2:{1:'#f5a623'}, 3:{1:'#00d4aa',2:'#00d4aa'}, 6:{1:'#ff3355'}}
                dark_table(pnl_rows, ["Metric","Value","Detail"], hl2, height=275)

                if is_open_offer:
                    if cur_px and sub_px and cur_px > sub_px:
                        st.success(f"◆  Take up: sub {ev['currency']} {sub_px:.2f} < TERP {terp_calc:.2f}. Open offer is non-renounceable: take up or let lapse, the entitlement cannot be sold.")
                    else:
                        st.warning("⚠  Sub price near or above TERP, taking up offers little benefit; lapse is reasonable. (Non-renounceable, no nil-paid to sell.)")
                elif nil_calc > 0 and cur_px > sub_px:
                    st.success(f"◆  Take up rights: sub {ev['currency']} {sub_px:.2f} < TERP {terp_calc:.2f}. Nil-paid value: {ev['currency']} {nil_tot:,.2f}")
                else:
                    st.warning("⚠  Sub price near or above TERP, consider selling nil-paid rights")

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3 — TAKE-UP vs SELL CHART
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  Take-up Economics · P&L at Different Share Prices", expanded=True):
    if sub_px and cur_px and terp_calc:
        lo = sub_px * 0.80
        hi = cur_px * 1.30
        prices = [lo + (hi-lo)*i/300 for i in range(301)]

        # Take-up: profit = market_price - sub_price per right
        takeup_pnl = [max(0, p - sub_px) for p in prices]
        # Sell rights: nil-paid value = TERP(p) - sub_price
        def t_at(p): return (rd*p + rn*sub_px)/(rd+rn)
        sell_pnl   = [max(0, t_at(p) - sub_px) for p in prices]

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=prices, y=takeup_pnl, name="Take up (profit/right)",
            line=dict(color="#00d4aa",width=2.5),
            hovertemplate=f"Price: %{{x:.2f}}<br>Profit/right: %{{y:.2f}}<extra></extra>"))
        if not is_open_offer:
            fig.add_trace(go.Scatter(x=prices, y=sell_pnl, name="Sell nil-paid (value/right)",
                line=dict(color="#f5a623",width=2,dash="dash"),
                hovertemplate=f"Price: %{{x:.2f}}<br>Nil-paid: %{{y:.2f}}<extra></extra>"))

        for vx, col, label in [
            (sub_px,   "#ff3355", f"Sub {sub_px:.0f}"),
            (terp_calc,"#304050", f"TERP {terp_calc:.0f}"),
            (cur_px,   "#6a8090", f"Now {cur_px:.0f}"),
        ]:
            fig.add_vline(x=vx, line_color=col, line_width=1, line_dash="dot",
                annotation_text=label, annotation_font=dict(color=col,size=9,family="IBM Plex Mono"))
        fig.add_hline(y=0, line_color="#182436", line_width=1)

        fig.update_layout(
            paper_bgcolor="#04060a", plot_bgcolor="#080c12",
            font=dict(family="IBM Plex Mono",size=10,color="#6a8090"),
            height=295, margin=dict(l=8,r=8,t=20,b=30),
            legend=dict(font=dict(color="#6a8090",size=9),bgcolor="rgba(0,0,0,0)",y=0.98),
        )
        fig.update_xaxes(title_text=f"Share price ({ev['currency']})",gridcolor="#0e1825",tickfont=dict(size=9))
        fig.update_yaxes(title_text="P&L per right",gridcolor="#0e1825",tickfont=dict(size=9))
        st.plotly_chart(fig, use_container_width=True)
        if is_open_offer:
            _cap = (f"Break-even (take-up): <span style='color:#c8d8e8'>{ev['currency']} {sub_px:.2f}</span>"
                    f" &nbsp;·&nbsp; <span style='color:#6a8090'>Non-renounceable, take up or lapse only</span>")
        elif cur_px > sub_px:
            _cap = (f"Break-even (take-up): <span style='color:#c8d8e8'>{ev['currency']} {sub_px:.2f}</span>"
                    f" &nbsp;·&nbsp; Nil-paid value today: <span style='color:#00d4aa'>{ev['currency']} {nil_calc:.2f}/right</span>"
                    f" &nbsp;·&nbsp; <span style='color:#00d4aa'>Take up rights, positive P&L at current price</span>")
        else:
            _cap = (f"Break-even: <span style='color:#c8d8e8'>{ev['currency']} {sub_px:.2f}</span>"
                    f" &nbsp;·&nbsp; <span style='color:#f5a623'>Consider selling nil-paid rights in market</span>")
        st.markdown(
            f"<p style='font-family:IBM Plex Mono;font-size:0.66rem;color:#6a8090'>{_cap}</p>",
            unsafe_allow_html=True
        )

        # Portfolio-level P&L — at position size from sidebar
        if pos_shares > 0:
            st.markdown(
                "<p style='font-size:0.58rem;letter-spacing:0.12em;text-transform:uppercase;"
                "color:#304050;margin-top:0.8rem;margin-bottom:0.3rem'>"
                f"Portfolio P&L, {pos_shares:,} shares, {'take-up vs lapse' if is_open_offer else 'take-up vs lapse vs sell rights'}</p>",
                unsafe_allow_html=True
            )
            rights_ent = pos_shares * rn / rd
            port_takeup = [max(0, p - sub_px) * rights_ent for p in prices]
            port_sell   = [max(0, t_at(p) - sub_px) * rights_ent for p in prices]
            port_lapse  = [0.0] * len(prices)  # lapse = zero proceeds on rights

            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=prices, y=port_takeup, name="Take up",
                line=dict(color="#00d4aa", width=2.5),
                hovertemplate=f"Price: %{{x:.2f}}<br>Take-up P&L: {ev['currency']}%{{y:,.0f}}<extra></extra>"))
            if not is_open_offer:
                fig2.add_trace(go.Scatter(x=prices, y=port_sell, name="Sell nil-paid",
                    line=dict(color="#f5a623", width=2, dash="dash"),
                    hovertemplate=f"Price: %{{x:.2f}}<br>Sell P&L: {ev['currency']}%{{y:,.0f}}<extra></extra>"))
            fig2.add_trace(go.Scatter(x=prices, y=port_lapse, name="Lapse (forfeit)",
                line=dict(color="#ff3355", width=1.5, dash="dot"),
                hovertemplate="Lapse: forfeited rights<extra></extra>"))
            for vx, col, lbl in [
                (sub_px, "#ff3355", f"Sub {sub_px:.0f}"),
                (terp_calc, "#304050", f"TERP {terp_calc:.0f}"),
                (cur_px, "#6a8090", f"Now {cur_px:.0f}"),
            ]:
                fig2.add_vline(x=vx, line_color=col, line_width=1, line_dash="dot",
                    annotation_text=lbl, annotation_font=dict(color=col, size=9, family="IBM Plex Mono"))
            fig2.update_layout(
                paper_bgcolor="#04060a", plot_bgcolor="#080c12",
                font=dict(family="IBM Plex Mono", size=10, color="#6a8090"),
                height=260, margin=dict(l=8, r=8, t=15, b=30),
                legend=dict(font=dict(color="#6a8090", size=9), bgcolor="rgba(0,0,0,0)", y=0.98),
            )
            fig2.update_xaxes(title_text=f"Share price ({ev['currency']})", gridcolor="#0e1825", tickfont=dict(size=9))
            fig2.update_yaxes(title_text=f"Total P&L ({ev['currency']})", gridcolor="#0e1825", tickfont=dict(size=9))
            st.plotly_chart(fig2, use_container_width=True)
            # Callout at current price
            _tu_now  = max(0, cur_px - sub_px) * rights_ent
            _sel_now = max(0, nil_calc) * rights_ent
            _sell_seg = "" if is_open_offer else f" &nbsp;·&nbsp; sell nil-paid = <span style='color:#f5a623'>{ev['currency']} {_sel_now:,.0f}</span>"
            st.markdown(
                f"<p style='font-family:IBM Plex Mono;font-size:0.64rem;color:#6a8090'>"
                f"At current price: take-up = <span style='color:#00d4aa'>{ev['currency']} {_tu_now:,.0f}</span>"
                f"{_sell_seg}"
                f" &nbsp;·&nbsp; lapse = <span style='color:#ff3355'>forfeited</span>"
                f"</p>", unsafe_allow_html=True
            )

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 4 — DILUTION TABLE
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  Dilution Analysis", expanded=False):
    if sub_px and cur_px and rn and rd:
        st.markdown(
            f"<p style='font-size:0.7rem;color:#6a8090;margin-bottom:0.4rem'>"
            f"Dilution effect on existing holders who do <em>not</em> take up rights, "
            f"at different overall take-up rates.</p>",
            unsafe_allow_html=True
        )
        col_d, col_e = st.columns(2)
        with col_d:
            dil_rows=[]; dil_hl={}
            for k,takeup_pct in enumerate([0,20,40,60,80,100]):
                # At take-up X%: fraction of new shares issued = X%
                # New shares issued = X% × (total_existing × rn/rd)
                # Total shares post = existing + new_issued
                # Dilution to non-taker = new_issued / total_post
                frac_new   = takeup_pct/100 * rn/rd  # per existing share
                total_mult = 1 + frac_new             # multiplier on share count
                dil        = frac_new / total_mult * 100
                # Post-TERP for non-taker
                new_terp   = (cur_px + frac_new*sub_px) / total_mult
                dil_rows.append([
                    f"{takeup_pct}%",
                    f"{frac_new:.4f}",
                    f"{dil:.2f}%",
                    f"{ev['currency']} {new_terp:.2f}",
                    f"{(new_terp/cur_px-1)*100:+.2f}%",
                ])
                dil_hl[k] = {2:'#ff3355' if dil>5 else '#f5a623' if dil>2 else '#6a8090',
                             4:'#ff3355' if new_terp<cur_px else '#6a8090'}
            dark_table(dil_rows, ["Take-up Rate","New Sh/Existing","Dilution","New TERP","TERP vs Current"], dil_hl, height=245)

        with col_e:
            st.markdown(f"""<div style='font-family:IBM Plex Mono;font-size:0.7rem;color:#6a8090;line-height:1.9'>
<span style='color:#c8d8e8;font-size:0.62rem;letter-spacing:0.1em;text-transform:uppercase'>Key Points</span><br><br>
Max dilution (100% take-up): <span style='color:#ff3355'>{rn/(rn+rd)*100:.1f}%</span><br>
Rights ratio: <span style='color:#c8d8e8'>{ev["rights_ratio"]}</span><br>
Sub price discount to current: <span style='color:#c8d8e8'>{(sub_px/cur_px-1)*100:+.1f}%</span><br><br>
Non-participating holders suffer TERP dilution.
Deep discount issues (like this one at {disc_calc:.1f}% vs TERP) are more dilutive.
Taking up rights preserves economic position.
</div>""", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 5 — SETTLEMENT & LENDER
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  Settlement & Lender Considerations", expanded=False):
    col_a, col_b = st.columns(2)
    with col_a:
        # Calculate T-2 business days from record date for lender recall deadline
        _rec_date_str = fmt_date(ev.get("record_date"))
        _recall_by_ri = "—"
        if _rec_date_str != "—":
            try:
                from datetime import date as _d2, timedelta as _td2
                _rec2 = _d2.fromisoformat(_rec_date_str)
                _cnt2, _rb2 = 0, _rec2
                while _cnt2 < 2:
                    _rb2 -= _td2(days=1)
                    if _rb2.weekday() < 5:
                        _cnt2 += 1
                _recall_by_ri = _rb2.isoformat()
            except Exception:
                _recall_by_ri = "T−2 from record"
        _np_trading = "Entitlement non-renounceable, cannot be traded" if is_open_offer else "Nil-paid trading opens: ex-date"
        _np_ticker = str(ev["nil_paid_ticker"]) if ev["nil_paid_ticker"] and str(ev["nil_paid_ticker"])!='nan' else "Check prospectus"
        _np_tail = ("<span style='color:#6a8090'>Non-renounceable, no nil-paid instrument</span>" if is_open_offer
                    else f"Nil-paid ticker: <span style='color:#c8d8e8'>{_np_ticker}</span><br>Current nil-paid value: <span style='color:#00d4aa'>{ev['currency']} {nil_calc:.2f}</span>")
        st.markdown(f"""<div style='font-family:IBM Plex Mono;font-size:0.7rem;color:#6a8090;line-height:1.9'>
<span style='color:#c8d8e8;font-size:0.62rem;letter-spacing:0.1em;text-transform:uppercase'>Timeline</span><br><br>
Ex-date: <span style='color:#c8d8e8'>{fmt_date(ev["ex_date"])}</span><br>
Record date: <span style='color:#c8d8e8'>{fmt_date(ev.get("record_date"))}</span><br>
{_np_trading}<br>
Subscription deadline: <span style='color:#c8d8e8'>{fmt_date(ev["election_deadline"])}</span> ({ddl_days}d)<br>
Payment/settlement: <span style='color:#c8d8e8'>{fmt_date(ev["payment_date"])}</span><br><br>
{_np_tail}
</div>""", unsafe_allow_html=True)

    with col_b:
        _recall_html = f"<span style='color:#{'ff3355' if _recall_by_ri not in ('—','T−2 from record') else '6a8090'}'>{_recall_by_ri}</span> <span style='color:#304050'>(T−2 business days before record date)</span>"
        if is_open_offer:
            _lender_body = (
                "Shares on loan over record date: borrower is holder of record and receives the "
                "<strong style='color:#f5a623'>non-renounceable</strong> entitlement.<br><br>"
                "The entitlement cannot be sold or manufactured back as a tradeable right. To "
                "participate, the lender must recall before record date to become holder of record "
                "and decide take-up vs lapse.<br><br>"
                f"Recall by: {_recall_html}<br><br>"
                "No nil-paid value to capture, the recall decision turns on the take-up opportunity "
                "(subscribe below TERP), not on selling rights."
            )
        else:
            _lender_body = (
                "Shares on loan over ex-date: borrower receives nil-paid rights. "
                "Lender receives <strong style='color:#f5a623'>manufactured nil-paid rights</strong> from borrower.<br><br>"
                "Lender must instruct borrower on election before deadline. "
                "If stock not recalled, election instruction must go via borrower, coordination critical.<br><br>"
                f"Recall by: {_recall_html}<br><br>"
                f"Recall if nil-paid value ({ev['currency']} {nil_calc:.2f}/right × {int(pos_shares*rn/rd):,} rights = "
                f"<span style='color:#00d4aa'>{ev['currency']} {int(pos_shares*rn/rd)*nil_calc:,.0f}</span>) exceeds lending income."
            )
        st.markdown(f"""<div style='font-family:IBM Plex Mono;font-size:0.7rem;color:#6a8090;line-height:1.9'>
<span style='color:#c8d8e8;font-size:0.62rem;letter-spacing:0.1em;text-transform:uppercase'>Lender Considerations</span><br><br>
{_lender_body}
</div>""", unsafe_allow_html=True)

    if ddl_days is not None and 0 <= ddl_days <= 5:
        _imm_tail = "election window closing imminently" if is_open_offer else "nil-paid rights trading closing imminently"
        st.markdown(f"<div style='border-left:2px solid #ff3355;background:#ff335508;padding:0.3rem 0.7rem;font-family:IBM Plex Mono;font-size:0.66rem;color:#ff3355;margin-top:0.3rem'>🔴  Subscription deadline {ddl_days}d, {_imm_tail}.</div>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# METHODOLOGY
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  Methodology & Formulas", expanded=False):
    st.markdown("""<div style='font-family:IBM Plex Mono;font-size:0.7rem;color:#6a8090;line-height:2.0'>
<span style='color:#c8d8e8;font-size:0.62rem;letter-spacing:0.12em;text-transform:uppercase'>Rights Issue Valuation</span><br><br>
<strong style='color:#c8d8e8'>Theoretical Ex-Rights Price (TERP)</strong><br>
&nbsp;&nbsp;&nbsp;TERP = (N_existing × P_cum + N_new × Sub_price) ÷ (N_existing + N_new)<br>
&nbsp;&nbsp;&nbsp;Assumption: no market impact, no signalling effect, linear share dilution<br>
&nbsp;&nbsp;&nbsp;Example, 1 for 4 at 80p, current 120p: TERP = (4×120 + 1×80) ÷ 5 = 112p<br><br>
<strong style='color:#c8d8e8'>Nil-paid value (value of the right itself)</strong><br>
&nbsp;&nbsp;&nbsp;Nil_paid = max(0, TERP − Sub_price)<br>
&nbsp;&nbsp;&nbsp;This is the intrinsic value of the right to subscribe at Sub_price when stock trades at TERP<br>
&nbsp;&nbsp;&nbsp;Traded in the market as a separate instrument between ex-date and subscription deadline<br><br>
<strong style='color:#c8d8e8'>Discount to TERP</strong><br>
&nbsp;&nbsp;&nbsp;Disc% = Sub_price ÷ TERP − 1  (typically negative, deeper = more dilutive)<br>
&nbsp;&nbsp;&nbsp;Reflects how aggressively the issue is priced to ensure take-up<br><br>
<strong style='color:#c8d8e8'>Maximum dilution (if all rights taken up)</strong><br>
&nbsp;&nbsp;&nbsp;Dilution_max = N_new ÷ (N_existing + N_new)<br>
&nbsp;&nbsp;&nbsp;Non-participating holders suffer this dilution to their economic position<br><br>
<strong style='color:#c8d8e8'>Lender recall deadline</strong><br>
&nbsp;&nbsp;&nbsp;Recall_by = Record_date − 2 business days<br>
&nbsp;&nbsp;&nbsp;Shares must be back in the account before record date for the holder to receive nil-paid rights
</div>""", unsafe_allow_html=True)
