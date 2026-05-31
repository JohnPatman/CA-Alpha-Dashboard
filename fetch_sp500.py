import requests
import pandas as pd
from io import StringIO

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
response = requests.get(url, headers=headers)
df = pd.read_html(StringIO(response.text))[0]
df = df[["Security", "Symbol", "GICS Sector"]].copy()
df.columns = ["company_name", "ticker", "sector"]
df["ticker_yfinance"] = df["ticker"].str.replace(".", "-", regex=False)
df["currency"]   = "USD"
df["exchange"]   = "NYSE/NASDAQ"
df["country"]    = "US"
df["index"]      = "SP500"
df["has_adr"]    = False
df["adr_ticker"] = ""
df.to_csv("data/sp500.csv", index=False)
print(f"Done — {len(df)} S&P 500 companies saved to data/sp500.csv")
