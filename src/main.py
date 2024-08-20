import requests

def get_movers():
    url = "https://data.alpaca.markets/v1beta1/screener/crypto/movers?top=10"

    headers = {
    "accept": "application/json",
    "APCA-API-KEY-ID": "PKFAJUYNZFD6NMBTWAWE",
    "APCA-API-SECRET-KEY": "PjL6xPoDYsg9o2u3KAEFKQVoFecL9ayVlOoambgT"
    }

    response = requests.get(url, headers=headers)

    print(response.text)

get_movers()