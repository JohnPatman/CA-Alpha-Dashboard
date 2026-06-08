import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

st.set_page_config(
    page_title="CA Alpha Dashboard",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="expanded"
)

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400;500;600&family=IBM+Plex+Sans:wght@300;400;500;600&display=swap');
:root {
    --bg:#04060a; --bg-card:#080c12; --bg-sidebar:#04060a;
    --accent:#00d4aa; --accent-dim:#00d4aa12;
    --red:#ff3355; --amber:#f5a623; --yellow:#d4c200;
    --border:#0e1825; --border-mid:#182436; --border-bright:#243548;
    --text-primary:#c8d8e8;
    --text-secondary:#6a8090;
    --text-muted:#304050;
    --font-mono:'IBM Plex Mono',monospace;
}
html,body,.stApp,[class*="css"]{background:var(--bg)!important;color:var(--text-primary)!important;}
#MainMenu,footer,header,[data-testid="stToolbar"],[data-testid="stDecoration"],[data-testid="stStatusWidget"]{display:none!important;}
.main .block-container{padding:1rem 2rem 3rem!important;max-width:100%!important;}

/* sidebar */
section[data-testid="stSidebar"]{background:var(--bg-sidebar)!important;border-right:1px solid var(--border-mid)!important;}
section[data-testid="stSidebar"] *{font-family:var(--font-mono)!important;color:var(--text-secondary)!important;}
section[data-testid="stSidebar"] [aria-current="page"] {
    color:var(--accent)!important;
    background:var(--accent-dim)!important;
    border-radius:0!important;
    border:none!important;
}
section[data-testid="stSidebar"] [aria-current="page"] * {
    color:var(--accent)!important;
    background:transparent!important;
}
section[data-testid="stSidebar"] a,
section[data-testid="stSidebar"] li {
    border-radius:0!important;
    border:none!important;
}

/* typography */
h1{font-family:var(--font-mono)!important;font-size:0.82rem!important;font-weight:500!important;color:var(--accent)!important;letter-spacing:0.18em!important;text-transform:uppercase!important;padding:0.5rem 0 0.4rem!important;border-bottom:1px solid var(--border-mid)!important;margin-bottom:0.8rem!important;}
h2{font-family:var(--font-mono)!important;font-size:0.55rem!important;font-weight:600!important;letter-spacing:0.2em!important;text-transform:uppercase!important;color:var(--text-muted)!important;margin-top:1.6rem!important;margin-bottom:0.4rem!important;padding-bottom:0.25rem!important;border-bottom:1px solid var(--border)!important;}
h3{font-family:var(--font-mono)!important;font-size:0.75rem!important;font-weight:500!important;color:var(--accent)!important;letter-spacing:0.06em!important;margin-bottom:0.2rem!important;}
p{color:var(--text-secondary)!important;font-size:0.72rem!important;font-family:var(--font-mono)!important;line-height:1.5!important;}
strong{color:var(--text-primary)!important;font-weight:500!important;}

/* metrics — tighter, no gap below title */
[data-testid="stMetric"]{background:var(--bg-card)!important;border:1px solid var(--border-mid)!important;border-top:1px solid var(--border-bright)!important;border-radius:0!important;padding:0.5rem 0.8rem!important;min-height:5.5rem!important;}
[data-testid="stMetric"] label{font-family:var(--font-mono)!important;font-size:0.52rem!important;letter-spacing:0.16em!important;text-transform:uppercase!important;color:var(--text-muted)!important;}
[data-testid="stMetric"] [data-testid="stMetricValue"]{font-family:var(--font-mono)!important;font-size:1.35rem!important;font-weight:400!important;color:var(--text-primary)!important;line-height:1.1!important;}
[data-testid="stMetricDelta"] svg{display:none!important;}
[data-testid="stMetricDelta"]{font-family:var(--font-mono)!important;font-size:0.58rem!important;color:var(--red)!important;}

/* buttons */
[data-testid="stButton"] button{background:transparent!important;border:1px solid var(--border-bright)!important;border-radius:0!important;color:var(--text-secondary)!important;font-family:var(--font-mono)!important;font-size:0.58rem!important;letter-spacing:0.14em!important;text-transform:uppercase!important;padding:0.25rem 0.65rem!important;}
[data-testid="stButton"] button:hover{border-color:var(--accent)!important;color:var(--accent)!important;background:var(--accent-dim)!important;}
[data-testid="stButton"] button:disabled{opacity:0.2!important;}

hr{border-color:var(--border-mid)!important;margin:0.4rem 0!important;}
::-webkit-scrollbar{width:3px;height:3px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--border-bright);}


/* sidebar width */
section[data-testid="stSidebar"],
section[data-testid="stSidebar"] > div:first-child {
    width:200px!important;min-width:200px!important;max-width:200px!important;
}
/* hide ALL collapse controls */



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






DB = "data/events.db"

# ── HTML table renderer (replaces st.dataframe — avoids white bg) ─────────────
def html_table(df):
    cols = list(df.columns)
    rows_html = ""
    for _, row in df.iterrows():
        cells = ""
        for i, col in enumerate(cols):
            val = row[col]
            align = "right" if isinstance(val, (int, float)) else "left"
            cells += (
                f'<td style="padding:0.28rem 0.6rem;color:#c8d8e8;'
                f'font-size:0.7rem;text-align:{align};'
                f'border-bottom:1px solid #0e1825;">{val}</td>'
            )
        rows_html += f"<tr>{cells}</tr>"

    headers = "".join(
        f'<th style="padding:0.28rem 0.6rem;text-align:left;font-size:0.55rem;'
        f'letter-spacing:0.1em;text-transform:uppercase;color:#304050;'
        f'background:#080c12;border-bottom:1px solid #243548;">{c}</th>'
        for c in cols
    )

    return (
        f'<div style="border:1px solid #182436;overflow:hidden;">'
        f'<table style="width:100%;border-collapse:collapse;'
        f'font-family:IBM Plex Mono,monospace;">'
        f'<thead><tr>{headers}</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        f'</table></div>'
    )

@st.cache_data(ttl=300)
def get_summary():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    total     = c.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    live      = c.execute("SELECT COUNT(*) FROM events WHERE status='LIVE'").fetchone()[0]
    upcoming  = c.execute("SELECT COUNT(*) FROM events WHERE status='UPCOMING'").fetchone()[0]
    vol       = c.execute("SELECT COUNT(*) FROM events WHERE event_category='VOLUNTARY' AND status='LIVE'").fetchone()[0]
    mwc       = c.execute("SELECT COUNT(*) FROM events WHERE event_category='MANDATORY_WITH_CHOICE' AND status='LIVE'").fetchone()[0]
    countries = c.execute("SELECT COUNT(DISTINCT country) FROM events WHERE status IN ('LIVE','UPCOMING')").fetchone()[0]
    today     = date.today().isoformat()
    urgent    = c.execute("""SELECT COUNT(*) FROM events
        WHERE election_deadline IS NOT NULL
        AND election_deadline BETWEEN ? AND date(?,'+7 days')
        AND status='LIVE'""", (today, today)).fetchone()[0]
    conn.close()
    return dict(total=total, live=live, upcoming=upcoming,
                vol=vol, mwc=mwc, countries=countries, urgent=urgent)

@st.cache_data(ttl=300)
def get_type_breakdown():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("""SELECT event_type, COUNT(*) as n
        FROM events WHERE status IN ('LIVE','UPCOMING')
        GROUP BY event_type ORDER BY n DESC""", conn)
    conn.close()
    return df

@st.cache_data(ttl=300)
def get_country_breakdown():
    conn = sqlite3.connect(DB)
    df = pd.read_sql("""SELECT country, COUNT(*) as events
        FROM events WHERE status IN ('LIVE','UPCOMING')
        GROUP BY country ORDER BY events DESC""", conn)
    conn.close()
    return df

# ── page ──────────────────────────────────────────────────────────────────────
st.title("◆ Voluntary CA Alpha Dashboard")

s = get_summary()

def kpi_card(label, value, accent=False, urgent=False):
    border_top = "#ff3355" if urgent else ("#00d4aa" if accent else "#243548")
    val_color  = "#ff3355" if urgent else "#c8d8e8"
    badge      = "<span style='display:inline-block;margin-top:0.35rem;font-size:0.52rem;letter-spacing:0.1em;color:#ff3355;text-transform:uppercase'>urgent</span>" if urgent else ""
    return (
        f"<div style='background:#080c12;border:1px solid #182436;"
        f"border-top:2px solid {border_top};padding:0.55rem 0.8rem;"
        f"font-family:IBM Plex Mono,monospace;height:5.2rem;box-sizing:border-box'>"
        f"<div style='font-size:0.52rem;letter-spacing:0.16em;text-transform:uppercase;"
        f"color:#304050;margin-bottom:0.3rem'>{label}</div>"
        f"<div style='font-size:1.4rem;font-weight:400;color:{val_color};line-height:1.1'>{value}</div>"
        f"{badge}</div>"
    )

kc1,kc2,kc3,kc4,kc5,kc6 = st.columns(6)
kc1.markdown(kpi_card("Live Events",   s["live"]),     unsafe_allow_html=True)
kc2.markdown(kpi_card("Upcoming",      s["upcoming"]), unsafe_allow_html=True)
kc3.markdown(kpi_card("Voluntary",     s["vol"]),      unsafe_allow_html=True)
kc4.markdown(kpi_card("Choice Events", s["mwc"]),      unsafe_allow_html=True)
kc5.markdown(kpi_card("Countries",     s["countries"]),unsafe_allow_html=True)
kc6.markdown(kpi_card("Deadlines ≤7d", s["urgent"],
    urgent=s["urgent"] > 0),                           unsafe_allow_html=True)

st.markdown("## Event Universe")

col_a, col_b = st.columns(2)
with col_a:
    st.markdown(
        "<p style='font-size:0.6rem;letter-spacing:0.12em;text-transform:uppercase;"
        "color:#304050;margin-bottom:0.4rem'>Live events by type</p>",
        unsafe_allow_html=True
    )
    df_type = get_type_breakdown()
    df_type.columns = ["Type", "Count"]
    df_type["Type"] = df_type["Type"].str.replace("_", " ").str.title().str.replace("Fx ", "CCY ")
    st.markdown(html_table(df_type), unsafe_allow_html=True)

with col_b:
    st.markdown(
        "<p style='font-size:0.6rem;letter-spacing:0.12em;text-transform:uppercase;"
        "color:#304050;margin-bottom:0.4rem'>Events by country (live + upcoming)</p>",
        unsafe_allow_html=True
    )
    df_ctry = get_country_breakdown()
    df_ctry.columns = ["Country", "Events"]
    # Wrap in fixed-height scrollable div matching the type table height
    table_html = html_table(df_ctry)
    scrollable = (
        f"<div style='max-height:380px;overflow-y:auto;"
        f"scrollbar-width:thin;scrollbar-color:#243548 #04060a'>"
        f"{table_html}</div>"
    )
    st.markdown(scrollable, unsafe_allow_html=True)

st.markdown("## Modules")

m1,m2,m3 = st.columns(3)
with m1:
    st.markdown("**◆ Event Pipeline**")
    st.markdown("Live event tracker with deadline countdown, traffic light status, and alpha flags.")
    if st.button("Open Event Pipeline →", key="m1"):
        st.switch_page("pages/1_Event_Pipeline.py")
with m2:
    st.markdown("**◆ Scrip Arbitrage**")
    st.markdown("Multi-name scrip dividend engine — cash vs scrip economics, lender conflict analysis.")
    if st.button("Open Scrip Arbitrage →", key="m2"):
        st.switch_page("pages/2_Scrip_Arbitrage.py")
with m3:
    st.markdown("**◆ CCY Election Optimiser**")
    st.markdown("Currency election analysis — company FX vs market FX, arbitrage detection.")
    if st.button("Open CCY Optimiser →", key="m3"):
        st.switch_page("pages/3_CCY_Election.py")

m4,m5,m6 = st.columns(3)
with m4:
    st.markdown("**◆ Rights Issue Analyser**")
    st.markdown("TERP calculator, nil-paid value, take-up vs sell economics.")
    if st.button("Open Rights Analyser →", key="m4"):
        st.switch_page("pages/4_Rights_Issue.py")
with m5:
    st.markdown("**◆ Tender Tracker**")
    st.markdown("Proration modelling, dutch auction range analysis, spread to terms.")
    if st.button("Open Tender Tracker →", key="m5"):
        st.switch_page("pages/5_Tender_Tracker.py")
with m6:
    st.markdown("**◆ Merger & Scheme Tracker**")
    st.markdown("Spread to terms, break risk, consideration election optimiser.")
    if st.button("Open Merger Tracker →", key="m6"):
        st.switch_page("pages/6_Merger_Tracker.py")

st.markdown("---")
st.markdown(
    f"<p style='font-family:IBM Plex Mono,monospace;font-size:0.58rem;"
    f"color:#304050;letter-spacing:0.08em'>"
    f"UNIVERSE  1,207 companies · 36 countries · {s['total']} events · "
    f"AS AT  {date.today().isoformat()}</p>",
    unsafe_allow_html=True
)
st.markdown(
    "<div style='font-family:IBM Plex Mono,monospace;font-size:0.58rem;"
    "color:#6a8090;line-height:1.9;margin-top:0.8rem;"
    "border-top:1px solid #0e1825;padding-top:0.7rem'>"

    # — About block —
    "<span style='color:#304050;font-size:0.52rem;letter-spacing:0.16em;"
    "text-transform:uppercase'>About this project</span><br>"
    "A personal portfolio project built to demonstrate corporate actions analytics methodology "
    "across six event categories: scrip dividend arbitrage, currency election optimisation, "
    "rights issue valuation, tender offer spread analysis, and merger &amp; scheme arbitrage. "
    "Analytical frameworks — TERP from first principles, implied deal probability, CCY arb "
    "detection, annualised return modelling, and lender recall logic — reflect genuine market "
    "methodology applied to a synthetic dataset. "
    "Built in Python using Streamlit, SQLite, Pandas, and Plotly. "
    "<a href='https://github.com/JohnPatman/CA-Alpha-Dashboard' "
    "style='color:#304050;text-decoration:underline' target='_blank'>Source on GitHub ↗</a>"

    "<br><br>"

    # — Data block —
    "<span style='color:#304050;font-size:0.52rem;letter-spacing:0.16em;"
    "text-transform:uppercase'>Data</span><br>"
    "All companies, tickers, event terms, prices, ratios, spreads, FX rates, and deadlines are "
    "<strong style='color:#c8d8e8'>entirely synthetic</strong> and generated solely for "
    "illustrative purposes. They do not represent real corporate actions or real securities. "
    "Nothing on this dashboard constitutes investment advice or should be relied upon for any "
    "financial, legal, or investment decision."

    "<br><br>"

    # — Affiliation block —
    "<span style='color:#304050;font-size:0.52rem;letter-spacing:0.16em;"
    "text-transform:uppercase'>Affiliation</span><br>"
    "This project is independent and has no affiliation with JPMorgan Chase, Nomura, or any "
    "other financial institution. All views and methodologies are the author's own and do not "
    "represent the views of any current or former employer."

    "</div>",
    unsafe_allow_html=True
)
