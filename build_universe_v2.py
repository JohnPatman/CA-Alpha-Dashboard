"""
build_universe_v2.py
--------------------
Extended universe adding Australia (ASX 50), Hong Kong/China (HSI 50),
Japan (Nikkei top 30), China A-shares (CSI 20).
Merges with existing universe.csv and sp500.csv.

Run:  python3 build_universe_v2.py
Out:  data/universe.csv  (full merged universe)
"""
import os, pandas as pd

OUTPUT = "data/universe.csv"
COLS   = ["company_name","ticker","currency","exchange",
          "country","index","sector","ticker_yfinance","has_adr","adr_ticker"]

def rows(data):
    out = []
    for r in data:
        name,tkr,ccy,exch,ctry,idx,sec = r
        out.append(dict(company_name=name,ticker=tkr,currency=ccy,
                        exchange=exch,country=ctry,index=idx,sector=sec,
                        ticker_yfinance=tkr,has_adr=False,adr_ticker=""))
    return out

# ── Australia ASX 50 ─────────────────────────────────────────────────────────
ASX = [
    ("BHP Group Ltd","BHP.AX","AUD","ASX","Australia","ASX50","Mining"),
    ("Commonwealth Bank of Australia","CBA.AX","AUD","ASX","Australia","ASX50","Banking"),
    ("CSL Ltd","CSL.AX","AUD","ASX","Australia","ASX50","Pharmaceuticals"),
    ("National Australia Bank Ltd","NAB.AX","AUD","ASX","Australia","ASX50","Banking"),
    ("Westpac Banking Corp","WBC.AX","AUD","ASX","Australia","ASX50","Banking"),
    ("ANZ Banking Group Ltd","ANZ.AX","AUD","ASX","Australia","ASX50","Banking"),
    ("Macquarie Group Ltd","MQG.AX","AUD","ASX","Australia","ASX50","Financial Services"),
    ("Wesfarmers Ltd","WES.AX","AUD","ASX","Australia","ASX50","Retail"),
    ("Woodside Energy Group Ltd","WDS.AX","AUD","ASX","Australia","ASX50","Energy"),
    ("Fortescue Ltd","FMG.AX","AUD","ASX","Australia","ASX50","Mining"),
    ("Rio Tinto Ltd","RIO.AX","AUD","ASX","Australia","ASX50","Mining"),
    ("Woolworths Group Ltd","WOW.AX","AUD","ASX","Australia","ASX50","Retail"),
    ("Telstra Group Ltd","TLS.AX","AUD","ASX","Australia","ASX50","Telecom"),
    ("Coles Group Ltd","COL.AX","AUD","ASX","Australia","ASX50","Retail"),
    ("Goodman Group","GMG.AX","AUD","ASX","Australia","ASX50","Real Estate"),
    ("Transurban Group","TCL.AX","AUD","ASX","Australia","ASX50","Industrials"),
    ("Santos Ltd","STO.AX","AUD","ASX","Australia","ASX50","Energy"),
    ("South32 Ltd","S32.AX","AUD","ASX","Australia","ASX50","Mining"),
    ("APA Group","APA.AX","AUD","ASX","Australia","ASX50","Utilities"),
    ("Suncorp Group Ltd","SUN.AX","AUD","ASX","Australia","ASX50","Insurance"),
    ("Insurance Australia Group Ltd","IAG.AX","AUD","ASX","Australia","ASX50","Insurance"),
    ("QBE Insurance Group Ltd","QBE.AX","AUD","ASX","Australia","ASX50","Insurance"),
    ("ASX Ltd","ASX.AX","AUD","ASX","Australia","ASX50","Financial Services"),
    ("Scentre Group","SCG.AX","AUD","ASX","Australia","ASX50","Real Estate"),
    ("Dexus","DXS.AX","AUD","ASX","Australia","ASX50","Real Estate"),
    ("Mirvac Group","MGR.AX","AUD","ASX","Australia","ASX50","Real Estate"),
    ("Stockland Corp Ltd","SGP.AX","AUD","ASX","Australia","ASX50","Real Estate"),
    ("Origin Energy Ltd","ORG.AX","AUD","ASX","Australia","ASX50","Energy"),
    ("AGL Energy Ltd","AGL.AX","AUD","ASX","Australia","ASX50","Utilities"),
    ("ResMed Inc","RMD.AX","AUD","ASX","Australia","ASX50","Healthcare"),
    ("Cochlear Ltd","COH.AX","AUD","ASX","Australia","ASX50","Healthcare"),
    ("James Hardie Industries PLC","JHX.AX","AUD","ASX","Australia","ASX50","Materials"),
    ("Amcor PLC","AMC.AX","AUD","ASX","Australia","ASX50","Packaging"),
    ("Brambles Ltd","BXB.AX","AUD","ASX","Australia","ASX50","Industrials"),
    ("Computershare Ltd","CPU.AX","AUD","ASX","Australia","ASX50","Financial Services"),
    ("REA Group Ltd","REA.AX","AUD","ASX","Australia","ASX50","Technology"),
    ("WiseTech Global Ltd","WTC.AX","AUD","ASX","Australia","ASX50","Technology"),
    ("Xero Ltd","XRO.AX","AUD","ASX","Australia","ASX50","Technology"),
    ("Aristocrat Leisure Ltd","ALL.AX","AUD","ASX","Australia","ASX50","Consumer Services"),
    ("Qantas Airways Ltd","QAN.AX","AUD","ASX","Australia","ASX50","Airlines"),
    ("Seek Ltd","SEK.AX","AUD","ASX","Australia","ASX50","Technology"),
    ("Treasury Wine Estates Ltd","TWE.AX","AUD","ASX","Australia","ASX50","Consumer Staples"),
    ("Newmont Corp","NEM.AX","AUD","ASX","Australia","ASX50","Mining"),
    ("Northern Star Resources Ltd","NST.AX","AUD","ASX","Australia","ASX50","Mining"),
    ("Evolution Mining Ltd","EVN.AX","AUD","ASX","Australia","ASX50","Mining"),
    ("Mineral Resources Ltd","MIN.AX","AUD","ASX","Australia","ASX50","Mining"),
    ("Pilbara Minerals Ltd","PLS.AX","AUD","ASX","Australia","ASX50","Mining"),
    ("Meridian Energy Ltd","MEZ.AX","AUD","ASX","Australia","ASX50","Utilities"),
    ("Ramsay Health Care Ltd","RHC.AX","AUD","ASX","Australia","ASX50","Healthcare"),
    ("Flight Centre Travel Group Ltd","FLT.AX","AUD","ASX","Australia","ASX50","Consumer Services"),
]

# ── Hong Kong / China HSI 50 ─────────────────────────────────────────────────
HSI = [
    ("HSBC Holdings PLC","0005.HK","HKD","HKEX","Hong Kong","HSI50","Banking"),
    ("AIA Group Ltd","1299.HK","HKD","HKEX","Hong Kong","HSI50","Insurance"),
    ("Tencent Holdings Ltd","0700.HK","HKD","HKEX","Hong Kong","HSI50","Technology"),
    ("Alibaba Group Holding Ltd","9988.HK","HKD","HKEX","Hong Kong","HSI50","Technology"),
    ("Meituan","3690.HK","HKD","HKEX","Hong Kong","HSI50","Technology"),
    ("China Mobile Ltd","0941.HK","HKD","HKEX","Hong Kong","HSI50","Telecom"),
    ("China Construction Bank Corp","0939.HK","HKD","HKEX","Hong Kong","HSI50","Banking"),
    ("Industrial & Commercial Bank of China","1398.HK","HKD","HKEX","Hong Kong","HSI50","Banking"),
    ("Bank of China Ltd","3988.HK","HKD","HKEX","Hong Kong","HSI50","Banking"),
    ("Ping An Insurance Group Co","2318.HK","HKD","HKEX","Hong Kong","HSI50","Insurance"),
    ("China Life Insurance Co Ltd","2628.HK","HKD","HKEX","Hong Kong","HSI50","Insurance"),
    ("CNOOC Ltd","0883.HK","HKD","HKEX","Hong Kong","HSI50","Energy"),
    ("PetroChina Co Ltd","0857.HK","HKD","HKEX","Hong Kong","HSI50","Energy"),
    ("China Petroleum & Chemical Corp","0386.HK","HKD","HKEX","Hong Kong","HSI50","Energy"),
    ("CK Hutchison Holdings Ltd","0001.HK","HKD","HKEX","Hong Kong","HSI50","Industrials"),
    ("CK Asset Holdings Ltd","1113.HK","HKD","HKEX","Hong Kong","HSI50","Real Estate"),
    ("Sun Hung Kai Properties Ltd","0016.HK","HKD","HKEX","Hong Kong","HSI50","Real Estate"),
    ("Link Real Estate Investment Trust","0823.HK","HKD","HKEX","Hong Kong","HSI50","Real Estate"),
    ("MTR Corp Ltd","0066.HK","HKD","HKEX","Hong Kong","HSI50","Industrials"),
    ("CLP Holdings Ltd","0002.HK","HKD","HKEX","Hong Kong","HSI50","Utilities"),
    ("Hong Kong & China Gas Co Ltd","0003.HK","HKD","HKEX","Hong Kong","HSI50","Utilities"),
    ("Power Assets Holdings Ltd","0006.HK","HKD","HKEX","Hong Kong","HSI50","Utilities"),
    ("Swire Pacific Ltd","0019.HK","HKD","HKEX","Hong Kong","HSI50","Industrials"),
    ("Hong Kong Exchanges & Clearing Ltd","0388.HK","HKD","HKEX","Hong Kong","HSI50","Financial Services"),
    ("Hang Seng Bank Ltd","0011.HK","HKD","HKEX","Hong Kong","HSI50","Banking"),
    ("China Resources Land Ltd","1109.HK","HKD","HKEX","Hong Kong","HSI50","Real Estate"),
    ("China Overseas Land & Investment Ltd","0688.HK","HKD","HKEX","Hong Kong","HSI50","Real Estate"),
    ("Longfor Group Holdings Ltd","0960.HK","HKD","HKEX","Hong Kong","HSI50","Real Estate"),
    ("Geely Automobile Holdings Ltd","0175.HK","HKD","HKEX","Hong Kong","HSI50","Automotive"),
    ("BYD Co Ltd","1211.HK","HKD","HKEX","Hong Kong","HSI50","Automotive"),
    ("Xiaomi Corp","1810.HK","HKD","HKEX","Hong Kong","HSI50","Technology"),
    ("NetEase Inc","9999.HK","HKD","HKEX","Hong Kong","HSI50","Technology"),
    ("JD.com Inc","9618.HK","HKD","HKEX","Hong Kong","HSI50","Technology"),
    ("Baidu Inc","9888.HK","HKD","HKEX","Hong Kong","HSI50","Technology"),
    ("Wuxi Biologics Cayman Inc","2269.HK","HKD","HKEX","Hong Kong","HSI50","Pharmaceuticals"),
    ("Semiconductor Manufacturing Intl Corp","0981.HK","HKD","HKEX","Hong Kong","HSI50","Technology"),
    ("Galaxy Entertainment Group Ltd","0027.HK","HKD","HKEX","Hong Kong","HSI50","Consumer Services"),
    ("Sands China Ltd","1928.HK","HKD","HKEX","Hong Kong","HSI50","Consumer Services"),
    ("Li Ning Co Ltd","2331.HK","HKD","HKEX","Hong Kong","HSI50","Consumer Staples"),
    ("Anta Sports Products Ltd","2020.HK","HKD","HKEX","Hong Kong","HSI50","Consumer Staples"),
    ("Henderson Land Development Co Ltd","0012.HK","HKD","HKEX","Hong Kong","HSI50","Real Estate"),
    ("New World Development Co Ltd","0017.HK","HKD","HKEX","Hong Kong","HSI50","Real Estate"),
    ("Sino Land Co Ltd","0083.HK","HKD","HKEX","Hong Kong","HSI50","Real Estate"),
    ("China Unicom Hong Kong Ltd","0762.HK","HKD","HKEX","Hong Kong","HSI50","Telecom"),
    ("China Telecom Corp Ltd","0728.HK","HKD","HKEX","Hong Kong","HSI50","Telecom"),
    ("BOC Hong Kong Holdings Ltd","2388.HK","HKD","HKEX","Hong Kong","HSI50","Banking"),
    ("Wharf Real Estate Investment Co Ltd","1997.HK","HKD","HKEX","Hong Kong","HSI50","Real Estate"),
    ("Budweiser Brewing Company APAC Ltd","1876.HK","HKD","HKEX","Hong Kong","HSI50","Consumer Staples"),
    ("Nongfu Spring Co Ltd","9633.HK","HKD","HKEX","Hong Kong","HSI50","Consumer Staples"),
    ("Trip.com Group Ltd","9961.HK","HKD","HKEX","Hong Kong","HSI50","Technology"),
]

# ── Japan Nikkei Top 30 ───────────────────────────────────────────────────────
JAPAN = [
    ("Toyota Motor Corp","7203.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Automotive"),
    ("Sony Group Corp","6758.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Technology"),
    ("SoftBank Group Corp","9984.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Technology"),
    ("Keyence Corp","6861.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Technology"),
    ("Recruit Holdings Co Ltd","6098.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Technology"),
    ("KDDI Corp","9433.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Telecom"),
    ("Nippon Telegraph and Telephone Corp","9432.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Telecom"),
    ("Mitsubishi UFJ Financial Group Inc","8306.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Banking"),
    ("Sumitomo Mitsui Financial Group Inc","8316.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Banking"),
    ("Mizuho Financial Group Inc","8411.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Banking"),
    ("Fast Retailing Co Ltd","9983.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Retail"),
    ("Shin-Etsu Chemical Co Ltd","4063.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Chemicals"),
    ("Daikin Industries Ltd","6367.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Industrials"),
    ("Honda Motor Co Ltd","7267.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Automotive"),
    ("Hitachi Ltd","6501.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Industrials"),
    ("Fanuc Corp","6954.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Industrials"),
    ("Murata Manufacturing Co Ltd","6981.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Technology"),
    ("TDK Corp","6762.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Technology"),
    ("Asahi Group Holdings Ltd","2502.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Consumer Staples"),
    ("Kirin Holdings Co Ltd","2503.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Consumer Staples"),
    ("Nippon Steel Corp","5401.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Materials"),
    ("Bridgestone Corp","5108.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Automotive"),
    ("Denso Corp","6902.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Automotive"),
    ("Kubota Corp","6326.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Industrials"),
    ("Fujitsu Ltd","6702.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Technology"),
    ("Takeda Pharmaceutical Co Ltd","4502.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Pharmaceuticals"),
    ("Astellas Pharma Inc","4503.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Pharmaceuticals"),
    ("Daiichi Sankyo Co Ltd","4568.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Pharmaceuticals"),
    ("Olympus Corp","7733.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Healthcare"),
    ("Panasonic Holdings Corp","6752.T","JPY","Tokyo Stock Exchange","Japan","NIKKEI30","Technology"),
]

# ── China A-Shares CSI 300 Top 20 ─────────────────────────────────────────────
CHINA_A = [
    ("Kweichow Moutai Co Ltd","600519.SS","CNY","Shanghai Stock Exchange","China","CSI300","Consumer Staples"),
    ("China Merchants Bank Co Ltd","600036.SS","CNY","Shanghai Stock Exchange","China","CSI300","Banking"),
    ("Ping An Insurance Group Co A","601318.SS","CNY","Shanghai Stock Exchange","China","CSI300","Insurance"),
    ("Industrial Bank Co Ltd","601166.SS","CNY","Shanghai Stock Exchange","China","CSI300","Banking"),
    ("Wuliangye Yibin Co Ltd","000858.SZ","CNY","Shenzhen Stock Exchange","China","CSI300","Consumer Staples"),
    ("CITIC Securities Co Ltd","600030.SS","CNY","Shanghai Stock Exchange","China","CSI300","Financial Services"),
    ("Midea Group Co Ltd","000333.SZ","CNY","Shenzhen Stock Exchange","China","CSI300","Consumer Staples"),
    ("Gree Electric Appliances Inc","000651.SZ","CNY","Shenzhen Stock Exchange","China","CSI300","Consumer Staples"),
    ("LONGi Green Energy Technology Co","601012.SS","CNY","Shanghai Stock Exchange","China","CSI300","Energy"),
    ("BYD Co Ltd A","002594.SZ","CNY","Shenzhen Stock Exchange","China","CSI300","Automotive"),
    ("Contemporary Amperex Technology Co","300750.SZ","CNY","Shenzhen Stock Exchange","China","CSI300","Technology"),
    ("Zijin Mining Group Co Ltd","601899.SS","CNY","Shanghai Stock Exchange","China","CSI300","Mining"),
    ("China Yangtze Power Co Ltd","600900.SS","CNY","Shanghai Stock Exchange","China","CSI300","Utilities"),
    ("Sungrow Power Supply Co Ltd","300274.SZ","CNY","Shenzhen Stock Exchange","China","CSI300","Energy"),
    ("Jiangsu Hengrui Medicine Co Ltd","600276.SS","CNY","Shanghai Stock Exchange","China","CSI300","Pharmaceuticals"),
    ("Muyuan Foods Co Ltd","002714.SZ","CNY","Shenzhen Stock Exchange","China","CSI300","Consumer Staples"),
    ("China Tourism Group Duty Free","601888.SS","CNY","Shanghai Stock Exchange","China","CSI300","Retail"),
    ("Will Semiconductor Co Ltd","603501.SS","CNY","Shanghai Stock Exchange","China","CSI300","Technology"),
    ("Bank of Ningbo Co Ltd","002142.SZ","CNY","Shenzhen Stock Exchange","China","CSI300","Banking"),
    ("East Money Information Co Ltd","300059.SZ","CNY","Shenzhen Stock Exchange","China","CSI300","Financial Services"),
]

# ── ADR mappings for new additions ────────────────────────────────────────────
NEW_ADR_MAP = {
    "BHP.AX":"BHP","RIO.AX":"RIO","WDS.AX":"WDS","AMC.AX":"AMCR",
    "BXB.AX":"BXBLY","CSL.AX":"CSLLY","RMD.AX":"RMD","JHX.AX":"JHX",
    "QAN.AX":"QABSY","COH.AX":"CHEAR",
    "0700.HK":"TCEHY","9988.HK":"BABA","1299.HK":"AAGIY",
    "0941.HK":"CHL","2318.HK":"PIAIF","0883.HK":"CEO",
    "0857.HK":"PTR","0386.HK":"SNP","1211.HK":"BYDDY",
    "9999.HK":"NTES","9618.HK":"JD","9888.HK":"BIDU",
    "0005.HK":"HSBC",
    "7203.T":"TM","6758.T":"SONY","9984.T":"SFTBY",
    "8306.T":"MUFG","8316.T":"SMFG","8411.T":"MFG",
    "7267.T":"HMC","4502.T":"TAK","5401.T":"NPSCY",
    "5108.T":"BRDCY","6501.T":"HTHIY","6752.T":"PCRFY",
}

def main():
    # Load existing universe
    if os.path.exists(OUTPUT):
        df_existing = pd.read_csv(OUTPUT)
        print(f"Loaded existing universe: {len(df_existing)} companies")
    else:
        df_existing = pd.DataFrame(columns=COLS)
        print("No existing universe found, building from scratch")

    # Merge sp500 if present
    sp500_path = "data/sp500.csv"
    if os.path.exists(sp500_path):
        df_sp = pd.read_csv(sp500_path)
        df_existing = pd.concat([df_existing, df_sp]).drop_duplicates(subset=["ticker"]).reset_index(drop=True)
        print(f"Merged sp500.csv -> {len(df_existing)} companies")

    # Build new APAC
    all_new = rows(ASX) + rows(HSI) + rows(JAPAN) + rows(CHINA_A)
    df_new  = pd.DataFrame(all_new, columns=COLS)

    # Merge
    df = pd.concat([df_existing, df_new], ignore_index=True)
    df = df.drop_duplicates(subset=["ticker"]).reset_index(drop=True)

    # Apply new ADR mappings
    for tkr, adr in NEW_ADR_MAP.items():
        mask = df["ticker"] == tkr
        df.loc[mask, "has_adr"]   = True
        df.loc[mask, "adr_ticker"] = adr

    df.to_csv(OUTPUT, index=False)

    print(f"\n✓ Universe saved → {OUTPUT}")
    print(f"  Total companies : {len(df):,}")
    print(f"\n  By country (top 15):")
    for ctry, n in df.groupby("country").size().sort_values(ascending=False).head(15).items():
        print(f"    {ctry:<28} {n:>4}")
    print(f"  ... and {df['country'].nunique()} countries total")
    print(f"\n  ADR mappings    : {df['has_adr'].sum()}")

if __name__ == "__main__":
    main()
