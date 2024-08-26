from main import trading_strategy
import requests
import time

headers={
    "accept": "application/json",
    "APCA-API-KEY-ID": "PKFAJUYNZFD6NMBTWAWE",
    "APCA-API-SECRET-KEY": "PjL6xPoDYsg9o2u3KAEFKQVoFecL9ayVlOoambgT"
    }
def keep_trading():
    response=requests.get("https://paper-api.alpaca.markets/v2/account", headers=headers)
    account = response.json()
    cash=float(account['cash'])
    goal_profit = float(cash+50)
    print(goal_profit)
    while cash < goal_profit:
        time.sleep(1) 
        try:
            trading_strategy()
        except ValueError as e:
            print(f"Error: {e}")
            time.sleep(30)
        response=requests.get("https://paper-api.alpaca.markets/v2/account", headers=headers)
        account = response.json()

keep_trading()