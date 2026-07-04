"""
add_past_urgent_events.py
-------------------------
Patches data/events.db to add:
  - 20 LIVE events with passed election deadlines  (Passed Deadlines section)
  - 10 LIVE events with 1-6 day deadlines          (Deadlines ≤7d KPI, urgent dots)
  - Fixes ARCLK.IS merger data (HIGH risk + high implied prob contradiction)
  - Adds odd_lot_threshold to CTEC.L tender

Auto-detects the current DB's effective reference date from a known event
(E007 NG.L, original deadline d(2) from 2026-05-25 = 2026-05-27), so dates
are always correct relative to the DB state regardless of how many rebase
cycles have run.

Run from project root:  python3 add_past_urgent_events.py
"""
import sqlite3
from datetime import date, timedelta

# ── Auto-detect DB effective reference date ───────────────────────────────────
_conn_probe = sqlite3.connect("data/events.db")
_row = _conn_probe.execute(
    "SELECT election_deadline FROM events WHERE event_id='E007'"
).fetchone()
_conn_probe.close()

if _row and _row[0]:
    # E007 (NG.L) was created as d(2) from ref 2026-05-25 → original = 2026-05-27
    _ORIGINAL_E007 = date(2026, 5, 27)
    _current_E007  = date.fromisoformat(_row[0])
    _shift = (_current_E007 - _ORIGINAL_E007).days
    EFFECTIVE_REF  = date(2026, 5, 25) + timedelta(days=_shift)
else:
    EFFECTIVE_REF = date.today()

print(f"Effective DB reference date: {EFFECTIVE_REF}  (today = {date.today()})")

def d(n):  return (EFFECTIVE_REF + timedelta(days=n)).isoformat()
def dp(n): return (EFFECTIVE_REF - timedelta(days=n)).isoformat()

conn = sqlite3.connect("data/events.db")
c    = conn.cursor()

# ─────────────────────────────────────────────────────────────────────────────
# 1. FIX ARCLK.IS — HIGH break risk + 90% implied prob is contradictory
#    New: terms=42.5, current=38.5 → spread=10.4% → p=|15|/(10.4+15)=59%
#    Consistent: HIGH break risk, ~59% implied probability
# ─────────────────────────────────────────────────────────────────────────────
c.execute("""UPDATE merger_details SET current_price=38.5, spread_to_terms_pct=10.4
    WHERE event_id='E102'""")

# ─────────────────────────────────────────────────────────────────────────────
# 2. ADD ODD LOT THRESHOLD TO CTEC.L (E027)
#    ≤100 shares guaranteed fill at tender price — no proration risk
# ─────────────────────────────────────────────────────────────────────────────
c.execute("""UPDATE tender_details SET odd_lot_threshold=100, odd_lot_guaranteed=1
    WHERE event_id='E027'""")

# ─────────────────────────────────────────────────────────────────────────────
# 3. PAST EVENTS (deadline already passed — election closed, payment pending)
#    status=LIVE, election_deadline < EFFECTIVE_REF (effective "today" in DB)
# ─────────────────────────────────────────────────────────────────────────────
PAST_EVENTS = [
    # Past scrip dividends (8)
    ("P001","BLND.L","British Land Co","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(35),dp(18),dp(17),dp(3), d(15),d(16), "https://britishland.com","Q1 2026 scrip — election closed, payment pending"),
    ("P002","SGRO.L","SEGRO PLC","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(30),dp(14),dp(13),dp(7), d(12),d(13), "https://segro.com","H1 2026 DRP — election closed"),
    ("P003","PSN.L","Persimmon PLC","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(28),dp(12),dp(11),dp(5), d(14),d(15), "https://persimmonhomes.com","Final 2025 scrip — closed"),
    ("P004","ALV.DE","Allianz SE","Germany","EUR","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(32),dp(16),dp(15),dp(2), d(18),d(19), "https://allianz.com","2026 AGM scrip — election closed"),
    ("P005","AXA.PA","AXA SA","France","EUR","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(38),dp(22),dp(21),dp(8), d(11),d(12), "https://axa.com","2026 dividend option — closed"),
    ("P006","SAN.ES","Banco Santander SA","Spain","EUR","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(42),dp(26),dp(25),dp(12),d(8), d(9),  "https://santander.com","Accion Santander Q1 — closed"),
    ("P007","NOVN.SW","Novartis AG","Switzerland","CHF","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(45),dp(29),dp(28),dp(15),d(5), d(6),  "https://novartis.com","2026 AGM DRP — closed"),
    ("P008","BMW.DE","BMW AG","Germany","EUR","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(50),dp(34),dp(33),dp(20),d(1), d(2),  "https://bmwgroup.com","2026 AGM dividend option — closed"),
    # Past CCY elections (2) — rate fixed pre-deadline, now closed
    ("P010","RIO.AX","Rio Tinto Ltd","Australia","AUD","fx_election","MANDATORY_WITH_CHOICE","LIVE",
     dp(28),dp(12),dp(11),dp(9), d(11),d(12), "https://riotinto.com","USD/AUD/GBP — election closed"),
    ("P011","BHP.JO","BHP Group JSE","South Africa","ZAR","fx_election","MANDATORY_WITH_CHOICE","LIVE",
     dp(35),dp(19),dp(18),dp(6), d(14),d(15), "https://bhp.com","USD/ZAR/GBP — election closed"),
    # Past rights issues (4)
    ("P012","BARC.L","Barclays PLC","UK","GBX","rights_issue","VOLUNTARY","LIVE",
     dp(32),dp(14),dp(13),dp(3), d(16),d(20), "https://barclays.com","1 for 6 at 185p — subscription closed"),
    ("P013","UCG.MI","UniCredit SpA","Italy","EUR","rights_issue","VOLUNTARY","LIVE",
     dp(38),dp(20),dp(19),dp(8), d(12),d(17), "https://unicreditgroup.eu","1 for 8 at EUR 3.20 — closed"),
    ("P014","PKO.WA","PKO Bank Polski","Poland","PLN","rights_issue","VOLUNTARY","LIVE",
     dp(42),dp(24),dp(23),dp(14),d(6), d(11), "https://pkobp.pl","1 for 6 at PLN 32 — closed"),
    ("P015","FSR.JO","FirstRand Ltd","South Africa","ZAR","rights_issue","VOLUNTARY","LIVE",
     dp(50),dp(32),dp(31),dp(22),dp(2),d(4),  "https://firstrand.co.za","1 for 8 at ZAR 180 — closed"),
    # Past tenders (3)
    ("P016","RTO.L","Rentokil Initial PLC","UK","GBX","tender_offer","VOLUNTARY","LIVE",
     dp(30),None,dp(18),dp(2), None, d(5),    "https://rentokininitial.com","600m tender — settled"),
    ("P017","7203.T","Toyota Motor Corp","Japan","JPY","tender_offer","VOLUNTARY","LIVE",
     dp(35),None,dp(22),dp(6), None, d(4),    "https://toyota.co.jp","JPY 500bn tender — settling"),
    ("P018","JPM","JPMorgan Chase","US","USD","tender_offer","VOLUNTARY","LIVE",
     dp(32),None,dp(20),dp(10),None, d(2),    "https://jpmorganchase.com","$30bn tender — election closed"),
    # Past schemes (2)
    ("P019","PSON.L","Pearson PLC","UK","GBX","scheme_of_arrangement","VOLUNTARY","LIVE",
     dp(65),None,dp(28),dp(3), d(20),d(25),   "https://pearson.com","Apollo acquisition — election closed, court pending"),
    ("P020","SDR.L","Schroders PLC","UK","GBX","scheme_of_arrangement","VOLUNTARY","LIVE",
     dp(70),None,dp(35),dp(9), d(14),d(18),   "https://schroders.com","BlackRock acquisition — election closed"),
]

c.executemany("""INSERT OR IGNORE INTO events(
    event_id,ticker,company_name,country,currency,event_type,event_category,
    status,announcement_date,ex_date,record_date,election_deadline,
    payment_date,settlement_date,source_url,notes)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", PAST_EVENTS)

PAST_SCRIP = [
    ("P001", 8.6,  "GBX", 620.0, "1 per 72",  "GBP", None,None,None,"CASH",0,   -1.1, "SCRIP",0),
    ("P002", 6.5,  "GBX", 740.0, "1 per 114", "GBP", None,None,None,"CASH",0,   -0.8, "SCRIP",0),
    ("P003", 60.0, "GBX",1060.0, "1 per 18",  "GBP", None,None,None,"CASH",0,   -1.5, "CASH", 0),
    ("P004", 14.4, "EUR", 210.0, "1 per 14",  "EUR", None,None,None,"CASH",26.375,-1.2,"SCRIP",0),
    ("P005", 1.90, "EUR",  28.5, "1 per 15",  "EUR", None,None,None,"CASH",30.0, -0.9, "SCRIP",0),
    ("P006", 0.10, "EUR",   4.2, "1 per 42",  "EUR", None,None,None,"CASH",19.0, -1.1, "SCRIP",0),
    ("P007", 3.90, "CHF", 820.0, "1 per 210", "CHF", None,None,None,"CASH",35.0, -0.7, "SCRIP",0),
    ("P008", 6.00, "EUR",  82.5, "1 per 14",  "EUR", None,None,None,"CASH",26.375,-1.4,"CASH", 0),
    ("P010", 1.55, "USD", None, None, "USD|AUD|GBP", 0.6480,0.6430,0.78,"CASH",0,None,"AUD",1),
    ("P011", 0.72, "USD", None, None, "USD|ZAR|GBP", 0.6510,0.6430,1.24,"CASH",0,None,"GBP",1),
]
c.executemany(
    "INSERT OR IGNORE INTO scrip_details VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
    PAST_SCRIP
)
for eid in ('P010','P011'):
    c.execute("UPDATE scrip_details SET rate_pre_deadline=1 WHERE event_id=?", (eid,))

PAST_RIGHTS = [
    ("P012","RIGHTS_ISSUE","1 for 6",  185.0, 238.0,229.5, 44.5, "BARC-N.L",-19.4,"Goldman Sachs",1200.0,1),
    ("P013","RIGHTS_ISSUE","1 for 8",  3.20,  5.60, 5.378, 2.178,"UCG-N.MI", -40.5,"Mediobanca",  3500.0,1),
    ("P014","RIGHTS_ISSUE","1 for 6",  32.0,  56.0, 52.0,  20.0, "PKO-N.WA", -38.5,"PKO TFI",     3200.0,1),
    ("P015","RIGHTS_ISSUE","1 for 8",  180.0,250.0,241.25,61.25, "FSR-N.JO", -25.4,"Standard Bank",5000.0,1),
]
c.executemany(
    "INSERT OR IGNORE INTO rights_details(event_id,rights_type,rights_ratio,subscription_price,"
    "current_price,terp,nil_paid_value,nil_paid_ticker,discount_to_terp_pct,underwriter,"
    "gross_proceeds_mn,fully_underwritten) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
    PAST_RIGHTS
)

PAST_TENDERS = [
    ("P016","FIXED",620.0, None,None,618.0, 0.32,None, 600.0,  0,None,None,0),
    ("P017","FIXED",3400.0,None,None,3395.0,0.15,None,500000.0,0,None,None,0),
    ("P018","FIXED",245.0, None,None,244.2, 0.33,None, 30000.0,0,None,None,0),
]
c.executemany("INSERT OR IGNORE INTO tender_details VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", PAST_TENDERS)

PAST_MERGERS = [
    ("P019","SCHEME","Apollo Global",  "APO","CASH",1050.0,None,1048.5,0.14,dp(3),d(60), "CLEARED","LOW"),
    ("P020","SCHEME","BlackRock Inc",  "BLK","MIXED",2850.0,"0.08 BLK per SDR",2845.0,0.18,dp(9),d(45),"CLEARED","LOW"),
]
c.executemany("INSERT OR IGNORE INTO merger_details VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", PAST_MERGERS)

# ─────────────────────────────────────────────────────────────────────────────
# 4. URGENT EVENTS (deadlines 1-6 days from EFFECTIVE_REF = DB "today")
#    These trigger the ≤7d KPI, red/amber traffic-light dots, and
#    appear in the module scanners' urgent counts.
# ─────────────────────────────────────────────────────────────────────────────
URGENT_EVENTS = [
    # Urgent scrip dividends (4)
    ("U001","GLEN.L","Glencore PLC","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(28),dp(12),dp(11),d(1),d(16),d(17),"https://glencore.com","2026 scrip — 1 DAY REMAINING"),
    ("U002","IMB.L","Imperial Brands PLC","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(25),dp(9), dp(8), d(3),d(18),d(19),"https://imperialbrandsplc.com","H1 2026 scrip — 3 days"),
    ("U003","LAND.L","Land Securities Group","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(22),dp(7), dp(6), d(5),d(20),d(21),"https://landsec.com","Final 2026 DRP — 5 days"),
    ("U004","SMDS.L","DS Smith PLC","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(20),dp(5), dp(4), d(6),d(22),d(23),"https://dssmith.com","2026 scrip — 6 days"),
    # Urgent CCY elections (2) — rate pre-deadline, genuine arb closing
    ("U005","ANTO.L","Antofagasta PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","LIVE",
     dp(26),dp(10),dp(9), d(2),d(18),d(19),"https://antofagasta.co.uk","USD/GBP 2026 — 2 DAYS"),
    ("U006","RIO.L","Rio Tinto PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","LIVE",
     dp(30),dp(14),dp(13),d(4),d(20),d(21),"https://riotinto.com","USD/GBP interim 2026 — 4 days"),
    # Urgent rights issues (2)
    ("U007","ALD.PA","ALD Automotive SA","France","EUR","rights_issue","VOLUNTARY","LIVE",
     dp(22),dp(6), dp(5), d(3),d(18),d(23),"https://aldautomotive.com","1 for 5 at EUR 5.80 — 3 days"),
    ("U008","REL.L","RELX PLC","UK","GBX","rights_issue","VOLUNTARY","LIVE",
     dp(18),dp(4), dp(3), d(5),d(22),d(27),"https://relx.com","1 for 8 at 2200p — 5 days"),
    # Urgent tender (1)
    ("U009","ORG.AX","Origin Energy Ltd","Australia","AUD","tender_offer","VOLUNTARY","LIVE",
     dp(20),None,  dp(6), d(3),None,  d(8), "https://originenergy.com.au","AUD 1.5bn fixed tender — 3 days"),
    # Urgent scheme (1) — court sanction imminent
    ("U010","MGGT.L","Meggitt PLC","UK","GBX","scheme_of_arrangement","VOLUNTARY","LIVE",
     dp(60),None,  dp(25),d(1),d(18),d(22), "https://meggitt.com","Parker Hannifin — sanction hearing TOMORROW"),
]

c.executemany("""INSERT OR IGNORE INTO events(
    event_id,ticker,company_name,country,currency,event_type,event_category,
    status,announcement_date,ex_date,record_date,election_deadline,
    payment_date,settlement_date,source_url,notes)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", URGENT_EVENTS)

URGENT_SCRIP = [
    ("U001",10.5,"GBX", 420.0,"1 per 40","GBP",None,None,None,"CASH",0,   0.95,"SCRIP",0),
    ("U002",46.5,"GBX",2840.0,"1 per 61","GBP",None,None,None,"CASH",0,   0.82,"SCRIP",0),
    ("U003",24.3,"GBX", 820.0,"1 per 34","GBP",None,None,None,"CASH",0,   1.15,"SCRIP",0),
    ("U004",12.8,"GBX", 380.0,"1 per 30","GBP",None,None,None,"CASH",0,   0.68,"SCRIP",0),
    ("U005",0.44,"USD",None,None,"GBP|USD",0.7845,0.7740,1.36,"CASH",0,None,"GBP",1),
    ("U006",1.77,"USD",None,None,"GBP|USD",0.7855,0.7750,1.35,"CASH",0,None,"GBP",1),
]
c.executemany(
    "INSERT OR IGNORE INTO scrip_details VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
    URGENT_SCRIP
)
for eid in ('U005','U006'):
    c.execute("UPDATE scrip_details SET rate_pre_deadline=1 WHERE event_id=?", (eid,))

URGENT_RIGHTS = [
    ("U007","RIGHTS_ISSUE","1 for 5",5.80, 8.20,7.67,  1.87,"ALD-N.PA",-24.4,"BNP Paribas",  850.0, 1),
    ("U008","RIGHTS_ISSUE","1 for 8",2200.0,3150.0,2993.8,793.8,"REL-N.L",-26.5,"Goldman Sachs",2400.0,1),
]
c.executemany(
    "INSERT OR IGNORE INTO rights_details(event_id,rights_type,rights_ratio,subscription_price,"
    "current_price,terp,nil_paid_value,nil_paid_ticker,discount_to_terp_pct,underwriter,"
    "gross_proceeds_mn,fully_underwritten) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
    URGENT_RIGHTS
)

URGENT_TENDERS = [
    ("U009","FIXED",8.50,None,None,8.05,5.6,None,1500.0,1,60.0,500,1),
]
c.executemany("INSERT OR IGNORE INTO tender_details VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", URGENT_TENDERS)

URGENT_MERGERS = [
    ("U010","SCHEME","Parker Hannifin","PH","CASH",850.0,None,848.5,0.18,d(1),d(30),"CLEARED","LOW"),
]
c.executemany("INSERT OR IGNORE INTO merger_details VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", URGENT_MERGERS)

conn.commit()

# ── Verification summary ──────────────────────────────────────────────────────
today_actual = date.today().isoformat()
total   = c.execute("SELECT COUNT(*) FROM events").fetchone()[0]
live    = c.execute("SELECT COUNT(*) FROM events WHERE status='LIVE'").fetchone()[0]
urgent  = c.execute(
    "SELECT COUNT(*) FROM events WHERE election_deadline IS NOT NULL "
    "AND election_deadline BETWEEN ? AND date(?,'+7 days') AND status='LIVE'",
    (today_actual, today_actual)
).fetchone()[0]
passed  = c.execute(
    "SELECT COUNT(*) FROM events WHERE election_deadline IS NOT NULL "
    "AND election_deadline < ? AND status='LIVE'",
    (today_actual,)
).fetchone()[0]
urg_new = c.execute(
    "SELECT COUNT(*) FROM events WHERE event_id LIKE 'U%' AND election_deadline >= ?",
    (today_actual,)
).fetchone()[0]

print(f"\n✓  events.db patched")
print(f"   Total events      : {total}")
print(f"   LIVE              : {live}")
print(f"   Deadlines ≤7d     : {urgent}  (includes {urg_new} new U-events)")
print(f"   Passed deadlines  : {passed}  (includes 20 P-events)")
print(f"\n   ARCLK.IS  spread  : 1.67% → 10.4%  (HIGH risk, ~59% impl prob)")
print(f"   CTEC.L odd lot    : ≤100 shares guaranteed fill added")
conn.close()
