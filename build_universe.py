"""
build_universe.py
-----------------
Generates data/universe.csv — master company universe for the
Voluntary Corporate Actions Alpha Dashboard.

Coverage:
  UK        — FTSE 100
  US        — S&P 500 (live from Wikipedia)
  Europe    — Germany, France, Netherlands, Switzerland, Sweden,
               Italy, Spain, Denmark, Norway, Finland, Belgium,
               Portugal, Austria, Poland, Greece, Czech Republic,
               Hungary, Romania
  Middle East — Saudi Arabia, UAE, Qatar, Kuwait, Bahrain, Israel
  Africa    — South Africa, Egypt, Morocco, Nigeria, Kenya
  Turkey    — BIST 30

Run:  python build_universe.py
Out:  data/universe.csv
"""

import os
import pandas as pd

OUTPUT_DIR  = "data"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "universe.csv")
os.makedirs(OUTPUT_DIR, exist_ok=True)

COLS = ["company_name","ticker","currency","exchange",
        "country","index","sector","ticker_yfinance","has_adr","adr_ticker"]

# ── helpers ───────────────────────────────────────────────────────────────────
def rows(data):
    out = []
    for r in data:
        name, tkr, ccy, exch, ctry, idx, sec = r
        out.append(dict(company_name=name, ticker=tkr, currency=ccy,
                        exchange=exch, country=ctry, index=idx, sector=sec,
                        ticker_yfinance=tkr, has_adr=False, adr_ticker=""))
    return out


# ══════════════════════════════════════════════════════════════════════════════
# UK — FTSE 100
# ══════════════════════════════════════════════════════════════════════════════
FTSE100 = [
    ("3I Group PLC","III.L","GBX","LSE","UK","FTSE100","Financial Services"),
    ("Admiral Group PLC","ADM.L","GBX","LSE","UK","FTSE100","Insurance"),
    ("Airtel Africa PLC","AAF.L","GBX","LSE","UK","FTSE100","Telecom"),
    ("Alliance Witan PLC","ALW.L","GBX","LSE","UK","FTSE100","Investment Trust"),
    ("Anglo American PLC","AAL.L","GBX","LSE","UK","FTSE100","Mining"),
    ("Antofagasta PLC","ANTO.L","GBX","LSE","UK","FTSE100","Mining"),
    ("Ashtead Group PLC","AHT.L","GBX","LSE","UK","FTSE100","Industrials"),
    ("Associated British Foods PLC","ABF.L","GBX","LSE","UK","FTSE100","Consumer Staples"),
    ("AstraZeneca PLC","AZN.L","GBX","LSE","UK","FTSE100","Pharmaceuticals"),
    ("Auto Trader Group PLC","AUTO.L","GBX","LSE","UK","FTSE100","Technology"),
    ("Aviva PLC","AV.L","GBX","LSE","UK","FTSE100","Insurance"),
    ("BAE Systems PLC","BA.L","GBX","LSE","UK","FTSE100","Aerospace & Defence"),
    ("Barclays PLC","BARC.L","GBX","LSE","UK","FTSE100","Banking"),
    ("Barratt Redrow PLC","BTRW.L","GBX","LSE","UK","FTSE100","Housebuilding"),
    ("Beazley PLC","BEZ.L","GBX","LSE","UK","FTSE100","Insurance"),
    ("Berkeley Group Holdings PLC","BKG.L","GBX","LSE","UK","FTSE100","Housebuilding"),
    ("BP PLC","BP.L","GBX","LSE","UK","FTSE100","Energy"),
    ("British American Tobacco PLC","BATS.L","GBX","LSE","UK","FTSE100","Consumer Staples"),
    ("British Land Co PLC","BLND.L","GBX","LSE","UK","FTSE100","Real Estate"),
    ("BT Group PLC","BT-A.L","GBX","LSE","UK","FTSE100","Telecom"),
    ("Bunzl PLC","BNZL.L","GBX","LSE","UK","FTSE100","Industrials"),
    ("Centrica PLC","CNA.L","GBX","LSE","UK","FTSE100","Utilities"),
    ("Coca-Cola HBC AG","CCH.L","GBX","LSE","UK","FTSE100","Consumer Staples"),
    ("Compass Group PLC","CPG.L","GBX","LSE","UK","FTSE100","Consumer Services"),
    ("Convatec Group PLC","CTEC.L","GBX","LSE","UK","FTSE100","Healthcare"),
    ("Croda International PLC","CRDA.L","GBX","LSE","UK","FTSE100","Chemicals"),
    ("DCC PLC","DCC.L","GBX","LSE","UK","FTSE100","Industrials"),
    ("Diageo PLC","DGE.L","GBX","LSE","UK","FTSE100","Consumer Staples"),
    ("Diploma PLC","DPLM.L","GBX","LSE","UK","FTSE100","Industrials"),
    ("EasyJet PLC","EZJ.L","GBX","LSE","UK","FTSE100","Airlines"),
    ("Endeavour Mining PLC","EDV.L","GBX","LSE","UK","FTSE100","Mining"),
    ("Entain PLC","ENT.L","GBX","LSE","UK","FTSE100","Consumer Services"),
    ("Experian PLC","EXPN.L","GBX","LSE","UK","FTSE100","Technology"),
    ("F&C Investment Trust PLC","FCIT.L","GBX","LSE","UK","FTSE100","Investment Trust"),
    ("Fresnillo PLC","FRES.L","GBX","LSE","UK","FTSE100","Mining"),
    ("Games Workshop Group PLC","GAW.L","GBX","LSE","UK","FTSE100","Consumer Services"),
    ("Glencore PLC","GLEN.L","GBX","LSE","UK","FTSE100","Mining"),
    ("GSK PLC","GSK.L","GBX","LSE","UK","FTSE100","Pharmaceuticals"),
    ("Haleon PLC","HLN.L","GBX","LSE","UK","FTSE100","Consumer Healthcare"),
    ("Halma PLC","HLMA.L","GBX","LSE","UK","FTSE100","Industrials"),
    ("Hargreaves Lansdown PLC","HL.L","GBX","LSE","UK","FTSE100","Financial Services"),
    ("Hikma Pharmaceuticals PLC","HIK.L","GBX","LSE","UK","FTSE100","Pharmaceuticals"),
    ("Hiscox Ltd","HSX.L","GBX","LSE","UK","FTSE100","Insurance"),
    ("Howden Joinery Group PLC","HWDN.L","GBX","LSE","UK","FTSE100","Consumer Services"),
    ("HSBC Holdings PLC","HSBA.L","GBX","LSE","UK","FTSE100","Banking"),
    ("IMI PLC","IMI.L","GBX","LSE","UK","FTSE100","Industrials"),
    ("Imperial Brands PLC","IMB.L","GBX","LSE","UK","FTSE100","Consumer Staples"),
    ("Informa PLC","INF.L","GBX","LSE","UK","FTSE100","Media"),
    ("InterContinental Hotels Group PLC","IHG.L","GBX","LSE","UK","FTSE100","Consumer Services"),
    ("Intermediate Capital Group PLC","ICG.L","GBX","LSE","UK","FTSE100","Financial Services"),
    ("Intertek Group PLC","ITRK.L","GBX","LSE","UK","FTSE100","Industrials"),
    ("Intl Consolidated Airlines Group SA","IAG.L","GBX","LSE","UK","FTSE100","Airlines"),
    ("JD Sports Fashion PLC","JD.L","GBX","LSE","UK","FTSE100","Retail"),
    ("Kingfisher PLC","KGF.L","GBX","LSE","UK","FTSE100","Retail"),
    ("Land Securities Group PLC","LAND.L","GBX","LSE","UK","FTSE100","Real Estate"),
    ("Legal & General Group PLC","LGEN.L","GBX","LSE","UK","FTSE100","Insurance"),
    ("Lloyds Banking Group PLC","LLOY.L","GBX","LSE","UK","FTSE100","Banking"),
    ("London Stock Exchange Group PLC","LSEG.L","GBX","LSE","UK","FTSE100","Financial Services"),
    ("LondonMetric Property PLC","LMP.L","GBX","LSE","UK","FTSE100","Real Estate"),
    ("M&G PLC","MNG.L","GBX","LSE","UK","FTSE100","Financial Services"),
    ("Marks & Spencer Group PLC","MKS.L","GBX","LSE","UK","FTSE100","Retail"),
    ("Melrose Industries PLC","MRO.L","GBX","LSE","UK","FTSE100","Industrials"),
    ("Mondi PLC","MNDI.L","GBX","LSE","UK","FTSE100","Packaging"),
    ("National Grid PLC","NG.L","GBX","LSE","UK","FTSE100","Utilities"),
    ("NatWest Group PLC","NWG.L","GBX","LSE","UK","FTSE100","Banking"),
    ("Next PLC","NXT.L","GBX","LSE","UK","FTSE100","Retail"),
    ("Pearson PLC","PSON.L","GBX","LSE","UK","FTSE100","Media"),
    ("Pershing Square Holdings Ltd","PSH.L","GBX","LSE","UK","FTSE100","Investment Trust"),
    ("Persimmon PLC","PSN.L","GBX","LSE","UK","FTSE100","Housebuilding"),
    ("Phoenix Group Holdings PLC","PHNX.L","GBX","LSE","UK","FTSE100","Insurance"),
    ("Prudential PLC","PRU.L","GBX","LSE","UK","FTSE100","Insurance"),
    ("Reckitt Benckiser Group PLC","RKT.L","GBX","LSE","UK","FTSE100","Consumer Healthcare"),
    ("RELX PLC","REL.L","GBX","LSE","UK","FTSE100","Technology"),
    ("Rentokil Initial PLC","RTO.L","GBX","LSE","UK","FTSE100","Industrials"),
    ("Rightmove PLC","RMV.L","GBX","LSE","UK","FTSE100","Technology"),
    ("Rio Tinto PLC","RIO.L","GBX","LSE","UK","FTSE100","Mining"),
    ("Rolls-Royce Holdings PLC","RR.L","GBX","LSE","UK","FTSE100","Aerospace & Defence"),
    ("Sage Group PLC","SGE.L","GBX","LSE","UK","FTSE100","Technology"),
    ("J Sainsbury PLC","SBRY.L","GBX","LSE","UK","FTSE100","Retail"),
    ("Schroders PLC","SDR.L","GBX","LSE","UK","FTSE100","Financial Services"),
    ("Scottish Mortgage Investment Trust PLC","SMT.L","GBX","LSE","UK","FTSE100","Investment Trust"),
    ("Segro PLC","SGRO.L","GBX","LSE","UK","FTSE100","Real Estate"),
    ("Severn Trent PLC","SVT.L","GBX","LSE","UK","FTSE100","Utilities"),
    ("Shell PLC","SHEL.L","GBX","LSE","UK","FTSE100","Energy"),
    ("Smith & Nephew PLC","SN.L","GBX","LSE","UK","FTSE100","Healthcare"),
    ("DS Smith PLC","SMDS.L","GBX","LSE","UK","FTSE100","Packaging"),
    ("Smiths Group PLC","SMIN.L","GBX","LSE","UK","FTSE100","Industrials"),
    ("Spirax Group PLC","SPX.L","GBX","LSE","UK","FTSE100","Industrials"),
    ("SSE PLC","SSE.L","GBX","LSE","UK","FTSE100","Utilities"),
    ("St James's Place PLC","STJ.L","GBX","LSE","UK","FTSE100","Financial Services"),
    ("Standard Chartered PLC","STAN.L","GBX","LSE","UK","FTSE100","Banking"),
    ("Taylor Wimpey PLC","TW.L","GBX","LSE","UK","FTSE100","Housebuilding"),
    ("Tesco PLC","TSCO.L","GBX","LSE","UK","FTSE100","Retail"),
    ("Unilever PLC","ULVR.L","GBX","LSE","UK","FTSE100","Consumer Staples"),
    ("Unite Group PLC","UTG.L","GBX","LSE","UK","FTSE100","Real Estate"),
    ("United Utilities Group PLC","UU.L","GBX","LSE","UK","FTSE100","Utilities"),
    ("Vodafone Group PLC","VOD.L","GBX","LSE","UK","FTSE100","Telecom"),
    ("Weir Group PLC","WEIR.L","GBX","LSE","UK","FTSE100","Industrials"),
    ("Whitbread PLC","WTB.L","GBX","LSE","UK","FTSE100","Consumer Services"),
    ("WPP PLC","WPP.L","GBX","LSE","UK","FTSE100","Media"),
]

# ══════════════════════════════════════════════════════════════════════════════
# EUROPE
# ══════════════════════════════════════════════════════════════════════════════
EUROPE = [
    # ── Germany DAX 40 ────────────────────────────────────────────────────────
    ("SAP SE","SAP.DE","EUR","XETRA","Germany","DAX40","Technology"),
    ("Siemens AG","SIE.DE","EUR","XETRA","Germany","DAX40","Industrials"),
    ("Allianz SE","ALV.DE","EUR","XETRA","Germany","DAX40","Insurance"),
    ("Deutsche Telekom AG","DTE.DE","EUR","XETRA","Germany","DAX40","Telecom"),
    ("BMW AG","BMW.DE","EUR","XETRA","Germany","DAX40","Automotive"),
    ("BASF SE","BAS.DE","EUR","XETRA","Germany","DAX40","Chemicals"),
    ("Volkswagen AG","VOW3.DE","EUR","XETRA","Germany","DAX40","Automotive"),
    ("Bayer AG","BAYN.DE","EUR","XETRA","Germany","DAX40","Pharmaceuticals"),
    ("Mercedes-Benz Group AG","MBG.DE","EUR","XETRA","Germany","DAX40","Automotive"),
    ("Deutsche Bank AG","DBK.DE","EUR","XETRA","Germany","DAX40","Banking"),
    ("Muenchener Rueckversicherungs AG","MUV2.DE","EUR","XETRA","Germany","DAX40","Insurance"),
    ("Infineon Technologies AG","IFX.DE","EUR","XETRA","Germany","DAX40","Technology"),
    ("Linde PLC","LIN.DE","EUR","XETRA","Germany","DAX40","Chemicals"),
    ("Airbus SE","AIR.DE","EUR","XETRA","Germany","DAX40","Aerospace & Defence"),
    ("Daimler Truck Holding AG","DTG.DE","EUR","XETRA","Germany","DAX40","Industrials"),
    ("Deutsche Boerse AG","DB1.DE","EUR","XETRA","Germany","DAX40","Financial Services"),
    ("E.ON SE","EOAN.DE","EUR","XETRA","Germany","DAX40","Utilities"),
    ("RWE AG","RWE.DE","EUR","XETRA","Germany","DAX40","Utilities"),
    ("Commerzbank AG","CBK.DE","EUR","XETRA","Germany","DAX40","Banking"),
    ("Hannover Rueck SE","HNR1.DE","EUR","XETRA","Germany","DAX40","Insurance"),
    ("Heidelberg Materials AG","HDMG.DE","EUR","XETRA","Germany","DAX40","Materials"),
    ("Merck KGaA","MRK.DE","EUR","XETRA","Germany","DAX40","Pharmaceuticals"),
    ("MTU Aero Engines AG","MTX.DE","EUR","XETRA","Germany","DAX40","Aerospace & Defence"),
    ("Porsche Automobil Holding SE","PAH3.DE","EUR","XETRA","Germany","DAX40","Automotive"),
    ("Rheinmetall AG","RHM.DE","EUR","XETRA","Germany","DAX40","Aerospace & Defence"),
    ("Sartorius AG","SRT3.DE","EUR","XETRA","Germany","DAX40","Healthcare"),
    ("Siemens Energy AG","ENR.DE","EUR","XETRA","Germany","DAX40","Energy"),
    ("Siemens Healthineers AG","SHL.DE","EUR","XETRA","Germany","DAX40","Healthcare"),
    ("Vonovia SE","VNA.DE","EUR","XETRA","Germany","DAX40","Real Estate"),
    ("Zalando SE","ZAL.DE","EUR","XETRA","Germany","DAX40","Retail"),

    # ── France CAC 40 ─────────────────────────────────────────────────────────
    ("LVMH Moet Hennessy Louis Vuitton SE","MC.PA","EUR","Euronext Paris","France","CAC40","Luxury"),
    ("TotalEnergies SE","TTE.PA","EUR","Euronext Paris","France","CAC40","Energy"),
    ("Hermes International SCA","RMS.PA","EUR","Euronext Paris","France","CAC40","Luxury"),
    ("Sanofi SA","SAN.PA","EUR","Euronext Paris","France","CAC40","Pharmaceuticals"),
    ("BNP Paribas SA","BNP.PA","EUR","Euronext Paris","France","CAC40","Banking"),
    ("Schneider Electric SE","SU.PA","EUR","Euronext Paris","France","CAC40","Industrials"),
    ("L'Oreal SA","OR.PA","EUR","Euronext Paris","France","CAC40","Consumer Staples"),
    ("AXA SA","CS.PA","EUR","Euronext Paris","France","CAC40","Insurance"),
    ("EssilorLuxottica SA","EL.PA","EUR","Euronext Paris","France","CAC40","Healthcare"),
    ("Safran SA","SAF.PA","EUR","Euronext Paris","France","CAC40","Aerospace & Defence"),
    ("Air Liquide SA","AI.PA","EUR","Euronext Paris","France","CAC40","Chemicals"),
    ("Danone SA","BN.PA","EUR","Euronext Paris","France","CAC40","Consumer Staples"),
    ("Kering SA","KER.PA","EUR","Euronext Paris","France","CAC40","Luxury"),
    ("Vinci SA","DG.PA","EUR","Euronext Paris","France","CAC40","Industrials"),
    ("Societe Generale SA","GLE.PA","EUR","Euronext Paris","France","CAC40","Banking"),
    ("Credit Agricole SA","ACA.PA","EUR","Euronext Paris","France","CAC40","Banking"),
    ("Capgemini SE","CAP.PA","EUR","Euronext Paris","France","CAC40","Technology"),
    ("Compagnie de Saint-Gobain SA","SGO.PA","EUR","Euronext Paris","France","CAC40","Materials"),
    ("Dassault Systemes SE","DSY.PA","EUR","Euronext Paris","France","CAC40","Technology"),
    ("Legrand SA","LR.PA","EUR","Euronext Paris","France","CAC40","Industrials"),
    ("Michelin SCA","ML.PA","EUR","Euronext Paris","France","CAC40","Automotive"),
    ("Pernod Ricard SA","RI.PA","EUR","Euronext Paris","France","CAC40","Consumer Staples"),
    ("Publicis Groupe SA","PUB.PA","EUR","Euronext Paris","France","CAC40","Media"),
    ("Renault SA","RNO.PA","EUR","Euronext Paris","France","CAC40","Automotive"),
    ("Stellantis NV","STLAM.PA","EUR","Euronext Paris","France","CAC40","Automotive"),
    ("STMicroelectronics NV","STM.PA","EUR","Euronext Paris","France","CAC40","Technology"),
    ("Teleperformance SE","TEP.PA","EUR","Euronext Paris","France","CAC40","Technology"),
    ("Thales SA","HO.PA","EUR","Euronext Paris","France","CAC40","Aerospace & Defence"),
    ("Unibail-Rodamco-Westfield SE","URW.PA","EUR","Euronext Paris","France","CAC40","Real Estate"),
    ("Veolia Environnement SA","VIE.PA","EUR","Euronext Paris","France","CAC40","Utilities"),

    # ── Netherlands AEX ───────────────────────────────────────────────────────
    ("ASML Holding NV","ASML.AS","EUR","Euronext Amsterdam","Netherlands","AEX25","Technology"),
    ("ING Groep NV","INGA.AS","EUR","Euronext Amsterdam","Netherlands","AEX25","Banking"),
    ("Heineken NV","HEIA.AS","EUR","Euronext Amsterdam","Netherlands","AEX25","Consumer Staples"),
    ("Wolters Kluwer NV","WKL.AS","EUR","Euronext Amsterdam","Netherlands","AEX25","Technology"),
    ("Philips NV","PHIA.AS","EUR","Euronext Amsterdam","Netherlands","AEX25","Healthcare"),
    ("NN Group NV","NN.AS","EUR","Euronext Amsterdam","Netherlands","AEX25","Insurance"),
    ("Randstad NV","RAND.AS","EUR","Euronext Amsterdam","Netherlands","AEX25","Industrials"),
    ("ABN AMRO Bank NV","ABN.AS","EUR","Euronext Amsterdam","Netherlands","AEX25","Banking"),
    ("Aegon NV","AGN.AS","EUR","Euronext Amsterdam","Netherlands","AEX25","Insurance"),
    ("Adyen NV","ADYEN.AS","EUR","Euronext Amsterdam","Netherlands","AEX25","Technology"),
    ("Akzo Nobel NV","AKZA.AS","EUR","Euronext Amsterdam","Netherlands","AEX25","Chemicals"),
    ("ArcelorMittal SA","MT.AS","EUR","Euronext Amsterdam","Netherlands","AEX25","Materials"),
    ("ASM International NV","ASMI.AS","EUR","Euronext Amsterdam","Netherlands","AEX25","Technology"),
    ("BE Semiconductor Industries NV","BESI.AS","EUR","Euronext Amsterdam","Netherlands","AEX25","Technology"),
    ("DSM-Firmenich AG","DSFIR.AS","EUR","Euronext Amsterdam","Netherlands","AEX25","Chemicals"),

    # ── Switzerland SMI ───────────────────────────────────────────────────────
    ("Nestle SA","NESN.SW","CHF","SIX","Switzerland","SMI20","Consumer Staples"),
    ("Novartis AG","NOVN.SW","CHF","SIX","Switzerland","SMI20","Pharmaceuticals"),
    ("Roche Holding AG","ROG.SW","CHF","SIX","Switzerland","SMI20","Pharmaceuticals"),
    ("ABB Ltd","ABBN.SW","CHF","SIX","Switzerland","SMI20","Industrials"),
    ("Zurich Insurance Group AG","ZURN.SW","CHF","SIX","Switzerland","SMI20","Insurance"),
    ("Cie Financiere Richemont SA","CFR.SW","CHF","SIX","Switzerland","SMI20","Luxury"),
    ("Lonza Group AG","LONN.SW","CHF","SIX","Switzerland","SMI20","Pharmaceuticals"),
    ("UBS Group AG","UBSG.SW","CHF","SIX","Switzerland","SMI20","Banking"),
    ("Swiss Re AG","SREN.SW","CHF","SIX","Switzerland","SMI20","Insurance"),
    ("Holcim Ltd","HOLN.SW","CHF","SIX","Switzerland","SMI20","Materials"),
    ("Geberit AG","GEBN.SW","CHF","SIX","Switzerland","SMI20","Industrials"),
    ("Givaudan SA","GIVN.SW","CHF","SIX","Switzerland","SMI20","Chemicals"),
    ("Kuehne + Nagel International AG","KNIN.SW","CHF","SIX","Switzerland","SMI20","Industrials"),
    ("Partners Group Holding AG","PGHN.SW","CHF","SIX","Switzerland","SMI20","Financial Services"),
    ("Sika AG","SIKA.SW","CHF","SIX","Switzerland","SMI20","Chemicals"),

    # ── Sweden OMX30 ──────────────────────────────────────────────────────────
    ("Atlas Copco AB","ATCO-A.ST","SEK","OMX Stockholm","Sweden","OMX30","Industrials"),
    ("Investor AB","INVE-B.ST","SEK","OMX Stockholm","Sweden","OMX30","Financial Services"),
    ("Volvo AB","VOLV-B.ST","SEK","OMX Stockholm","Sweden","OMX30","Industrials"),
    ("Telefonaktiebolaget LM Ericsson","ERIC-B.ST","SEK","OMX Stockholm","Sweden","OMX30","Technology"),
    ("H & M Hennes & Mauritz AB","HM-B.ST","SEK","OMX Stockholm","Sweden","OMX30","Retail"),
    ("Nordea Bank Abp","NDA-SE.ST","SEK","OMX Stockholm","Sweden","OMX30","Banking"),
    ("Sandvik AB","SAND.ST","SEK","OMX Stockholm","Sweden","OMX30","Industrials"),
    ("Hexagon AB","HEXA-B.ST","SEK","OMX Stockholm","Sweden","OMX30","Technology"),
    ("Alfa Laval AB","ALFA.ST","SEK","OMX Stockholm","Sweden","OMX30","Industrials"),
    ("Svenska Handelsbanken AB","SHB-A.ST","SEK","OMX Stockholm","Sweden","OMX30","Banking"),
    ("Essity AB","ESSITY-B.ST","SEK","OMX Stockholm","Sweden","OMX30","Consumer Staples"),
    ("Evolution AB","EVO.ST","SEK","OMX Stockholm","Sweden","OMX30","Technology"),
    ("Getinge AB","GETI-B.ST","SEK","OMX Stockholm","Sweden","OMX30","Healthcare"),
    ("Industrivarden AB","INDU-A.ST","SEK","OMX Stockholm","Sweden","OMX30","Financial Services"),
    ("SKF AB","SKF-B.ST","SEK","OMX Stockholm","Sweden","OMX30","Industrials"),
    ("Swedbank AB","SWED-A.ST","SEK","OMX Stockholm","Sweden","OMX30","Banking"),
    ("Tele2 AB","TEL2-B.ST","SEK","OMX Stockholm","Sweden","OMX30","Telecom"),
    ("Volvo Cars AB","VOLCAR-B.ST","SEK","OMX Stockholm","Sweden","OMX30","Automotive"),

    # ── Italy FTSE MIB ────────────────────────────────────────────────────────
    ("Enel SpA","ENEL.MI","EUR","Borsa Italiana","Italy","FTSEMIB","Utilities"),
    ("ENI SpA","ENI.MI","EUR","Borsa Italiana","Italy","FTSEMIB","Energy"),
    ("Intesa Sanpaolo SpA","ISP.MI","EUR","Borsa Italiana","Italy","FTSEMIB","Banking"),
    ("UniCredit SpA","UCG.MI","EUR","Borsa Italiana","Italy","FTSEMIB","Banking"),
    ("Ferrari NV","RACE.MI","EUR","Borsa Italiana","Italy","FTSEMIB","Automotive"),
    ("Assicurazioni Generali SpA","G.MI","EUR","Borsa Italiana","Italy","FTSEMIB","Insurance"),
    ("Leonardo SpA","LDO.MI","EUR","Borsa Italiana","Italy","FTSEMIB","Aerospace & Defence"),
    ("Prysmian SpA","PRY.MI","EUR","Borsa Italiana","Italy","FTSEMIB","Industrials"),
    ("Moncler SpA","MONC.MI","EUR","Borsa Italiana","Italy","FTSEMIB","Luxury"),
    ("Mediobanca SpA","MB.MI","EUR","Borsa Italiana","Italy","FTSEMIB","Banking"),
    ("Banco BPM SpA","BAMI.MI","EUR","Borsa Italiana","Italy","FTSEMIB","Banking"),
    ("BPER Banca SpA","BPE.MI","EUR","Borsa Italiana","Italy","FTSEMIB","Banking"),
    ("Davide Campari-Milano NV","CPR.MI","EUR","Borsa Italiana","Italy","FTSEMIB","Consumer Staples"),
    ("DiaSorin SpA","DIA.MI","EUR","Borsa Italiana","Italy","FTSEMIB","Healthcare"),
    ("Italgas SpA","IG.MI","EUR","Borsa Italiana","Italy","FTSEMIB","Utilities"),
    ("Nexi SpA","NEXI.MI","EUR","Borsa Italiana","Italy","FTSEMIB","Technology"),
    ("Recordati SpA","REC.MI","EUR","Borsa Italiana","Italy","FTSEMIB","Pharmaceuticals"),
    ("Saipem SpA","SPM.MI","EUR","Borsa Italiana","Italy","FTSEMIB","Energy"),
    ("Snam SpA","SRG.MI","EUR","Borsa Italiana","Italy","FTSEMIB","Utilities"),
    ("Telecom Italia SpA","TIT.MI","EUR","Borsa Italiana","Italy","FTSEMIB","Telecom"),

    # ── Spain IBEX 35 ─────────────────────────────────────────────────────────
    ("Inditex SA","ITX.MC","EUR","BME","Spain","IBEX35","Retail"),
    ("Banco Santander SA","SAN.MC","EUR","BME","Spain","IBEX35","Banking"),
    ("BBVA SA","BBVA.MC","EUR","BME","Spain","IBEX35","Banking"),
    ("Iberdrola SA","IBE.MC","EUR","BME","Spain","IBEX35","Utilities"),
    ("CaixaBank SA","CABK.MC","EUR","BME","Spain","IBEX35","Banking"),
    ("Telefonica SA","TEF.MC","EUR","BME","Spain","IBEX35","Telecom"),
    ("Amadeus IT Group SA","AMS.MC","EUR","BME","Spain","IBEX35","Technology"),
    ("Repsol SA","REP.MC","EUR","BME","Spain","IBEX35","Energy"),
    ("Ferrovial SE","FER.MC","EUR","BME","Spain","IBEX35","Industrials"),
    ("ACS Actividades de Construccion","ACS.MC","EUR","BME","Spain","IBEX35","Industrials"),
    ("Acciona SA","ANA.MC","EUR","BME","Spain","IBEX35","Utilities"),
    ("Aena SME SA","AENA.MC","EUR","BME","Spain","IBEX35","Industrials"),
    ("ArcelorMittal SA","MTS.MC","EUR","BME","Spain","IBEX35","Materials"),
    ("Bankinter SA","BKT.MC","EUR","BME","Spain","IBEX35","Banking"),
    ("Colonial Inmobiliaria SA","COL.MC","EUR","BME","Spain","IBEX35","Real Estate"),

    # ── Denmark OMX25 ─────────────────────────────────────────────────────────
    ("Novo Nordisk A/S","NOVO-B.CO","DKK","OMX Copenhagen","Denmark","OMX25","Pharmaceuticals"),
    ("Vestas Wind Systems A/S","VWS.CO","DKK","OMX Copenhagen","Denmark","OMX25","Energy"),
    ("Orsted A/S","ORSTED.CO","DKK","OMX Copenhagen","Denmark","OMX25","Utilities"),
    ("A.P. Moller Maersk A/S","MAERSK-B.CO","DKK","OMX Copenhagen","Denmark","OMX25","Industrials"),
    ("DSV A/S","DSV.CO","DKK","OMX Copenhagen","Denmark","OMX25","Industrials"),
    ("Coloplast A/S","COLO-B.CO","DKK","OMX Copenhagen","Denmark","OMX25","Healthcare"),
    ("Demant A/S","DEMANT.CO","DKK","OMX Copenhagen","Denmark","OMX25","Healthcare"),
    ("GN Store Nord A/S","GN.CO","DKK","OMX Copenhagen","Denmark","OMX25","Technology"),
    ("Genmab A/S","GMAB.CO","DKK","OMX Copenhagen","Denmark","OMX25","Pharmaceuticals"),
    ("Tryg A/S","TRYG.CO","DKK","OMX Copenhagen","Denmark","OMX25","Insurance"),

    # ── Norway OBX ────────────────────────────────────────────────────────────
    ("Equinor ASA","EQNR.OL","NOK","Oslo Bors","Norway","OBX25","Energy"),
    ("Norsk Hydro ASA","NHY.OL","NOK","Oslo Bors","Norway","OBX25","Materials"),
    ("Telenor ASA","TEL.OL","NOK","Oslo Bors","Norway","OBX25","Telecom"),
    ("DNB Bank ASA","DNB.OL","NOK","Oslo Bors","Norway","OBX25","Banking"),
    ("Mowi ASA","MOWI.OL","NOK","Oslo Bors","Norway","OBX25","Consumer Staples"),
    ("Aker BP ASA","AKRBP.OL","NOK","Oslo Bors","Norway","OBX25","Energy"),
    ("Kongsberg Gruppen ASA","KOG.OL","NOK","Oslo Bors","Norway","OBX25","Aerospace & Defence"),
    ("Salmar ASA","SALM.OL","NOK","Oslo Bors","Norway","OBX25","Consumer Staples"),
    ("Schibsted ASA","SCHB.OL","NOK","Oslo Bors","Norway","OBX25","Media"),
    ("Storebrand ASA","STB.OL","NOK","Oslo Bors","Norway","OBX25","Insurance"),

    # ── Finland OMX Helsinki ──────────────────────────────────────────────────
    ("Nokia Oyj","NOKIA.HE","EUR","OMX Helsinki","Finland","OMX25FI","Technology"),
    ("Kone Oyj","KNEBV.HE","EUR","OMX Helsinki","Finland","OMX25FI","Industrials"),
    ("Sampo Oyj","SAMPO.HE","EUR","OMX Helsinki","Finland","OMX25FI","Insurance"),
    ("Neste Oyj","NESTE.HE","EUR","OMX Helsinki","Finland","OMX25FI","Energy"),
    ("Metso Oyj","METSO.HE","EUR","OMX Helsinki","Finland","OMX25FI","Industrials"),
    ("Fortum Oyj","FORTUM.HE","EUR","OMX Helsinki","Finland","OMX25FI","Utilities"),
    ("Kesko Oyj","KESKOV.HE","EUR","OMX Helsinki","Finland","OMX25FI","Retail"),
    ("Outokumpu Oyj","OUT1V.HE","EUR","OMX Helsinki","Finland","OMX25FI","Materials"),
    ("Stora Enso Oyj","STERV.HE","EUR","OMX Helsinki","Finland","OMX25FI","Materials"),
    ("UPM-Kymmene Oyj","UPM.HE","EUR","OMX Helsinki","Finland","OMX25FI","Materials"),

    # ── Belgium BEL 20 ────────────────────────────────────────────────────────
    ("Anheuser-Busch InBev SA","ABI.BR","EUR","Euronext Brussels","Belgium","BEL20","Consumer Staples"),
    ("KBC Group NV","KBC.BR","EUR","Euronext Brussels","Belgium","BEL20","Banking"),
    ("UCB SA","UCB.BR","EUR","Euronext Brussels","Belgium","BEL20","Pharmaceuticals"),
    ("Solvay SA","SOLB.BR","EUR","Euronext Brussels","Belgium","BEL20","Chemicals"),
    ("Ageas SA","AGS.BR","EUR","Euronext Brussels","Belgium","BEL20","Insurance"),
    ("Colruyt Group NV","COLR.BR","EUR","Euronext Brussels","Belgium","BEL20","Retail"),
    ("Elia Group SA","ELI.BR","EUR","Euronext Brussels","Belgium","BEL20","Utilities"),
    ("Proximus PLC","PROX.BR","EUR","Euronext Brussels","Belgium","BEL20","Telecom"),
    ("Sofina SA","SOF.BR","EUR","Euronext Brussels","Belgium","BEL20","Financial Services"),
    ("Umicore SA","UMI.BR","EUR","Euronext Brussels","Belgium","BEL20","Materials"),

    # ── Portugal PSI ──────────────────────────────────────────────────────────
    ("EDP - Energias de Portugal SA","EDP.LS","EUR","Euronext Lisbon","Portugal","PSI20","Utilities"),
    ("Galp Energia SGPS SA","GALP.LS","EUR","Euronext Lisbon","Portugal","PSI20","Energy"),
    ("Jeronimo Martins SGPS SA","JMT.LS","EUR","Euronext Lisbon","Portugal","PSI20","Retail"),
    ("Banco Comercial Portugues SA","BCP.LS","EUR","Euronext Lisbon","Portugal","PSI20","Banking"),
    ("Sonae SGPS SA","SON.LS","EUR","Euronext Lisbon","Portugal","PSI20","Retail"),
    ("NOS SGPS SA","NOS.LS","EUR","Euronext Lisbon","Portugal","PSI20","Telecom"),
    ("REN - Redes Energeticas Nacionais SA","RENE.LS","EUR","Euronext Lisbon","Portugal","PSI20","Utilities"),
    ("The Navigator Company SA","NVG.LS","EUR","Euronext Lisbon","Portugal","PSI20","Materials"),
    ("Corticeira Amorim SGPS SA","COR.LS","EUR","Euronext Lisbon","Portugal","PSI20","Materials"),
    ("Semapa SA","SEM.LS","EUR","Euronext Lisbon","Portugal","PSI20","Industrials"),

    # ── Austria ATX ───────────────────────────────────────────────────────────
    ("OMV AG","OMV.VI","EUR","Vienna Stock Exchange","Austria","ATX20","Energy"),
    ("Verbund AG","VER.VI","EUR","Vienna Stock Exchange","Austria","ATX20","Utilities"),
    ("Erste Group Bank AG","EBS.VI","EUR","Vienna Stock Exchange","Austria","ATX20","Banking"),
    ("Raiffeisen Bank International AG","RBI.VI","EUR","Vienna Stock Exchange","Austria","ATX20","Banking"),
    ("Andritz AG","ANDR.VI","EUR","Vienna Stock Exchange","Austria","ATX20","Industrials"),
    ("voestalpine AG","VOE.VI","EUR","Vienna Stock Exchange","Austria","ATX20","Materials"),
    ("Vienna Insurance Group AG","VIG.VI","EUR","Vienna Stock Exchange","Austria","ATX20","Insurance"),
    ("Oesterreichische Post AG","POST.VI","EUR","Vienna Stock Exchange","Austria","ATX20","Industrials"),
    ("EVN AG","EVN.VI","EUR","Vienna Stock Exchange","Austria","ATX20","Utilities"),
    ("Frequentis AG","FQT.VI","EUR","Vienna Stock Exchange","Austria","ATX20","Technology"),

    # ── Poland WIG 20 ─────────────────────────────────────────────────────────
    ("PKN Orlen SA","PKN.WA","PLN","Warsaw Stock Exchange","Poland","WIG20","Energy"),
    ("PKO Bank Polski SA","PKO.WA","PLN","Warsaw Stock Exchange","Poland","WIG20","Banking"),
    ("Bank Pekao SA","PEO.WA","PLN","Warsaw Stock Exchange","Poland","WIG20","Banking"),
    ("KGHM Polska Miedz SA","KGH.WA","PLN","Warsaw Stock Exchange","Poland","WIG20","Mining"),
    ("Allegro.eu SA","ALE.WA","PLN","Warsaw Stock Exchange","Poland","WIG20","Retail"),
    ("Dino Polska SA","DNP.WA","PLN","Warsaw Stock Exchange","Poland","WIG20","Retail"),
    ("LPP SA","LPP.WA","PLN","Warsaw Stock Exchange","Poland","WIG20","Retail"),
    ("Santander Bank Polska SA","SPL.WA","PLN","Warsaw Stock Exchange","Poland","WIG20","Banking"),
    ("mBank SA","MBK.WA","PLN","Warsaw Stock Exchange","Poland","WIG20","Banking"),
    ("PZU SA","PZU.WA","PLN","Warsaw Stock Exchange","Poland","WIG20","Insurance"),
    ("CD Projekt SA","CDR.WA","PLN","Warsaw Stock Exchange","Poland","WIG20","Technology"),
    ("PGE Polska Grupa Energetyczna SA","PGE.WA","PLN","Warsaw Stock Exchange","Poland","WIG20","Utilities"),
    ("Cyfrowy Polsat SA","CPS.WA","PLN","Warsaw Stock Exchange","Poland","WIG20","Media"),
    ("Orange Polska SA","OPL.WA","PLN","Warsaw Stock Exchange","Poland","WIG20","Telecom"),
    ("Asseco Poland SA","APC.WA","PLN","Warsaw Stock Exchange","Poland","WIG20","Technology"),

    # ── Greece ATHEX ──────────────────────────────────────────────────────────
    ("National Bank of Greece SA","ETE.AT","EUR","Athens Stock Exchange","Greece","ATHEX25","Banking"),
    ("Alpha Services and Holdings SA","ALPHA.AT","EUR","Athens Stock Exchange","Greece","ATHEX25","Banking"),
    ("Piraeus Financial Holdings SA","TPEIR.AT","EUR","Athens Stock Exchange","Greece","ATHEX25","Banking"),
    ("Eurobank Ergasias Services SA","EUROB.AT","EUR","Athens Stock Exchange","Greece","ATHEX25","Banking"),
    ("Mytilineos Holdings SA","MYTIL.AT","EUR","Athens Stock Exchange","Greece","ATHEX25","Industrials"),
    ("Motor Oil Hellas SA","MOH.AT","EUR","Athens Stock Exchange","Greece","ATHEX25","Energy"),
    ("Hellenic Petroleum SA","ELPE.AT","EUR","Athens Stock Exchange","Greece","ATHEX25","Energy"),
    ("OTE SA","OTE.AT","EUR","Athens Stock Exchange","Greece","ATHEX25","Telecom"),
    ("OPAP SA","OPAP.AT","EUR","Athens Stock Exchange","Greece","ATHEX25","Consumer Services"),
    ("Titan Cement International SA","TITC.AT","EUR","Athens Stock Exchange","Greece","ATHEX25","Materials"),
    ("Public Power Corporation SA","PPC.AT","EUR","Athens Stock Exchange","Greece","ATHEX25","Utilities"),
    ("Jumbo SA","BELA.AT","EUR","Athens Stock Exchange","Greece","ATHEX25","Retail"),

    # ── Czech Republic PX ─────────────────────────────────────────────────────
    ("CEZ AS","CEZ.PR","CZK","Prague Stock Exchange","Czech Republic","PX14","Utilities"),
    ("Komercni Banka AS","KOMB.PR","CZK","Prague Stock Exchange","Czech Republic","PX14","Banking"),
    ("O2 Czech Republic AS","TELEC.PR","CZK","Prague Stock Exchange","Czech Republic","PX14","Telecom"),
    ("Moneta Money Bank AS","MONET.PR","CZK","Prague Stock Exchange","Czech Republic","PX14","Banking"),
    ("Philip Morris CR AS","TABAK.PR","CZK","Prague Stock Exchange","Czech Republic","PX14","Consumer Staples"),

    # ── Hungary BUX ───────────────────────────────────────────────────────────
    ("OTP Bank Nyrt","OTP.BD","HUF","Budapest Stock Exchange","Hungary","BUX","Banking"),
    ("MOL Magyar Olaj-es Gazipari Nyrt","MOL.BD","HUF","Budapest Stock Exchange","Hungary","BUX","Energy"),
    ("Gedeon Richter Nyrt","RICHTER.BD","HUF","Budapest Stock Exchange","Hungary","BUX","Pharmaceuticals"),
    ("Magyar Telekom Nyrt","MTELEKOM.BD","HUF","Budapest Stock Exchange","Hungary","BUX","Telecom"),
    ("Opus Global Nyrt","OPUS.BD","HUF","Budapest Stock Exchange","Hungary","BUX","Industrials"),

    # ── Romania BET ───────────────────────────────────────────────────────────
    ("Banca Transilvania SA","TLV.RO","RON","Bucharest Stock Exchange","Romania","BET10","Banking"),
    ("OMV Petrom SA","SNP.RO","RON","Bucharest Stock Exchange","Romania","BET10","Energy"),
    ("Romgaz SA","SNG.RO","RON","Bucharest Stock Exchange","Romania","BET10","Energy"),
    ("Transgaz SA","TGN.RO","RON","Bucharest Stock Exchange","Romania","BET10","Utilities"),
    ("Transelectrica SA","TEL.RO","RON","Bucharest Stock Exchange","Romania","BET10","Utilities"),
    ("BRD - Groupe Societe Generale SA","BRD.RO","RON","Bucharest Stock Exchange","Romania","BET10","Banking"),
    ("Electrica SA","EL.RO","RON","Bucharest Stock Exchange","Romania","BET10","Utilities"),
    ("MedLife SA","M.RO","RON","Bucharest Stock Exchange","Romania","BET10","Healthcare"),
]

# ══════════════════════════════════════════════════════════════════════════════
# TURKEY — BIST 30
# ══════════════════════════════════════════════════════════════════════════════
TURKEY = [
    ("Garanti BBVA AS","GARAN.IS","TRY","Borsa Istanbul","Turkey","BIST30","Banking"),
    ("Akbank TAS","AKBNK.IS","TRY","Borsa Istanbul","Turkey","BIST30","Banking"),
    ("Turkiye Is Bankasi AS","ISCTR.IS","TRY","Borsa Istanbul","Turkey","BIST30","Banking"),
    ("Yapi ve Kredi Bankasi AS","YKBNK.IS","TRY","Borsa Istanbul","Turkey","BIST30","Banking"),
    ("Halkbank AS","HALKB.IS","TRY","Borsa Istanbul","Turkey","BIST30","Banking"),
    ("Vakifbank AS","VAKBN.IS","TRY","Borsa Istanbul","Turkey","BIST30","Banking"),
    ("Turkcell Iletisim Hizmetleri AS","TCELL.IS","TRY","Borsa Istanbul","Turkey","BIST30","Telecom"),
    ("Turk Telekomunikasyon AS","TTKOM.IS","TRY","Borsa Istanbul","Turkey","BIST30","Telecom"),
    ("BIM Birlesik Magazalar AS","BIMAS.IS","TRY","Borsa Istanbul","Turkey","BIST30","Retail"),
    ("Koc Holding AS","KCHOL.IS","TRY","Borsa Istanbul","Turkey","BIST30","Financial Services"),
    ("Sabanci Holding AS","SAHOL.IS","TRY","Borsa Istanbul","Turkey","BIST30","Financial Services"),
    ("Eregli Demir ve Celik Fabrikalari AS","EREGL.IS","TRY","Borsa Istanbul","Turkey","BIST30","Materials"),
    ("Turk Hava Yollari AS","THYAO.IS","TRY","Borsa Istanbul","Turkey","BIST30","Airlines"),
    ("Aselsan Elektronik Sanayi ve Tic AS","ASELS.IS","TRY","Borsa Istanbul","Turkey","BIST30","Aerospace & Defence"),
    ("Arcelik AS","ARCLK.IS","TRY","Borsa Istanbul","Turkey","BIST30","Consumer Staples"),
    ("Ford Otomotiv Sanayi AS","FROTO.IS","TRY","Borsa Istanbul","Turkey","BIST30","Automotive"),
    ("Tupras Turkiye Petrol Rafinerileri AS","TUPRS.IS","TRY","Borsa Istanbul","Turkey","BIST30","Energy"),
    ("Enerjisa Enerji AS","ENJSA.IS","TRY","Borsa Istanbul","Turkey","BIST30","Utilities"),
    ("Emlak Konut GYO AS","EKGYO.IS","TRY","Borsa Istanbul","Turkey","BIST30","Real Estate"),
    ("Migros Ticaret AS","MGROS.IS","TRY","Borsa Istanbul","Turkey","BIST30","Retail"),
    ("Sise ve Cam Fabrikalari AS","SISE.IS","TRY","Borsa Istanbul","Turkey","BIST30","Materials"),
    ("TAV Havalimanlari Holding AS","TAVHL.IS","TRY","Borsa Istanbul","Turkey","BIST30","Industrials"),
    ("Torunlar GYO AS","TRGYO.IS","TRY","Borsa Istanbul","Turkey","BIST30","Real Estate"),
    ("Petkim Petrokimya Holding AS","PETKM.IS","TRY","Borsa Istanbul","Turkey","BIST30","Chemicals"),
    ("Zorlu Enerji Elektrik Uretim AS","ZOREN.IS","TRY","Borsa Istanbul","Turkey","BIST30","Utilities"),
]

# ══════════════════════════════════════════════════════════════════════════════
# MIDDLE EAST — Saudi Arabia, UAE, Qatar, Kuwait, Bahrain, Israel
# ══════════════════════════════════════════════════════════════════════════════
MIDDLE_EAST = [
    # ── Saudi Arabia TASI (top 30 by market cap) ──────────────────────────────
    ("Saudi Arabian Oil Co (Aramco)","2222.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Energy"),
    ("Al Rajhi Banking & Investment Corp","1120.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Banking"),
    ("Saudi National Bank","1180.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Banking"),
    ("Saudi Basic Industries Corp (SABIC)","2010.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Chemicals"),
    ("Saudi Telecom Company (STC)","7010.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Telecom"),
    ("Riyad Bank","1010.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Banking"),
    ("Saudi British Bank (SABB)","1060.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Banking"),
    ("Banque Saudi Fransi","1050.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Banking"),
    ("Arab National Bank","1080.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Banking"),
    ("Alinma Bank","1150.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Banking"),
    ("Saudi Electricity Company","5110.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Utilities"),
    ("Saudi Arabian Mining Co (Maaden)","1211.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Mining"),
    ("ACWA Power Company","2082.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Utilities"),
    ("Dr Sulaiman Al Habib Medical","4013.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Healthcare"),
    ("Jarir Marketing Company","4190.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Retail"),
    ("Etihad Etisalat (Mobily)","7020.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Telecom"),
    ("Saudi Kayan Petrochemical Company","2350.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Chemicals"),
    ("Yanbu National Petrochemical (Yansab)","2290.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Chemicals"),
    ("Advanced Petrochemical Company","1310.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Chemicals"),
    ("Savola Group","2050.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Consumer Staples"),
    ("Kingdom Holding Company","4280.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Financial Services"),
    ("Aldar Properties (Saudi listed)","4300.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Real Estate"),
    ("Saudi Airlines Catering","6004.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Consumer Services"),
    ("Al Marai Company","2280.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Consumer Staples"),
    ("Bupa Arabia","8210.SR","SAR","Saudi Exchange","Saudi Arabia","TASI30","Insurance"),

    # ── UAE — ADX + DFM ───────────────────────────────────────────────────────
    ("First Abu Dhabi Bank PJSC","FAB.AD","AED","ADX","UAE","ADX10","Banking"),
    ("Abu Dhabi Commercial Bank PJSC","ADCB.AD","AED","ADX","UAE","ADX10","Banking"),
    ("e& (Etisalat)","ETISALAT.AD","AED","ADX","UAE","ADX10","Telecom"),
    ("Abu Dhabi National Energy Co (TAQA)","TAQA.AD","AED","ADX","UAE","ADX10","Energy"),
    ("ADNOC Distribution","ADNOCDIST.AD","AED","ADX","UAE","ADX10","Energy"),
    ("Abu Dhabi Islamic Bank PJSC","ADIB.AD","AED","ADX","UAE","ADX10","Banking"),
    ("Aldar Properties PJSC","ALDAR.AD","AED","ADX","UAE","ADX10","Real Estate"),
    ("International Holding Company PJSC","IHC.AD","AED","ADX","UAE","ADX10","Financial Services"),
    ("Emirates NBD Bank PJSC","EMIRATES.DU","AED","DFM","UAE","DFM10","Banking"),
    ("Emaar Properties PJSC","EMAAR.DU","AED","DFM","UAE","DFM10","Real Estate"),
    ("Dubai Islamic Bank PJSC","DIB.DU","AED","DFM","UAE","DFM10","Banking"),
    ("Dubai Electricity & Water Authority","DEWA.DU","AED","DFM","UAE","DFM10","Utilities"),
    ("Air Arabia PJSC","AIRARABI.DU","AED","DFM","UAE","DFM10","Airlines"),
    ("Emaar Development PJSC","EMAARDEV.DU","AED","DFM","UAE","DFM10","Real Estate"),
    ("Salik Company PJSC","SALIK.DU","AED","DFM","UAE","DFM10","Industrials"),

    # ── Qatar QE Index ────────────────────────────────────────────────────────
    ("Qatar National Bank SAQ","QNBK.QA","QAR","Qatar Stock Exchange","Qatar","QE20","Banking"),
    ("Qatar Islamic Bank SAQ","QIBK.QA","QAR","Qatar Stock Exchange","Qatar","QE20","Banking"),
    ("Industries Qatar QSC","IQCD.QA","QAR","Qatar Stock Exchange","Qatar","QE20","Industrials"),
    ("Qatar Electricity & Water Co QSC","QEWS.QA","QAR","Qatar Stock Exchange","Qatar","QE20","Utilities"),
    ("Commercial Bank PSQC","CBQK.QA","QAR","Qatar Stock Exchange","Qatar","QE20","Banking"),
    ("Ooredoo QSC","ORDS.QA","QAR","Qatar Stock Exchange","Qatar","QE20","Telecom"),
    ("Masraf Al Rayan QSC","MARK.QA","QAR","Qatar Stock Exchange","Qatar","QE20","Banking"),
    ("Qatar Navigation QSC","QNNS.QA","QAR","Qatar Stock Exchange","Qatar","QE20","Industrials"),
    ("Qatar Fuel Company QSC (Woqod)","QFLS.QA","QAR","Qatar Stock Exchange","Qatar","QE20","Energy"),
    ("Gulf International Services QSC","GISS.QA","QAR","Qatar Stock Exchange","Qatar","QE20","Energy"),
    ("Nakilat QSC","QGTS.QA","QAR","Qatar Stock Exchange","Qatar","QE20","Industrials"),
    ("Qatar International Islamic Bank","QIIK.QA","QAR","Qatar Stock Exchange","Qatar","QE20","Banking"),

    # ── Kuwait Boursa Kuwait ──────────────────────────────────────────────────
    ("National Bank of Kuwait SAKP","NBK.KW","KWD","Boursa Kuwait","Kuwait","BK15","Banking"),
    ("Kuwait Finance House KSCP","KFH.KW","KWD","Boursa Kuwait","Kuwait","BK15","Banking"),
    ("Gulf Bank KSCP","GBK.KW","KWD","Boursa Kuwait","Kuwait","BK15","Banking"),
    ("Burgan Bank SAK","BURG.KW","KWD","Boursa Kuwait","Kuwait","BK15","Banking"),
    ("Mobile Telecommunications Co KSCP (Zain)","ZAIN.KW","KWD","Boursa Kuwait","Kuwait","BK15","Telecom"),
    ("Agility Public Warehousing Co KSCP","AGLTY.KW","KWD","Boursa Kuwait","Kuwait","BK15","Industrials"),
    ("Boubyan Bank KSCP","BBK.KW","KWD","Boursa Kuwait","Kuwait","BK15","Banking"),
    ("Humansoft Holding Co KSCP","HUMANSOFT.KW","KWD","Boursa Kuwait","Kuwait","BK15","Technology"),
    ("Gulf Insurance Group KSCP","GIG.KW","KWD","Boursa Kuwait","Kuwait","BK15","Insurance"),
    ("Jazeera Airways Co KSCP","JAZEERA.KW","KWD","Boursa Kuwait","Kuwait","BK15","Airlines"),

    # ── Bahrain BSE ───────────────────────────────────────────────────────────
    ("Al Baraka Banking Group BSC","ABB.BH","BHD","Bahrain Bourse","Bahrain","BSE10","Banking"),
    ("Ahli United Bank BSC","AUB.BH","BHD","Bahrain Bourse","Bahrain","BSE10","Banking"),
    ("National Bank of Bahrain BSC","NBB.BH","BHD","Bahrain Bourse","Bahrain","BSE10","Banking"),
    ("Aluminium Bahrain BSC (Alba)","ALBH.BH","BHD","Bahrain Bourse","Bahrain","BSE10","Materials"),
    ("Beyon Communications BSC (Batelco)","BATELCO.BH","BHD","Bahrain Bourse","Bahrain","BSE10","Telecom"),
    ("GFH Financial Group BSC","GFH.BH","BHD","Bahrain Bourse","Bahrain","BSE10","Financial Services"),
    ("Investcorp Bank BSC","INVCORP.BH","BHD","Bahrain Bourse","Bahrain","BSE10","Financial Services"),

    # ── Israel TA-35 ──────────────────────────────────────────────────────────
    ("Bank Hapoalim BM","POLI.TA","ILS","TASE","Israel","TA35","Banking"),
    ("Bank Leumi le-Israel BM","LUMI.TA","ILS","TASE","Israel","TA35","Banking"),
    ("Israel Discount Bank Ltd","DSCT.TA","ILS","TASE","Israel","TA35","Banking"),
    ("Mizrahi-Tefahot Bank Ltd","MZTF.TA","ILS","TASE","Israel","TA35","Banking"),
    ("First International Bank of Israel","FIBI.TA","ILS","TASE","Israel","TA35","Banking"),
    ("Teva Pharmaceutical Industries Ltd","TEVA.TA","ILS","TASE","Israel","TA35","Pharmaceuticals"),
    ("NICE Ltd","NICE.TA","ILS","TASE","Israel","TA35","Technology"),
    ("Elbit Systems Ltd","ESLT.TA","ILS","TASE","Israel","TA35","Aerospace & Defence"),
    ("ICL Group Ltd","ICL.TA","ILS","TASE","Israel","TA35","Chemicals"),
    ("Tower Semiconductor Ltd","TSEM.TA","ILS","TASE","Israel","TA35","Technology"),
    ("Nova Measuring Instruments Ltd","NVMI.TA","ILS","TASE","Israel","TA35","Technology"),
    ("Camtek Ltd","CAMT.TA","ILS","TASE","Israel","TA35","Technology"),
    ("Azrieli Group Ltd","AZRG.TA","ILS","TASE","Israel","TA35","Real Estate"),
    ("Melisron Ltd","MLSR.TA","ILS","TASE","Israel","TA35","Real Estate"),
    ("OPC Energy Ltd","OPCE.TA","ILS","TASE","Israel","TA35","Energy"),
    ("Bezeq Israeli Telecommunication","BEZQ.TA","ILS","TASE","Israel","TA35","Telecom"),
    ("Enlight Renewable Energy Ltd","ENLT.TA","ILS","TASE","Israel","TA35","Utilities"),
    ("NewMed Energy LP","NWMD.TA","ILS","TASE","Israel","TA35","Energy"),
    ("Delek Group Ltd","DLEKG.TA","ILS","TASE","Israel","TA35","Energy"),
    ("Phoenix Holdings Ltd","PHOE.TA","ILS","TASE","Israel","TA35","Insurance"),
    ("Harel Insurance Investments","HARL.TA","ILS","TASE","Israel","TA35","Insurance"),
    ("Clal Insurance Holdings Ltd","CLIS.TA","ILS","TASE","Israel","TA35","Insurance"),
    ("Migdal Insurance & Financial Holdings","MGDL.TA","ILS","TASE","Israel","TA35","Insurance"),
    ("Menora Mivtachim Holdings Ltd","MMHD.TA","ILS","TASE","Israel","TA35","Insurance"),
    ("Strauss Group Ltd","STRS.TA","ILS","TASE","Israel","TA35","Consumer Staples"),
    ("Shufersal Ltd","SAE.TA","ILS","TASE","Israel","TA35","Retail"),
    ("Fattal Holdings Ltd","FTAL.TA","ILS","TASE","Israel","TA35","Consumer Services"),
    ("BIG Shopping Centers Ltd","BIG.TA","ILS","TASE","Israel","TA35","Real Estate"),
    ("AMOT Investments Ltd","AMOT.TA","ILS","TASE","Israel","TA35","Real Estate"),
    ("Dimri Construction & Development","DIMRI.TA","ILS","TASE","Israel","TA35","Real Estate"),
    ("Mivne Real Estate KD Ltd","MVNE.TA","ILS","TASE","Israel","TA35","Real Estate"),
    ("Navitas Petroleum LP","NVPT.TA","ILS","TASE","Israel","TA35","Energy"),
    ("Shapir Engineering and Industry Ltd","SPEN.TA","ILS","TASE","Israel","TA35","Industrials"),
]

# ══════════════════════════════════════════════════════════════════════════════
# AFRICA — South Africa, Egypt, Morocco, Nigeria, Kenya
# ══════════════════════════════════════════════════════════════════════════════
AFRICA = [
    # ── South Africa JSE Top 40 ───────────────────────────────────────────────
    ("Naspers Ltd","NPN.JO","ZAR","JSE","South Africa","JSE40","Technology"),
    ("Prosus NV","PRX.JO","ZAR","JSE","South Africa","JSE40","Technology"),
    ("BHP Group Ltd","BHP.JO","ZAR","JSE","South Africa","JSE40","Mining"),
    ("Anglo American Platinum Ltd","AMS.JO","ZAR","JSE","South Africa","JSE40","Mining"),
    ("Anglo American PLC","AGL.JO","ZAR","JSE","South Africa","JSE40","Mining"),
    ("Glencore PLC","GLN.JO","ZAR","JSE","South Africa","JSE40","Mining"),
    ("Impala Platinum Holdings Ltd","IMP.JO","ZAR","JSE","South Africa","JSE40","Mining"),
    ("Sibanye Stillwater Ltd","SSW.JO","ZAR","JSE","South Africa","JSE40","Mining"),
    ("Gold Fields Ltd","GFI.JO","ZAR","JSE","South Africa","JSE40","Mining"),
    ("Sasol Ltd","SOL.JO","ZAR","JSE","South Africa","JSE40","Energy"),
    ("FirstRand Ltd","FSR.JO","ZAR","JSE","South Africa","JSE40","Banking"),
    ("Standard Bank Group Ltd","SBK.JO","ZAR","JSE","South Africa","JSE40","Banking"),
    ("Nedbank Group Ltd","NED.JO","ZAR","JSE","South Africa","JSE40","Banking"),
    ("Absa Group Ltd","ABG.JO","ZAR","JSE","South Africa","JSE40","Banking"),
    ("Capitec Bank Holdings Ltd","CPI.JO","ZAR","JSE","South Africa","JSE40","Banking"),
    ("MTN Group Ltd","MTN.JO","ZAR","JSE","South Africa","JSE40","Telecom"),
    ("Vodacom Group Ltd","VOD.JO","ZAR","JSE","South Africa","JSE40","Telecom"),
    ("Sanlam Ltd","SLM.JO","ZAR","JSE","South Africa","JSE40","Insurance"),
    ("Old Mutual Ltd","OMU.JO","ZAR","JSE","South Africa","JSE40","Insurance"),
    ("Discovery Ltd","DSY.JO","ZAR","JSE","South Africa","JSE40","Insurance"),
    ("Shoprite Holdings Ltd","SHP.JO","ZAR","JSE","South Africa","JSE40","Retail"),
    ("Woolworths Holdings Ltd","WHL.JO","ZAR","JSE","South Africa","JSE40","Retail"),
    ("Mr Price Group Ltd","MRP.JO","ZAR","JSE","South Africa","JSE40","Retail"),
    ("Bidcorp Ltd","BID.JO","ZAR","JSE","South Africa","JSE40","Consumer Staples"),
    ("Tiger Brands Ltd","TBS.JO","ZAR","JSE","South Africa","JSE40","Consumer Staples"),
    ("AngloGold Ashanti PLC","ANG.JO","ZAR","JSE","South Africa","JSE40","Mining"),
    ("Kumba Iron Ore Ltd","KIO.JO","ZAR","JSE","South Africa","JSE40","Mining"),
    ("Exxaro Resources Ltd","EXX.JO","ZAR","JSE","South Africa","JSE40","Mining"),
    ("Remgro Ltd","REM.JO","ZAR","JSE","South Africa","JSE40","Financial Services"),
    ("Aspen Pharmacare Holdings Ltd","APN.JO","ZAR","JSE","South Africa","JSE40","Pharmaceuticals"),
    ("Life Healthcare Group Holdings Ltd","LHC.JO","ZAR","JSE","South Africa","JSE40","Healthcare"),
    ("Growthpoint Properties Ltd","GRT.JO","ZAR","JSE","South Africa","JSE40","Real Estate"),
    ("Redefine Properties Ltd","RDF.JO","ZAR","JSE","South Africa","JSE40","Real Estate"),
    ("Clicks Group Ltd","CLS.JO","ZAR","JSE","South Africa","JSE40","Retail"),
    ("Investec Ltd","INL.JO","ZAR","JSE","South Africa","JSE40","Financial Services"),

    # ── Egypt EGX 30 ──────────────────────────────────────────────────────────
    ("Commercial International Bank Egypt SAE","COMI.CA","EGP","Egyptian Exchange","Egypt","EGX30","Banking"),
    ("Eastern Company SAE","EAST.CA","EGP","Egyptian Exchange","Egypt","EGX30","Consumer Staples"),
    ("Telecom Egypt SAE","ETEL.CA","EGP","Egyptian Exchange","Egypt","EGX30","Telecom"),
    ("EFG Hermes Holding SAE","HRHO.CA","EGP","Egyptian Exchange","Egypt","EGX30","Financial Services"),
    ("Sodic SAE","OCDI.CA","EGP","Egyptian Exchange","Egypt","EGX30","Real Estate"),
    ("Orascom Construction PLC","ORAS.CA","EGP","Egyptian Exchange","Egypt","EGX30","Industrials"),
    ("Palm Hills Developments SAE","PHDC.CA","EGP","Egyptian Exchange","Egypt","EGX30","Real Estate"),
    ("Juhayna Food Industries SAE","JUFO.CA","EGP","Egyptian Exchange","Egypt","EGX30","Consumer Staples"),
    ("Edita Food Industries SAE","EDIT.CA","EGP","Egyptian Exchange","Egypt","EGX30","Consumer Staples"),
    ("Egyptian Resorts Company SAE","EGTS.CA","EGP","Egyptian Exchange","Egypt","EGX30","Real Estate"),
    ("Madinet Nasr Housing & Development","MNHD.CA","EGP","Egyptian Exchange","Egypt","EGX30","Real Estate"),
    ("Credit Agricole Egypt SAE","CIEB.CA","EGP","Egyptian Exchange","Egypt","EGX30","Banking"),

    # ── Morocco MASI ──────────────────────────────────────────────────────────
    ("Maroc Telecom SA","IAM.CS","MAD","Casablanca Stock Exchange","Morocco","MASI20","Telecom"),
    ("Attijariwafa Bank SA","ATW.CS","MAD","Casablanca Stock Exchange","Morocco","MASI20","Banking"),
    ("Banque Centrale Populaire SA","BCP.CS","MAD","Casablanca Stock Exchange","Morocco","MASI20","Banking"),
    ("BMCE Bank of Africa SA","BOA.CS","MAD","Casablanca Stock Exchange","Morocco","MASI20","Banking"),
    ("LafargeHolcim Maroc SA","LHM.CS","MAD","Casablanca Stock Exchange","Morocco","MASI20","Materials"),
    ("Wafa Assurance SA","WAA.CS","MAD","Casablanca Stock Exchange","Morocco","MASI20","Insurance"),
    ("Label Vie SA","LBV.CS","MAD","Casablanca Stock Exchange","Morocco","MASI20","Retail"),
    ("Cosumar SA","CSR.CS","MAD","Casablanca Stock Exchange","Morocco","MASI20","Consumer Staples"),
    ("Managem Group SA","MNG.CS","MAD","Casablanca Stock Exchange","Morocco","MASI20","Mining"),
    ("Ciments du Maroc SA","CIM.CS","MAD","Casablanca Stock Exchange","Morocco","MASI20","Materials"),

    # ── Nigeria NGX ───────────────────────────────────────────────────────────
    ("Dangote Cement PLC","DANGCEM.LG","NGN","Nigerian Exchange","Nigeria","NGX30","Materials"),
    ("MTN Nigeria Communications PLC","MTNN.LG","NGN","Nigerian Exchange","Nigeria","NGX30","Telecom"),
    ("Airtel Africa Nigeria","AIRTELAFRI.LG","NGN","Nigerian Exchange","Nigeria","NGX30","Telecom"),
    ("Zenith Bank PLC","ZENITHBANK.LG","NGN","Nigerian Exchange","Nigeria","NGX30","Banking"),
    ("Access Holdings PLC","ACCESSCORP.LG","NGN","Nigerian Exchange","Nigeria","NGX30","Banking"),
    ("Guaranty Trust Holding Co PLC","GTCO.LG","NGN","Nigerian Exchange","Nigeria","NGX30","Banking"),
    ("First Bank Holdings PLC","FBNH.LG","NGN","Nigerian Exchange","Nigeria","NGX30","Banking"),
    ("United Bank for Africa PLC","UBA.LG","NGN","Nigerian Exchange","Nigeria","NGX30","Banking"),
    ("Nestle Nigeria PLC","NESTLE.LG","NGN","Nigerian Exchange","Nigeria","NGX30","Consumer Staples"),
    ("Lafarge Africa PLC","WAPCO.LG","NGN","Nigerian Exchange","Nigeria","NGX30","Materials"),
    ("Nigerian Breweries PLC","NB.LG","NGN","Nigerian Exchange","Nigeria","NGX30","Consumer Staples"),
    ("Stanbic IBTC Holdings PLC","STANBIC.LG","NGN","Nigerian Exchange","Nigeria","NGX30","Banking"),

    # ── Kenya NSE ─────────────────────────────────────────────────────────────
    ("Safaricom PLC","SCOM.NR","KES","Nairobi Securities Exchange","Kenya","NSE20","Telecom"),
    ("East African Breweries Ltd","EABL.NR","KES","Nairobi Securities Exchange","Kenya","NSE20","Consumer Staples"),
    ("KCB Group PLC","KCB.NR","KES","Nairobi Securities Exchange","Kenya","NSE20","Banking"),
    ("Equity Group Holdings PLC","EQTY.NR","KES","Nairobi Securities Exchange","Kenya","NSE20","Banking"),
    ("Co-operative Bank of Kenya Ltd","COOP.NR","KES","Nairobi Securities Exchange","Kenya","NSE20","Banking"),
    ("BAT Kenya PLC","BAT.NR","KES","Nairobi Securities Exchange","Kenya","NSE20","Consumer Staples"),
    ("Standard Chartered Bank Kenya Ltd","SCBK.NR","KES","Nairobi Securities Exchange","Kenya","NSE20","Banking"),
    ("Jubilee Holdings Ltd","JUB.NR","KES","Nairobi Securities Exchange","Kenya","NSE20","Insurance"),
    ("ABSA Bank Kenya PLC","ABSA.NR","KES","Nairobi Securities Exchange","Kenya","NSE20","Banking"),
    ("Diamond Trust Bank Kenya Ltd","DTK.NR","KES","Nairobi Securities Exchange","Kenya","NSE20","Banking"),
]

# ══════════════════════════════════════════════════════════════════════════════
# US — S&P 500 live from Wikipedia
# ══════════════════════════════════════════════════════════════════════════════
def fetch_sp500():
    print("Fetching S&P 500 from Wikipedia...")
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    tables = pd.read_html(url)
    df = tables[0][["Security","Symbol","GICS Sector"]].copy()
    df.columns = ["company_name","ticker","sector"]
    df["ticker_yfinance"] = df["ticker"].str.replace(".","-",regex=False)
    df["currency"]  = "USD"
    df["exchange"]  = "NYSE/NASDAQ"
    df["country"]   = "US"
    df["index"]     = "SP500"
    df["has_adr"]   = False
    df["adr_ticker"] = ""
    print(f"  → {len(df)} companies")
    return df[COLS]

# ══════════════════════════════════════════════════════════════════════════════
# ADR MAP
# ══════════════════════════════════════════════════════════════════════════════
ADR_MAP = {
    # UK
    "AZN.L":"AZN","HSBA.L":"HSBC","BP.L":"BP","SHEL.L":"SHEL",
    "ULVR.L":"UL","RIO.L":"RIO","GSK.L":"GSK","VOD.L":"VOD",
    "BATS.L":"BTI","IMB.L":"IMBBY","PRU.L":"PUK","STAN.L":"SCBFY",
    "DGE.L":"DEO","EXPN.L":"EXPGY","REL.L":"RELX","HLN.L":"HLN",
    "CPG.L":"CMPGY","RKT.L":"RBGLY","AAL.L":"NGLOY","GLEN.L":"GLNCY",
    "RR.L":"RYCEY","BA.L":"BAESY","SBRY.L":"JSAIY","TSCO.L":"TSCDY",
    # Switzerland
    "NESN.SW":"NSRGY","NOVN.SW":"NVS","ROG.SW":"RHHBY",
    "ABBN.SW":"ABBNY","ZURN.SW":"ZURVY","UBSG.SW":"UBS",
    "LONN.SW":"LZAGY","SREN.SW":"SSREY",
    # Germany
    "SAP.DE":"SAP","SIE.DE":"SIEGY","ALV.DE":"AZSEY",
    "DTE.DE":"DTEGY","BAYN.DE":"BAYRY","BAS.DE":"BASFY",
    "DBK.DE":"DB","BMW.DE":"BMWYY","MBG.DE":"MBGAF",
    "MUV2.DE":"MURGY","IFX.DE":"IFNNY","VOW3.DE":"VWAGY",
    # France
    "MC.PA":"LVMHF","TTE.PA":"TTE","SAN.PA":"SNY","BNP.PA":"BNPQY",
    "OR.PA":"LRLCY","ACA.PA":"CRARY","GLE.PA":"SCGLY",
    "KER.PA":"PPRUY","RMS.PA":"HESAY","SAF.PA":"SAFRY",
    # Netherlands
    "ASML.AS":"ASML","INGA.AS":"ING","HEIA.AS":"HEINY",
    "PHIA.AS":"PHG","MT.AS":"MT",
    # Sweden
    "ERIC-B.ST":"ERIC","VOLV-B.ST":"VLVLY","NDA-SE.ST":"NDA",
    "HM-B.ST":"HNNMY","ATCO-A.ST":"ATLKY",
    # Italy
    "ENI.MI":"E","ENEL.MI":"ENLAY","RACE.MI":"RACE",
    "ISP.MI":"ISNPY","UCG.MI":"UNCRY","G.MI":"ARZGY",
    # Spain
    "SAN.MC":"SAN","BBVA.MC":"BBVA","TEF.MC":"TEF","IBE.MC":"IBDRY",
    # Denmark
    "NOVO-B.CO":"NVO","MAERSK-B.CO":"AMKBY","DSV.CO":"DSDVY",
    "GMAB.CO":"GMAB",
    # Norway
    "EQNR.OL":"EQNR","NHY.OL":"NHYDY","TEL.OL":"TELNF",
    # Belgium
    "ABI.BR":"BUD","KBC.BR":"KBCSY","UCB.BR":"UCBJY",
    # Israel
    "TEVA.TA":"TEVA","NICE.TA":"NICE","ESLT.TA":"ESLT",
    "ICL.TA":"ICL","TSEM.TA":"TSEM","NVMI.TA":"NVMI","CAMT.TA":"CAMT",
    # South Africa
    "NPN.JO":"NPSNY","GFI.JO":"GFI","ANG.JO":"AU",
    "MTN.JO":"MTNOY","SOL.JO":"SASOY","FSR.JO":"FANDF",
    "SBK.JO":"SGBLY",
    # Saudi Arabia
    "2222.SR":"ARMCO",  # Aramco not US listed but noting
    # UAE
    "ETISALAT.AD":"ETISALAT",
    # Turkey
    "GARAN.IS":"TKGBY","AKBNK.IS":"AKBTY","THYAO.IS":"TKHVY",
    "TCELL.IS":"TKC",
}

# ══════════════════════════════════════════════════════════════════════════════
# BUILD
# ══════════════════════════════════════════════════════════════════════════════
def main():
    all_rows = (rows(FTSE100) + rows(EUROPE) + rows(TURKEY) +
                rows(MIDDLE_EAST) + rows(AFRICA))

    df_manual = pd.DataFrame(all_rows, columns=COLS)

    try:
        df_us = fetch_sp500()
    except Exception as e:
        print(f"  ⚠ S&P 500 fetch failed: {e} — continuing without")
        df_us = pd.DataFrame(columns=COLS)

    df = pd.concat([df_manual, df_us], ignore_index=True)
    df = df.drop_duplicates(subset=["ticker"]).reset_index(drop=True)

    # Apply ADRs
    df["has_adr"]   = df["ticker"].isin(ADR_MAP.keys())
    df["adr_ticker"] = df["ticker"].map(ADR_MAP).fillna("")

    df.to_csv(OUTPUT_FILE, index=False)

    # Summary
    print(f"\n✓ Universe saved → {OUTPUT_FILE}")
    print(f"  Total companies : {len(df):,}")
    print(f"\n  Breakdown by region/country:")
    for ctry, n in df.groupby("country").size().sort_values(ascending=False).items():
        idx_names = ", ".join(df[df.country==ctry]["index"].unique()[:2])
        print(f"    {ctry:<28} {n:>4}   [{idx_names}]")
    print(f"\n  Companies with ADR mapping: {df['has_adr'].sum()}")

if __name__ == "__main__":
    main()
