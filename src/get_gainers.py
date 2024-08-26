import requests
headers={
    "accept": "application/json",
    "APCA-API-KEY-ID": "PKFAJUYNZFD6NMBTWAWE",
    "APCA-API-SECRET-KEY": "PjL6xPoDYsg9o2u3KAEFKQVoFecL9ayVlOoambgT"
    }

def price_filter(data):
    symbol=[]
    for stock in data:
        if stock['price']<= 9 and stock['price']<= 1:
            symbol.append(stock['symbol'])
    return symbol

def get_top_movers():
    response = requests.get("https://data.alpaca.markets/v1beta1/screener/stocks/movers?top=20", headers=headers)
    movers=response.json()
    return price_filter(movers['gainers'])

