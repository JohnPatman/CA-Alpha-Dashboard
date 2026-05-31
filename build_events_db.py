"""
build_events_db.py
------------------
Creates data/events.db — the SQLite corporate actions event store
for the Voluntary CA Alpha Dashboard.

Tables:
    events          — master event table (all types)
    scrip_details   — scrip dividend / FX election specifics
    rights_details  — rights issue / open offer specifics
    tender_details  — tender offer / buyback / dutch auction specifics
    merger_details  — scheme of arrangement / merger specifics
    spinoff_details — spin-off / demerger specifics
    split_details   — stock split / consolidation specifics

Run:  python3 build_events_db.py
Out:  data/events.db
"""

import sqlite3
import os
from datetime import date, timedelta

DB_PATH = "data/events.db"
os.makedirs("data", exist_ok=True)

# ── today reference ────────────────────────────────────────────────────────
TODAY = date(2026, 5, 25)

def d(days):
    """Return ISO date string relative to TODAY."""
    return (TODAY + timedelta(days=days)).isoformat()

def dp(days):
    """Past date."""
    return (TODAY - timedelta(days=days)).isoformat()


# ══════════════════════════════════════════════════════════════════════════════
# SCHEMA
# ══════════════════════════════════════════════════════════════════════════════

SCHEMA = """
-- ── Master events table ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS events (
    event_id            TEXT PRIMARY KEY,
    ticker              TEXT NOT NULL,
    company_name        TEXT NOT NULL,
    country             TEXT NOT NULL,
    currency            TEXT NOT NULL,
    event_type          TEXT NOT NULL,
    event_category      TEXT NOT NULL,   -- MANDATORY / MANDATORY_WITH_CHOICE / VOLUNTARY
    status              TEXT NOT NULL,   -- LIVE / UPCOMING / CLOSED / CANCELLED
    announcement_date   TEXT,
    ex_date             TEXT,
    record_date         TEXT,
    election_deadline   TEXT,
    payment_date        TEXT,
    settlement_date     TEXT,
    source_url          TEXT,
    notes               TEXT,
    last_updated        TEXT DEFAULT (date('now'))
);

-- ── Scrip dividend & FX election details ─────────────────────────────────────
CREATE TABLE IF NOT EXISTS scrip_details (
    event_id                TEXT PRIMARY KEY REFERENCES events(event_id),
    cash_amount             REAL,
    cash_currency           TEXT,
    scrip_issue_price       REAL,
    scrip_ratio             TEXT,           -- e.g. "1 share per 52 held"
    dividend_currency_opts  TEXT,           -- e.g. "GBP|USD"
    company_fx_rate         REAL,           -- company published rate
    market_fx_rate          REAL,           -- live market rate
    fx_arbitrage_pct        REAL,           -- (company - market) / market * 100
    election_default        TEXT,           -- CASH or SCRIP
    withholding_tax_pct     REAL DEFAULT 0,
    scrip_discount_pct      REAL,           -- implied discount/premium vs cash
    optimal_election        TEXT            -- CASH or SCRIP (calculated)
);

-- ── Rights issue & open offer details ────────────────────────────────────────
CREATE TABLE IF NOT EXISTS rights_details (
    event_id            TEXT PRIMARY KEY REFERENCES events(event_id),
    rights_type         TEXT,           -- RIGHTS_ISSUE / OPEN_OFFER / PLACING
    rights_ratio        TEXT,           -- e.g. "1 for 4"
    subscription_price  REAL,
    current_price       REAL,
    terp                REAL,           -- theoretical ex-rights price
    nil_paid_value      REAL,           -- TERP - subscription price
    nil_paid_ticker     TEXT,
    discount_to_terp_pct REAL,
    underwriter         TEXT,
    gross_proceeds_mn   REAL,           -- £/€/$ millions
    fully_underwritten  INTEGER DEFAULT 1  -- boolean
);

-- ── Tender offer, buyback, dutch auction, odd-lot details ────────────────────
CREATE TABLE IF NOT EXISTS tender_details (
    event_id            TEXT PRIMARY KEY REFERENCES events(event_id),
    tender_type         TEXT,           -- FIXED / DUTCH_AUCTION / ODD_LOT / BUYBACK
    tender_price        REAL,
    tender_price_low    REAL,           -- dutch auction lower bound
    tender_price_high   REAL,           -- dutch auction upper bound
    current_price       REAL,
    premium_to_mkt_pct  REAL,
    max_shares_sought   INTEGER,
    max_value_mn        REAL,           -- £/€/$ millions
    proration_expected  INTEGER,        -- boolean
    estimated_proration_pct REAL,
    odd_lot_threshold   INTEGER,        -- shares (e.g. 99 for odd-lot)
    odd_lot_guaranteed  INTEGER DEFAULT 0  -- boolean
);

-- ── Merger, scheme of arrangement, exchange offer details ────────────────────
CREATE TABLE IF NOT EXISTS merger_details (
    event_id                TEXT PRIMARY KEY REFERENCES events(event_id),
    merger_type             TEXT,       -- SCHEME / MERGER / EXCHANGE_OFFER
    acquirer                TEXT,
    acquirer_ticker         TEXT,
    consideration_type      TEXT,       -- CASH / SHARES / MIXED
    cash_per_share          REAL,
    share_ratio             TEXT,       -- e.g. "0.4 acquirer shares per target share"
    current_price           REAL,
    spread_to_terms_pct     REAL,       -- arbitrage spread
    court_sanction_date     TEXT,
    long_stop_date          TEXT,
    regulatory_status       TEXT,       -- PENDING / CLEARED / BLOCKED
    break_risk              TEXT        -- LOW / MEDIUM / HIGH
);

-- ── Spin-off & demerger details ───────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS spinoff_details (
    event_id            TEXT PRIMARY KEY REFERENCES events(event_id),
    spinoff_name        TEXT,
    spinoff_ticker      TEXT,
    spinoff_exchange    TEXT,
    distribution_ratio  TEXT,          -- e.g. "1 spinoff share per 4 held"
    spinoff_sector      TEXT,
    estimated_value     REAL,          -- per share estimate
    listing_date        TEXT
);

-- ── Stock split & consolidation details ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS split_details (
    event_id        TEXT PRIMARY KEY REFERENCES events(event_id),
    split_type      TEXT,              -- SPLIT / CONSOLIDATION
    split_ratio     TEXT,              -- e.g. "10:1" or "1:5"
    pre_split_price REAL,
    post_split_price_est REAL
);
"""


# ══════════════════════════════════════════════════════════════════════════════
# SEED DATA
# ══════════════════════════════════════════════════════════════════════════════

# ── Master events ─────────────────────────────────────────────────────────────
EVENTS = [

    # ── SCRIP DIVIDENDS (20) ─────────────────────────────────────────────────
    ("EVT-001","LMP.L","LondonMetric Property PLC","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(30),dp(14),dp(13),d(5),d(20),d(21),"https://www.londonmetric.com/investors","Q1 2026 scrip dividend"),

    ("EVT-002","LGEN.L","Legal & General Group PLC","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(25),dp(10),dp(9),d(8),d(25),d(26),"https://www.legalandgeneral.com/investors","Final dividend 2025"),

    ("EVT-003","ULVR.L","Unilever PLC","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(20),dp(7),dp(6),d(12),d(30),d(31),"https://www.unilever.com/investors","Q1 2026 interim dividend"),

    ("EVT-004","HSBA.L","HSBC Holdings PLC","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","UPCOMING",
     dp(5),d(14),d(15),d(35),d(55),d(56),"https://www.hsbc.com/investors","2026 interim scrip election"),

    ("EVT-005","SHEL.L","Shell PLC","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(28),dp(12),dp(11),d(3),d(18),d(19),"https://www.shell.com/investors","Q1 2026 scrip dividend"),

    ("EVT-006","RIO.L","Rio Tinto PLC","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","UPCOMING",
     dp(3),d(18),d(19),d(40),d(60),d(61),"https://www.riotinto.com/investors","2026 interim dividend"),

    ("EVT-007","NG.L","National Grid PLC","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(35),dp(18),dp(17),d(2),d(15),d(16),"https://www.nationalgrid.com/investors","FY2026 final dividend"),

    ("EVT-008","AV.L","Aviva PLC","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","UPCOMING",
     dp(7),d(21),d(22),d(42),d(65),d(66),"https://www.aviva.com/investors","2026 interim scrip"),

    ("EVT-009","GSK.L","GSK PLC","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(22),dp(8),dp(7),d(7),d(22),d(23),"https://www.gsk.com/investors","Q1 2026 quarterly dividend"),

    ("EVT-010","PRU.L","Prudential PLC","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(18),dp(5),dp(4),d(10),d(28),d(29),"https://www.prudentialplc.com/investors","2026 interim scrip"),

    ("EVT-011","NESN.SW","Nestle SA","Switzerland","CHF","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(30),dp(14),dp(13),d(4),d(20),d(21),"https://www.nestle.com/investors","AGM 2026 dividend"),

    ("EVT-012","SAN.MC","Banco Santander SA","Spain","EUR","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(25),dp(10),dp(9),d(6),d(22),d(23),"https://www.santander.com/investors","Santander Dividendo Eleccion Q2 2026"),

    ("EVT-013","BBVA.MC","BBVA SA","Spain","EUR","scrip_dividend","MANDATORY_WITH_CHOICE","UPCOMING",
     dp(4),d(20),d(21),d(45),d(65),d(66),"https://www.bbva.com/investors","BBVA Dividendo Eleccion 2026"),

    ("EVT-014","ENEL.MI","Enel SpA","Italy","EUR","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(20),dp(6),dp(5),d(9),d(25),d(26),"https://www.enel.com/investors","2026 interim dividend scrip"),

    ("EVT-015","ISP.MI","Intesa Sanpaolo SpA","Italy","EUR","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(15),dp(4),dp(3),d(11),d(28),d(29),"https://www.intesasanpaolo.com/investors","2026 scrip dividend option"),

    ("EVT-016","NPN.JO","Naspers Ltd","South Africa","ZAR","scrip_dividend","MANDATORY_WITH_CHOICE","UPCOMING",
     dp(6),d(25),d(26),d(50),d(70),d(71),"https://www.naspers.com/investors","FY2026 final dividend"),

    ("EVT-017","MTN.JO","MTN Group Ltd","South Africa","ZAR","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(28),dp(12),dp(11),d(4),d(20),d(21),"https://www.mtn.com/investors","2026 H1 scrip dividend"),

    ("EVT-018","ABI.BR","Anheuser-Busch InBev SA","Belgium","EUR","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(32),dp(16),dp(15),d(2),d(18),d(19),"https://www.ab-inbev.com/investors","2026 interim scrip option"),

    ("EVT-019","HEIA.AS","Heineken NV","Netherlands","EUR","scrip_dividend","MANDATORY_WITH_CHOICE","UPCOMING",
     dp(5),d(22),d(23),d(44),d(65),d(66),"https://www.theheinekencompany.com/investors","2026 final dividend"),

    ("EVT-020","OR.PA","L'Oreal SA","France","EUR","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",
     dp(18),dp(5),dp(4),d(8),d(25),d(26),"https://www.loreal-finance.com","2026 AGM dividend"),

    # ── FX CURRENCY ELECTIONS (15) ────────────────────────────────────────────
    ("EVT-021","AAF.L","Airtel Africa PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","LIVE",
     dp(28),dp(12),dp(11),d(4),d(20),d(21),"https://www.airtelafrica.com/investors","Q3 FY2026 dividend FX election"),

    ("EVT-022","AAF.L","Airtel Africa PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","UPCOMING",
     dp(3),d(35),d(36),d(60),d(80),d(81),"https://www.airtelafrica.com/investors","Q4 FY2026 dividend FX election"),

    ("EVT-023","HSBA.L","HSBC Holdings PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","LIVE",
     dp(20),dp(7),dp(6),d(12),d(30),d(31),"https://www.hsbc.com/investors","Q1 2026 USD/GBP election"),

    ("EVT-024","PRU.L","Prudential PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","LIVE",
     dp(15),dp(4),dp(3),d(14),d(32),d(33),"https://www.prudentialplc.com/investors","HKD/USD/GBP election 2026"),

    ("EVT-025","STAN.L","Standard Chartered PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","LIVE",
     dp(22),dp(8),dp(7),d(8),d(24),d(25),"https://www.sc.com/investors","2026 interim USD/GBP election"),

    ("EVT-026","VOD.L","Vodafone Group PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","UPCOMING",
     dp(4),d(28),d(29),d(50),d(70),d(71),"https://www.vodafone.com/investors","FY2026 EUR/GBP election"),

    ("EVT-027","RIO.L","Rio Tinto PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","UPCOMING",
     dp(3),d(18),d(19),d(40),d(60),d(61),"https://www.riotinto.com/investors","2026 interim USD/GBP/AUD election"),

    ("EVT-028","AZN.L","AstraZeneca PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","LIVE",
     dp(24),dp(9),dp(8),d(6),d(22),d(23),"https://www.astrazeneca.com/investors","Q1 2026 USD/GBP election"),

    ("EVT-029","BHP.JO","BHP Group Ltd","South Africa","ZAR","fx_election","MANDATORY_WITH_CHOICE","LIVE",
     dp(20),dp(6),dp(5),d(10),d(28),d(29),"https://www.bhp.com/investors","2026 H1 USD/ZAR/GBP election"),

    ("EVT-030","GLEN.L","Glencore PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","UPCOMING",
     dp(6),d(30),d(31),d(55),d(75),d(76),"https://www.glencore.com/investors","2026 USD/GBP election"),

    ("EVT-031","EXPN.L","Experian PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","LIVE",
     dp(18),dp(5),dp(4),d(9),d(26),d(27),"https://www.experianplc.com/investors","FY2026 USD/GBP/EUR election"),

    ("EVT-032","CCH.L","Coca-Cola HBC AG","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","LIVE",
     dp(25),dp(10),dp(9),d(5),d(21),d(22),"https://www.coca-colahbc.com/investors","2026 EUR/GBP election"),

    ("EVT-033","MNDI.L","Mondi PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","UPCOMING",
     dp(4),d(24),d(25),d(46),d(66),d(67),"https://www.mondigroup.com/investors","2026 interim ZAR/GBP/EUR election"),

    ("EVT-034","ANF.L","Anglo American PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","LIVE",
     dp(30),dp(14),dp(13),d(3),d(19),d(20),"https://www.angloamerican.com/investors","2026 USD/GBP election"),

    ("EVT-035","EQNR.OL","Equinor ASA","Norway","NOK","fx_election","MANDATORY_WITH_CHOICE","LIVE",
     dp(22),dp(8),dp(7),d(7),d(23),d(24),"https://www.equinor.com/investors","Q1 2026 USD/NOK election"),

    # ── TENDER OFFERS / BUYBACKS (12) ─────────────────────────────────────────
    ("EVT-036","CTEC.L","Convatec Group PLC","UK","GBX","tender_offer","VOLUNTARY","LIVE",
     dp(18),None,dp(5),d(14),None,d(20),"https://www.convatecgroup.com/investors","Share buyback tender offer"),

    ("EVT-037","RMV.L","Rightmove PLC","UK","GBX","buyback","VOLUNTARY","LIVE",
     dp(30),None,None,d(60),None,None,"https://www.rightmove.co.uk/investors","2026 on-market buyback programme"),

    ("EVT-038","NXT.L","Next PLC","UK","GBX","tender_offer","VOLUNTARY","UPCOMING",
     dp(5),None,d(10),d(30),None,d(36),"https://www.nextplc.co.uk/investors","FY2026 tender offer"),

    ("EVT-039","MSFT","Microsoft Corporation","US","USD","buyback","VOLUNTARY","LIVE",
     dp(45),None,None,d(90),None,None,"https://www.microsoft.com/investors","$60bn buyback programme 2026"),

    ("EVT-040","AAPL","Apple Inc","US","USD","tender_offer","VOLUNTARY","LIVE",
     dp(20),None,dp(8),d(15),None,d(21),"https://www.apple.com/investors","Q2 2026 accelerated buyback"),

    ("EVT-041","META","Meta Platforms Inc","US","USD","buyback","VOLUNTARY","LIVE",
     dp(60),None,None,d(120),None,None,"https://investor.fb.com","2026 buyback programme"),

    ("EVT-042","IHG.L","InterContinental Hotels Group PLC","UK","GBX","tender_offer","VOLUNTARY","LIVE",
     dp(12),None,dp(3),d(18),None,d(24),"https://www.ihgplc.com/investors","$800m tender offer 2026"),

    ("EVT-043","CPG.L","Compass Group PLC","UK","GBX","buyback","VOLUNTARY","UPCOMING",
     dp(8),None,None,d(80),None,None,"https://www.compass-group.com/investors","£1bn buyback 2026"),

    ("EVT-044","SAP.DE","SAP SE","Germany","EUR","buyback","VOLUNTARY","LIVE",
     dp(40),None,None,d(100),None,None,"https://www.sap.com/investors","€2bn buyback programme 2026"),

    ("EVT-045","TTE.PA","TotalEnergies SE","France","EUR","buyback","VOLUNTARY","LIVE",
     dp(35),None,None,d(95),None,None,"https://totalenergies.com/investors","$2bn quarterly buyback Q2 2026"),

    ("EVT-046","NOVO-B.CO","Novo Nordisk A/S","Denmark","DKK","buyback","VOLUNTARY","LIVE",
     dp(50),None,None,d(130),None,None,"https://www.novonordisk.com/investors","2026 share buyback programme"),

    ("EVT-047","2222.SR","Saudi Arabian Oil Co","Saudi Arabia","SAR","buyback","VOLUNTARY","UPCOMING",
     dp(6),None,None,d(75),None,None,"https://www.aramco.com/investors","SAR 50bn buyback 2026"),

    # ── RIGHTS ISSUES / OPEN OFFERS (10) ──────────────────────────────────────
    ("EVT-048","BT-A.L","BT Group PLC","UK","GBX","rights_issue","VOLUNTARY","LIVE",
     dp(15),d(5),d(6),d(20),d(35),d(40),"https://www.bt.com/investors","1 for 3 rights issue at 95p"),

    ("EVT-049","VOD.L","Vodafone Group PLC","UK","GBX","open_offer","VOLUNTARY","UPCOMING",
     dp(3),d(18),d(19),d(35),d(50),d(55),"https://www.vodafone.com/investors","Open offer at 62p"),

    ("EVT-050","BARC.L","Barclays PLC","UK","GBX","rights_issue","VOLUNTARY","CLOSED",
     dp(60),dp(45),dp(44),dp(25),dp(10),dp(5),"https://www.barclays.com/investors","1 for 5 rights issue at 140p — CLOSED"),

    ("EVT-051","UCG.MI","UniCredit SpA","Italy","EUR","rights_issue","VOLUNTARY","UPCOMING",
     dp(4),d(22),d(23),d(40),d(58),d(63),"https://www.unicreditgroup.eu/investors","Capital raise rights issue"),

    ("EVT-052","ALPHA.AT","Alpha Services and Holdings SA","Greece","EUR","rights_issue","VOLUNTARY","LIVE",
     dp(20),d(8),d(9),d(25),d(42),d(47),"https://www.alpha.gr/investors","1 for 2 rights issue at €0.85"),

    ("EVT-053","NWG.L","NatWest Group PLC","UK","GBX","open_offer","VOLUNTARY","LIVE",
     dp(12),d(3),d(4),d(18),d(33),d(38),"https://www.natwestgroup.com/investors","Open offer at 280p"),

    ("EVT-054","THYAO.IS","Turk Hava Yollari AS","Turkey","TRY","rights_issue","VOLUNTARY","LIVE",
     dp(18),d(5),d(6),d(22),d(38),d(43),"https://www.turkishairlines.com/investors","Capital increase rights issue"),

    ("EVT-055","FSR.JO","FirstRand Ltd","South Africa","ZAR","rights_issue","VOLUNTARY","UPCOMING",
     dp(5),d(28),d(29),d(48),d(68),d(73),"https://www.firstrand.co.za/investors","1 for 8 rights issue"),

    ("EVT-056","ETEL.CA","Telecom Egypt SAE","Egypt","EGP","rights_issue","VOLUNTARY","LIVE",
     dp(22),d(6),d(7),d(24),d(42),d(47),"https://www.telecomegypt.com.eg/investors","Capital increase 1 for 4"),

    ("EVT-057","TPEIR.AT","Piraeus Financial Holdings SA","Greece","EUR","open_offer","VOLUNTARY","UPCOMING",
     dp(4),d(20),d(21),d(38),d(56),d(61),"https://www.piraeusholdings.gr/investors","Open offer at €2.40"),

    # ── SCHEMES / MERGERS (8) ─────────────────────────────────────────────────
    ("EVT-058","SMIN.L","Smiths Group PLC","UK","GBX","scheme_of_arrangement","VOLUNTARY","LIVE",
     dp(45),None,dp(10),d(25),d(40),d(45),"https://www.smiths.com/investors","Recommended acquisition by US buyer"),

    ("EVT-059","BNZL.L","Bunzl PLC","UK","GBX","scheme_of_arrangement","VOLUNTARY","UPCOMING",
     dp(8),None,d(15),d(40),d(60),d(65),"https://www.bunzl.com/investors","Recommended cash offer"),

    ("EVT-060","DCC.L","DCC PLC","UK","GBX","scheme_of_arrangement","VOLUNTARY","LIVE",
     dp(55),None,dp(20),d(15),d(30),d(35),"https://www.dcc.ie/investors","Recommended acquisition"),

    ("EVT-061","ENTAIN","Entain PLC","UK","GBX","scheme_of_arrangement","VOLUNTARY","UPCOMING",
     dp(10),None,d(20),d(45),d(65),d(70),"https://www.entaingroup.com/investors","Recommended cash and share offer"),

    ("EVT-062","ARCLK.IS","Arcelik AS","Turkey","TRY","merger","VOLUNTARY","LIVE",
     dp(30),None,dp(5),d(20),d(38),d(43),"https://www.arcelikglobal.com/investors","Strategic merger consideration"),

    ("EVT-063","ZORN.IS","Zorlu Enerji AS","Turkey","TRY","exchange_offer","VOLUNTARY","LIVE",
     dp(25),None,dp(3),d(18),d(35),d(40),"https://www.zorluenerji.com.tr/investors","Share exchange offer"),

    ("EVT-064","COMI.CA","Commercial International Bank Egypt","Egypt","EGP","scheme_of_arrangement","VOLUNTARY","UPCOMING",
     dp(4),None,d(25),d(50),d(70),d(75),"https://www.cibeg.com/investors","Strategic acquisition proposal"),

    ("EVT-065","ATCO-A.ST","Atlas Copco AB","Sweden","SEK","merger","VOLUNTARY","CLOSED",
     dp(90),None,dp(45),dp(20),dp(5),dp(2),"https://www.atlascopcogroup.com/investors","Division merger — CLOSED"),

    # ── DUTCH AUCTION TENDERS (6) ─────────────────────────────────────────────
    ("EVT-066","EXPN.L","Experian PLC","UK","GBX","dutch_auction","VOLUNTARY","LIVE",
     dp(14),None,dp(2),d(16),None,d(22),"https://www.experianplc.com/investors","Dutch auction tender $500m"),

    ("EVT-067","REL.L","RELX PLC","UK","GBX","dutch_auction","VOLUNTARY","UPCOMING",
     dp(5),None,d(12),d(32),None,d(38),"https://www.relx.com/investors","Dutch auction tender £400m"),

    ("EVT-068","GOOG","Alphabet Inc","US","USD","dutch_auction","VOLUNTARY","LIVE",
     dp(20),None,dp(5),d(15),None,d(21),"https://abc.xyz/investor","Dutch auction tender $5bn"),

    ("EVT-069","V","Visa Inc","US","USD","dutch_auction","VOLUNTARY","LIVE",
     dp(18),None,dp(4),d(18),None,d(24),"https://investor.visa.com","Dutch auction tender $4bn"),

    ("EVT-070","MC.PA","LVMH Moet Hennessy Louis Vuitton SE","France","EUR","dutch_auction","VOLUNTARY","UPCOMING",
     dp(6),None,d(18),d(40),None,d(46),"https://www.lvmh.com/investors","€2bn dutch auction buyback"),

    ("EVT-071","SIE.DE","Siemens AG","Germany","EUR","dutch_auction","VOLUNTARY","LIVE",
     dp(22),None,dp(6),d(14),None,d(20),"https://www.siemens.com/investors","€1.5bn dutch auction tender"),

    # ── SPIN-OFFS / DEMERGERS (5) ─────────────────────────────────────────────
    ("EVT-072","GSK.L","GSK PLC","UK","GBX","spinoff","MANDATORY","UPCOMING",
     dp(8),d(30),d(31),None,d(45),d(46),"https://www.gsk.com/investors","Consumer healthcare division spinoff"),

    ("EVT-073","GLEN.L","Glencore PLC","UK","GBX","demerger","MANDATORY","UPCOMING",
     dp(12),d(45),d(46),None,d(60),d(61),"https://www.glencore.com/investors","Coal assets demerger"),

    ("EVT-074","SIE.DE","Siemens AG","Germany","EUR","spinoff","MANDATORY","LIVE",
     dp(30),d(15),d(16),None,d(30),d(31),"https://www.siemens.com/investors","Energy division partial spinoff"),

    ("EVT-075","ENEL.MI","Enel SpA","Italy","EUR","demerger","MANDATORY","UPCOMING",
     dp(4),d(60),d(61),None,d(75),d(76),"https://www.enel.com/investors","Grid infrastructure demerger"),

    ("EVT-076","TTE.PA","TotalEnergies SE","France","EUR","spinoff","MANDATORY","UPCOMING",
     dp(7),d(50),d(51),None,d(65),d(66),"https://totalenergies.com/investors","Renewable energy subsidiary listing"),

    # ── ODD-LOT OFFERS (4) ────────────────────────────────────────────────────
    ("EVT-077","TSCO.L","Tesco PLC","UK","GBX","odd_lot_offer","VOLUNTARY","LIVE",
     dp(14),None,dp(3),d(17),None,d(23),"https://www.tescoplc.com/investors","Odd-lot offer up to 99 shares"),

    ("EVT-078","AZN.L","AstraZeneca PLC","UK","GBX","odd_lot_offer","VOLUNTARY","LIVE",
     dp(18),None,dp(5),d(13),None,d(19),"https://www.astrazeneca.com/investors","Odd-lot tender — 100% take-up guaranteed"),

    ("EVT-079","JNJ","Johnson & Johnson","US","USD","odd_lot_offer","VOLUNTARY","UPCOMING",
     dp(5),None,d(10),d(30),None,d(36),"https://www.investor.jnj.com","Odd-lot offer within buyback"),

    ("EVT-080","LSEG.L","London Stock Exchange Group PLC","UK","GBX","odd_lot_offer","VOLUNTARY","LIVE",
     dp(20),None,dp(7),d(10),None,d(16),"https://www.lseg.com/investors","Odd-lot offer up to 99 shares"),

    # ── STOCK SPLITS / CONSOLIDATIONS (5) ────────────────────────────────────
    ("EVT-081","NVDA","NVIDIA Corporation","US","USD","stock_split","MANDATORY","UPCOMING",
     dp(10),d(20),d(21),None,None,None,"https://investor.nvidia.com","10:1 stock split"),

    ("EVT-082","GAW.L","Games Workshop Group PLC","UK","GBX","stock_split","MANDATORY","LIVE",
     dp(25),d(5),d(6),None,None,None,"https://www.games-workshop.com/investors","5:1 stock split"),

    ("EVT-083","NOVO-B.CO","Novo Nordisk A/S","Denmark","DKK","stock_split","MANDATORY","CLOSED",
     dp(60),dp(45),dp(44),None,None,None,"https://www.novonordisk.com/investors","2:1 split — CLOSED"),

    ("EVT-084","EZJ.L","EasyJet PLC","UK","GBX","consolidation","MANDATORY","UPCOMING",
     dp(6),d(25),d(26),None,None,None,"https://corporate.easyjet.com/investors","1:10 share consolidation"),

    ("EVT-085","BAYN.DE","Bayer AG","Germany","EUR","consolidation","MANDATORY","LIVE",
     dp(18),d(8),d(9),None,None,None,"https://www.investor.bayer.com","1:5 share consolidation"),
]

# ── Scrip details ──────────────────────────────────────────────────────────────
SCRIP = [
    # event_id, cash_amt, cash_ccy, scrip_price, ratio, ccy_opts, co_fx, mkt_fx, fx_arb, default, wht, disc, optimal
    ("EVT-001", 3.05,"GBP", 181.80,"1 share per 59 held","GBP",  None, None, None,"CASH", 0, -1.47,"CASH"),
    ("EVT-002", 5.84,"GBP", 240.00,"1 share per 41 held","GBP",  None, None, None,"CASH", 0, -0.83,"CASH"),
    ("EVT-003",43.50,"GBP",4120.00,"1 share per 94 held","GBP",  None, None, None,"CASH", 0,  0.24,"SCRIP"),
    ("EVT-004", 0.10,"USD",   None, None,                "GBP|USD",0.7617,0.7402, 2.91,"CASH", 0, None,"CASH"),
    ("EVT-005",34.00,"USD",2465.00,"1 share per 72 held","GBP|USD",0.7920,0.7750, 2.19,"CASH", 0, -0.62,"CASH"),
    ("EVT-006", 1.77,"USD",   None, None,                "GBP|USD",0.7850,0.7750, 1.29,"CASH", 0, None,"CASH"),
    ("EVT-007",17.40,"GBP",1058.00,"1 share per 60 held","GBP",  None, None, None,"CASH", 0,  0.38,"SCRIP"),
    ("EVT-008",22.50,"GBP", 480.00,"1 share per 21 held","GBP",  None, None, None,"CASH", 0, -0.42,"CASH"),
    ("EVT-009",16.25,"GBP",1890.00,"1 share per 116 held","GBP", None, None, None,"CASH", 0,  0.15,"SCRIP"),
    ("EVT-010", 5.90,"USD",   None, None,                "GBP|USD|HKD",0.7820,0.7750, 0.90,"CASH", 0, None,"CASH"),
    ("EVT-011", 2.80,"CHF",  95.20,"1 share per 34 held","CHF",  None, None, None,"CASH", 35, -1.05,"CASH"),
    ("EVT-012", 0.10,"EUR",   4.12,"1 share per 41 held","EUR",  None, None, None,"SCRIP", 19,-0.73,"CASH"),
    ("EVT-013", 0.08,"EUR",   9.45,"1 share per 118 held","EUR", None, None, None,"SCRIP", 19,-0.55,"CASH"),
    ("EVT-014", 0.43,"EUR",   7.25,"1 share per 16 held","EUR",  None, None, None,"CASH", 26,-0.88,"CASH"),
    ("EVT-015", 0.22,"EUR",   3.85,"1 share per 17 held","EUR",  None, None, None,"CASH", 26,-1.04,"CASH"),
    ("EVT-016",25.00,"ZAR",5200.00,"1 share per 208 held","ZAR", None, None, None,"CASH", 20,-0.38,"CASH"),
    ("EVT-017", 3.50,"ZAR", 148.00,"1 share per 42 held","ZAR",  None, None, None,"CASH", 20,-0.27,"SCRIP"),
    ("EVT-018", 0.80,"EUR",  55.20,"1 share per 69 held","EUR",  None, None, None,"CASH", 30,-1.16,"CASH"),
    ("EVT-019", 1.04,"EUR",  82.00,"1 share per 78 held","EUR",  None, None, None,"CASH", 15,-0.49,"CASH"),
    ("EVT-020", 5.40,"EUR", 395.00,"1 share per 73 held","EUR",  None, None, None,"CASH", 30,-0.63,"CASH"),
]

# ── FX election details (reuses scrip_details table for FX fields) ─────────────
FX_ELECTIONS = [
    # event_id, cash_amt, cash_ccy, scrip_price, ratio, ccy_opts, co_fx, mkt_fx, fx_arb, default, wht, disc, optimal
    ("EVT-021", 0.0284,"USD",None,None,"GBP|USD", 0.7617, 0.7402, 2.91,"CASH", 0, None,"GBP"),
    ("EVT-022", 0.0290,"USD",None,None,"GBP|USD", None,   0.7750, None,"CASH", 0, None, None),
    ("EVT-023", 0.1000,"USD",None,None,"GBP|USD", 0.7820, 0.7750, 0.90,"CASH", 0, None,"GBP"),
    ("EVT-024", 0.0600,"USD",None,None,"GBP|USD|HKD",0.7820,0.7750,0.90,"CASH",0, None,"GBP"),
    ("EVT-025", 0.0720,"USD",None,None,"GBP|USD", 0.7900, 0.7750, 1.94,"CASH", 0, None,"GBP"),
    ("EVT-026", 0.0450,"EUR",None,None,"GBP|EUR", 0.8520, 0.8480, 0.47,"CASH", 0, None,"GBP"),
    ("EVT-027", 1.7700,"USD",None,None,"GBP|USD|AUD",0.7850,0.7750,1.29,"CASH",0, None,"GBP"),
    ("EVT-028", 1.0200,"USD",None,None,"GBP|USD", 0.7800, 0.7750, 0.65,"CASH", 0, None,"GBP"),
    ("EVT-029", 0.7200,"USD",None,None,"USD|ZAR|GBP",0.7830,0.7750,1.03,"CASH",0, None,"GBP"),
    ("EVT-030", 0.0600,"USD",None,None,"GBP|USD", None,   0.7750, None,"CASH", 0, None, None),
    ("EVT-031", 0.3850,"USD",None,None,"GBP|USD|EUR",0.7810,0.7750,0.77,"CASH",0, None,"GBP"),
    ("EVT-032", 0.2200,"EUR",None,None,"GBP|EUR", 0.8530, 0.8480, 0.59,"CASH", 0, None,"GBP"),
    ("EVT-033", 0.1500,"EUR",None,None,"ZAR|GBP|EUR",0.8510,0.8480,0.37,"CASH",0, None,"GBP"),
    ("EVT-034", 0.5500,"USD",None,None,"GBP|USD", 0.7840, 0.7750, 1.16,"CASH", 0, None,"GBP"),
    ("EVT-035", 0.3500,"USD",None,None,"USD|NOK", 10.820, 10.750, 0.65,"CASH", 0, None,"NOK"),
]

# ── Tender details ─────────────────────────────────────────────────────────────
TENDERS = [
    # event_id, type, price, low, high, curr_price, premium%, max_shares, max_val_mn, proration, proration%, odd_lot_thresh, odd_lot_guar
    ("EVT-036","FIXED",     220.0, None, None, 198.0, 11.1,  50000000,  110.0, 0,  None, None, 0),
    ("EVT-037","BUYBACK",   None,  None, None, 654.0, None,  None,      500.0, 0,  None, None, 0),
    ("EVT-038","FIXED",    4200.0, None, None,3980.0,  5.5,  12000000,  500.0, 1,  65.0, None, 0),
    ("EVT-039","BUYBACK",   None,  None, None, 415.0, None,  None,    60000.0, 0,  None, None, 0),
    ("EVT-040","BUYBACK",   None,  None, None, 225.0, None,  None,    10000.0, 0,  None, None, 0),
    ("EVT-041","BUYBACK",   None,  None, None, 580.0, None,  None,    50000.0, 0,  None, None, 0),
    ("EVT-042","FIXED",    7200.0, None, None,6850.0,  5.1,   8000000,  576.0, 1,  55.0, None, 0),
    ("EVT-043","BUYBACK",   None,  None, None,2450.0, None,  None,     1000.0, 0,  None, None, 0),
    ("EVT-044","BUYBACK",   None,  None, None, 178.0, None,  None,     2000.0, 0,  None, None, 0),
    ("EVT-045","BUYBACK",   None,  None, None,  58.5, None,  None,     2000.0, 0,  None, None, 0),
    ("EVT-046","BUYBACK",   None,  None, None, 820.0, None,  None,     5000.0, 0,  None, None, 0),
    ("EVT-047","BUYBACK",   None,  None, None,  28.5, None,  None,    13500.0, 0,  None, None, 0),
]

# ── Rights details ─────────────────────────────────────────────────────────────
RIGHTS = [
    # event_id, type, ratio, sub_price, curr_price, terp, nil_paid, nil_paid_tkr, disc_terp%, underwriter, proceeds_mn, underwritten
    ("EVT-048","RIGHTS_ISSUE","1 for 3",  95.0, 128.0, 119.75, 24.75,"BT-A-N.L",   -20.7,"Goldman Sachs", 850.0, 1),
    ("EVT-049","OPEN_OFFER",  "1 for 8",  62.0,  88.0,  84.75, None, None,          -26.8,"Barclays",      180.0, 1),
    ("EVT-050","RIGHTS_ISSUE","1 for 5", 140.0, 178.0, 172.33, 32.33,"BARC-N.L",   -18.8,"JPMorgan",     1200.0, 1),
    ("EVT-051","RIGHTS_ISSUE","1 for 3",  8.50, 12.40, 11.47,  2.97,"UCG-N.MI",    -25.9,"Deutsche Bank",3500.0, 1),
    ("EVT-052","RIGHTS_ISSUE","1 for 2",  0.85,  1.42,  1.24,  0.39,"ALPHA-N.AT",  -31.5,"Piraeus Bank",  800.0, 1),
    ("EVT-053","OPEN_OFFER",  "1 for 10",280.0, 340.0, 334.55, None, None,          -16.3,"UBS",           420.0, 1),
    ("EVT-054","RIGHTS_ISSUE","1 for 4", 180.0, 248.0, 231.25, 51.25,"THYAO-N.IS", -22.1,"Is Yatirim",   2800.0, 1),
    ("EVT-055","RIGHTS_ISSUE","1 for 8", 4200.0,5800.0,5644.0,1444.0,"FSR-N.JO",   -25.6,"RMB",          4500.0, 1),
    ("EVT-056","RIGHTS_ISSUE","1 for 4",  3.20,  5.80,  5.45,  2.25,"ETEL-N.CA",   -41.3,"CIB",          1200.0, 1),
    ("EVT-057","OPEN_OFFER",  "1 for 6",  2.40,  3.25,  3.11,  None, None,          -22.8,"Alpha Bank",    650.0, 1),
]

# ── Merger details ─────────────────────────────────────────────────────────────
MERGERS = [
    # event_id, type, acquirer, acq_ticker, consid_type, cash/sh, share_ratio, curr_price, spread%, court_date, longstop, reg_status, break_risk
    ("EVT-058","SCHEME",  "Emerson Electric Co","EMR",   "CASH",  1850.0,None, 1820.0,  1.65,d(25), d(180),"CLEARED","LOW"),
    ("EVT-059","SCHEME",  "Undisclosed Bidder",  None,   "CASH",  3200.0,None, 3140.0,  1.91,d(40), d(210),"PENDING","MEDIUM"),
    ("EVT-060","SCHEME",  "Ferguson Enterprises","FERG", "CASH",  8500.0,None, 8420.0,  0.95,d(15), d(150),"CLEARED","LOW"),
    ("EVT-061","SCHEME",  "MGM Resorts Intl",   "MGM",  "MIXED", 1200.0,"0.12 MGM per ENT",1180.0,1.69,d(45),d(240),"PENDING","MEDIUM"),
    ("EVT-062","MERGER",  "Haier Group",         None,   "CASH",  42.50, None, 41.80,   1.67,None,  d(180),"PENDING","HIGH"),
    ("EVT-063","EXCHANGE","Parent Company",      None,   "SHARES",None, "1.2 new per old",58.20,None,None, d(120),"PENDING","MEDIUM"),
    ("EVT-064","SCHEME",  "Saudi National Bank", "1180.SR","CASH",18.50,None, 17.80,   3.93,d(50), d(270),"PENDING","HIGH"),
    ("EVT-065","MERGER",  "Internal Restructure",None,  "SHARES",None, "1:1 new division",None,None,None, dp(2),"CLEARED","LOW"),
]

# ── Spinoff details ────────────────────────────────────────────────────────────
SPINOFFS = [
    # event_id, name, ticker, exchange, ratio, sector, est_value, listing_date
    ("EVT-072","GSK Consumer NewCo",   "HLNX.L",  "LSE",       "1 for 5 held","Consumer Healthcare", 42.50, d(45)),
    ("EVT-073","Glencore Coal Ltd",    "COAL.L",  "LSE",       "1 for 3 held","Mining",               8.20,  d(60)),
    ("EVT-074","Siemens Energy NewCo", "SENR.DE", "XETRA",     "1 for 8 held","Energy",              22.40,  d(30)),
    ("EVT-075","Enel Grid SpA",        "GRID.MI", "Borsa Ital","1 for 4 held","Utilities",           18.60,  d(75)),
    ("EVT-076","TotalEnergies Renew",  "TREN.PA", "Euronext",  "1 for 6 held","Renewable Energy",    35.80,  d(65)),
]

# ── Split details ──────────────────────────────────────────────────────────────
SPLITS = [
    # event_id, type, ratio, pre_price, post_price_est
    ("EVT-081","SPLIT",        "10:1",  1340.00, 134.00),
    ("EVT-082","SPLIT",        "5:1",   8450.00,1690.00),
    ("EVT-083","SPLIT",        "2:1",    920.00, 460.00),
    ("EVT-084","CONSOLIDATION","1:10",    92.00, 920.00),
    ("EVT-085","CONSOLIDATION","1:5",     18.40,  92.00),
]

# ── Dutch auction details (reuses tender_details) ──────────────────────────────
DUTCH = [
    # event_id, type, price, low, high, curr, premium%, max_sh, max_val, proration, pror%, odd_thresh, odd_guar
    ("EVT-066","DUTCH_AUCTION", None,3400.0,3700.0,3520.0, None, 15000000, 500.0, 1, 70.0, None, 0),
    ("EVT-067","DUTCH_AUCTION", None,2800.0,3100.0,2920.0, None, 14000000, 400.0, 1, 65.0, None, 0),
    ("EVT-068","DUTCH_AUCTION", None, 185.0, 200.0, 190.0, None,  None,  5000.0, 1, 60.0, None, 0),
    ("EVT-069","DUTCH_AUCTION", None, 290.0, 310.0, 298.0, None,  None,  4000.0, 1, 55.0, None, 0),
    ("EVT-070","DUTCH_AUCTION", None, 640.0, 700.0, 665.0, None, 3000000,2000.0, 1, 65.0, None, 0),
    ("EVT-071","DUTCH_AUCTION", None, 185.0, 205.0, 194.0, None, 8000000,1500.0, 1, 60.0, None, 0),
]

# ── Odd-lot details (reuses tender_details) ────────────────────────────────────
ODD_LOTS = [
    # event_id, type, price, low, high, curr, premium%, max_sh, max_val, proration, pror%, odd_thresh, odd_guar
    ("EVT-077","ODD_LOT", 300.0, None,None, 294.0, 2.04, None, 50.0, 0, None, 99, 1),
    ("EVT-078","ODD_LOT",9200.0, None,None,8980.0, 2.45, None,100.0, 0, None, 99, 1),
    ("EVT-079","ODD_LOT", 165.0, None,None, 161.0, 2.48, None,200.0, 0, None, 99, 1),
    ("EVT-080","ODD_LOT",8800.0, None,None,8620.0, 2.09, None,150.0, 0, None, 99, 1),
]


# ══════════════════════════════════════════════════════════════════════════════
# BUILD DATABASE
# ══════════════════════════════════════════════════════════════════════════════

def build():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"  Removed existing {DB_PATH}")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create schema
    for stmt in SCHEMA.strip().split(";"):
        s = stmt.strip()
        if s:
            c.execute(s)

    # Insert events
    c.executemany("""
        INSERT INTO events(event_id,ticker,company_name,country,currency,
        event_type,event_category,status,announcement_date,ex_date,record_date,
        election_deadline,payment_date,settlement_date,source_url,notes)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, EVENTS)

    # Insert scrip + FX elections
    all_scrip = SCRIP + FX_ELECTIONS
    c.executemany("""
        INSERT INTO scrip_details VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, all_scrip)

    # Insert rights
    c.executemany("""
        INSERT INTO rights_details VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
    """, RIGHTS)

    # Insert tenders + dutch + odd-lots
    all_tenders = TENDERS + DUTCH + ODD_LOTS
    c.executemany("""
        INSERT INTO tender_details VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, all_tenders)

    # Insert mergers
    c.executemany("""
        INSERT INTO merger_details VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
    """, MERGERS)

    # Insert spinoffs
    c.executemany("""
        INSERT INTO spinoff_details VALUES (?,?,?,?,?,?,?,?)
    """, SPINOFFS)

    # Insert splits
    c.executemany("""
        INSERT INTO split_details VALUES (?,?,?,?,?)
    """, SPLITS)

    conn.commit()

    # Summary
    print(f"\n✓ Database built → {DB_PATH}")
    print(f"\n  Event breakdown:")
    for row in c.execute("""
        SELECT event_type, event_category, status, COUNT(*) as n
        FROM events
        GROUP BY event_type, event_category, status
        ORDER BY event_category, event_type
    """):
        print(f"    {row[0]:<28} {row[1]:<25} {row[2]:<10} {row[3]}")

    total    = c.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    live     = c.execute("SELECT COUNT(*) FROM events WHERE status='LIVE'").fetchone()[0]
    upcoming = c.execute("SELECT COUNT(*) FROM events WHERE status='UPCOMING'").fetchone()[0]
    closed   = c.execute("SELECT COUNT(*) FROM events WHERE status='CLOSED'").fetchone()[0]
    print(f"  Total events: {total}")
    print(f"  LIVE:         {live}")
    print(f"  UPCOMING:     {upcoming}")
    print(f"  CLOSED:       {closed}")
    print(f"\n  Countries covered:")
    for row in c.execute("SELECT country, COUNT(*) FROM events GROUP BY country ORDER BY COUNT(*) DESC"):
        print(f"    {row[0]:<25} {row[1]}")

    conn.close()

if __name__ == "__main__":
    build()
