"""
utils/ui.py
-----------
Shared Streamlit UI components for the CA Alpha Dashboard.

Usage in any page module:
    from utils.ui import apply_theme, dark_table

    st.set_page_config(...)
    apply_theme()          # injects dark CSS + kills sidebar collapse button
"""
import streamlit as st
import streamlit.components.v1 as _c


# ── Shared dark terminal theme ───────────────────────────────────────────────
# Consumed by every page via apply_theme() EXCEPT Home.py and pages/1_Event_Pipeline.py,
# which keep their own standalone CSS. If you change a rule here that those two pages also
# use, mirror it into their inline CSS blocks too, or the change will not appear there.

_MODULE_CSS = """<style>
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
[data-testid="stColumn"]:has([data-testid="stMetric"]){display:flex!important;flex-direction:column!important;}
[data-testid="stColumn"]:has([data-testid="stMetric"]) > [data-testid="stVerticalBlock"]{flex:1 1 auto!important;}
[data-testid="stColumn"]:has([data-testid="stMetric"]) [data-testid="stElementContainer"]:has([data-testid="stMetric"]){flex:1 1 auto!important;}
[data-testid="stMetric"]{background:var(--bg-card)!important;border:1px solid var(--border-mid)!important;border-top:1px solid var(--border-bright)!important;border-radius:0!important;padding:0.5rem 0.8rem!important;min-height:4.4rem!important;height:100%!important;display:flex!important;flex-direction:column!important;justify-content:flex-start!important;}
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

_SIDEBAR_JS = """<script>
(function(){
    function kill(){
        try{
            var d=window.parent.document;
            ['stSidebarCollapseButton','collapsedControl'].forEach(function(id){
                d.querySelectorAll('[data-testid="'+id+'"]').forEach(function(el){
                    el.style.cssText='display:none!important';
                });
            });
        }catch(e){}
    }
    kill();
    [100,500,1500].forEach(function(t){setTimeout(kill,t);});
    try{
        new MutationObserver(kill).observe(
            window.parent.document.body,{childList:true,subtree:true}
        );
    }catch(e){}
})();
</script>"""


def apply_theme():
    """
    Inject the shared dark terminal CSS and sidebar collapse-button fix.
    Call once near the top of each page module, after st.set_page_config().
    """
    st.markdown(_MODULE_CSS, unsafe_allow_html=True)
    _c.html(_SIDEBAR_JS, height=1)


# ── Sortable dark table ──────────────────────────────────────────────────────

def dark_table(rows, headers, highlights=None, height=None):
    """
    Render a list of rows as a dark, sortable HTML table inside a Streamlit iframe.

    Parameters
    ----------
    rows       : list of tuples/lists — one per table row
    headers    : list of str — column headers
    highlights : dict {row_index: {col_index: hex_colour}} for cell colouring
    height     : int — iframe height in px (auto-calculated if None)

    Sorting
    -------
    Click any column header to sort ascending (▲); click again for descending (▼).
    Numeric columns sort by value; text columns sort alphabetically.
    """
    th = ''.join(
        f'<th style="padding:0.3rem 0.7rem;font-size:0.52rem;'
        f'letter-spacing:0.1em;text-transform:uppercase;color:#304050;'
        f'background:#04060a;border-bottom:1px solid #243548;'
        f'position:sticky;top:0;z-index:2;'
        f'text-align:left;white-space:nowrap;cursor:pointer;user-select:none">'
        f'{h}<span class="si" style="color:#00d4aa;font-size:0.5rem"></span></th>'
        for h in headers
    )
    tbody = ''
    for i, row in enumerate(rows):
        bg = '#080c12' if i % 2 == 0 else '#04060a'
        hl = (highlights or {}).get(i, {})
        cells = ''.join(
            f'<td style="padding:0.28rem 0.7rem;color:{hl.get(j, "#c8d8e8")};'
            f'font-size:0.7rem;background:{bg};border-bottom:1px solid #0e1825;'
            f'white-space:nowrap">{str(v) if v is not None else "—"}</td>'
            for j, v in enumerate(row)
        )
        tbody += f'<tr>{cells}</tr>'

    h_px = height or min(len(rows) * 32 + 52, 560)

    html = (
        '<!DOCTYPE html><html><head>'
        '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono'
        ':wght@400;500&display=swap" rel="stylesheet">'
        '<style>'
        '*{box-sizing:border-box;margin:0;padding:0;}'
        'html,body{background:#04060a;font-family:"IBM Plex Mono",monospace;}'
        'table{width:100%;border-collapse:collapse;}'
        'tr:hover td{background:#0e1825!important;}'
        'thead th:hover{color:#6a8090!important;}'
        '</style>'
        '<script>'
        'function sT(th){'
        'var tb=th.closest("table").querySelector("tbody");'
        'var rs=Array.from(tb.querySelectorAll("tr"));'
        'var idx=Array.from(th.parentElement.children).indexOf(th);'
        'var asc=th.dataset.s!=="a";'
        'rs.sort(function(a,b){'
        'var av=a.cells[idx]?a.cells[idx].textContent.trim():"";'
        'var bv=b.cells[idx]?b.cells[idx].textContent.trim():"";'
        'var an=parseFloat(av.replace(/[^-\\d.]/g,""));'
        'var bn=parseFloat(bv.replace(/[^-\\d.]/g,""));'
        'if(!isNaN(an)&&!isNaN(bn))return asc?an-bn:bn-an;'
        'return asc?av.localeCompare(bv):bv.localeCompare(av);});'
        'th.parentElement.querySelectorAll("th").forEach(function(t){'
        't.dataset.s="";var s=t.querySelector(".si");if(s)s.textContent="";});'
        'th.dataset.s=asc?"a":"d";'
        'var ind=th.querySelector(".si");'
        'if(ind)ind.textContent=asc?" \u25b2":" \u25bc";'
        'rs.forEach(function(r){tb.appendChild(r);});}'
        '</script>'
        '</head><body>'
        f'<table><thead><tr>{th}</tr></thead><tbody>{tbody}</tbody></table>'
        '<script>'
        'Array.from(document.querySelectorAll("thead th")).forEach('
        'function(th){th.onclick=function(){sT(th);};});'
        '</script>'
        '</body></html>'
    )
    _c.html(html, height=h_px, scrolling=True)


def render_top_nav():
    items = [
        ("Home", "/"), ("Pipeline", "/Event_Pipeline"), ("Briefing", "/Priority_Briefing"),
        ("Scrip", "/Scrip_Arbitrage"), ("CCY", "/CCY_Election"), ("Rights", "/Rights_Issue"),
        ("Tender", "/Tender_Tracker"), ("Merger", "/Merger_Tracker"), ("ADR", "/ADR_Pricing"),
        ("Closed", "/Closed_Events"),
    ]
    links = "".join(f"<a href='{u}' target='_self' class='canav'>{n}</a>" for n, u in items)
    st.markdown(
        "<style>.canavwrap{display:flex;flex-wrap:wrap;align-items:center;gap:0.3rem;"
        "margin-bottom:0.6rem;padding-bottom:0.45rem;border-bottom:1px solid #182436}"
        ".canav{background:#080c12;border:1px solid #182436;color:#c8d8e8;"
        "padding:0.25rem 0.6rem;font-family:IBM Plex Mono;font-size:0.72rem;"
        "text-decoration:none;white-space:nowrap}"
        ".canav:hover{border-color:#00d4aa;color:#00d4aa}</style>"
        f"<div class='canavwrap'>{links}</div>",
        unsafe_allow_html=True,
    )
