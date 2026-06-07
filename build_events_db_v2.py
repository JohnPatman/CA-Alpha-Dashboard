"""
build_events_db_v2.py
---------------------
200 events across 35+ countries.
NO buybacks (open-market). NO odd-lot offers.
Replaced with: rights issues, CCY elections, tender offers, schemes.

Run:  python3 build_events_db_v2.py
Out:  data/events.db
"""

import sqlite3, os
from datetime import date, timedelta

DB   = "data/events.db"
os.makedirs("data", exist_ok=True)

TODAY = date(2026, 5, 25)
def d(n):  return (TODAY + timedelta(days=n)).isoformat()
def dp(n): return (TODAY - timedelta(days=n)).isoformat()

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    event_id TEXT PRIMARY KEY, ticker TEXT NOT NULL, company_name TEXT NOT NULL,
    country TEXT NOT NULL, currency TEXT NOT NULL, event_type TEXT NOT NULL,
    event_category TEXT NOT NULL, status TEXT NOT NULL,
    announcement_date TEXT, ex_date TEXT, record_date TEXT,
    election_deadline TEXT, payment_date TEXT, settlement_date TEXT,
    source_url TEXT, notes TEXT,
    last_updated TEXT DEFAULT (date('now'))
);
CREATE TABLE IF NOT EXISTS scrip_details (
    event_id TEXT PRIMARY KEY REFERENCES events(event_id),
    cash_amount REAL, cash_currency TEXT, scrip_issue_price REAL,
    scrip_ratio TEXT, dividend_currency_opts TEXT, company_fx_rate REAL,
    market_fx_rate REAL, fx_arbitrage_pct REAL, election_default TEXT,
    withholding_tax_pct REAL DEFAULT 0, scrip_discount_pct REAL, optimal_election TEXT,
    rate_pre_deadline INTEGER DEFAULT 0
    -- rate_pre_deadline: 1 = company announces fixed FX rate before election deadline (genuine arb)
    --                    0 = rate determined at/after deadline (no locked-in arb, currency preference only)
    -- Only set to 1 when you can confirm from the dividend announcement that a fixed rate was published.
    -- Typical 1 candidates: UK-listed mining/resources cos (RIO, BHP, AAL, ANTO), African telecom ADRs (AAF.L)
);
CREATE TABLE IF NOT EXISTS rights_details (
    event_id TEXT PRIMARY KEY REFERENCES events(event_id),
    rights_type TEXT, rights_ratio TEXT, subscription_price REAL,
    current_price REAL, terp REAL, nil_paid_value REAL, nil_paid_ticker TEXT,
    discount_to_terp_pct REAL, underwriter TEXT, gross_proceeds_mn REAL,
    fully_underwritten INTEGER DEFAULT 1
);
CREATE TABLE IF NOT EXISTS tender_details (
    event_id TEXT PRIMARY KEY REFERENCES events(event_id),
    tender_type TEXT, tender_price REAL, tender_price_low REAL,
    tender_price_high REAL, current_price REAL, premium_to_mkt_pct REAL,
    max_shares_sought INTEGER, max_value_mn REAL, proration_expected INTEGER,
    estimated_proration_pct REAL, odd_lot_threshold INTEGER, odd_lot_guaranteed INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS merger_details (
    event_id TEXT PRIMARY KEY REFERENCES events(event_id),
    merger_type TEXT, acquirer TEXT, acquirer_ticker TEXT,
    consideration_type TEXT, cash_per_share REAL, share_ratio TEXT,
    current_price REAL, spread_to_terms_pct REAL, court_sanction_date TEXT,
    long_stop_date TEXT, regulatory_status TEXT, break_risk TEXT
);
CREATE TABLE IF NOT EXISTS spinoff_details (
    event_id TEXT PRIMARY KEY REFERENCES events(event_id),
    spinoff_name TEXT, spinoff_ticker TEXT, spinoff_exchange TEXT,
    distribution_ratio TEXT, spinoff_sector TEXT, estimated_value REAL, listing_date TEXT
);
CREATE TABLE IF NOT EXISTS split_details (
    event_id TEXT PRIMARY KEY REFERENCES events(event_id),
    split_type TEXT, split_ratio TEXT, pre_split_price REAL, post_split_price_est REAL
);
"""

E = [
  # ── UK SCRIP DIVIDENDS (12) ───────────────────────────────────────────────
  ("E001","LMP.L","LondonMetric Property","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(30),dp(14),dp(13),d(5),d(20),d(21),"https://londonmetric.com","Q1 2026 scrip"),
  ("E002","LGEN.L","Legal & General","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(25),dp(10),dp(9),d(8),d(25),d(26),"https://legalandgeneral.com","Final 2025"),
  ("E003","ULVR.L","Unilever PLC","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(20),dp(7),dp(6),d(12),d(30),d(31),"https://unilever.com","Q1 2026"),
  ("E004","HSBA.L","HSBC Holdings","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","UPCOMING",dp(5),d(14),d(15),d(35),d(55),d(56),"https://hsbc.com","2026 interim"),
  ("E005","SHEL.L","Shell PLC","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(28),dp(12),dp(11),d(3),d(18),d(19),"https://shell.com","Q1 2026"),
  ("E006","RIO.L","Rio Tinto PLC","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","UPCOMING",dp(3),d(18),d(19),d(40),d(60),d(61),"https://riotinto.com","2026 interim"),
  ("E007","NG.L","National Grid","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(35),dp(18),dp(17),d(2),d(15),d(16),"https://nationalgrid.com","FY2026 final"),
  ("E008","AV.L","Aviva PLC","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","UPCOMING",dp(7),d(21),d(22),d(42),d(65),d(66),"https://aviva.com","2026 interim"),
  ("E009","GSK.L","GSK PLC","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(22),dp(8),dp(7),d(7),d(22),d(23),"https://gsk.com","Q1 2026"),
  ("E010","PRU.L","Prudential PLC","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(18),dp(5),dp(4),d(10),d(28),d(29),"https://prudentialplc.com","2026 interim"),
  ("E011","MNDI.L","Mondi PLC","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","UPCOMING",dp(4),d(24),d(25),d(46),d(66),d(67),"https://mondigroup.com","2026 interim"),
  ("E012","MNG.L","M&G PLC","UK","GBX","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(20),dp(6),dp(5),d(9),d(26),d(27),"https://mandg.com","2026 final"),

  # ── UK CCY ELECTIONS (6) ──────────────────────────────────────────────────
  ("E013","AAF.L","Airtel Africa","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","LIVE",dp(28),dp(12),dp(11),d(4),d(20),d(21),"https://airtelafrica.com","Q3 FY2026 USD/GBP"),
  ("E014","HSBA.L","HSBC Holdings","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","LIVE",dp(20),dp(7),dp(6),d(12),d(30),d(31),"https://hsbc.com","Q1 2026 USD/GBP"),
  ("E015","STAN.L","Standard Chartered","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","LIVE",dp(22),dp(8),dp(7),d(8),d(24),d(25),"https://sc.com","2026 interim USD/GBP"),
  ("E016","AZN.L","AstraZeneca PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","LIVE",dp(24),dp(9),dp(8),d(6),d(22),d(23),"https://astrazeneca.com","Q1 2026 USD/GBP"),
  ("E017","EXPN.L","Experian PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","LIVE",dp(18),dp(5),dp(4),d(9),d(26),d(27),"https://experianplc.com","FY2026 USD/GBP"),
  ("E018","CCH.L","Coca-Cola HBC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","LIVE",dp(25),dp(10),dp(9),d(5),d(21),d(22),"https://coca-colahbc.com","2026 EUR/GBP"),

  # ── UK RIGHTS / OPEN OFFERS (5) ───────────────────────────────────────────
  ("E019","BT-A.L","BT Group PLC","UK","GBX","rights_issue","VOLUNTARY","LIVE",dp(15),d(5),d(6),d(20),d(35),d(40),"https://bt.com","1 for 3 at 95p"),
  ("E020","VOD.L","Vodafone Group","UK","GBX","open_offer","VOLUNTARY","UPCOMING",dp(3),d(18),d(19),d(35),d(50),d(55),"https://vodafone.com","Open offer at 62p"),
  ("E021","NWG.L","NatWest Group","UK","GBX","open_offer","VOLUNTARY","LIVE",dp(12),d(3),d(4),d(18),d(33),d(38),"https://natwestgroup.com","Open offer 280p"),
  ("E022","LLOY.L","Lloyds Banking Group","UK","GBX","rights_issue","VOLUNTARY","UPCOMING",dp(4),d(22),d(23),d(40),d(58),d(63),"https://lloydsbankinggroup.com","1 for 6 at 38p"),
  ("E023","BARC.L","Barclays PLC","UK","GBX","rights_issue","VOLUNTARY","CLOSED",dp(60),dp(45),dp(44),dp(25),dp(10),dp(5),"https://barclays.com","CLOSED 1 for 5 at 140p"),

  # ── UK SCHEMES / TENDERS (7) ──────────────────────────────────────────────
  ("E024","SMIN.L","Smiths Group PLC","UK","GBX","scheme_of_arrangement","VOLUNTARY","LIVE",dp(45),None,dp(10),d(25),d(40),d(45),"https://smiths.com","Recommended acquisition"),
  ("E025","BNZL.L","Bunzl PLC","UK","GBX","scheme_of_arrangement","VOLUNTARY","UPCOMING",dp(8),None,d(15),d(40),d(60),d(65),"https://bunzl.com","Recommended cash offer"),
  ("E026","DCC.L","DCC PLC","UK","GBX","scheme_of_arrangement","VOLUNTARY","LIVE",dp(55),None,dp(20),d(15),d(30),d(35),"https://dcc.ie","Recommended acquisition"),
  ("E027","CTEC.L","Convatec Group","UK","GBX","tender_offer","VOLUNTARY","LIVE",dp(18),None,dp(5),d(14),None,d(20),"https://convatecgroup.com","Share tender"),
  ("E036","RTO.L","Rentokil Initial PLC","UK","GBX","tender_offer","VOLUNTARY","LIVE",dp(14),None,dp(3),d(16),None,d(22),"https://rentokininitial.com","600m fixed price tender"),
  ("E037","EXPN.L","Experian PLC","UK","GBX","tender_offer","VOLUNTARY","UPCOMING",dp(4),None,d(14),d(34),None,d(40),"https://experianplc.com","750m tender offer"),
  ("E038","AZN.L","AstraZeneca PLC","UK","GBX","tender_offer","VOLUNTARY","LIVE",dp(20),None,dp(6),d(14),None,d(20),"https://astrazeneca.com","2bn accelerated tender"),

  # ── EUROPE SCRIP DIVIDENDS (15) ───────────────────────────────────────────
  ("E066","NESN.SW","Nestle SA","Switzerland","CHF","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(30),dp(14),dp(13),d(4),d(20),d(21),"https://nestle.com","AGM 2026"),
  ("E067","SAN.MC","Banco Santander","Spain","EUR","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(25),dp(10),dp(9),d(6),d(22),d(23),"https://santander.com","Dividendo Eleccion Q2"),
  ("E068","BBVA.MC","BBVA SA","Spain","EUR","scrip_dividend","MANDATORY_WITH_CHOICE","UPCOMING",dp(4),d(20),d(21),d(45),d(65),d(66),"https://bbva.com","Dividendo Eleccion 2026"),
  ("E069","ENEL.MI","Enel SpA","Italy","EUR","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(20),dp(6),dp(5),d(9),d(25),d(26),"https://enel.com","2026 interim"),
  ("E070","ISP.MI","Intesa Sanpaolo","Italy","EUR","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(15),dp(4),dp(3),d(11),d(28),d(29),"https://intesasanpaolo.com","2026 scrip"),
  ("E071","ABI.BR","AB InBev SA","Belgium","EUR","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(32),dp(16),dp(15),d(2),d(18),d(19),"https://ab-inbev.com","2026 interim"),
  ("E072","HEIA.AS","Heineken NV","Netherlands","EUR","scrip_dividend","MANDATORY_WITH_CHOICE","UPCOMING",dp(5),d(22),d(23),d(44),d(65),d(66),"https://theheinekencompany.com","2026 final"),
  ("E073","OR.PA","L'Oreal SA","France","EUR","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(18),dp(5),dp(4),d(8),d(25),d(26),"https://loreal-finance.com","AGM 2026"),
  ("E074","IBE.MC","Iberdrola SA","Spain","EUR","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(22),dp(8),dp(7),d(7),d(24),d(25),"https://iberdrola.com","Scrip 2026"),
  ("E075","ENI.MI","ENI SpA","Italy","EUR","scrip_dividend","MANDATORY_WITH_CHOICE","UPCOMING",dp(6),d(28),d(29),d(50),d(70),d(71),"https://eni.com","Q2 2026"),
  ("E076","KBC.BR","KBC Group NV","Belgium","EUR","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(20),dp(7),dp(6),d(8),d(25),d(26),"https://kbc.com","2026 interim"),
  ("E077","NOVN.SW","Novartis AG","Switzerland","CHF","scrip_dividend","MANDATORY_WITH_CHOICE","UPCOMING",dp(4),d(30),d(31),d(52),d(72),d(73),"https://novartis.com","2026 AGM"),
  ("E078","ROG.SW","Roche Holding AG","Switzerland","CHF","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(28),dp(13),dp(12),d(5),d(22),d(23),"https://roche.com","2026 annual"),
  ("E079","BNP.PA","BNP Paribas SA","France","EUR","scrip_dividend","MANDATORY_WITH_CHOICE","UPCOMING",dp(3),d(25),d(26),d(47),d(67),d(68),"https://invest.bnpparibas.com","2026 scrip"),
  ("E080","DTE.DE","Deutsche Telekom","Germany","EUR","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(16),dp(3),dp(2),d(12),d(30),d(31),"https://telekom.com","2026 AGM"),

  # ── EUROPE CCY ELECTIONS (5) ──────────────────────────────────────────────
  ("E081","EQNR.OL","Equinor ASA","Norway","NOK","fx_election","MANDATORY_WITH_CHOICE","LIVE",dp(22),dp(8),dp(7),d(7),d(23),d(24),"https://equinor.com","Q1 2026 USD/NOK"),
  ("E082","GLEN.L","Glencore PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","UPCOMING",dp(6),d(30),d(31),d(55),d(75),d(76),"https://glencore.com","2026 USD/GBP"),
  ("E083","AAL.L","Anglo American","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","LIVE",dp(30),dp(14),dp(13),d(3),d(19),d(20),"https://angloamerican.com","2026 USD/GBP"),
  ("E084","CFR.SW","Richemont SA","Switzerland","CHF","fx_election","MANDATORY_WITH_CHOICE","LIVE",dp(18),dp(5),dp(4),d(10),d(28),d(29),"https://richemont.com","2026 EUR/CHF/GBP"),
  ("E085","ABB.BR","Al Baraka Banking","Bahrain","BHD","fx_election","MANDATORY_WITH_CHOICE","UPCOMING",dp(4),d(22),d(23),d(44),d(65),d(66),"https://albaraka.com","USD/BHD 2026"),

  # ── EUROPE RIGHTS / OPEN OFFERS (10) ──────────────────────────────────────
  ("E086","UCG.MI","UniCredit SpA","Italy","EUR","rights_issue","VOLUNTARY","UPCOMING",dp(4),d(22),d(23),d(40),d(58),d(63),"https://unicreditgroup.eu","Capital raise"),
  ("E087","ALPHA.AT","Alpha Bank SA","Greece","EUR","rights_issue","VOLUNTARY","LIVE",dp(20),d(8),d(9),d(25),d(42),d(47),"https://alpha.gr","1 for 2 at 0.85"),
  ("E088","TPEIR.AT","Piraeus Holdings","Greece","EUR","open_offer","VOLUNTARY","UPCOMING",dp(4),d(20),d(21),d(38),d(56),d(61),"https://piraeusholdings.gr","Open offer 2.40"),
  ("E089","ETE.AT","National Bank of Greece","Greece","EUR","rights_issue","VOLUNTARY","LIVE",dp(18),d(6),d(7),d(22),d(40),d(45),"https://nbg.gr","1 for 3 at 4.20"),
  ("E090","DBK.DE","Deutsche Bank AG","Germany","EUR","rights_issue","VOLUNTARY","UPCOMING",dp(5),d(28),d(29),d(48),d(68),d(73),"https://investor.db.com","Capital increase"),
  ("E091","BCP.LS","BCP Portugal","Portugal","EUR","rights_issue","VOLUNTARY","LIVE",dp(22),d(6),d(7),d(24),d(42),d(47),"https://millenniumbcp.pt","1 for 4 at 0.14"),
  ("E092","PKO.WA","PKO Bank Polski","Poland","PLN","rights_issue","VOLUNTARY","UPCOMING",dp(6),d(30),d(31),d(52),d(72),d(77),"https://pkobp.pl","Capital increase"),
  ("E093","OTP.BD","OTP Bank Nyrt","Hungary","HUF","open_offer","VOLUNTARY","LIVE",dp(15),d(5),d(6),d(20),d(38),d(43),"https://otpbank.hu","Open offer HUF 14,500"),
  ("R022","BNP.PA","BNP Paribas SA","France","EUR","rights_issue","VOLUNTARY","LIVE",dp(18),d(7),d(8),d(24),d(42),d(47),"https://invest.bnpparibas.com","1 for 8 at 52"),
  ("R023","GLE.PA","Societe Generale SA","France","EUR","rights_issue","VOLUNTARY","UPCOMING",dp(3),d(25),d(26),d(46),d(66),d(71),"https://societegenerale.com","Capital increase 2bn"),

  # ── EUROPE SCHEMES / MERGERS / TENDERS (10) ───────────────────────────────
  ("E094","SAP.DE","SAP SE","Germany","EUR","dutch_auction","VOLUNTARY","LIVE",dp(22),None,dp(6),d(14),None,d(20),"https://sap.com","1.5bn dutch auction"),
  ("E095","TTE.PA","TotalEnergies SE","France","EUR","dutch_auction","VOLUNTARY","LIVE",dp(35),None,None,d(95),None,None,"https://totalenergies.com","2bn Q2 dutch"),
  ("E096","MC.PA","LVMH SE","France","EUR","dutch_auction","VOLUNTARY","UPCOMING",dp(6),None,d(18),d(40),None,d(46),"https://lvmh.com","2bn dutch auction"),
  ("E097","SIE.DE","Siemens AG","Germany","EUR","dutch_auction","VOLUNTARY","LIVE",dp(22),None,dp(6),d(14),None,d(20),"https://siemens.com","1.5bn dutch"),
  ("E098","NOVO-B.CO","Novo Nordisk","Denmark","DKK","dutch_auction","VOLUNTARY","LIVE",dp(50),None,None,d(130),None,None,"https://novonordisk.com","2026 dutch auction"),
  ("E099","NESN.SW","Nestle SA","Switzerland","CHF","dutch_auction","VOLUNTARY","LIVE",dp(30),None,None,d(90),None,None,"https://nestle.com","CHF 5bn dutch"),
  ("E100","VWS.CO","Vestas Wind Systems","Denmark","DKK","rights_issue","VOLUNTARY","LIVE",dp(18),d(5),d(6),d(22),d(40),d(45),"https://vestas.com","1 for 5 at DKK 95"),
  ("E101","SISE.IS","Sise ve Cam","Turkey","TRY","merger","VOLUNTARY","LIVE",dp(25),None,dp(3),d(18),d(35),d(40),"https://sisecam.com","Strategic merger"),
  ("E102","ARCLK.IS","Arcelik AS","Turkey","TRY","merger","VOLUNTARY","LIVE",dp(30),None,dp(5),d(20),d(38),d(43),"https://arcelikglobal.com","Merger consideration"),
  ("E103","THYAO.IS","Turkish Airlines","Turkey","TRY","rights_issue","VOLUNTARY","LIVE",dp(18),d(5),d(6),d(22),d(38),d(43),"https://turkishairlines.com","Capital increase"),

  # ── AUSTRALIA SCRIP (8) ───────────────────────────────────────────────────
  ("E106","CBA.AX","Commonwealth Bank","Australia","AUD","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(28),dp(12),dp(11),d(5),d(22),d(23),"https://commbank.com.au","DRP H1 2026"),
  ("E107","WBC.AX","Westpac Banking","Australia","AUD","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(22),dp(8),dp(7),d(8),d(25),d(26),"https://westpac.com.au","DRP H1 2026"),
  ("E108","NAB.AX","National Australia Bank","Australia","AUD","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(18),dp(5),dp(4),d(10),d(28),d(29),"https://nab.com.au","DRP 2026 interim"),
  ("E109","ANZ.AX","ANZ Banking Group","Australia","AUD","scrip_dividend","MANDATORY_WITH_CHOICE","UPCOMING",dp(4),d(25),d(26),d(47),d(67),d(68),"https://anz.com.au","DRP H1 2026"),
  ("E110","WDS.AX","Woodside Energy","Australia","AUD","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(20),dp(6),dp(5),d(9),d(26),d(27),"https://woodside.com","2026 Q1 DRP"),
  ("E111","TLS.AX","Telstra Group","Australia","AUD","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(15),dp(4),dp(3),d(11),d(29),d(30),"https://telstra.com.au","H1 2026 DRP"),
  ("E112","CSL.AX","CSL Ltd","Australia","AUD","scrip_dividend","MANDATORY_WITH_CHOICE","UPCOMING",dp(3),d(30),d(31),d(52),d(72),d(73),"https://csl.com","2026 interim DRP"),
  ("E113","BHP.AX","BHP Group Ltd","Australia","AUD","scrip_dividend","MANDATORY_WITH_CHOICE","UPCOMING",dp(5),d(20),d(21),d(42),d(62),d(63),"https://bhp.com","2026 interim DRP"),

  # ── AUSTRALIA CCY ELECTIONS (3) ───────────────────────────────────────────
  ("E114","RIO.AX","Rio Tinto Ltd","Australia","AUD","fx_election","MANDATORY_WITH_CHOICE","UPCOMING",dp(3),d(18),d(19),d(40),d(60),d(61),"https://riotinto.com","USD/AUD election"),
  ("E115","BHP.AX","BHP Group Ltd","Australia","AUD","fx_election","MANDATORY_WITH_CHOICE","LIVE",dp(20),dp(6),dp(5),d(10),d(28),d(29),"https://bhp.com","USD/AUD/GBP election"),
  ("E116","AMC.AX","Amcor PLC","Australia","AUD","fx_election","MANDATORY_WITH_CHOICE","LIVE",dp(18),dp(5),dp(4),d(9),d(26),d(27),"https://amcor.com","USD/AUD election"),

  # ── AUSTRALIA RIGHTS / SCHEMES / SPLITS (7) ───────────────────────────────
  ("E117","QBE.AX","QBE Insurance Group","Australia","AUD","rights_issue","VOLUNTARY","LIVE",dp(15),d(5),d(6),d(20),d(38),d(43),"https://qbe.com","1 for 5 at AUD 14.50"),
  ("E118","ORG.AX","Origin Energy","Australia","AUD","scheme_of_arrangement","VOLUNTARY","LIVE",dp(40),None,dp(8),d(22),d(40),d(45),"https://originenergy.com.au","Recommended cash scheme"),
  ("E119","STO.AX","Santos Ltd","Australia","AUD","scheme_of_arrangement","VOLUNTARY","UPCOMING",dp(8),None,d(20),d(45),d(65),d(70),"https://santos.com","Recommended merger"),
  ("E123","COH.AX","Cochlear Ltd","Australia","AUD","stock_split","MANDATORY","UPCOMING",dp(8),d(22),d(23),None,None,None,"https://cochlear.com","2:1 split"),
  ("E124","XRO.AX","Xero Ltd","Australia","AUD","stock_split","MANDATORY","UPCOMING",dp(5),d(28),d(29),None,None,None,"https://xero.com","5:1 split"),
  ("E125","CSL.AX","CSL Ltd","Australia","AUD","spinoff","MANDATORY","UPCOMING",dp(10),d(40),d(41),None,d(55),d(56),"https://csl.com","Vifor spinoff"),
  ("R017","IAG.L","Intl Consolidated Airlines","UK","GBX","rights_issue","VOLUNTARY","LIVE",dp(18),d(6),d(7),d(22),d(40),d(45),"https://iairgroup.com","1 for 4 at 145p"),

  # ── HK / CHINA (18) ───────────────────────────────────────────────────────
  ("E126","0939.HK","China Construction Bank","Hong Kong","HKD","rights_issue","VOLUNTARY","LIVE",dp(18),d(6),d(7),d(22),d(40),d(45),"https://ccb.com","A+H rights issue"),
  ("E127","1398.HK","ICBC","Hong Kong","HKD","rights_issue","VOLUNTARY","UPCOMING",dp(5),d(25),d(26),d(46),d(66),d(71),"https://icbc-ltd.com","Capital increase"),
  ("E128","0941.HK","China Mobile","Hong Kong","HKD","dutch_auction","VOLUNTARY","LIVE",dp(30),None,None,d(90),None,None,"https://chinamobileltd.com","HKD 10bn dutch"),
  ("E129","9988.HK","Alibaba Group","Hong Kong","HKD","dutch_auction","VOLUNTARY","LIVE",dp(45),None,None,d(105),None,None,"https://alibabagroup.com","12bn dutch auction"),
  ("E130","0700.HK","Tencent Holdings","Hong Kong","HKD","dutch_auction","VOLUNTARY","LIVE",dp(38),None,None,d(98),None,None,"https://tencent.com","HKD 100bn dutch"),
  ("E131","1211.HK","BYD Co Ltd","Hong Kong","HKD","rights_issue","VOLUNTARY","UPCOMING",dp(6),d(28),d(29),d(50),d(70),d(75),"https://bydglobal.com","A+H capital raise"),
  ("E132","1810.HK","Xiaomi Corp","Hong Kong","HKD","stock_split","MANDATORY","UPCOMING",dp(8),d(20),d(21),None,None,None,"https://ir.mi.com","5:1 stock split"),
  ("E133","0002.HK","CLP Holdings","Hong Kong","HKD","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(25),dp(10),dp(9),d(6),d(22),d(23),"https://clpgroup.com","Scrip 2026"),
  ("E134","0006.HK","Power Assets","Hong Kong","HKD","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(20),dp(7),dp(6),d(8),d(24),d(25),"https://powerassets.com","2026 interim scrip"),
  ("E135","0823.HK","Link REIT","Hong Kong","HKD","scrip_dividend","MANDATORY_WITH_CHOICE","UPCOMING",dp(4),d(22),d(23),d(44),d(64),d(65),"https://linkreit.com","2026 scrip"),
  ("E136","0001.HK","CK Hutchison","Hong Kong","HKD","spinoff","MANDATORY","UPCOMING",dp(12),d(45),d(46),None,d(60),d(61),"https://ckh.com.hk","Port ops spinoff"),
  ("E137","0019.HK","Swire Pacific","Hong Kong","HKD","demerger","MANDATORY","UPCOMING",dp(8),d(50),d(51),None,d(65),d(66),"https://swire.com","Aviation demerger"),
  ("E138","9618.HK","JD.com Inc","Hong Kong","HKD","spinoff","MANDATORY","LIVE",dp(20),d(15),d(16),None,d(30),d(31),"https://jd.com","JD Health spinoff"),
  ("E139","3690.HK","Meituan","Hong Kong","HKD","rights_issue","VOLUNTARY","UPCOMING",dp(5),d(30),d(31),d(52),d(72),d(77),"https://meituan.com","Capital raise"),
  ("E141","600519.SS","Kweichow Moutai","China","CNY","stock_split","MANDATORY","UPCOMING",dp(6),d(25),d(26),None,None,None,"https://moutai.com","10:1 split"),
  ("E142","300750.SZ","CATL","China","CNY","rights_issue","VOLUNTARY","LIVE",dp(18),d(8),d(9),d(25),d(45),d(50),"https://catl.com","1 for 10 at CNY 180"),
  ("E186","0003.HK","HK & China Gas","Hong Kong","HKD","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(20),dp(7),dp(6),d(8),d(25),d(26),"https://hkcg.com","2026 interim scrip"),
  ("E187","0011.HK","Hang Seng Bank","Hong Kong","HKD","scrip_dividend","MANDATORY_WITH_CHOICE","UPCOMING",dp(4),d(22),d(23),d(44),d(65),d(66),"https://hangseng.com","2026 scrip"),

  # ── JAPAN (10) ────────────────────────────────────────────────────────────
  ("E144","7203.T","Toyota Motor Corp","Japan","JPY","tender_offer","VOLUNTARY","LIVE",dp(22),None,dp(7),d(13),None,d(19),"https://toyota.co.jp","JPY 500bn tender"),
  ("E145","6758.T","Sony Group Corp","Japan","JPY","dutch_auction","VOLUNTARY","LIVE",dp(30),None,None,d(90),None,None,"https://sony.com","JPY 200bn dutch"),
  ("E146","9984.T","SoftBank Group","Japan","JPY","dutch_auction","VOLUNTARY","LIVE",dp(25),None,None,d(85),None,None,"https://softbank.jp","JPY 500bn dutch"),
  ("E147","8306.T","MUFG","Japan","JPY","tender_offer","VOLUNTARY","UPCOMING",dp(5),None,None,d(65),None,None,"https://mufg.jp","JPY 300bn tender"),
  ("E148","8316.T","SMFG","Japan","JPY","rights_issue","VOLUNTARY","UPCOMING",dp(5),d(30),d(31),d(52),d(72),d(77),"https://smfg.co.jp","Capital increase"),
  ("E149","6861.T","Keyence Corp","Japan","JPY","stock_split","MANDATORY","UPCOMING",dp(8),d(22),d(23),None,None,None,"https://keyence.co.jp","5:1 split"),
  ("E150","9983.T","Fast Retailing","Japan","JPY","stock_split","MANDATORY","UPCOMING",dp(5),d(30),d(31),None,None,None,"https://fastretailing.com","3:1 split"),
  ("E151","7267.T","Honda Motor Co","Japan","JPY","merger","VOLUNTARY","LIVE",dp(45),None,dp(10),d(20),d(40),d(45),"https://honda.com","Honda-Nissan merger"),
  ("E152","7201.T","Nissan Motor Co","Japan","JPY","scheme_of_arrangement","VOLUNTARY","LIVE",dp(45),None,dp(10),d(20),d(40),d(45),"https://nissan-global.com","Honda-Nissan scheme"),
  ("E153","4502.T","Takeda Pharma","Japan","JPY","rights_issue","VOLUNTARY","UPCOMING",dp(6),d(28),d(29),d(50),d(70),d(75),"https://takeda.com","Capital increase"),

  # ── MIDDLE EAST (12) ──────────────────────────────────────────────────────
  ("E154","2222.SR","Saudi Aramco","Saudi Arabia","SAR","tender_offer","VOLUNTARY","LIVE",dp(18),None,dp(5),d(15),None,d(21),"https://aramco.com","SAR 20bn fixed tender"),
  ("E155","1120.SR","Al Rajhi Bank","Saudi Arabia","SAR","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(20),dp(7),dp(6),d(8),d(25),d(26),"https://alrajhibank.com.sa","Q1 2026 scrip"),
  ("E156","1180.SR","Saudi National Bank","Saudi Arabia","SAR","rights_issue","VOLUNTARY","UPCOMING",dp(5),d(28),d(29),d(50),d(70),d(75),"https://alahli.com","Capital increase"),
  ("E157","7010.SR","Saudi Telecom STC","Saudi Arabia","SAR","tender_offer","VOLUNTARY","LIVE",dp(28),None,None,d(88),None,None,"https://stc.com.sa","SAR 5bn tender"),
  ("E158","FAB.AD","First Abu Dhabi Bank","UAE","AED","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(22),dp(8),dp(7),d(7),d(24),d(25),"https://bankfab.com","2026 scrip"),
  ("E159","EMAAR.DU","Emaar Properties","UAE","AED","rights_issue","VOLUNTARY","UPCOMING",dp(4),d(25),d(26),d(46),d(66),d(71),"https://emaar.com","1 for 5 at AED 4.20"),
  ("E160","ETISALAT.AD","e& (Etisalat)","UAE","AED","tender_offer","VOLUNTARY","LIVE",dp(30),None,None,d(90),None,None,"https://etisalat.com","AED 3bn tender"),
  ("E161","QNBK.QA","Qatar National Bank","Qatar","QAR","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(18),dp(5),dp(4),d(10),d(28),d(29),"https://qnb.com","Q1 2026 scrip"),
  ("E162","ORDS.QA","Ooredoo QSC","Qatar","QAR","rights_issue","VOLUNTARY","UPCOMING",dp(6),d(30),d(31),d(52),d(72),d(77),"https://ooredoo.com","Capital increase"),
  ("E163","NBK.KW","National Bank of Kuwait","Kuwait","KWD","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(25),dp(10),dp(9),d(5),d(22),d(23),"https://nbk.com","2026 scrip"),
  ("E164","POLI.TA","Bank Hapoalim","Israel","ILS","rights_issue","VOLUNTARY","UPCOMING",dp(5),d(25),d(26),d(46),d(66),d(71),"https://bankhapoalim.co.il","Capital increase"),
  ("E165","NICE.TA","NICE Ltd","Israel","ILS","tender_offer","VOLUNTARY","LIVE",dp(22),None,None,d(82),None,None,"https://nice.com","500m tender"),

  # ── AFRICA (12) ───────────────────────────────────────────────────────────
  ("E166","NPN.JO","Naspers Ltd","South Africa","ZAR","scrip_dividend","MANDATORY_WITH_CHOICE","UPCOMING",dp(6),d(25),d(26),d(50),d(70),d(71),"https://naspers.com","FY2026 final"),
  ("E167","MTN.JO","MTN Group Ltd","South Africa","ZAR","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(28),dp(12),dp(11),d(4),d(20),d(21),"https://mtn.com","H1 2026 scrip"),
  ("E168","FSR.JO","FirstRand Ltd","South Africa","ZAR","rights_issue","VOLUNTARY","UPCOMING",dp(5),d(28),d(29),d(48),d(68),d(73),"https://firstrand.co.za","1 for 8 rights"),
  ("E169","BHP.JO","BHP Group JSE","South Africa","ZAR","fx_election","MANDATORY_WITH_CHOICE","LIVE",dp(20),dp(6),dp(5),d(10),d(28),d(29),"https://bhp.com","USD/ZAR/GBP election"),
  ("E170","GFI.JO","Gold Fields Ltd","South Africa","ZAR","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(18),dp(5),dp(4),d(9),d(26),d(27),"https://goldfields.com","2026 interim DRP"),
  ("E171","SSW.JO","Sibanye Stillwater","South Africa","ZAR","rights_issue","VOLUNTARY","LIVE",dp(15),d(5),d(6),d(20),d(38),d(43),"https://sibanyestillwater.com","1 for 4 at ZAR 18"),
  ("E172","MTN.JO","MTN Group","South Africa","ZAR","tender_offer","VOLUNTARY","LIVE",dp(30),None,None,d(90),None,None,"https://mtn.com","ZAR 3bn tender"),
  ("E173","COMI.CA","CIB Egypt","Egypt","EGP","rights_issue","VOLUNTARY","LIVE",dp(22),d(6),d(7),d(24),d(42),d(47),"https://cibeg.com","Capital increase"),
  ("E174","ETEL.CA","Telecom Egypt","Egypt","EGP","rights_issue","VOLUNTARY","LIVE",dp(18),d(8),d(9),d(26),d(45),d(50),"https://telecomegypt.com.eg","1 for 4"),
  ("E175","IAM.CS","Maroc Telecom","Morocco","MAD","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(25),dp(10),dp(9),d(5),d(22),d(23),"https://iam.ma","2026 dividend option"),
  ("E176","DANGCEM.LG","Dangote Cement","Nigeria","NGN","scrip_dividend","MANDATORY_WITH_CHOICE","UPCOMING",dp(4),d(28),d(29),d(50),d(70),d(75),"https://dangote.com","2026 scrip"),
  ("E177","SCOM.NR","Safaricom PLC","Kenya","KES","rights_issue","VOLUNTARY","UPCOMING",dp(6),d(30),d(31),d(52),d(72),d(77),"https://safaricom.co.ke","Capital increase"),

  # ── NORDIC (5) ────────────────────────────────────────────────────────────
  ("E178","NOVO-B.CO","Novo Nordisk","Denmark","DKK","stock_split","MANDATORY","CLOSED",dp(60),dp(45),dp(44),None,None,None,"https://novonordisk.com","2:1 split CLOSED"),
  ("E179","VWS.CO","Vestas Wind Systems","Denmark","DKK","tender_offer","VOLUNTARY","LIVE",dp(14),None,dp(3),d(16),None,d(22),"https://vestas.com","DKK 2bn tender"),
  ("E180","EQNR.OL","Equinor ASA","Norway","NOK","rights_issue","VOLUNTARY","LIVE",dp(18),d(6),d(7),d(22),d(40),d(45),"https://equinor.com","NOK 5bn rights"),
  ("E181","NHY.OL","Norsk Hydro ASA","Norway","NOK","rights_issue","VOLUNTARY","UPCOMING",dp(5),d(25),d(26),d(46),d(66),d(71),"https://hydro.com","NOK 5bn capital"),
  ("E182","ATCO-A.ST","Atlas Copco AB","Sweden","SEK","tender_offer","VOLUNTARY","LIVE",dp(25),None,None,d(85),None,None,"https://atlascopcogroup.com","SEK 10bn tender"),

  # ── ADDITIONAL (18) ───────────────────────────────────────────────────────
  ("E185","NEE","NextEra Energy","US","USD","spinoff","MANDATORY","UPCOMING",dp(8),d(45),d(46),None,d(60),d(61),"https://nexteraenergy.com","Energy Resources spinoff"),
  ("E188","LUMI.TA","Bank Leumi","Israel","ILS","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(18),dp(5),dp(4),d(9),d(26),d(27),"https://bankleumi.co.il","Q1 2026 scrip"),
  ("E189","AUB.BH","Ahli United Bank","Bahrain","BHD","rights_issue","VOLUNTARY","UPCOMING",dp(6),d(30),d(31),d(52),d(72),d(77),"https://ahliunited.com","Capital increase"),
  ("E190","MOL.BD","MOL Group","Hungary","HUF","merger","VOLUNTARY","LIVE",dp(22),None,None,d(82),None,None,"https://mol.hu","Strategic acquisition"),
  ("E191","CEZ.PR","CEZ AS","Czech Republic","CZK","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(20),dp(7),dp(6),d(8),d(25),d(26),"https://cez.cz","2026 AGM dividend"),
  ("E192","SNP.RO","OMV Petrom SA","Romania","RON","rights_issue","VOLUNTARY","UPCOMING",dp(4),d(25),d(26),d(46),d(66),d(71),"https://omvpetrom.com","Capital increase"),
  ("E193","2082.SR","ACWA Power","Saudi Arabia","SAR","rights_issue","VOLUNTARY","LIVE",dp(18),d(6),d(7),d(22),d(42),d(47),"https://acwapower.com","1 for 4 capital raise"),
  ("E194","INGA.AS","ING Groep NV","Netherlands","EUR","rights_issue","VOLUNTARY","LIVE",dp(28),d(8),d(9),d(26),d(44),d(49),"https://ing.com","1 for 10 at 12.80"),
  ("E195","SHB-A.ST","Svenska Handelsbanken","Sweden","SEK","rights_issue","VOLUNTARY","UPCOMING",dp(5),d(28),d(29),d(50),d(70),d(75),"https://handelsbanken.se","SEK 15bn rights"),
  ("E196","MOWI.OL","Mowi ASA","Norway","NOK","scrip_dividend","MANDATORY_WITH_CHOICE","LIVE",dp(22),dp(8),dp(7),d(7),d(24),d(25),"https://mowi.com","2026 DRP"),
  ("E197","GAW.L","Games Workshop","UK","GBX","stock_split","MANDATORY","LIVE",dp(25),d(5),d(6),None,None,None,"https://games-workshop.com","5:1 split"),
  ("E198","EZJ.L","EasyJet PLC","UK","GBX","consolidation","MANDATORY","UPCOMING",dp(6),d(25),d(26),None,None,None,"https://corporate.easyjet.com","1:10 consolidation"),
  ("E199","BAYN.DE","Bayer AG","Germany","EUR","consolidation","MANDATORY","LIVE",dp(18),d(8),d(9),None,None,None,"https://investor.bayer.com","1:5 consolidation"),
  ("E200","KBC.BR","KBC Group","Belgium","EUR","scheme_of_arrangement","VOLUNTARY","UPCOMING",dp(7),None,d(22),d(48),d(68),d(73),"https://kbc.com","Recommended acquisition"),
  ("R016","BARC.L","Barclays PLC","UK","GBX","rights_issue","VOLUNTARY","LIVE",dp(15),d(5),d(6),d(20),d(38),d(43),"https://barclays.com","1 for 6 at 185p"),
  ("R019","EUROB.AT","Eurobank Ergasias","Greece","EUR","rights_issue","VOLUNTARY","UPCOMING",dp(4),d(28),d(29),d(48),d(66),d(71),"https://eurobank.gr","Capital increase 800m"),
  ("R024","CBK.DE","Commerzbank AG","Germany","EUR","rights_issue","VOLUNTARY","LIVE",dp(20),d(8),d(9),d(26),d(44),d(49),"https://commerzbank.com","1 for 5 at 11.50"),
  ("R033","WTB.L","Whitbread PLC","UK","GBX","scheme_of_arrangement","VOLUNTARY","LIVE",dp(35),None,dp(8),d(22),d(40),d(45),"https://whitbread.co.uk","Recommended cash offer"),
]

# ── SCRIP DETAILS ─────────────────────────────────────────────────────────────
SCRIP = [
  ("E001",3.05,"GBP",181.80,"1 per 59","GBP",None,None,None,"CASH",0,-1.47,"CASH",0),
  ("E002",5.84,"GBP",240.00,"1 per 41","GBP",None,None,None,"CASH",0,-0.83,"CASH",0),
  ("E003",43.50,"GBP",4120.00,"1 per 94","GBP",None,None,None,"CASH",0,0.24,"SCRIP",0),
  ("E004",0.10,"USD",None,None,"GBP|USD",0.7617,0.7402,2.91,"CASH",0,None,"GBP",0),
  ("E005",34.00,"USD",2465.00,"1 per 72","GBP|USD",0.7920,0.7750,2.19,"CASH",0,-0.62,"CASH",0),
  ("E006",1.77,"USD",None,None,"GBP|USD|AUD",0.7850,0.7750,1.29,"CASH",0,None,"GBP",0),
  ("E007",17.40,"GBP",1058.00,"1 per 60","GBP",None,None,None,"CASH",0,0.38,"SCRIP",0),
  ("E008",22.50,"GBP",480.00,"1 per 21","GBP",None,None,None,"CASH",0,-0.42,"CASH",0),
  ("E009",16.25,"GBP",1890.00,"1 per 116","GBP",None,None,None,"CASH",0,0.15,"SCRIP",0),
  ("E010",5.90,"USD",None,None,"GBP|USD|HKD",0.7820,0.7750,0.90,"CASH",0,None,"GBP",0),
  ("E011",0.15,"EUR",None,None,"GBP|EUR|ZAR",0.8510,0.8480,0.37,"CASH",0,None,"GBP",0),
  ("E012",5.80,"GBP",292.00,"1 per 50","GBP",None,None,None,"CASH",0,-0.55,"CASH",0),
  ("E013",0.0284,"USD",None,None,"GBP|USD",0.7617,0.7402,2.91,"CASH",0,None,"GBP",0),
  ("E014",0.1000,"USD",None,None,"GBP|USD",0.7820,0.7750,0.90,"CASH",0,None,"GBP",0),
  ("E015",0.0720,"USD",None,None,"GBP|USD",0.7900,0.7750,1.94,"CASH",0,None,"GBP",0),
  ("E016",1.0200,"USD",None,None,"GBP|USD",0.7800,0.7750,0.65,"CASH",0,None,"GBP",0),
  ("E017",0.3850,"USD",None,None,"GBP|USD|EUR",0.7810,0.7750,0.77,"CASH",0,None,"GBP",0),
  ("E018",0.2200,"EUR",None,None,"GBP|EUR",0.8530,0.8480,0.59,"CASH",0,None,"GBP",0),
  ("E066",2.80,"CHF",95.20,"1 per 34","CHF",None,None,None,"CASH",35,-1.05,"CASH",0),
  ("E067",0.10,"EUR",4.12,"1 per 41","EUR",None,None,None,"SCRIP",19,-0.73,"CASH",0),
  ("E068",0.08,"EUR",9.45,"1 per 118","EUR",None,None,None,"SCRIP",19,-0.55,"CASH",0),
  ("E069",0.43,"EUR",7.25,"1 per 16","EUR",None,None,None,"CASH",26,-0.88,"CASH",0),
  ("E070",0.22,"EUR",3.85,"1 per 17","EUR",None,None,None,"CASH",26,-1.04,"CASH",0),
  ("E071",0.80,"EUR",55.20,"1 per 69","EUR",None,None,None,"CASH",30,-1.16,"CASH",0),
  ("E072",1.04,"EUR",82.00,"1 per 78","EUR",None,None,None,"CASH",15,-0.49,"CASH",0),
  ("E073",5.40,"EUR",395.00,"1 per 73","EUR",None,None,None,"CASH",30,-0.63,"CASH",0),
  ("E074",0.45,"EUR",11.20,"1 per 24","EUR",None,None,None,"CASH",19,-0.71,"CASH",0),
  ("E075",0.38,"EUR",6.80,"1 per 17","EUR",None,None,None,"CASH",26,-0.88,"CASH",0),
  ("E076",3.00,"EUR",68.50,"1 per 22","EUR",None,None,None,"CASH",30,-0.73,"CASH",0),
  ("E077",3.50,"CHF",96.00,"1 per 27","CHF",None,None,None,"CASH",35,-0.83,"CASH",0),
  ("E078",9.70,"CHF",295.00,"1 per 30","CHF",None,None,None,"CASH",35,-0.45,"CASH",0),
  ("E079",3.50,"EUR",62.00,"1 per 17","EUR",None,None,None,"CASH",30,-1.12,"CASH",0),
  ("E080",0.90,"EUR",14.80,"1 per 16","EUR",None,None,None,"CASH",26,-0.94,"CASH",0),
  ("E081",0.35,"USD",None,None,"USD|NOK",10.820,10.750,0.65,"CASH",0,None,"NOK",0),
  ("E082",0.06,"USD",None,None,"GBP|USD",None,0.7750,None,"CASH",0,None,None,0),
  ("E083",0.55,"USD",None,None,"GBP|USD",0.7840,0.7750,1.16,"CASH",0,None,"GBP",0),
  ("E084",1.20,"EUR",None,None,"EUR|CHF|GBP",0.8520,0.8480,0.47,"CASH",0,None,"GBP",0),
  ("E085",0.025,"USD",None,None,"USD|BHD",0.3770,0.3760,0.27,"CASH",0,None,"BHD",0),
  ("E106",4.50,"AUD",122.00,"1 per 27","AUD",None,None,None,"CASH",0,-0.82,"CASH",0),
  ("E107",1.20,"AUD",27.50,"1 per 22","AUD",None,None,None,"CASH",0,-0.55,"CASH",0),
  ("E108",0.85,"AUD",36.80,"1 per 43","AUD",None,None,None,"CASH",0,-0.61,"CASH",0),
  ("E109",0.90,"AUD",28.50,"1 per 31","AUD",None,None,None,"CASH",0,-0.44,"CASH",0),
  ("E110",0.60,"USD",None,None,"AUD|USD",0.6420,0.6380,0.63,"CASH",0,None,"AUD",0),
  ("E111",0.09,"AUD",4.05,"1 per 44","AUD",None,None,None,"CASH",0,-0.74,"CASH",0),
  ("E112",1.10,"USD",None,None,"AUD|USD",0.6440,0.6380,0.94,"CASH",0,None,"AUD",0),
  ("E113",0.72,"USD",None,None,"AUD|USD",0.6420,0.6380,0.63,"CASH",0,None,"AUD",0),
  ("E114",0.72,"USD",None,None,"AUD|USD|GBP",0.6410,0.6380,0.49,"CASH",0,None,"AUD",0),
  ("E115",0.72,"USD",None,None,"USD|AUD|GBP",0.6420,0.6380,0.63,"CASH",0,None,"AUD",0),
  ("E116",0.22,"USD",None,None,"USD|AUD",0.6430,0.6380,0.80,"CASH",0,None,"AUD",0),
  ("E133",0.65,"HKD",12.40,"1 per 19","HKD",None,None,None,"CASH",0,-0.48,"CASH",0),
  ("E134",0.55,"HKD",72.00,"1 per 130","HKD",None,None,None,"CASH",0,-0.55,"CASH",0),
  ("E135",0.38,"HKD",60.50,"1 per 159","HKD",None,None,None,"CASH",0,-0.41,"CASH",0),
  ("E155",0.25,"SAR",28.50,"1 per 114","SAR",None,None,None,"CASH",0,-0.35,"CASH",0),
  ("E158",0.28,"AED",13.20,"1 per 47","AED",None,None,None,"CASH",0,-0.53,"CASH",0),
  ("E161",0.32,"QAR",19.40,"1 per 60","QAR",None,None,None,"CASH",0,-0.62,"CASH",0),
  ("E163",0.04,"KWD",0.920,"1 per 23","KWD",None,None,None,"CASH",0,-0.44,"CASH",0),
  ("E166",25.00,"ZAR",5200.00,"1 per 208","ZAR",None,None,None,"CASH",20,-0.38,"CASH",0),
  ("E167",3.50,"ZAR",148.00,"1 per 42","ZAR",None,None,None,"CASH",20,-0.27,"SCRIP",0),
  ("E169",0.72,"USD",None,None,"USD|ZAR|GBP",0.7830,0.7750,1.03,"CASH",0,None,"GBP",0),
  ("E170",0.45,"USD",None,None,"ZAR|USD",0.7810,0.7750,0.77,"CASH",0,None,"USD",0),
  ("E175",1.80,"MAD",62.00,"1 per 34","MAD",None,None,None,"CASH",15,-0.65,"CASH",0),
  ("E176",3.00,"NGN",28.50,"1 per 9","NGN",None,None,None,"CASH",10,-0.88,"CASH",0),
  ("E186",0.32,"HKD",2.15,"1 per 6","HKD",None,None,None,"CASH",0,-0.93,"CASH",0),
  ("E187",0.62,"HKD",100.00,"1 per 161","HKD",None,None,None,"CASH",0,-0.62,"CASH",0),
  ("E188",0.18,"ILS",32.50,"1 per 180","ILS",None,None,None,"CASH",0,-0.55,"CASH",0),
  ("E191",28.00,"CZK",840.00,"1 per 30","CZK",None,None,None,"CASH",15,-0.48,"CASH",0),
  ("E196",1.80,"NOK",22.50,"1 per 12","NOK",None,None,None,"CASH",0,-0.67,"CASH",0),
]

# ── RIGHTS DETAILS ────────────────────────────────────────────────────────────
RIGHTS = [
  ("E019","RIGHTS_ISSUE","1 for 3",95.0,128.0,119.75,24.75,"BT-N.L",-20.7,"Goldman Sachs",850.0,1),
  ("E020","OPEN_OFFER","1 for 8",62.0,88.0,84.75,None,None,-26.8,"Barclays",180.0,1),
  ("E021","OPEN_OFFER","1 for 10",280.0,340.0,334.55,None,None,-16.3,"UBS",420.0,1),
  ("E022","RIGHTS_ISSUE","1 for 6",38.0,55.0,52.43,14.43,"LLOY-N.L",-27.5,"JPMorgan",650.0,1),
  ("E023","RIGHTS_ISSUE","1 for 5",140.0,178.0,172.33,32.33,"BARC-N.L",-18.8,"JPMorgan",1200.0,1),
  ("E086","RIGHTS_ISSUE","1 for 3",8.50,12.40,11.47,2.97,"UCG-N.MI",-25.9,"Deutsche Bank",3500.0,1),
  ("E087","RIGHTS_ISSUE","1 for 2",0.85,1.42,1.24,0.39,"ALPHA-N.AT",-31.5,"Piraeus",800.0,1),
  ("E088","OPEN_OFFER","1 for 6",2.40,3.25,3.11,None,None,-22.8,"Alpha Bank",650.0,1),
  ("E089","RIGHTS_ISSUE","1 for 3",4.20,6.40,5.87,1.67,"ETE-N.AT",-28.4,"Eurobank",1200.0,1),
  ("E090","RIGHTS_ISSUE","1 for 5",12.50,18.20,17.13,4.63,"DBK-N.DE",-27.0,"Morgan Stanley",4500.0,1),
  ("E091","RIGHTS_ISSUE","1 for 4",0.14,0.22,0.205,0.065,"BCP-N.LS",-31.7,"CAIXA",350.0,1),
  ("E092","RIGHTS_ISSUE","1 for 6",32.0,48.5,46.08,14.08,"PKO-N.WA",-30.6,"mBank",2800.0,1),
  ("E093","OPEN_OFFER","1 for 8",14500.0,20200.0,19487.5,4987.5,None,-25.6,"OTP Securities",850.0,1),
  ("E100","RIGHTS_ISSUE","1 for 5",95.0,140.0,131.25,36.25,"VWS-N.CO",-27.6,"Nordea",2400.0,1),
  ("E103","RIGHTS_ISSUE","1 for 4",180.0,248.0,231.25,51.25,"THYAO-N.IS",-22.1,"Is Yatirim",2800.0,1),
  ("E117","RIGHTS_ISSUE","1 for 5",14.50,20.80,19.55,5.05,"QBE-N.AX",-25.8,"Macquarie",1200.0,1),
  ("E126","RIGHTS_ISSUE","1 for 10",5.50,7.20,6.98,1.48,"0939-N.HK",-21.2,"CICC",8500.0,1),
  ("E127","RIGHTS_ISSUE","1 for 8",4.20,5.80,5.62,1.42,"1398-N.HK",-25.3,"BOC International",12000.0,1),
  ("E131","RIGHTS_ISSUE","1 for 5",220.0,295.0,277.5,57.5,"1211-N.HK",-20.7,"Goldman HK",15000.0,1),
  ("E139","RIGHTS_ISSUE","1 for 8",145.0,195.0,188.75,43.75,"3690-N.HK",-23.1,"Morgan Stanley HK",8000.0,1),
  ("E142","RIGHTS_ISSUE","1 for 10",180.0,245.0,238.5,58.5,"300750-N.SZ",-24.5,"CICC",20000.0,1),
  ("E148","RIGHTS_ISSUE","1 for 8",3200.0,4800.0,4625.0,1425.0,"8316-N.T",-30.8,"Nomura",400000.0,1),
  ("E153","RIGHTS_ISSUE","1 for 4",3200.0,4500.0,4175.0,975.0,"4502-N.T",-23.4,"Nomura",250000.0,1),
  ("E156","RIGHTS_ISSUE","1 for 5",32.0,45.8,43.13,11.13,"1180-N.SR",-25.9,"Saudi Fransi",8500.0,1),
  ("E159","OPEN_OFFER","1 for 5",4.20,6.10,5.77,None,None,-27.2,"EFG",3500.0,1),
  ("E162","RIGHTS_ISSUE","1 for 6",8.50,12.20,11.55,3.05,"ORDS-N.QA",-26.5,"QNB Capital",2800.0,1),
  ("E164","RIGHTS_ISSUE","1 for 5",12.50,18.40,17.15,4.65,"POLI-N.TA",-27.1,"Bank Hapoalim",1500.0,1),
  ("E168","RIGHTS_ISSUE","1 for 8",4200.0,5800.0,5644.0,1444.0,"FSR-N.JO",-25.6,"RMB",4500.0,1),
  ("E171","RIGHTS_ISSUE","1 for 4",18.0,28.5,26.13,8.13,"SSW-N.JO",-31.1,"Standard Bank",2200.0,1),
  ("E173","RIGHTS_ISSUE","1 for 3",15.0,22.5,20.63,5.63,"COMI-N.CA",-27.4,"CIB",1800.0,1),
  ("E174","RIGHTS_ISSUE","1 for 4",3.20,5.80,5.45,2.25,"ETEL-N.CA",-41.3,"CIB",1200.0,1),
  ("E177","RIGHTS_ISSUE","1 for 6",24.0,38.5,36.08,12.08,"SCOM-N.NR",-33.6,"KCB",5500.0,1),
  ("E180","RIGHTS_ISSUE","1 for 4",28.0,42.5,39.38,11.38,"EQNR-N.OL",-28.9,"DNB",5000.0,1),
  ("E181","RIGHTS_ISSUE","1 for 4",28.0,42.5,39.38,11.38,"NHY-N.OL",-28.9,"DNB Markets",5000.0,1),
  ("E189","RIGHTS_ISSUE","1 for 4",0.18,0.295,0.266,0.086,"AUB-N.BH",-32.3,"AUB Capital",250.0,1),
  ("E192","RIGHTS_ISSUE","1 for 5",0.38,0.58,0.546,0.166,"SNP-N.RO",-30.4,"BRD",1200.0,1),
  ("E193","RIGHTS_ISSUE","1 for 4",62.0,92.0,84.5,22.5,"2082-N.SR",-26.6,"Saudi Fransi",4800.0,1),
  ("E194","RIGHTS_ISSUE","1 for 10",12.80,17.50,16.93,4.13,"INGA-N.AS",-24.4,"ING",2800.0,1),
  ("E195","RIGHTS_ISSUE","1 for 6",88.0,130.0,123.0,35.0,"SHB-N.ST",-28.5,"SEB",15000.0,1),
  ("R016","RIGHTS_ISSUE","1 for 6",185.0,248.0,239.5,54.5,"BARC-N.L",-22.7,"Goldman Sachs",1200.0,1),
  ("R017","RIGHTS_ISSUE","1 for 4",145.0,195.0,183.75,38.75,"IAG-N.L",-21.0,"Barclays",950.0,1),
  ("R019","RIGHTS_ISSUE","1 for 5",1.80,2.65,2.47,0.67,"EUROB-N.AT",-27.1,"Eurobank",800.0,1),
  ("R022","RIGHTS_ISSUE","1 for 8",52.0,72.0,69.5,17.5,"BNP-N.PA",-25.2,"BNP Paribas",3500.0,1),
  ("R023","RIGHTS_ISSUE","1 for 6",28.0,42.0,39.67,11.67,"GLE-N.PA",-29.4,"SocGen",2000.0,1),
  ("R024","RIGHTS_ISSUE","1 for 5",11.50,16.80,15.77,4.27,"CBK-N.DE",-27.1,"Deutsche Bank",2200.0,1),
]

# ── TENDER DETAILS ────────────────────────────────────────────────────────────
TENDERS = [
  ("E027","FIXED",220.0,None,None,198.0,11.1,50000000,110.0,0,None,None,0),
  ("E036","FIXED",620.0,None,None,588.0,5.4,8000000,600.0,1,60.0,None,0),
  ("E037","FIXED",4200.0,None,None,3960.0,6.1,5000000,750.0,1,58.0,None,0),
  ("E038","FIXED",10200.0,None,None,9750.0,4.6,3500000,2000.0,1,55.0,None,0),
  ("E051","FIXED",7200.0,None,None,6850.0,5.1,8000000,576.0,1,55.0,None,0),
  ("E052","DUTCH_AUCTION",None,185.0,200.0,190.0,None,None,5000.0,1,60.0,None,0),
  ("E053","DUTCH_AUCTION",None,290.0,310.0,298.0,None,None,4000.0,1,55.0,None,0),
  ("E054","FIXED",4200.0,None,None,3980.0,5.5,12000000,500.0,1,65.0,None,0),
  ("E058","DUTCH_AUCTION",None,3400.0,3700.0,3520.0,None,15000000,500.0,1,70.0,None,0),
  ("E059","DUTCH_AUCTION",None,2800.0,3100.0,2920.0,None,14000000,400.0,1,65.0,None,0),
  ("E060","DUTCH_AUCTION",None,295.0,320.0,308.0,None,None,3000.0,1,60.0,None,0),
  ("E094","DUTCH_AUCTION",None,185.0,205.0,194.0,None,8000000,1500.0,1,60.0,None,0),
  ("E095","DUTCH_AUCTION",None,58.0,65.0,61.0,None,None,2000.0,1,58.0,None,0),
  ("E096","DUTCH_AUCTION",None,640.0,700.0,665.0,None,3000000,2000.0,1,65.0,None,0),
  ("E097","DUTCH_AUCTION",None,185.0,205.0,194.0,None,8000000,1500.0,1,60.0,None,0),
  ("E098","DUTCH_AUCTION",None,820.0,900.0,855.0,None,None,5000.0,1,62.0,None,0),
  ("E099","DUTCH_AUCTION",None,88.0,96.0,92.0,None,None,5000.0,1,60.0,None,0),
  ("E128","DUTCH_AUCTION",None,8.0,9.2,8.5,None,None,10000.0,1,58.0,None,0),
  ("E129","DUTCH_AUCTION",None,85.0,95.0,90.0,None,None,12000.0,1,60.0,None,0),
  ("E130","DUTCH_AUCTION",None,370.0,420.0,395.0,None,None,100000.0,1,62.0,None,0),
  ("E144","FIXED",3400.0,None,None,3220.0,5.6,None,500000.0,1,55.0,None,0),
  ("E145","DUTCH_AUCTION",None,3200.0,3600.0,3400.0,None,None,200000.0,1,60.0,None,0),
  ("E146","DUTCH_AUCTION",None,7800.0,8600.0,8200.0,None,None,500000.0,1,58.0,None,0),
  ("E147","FIXED",1850.0,None,None,1760.0,5.1,None,300000.0,1,58.0,None,0),
  ("E154","FIXED",32.0,None,None,30.2,6.0,None,20000.0,1,55.0,None,0),
  ("E157","FIXED",125.0,None,None,118.0,5.9,None,5000.0,1,58.0,None,0),
  ("E160","FIXED",14.8,None,None,14.0,5.7,None,3000.0,1,60.0,None,0),
  ("E165","FIXED",310.0,None,None,294.0,5.4,None,500.0,1,55.0,None,0),
  ("E172","FIXED",148.0,None,None,140.0,5.7,None,3000.0,1,58.0,None,0),
  ("E179","FIXED",128.0,None,None,122.0,4.9,15000000,2000.0,1,55.0,None,0),
  ("E182","FIXED",145.0,None,None,138.0,5.1,None,10000.0,1,58.0,None,0),
]

# ── MERGER DETAILS ────────────────────────────────────────────────────────────
MERGERS = [
  ("E024","SCHEME","Emerson Electric","EMR","CASH",1850.0,None,1820.0,1.65,d(25),d(180),"CLEARED","LOW"),
  ("E025","SCHEME","Undisclosed Bidder",None,"CASH",3200.0,None,3140.0,1.91,d(40),d(210),"PENDING","MEDIUM"),
  ("E026","SCHEME","Ferguson Enterprises","FERG","CASH",8500.0,None,8420.0,0.95,d(15),d(150),"CLEARED","LOW"),
  ("E101","MERGER","AGC Inc",None,"SHARES",None,"1.1 new per old",58.2,None,None,d(180),"PENDING","MEDIUM"),
  ("E102","MERGER","Haier Group",None,"CASH",42.5,None,41.8,1.67,None,d(180),"PENDING","HIGH"),
  ("E118","SCHEME","Brookfield Asset Mgmt","BAM","CASH",9.80,None,9.62,1.87,d(22),d(180),"CLEARED","LOW"),
  ("E119","SCHEME","Harbour Energy","HBR.L","MIXED",6.20,"0.35 HBR per STO",6.05,2.48,d(45),d(240),"PENDING","MEDIUM"),
  ("E151","SCHEME","Honda Motor Co","7267.T","SHARES",None,"0.5 Honda per Nissan",485.0,None,d(20),d(300),"PENDING","HIGH"),
  ("E152","SCHEME","Honda Motor Co","7267.T","SHARES",None,"0.5 Honda per Nissan",485.0,None,d(20),d(300),"PENDING","HIGH"),
  ("E190","MERGER","INA Croatia",None,"CASH",3800.0,None,3680.0,3.26,None,d(180),"PENDING","HIGH"),
  ("E200","SCHEME","Undisclosed PE",None,"CASH",82.0,None,79.5,3.14,d(48),d(240),"PENDING","MEDIUM"),
  ("R033","SCHEME","Marriott International","MAR","CASH",3200.0,None,3140.0,1.91,d(22),d(210),"CLEARED","LOW"),
]

# ── SPINOFF DETAILS ───────────────────────────────────────────────────────────
SPINOFFS = [
  ("E125","CSL Vifor Ltd","VIFR.AX","ASX","1 for 12","Pharmaceuticals",18.0,d(55)),
  ("E136","Hutchison Ports Holdings","HPC.HK","HKEX","1 for 8","Industrials",4.20,d(60)),
  ("E137","Cathay Pacific Cargo","CPAC.HK","HKEX","1 for 10","Airlines",2.80,d(65)),
  ("E138","JD Health International","6618.HK","HKEX","1 for 10","Healthcare",28.0,d(30)),
  ("E185","NextEra Energy Resources","NEER","NYSE","1 for 4","Utilities",42.0,d(60)),
]

# ── SPLIT DETAILS ─────────────────────────────────────────────────────────────
SPLITS = [
  ("E123","SPLIT","2:1",295.0,147.5),
  ("E124","SPLIT","5:1",145.0,29.0),
  ("E132","SPLIT","5:1",18.5,3.7),
  ("E141","SPLIT","10:1",1850.0,185.0),
  ("E149","SPLIT","5:1",65000.0,13000.0),
  ("E150","SPLIT","3:1",42000.0,14000.0),
  ("E178","SPLIT","2:1",920.0,460.0),
  ("E197","SPLIT","5:1",8450.0,1690.0),
  ("E198","CONSOLIDATION","1:10",92.0,920.0),
  ("E199","CONSOLIDATION","1:5",18.4,92.0),
]

# ─────────────────────────────────────────────────────────────────────────────
# US EVENTS — tenders, dutch auctions, stock splits, mergers, spinoffs
# (US market does not do scrip dividends, CCY elections or rights issues)
# ─────────────────────────────────────────────────────────────────────────────
US_E = [
    ("US001","AAPL","Apple Inc","US","USD","tender_offer","VOLUNTARY","LIVE",dp(18),None,dp(5),d(14),None,d(20),"https://apple.com","$90bn fixed price tender"),
    ("US002","MSFT","Microsoft Corp","US","USD","tender_offer","VOLUNTARY","UPCOMING",dp(5),None,d(16),d(36),None,d(42),"https://microsoft.com","$60bn tender offer"),
    ("US003","GOOGL","Alphabet Inc","US","USD","tender_offer","VOLUNTARY","LIVE",dp(22),None,dp(8),d(12),None,d(18),"https://abc.xyz","$70bn accelerated tender"),
    ("US004","META","Meta Platforms Inc","US","USD","tender_offer","VOLUNTARY","LIVE",dp(16),None,dp(4),d(16),None,d(22),"https://investor.fb.com","$50bn fixed price tender"),
    ("US005","BRK-B","Berkshire Hathaway","US","USD","tender_offer","VOLUNTARY","UPCOMING",dp(4),None,d(20),d(40),None,d(46),"https://berkshirehathaway.com","$20bn tender offer"),
    ("US006","JPM","JPMorgan Chase","US","USD","tender_offer","VOLUNTARY","LIVE",dp(20),None,dp(6),d(14),None,d(20),"https://jpmorganchase.com","$30bn fixed price tender"),
    ("US007","V","Visa Inc","US","USD","tender_offer","VOLUNTARY","UPCOMING",dp(3),None,d(18),d(38),None,d(44),"https://investor.visa.com","$12bn tender offer"),
    ("US008","UNH","UnitedHealth Group","US","USD","tender_offer","VOLUNTARY","LIVE",dp(14),None,dp(3),d(17),None,d(23),"https://unitedhealthgroup.com","$8bn fixed price tender"),
    ("US009","NVDA","NVIDIA Corp","US","USD","dutch_auction","VOLUNTARY","LIVE",dp(30),None,None,d(90),None,None,"https://nvidia.com","$50bn dutch auction"),
    ("US010","AMZN","Amazon.com Inc","US","USD","dutch_auction","VOLUNTARY","LIVE",dp(25),None,None,d(80),None,None,"https://ir.aboutamazon.com","$40bn dutch auction"),
    ("US011","TSM","Taiwan Semi ADR","US","USD","dutch_auction","VOLUNTARY","UPCOMING",dp(5),None,None,d(95),None,None,"https://tsmc.com","$15bn dutch auction"),
    ("US012","LLY","Eli Lilly and Co","US","USD","dutch_auction","VOLUNTARY","LIVE",dp(20),None,None,d(85),None,None,"https://investor.lilly.com","$10bn dutch auction"),
    ("US013","AVGO","Broadcom Inc","US","USD","dutch_auction","VOLUNTARY","UPCOMING",dp(4),None,None,d(92),None,None,"https://investors.broadcom.com","$8bn dutch auction"),
    ("US014","WMT","Walmart Inc","US","USD","dutch_auction","VOLUNTARY","LIVE",dp(18),None,None,d(88),None,None,"https://stock.walmart.com","$12bn dutch auction"),
    ("US015","NVDA","NVIDIA Corp","US","USD","stock_split","MANDATORY","UPCOMING",dp(8),d(22),d(23),None,None,None,"https://nvidia.com","10:1 forward split"),
    ("US016","TSLA","Tesla Inc","US","USD","stock_split","MANDATORY","UPCOMING",dp(5),d(28),d(29),None,None,None,"https://ir.tesla.com","3:1 forward split"),
    ("US017","AMZN","Amazon.com Inc","US","USD","stock_split","MANDATORY","LIVE",dp(25),d(5),d(6),None,None,None,"https://ir.aboutamazon.com","20:1 forward split"),
    ("US018","AAPL","Apple Inc","US","USD","stock_split","MANDATORY","UPCOMING",dp(6),d(30),d(31),None,None,None,"https://apple.com","4:1 forward split"),
    ("US019","GOOGL","Alphabet Inc","US","USD","stock_split","MANDATORY","UPCOMING",dp(3),d(35),d(36),None,None,None,"https://abc.xyz","20:1 forward split"),
    ("US020","META","Meta Platforms Inc","US","USD","stock_split","MANDATORY","LIVE",dp(20),d(8),d(9),None,None,None,"https://investor.fb.com","5:1 forward split"),
    ("US021","ATVI","Activision Blizzard","US","USD","merger","VOLUNTARY","LIVE",dp(45),None,dp(10),d(20),d(40),d(45),"https://investor.activision.com","Microsoft acquisition"),
    ("US022","VMW","VMware Inc","US","USD","scheme_of_arrangement","VOLUNTARY","LIVE",dp(38),None,dp(8),d(22),d(40),d(45),"https://ir.vmware.com","Broadcom acquisition"),
    ("US023","TWTR","Twitter / X Corp","US","USD","scheme_of_arrangement","VOLUNTARY","UPCOMING",dp(5),None,d(30),d(55),d(75),d(80),"https://twitter.com","Strategic acquisition"),
    ("US024","GE","GE Aerospace","US","USD","spinoff","MANDATORY","UPCOMING",dp(12),d(45),d(46),None,d(60),d(61),"https://geaerospace.com","GE Vernova energy spinoff"),
    ("US025","JNJ","Johnson & Johnson","US","USD","spinoff","MANDATORY","LIVE",dp(20),d(15),d(16),None,d(30),d(31),"https://investor.jnj.com","Kenvue consumer spinoff"),
]
US_TENDERS = [
    ("US001","FIXED",235.0,None,None,218.0,7.8,None,90000.0,1,55.0,None,0),
    ("US002","FIXED",425.0,None,None,398.0,6.8,None,60000.0,1,58.0,None,0),
    ("US003","FIXED",185.0,None,None,175.0,5.7,None,70000.0,1,55.0,None,0),
    ("US004","FIXED",580.0,None,None,548.0,5.8,None,50000.0,1,60.0,None,0),
    ("US005","FIXED",375.0,None,None,355.0,5.6,None,20000.0,1,58.0,None,0),
    ("US006","FIXED",245.0,None,None,232.0,5.6,None,30000.0,1,55.0,None,0),
    ("US007","FIXED",285.0,None,None,270.0,5.6,None,12000.0,1,60.0,None,0),
    ("US008","FIXED",520.0,None,None,492.0,5.7,None,8000.0,1,58.0,None,0),
    ("US009","DUTCH_AUCTION",None,115.0,135.0,124.0,None,None,50000.0,1,62.0,None,0),
    ("US010","DUTCH_AUCTION",None,175.0,205.0,188.0,None,None,40000.0,1,60.0,None,0),
    ("US011","DUTCH_AUCTION",None,155.0,175.0,164.0,None,None,15000.0,1,58.0,None,0),
    ("US012","DUTCH_AUCTION",None,780.0,850.0,812.0,None,None,10000.0,1,60.0,None,0),
    ("US013","DUTCH_AUCTION",None,175.0,200.0,186.0,None,None,8000.0,1,62.0,None,0),
    ("US014","DUTCH_AUCTION",None,92.0,108.0,99.0,None,None,12000.0,1,58.0,None,0),
]
US_SPLITS = [
    ("US015","SPLIT","10:1",1250.0,125.0),
    ("US016","SPLIT","3:1",285.0,95.0),
    ("US017","SPLIT","20:1",180.0,9.0),
    ("US018","SPLIT","4:1",195.0,48.75),
    ("US019","SPLIT","20:1",178.0,8.9),
    ("US020","SPLIT","5:1",580.0,116.0),
]
US_MERGERS = [
    ("US021","MERGER","Microsoft Corp","MSFT","CASH",95.0,None,92.5,2.70,d(20),d(180),"CLEARED","LOW"),
    ("US022","SCHEME","Broadcom Inc","AVGO","CASH",142.5,None,139.0,2.52,d(22),d(180),"CLEARED","LOW"),
    ("US023","SCHEME","Undisclosed","","CASH",54.2,None,51.8,4.63,d(55),d(240),"PENDING","MEDIUM"),
]
US_SPINOFFS = [
    ("US024","GE Vernova Ltd","GEV","NYSE","1 for 4","Energy/Utilities",22.0,d(60)),
    ("US025","Kenvue Inc","KVUE","NYSE","1 for 3","Consumer Health",18.0,d(30)),
]

def build():
    if os.path.exists(DB):
        os.remove(DB)
    conn = sqlite3.connect(DB)
    c    = conn.cursor()
    for stmt in SCHEMA.strip().split(";"):
        s = stmt.strip()
        if s: c.execute(s)

    c.executemany("""INSERT OR IGNORE INTO events(event_id,ticker,company_name,country,
        currency,event_type,event_category,status,announcement_date,ex_date,
        record_date,election_deadline,payment_date,settlement_date,source_url,notes)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", E)

    c.executemany("INSERT OR IGNORE INTO scrip_details VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", SCRIP)
    c.executemany("INSERT OR IGNORE INTO rights_details VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", RIGHTS)
    c.executemany("INSERT OR IGNORE INTO tender_details VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", TENDERS)
    c.executemany("INSERT OR IGNORE INTO merger_details VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", MERGERS)
    c.executemany("INSERT OR IGNORE INTO spinoff_details VALUES(?,?,?,?,?,?,?,?)", SPINOFFS)
    c.executemany("INSERT OR IGNORE INTO split_details VALUES(?,?,?,?,?)", SPLITS)
    c.executemany("""INSERT OR IGNORE INTO events(event_id,ticker,company_name,country,
        currency,event_type,event_category,status,announcement_date,ex_date,
        record_date,election_deadline,payment_date,settlement_date,source_url,notes)
        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", US_E)
    c.executemany("INSERT OR IGNORE INTO tender_details VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", US_TENDERS)
    c.executemany("INSERT OR IGNORE INTO split_details VALUES(?,?,?,?,?)", US_SPLITS)
    c.executemany("INSERT OR IGNORE INTO merger_details VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", US_MERGERS)
    c.executemany("INSERT OR IGNORE INTO spinoff_details VALUES(?,?,?,?,?,?,?,?)", US_SPINOFFS)
    # ── CCY election: flag events with rate fixed before deadline (genuine arb) ──
    # Only set rate_pre_deadline=1 when confirmed that the company publishes
    # a fixed FX reference rate at the dividend announcement (before election deadline).
    # Typical candidates: UK-listed mining/resources, African telecom ADRs.
    # Update this list as you confirm each event in real-world processing.
    PRE_DEADLINE_TICKERS = ['AAF.L', 'STAN.L', 'RIO.L', 'AAL.L', 'ANTO.L', 'BHP.JO', 'HSBA.L', 'BHP.AX', 'RIO.AX']
    for ticker in PRE_DEADLINE_TICKERS:
        c.execute("""UPDATE scrip_details SET rate_pre_deadline=1
            WHERE event_id IN (
                SELECT event_id FROM events
                WHERE ticker=? AND event_type='fx_election'
            )""", (ticker,))


    conn.commit()

    total    = c.execute("SELECT COUNT(*) FROM events").fetchone()[0]
    live     = c.execute("SELECT COUNT(*) FROM events WHERE status='LIVE'").fetchone()[0]
    upcoming = c.execute("SELECT COUNT(*) FROM events WHERE status='UPCOMING'").fetchone()[0]
    closed   = c.execute("SELECT COUNT(*) FROM events WHERE status='CLOSED'").fetchone()[0]

    print(f"\n✓ events.db built — {total} events")
    print(f"  LIVE {live}  UPCOMING {upcoming}  CLOSED {closed}")
    print(f"\n  By type:")
    for row in c.execute("SELECT event_type,COUNT(*) n FROM events GROUP BY event_type ORDER BY n DESC"):
        print(f"    {row[0]:<28} {row[1]}")
    print(f"\n  By country (top 10):")
    for row in c.execute("SELECT country,COUNT(*) n FROM events GROUP BY country ORDER BY n DESC LIMIT 10"):
        print(f"    {row[0]:<25} {row[1]}")
    conn.close()

if __name__ == "__main__":
    build()
