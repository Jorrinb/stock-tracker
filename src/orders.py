import requests
import time
headers={
"accept": "application/json",
"APCA-API-KEY-ID": "PKFAJUYNZFD6NMBTWAWE",
"APCA-API-SECRET-KEY": "PjL6xPoDYsg9o2u3KAEFKQVoFecL9ayVlOoambgT"
}

def get_orders(id):
    response = requests.get(f"https://paper-api.alpaca.markets/v2/orders/{id}", headers=headers)
    order=response.json()
    return order

def buy_order(ticker,qty):
    payload = {
    "side": "buy",
    "type": "market",
    "time_in_force": "day",
    "symbol": f"{ticker}",
    "qty": f"{qty}"
    }
    response = requests.post("https://paper-api.alpaca.markets/v2/orders", json=payload, headers=headers)
    order=response.json()
    print(f'Buy order placed for {qty} of ${ticker}')
    # Retrieve the filled order to get the buy price
    print(order)
    buy_price =order['filled_avg_price']
    id=order['id']
    while buy_price == None:
        time.sleep(1)
        order=get_orders(id)
        buy_price =order['filled_avg_price']
    return buy_price

def sell_order(ticker,qty,type,stop_price):
    url = "https://paper-api.alpaca.markets/v2/orders"
    if type=="stop":
        payload = {
            "side": "sell",
            "type": "stop",
            "time_in_force": "day",
            "symbol": f"{ticker}",
            "qty": f"{qty}",
            "extended_hours": False,
            "stop_price": f"{stop_price}"
            }
    elif type=="market":
        payload = {
            "side": "sell",
            "type": "market",
            "time_in_force": "day",
            "symbol": f"{ticker}",
            "qty": f"{qty}",
            "extended_hours": False,
        }
    response = requests.post(url, json=payload, headers=headers)
    confirmation=response.json()
    while 'status' not in confirmation:
        print(confirmation)
        time.sleep(1)
        response = requests.post(url, json=payload, headers=headers)
        confirmation=response.json()
    while 'status' in confirmation:
        while confirmation['status']!="accepted" and confirmation['status']!="filled" and confirmation['status']!="new" :
            print(f'Sell order NOT placed for {ticker} at ${stop_price} yet')
            print(confirmation['status'])
            time.sleep(2)
            id=confirmation['id']
            response = requests.get(f"https://paper-api.alpaca.markets/v2/orders/{id}", headers=headers)
            confirmation=response.json()
        return id

def cancel_order(id):
    response = requests.delete(f"https://paper-api.alpaca.markets/v2/orders/{id}", headers=headers)
    return

def check_stop_limit(id):
    stop_limit=get_orders("3455e9f7-d79b-41c1-b74b-db7501723bbc")
    if stop_limit['status']=="filled" or stop_limit['status']=="canceled":
        return False
    else:
        return True

def get_postions(symbol):
    url = f"https://paper-api.alpaca.markets/v2/positions/{symbol}"
    response = requests.get(url, headers=headers)
    postions= response.json()
    if 'meassage' in postions:
        return False
    else:
        return True