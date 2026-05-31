import sqlite3
from datetime import date, timedelta

TODAY = date(2026, 5, 25)
def d(n):  return (TODAY + timedelta(days=n)).isoformat()
def dp(n): return (TODAY - timedelta(days=n)).isoformat()

conn = sqlite3.connect("data/events.db")
c    = conn.cursor()

NEW_EVENTS = [
    ("R001","VOD.L","Vodafone Group PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","LIVE",dp(22),dp(8),dp(7),d(7),d(23),d(24),"https://vodafone.com","EUR/GBP Q1 2026"),
    ("R002","PRU.L","Prudential PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","UPCOMING",dp(4),d(22),d(23),d(44),d(65),d(66),"https://prudentialplc.com","USD/GBP/HKD 2026"),
    ("R003","RIO.L","Rio Tinto PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","LIVE",dp(20),dp(6),dp(5),d(9),d(26),d(27),"https://riotinto.com","USD/GBP 2026 interim"),
    ("R004","ANTO.L","Antofagasta PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","LIVE",dp(18),dp(5),dp(4),d(10),d(28),d(29),"https://antofagasta.co.uk","USD/GBP 2026"),
    ("R005","MNDI.L","Mondi PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","UPCOMING",dp(3),d(20),d(21),d(42),d(62),d(63),"https://mondigroup.com","EUR/GBP 2026"),
    ("R006","BHP.AX","BHP Group Ltd","Australia","AUD","fx_election","MANDATORY_WITH_CHOICE","LIVE",dp(16),dp(3),dp(2),d(12),d(30),d(31),"https://bhp.com","USD/AUD/GBP 2026 final"),
    ("R007","WDS.AX","Woodside Energy","Australia","AUD","fx_election","MANDATORY_WITH_CHOICE","UPCOMING",dp(4),d(24),d(25),d(46),d(66),d(67),"https://woodside.com","USD/AUD 2026"),
    ("R008","STO.AX","Santos Ltd","Australia","AUD","fx_election","MANDATORY_WITH_CHOICE","LIVE",dp(20),dp(7),dp(6),d(8),d(25),d(26),"https://santos.com","USD/AUD election 2026"),
    ("R009","HSBA.L","HSBC Holdings PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","UPCOMING",dp(5),d(28),d(29),d(50),d(70),d(71),"https://hsbc.com","Q2 2026 USD/GBP"),
    ("R010","STAN.L","Standard Chartered PLC","UK","GBX","fx_election","MANDATORY_WITH_CHOICE","UPCOMING",dp(3),d(30),d(31),d(52),d(72),d(73),"https://sc.com","Q2 2026 USD/GBP"),
    ("R011","EQNR.OL","Equinor ASA","Norway","NOK","fx_election","MANDATORY_WITH_CHOICE","UPCOMING",dp(4),d(32),d(33),d(55),d(75),d(76),"https://equinor.com","Q2 2026 USD/NOK"),
    ("R012","GFI.JO","Gold Fields Ltd","South Africa","ZAR","fx_election","MANDATORY_WITH_CHOICE","LIVE",dp(18),dp(5),dp(4),d(10),d(28),d(29),"https://goldfields.com","USD/ZAR 2026"),
    ("R013","ANG.JO","AngloGold Ashanti PLC","South Africa","ZAR","fx_election","MANDATORY_WITH_CHOICE","LIVE",dp(22),dp(8),dp(7),d(8),d(25),d(26),"https://anglogoldashanti.com","USD/ZAR 2026"),
    ("R014","2318.HK","Ping An Insurance","Hong Kong","HKD","fx_election","MANDATORY_WITH_CHOICE","LIVE",dp(16),dp(3),dp(2),d(11),d(29),d(30),"https://pingan.com","HKD/CNY 2026"),
    ("R015","0941.HK","China Mobile Ltd","Hong Kong","HKD","fx_election","MANDATORY_WITH_CHOICE","UPCOMING",dp(5),d(26),d(27),d(48),d(68),d(69),"https://chinamobileltd.com","HKD/CNY 2026"),
    ("R016","BARC.L","Barclays PLC","UK","GBX","rights_issue","VOLUNTARY","LIVE",dp(15),d(5),d(6),d(20),d(38),d(43),"https://barclays.com","1 for 6 at 185p"),
    ("R017","IAG.L","Intl Consolidated Airlines","UK","GBX","rights_issue","VOLUNTARY","LIVE",dp(18),d(6),d(7),d(22),d(40),d(45),"https://iairgroup.com","1 for 4 at 145p"),
    ("R018","EZJ.L","EasyJet PLC","UK","GBX","rights_issue","VOLUNTARY","UPCOMING",dp(5),d(25),d(26),d(44),d(62),d(67),"https://corporate.easyjet.com","1 for 5 at 310p"),
    ("R019","EUROB.AT","Eurobank Ergasias","Greece","EUR","rights_issue","VOLUNTARY","UPCOMING",dp(4),d(28),d(29),d(48),d(66),d(71),"https://eurobank.gr","Capital increase 800m"),
    ("R020","ISP.MI","Intesa Sanpaolo SpA","Italy","EUR","rights_issue","VOLUNTARY","LIVE",dp(16),d(5),d(6),d(20),d(38),d(43),"https://intesasanpaolo.com","1 for 10 at 3.20"),
    ("R021","G.MI","Assicurazioni Generali","Italy","EUR","rights_issue","VOLUNTARY","UPCOMING",dp(5),d(30),d(31),d(52),d(72),d(77),"https://generali.com","Capital raise 1.5bn"),
    ("R022","BNP.PA","BNP Paribas SA","France","EUR","rights_issue","VOLUNTARY","LIVE",dp(18),d(7),d(8),d(24),d(42),d(47),"https://invest.bnpparibas.com","1 for 8 at 52"),
    ("R023","GLE.PA","Societe Generale SA","France","EUR","rights_issue","VOLUNTARY","UPCOMING",dp(3),d(25),d(26),d(46),d(66),d(71),"https://societegenerale.com","Capital increase 2bn"),
    ("R024","CBK.DE","Commerzbank AG","Germany","EUR","rights_issue","VOLUNTARY","LIVE",dp(20),d(8),d(9),d(26),d(44),d(49),"https://commerzbank.com","1 for 5 at 11.50"),
    ("R025","SAN.MC","Banco Santander SA","Spain","EUR","rights_issue","VOLUNTARY","LIVE",dp(15),d(5),d(6),d(20),d(38),d(43),"https://santander.com","1 for 12 at 4.10"),
    ("R026","CABK.MC","CaixaBank SA","Spain","EUR","rights_issue","VOLUNTARY","UPCOMING",dp(5),d(28),d(29),d(50),d(70),d(75),"https://caixabank.com","Capital increase 1bn"),
    ("R027","PKN.WA","PKN Orlen SA","Poland","PLN","rights_issue","VOLUNTARY","LIVE",dp(18),d(6),d(7),d(22),d(40),d(45),"https://orlen.pl","1 for 8 at PLN 48"),
    ("R028","SBK.JO","Standard Bank Group","South Africa","ZAR","rights_issue","VOLUNTARY","LIVE",dp(16),d(5),d(6),d(20),d(38),d(43),"https://standardbank.com","1 for 10 at ZAR 180"),
    ("R029","NED.JO","Nedbank Group Ltd","South Africa","ZAR","rights_issue","VOLUNTARY","UPCOMING",dp(3),d(26),d(27),d(46),d(66),d(71),"https://nedbankgroup.co.za","Capital raise ZAR 6bn"),
    ("R030","3988.HK","Bank of China Ltd","Hong Kong","HKD","rights_issue","VOLUNTARY","UPCOMING",dp(4),d(28),d(29),d(50),d(70),d(75),"https://boc.cn","A+H capital raise"),
    ("R031","TEVA.TA","Teva Pharmaceutical","Israel","ILS","rights_issue","VOLUNTARY","LIVE",dp(16),d(5),d(6),d(20),d(38),d(43),"https://tevapharm.com","1 for 5 at ILS 32"),
    ("R032","8316.T","SMFG","Japan","JPY","rights_issue","VOLUNTARY","UPCOMING",dp(5),d(30),d(31),d(52),d(72),d(77),"https://smfg.co.jp","Capital increase JPY 400bn"),
    ("R033","WTB.L","Whitbread PLC","UK","GBX","scheme_of_arrangement","VOLUNTARY","LIVE",dp(35),None,dp(8),d(22),d(40),d(45),"https://whitbread.co.uk","Recommended cash offer"),
    ("R034","PSON.L","Pearson PLC","UK","GBX","scheme_of_arrangement","VOLUNTARY","UPCOMING",dp(6),None,d(20),d(45),d(65),d(70),"https://pearson.com","Recommended acquisition"),
    ("R035","SDR.L","Schroders PLC","UK","GBX","scheme_of_arrangement","VOLUNTARY","LIVE",dp(28),None,dp(5),d(25),d(42),d(47),"https://schroders.com","Recommended cash offer"),
    ("R036","RACE.MI","Ferrari NV","Italy","EUR","scheme_of_arrangement","VOLUNTARY","UPCOMING",dp(5),None,d(35),d(60),d(80),d(85),"https://ferrari.com","Recommended acquisition"),
    ("R037","KER.PA","Kering SA","France","EUR","merger","VOLUNTARY","LIVE",dp(22),None,dp(4),d(20),d(38),d(43),"https://kering.com","Strategic merger"),
    ("R038","IAM.CS","Maroc Telecom SA","Morocco","MAD","merger","VOLUNTARY","UPCOMING",dp(5),None,d(30),d(55),d(75),d(80),"https://iam.ma","Strategic merger proposal"),
    ("R039","RTO.L","Rentokil Initial PLC","UK","GBX","tender_offer","VOLUNTARY","LIVE",dp(14),None,dp(3),d(16),None,d(22),"https://rentokininitial.com","600m fixed price tender"),
    ("R040","AZN.L","AstraZeneca PLC","UK","GBX","tender_offer","VOLUNTARY","LIVE",dp(20),None,dp(6),d(14),None,d(20),"https://astrazeneca.com","2bn accelerated tender"),
    ("R041","8306.T","Mitsubishi UFJ Financial","Japan","JPY","tender_offer","VOLUNTARY","UPCOMING",dp(5),None,d(18),d(38),None,d(44),"https://mufg.jp","JPY 300bn tender offer"),
    ("R042","2222.SR","Saudi Aramco","Saudi Arabia","SAR","tender_offer","VOLUNTARY","LIVE",dp(18),None,dp(5),d(15),None,d(21),"https://aramco.com","SAR 20bn fixed tender"),
    ("R043","FAB.AD","First Abu Dhabi Bank","UAE","AED","tender_offer","VOLUNTARY","UPCOMING",dp(4),None,d(20),d(40),None,d(46),"https://bankfab.com","AED 3bn tender offer"),
    ("R044","QNBK.QA","Qatar National Bank","Qatar","QAR","tender_offer","VOLUNTARY","LIVE",dp(16),None,dp(3),d(17),None,d(23),"https://qnb.com","QAR 5bn tender offer"),
    ("R045","7203.T","Toyota Motor Corp","Japan","JPY","tender_offer","VOLUNTARY","LIVE",dp(22),None,dp(7),d(13),None,d(19),"https://toyota.co.jp","JPY 500bn tender offer"),
    ("R046","NESN.SW","Nestle SA","Switzerland","CHF","tender_offer","VOLUNTARY","UPCOMING",dp(5),None,d(16),d(36),None,d(42),"https://nestle.com","CHF 3bn fixed price tender"),
    ("R047","EXPN.L","Experian PLC","UK","GBX","tender_offer","VOLUNTARY","UPCOMING",dp(4),None,d(14),d(34),None,d(40),"https://experianplc.com","750m tender offer"),
    ("R048","TEVA.TA","Teva Pharmaceutical","Israel","ILS","scheme_of_arrangement","VOLUNTARY","LIVE",dp(30),None,dp(8),d(22),d(40),d(45),"https://tevapharm.com","Recommended cash offer"),
    ("R049","MOL.BD","MOL Group","Hungary","HUF","merger","VOLUNTARY","UPCOMING",dp(4),None,d(28),d(52),d(72),d(77),"https://mol.hu","Strategic acquisition"),
    ("R050","ETEL.CA","Telecom Egypt","Egypt","EGP","scheme_of_arrangement","VOLUNTARY","LIVE",dp(18),None,dp(4),d(20),d(38),d(43),"https://telecomegypt.com.eg","Recommended offer"),
    ("R051","ISP.MI","Intesa Sanpaolo SpA","Italy","EUR","tender_offer","VOLUNTARY","LIVE",dp(12),None,dp(2),d(18),None,d(24),"https://intesasanpaolo.com","EUR 2bn tender offer"),
    ("R052","LVMH","LVMH Moet Hennessy","France","EUR","tender_offer","VOLUNTARY","LIVE",dp(16),None,dp(4),d(16),None,d(22),"https://lvmh.com","EUR 1bn fixed price tender"),
    ("R053","CBK.DE","Commerzbank AG","Germany","EUR","scheme_of_arrangement","VOLUNTARY","UPCOMING",dp(6),None,d(22),d(48),d(68),d(73),"https://commerzbank.com","Recommended acquisition"),
    ("R054","PGE.WA","PGE Polska","Poland","PLN","rights_issue","VOLUNTARY","UPCOMING",dp(4),d(24),d(25),d(44),d(64),d(69),"https://pge.pl","Capital increase PLN 4bn"),
]

c.executemany("""INSERT OR IGNORE INTO events(
    event_id,ticker,company_name,country,currency,event_type,event_category,
    status,announcement_date,ex_date,record_date,election_deadline,
    payment_date,settlement_date,source_url,notes)
    VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", NEW_EVENTS)

NEW_SCRIP = [
    ("R001",0.045,"EUR",None,None,"GBP|EUR",0.8520,0.8480,0.47,"CASH",0,None,"GBP"),
    ("R002",0.059,"USD",None,None,"GBP|USD|HKD",0.7820,0.7750,0.90,"CASH",0,None,"GBP"),
    ("R003",1.770,"USD",None,None,"GBP|USD|AUD",0.7850,0.7750,1.29,"CASH",0,None,"GBP"),
    ("R004",0.440,"USD",None,None,"GBP|USD",0.7840,0.7750,1.16,"CASH",0,None,"GBP"),
    ("R005",0.150,"EUR",None,None,"GBP|EUR",0.8510,0.8480,0.37,"CASH",0,None,"GBP"),
    ("R006",0.720,"USD",None,None,"USD|AUD|GBP",0.6420,0.6380,0.63,"CASH",0,None,"AUD"),
    ("R007",0.600,"USD",None,None,"AUD|USD",0.6430,0.6380,0.80,"CASH",0,None,"AUD"),
    ("R008",0.380,"USD",None,None,"AUD|USD",0.6410,0.6380,0.49,"CASH",0,None,"AUD"),
    ("R009",0.100,"USD",None,None,"GBP|USD",0.7817,0.7750,0.86,"CASH",0,None,"GBP"),
    ("R010",0.072,"USD",None,None,"GBP|USD",0.7900,0.7750,1.94,"CASH",0,None,"GBP"),
    ("R011",0.350,"USD",None,None,"USD|NOK",10.820,10.750,0.65,"CASH",0,None,"NOK"),
    ("R012",0.450,"USD",None,None,"USD|ZAR",0.7810,0.7750,0.77,"CASH",0,None,"USD"),
    ("R013",0.320,"USD",None,None,"USD|ZAR",0.7830,0.7750,1.03,"CASH",0,None,"USD"),
    ("R014",0.620,"HKD",None,None,"HKD|CNY",0.9210,0.9180,0.34,"CASH",0,None,"HKD"),
    ("R015",0.420,"HKD",None,None,"HKD|CNY",0.9200,0.9180,0.22,"CASH",0,None,"HKD"),
]
c.executemany("INSERT OR IGNORE INTO scrip_details VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", NEW_SCRIP)

NEW_RIGHTS = [
    ("R016","RIGHTS_ISSUE","1 for 6",185.0,248.0,239.5,54.5,"BARC-N.L",-22.7,"Goldman Sachs",1200.0,1),
    ("R017","RIGHTS_ISSUE","1 for 4",145.0,195.0,183.75,38.75,"IAG-N.L",-21.0,"Barclays",950.0,1),
    ("R018","RIGHTS_ISSUE","1 for 5",310.0,425.0,397.0,87.0,"EZJ-N.L",-21.9,"Deutsche Bank",850.0,1),
    ("R019","RIGHTS_ISSUE","1 for 5",1.80,2.65,2.47,0.67,"EUROB-N.AT",-27.1,"Eurobank",800.0,1),
    ("R020","RIGHTS_ISSUE","1 for 10",3.20,4.85,4.685,1.485,"ISP-N.MI",-31.7,"Mediobanca",2800.0,1),
    ("R021","RIGHTS_ISSUE","1 for 6",8.50,12.40,11.47,2.97,"G-N.MI",-25.9,"Goldman Sachs",1500.0,1),
    ("R022","RIGHTS_ISSUE","1 for 8",52.0,72.0,69.5,17.5,"BNP-N.PA",-25.2,"BNP Paribas",3500.0,1),
    ("R023","RIGHTS_ISSUE","1 for 6",28.0,42.0,39.67,11.67,"GLE-N.PA",-29.4,"SocGen",2000.0,1),
    ("R024","RIGHTS_ISSUE","1 for 5",11.50,16.80,15.77,4.27,"CBK-N.DE",-27.1,"Deutsche Bank",2200.0,1),
    ("R025","RIGHTS_ISSUE","1 for 12",4.10,5.80,5.66,1.56,"SAN-N.MC",-27.5,"Santander",3200.0,1),
    ("R026","RIGHTS_ISSUE","1 for 8",3.40,5.20,4.98,1.58,"CABK-N.MC",-31.7,"CaixaBank",1000.0,1),
    ("R027","RIGHTS_ISSUE","1 for 8",48.0,72.0,69.0,21.0,"PKN-N.WA",-30.4,"mBank",3200.0,1),
    ("R028","RIGHTS_ISSUE","1 for 10",180.0,248.0,241.2,61.2,"SBK-N.JO",-25.4,"Standard Bank",2800.0,1),
    ("R029","RIGHTS_ISSUE","1 for 8",145.0,210.0,201.25,56.25,"NED-N.JO",-27.9,"Nedbank CIB",6000.0,1),
    ("R030","RIGHTS_ISSUE","1 for 10",3.20,4.60,4.45,1.25,"3988-N.HK",-28.1,"CICC",18000.0,1),
    ("R031","RIGHTS_ISSUE","1 for 5",32.0,48.0,44.8,12.8,"TEVA-N.TA",-28.6,"Bank Hapoalim",1500.0,1),
    ("R032","RIGHTS_ISSUE","1 for 8",3200.0,4800.0,4625.0,1425.0,"8316-N.T",-30.8,"Nomura",400000.0,1),
    ("R054","RIGHTS_ISSUE","1 for 6",12.0,18.5,17.58,5.58,"PGE-N.WA",-31.7,"PKO BP",4000.0,1),
]
c.executemany("INSERT OR IGNORE INTO rights_details VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", NEW_RIGHTS)

NEW_TENDERS = [
    ("R039","FIXED",620.0,None,None,588.0,5.4,8000000,600.0,1,60.0,None,0),
    ("R040","FIXED",10200.0,None,None,9750.0,4.6,3500000,2000.0,1,55.0,None,0),
    ("R041","FIXED",1850.0,None,None,1760.0,5.1,None,300000.0,1,58.0,None,0),
    ("R042","FIXED",32.0,None,None,30.2,6.0,None,20000.0,1,55.0,None,0),
    ("R043","FIXED",14.8,None,None,14.0,5.7,None,3000.0,1,60.0,None,0),
    ("R044","FIXED",195.0,None,None,184.0,6.0,None,5000.0,1,58.0,None,0),
    ("R045","FIXED",3400.0,None,None,3220.0,5.6,None,500000.0,1,55.0,None,0),
    ("R046","FIXED",105.0,None,None,99.5,5.5,None,3000.0,1,60.0,None,0),
    ("R047","FIXED",4200.0,None,None,3960.0,6.1,5000000,750.0,1,58.0,None,0),
    ("R051","FIXED",6.20,None,None,5.85,6.0,None,2000.0,1,55.0,None,0),
    ("R052","FIXED",750.0,None,None,712.0,5.3,1400000,1000.0,1,62.0,None,0),
]
c.executemany("INSERT OR IGNORE INTO tender_details VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", NEW_TENDERS)

NEW_MERGERS = [
    ("R033","SCHEME","Marriott International","MAR","CASH",3200.0,None,3140.0,1.91,d(22),d(210),"CLEARED","LOW"),
    ("R034","SCHEME","Apollo Global","APO","CASH",1050.0,None,1020.0,2.94,d(45),d(240),"PENDING","MEDIUM"),
    ("R035","SCHEME","BlackRock Inc","BLK","MIXED",2850.0,"0.08 BLK per SDR",2780.0,2.52,d(25),d(180),"CLEARED","LOW"),
    ("R036","SCHEME","Stellantis NV","STLAM","CASH",245.0,None,238.0,2.94,d(35),d(240),"PENDING","MEDIUM"),
    ("R037","MERGER","Richemont SA","CFR.SW","SHARES",None,"0.35 CFR per KER",720.0,None,None,d(180),"PENDING","HIGH"),
    ("R038","MERGER","MTN Group","MTN.JO","SHARES",None,"0.18 MTN per IAM",62.0,None,None,d(180),"PENDING","MEDIUM"),
    ("R048","SCHEME","Teva Acquirer",None,"CASH",18.50,None,17.80,3.93,d(22),d(210),"CLEARED","LOW"),
    ("R049","MERGER","INA Croatia",None,"CASH",3800.0,None,3680.0,3.26,None,d(180),"PENDING","HIGH"),
    ("R050","SCHEME","Orange SA","ORA.PA","CASH",28.50,None,27.20,4.78,d(20),d(210),"CLEARED","LOW"),
    ("R053","SCHEME","Undisclosed PE",None,"CASH",14.50,None,13.80,5.07,d(48),d(240),"PENDING","MEDIUM"),
]
c.executemany("INSERT OR IGNORE INTO merger_details VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)", NEW_MERGERS)

conn.commit()

total = c.execute("SELECT COUNT(*) FROM events").fetchone()[0]
print(f"Done. Total events: {total}")
for row in c.execute("SELECT event_type, COUNT(*) FROM events GROUP BY event_type ORDER BY COUNT(*) DESC"):
    print(f"  {row[0]:<30} {row[1]}")
conn.close()
