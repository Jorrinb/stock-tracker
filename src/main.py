import requests
from get_gainers import get_top_movers
from orders import get_orders,buy_order,sell_order, cancel_order,get_postions
from candle_analysis import detect_green_shooting_star,detect_hammer
from indicators import calculate_relative_volume, get_avg_volume,check_breaking_news,calculate_green_tape_percentage
from stocks import get_stock_data
import json
from datetime import date, timedelta,datetime
import pandas as pd
import yfinance as yf
import time
import json

ticker=""
start_time=""
end_time=""
timeframe=""
today=date.today()- timedelta(days=30)

headers={
    "accept": "application/json",
    "APCA-API-KEY-ID": "PKFAJUYNZFD6NMBTWAWE",
    "APCA-API-SECRET-KEY": "PjL6xPoDYsg9o2u3KAEFKQVoFecL9ayVlOoambgT"
    }

def check_candlestick_pattern(data):
    return detect_hammer(data)


# Function to place a stop-loss order 10 cents below the buy price
def place_stop_loss_order(ticker, qty, buy_price):
    url = "https://paper-api.alpaca.markets/v2/orders"
    # 10 cents below buy price
    buy_price=float(buy_price)
    stop_price = buy_price
    id=sell_order(ticker,qty,"stop",stop_price)
    print(f'Stop-loss order placed for {ticker} at ${stop_price}')
    return id

# Function to sell full position if price doesn't go up by 10 cents or if tape turns red
def monitor_price_and_tape(ticker, qty, buy_price,sl_id,stop_loss):
    profit_limit=(float(buy_price)-float(stop_loss))*2
    time.sleep(45)
    # Check the open price after 1 minute
    latest_data = get_stock_data(ticker)
    current_open_price = latest_data.iloc[-1]['open']

    while get_postions(ticker):
        time.sleep(5)  # Wait for 15 seconds
        # Check the open price after 15 seconds
        latest_data = get_stock_data(ticker)
        current_open_price = latest_data.iloc[-1]['open']
        
        if current_open_price>= profit_limit:
            if get_postions(ticker):
                print(f'{ticker}: Price hit profit limit. Selling full position...')
                cancel_order(sl_id)
                sell_order(ticker,qty,"market",0)
                print(f'Full position sold for {ticker}')
            return
        
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



# Function to calculate the number of shares to buy based on 10% of buying power
def calculate_position_size(ticker):
    response=requests.get("https://paper-api.alpaca.markets/v2/account", headers=headers)
    account = response.json()
    url = f"https://data.alpaca.markets/v2/stocks/trades/latest?symbols={ticker}&feed=iex"
    response = requests.get(url, headers=headers)
    trade_data=response.json()
    buying_power = float(account['cash'])
    allocation = buying_power * 0.10  # 10% of buying power
    current_price = trade_data['trades'][ticker]['p']
    qty = int(allocation / current_price)
    return qty

# Function to monitor and trade
def trading_strategy():
    top_movers = get_top_movers()
    for ticker in top_movers:
        if check_breaking_news(ticker):
            print(ticker)
            avg_vol=get_avg_volume(ticker)
            if avg_vol>0:
                relative_volume = calculate_relative_volume(ticker,avg_vol)
                if relative_volume >= 2:  # Check if relative volume is over 200%
                    data = get_stock_data(ticker,"1m","1d")
                    if check_candlestick_pattern(data):
                        green_tape_percentage, _ = calculate_green_tape_percentage(ticker)
                        print(f"Green_percent{green_tape_percentage}")
                        if green_tape_percentage >= 70 or green_tape_percentage==0:  # Ensure at least 70% green trades in the last minute
                            print(f'{ticker}: Pattern matched, news confirmed, relative volume high, and tape green, considering buy...')
                        
                            # Calculate position size based on 10% of buying power
                            qty = calculate_position_size(ticker)
                            if qty == 0:
                                print(f'{ticker}: Not enough buying power to make a trade.')
                                continue
                            # Place a market buy order
                            buy_price=buy_order(ticker,qty)
                            print(f"{qty} {ticker} bought at {buy_price}")
                            stop_loss=data['low'][1]
                            print(f"Low is {stop_loss}")

                            # Place a stop-loss order 10 cents below the buy price
                            stop_loss_id=place_stop_loss_order(ticker, qty, stop_loss)
                        
                            # Monitor the price and tape, and sell if conditions are not met
                            monitor_price_and_tape(ticker, qty, buy_price,stop_loss_id,stop_loss)

