import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import math
from datetime import date
from utils.helpers import sf
from utils.ui import apply_theme, dark_table, render_top_nav

st.set_page_config(page_title="ADR Pricing · CA Alpha", page_icon="◆", layout="wide", initial_sidebar_state="expanded")
apply_theme()
render_top_nav()
TODAY = date.today()

# ═════════════════════════════════════════════════════════════════════════════
# SYNTHETIC ADR / CROSS-LISTED DATASET
#
# All GBX→USD conversions use spot_fx = 0.012647
# This is: 1 GBX (pence) × 0.01 × GBPUSD(1.2647) = $0.012647
#
# ADR prices are set to produce realistic small arbs (±0.1–0.8% gross)
# reflecting typical intraday pricing inefficiencies in liquid names.
# Cross-listings (CROSS type) can show slightly wider spreads (1–3%) due to
# structural differences: different shareholder bases, franking credits, index
# inclusion differences, and cross-currency settlement mechanics.
#
# Arb verification for each pair (in comments):
#   local_usd = local_px × spot_fx
#   implied_local = adr_px / adr_ratio
#   gross_arb = (implied_local - local_usd) / local_usd × 100
# ═════════════════════════════════════════════════════════════════════════════
_FX = 0.012647   # GBX → USD (GBPUSD = 1.2647)
ADR_DATA = [
    # ── UK ADR pairs ──────────────────────────────────────────────────────────
    # BP.L/BP: 480p, 6:1 → local_usd=$6.071, fair_adr=$36.42, actual=$36.55 → +0.36% gross
    dict(ticker_l="BP.L",    ticker_a="BP",    company="BP PLC",
         typ="ADR",  local_px=480.0,  local_ccy="GBX", local_exch="LSE", local_mkt_cap=80.4,
         adr_px=36.55,  adr_ratio=6, spot_fx=_FX, friction=0.20, adr_exch="NYSE"),

    # SHEL.L/SHEL: 2680p, 2:1 → local_usd=$33.90, fair_adr=$67.80, actual=$67.55 → -0.37% gross
    dict(ticker_l="SHEL.L",  ticker_a="SHEL",  company="Shell PLC",
         typ="ADR",  local_px=2680.0, local_ccy="GBX", local_exch="LSE", local_mkt_cap=162.1,
         adr_px=67.55,  adr_ratio=2, spot_fx=_FX, friction=0.20, adr_exch="NYSE"),

    # AZN.L/AZN: direct NYSE listing since 2 Feb 2026. The harmonised listing replaced the former
    # 2:1 Nasdaq ADR; LSE and NYSE now trade the same fungible ordinary share, so this arbs to parity
    # (tight), unlike the non-fungible dual-primaries below. 11920p → local_usd=$150.75, NYSE=$151.24 → +0.32%
    dict(ticker_l="AZN.L",   ticker_a="AZN",   company="AstraZeneca PLC",
         typ="CROSS", local_px=11920.0,local_ccy="GBX", local_exch="LSE", local_mkt_cap=196.0,
         adr_px=151.24, adr_ratio=1, spot_fx=_FX, friction=0.20,
         adr_exch="NYSE", adr_ccy="USD", adr_spot=1.0),

    # GSK.L/GSK: 1720p, 2:1 → local_usd=$21.75, fair_adr=$43.50, actual=$43.73 → +0.53% gross
    dict(ticker_l="GSK.L",   ticker_a="GSK",   company="GSK PLC",
         typ="ADR",  local_px=1720.0, local_ccy="GBX", local_exch="LSE", local_mkt_cap=71.2,
         adr_px=43.73,  adr_ratio=2, spot_fx=_FX, friction=0.20, adr_exch="NYSE"),

    # HSBA.L/HSBC: 735p, 5:1 → local_usd=$9.295, fair_adr=$46.48, actual=$46.27 → -0.45% gross
    dict(ticker_l="HSBA.L",  ticker_a="HSBC",  company="HSBC Holdings PLC",
         typ="ADR",  local_px=735.0,  local_ccy="GBX", local_exch="LSE", local_mkt_cap=136.4,
         adr_px=46.27,  adr_ratio=5, spot_fx=_FX, friction=0.25, adr_exch="NYSE"),

    # BTI.L/BTI: 2620p, 1:1 → local_usd=$33.13, actual=$33.19 → +0.18% gross (net -0.02%, monitor)
    dict(ticker_l="BTI.L",   ticker_a="BTI",   company="BAT PLC",
         typ="ADR",  local_px=2620.0, local_ccy="GBX", local_exch="LSE", local_mkt_cap=56.2,
         adr_px=33.19,  adr_ratio=1, spot_fx=_FX, friction=0.20, adr_exch="NYSE"),

    # ULVR.L/UL: 4380p, 1:1 → local_usd=$55.41, actual=$55.69 → +0.51% gross
    dict(ticker_l="ULVR.L",  ticker_a="UL",    company="Unilever PLC",
         typ="ADR",  local_px=4380.0, local_ccy="GBX", local_exch="LSE", local_mkt_cap=113.8,
         adr_px=55.69,  adr_ratio=1, spot_fx=_FX, friction=0.20, adr_exch="NYSE"),

    # RIO.L/RIO (ADR): 5240p, 1:1 → local_usd=$66.23, actual=$66.59 → +0.54% gross
    dict(ticker_l="RIO.L",   ticker_a="RIO",   company="Rio Tinto PLC (ADR)",
         typ="ADR",  local_px=5240.0, local_ccy="GBX", local_exch="LSE", local_mkt_cap=83.6,
         adr_px=66.59,  adr_ratio=1, spot_fx=_FX, friction=0.20, adr_exch="NYSE"),

    # ── Dual-primary cross-listings (AUD/GBX same economic interest) ──────────
    # BHP.L/BHP.AX: 2220p vs AUD 44.85 → BHP.L_usd=$28.08, BHP.AX_usd=$28.93 → +3.0% structural gap
    # This premium is common due to ASX index weights, franking credits, and different shareholder bases
    dict(ticker_l="BHP.L",   ticker_a="BHP.AX",company="BHP Group (dual-listed LSE/ASX)",
         typ="CROSS", local_px=2220.0, local_ccy="GBX", local_exch="LSE", local_mkt_cap=109.2,
         adr_px=44.85, adr_ratio=1,    spot_fx=_FX, friction=0.35,
         adr_exch="ASX", adr_ccy="AUD", adr_spot=0.645),

    # RIO.L/RIO.AX (cross): 5240p vs AUD 132.50 → RIO.L_usd=$66.23, RIO.AX_usd=$85.46 → structural
    # RIO Ltd (ASX class) persistently trades at premium to RIO PLC (LSE) due to Australian shareholder base
    dict(ticker_l="RIO.L",   ticker_a="RIO.AX",company="Rio Tinto (dual-listed LSE/ASX)",
         typ="CROSS", local_px=5240.0, local_ccy="GBX", local_exch="LSE", local_mkt_cap=83.6,
         adr_px=104.50, adr_ratio=1,   spot_fx=_FX, friction=0.35,
         adr_exch="ASX", adr_ccy="AUD", adr_spot=0.645),
]

# ═════════════════════════════════════════════════════════════════════════════
# CALCULATIONS
# ═════════════════════════════════════════════════════════════════════════════
def calc_arb(row):
    is_cross = row.get("typ") == "CROSS"
    local_px  = row["local_px"]
    local_ccy = row["local_ccy"]
    spot_fx   = row["spot_fx"]      # local → USD
    adr_px    = row["adr_px"]       # USD (or AUD for cross-listed)
    adr_ratio = row["adr_ratio"]    # local shares per ADR (or 1:1 for cross)
    friction  = row["friction"]     # round-trip %

    # Local price in USD
    local_usd = local_px * spot_fx

    if is_cross:
        # AUD side → USD
        adr_spot = row.get("adr_spot", 1.0)
        other_usd = adr_px * adr_spot
        implied_local_usd = other_usd  # 1:1 ratio
    else:
        # ADR price implies local price in USD
        implied_local_usd = adr_px / adr_ratio   # USD per local share from ADR
        other_usd = adr_px

    arb_pct   = (implied_local_usd - local_usd) / local_usd * 100
    # Round-trip friction is a cost that always erodes the edge toward zero,
    # regardless of which leg is bought. Subtracting it with the sign of the
    # gross arb keeps "buy ADR" (negative) rows from being inflated.
    net_arb   = arb_pct - math.copysign(friction, arb_pct) if arb_pct else -friction
    direction = "BUY LOCAL / SELL ADR" if arb_pct > 0 else "BUY ADR / SELL LOCAL"
    actionable = abs(net_arb) >= 0.10  # net of friction

    return dict(
        local_usd       = local_usd,
        implied_local_usd = implied_local_usd,
        other_usd       = other_usd,
        arb_pct         = arb_pct,
        net_arb         = net_arb,
        direction       = direction,
        actionable      = actionable,
    )

processed = []
for row in ADR_DATA:
    r = dict(row)
    r.update(calc_arb(row))
    processed.append(r)

processed.sort(key=lambda x: abs(x["net_arb"]), reverse=True)

# ═════════════════════════════════════════════════════════════════════════════
# UI
# ═════════════════════════════════════════════════════════════════════════════
st.title("◆ ADR / Cross-Listed Pricing")
st.markdown(
    "<div style='font-family:IBM Plex Mono;font-size:0.70rem;color:#6a8090;"
    "padding:0.3rem 0 0.7rem;border-bottom:1px solid #182436;margin-bottom:0.8rem'>"
    "Conversion-adjusted price comparison between primary listing and ADR / secondary exchange. "
    "Arb = (implied local price from ADR − local market price) / local price. "
    "Net arb = gross arb minus estimated round-trip friction. "
    "Action flag triggers when |net arb| ≥ 0.10%.</div>",
    unsafe_allow_html=True
)

n_act = sum(1 for r in processed if r["actionable"])
n_prem = sum(1 for r in processed if r["arb_pct"] > 0)
avg_gross = sum(abs(r["arb_pct"]) for r in processed) / max(len(processed),1)

k1,k2,k3,k4 = st.columns(4)
k1.metric("Pairs Monitored",   len(processed))
k2.metric("Actionable (net)",  n_act,   help="|net arb| ≥ 0.10% after friction")
k3.metric("ADR at Premium",    n_prem,  help="ADR implied price > local market")
k4.metric("Avg Gross Arb",     f"{avg_gross:.2f}%", help="Absolute average before friction")

st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1, SCANNER TABLE
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  ADR Arb Scanner · All Pairs", expanded=True):
    scan_rows = []; scan_hl = {}
    for i,r in enumerate(processed):
        # Direction abbreviated: ▲ = buy local/sell ADR, ▼ = buy ADR/sell local
        dir_short = "▲ Buy local" if r["arb_pct"] > 0 else "▼ Buy ADR"
        act_flag  = "◆ ACTION" if r["actionable"] else "Monitor"
        row = [
            r["ticker_l"],
            r["ticker_a"],
            r["company"][:16],
            r["typ"],
            f"{r['arb_pct']:+.3f}%",
            f"{r['net_arb']:+.3f}%",
            dir_short if r["actionable"] else "—",
            act_flag,
        ]
        scan_rows.append(row)
        net = r["net_arb"]
        scan_hl[i] = {
            4: "#00d4aa" if r["arb_pct"] > 0 else "#ff3355",
            5: "#00d4aa" if net > 0.10 else "#ff3355" if net < -0.10 else "#6a8090",
            7: "#00d4aa" if r["actionable"] else "#304050",
        }

    dark_table(scan_rows,
               ["Local","ADR/Alt","Company","Type","Gross Arb","Net Arb","Direction","Signal"],
               scan_hl)
    st.markdown(
        "<p style='font-family:IBM Plex Mono;font-size:0.58rem;color:#304050;margin-top:0.2rem'>"
        "Net arb = gross arb − round-trip friction (0.20–0.35%). "
        "Full price breakdown and FX rate in deep-dive below. "
        "Action flag: |net arb| ≥ 0.10%.</p>",
        unsafe_allow_html=True
    )

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2, DEEP-DIVE (selected pair)
# ═════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)
sel_tickers = [f"{r['ticker_l']} / {r['ticker_a']}  ·  {r['company']}" for r in processed]
sel_idx = st.selectbox("Select pair for deep-dive", range(len(sel_tickers)),
                       format_func=lambda i: sel_tickers[i])
r = processed[sel_idx]

# KPIs
st.markdown(
    f"<div style='font-family:IBM Plex Mono;font-size:0.68rem;color:#6a8090;"
    f"padding:0.3rem 0 0.5rem;margin-bottom:0.6rem;border-bottom:1px solid #182436'>"
    f"{r['company']} &nbsp;·&nbsp; {r['local_exch']} ({r['local_ccy']}) "
    f"↔ {r['adr_exch']} ({r.get('adr_ccy','USD')}) &nbsp;·&nbsp; "
    f"Ratio: {r['adr_ratio']}:1 &nbsp;·&nbsp; Type: {r['typ']}"
    f"</div>", unsafe_allow_html=True
)

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Local Price",     f"{r['local_ccy']} {r['local_px']:.2f}")
c2.metric("Local in USD",    f"USD {r['local_usd']:.4f}", help=f"× {r['spot_fx']:.6f} FX rate")
c3.metric("ADR Implied USD", f"USD {r['implied_local_usd']:.4f}", help="ADR price ÷ ratio")
c4.metric("Gross Arb",       f"{r['arb_pct']:+.3f}%",
          delta="ADR at premium" if r["arb_pct"]>0 else "ADR at discount")
c5.metric("Net Arb",         f"{r['net_arb']:+.3f}%",
          delta="◆ ACTIONABLE" if r["actionable"] else "Below threshold",
          delta_color="normal" if r["actionable"] else "off")

# Arb breakdown bar chart, percentages only (prices are incomparable scale)
_friction_step = -math.copysign(r["friction"], r["arb_pct"]) if r["arb_pct"] else -r["friction"]
_levels = [0.0, r["arb_pct"], r["net_arb"]]
_lo, _hi = min(_levels), max(_levels)
_pad = max((_hi - _lo) * 0.22, 0.3)
fig = go.Figure(go.Waterfall(
    orientation="v",
    measure=["absolute", "relative", "total"],
    x=["Gross Arb", "Round-trip Friction", "Net Arb"],
    y=[r["arb_pct"], _friction_step, r["net_arb"]],
    text=[f"{r['arb_pct']:+.3f}%", f"{_friction_step:+.3f}%", f"{r['net_arb']:+.3f}%"],
    textposition="outside",
    textfont=dict(family="IBM Plex Mono", size=10, color="#c8d8e8"),
    connector=dict(line=dict(color="#243548", width=1)),
    increasing=dict(marker=dict(color="#00d4aa")),
    decreasing=dict(marker=dict(color="#ff3355")),
    totals=dict(marker=dict(color="#00d4aa" if r["net_arb"] > 0.10 else "#ff3355" if r["net_arb"] < -0.10 else "#6a8090")),
    hovertemplate="%{x}: %{y:+.4f}%<extra></extra>",
))
fig.add_hline(y=0, line_color="#182436", line_width=1)
fig.update_layout(
    paper_bgcolor="#04060a", plot_bgcolor="#080c12",
    font=dict(family="IBM Plex Mono", size=10, color="#6a8090"),
    height=280, margin=dict(l=8, r=8, t=30, b=30),
    showlegend=False, yaxis_ticksuffix="%",
)
fig.update_xaxes(gridcolor="#0e1825")
fig.update_yaxes(gridcolor="#0e1825", zeroline=False, range=[_lo - _pad, _hi + _pad])
st.plotly_chart(fig, width='stretch')

# Detail table
detail_rows = [
    ("Local ticker",          r["ticker_l"],                          f"Primary listing on {r['local_exch']}"),
    ("ADR / alt ticker",      r["ticker_a"],                          f"Listed on {r['adr_exch']}"),
    ("Conversion ratio",      f"{r['adr_ratio']} local : 1 ADR",     "Local shares represented by one ADR" if r["typ"]=="ADR" else "1:1 cross-listing"),
    ("Local price",           f"{r['local_ccy']} {r['local_px']:.2f}", f"Primary exchange last traded"),
    ("FX rate",               f"{r['local_ccy']}→USD {r['spot_fx']:.6f}", "Market spot rate applied"),
    ("Local price (USD)",     f"USD {r['local_usd']:.4f}",            "Local price converted at spot"),
    ("ADR/alt price",         f"USD {r['adr_px']:.4f}" if r.get('adr_ccy','USD')=='USD' else f"{r.get('adr_ccy','USD')} {r['adr_px']:.4f}", f"Last traded on {r['adr_exch']}"),
    ("ADR implied local",     f"USD {r['implied_local_usd']:.4f}",    "ADR price ÷ ratio, what local should trade at"),
    ("Gross arb",             f"{r['arb_pct']:+.4f}%",                "(Implied − local) ÷ local × 100"),
    ("Round-trip friction",   f"{r['friction']:.2f}%",                "Est. conversion fees + bid-ask + timing"),
    ("Net arb",               f"{r['net_arb']:+.4f}%",                "Gross arb minus round-trip friction"),
    ("Direction",             r["direction"],                          "Which leg to buy / sell"),
    ("Signal",                "◆ ACTIONABLE" if r["actionable"] else "MONITOR", "|net arb| ≥ 0.10% threshold"),
]
hl_d = {}
for i, row_d in enumerate(detail_rows):
    if row_d[0] == "Net arb":
        hl_d[i] = {1: "#00d4aa" if r["net_arb"]>0.10 else "#ff3355" if r["net_arb"]<-0.10 else "#6a8090"}
    if row_d[0] == "Signal":
        hl_d[i] = {1: "#00d4aa" if r["actionable"] else "#304050"}
dark_table(detail_rows, ["Parameter","Value","Note"], hl_d, height=480)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3, METHODOLOGY
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  Methodology & Formulas", expanded=False):
    st.markdown("""<div style='font-family:IBM Plex Mono;font-size:0.7rem;color:#6a8090;line-height:2.0'>
<span style='color:#c8d8e8;font-size:0.62rem;letter-spacing:0.12em;text-transform:uppercase'>ADR / Cross-Listed Arbitrage</span><br><br>
<strong style='color:#c8d8e8'>Core relationship</strong><br>
&nbsp;&nbsp;&nbsp;In efficient markets, the ADR price should equal the local share price converted at spot FX:<br>
&nbsp;&nbsp;&nbsp;ADR_fair = (Local_price × FX_rate) × ADR_ratio<br>
&nbsp;&nbsp;&nbsp;Any deviation (gross arb) is theoretically exploitable before friction costs<br><br>
<strong style='color:#c8d8e8'>Gross arbitrage</strong><br>
&nbsp;&nbsp;&nbsp;Gross_arb% = (Implied_local_USD − Local_USD) ÷ Local_USD × 100<br>
&nbsp;&nbsp;&nbsp;Where Implied_local_USD = ADR_price ÷ ADR_ratio<br>
&nbsp;&nbsp;&nbsp;Positive = ADR at premium to local → buy local, short ADR<br>
&nbsp;&nbsp;&nbsp;Negative = ADR at discount → buy ADR, short local<br><br>
<strong style='color:#c8d8e8'>Net arbitrage (after friction)</strong><br>
&nbsp;&nbsp;&nbsp;Net_arb% = Gross_arb% − Friction%<br>
&nbsp;&nbsp;&nbsp;Friction includes: ADR conversion fees (typically 0.01–0.03 USD/share),<br>
&nbsp;&nbsp;&nbsp;bid-ask spread on both legs (~0.05–0.10% each), FX conversion cost (~0.05%),<br>
&nbsp;&nbsp;&nbsp;and timing risk between execution legs (~0.05%)<br><br>
<strong style='color:#c8d8e8'>Cross-listings: fungible vs non-fungible</strong><br>
&nbsp;&nbsp;&nbsp;Fungible listings (e.g. AZN LSE/NYSE, direct-listed on the NYSE since 2 Feb 2026,<br>
&nbsp;&nbsp;&nbsp;replacing its former Nasdaq ADR) are the same transferable share, so they arb to near parity;<br>
&nbsp;&nbsp;&nbsp;residual edge is just FX timing and transfer friction<br>
&nbsp;&nbsp;&nbsp;Non-fungible dual-primaries (e.g. BHP LSE/ASX) are separate lines in the same company<br>
&nbsp;&nbsp;&nbsp;Arb = (GBX price in USD) vs (other-currency price in USD) at current spot rates<br>
&nbsp;&nbsp;&nbsp;These carry persistent structural gaps (franking credits, index weights, distinct holder bases)<br>
&nbsp;&nbsp;&nbsp;and higher friction from currency conversion and settlement differences on both legs<br><br>
<strong style='color:#c8d8e8'>Limitations of this model</strong><br>
&nbsp;&nbsp;&nbsp;Does not account for dividend entitlement timing differences between ADR and local<br>
&nbsp;&nbsp;&nbsp;Does not model borrowing costs for short positions<br>
&nbsp;&nbsp;&nbsp;Assumes simultaneous execution, in practice, leg 2 carries short-term market risk<br>
&nbsp;&nbsp;&nbsp;Corporate events (dividends, splits) can temporarily widen the spread
</div>""", unsafe_allow_html=True)
