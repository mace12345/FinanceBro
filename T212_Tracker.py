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
        T212_URL = "https://live.trading212.com/api/v0/equity/portfolio",
        AV_BASE_URL = "https://www.alphavantage.co/query",
    ):
        self.portfolio_path = portfolio_path
        self.T212_API_KEY = T212_API_KEY
        self.AV_API_KEY = AV_API_KEY
        self.T212

if "__main__" == __name__:
    print("Hi")