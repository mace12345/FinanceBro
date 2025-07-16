import requests
import pandas as pd
import time
import os
import numpy as np

# === API Setup ===
T212_URL = "https://live.trading212.com/api/v0/equity/portfolio"
T212_HEADERS = {"Authorization": "33802252ZVGbljRTOZojjmDWqtOEfAgKdUMCZ"}
AV_API_KEY = "89PV2157O3JISFQ3"
AV_BASE_URL = "https://www.alphavantage.co/query"

# === Helper: Clean ticker ===
def clean_ticker(ticker: str) -> str:
    return ticker.upper().split('_')[0]

# === Helper: Get Alpha Vantage Metadata ===
def get_company_info_av(ticker: str) -> dict:
    params = {
        "function": "OVERVIEW",
        "symbol": ticker,
        "apikey": AV_API_KEY
    }
    try:
        res = requests.get(AV_BASE_URL, params=params)
        data = res.json()
        print(data)
        return {
            "Company Name": data.get("Name", "N/A"),
            "Currency": data.get("Currency", "N/A"),
            "Sector": data.get("Sector", "N/A"),
            "Industry": data.get("Industry", "N/A"),
            "Country": data.get("Country", "N/A"),
        }
    except Exception:
        return {
            "Company Name": "N/A",
            "Currency": "N/A",
            "Sector": "N/A",
            "Industry": "N/A",
            "Country": "N/A"
        }

# === Helper: Get FX rate to GBP ===
fx_cache = {}

def get_fx_to_gbp(from_currency: str) -> float:
    if from_currency == "GBP":
        return 1.0
    if from_currency in fx_cache:
        return fx_cache[from_currency]

    params = {
        "function": "CURRENCY_EXCHANGE_RATE",
        "from_currency": from_currency,
        "to_currency": "GBP",
        "apikey": AV_API_KEY
    }
    try:
        res = requests.get(AV_BASE_URL, params=params)
        data = res.json()
        rate_str = data.get("Realtime Currency Exchange Rate", {}).get("5. Exchange Rate", "1.0")
        fx_rate = float(rate_str)
    except Exception:
        fx_rate = np.nan  # fallback in case of failure
    fx_cache[from_currency] = fx_rate
    time.sleep(13)  # Respect rate limits
    return fx_rate

response = requests.get(T212_URL, headers=T212_HEADERS)

if response.status_code != 200:
    print(f"Failed to fetch Trading212 data. Status code: {response.status_code}")
    exit()

data = response.json()
df = pd.DataFrame()

for idx, share in enumerate(data):
    raw_ticker = share.get("ticker", "")
    ticker = clean_ticker(raw_ticker)

    #info = get_company_info_av(ticker)
    #currency = info["Currency"]

    #fx_rate = get_fx_to_gbp(currency)
    #current_price = share["currentPrice"]
    quantity = share["quantity"]
    #price_gbp = current_price * fx_rate
    #position_size = quantity * current_price
    #position_size_gbp = position_size * fx_rate

    df.loc[idx, "Trading 212 Ticker"] = raw_ticker
    df.loc[idx, "Ticker"] = ticker
    df.loc[idx, "Quantity"] = quantity
    """df.loc[idx, "Company Name"] = info["Company Name"]
    df.loc[idx, "Sector"] = info["Sector"]
    df.loc[idx, "Industry"] = info["Industry"]
    df.loc[idx, "Country"] = info["Country"]
    df.loc[idx, "Currency"] = currency
    df.loc[idx, "FX Rate to GBP"] = fx_rate
    df.loc[idx, "Quantity"] = quantity
    df.loc[idx, "Current Price"] = current_price
    df.loc[idx, "Price in GBP"] = price_gbp
    df.loc[idx, "Position Size"] = position_size
    df.loc[idx, "Position Size in GBP"] = position_size_gbp"""
    print(share)

    #time.sleep(3)  # polite delay for yfinance to avoid throttling
    #break

# === OUTPUT ===
print(df)

#output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "T212_Portfolio.csv")
#df.to_csv(output_path)

