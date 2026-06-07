import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import sqlite3, re
from datetime import date
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

st.set_page_config(page_title="Rights Issue Analyser · CA Alpha", page_icon="◆", layout="wide", initial_sidebar_state="expanded")

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

def parse_ratio(s):
    if not s or str(s)=='nan': return None, None
    m = re.search(r'(\d+)\s+for\s+(\d+)', str(s), re.I)
    return (int(m.group(1)), int(m.group(2))) if m else (None, None)

def disc_colour(v):
    if v is None: return '#6a8090'
    if v < -25: return '#ff3355'
    if v < -15: return '#f5a623'
    return '#d4c200'

SORT_JS = """
<script>
function sortTable(th) {
    var table = th.closest('table');
    var tbody = table.querySelector('tbody');
    var rows  = Array.from(tbody.querySelectorAll('tr'));
    var idx   = Array.from(th.parentElement.children).indexOf(th);
    var asc   = th.dataset.sort !== 'asc';
    rows.sort(function(a, b) {
        var av = a.cells[idx] ? a.cells[idx].textContent.trim() : '';
        var bv = b.cells[idx] ? b.cells[idx].textContent.trim() : '';
        var an = parseFloat(av.replace(/[^-\\d.]/g,''));
        var bn = parseFloat(bv.replace(/[^-\\d.]/g,''));
        if (!isNaN(an) && !isNaN(bn)) return asc ? an-bn : bn-an;
        return asc ? av.localeCompare(bv) : bv.localeCompare(av);
    });
    th.parentElement.querySelectorAll('th').forEach(function(t){
        t.dataset.sort=''; var s=t.querySelector('span.sort-ind'); if(s) s.textContent='';
    });
    th.dataset.sort = asc ? 'asc' : 'desc';
    var ind=th.querySelector('span.sort-ind');
    if(ind) ind.textContent = asc ? ' \u25b2' : ' \u25bc';
    rows.forEach(function(r){ tbody.appendChild(r); });
}
</script>"""

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
        AND (e.election_deadline IS NULL OR e.election_deadline >= date('now'))
        ORDER BY r.discount_to_terp_pct ASC
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
disc_pct = sf(ev["discount_to_terp_pct"])
proceeds = sf(ev["gross_proceeds_mn"])
uw       = ev["fully_underwritten"]
ddl_days = days_to(ev["election_deadline"])
dot      = tdot(ddl_days)
rn, rd   = parse_ratio(ev["rights_ratio"]); rn = rn or 1; rd = rd or 1

# Calculate TERP from first principles
terp_calc = (rd*cur_px + rn*sub_px) / (rd+rn) if cur_px and sub_px else db_terp
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
k4.metric("Nil-Paid Value", f"{ev['currency']} {nil_calc:.2f}" if nil_calc else "—",
          delta="Tradeable" if nil_calc and nil_calc>0 else None, delta_color="normal")
k5.metric("Disc to TERP",   f"{disc_calc:+.1f}%" if disc_calc is not None else "—",
          delta_color="inverse")
k6.metric("Proceeds",       f"{ev['currency']} {proceeds:,.0f}m" if proceeds else "—")

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 1 — SCANNER
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  Rights Issue Scanner — All Live Events", expanded=True):
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
            f"{r['currency']} {np_:.2f}" if np_ else "—",
            f"{r['currency']} {proc:,.0f}m" if proc else "—",
            "✓" if r["fully_underwritten"]==1 else "—",
        ]
        scan_rows.append(row)
        scan_hl[i] = {9:disc_colour(disc), 10:'#00d4aa' if np_>0 else '#304050'}

    dark_table(scan_rows,
               ["Ticker","Company","Country","Type","Ratio","Deadline","Days","Sub Px","TERP","Disc%","Nil-Paid","Proceeds","UW"],
               scan_hl)

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 2 — TERP & POSITION ANALYSIS
# ═════════════════════════════════════════════════════════════════════════════
with st.expander(f"◆  TERP & Economics — {ev['ticker']} / {ev['company_name']}", expanded=True):
    if sub_px and cur_px:
        col_l, col_r = st.columns(2)
        with col_l:
            st.markdown("<p style='font-size:0.58rem;letter-spacing:0.12em;text-transform:uppercase;color:#304050;margin-bottom:0.4rem'>TERP calculation</p>", unsafe_allow_html=True)
            econ_rows = [
                ("Rights ratio",          str(ev["rights_ratio"]),                           f"{rn} new per {rd} existing"),
                ("Current price",         f"{ev['currency']} {cur_px:.2f}",                 "Pre-rights cum price"),
                ("Subscription price",    f"{ev['currency']} {sub_px:.2f}",                 "Price to take up rights"),
                ("TERP (calculated)",     f"{ev['currency']} {terp_calc:.2f}",               f"({rd}×{cur_px:.2f} + {rn}×{sub_px:.2f}) / {rd+rn}"),
                ("Nil-paid value",        f"{ev['currency']} {nil_calc:.2f}",               "TERP − sub price  (market value of right)"),
                ("Discount of sub to TERP",f"{disc_calc:+.1f}%",                             "How deep the issue is priced"),
                ("Current vs TERP",       f"{prem_terp:+.1f}%" if prem_terp else "—",       "Current price premium above TERP"),
                ("Underwriter",           str(ev["underwriter"]) if ev["underwriter"] and str(ev["underwriter"])!='nan' else "—", ""),
                ("Fully underwritten",    "Yes" if uw==1 else "No",                          "Protects against deal failure"),
                ("Gross proceeds",        f"{ev['currency']} {proceeds:,.0f}m" if proceeds else "—", ""),
                ("Nil-paid ticker",       str(ev["nil_paid_ticker"]) if ev["nil_paid_ticker"] and str(ev["nil_paid_ticker"])!='nan' else "Check prospectus", "Trade rights in market"),
            ]
            hl = {4:{1:'#00d4aa',2:'#00d4aa'},
                  5:{1:disc_colour(disc_calc)},
                  8:{1:'#00d4aa' if uw==1 else '#6a8090'}}
            dark_table(econ_rows, ["Parameter","Value","Note"], hl, height=430)

        with col_r:
            st.markdown("<p style='font-size:0.58rem;letter-spacing:0.12em;text-transform:uppercase;color:#304050;margin-bottom:0.4rem'>Position analysis — {:,.0f} shares</p>".format(pos_shares), unsafe_allow_html=True)
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
                    ("Nil-paid value",      f"{ev['currency']} {nil_tot:,.2f}",           f"@ {ev['currency']} {nil_calc:.2f}/right"),
                    ("Post-TERP (take up)", f"{ev['currency']} {post_take:,.2f}",         f"{pos_shares+new_ent:,} sh × {terp_calc:.2f}"),
                    ("Post-TERP (lapse)",   f"{ev['currency']} {post_lapse:,.2f}",        f"{pos_shares:,} sh × {terp_calc:.2f}"),
                    ("Max dilution",        f"{dilution:.1f}%",                            "If you lapse, others take up"),
                ]
                hl2 = {2:{1:'#f5a623'}, 3:{1:'#00d4aa',2:'#00d4aa'}, 6:{1:'#ff3355'}}
                dark_table(pnl_rows, ["Metric","Value","Detail"], hl2, height=275)

                if nil_calc > 0 and cur_px > sub_px:
                    st.success(f"◆  Take up rights — sub {ev['currency']} {sub_px:.2f} < TERP {terp_calc:.2f}. Nil-paid value: {ev['currency']} {nil_tot:,.2f}")
                else:
                    st.warning("⚠  Sub price near or above TERP — consider selling nil-paid rights")

# ═════════════════════════════════════════════════════════════════════════════
# SECTION 3 — TAKE-UP vs SELL CHART
# ═════════════════════════════════════════════════════════════════════════════
with st.expander("◆  Take-up vs Sell Rights — P&L at Different Share Prices", expanded=True):
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
        st.markdown(
            f"<p style='font-family:IBM Plex Mono;font-size:0.66rem;color:#6a8090'>"
            f"Break-even (take-up): <span style='color:#c8d8e8'>{ev['currency']} {sub_px:.2f}</span>"
            f" &nbsp;·&nbsp; Nil-paid value today: <span style='color:#00d4aa'>{ev['currency']} {nil_calc:.2f}/right</span>"
            f" &nbsp;·&nbsp; "
            f"<span style='color:#00d4aa'>Take up rights — positive P&L at current price</span>"
            if cur_px > sub_px else
            f"Break-even: <span style='color:#c8d8e8'>{ev['currency']} {sub_px:.2f}</span>"
            f" &nbsp;·&nbsp; <span style='color:#f5a623'>Consider selling nil-paid rights in market</span>"
            ,
            unsafe_allow_html=True
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
        st.markdown(f"""<div style='font-family:IBM Plex Mono;font-size:0.7rem;color:#6a8090;line-height:1.9'>
<span style='color:#c8d8e8;font-size:0.62rem;letter-spacing:0.1em;text-transform:uppercase'>Timeline</span><br><br>
Ex-date: <span style='color:#c8d8e8'>{fmt_date(ev["ex_date"])}</span><br>
Nil-paid trading opens: ex-date<br>
Subscription deadline: <span style='color:#c8d8e8'>{fmt_date(ev["election_deadline"])}</span> ({ddl_days}d)<br>
Payment/settlement: <span style='color:#c8d8e8'>{fmt_date(ev["payment_date"])}</span><br><br>
Nil-paid ticker: <span style='color:#c8d8e8'>{str(ev["nil_paid_ticker"]) if ev["nil_paid_ticker"] and str(ev["nil_paid_ticker"])!='nan' else "Check prospectus"}</span><br>
Current nil-paid value: <span style='color:#00d4aa'>{ev["currency"]} {nil_calc:.2f}</span>
</div>""", unsafe_allow_html=True)

    with col_b:
        st.markdown(f"""<div style='font-family:IBM Plex Mono;font-size:0.7rem;color:#6a8090;line-height:1.9'>
<span style='color:#c8d8e8;font-size:0.62rem;letter-spacing:0.1em;text-transform:uppercase'>Lender Considerations</span><br><br>
Shares on loan over ex-date: borrower receives nil-paid rights.
Lender receives <strong style='color:#f5a623'>manufactured nil-paid rights</strong> from borrower.<br><br>
Lender must instruct borrower on election before deadline.
If stock not recalled, election instruction must go via borrower — coordination critical.<br><br>
Recall if nil-paid value ({ev["currency"]} {nil_calc:.2f}/right × {int(pos_shares*rn/rd):,} rights = <span style='color:#00d4aa'>{ev["currency"]} {int(pos_shares*rn/rd)*nil_calc:,.0f}</span>) exceeds lending income.
</div>""", unsafe_allow_html=True)

    if ddl_days is not None and 0 <= ddl_days <= 5:
        st.markdown(f"<div style='border-left:2px solid #ff3355;background:#ff335508;padding:0.3rem 0.7rem;font-family:IBM Plex Mono;font-size:0.66rem;color:#ff3355;margin-top:0.3rem'>🔴  Subscription deadline {ddl_days}d — nil-paid rights trading closing imminently.</div>", unsafe_allow_html=True)
