import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import date, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.db import get_live_events, get_filter_options, traffic_light

st.set_page_config(
    page_title="Event Pipeline · CA Alpha",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&display=swap');
:root {
    --bg:#04060a; --bg-card:#080c12;
    --accent:#00d4aa; --accent-dim:#00d4aa12;
    --red:#ff3355; --amber:#f5a623; --yellow:#d4c200;
    --border:#0e1825; --border-mid:#182436; --border-bright:#243548;
    --text-primary:#c8d8e8; --text-secondary:#6a8090; --text-muted:#304050;
    --font-mono:'IBM Plex Mono',monospace;
}
html,body,.stApp,[class*="css"]{background:var(--bg)!important;color:var(--text-primary)!important;}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"]{display:none!important;}
.main .block-container{padding:1rem 2rem 3rem!important;max-width:100%!important;}

section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div:first-child{
    background:var(--bg)!important;border-right:1px solid var(--border-mid)!important;
    width:200px!important;min-width:200px!important;max-width:200px!important;}
section[data-testid="stSidebar"] *{font-family:var(--font-mono)!important;color:var(--text-secondary)!important;}
section[data-testid="stSidebar"] [aria-current="page"],
section[data-testid="stSidebar"] [aria-current="page"] *{color:var(--accent)!important;background:var(--accent-dim)!important;border-left:none!important;border-radius:0!important;}
section[data-testid="stSidebar"] a,
section[data-testid="stSidebar"] li,
section[data-testid="stSidebar"] [role="listitem"]{border-radius:0!important;}
section[data-testid="stSidebar"] label{font-size:0.58rem!important;letter-spacing:0.14em!important;text-transform:uppercase!important;}
section[data-testid="stSidebar"] .stMarkdown p{font-size:0.58rem!important;letter-spacing:0.14em!important;text-transform:uppercase!important;border-bottom:1px solid var(--border-mid)!important;padding-bottom:0.25rem!important;margin-bottom:0.4rem!important;}


h1{font-family:var(--font-mono)!important;font-size:0.82rem!important;font-weight:500!important;color:var(--accent)!important;letter-spacing:0.18em!important;text-transform:uppercase!important;padding:0.5rem 0 0.4rem!important;border-bottom:1px solid var(--border-mid)!important;margin-bottom:0.8rem!important;}
h2{font-family:var(--font-mono)!important;font-size:0.55rem!important;font-weight:600!important;letter-spacing:0.2em!important;text-transform:uppercase!important;color:var(--text-muted)!important;margin-top:1.6rem!important;margin-bottom:0.4rem!important;padding-bottom:0.25rem!important;border-bottom:1px solid var(--border)!important;}
p{color:var(--text-secondary)!important;font-size:0.72rem!important;font-family:var(--font-mono)!important;line-height:1.5!important;}
strong{color:var(--text-primary)!important;font-weight:500!important;}

[data-testid="stMetric"]{background:var(--bg-card)!important;border:1px solid var(--border-mid)!important;border-top:1px solid var(--border-bright)!important;border-radius:0!important;padding:0.5rem 0.8rem!important;}
[data-testid="stMetric"] label{font-family:var(--font-mono)!important;font-size:0.52rem!important;letter-spacing:0.16em!important;text-transform:uppercase!important;color:var(--text-muted)!important;}
[data-testid="stMetric"] [data-testid="stMetricValue"]{font-family:var(--font-mono)!important;font-size:1.35rem!important;font-weight:400!important;color:var(--text-primary)!important;line-height:1.1!important;}
[data-testid="stMetricDelta"] svg{display:none!important;}
[data-testid="stMetricDelta"]{font-family:var(--font-mono)!important;font-size:0.58rem!important;color:var(--red)!important;}

[data-testid="stDataFrame"]{border:1px solid var(--border-mid)!important;border-radius:0!important;}

[data-testid="stButton"] button{background:transparent!important;border:1px solid var(--border-bright)!important;border-radius:0!important;color:var(--text-secondary)!important;font-family:var(--font-mono)!important;font-size:0.58rem!important;letter-spacing:0.14em!important;text-transform:uppercase!important;padding:0.25rem 0.65rem!important;}
[data-testid="stButton"] button:hover{border-color:var(--accent)!important;color:var(--accent)!important;background:var(--accent-dim)!important;}

[data-testid="stSelectbox"]>div>div{background:var(--bg-card)!important;border:1px solid var(--border-mid)!important;border-radius:0!important;color:var(--text-primary)!important;font-family:var(--font-mono)!important;font-size:0.72rem!important;}
[data-testid="stCheckbox"] label p{font-family:var(--font-mono)!important;font-size:0.64rem!important;color:var(--text-secondary)!important;letter-spacing:0.04em!important;text-transform:none!important;}
[data-testid="stRadio"] label p{font-family:var(--font-mono)!important;font-size:0.68rem!important;color:var(--text-secondary)!important;text-transform:none!important;}

/* collapsible sections */
[data-testid="stExpander"]{background:transparent!important;border:0!important;border:1px solid var(--border-mid)!important;border-radius:0!important;margin-bottom:0.4rem!important;}
[data-testid="stExpander"] summary{font-family:var(--font-mono)!important;font-size:0.62rem!important;font-weight:600!important;letter-spacing:0.16em!important;text-transform:uppercase!important;color:var(--text-secondary)!important;padding:0.45rem 0.7rem!important;background:var(--bg-card)!important;border-radius:0!important;}
[data-testid="stExpander"] summary:hover{color:var(--text-primary)!important;}
[data-testid="stExpander"][open]>summary{color:var(--accent)!important;border-bottom:1px solid var(--border-mid)!important;}
[data-testid="stExpander"] [data-testid="stExpanderDetails"]{background:var(--bg)!important;padding:0.6rem 0.4rem!important;}
[data-testid="stExpander"] [data-testid="stExpanderDetails"] p{font-size:0.7rem!important;color:var(--text-primary)!important;}
[data-testid="stExpander"] [data-testid="stExpanderDetails"] strong{font-size:0.68rem!important;color:var(--text-secondary)!important;font-weight:400!important;}

/* event card rows — nested expanders inside section expanders */
[data-testid="stExpanderDetails"] [data-testid="stExpander"]{border:0!important;border-bottom:1px solid var(--border)!important;margin-bottom:0!important;}
[data-testid="stExpanderDetails"] [data-testid="stExpander"] summary{background:transparent!important;font-size:0.7rem!important;font-weight:400!important;letter-spacing:0!important;text-transform:none!important;color:var(--text-secondary)!important;padding:0.3rem 0.4rem!important;}
[data-testid="stExpanderDetails"] [data-testid="stExpander"] summary:hover{color:var(--text-primary)!important;background:var(--bg-card)!important;}
[data-testid="stExpanderDetails"] [data-testid="stExpander"][open]>summary{color:var(--text-primary)!important;border-left:2px solid var(--accent)!important;padding-left:0.5rem!important;border-bottom:1px solid var(--border-mid)!important;}
[data-testid="stExpanderDetails"] [data-testid="stExpanderDetails"]{background:var(--bg-card)!important;border-left:2px solid var(--border-mid)!important;padding:0.5rem 0.8rem!important;}

[data-testid="stAlert"],.stAlert{font-family:var(--font-mono)!important;font-size:0.66rem!important;border-radius:0!important;border:0!important;border-left:2px solid var(--accent)!important;background:var(--accent-dim)!important;color:var(--accent)!important;padding:0.25rem 0.5rem!important;}
[data-testid="stCaptionContainer"] p{font-size:0.6rem!important;color:var(--text-muted)!important;}
hr{border-color:var(--border-mid)!important;margin:0.4rem 0!important;}
::-webkit-scrollbar{width:3px;height:3px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--border-bright);}

[data-testid="collapsedControl"]:hover,
[data-testid="collapsedControl"]:hover * {
    color:#04060a!important;
    background:#04060a!important;
}

/* sidebar collapse — maximum specificity + every hiding property */
html body [data-testid="stSidebarCollapseButton"],
html body [data-testid="collapsedControl"],
html body [data-testid="stSidebarNavCollapseButton"] {
    display:none!important;
    visibility:hidden!important;
    opacity:0!important;
    width:0!important;height:0!important;
    max-width:0!important;max-height:0!important;
    min-width:0!important;min-height:0!important;
    overflow:hidden!important;
    padding:0!important;margin:0!important;
    border:0!important;outline:0!important;
    position:fixed!important;
    top:-9999px!important;left:-9999px!important;
    pointer-events:none!important;
    transform:scale(0)!important;
    clip-path:inset(100%)!important;
    font-size:0!important;
    color:transparent!important;
    background:transparent!important;
}


/* cover the ( bracket with a same-colour overlay */
section[data-testid="stSidebar"]::before {
    content:"";
    position:fixed;
    top:0;
    left:0;
    width:18px;
    height:100vh;
    background:#04060a;
    z-index:99999;
    pointer-events:none;
}


/* kill ( bracket — it's a ::before pseudo-element on sidebar nav */
section[data-testid="stSidebar"] *::before,
section[data-testid="stSidebar"] *::after {
    content:none!important;
    display:none!important;
    width:0!important;
    height:0!important;
}


/* beat emotion specificity — kill ( bracket pseudo-element */
html body section[data-testid="stSidebar"] *::before,
html body section[data-testid="stSidebar"] *::after {
    content:none!important;
    display:none!important;
    width:0!important;
    height:0!important;
    visibility:hidden!important;
}


/* kill both active indicator bars */
html body section[data-testid="stSidebar"] *[aria-current="page"]::before,
html body section[data-testid="stSidebar"] *[aria-current="page"]::after,
html body section[data-testid="stSidebar"] [aria-current="page"] > *:first-child {
    display:none!important;
    width:0!important;
    border:none!important;
    content:none!important;
}

</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ── JS: kill sidebar collapse bracket by text content ────────────────────────
import streamlit.components.v1 as _c
_c.html("""
<script>
(function() {
    function kill() {
        try {
            var d = window.parent.document;
            // Hide by data-testid
            ['stSidebarCollapseButton','collapsedControl','stSidebarNavCollapseButton'].forEach(function(id) {
                d.querySelectorAll('[data-testid="'+id+'"]').forEach(function(el) {
                    el.style.cssText = 'display:none!important;';
                });
            });
            // Hide by text content — find any leaf element containing only "("
            d.querySelectorAll('button, span, div, a').forEach(function(el) {
                if (el.children.length === 0 && el.textContent.trim() === '(') {
                    el.style.cssText = 'display:none!important;';
                    el.parentElement && (el.parentElement.style.cssText = 'display:none!important;');
                }
            });
        } catch(e) {}
    }
    kill();
    [100,300,800,2000].forEach(function(t){ setTimeout(kill, t); });
    try {
        new MutationObserver(kill).observe(
            window.parent.document.body,
            {childList:true, subtree:true}
        );
    } catch(e) {}
})();
</script>
""", height=1)
# ─────────────────────────────────────────────────────────────────────────────






TODAY = date.today()

CATEGORY_LABELS = {
    "MANDATORY":             "Mandatory",
    "MANDATORY_WITH_CHOICE": "Choice",
    "VOLUNTARY":             "Voluntary",
}
TYPE_LABELS = {
    "scrip_dividend":        "Scrip Dividend",
    "fx_election":           "CCY Election",
    "rights_issue":          "Rights Issue",
    "open_offer":            "Open Offer",
    "tender_offer":          "Tender Offer",
    "dutch_auction":         "Dutch Auction",
    "scheme_of_arrangement": "Scheme",
    "merger":                "Merger",
    "exchange_offer":        "Exchange Offer",
    "spinoff":               "Spinoff",
    "demerger":              "Demerger",
    "stock_split":           "Stock Split",
    "consolidation":         "Consolidation",
}

def fmt_type(t):  return TYPE_LABELS.get(t, t.replace("_", " ").title())
def fmt_date(d):
    if not d or str(d) == "nan": return "—"
    return str(d)[:10]
def safe_int(v):
    try:
        if v is None or str(v) == "nan": return None
        return int(v)
    except: return None

def alpha_flag(row):
    flags = []
    t = row.get("event_type", "")
    if t in ("scrip_dividend", "fx_election"):
        arb  = row.get("fx_arbitrage_pct")
        disc = row.get("scrip_discount_pct")
        if arb and float(arb) > 1.5:   flags.append(f"CCY arb {float(arb):.2f}%")
        if disc and float(disc) > 0:   flags.append("Scrip premium")
    if t == "rights_issue":
        disc = row.get("discount_to_terp_pct")
        if disc and float(disc) < -25: flags.append(f"Deep discount {float(disc):.1f}%")
    if t in ("scheme_of_arrangement", "merger"):
        spread = row.get("spread_to_terms_pct")
        brk    = row.get("break_risk", "")
        if spread and float(spread) > 1.5: flags.append(f"Spread {float(spread):.2f}%")
        if brk == "LOW":                   flags.append("Low break risk")
    if t == "tender_offer":
        prem = row.get("premium_to_mkt_pct")
        if prem and float(prem) > 5: flags.append(f"{float(prem):.1f}% premium")
    return "  ·  ".join(flags) if flags else ""

def render_table(df):
    """Render dataframe as dark HTML table in isolated iframe."""
    import streamlit.components.v1 as _comp
    import html as _hl
    import pandas as _pd

    cols = list(df.columns)
    headers = "".join(f"<th>{col}</th>" for col in cols)
    rows_html = ""
    for i, (_, row) in enumerate(df.iterrows()):
        bg = "#080c12" if i % 2 == 0 else "#04060a"
        cells = ""
        for col in cols:
            raw = row[col]
            if raw is None or (not isinstance(raw, str) and _pd.isna(raw)):
                val = "—"
            else:
                val = _hl.escape(str(raw))
            align = "right" if col == "Days" else "left"
            cls = ' class="alpha"' if (col == "Alpha" and val.strip() and val != "—") else ""
            cells += f'<td style="text-align:{align};background:{bg}"{cls}>{val}</td>'
        rows_html += f"<tr>{cells}</tr>"

    html = f"""<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
html,body{{background:#04060a;font-family:'IBM Plex Mono',monospace;}}
table{{width:100%;border-collapse:collapse;font-size:0.68rem;}}
th{{padding:0.3rem 0.7rem;text-align:left;font-size:0.52rem;letter-spacing:0.12em;text-transform:uppercase;color:#6a8090;background:#04060a;border-bottom:1px solid #243548;white-space:nowrap;}}
td{{padding:0.28rem 0.7rem;color:#c8d8e8;border-bottom:1px solid #0e1825;white-space:nowrap;}}
td.alpha{{color:#00d4aa;}}
tr:hover td{{background:#0e1825!important;}}
</style></head><body>
<table><thead><tr>{headers}</tr></thead><tbody>{rows_html}</tbody></table>
</body></html>"""

    _comp.html(html, height=min(len(df) * 32 + 55, 620), scrolling=True)

def render_cards(df_section):
    """Render events as expandable card rows."""
    if df_section.empty:
        st.info("No events in this section.")
        return
    for _, row in df_section.iterrows():
        days_int  = safe_int(row.get("days_to_deadline"))
        tl_dot, tl_label = traffic_light(days_int)
        cat_short  = CATEGORY_LABELS.get(row["event_category"], row["event_category"])
        type_label = TYPE_LABELS.get(row["event_type"], row["event_type"])
        alpha      = row["alpha_flag"]
        t          = row["event_type"]
        parts      = []

        if t in ("scrip_dividend", "fx_election"):
            if row.get("cash_amount") and str(row["cash_amount"]) != "nan":
                parts.append(f"Div  {row['cash_currency']} {float(row['cash_amount']):.4f}")
            if row.get("dividend_currency_opts") and str(row["dividend_currency_opts"]) != "nan":
                parts.append(f"CCY  {row['dividend_currency_opts']}")
            if row.get("fx_arbitrage_pct") and str(row["fx_arbitrage_pct"]) != "nan":
                parts.append(f"CCY arb  {float(row['fx_arbitrage_pct']):.2f}%")
            if row.get("optimal_election") and str(row["optimal_election"]) != "nan":
                parts.append(f"Optimal  {row['optimal_election']}")
        elif t in ("rights_issue", "open_offer"):
            if row.get("rights_ratio") and str(row["rights_ratio"]) != "nan":
                parts.append(f"Ratio  {row['rights_ratio']}")
            if row.get("subscription_price") and str(row["subscription_price"]) != "nan":
                parts.append(f"Sub px  {row['currency']} {float(row['subscription_price']):.2f}")
            if row.get("terp") and str(row["terp"]) != "nan":
                parts.append(f"TERP  {float(row['terp']):.2f}")
            if row.get("discount_to_terp_pct") and str(row["discount_to_terp_pct"]) != "nan":
                parts.append(f"Disc to TERP  {float(row['discount_to_terp_pct']):.1f}%")
            if row.get("underwriter") and str(row["underwriter"]) != "nan":
                parts.append(f"UW  {row['underwriter']}")
        elif t in ("tender_offer", "dutch_auction"):
            if row.get("tender_price") and str(row["tender_price"]) != "nan":
                parts.append(f"Price  {float(row['tender_price']):.2f}")
            if row.get("tender_price_low") and str(row["tender_price_low"]) != "nan":
                parts.append(f"Range  {float(row['tender_price_low']):.0f}–{float(row['tender_price_high']):.0f}")
            if row.get("max_value_mn") and str(row["max_value_mn"]) != "nan":
                parts.append(f"Size  {row['currency']} {float(row['max_value_mn']):,.0f}m")
            if row.get("proration_expected") and int(row["proration_expected"]) == 1:
                parts.append(f"Proration  ~{float(row['estimated_proration_pct']):.0f}%")
            if row.get("premium_to_mkt_pct") and str(row["premium_to_mkt_pct"]) != "nan":
                parts.append(f"Premium  {float(row['premium_to_mkt_pct']):.1f}%")
        elif t in ("scheme_of_arrangement", "merger", "exchange_offer"):
            if row.get("acquirer") and str(row["acquirer"]) != "nan":
                parts.append(f"Buyer  {row['acquirer']}")
            if row.get("consideration_type") and str(row["consideration_type"]) != "nan":
                parts.append(f"Terms  {row['consideration_type']}")
            if row.get("cash_per_share") and str(row["cash_per_share"]) != "nan":
                parts.append(f"Px  {row['currency']} {float(row['cash_per_share']):.2f}/sh")
            if row.get("spread_to_terms_pct") and str(row["spread_to_terms_pct"]) != "nan":
                parts.append(f"Spread  {float(row['spread_to_terms_pct']):.2f}%")
            if row.get("break_risk") and str(row["break_risk"]) != "nan":
                parts.append(f"Break  {row['break_risk']}")
            if row.get("regulatory_status") and str(row["regulatory_status"]) != "nan":
                parts.append(f"Reg  {row['regulatory_status']}")
        elif t in ("stock_split", "consolidation"):
            if row.get("split_ratio") and str(row["split_ratio"]) != "nan":
                parts.append(f"Ratio  {row['split_ratio']}")
        elif t in ("spinoff", "demerger"):
            if row.get("spinoff_name") and str(row["spinoff_name"]) != "nan":
                parts.append(f"NewCo  {row['spinoff_name']}")
            if row.get("spinoff_ticker") and str(row["spinoff_ticker"]) != "nan":
                parts.append(f"Ticker  {row['spinoff_ticker']}")
            if row.get("distribution_ratio") and str(row["distribution_ratio"]) != "nan":
                parts.append(f"Ratio  {row['distribution_ratio']}")

        ddl = fmt_date(row.get("election_deadline"))
        ex  = fmt_date(row.get("ex_date"))
        deadline_str = f"Deadline  {ddl}  ({tl_label})" if ddl != "—" else "No deadline"

        with st.expander(
            f"{tl_dot}  {row['ticker']}  ·  {row['company_name']}  ·  "
            f"{type_label}  ·  {row['country']}  ·  {cat_short}  ·  {deadline_str}",
            expanded=False
        ):
            c1, c2, c3 = st.columns(3)
            with c1:
                st.markdown(f"**Ticker** &nbsp; `{row['ticker']}`")
                st.markdown(f"**Company** &nbsp; {row['company_name']}")
                st.markdown(f"**Country** &nbsp; {row['country']}")
                st.markdown(f"**Currency** &nbsp; {row['currency']}")
                st.markdown(f"**Category** &nbsp; {cat_short}")
                st.markdown(f"**Status** &nbsp; {row['status']}")
            with c2:
                st.markdown(f"**Announced** &nbsp; {fmt_date(row.get('announcement_date'))}")
                st.markdown(f"**Ex-date** &nbsp; {ex}")
                st.markdown(f"**Record date** &nbsp; {fmt_date(row.get('record_date'))}")
                st.markdown(f"**Election deadline** &nbsp; {ddl} &nbsp; {tl_dot}")
                st.markdown(f"**Payment date** &nbsp; {fmt_date(row.get('payment_date'))}")
            with c3:
                for p in parts:
                    bits = p.split("  ", 1)
                    st.markdown(f"**{bits[0]}** &nbsp; {bits[1]}" if len(bits) == 2 else f"**{p}**")
                if alpha:
                    st.success(f"◆  {alpha}")
                if row.get("notes") and str(row["notes"]) != "nan":
                    st.caption(row["notes"])
                if row.get("source_url") and str(row["source_url"]) != "nan":
                    st.markdown(f"[Source →]({row['source_url']})")

# ── sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.markdown("### Filters")
types, categories, countries, statuses = get_filter_options()
sel_status     = st.sidebar.selectbox("Status",     ["All"] + statuses, index=0)
sel_cat        = st.sidebar.selectbox("Category",   ["All"] + categories, index=0)
type_display   = [TYPE_LABELS.get(t, t) for t in types]
type_map       = {TYPE_LABELS.get(t, t): t for t in types}
sel_type_label = st.sidebar.selectbox("Event Type", ["All"] + type_display, index=0)
sel_type       = "All" if sel_type_label == "All" else type_map.get(sel_type_label, sel_type_label)
sel_country    = st.sidebar.selectbox("Country",    ["All"] + countries, index=0)
urgent_only    = st.sidebar.checkbox("Deadlines ≤ 7 days only", value=False)
alpha_only     = st.sidebar.checkbox("Alpha flags only", value=False)
st.sidebar.markdown("---")
st.sidebar.markdown("### Sort")
sort_by = st.sidebar.selectbox("Sort by", [
    "Election deadline (soonest)", "Ex-date (soonest)",
    "Country", "Event type", "Company name",
])

# ── load & filter ─────────────────────────────────────────────────────────────
@st.cache_data(ttl=120)
def load(status, event_type, event_category, country):
    return get_live_events({"status": status, "event_type": event_type,
                            "event_category": event_category, "country": country})

df = load(sel_status, sel_type, sel_cat, sel_country)

if urgent_only:
    df = df[df["days_to_deadline"].notna() & (df["days_to_deadline"] <= 7)]

df["alpha_flag"] = df.apply(alpha_flag, axis=1)
df = df[df["event_type"] != "odd_lot_offer"]
if alpha_only:
    df = df[df["alpha_flag"] != ""]

# sort — passed deadlines always to bottom
if sort_by == "Election deadline (soonest)":
    df_active = df[df["days_to_deadline"].isna() | (df["days_to_deadline"] >= 0)]
    df_passed = df[df["days_to_deadline"].notna() & (df["days_to_deadline"] < 0)]
    df_active = df_active.sort_values("days_to_deadline", ascending=True, na_position="last")
    df_passed = df_passed.sort_values("days_to_deadline", ascending=False)
    df = pd.concat([df_active, df_passed], ignore_index=True)
else:
    sort_cfg = {
        "Ex-date (soonest)": ("days_to_ex", True),
        "Country":           ("country",    True),
        "Event type":        ("event_type", True),
        "Company name":      ("company_name", True),
    }
    scol, sasc = sort_cfg.get(sort_by, ("days_to_deadline", True))
    df = df.sort_values(scol, ascending=sasc, na_position="last")

# split active / passed
df_active = df[df["days_to_deadline"].isna() | (df["days_to_deadline"] >= 0)].copy()
df_passed = df[df["days_to_deadline"].notna() & (df["days_to_deadline"] < 0)].copy()

# ── header metrics ────────────────────────────────────────────────────────────
st.title("◆ Event Pipeline  /  Deadline Manager")

mc1, mc2, mc3, mc4, mc5 = st.columns(5)
mc1.metric("Showing",     len(df))
mc2.metric("Live",        len(df[df["status"] == "LIVE"]))
mc3.metric("Upcoming",    len(df[df["status"] == "UPCOMING"]))
mc4.metric("Urgent ≤7d",  len(df_active[df_active["days_to_deadline"].notna() & (df_active["days_to_deadline"] <= 7)]))
mc5.metric("Alpha Flags", len(df[df["alpha_flag"] != ""]))

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1 — DEADLINE COUNTDOWN
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  Deadline Countdown", expanded=True):
    df_bars = df_active[df_active["days_to_deadline"].notna()].copy().sort_values("days_to_deadline")
    if not df_bars.empty:
        df_bars["days_int"] = df_bars["days_to_deadline"].apply(safe_int)
        df_bars["label"]    = df_bars.apply(
            lambda r: f"{r['ticker']}  |  {r['company_name']}  |  {TYPE_LABELS.get(r['event_type'], r['event_type'])}  |  {r['country']}    ",
            axis=1
        )
        df_bars["colour"] = df_bars["days_int"].apply(
            lambda d: "#ff3355" if d is not None and d <= 3
            else "#f5a623" if d is not None and d <= 7
            else "#d4c200" if d is not None and d <= 14
            else "#00d4aa"
        )
        df_bars["hover"] = df_bars.apply(
            lambda r: (
                f"<b>{r['company_name']}</b><br>"
                f"Type: {TYPE_LABELS.get(r['event_type'], r['event_type'])}<br>"
                f"Deadline: {fmt_date(r['election_deadline'])}<br>"
                f"Days: {safe_int(r['days_to_deadline'])}<br>"
                f"Country: {r['country']}"
            ), axis=1
        )
        fig = go.Figure(go.Bar(
            x=df_bars["days_int"], y=df_bars["label"],
            orientation="h", marker_color=df_bars["colour"], marker_line_width=0,
            customdata=df_bars["hover"], hovertemplate="%{customdata}<extra></extra>",
            text=df_bars["days_int"].apply(lambda d: f"{d}d" if d is not None else ""),
            textposition="outside",
            textfont=dict(family="IBM Plex Mono", size=9, color="#6a8090"),
        ))
        fig.update_layout(
            paper_bgcolor="#04060a", plot_bgcolor="#080c12",
            font=dict(family="IBM Plex Mono", size=10, color="#6a8090"),
            height=max(400, len(df_bars) * 19),
            margin=dict(l=8, r=55, t=8, b=25),
            xaxis=dict(title=None, gridcolor="#0e1825", linecolor="#182436",
                       tickfont=dict(size=9, color="#6a8090"),
                       range=[0, min((df_bars["days_int"].max() or 30) + 8, 155)]),
            yaxis=dict(gridcolor="#0e1825", linecolor="#182436",
                       tickfont=dict(size=9, color="#8aa0b0"), autorange="reversed"),
            bargap=0.18,
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            "<p style='font-family:IBM Plex Mono;font-size:0.58rem;color:#304050;letter-spacing:0.1em'>"
            "RED  ≤3d &nbsp;&nbsp; AMBER  ≤7d &nbsp;&nbsp; YELLOW  ≤14d &nbsp;&nbsp; GREEN  >14d"
            "</p>", unsafe_allow_html=True
        )
    else:
        st.info("No active events with election deadlines.")

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2 — LIVE EVENT FEED (active events, default = Table)
# ═════════════════════════════════════════════════════════════════════════════
with st.expander(f"◆  Live Event Feed  —  {len(df_active)} events", expanded=True):
    view = st.radio("View", ["Table", "Cards"], index=0, horizontal=True, label_visibility="collapsed")

    if view == "Table":
        display_cols = ["ticker", "company_name", "country", "event_type", "event_category",
                        "status", "election_deadline", "days_to_deadline", "ex_date", "alpha_flag"]
        avail = [c for c in display_cols if c in df_active.columns]
        dfd = df_active[avail].copy()
        dfd["event_type"]        = dfd["event_type"].apply(fmt_type)
        dfd["event_category"]    = dfd["event_category"].map(CATEGORY_LABELS)
        dfd["election_deadline"] = dfd["election_deadline"].apply(fmt_date)
        dfd["ex_date"]           = dfd["ex_date"].apply(fmt_date)
        dfd["days_to_deadline"]  = dfd["days_to_deadline"].apply(safe_int)
        dfd.columns = ["Ticker", "Company", "Country", "Type", "Category",
                       "Status", "Deadline", "Days", "Ex-Date", "Alpha"]
        render_table(dfd)
    else:
        render_cards(df_active)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3 — PASSED DEADLINES (collapsed by default)
# ═════════════════════════════════════════════════════════════════════════════
if len(df_passed) > 0:
    with st.expander(f"◆  Passed Deadlines  —  {len(df_passed)} events", expanded=False):
        render_cards(df_passed)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 4 — DISTRIBUTION BY COUNTRY (collapsed by default)
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  Distribution by Country", expanded=False):
    cc = df.groupby("country").size().reset_index(name="events")
    fig2 = px.bar(
        cc.sort_values("events", ascending=True).tail(20),
        x="events", y="country", orientation="h",
        color="events",
        color_continuous_scale=[[0, "#0e1825"], [0.4, "#0a3028"], [1, "#00d4aa"]],
        labels={"events": "Events", "country": ""},
    )
    fig2.update_layout(
        paper_bgcolor="#04060a", plot_bgcolor="#080c12",
        font=dict(family="IBM Plex Mono", size=10, color="#6a8090"),
        coloraxis_showscale=False, height=360,
        margin=dict(l=8, r=20, t=8, b=20),
        xaxis=dict(gridcolor="#0e1825", linecolor="#182436", tickfont=dict(size=9, color="#6a8090")),
        yaxis=dict(gridcolor="#0e1825", linecolor="#182436", tickfont=dict(size=9, color="#8aa0b0")),
    )
    fig2.update_traces(marker_line_width=0)
    st.plotly_chart(fig2, use_container_width=True)
