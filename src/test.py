import yfinance as yf
from datetime import date, timedelta,datetime
import requests
import time
from orders import check_stop_limit, cancel_order, sell_order,get_postions
headers={
    "accept": "application/json",
    "APCA-API-KEY-ID": "PKFAJUYNZFD6NMBTWAWE",
    "APCA-API-SECRET-KEY": "PjL6xPoDYsg9o2u3KAEFKQVoFecL9ayVlOoambgT"
    }
# end_date = (datetime.today()- timedelta(days=10)).strftime('%Y-%m-%d')

# start_date = (datetime.today() - timedelta(days=1 * 30)).strftime('%Y-%m-%d')
    
# symbol = 'PTWOW'
# # ticker = yf.Ticker(symbol)
# # data = ticker.history(period="5d",start=start_date, end=end_date)
# # print(data)
# # # Get( the current bid and ask prices
# # print(ticker.info)
# # if 'bid' in ticker.info:
# #     bid_price = ticker.info['bid']
# # else:
# #     bid_price=0
# # if 'ask' in ticker.info:
# #     ask_price = ticker.info['ask']
# # else:
# #     ask_price=0
# # print(float(bid_price-.10))

# # print(f"Bid Price: {bid_price}, Ask Price: {ask_price}")
# url = f"https://data.alpaca.markets/v2/stocks/bars?symbols={symbol}&timeframe=1day&start={start_date}&limit=1000&adjustment=raw&feed=sip&sort=asc"
# response = requests.get(url, headers=headers)
# historical_data=response.json()
# volume=sum([bar['v'] for bar in historical_data['bars'][symbol]]) / len(historical_data['bars'][symbol])
# print(volume)
def monitor_price_and_tape(ticker, qty, buy_price,sl_id):
    time.sleep(45)
    if current_open_price <= round(float(buy_price) + 0.10,2):
        if get_postions(ticker):
            print(f'{ticker}: Price did not increase by 10 cents. Selling full position...')
            cancel_order(sl_id)
            sell_order(ticker,qty,"market",0)
            print(f'Full position sold for {ticker}')
            return
        else: return
    while get_postions(ticker):
        time.sleep(15)  # Wait for 30 seconds
        
        # Check the open price after 1 minute
        latest_data = get_stock_data(ticker)
        current_open_price = latest_data.iloc[-1]['open']
        
        # Check the green and red percentages on the tape in the last 30 seconds
        _, red_percentage = calculate_green_tape_percentage(ticker, duration=30)
        
        if red_percentage > 60 or red_percentage==0:
            print(f'{ticker}: Red trades on tape exceeded 60%. Selling full position...')
            cancel_order(sl_id)
            sell_order(ticker,qty,"market",0)
            print(f'Full position sold for {ticker}')
            return  # Exit after selling
        
        if detect_green_shooting_star(latest_data):
            print(f'{ticker}: Red trades on tape exceeded 60%. Selling full position...')
            cancel_order(sl_id)
            sell_order(ticker,qty,"market",0)
            print(f'Full position sold for {ticker}')
            return  # Exit after selling