import requests
import pandas as pd
import time
import os
import numpy as np


class T212Portfolio:
    def __init__(
        self,
        portfolio_path: str,
        T212_API_KEY: str,
        AV_API_KEY: str,
        FINNHUB_API_KEY: str,
        T212_URL="https://live.trading212.com/api/v0/equity/portfolio",
        AV_BASE_URL="https://www.alphavantage.co/query",
    ):
        self.portfolio_path = portfolio_path
        self.T212_API_KEY = T212_API_KEY
        self.AV_API_KEY = AV_API_KEY
        self.FINNHUB_API_KEY = (FINNHUB_API_KEY,)
        self.T212_URL = T212_URL
        self.AV_BASE_URL = AV_BASE_URL

        self.T212_Ticker_df = pd.read_csv(
            os.path.join(
                os.path.dirname(os.path.abspath(__file__)), "T212_Ticker_Dict.csv"
            ),
        )
        self.T212_Ticker_df.set_index("Trading 212 Ticker", inplace=True)
        self.T212_Ticker_df.fillna("NO_DATA", inplace=True)

        self.PortfolioDF = pd.DataFrame()
        self.fx_cache = {
            "GBP_to_USD": self.get_exchange_rate("GBP", "USD"),
            "USD_to_GBP": self.get_exchange_rate("USD", "GBP"),
            "EUR_to_GBP": self.get_exchange_rate("EUR", "GBP"),
            "GBP_to_EUR": self.get_exchange_rate("GBP", "EUR"),
            "CAD_to_GBP": self.get_exchange_rate("CAD", "GBP"),
            "GBP_to_CAD": self.get_exchange_rate("GBP", "CAD"),
            "GBP_to_GBX": 100,
            "GBX_to_GBP": 0.01,
            "GBP_to_GBP": 1,
        }

    def get_exchange_rate(self, base, target):
        url = f"https://api.frankfurter.app/latest?from={base}&to={target}"
        response = requests.get(url)
        data = response.json()
        rate = data["rates"][target]
        return rate

    def get_company_profile(self, ticker, api_key):
        url = f"https://finnhub.io/api/v1/stock/profile2"
        params = {"symbol": ticker, "token": api_key}
        response = requests.get(url, params=params)
        data = response.json()

        # Extract desired fields
        name = data.get("name", "N/A")
        country = data.get("country", "N/A")
        industry = data.get("finnhubIndustry", "N/A")
        sector = data.get("sector", "N/A")  # Only available for some stocks

        return {
            "name": name,
            "country": country,
            "industry": industry,
            "sector": sector,
        }

    def update_T212_Ticker_df(self):
        pass

    def fetch_portfolio(self):
        headers = {"Authorization": self.T212_API_KEY}
        try:
            res = requests.get(self.T212_URL, headers=headers)
            res.raise_for_status()
            data = res.json()
        except requests.RequestException as e:
            print(f"Error fetching portfolio: {e}")
            return None
        for idx, share in enumerate(data):

            t212_ticker = share["ticker"]
            ticker = self.T212_Ticker_df.loc[t212_ticker, "Actural Ticker"]
            name = self.T212_Ticker_df.loc[t212_ticker, "Instrament Name"]
            currency = self.T212_Ticker_df.loc[t212_ticker, "Currency"]
            sector = self.T212_Ticker_df.loc[t212_ticker, "Sector"]
            industry = self.T212_Ticker_df.loc[t212_ticker, "Industry"]
            country = self.T212_Ticker_df.loc[t212_ticker, "Country"]

            quantity = share["quantity"]
            current_price = share["currentPrice"]
            position_value = quantity * current_price
            position_value_GBP = position_value * self.fx_cache[f"{currency}_to_GBP"]

            self.PortfolioDF.loc[idx, "Ticker"] = ticker
            self.PortfolioDF.loc[idx, "Instrament Name"] = name
            self.PortfolioDF.loc[idx, "Currency"] = currency
            self.PortfolioDF.loc[idx, "Quantity"] = quantity
            self.PortfolioDF.loc[idx, "Current Price"] = current_price
            self.PortfolioDF.loc[idx, "Position Value"] = round(position_value, 2)
            self.PortfolioDF.loc[idx, "Position Value (GBP)"] = round(
                position_value_GBP, 2
            )
            self.PortfolioDF.loc[idx, "Sector"] = sector
            self.PortfolioDF.loc[idx, "Industry"] = industry
            self.PortfolioDF.loc[idx, "Country"] = country

        self.PortfolioDF["Position Value (%)"] = (
            self.PortfolioDF["Position Value (GBP)"] * 100
        ) / self.PortfolioDF["Position Value (GBP)"].sum()

        self.PortfolioDF.to_csv(self.portfolio_path, index=False)
