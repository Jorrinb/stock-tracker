import json

def price_filter(data):
    hard_price_limit = 20
    soft_price_limit = 10
    filtered_stocks=""
    for stock in data:
        #stocks=json.loads(stock)
        if stock['price']<= 9:
            filtered_stocks=filtered_stocks+stock['symbol']+','
            print(filtered_stocks[:-1])

    return filtered_stocks[:-1]

#def get_volume(data):
