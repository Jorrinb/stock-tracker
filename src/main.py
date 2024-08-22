import requests
from get_gainers import price_filter
import json
from datetime import date, timedelta

today=date.today()- timedelta(days=30)

def get_movers():
    url = "https://data.alpaca.markets/v1beta1/screener/stocks/movers?top=20"

    headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": "PKFAJUYNZFD6NMBTWAWE",
    "APCA-API-SECRET-KEY": "PjL6xPoDYsg9o2u3KAEFKQVoFecL9ayVlOoambgT"
    }

    response = requests.get(url, headers=headers)
    movers=response.json()
    return price_filter(movers['gainers'])


def get_volume(ticker):
    print(today)
    url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={ticker}&timeframe=1H&start={today}&limit=1000&adjustment=raw&feed=iex&sort=asc"
    headers = {
        "accept": "application/json",
        "APCA-API-KEY-ID": "PKFAJUYNZFD6NMBTWAWE",
        "APCA-API-SECRET-KEY": "PjL6xPoDYsg9o2u3KAEFKQVoFecL9ayVlOoambgT"
    }
    response = requests.get(url, headers=headers)
    volume=response.json()
    
get_volume(get_movers())
