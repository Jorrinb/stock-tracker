import requests
from get_gainers import get_top_movers
from orders import get_orders,buy_order,sell_order, cancel_order,get_postions
from candle_analysis import detect_green_shooting_star,detect_red_hammer
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
    return detect_red_hammer(data)


# Function to check for breaking news
def check_breaking_news(ticker):
    start_time=datetime.now().date()
    response= requests.get(f"https://data.alpaca.markets/v1beta1/news?sort=desc&symbols={ticker}", headers=headers)
    news = response.json()
    return len(news) > 0

def get_avg_volume(symbol, months=3):
    # Define the end date as today
    end_date = datetime.today().strftime('%Y-%m-%d')
    
    # Calculate the start date 3 months ago
    start_date = (datetime.today() - timedelta(days=months * 30)).strftime('%Y-%m-%d')
    
    # Fetch historical data for the last 3 months
    response = requests.get( f"https://data.alpaca.markets/v2/stocks/bars?symbols={symbol}&timeframe=1day&start={start_date}&limit=1000&adjustment=raw&feed=sip&sort=asc", headers=headers)
    historical_data=response.json()
    if 'bars' in historical_data:
        volume=sum([bar['v'] for bar in historical_data['bars'][symbol]]) / len(historical_data['bars'][symbol])
        print(f"Volume: {volume}")
    else: volume=100000000000000000000
    return volume

# Function to calculate relative volume
def calculate_relative_volume(ticker,avg_volume):
    end_time = datetime.now().date()
    start_time = end_time - timedelta(days=30)
    timeframe="1Day"
    response= requests.get(f"https://data.alpaca.markets/v2/stocks/bars?symbols={ticker}&timeframe=1D&limit=1000&adjustment=raw&feed=sip&sort=asc", headers=headers)
    historical_data = response.json()
    if 'bars' in historical_data:
        print
        current_volume = historical_data['bars'][ticker][0]['v']
        relative_volume = (current_volume / avg_volume) * 100
        print(f"Rel V:{relative_volume}")
        return relative_volume
    else:
        print(f"Error:{historical_data}")
        time.sleep(15)
        return 0

def calculate_green_tape_percentage(symbol, duration=10):
    green_trades = 0
    red_trades = 0
    total_checks = 0
    start_time = time.time()
    
    while time.time() - start_time < duration:
        print("Checking Tape")
        trade_url=f"https://data.alpaca.markets/v2/stocks/trades/latest?symbols={symbol}&feed=iex"
        response= requests.get(trade_url,headers=headers)
        trade_data=response.json()
        ticker = yf.Ticker(symbol)
        # Get the current bid and ask prices
        if 'bid' in ticker.info:
            bid_price = ticker.info['bid']
        else:
            bid_price=0
        if 'ask' in ticker.info:
            ask_price = ticker.info['ask']
        else:
            ask_price=0
        last_trade_price = trade_data['trades'][symbol]['p']

        print(f"Checking trade: Bid Price: {bid_price}, Ask Price: {ask_price}, Last Trade Price: {last_trade_price}")

        if last_trade_price == ask_price:
            green_trades = green_trades+trade_data['trades'][symbol]['s']
        elif last_trade_price == bid_price:
            red_trades = red_trades+trade_data['trades'][symbol]['s']
        
        total_checks += 1
        time.sleep(1)  # Wait for 1 second before checking again
    if green_trades==0:
        green_percentage=0
    else:
        green_percentage = (green_trades / total_checks) * 100
    if red_trades==0:
        red_percentage=0
    else:
        red_percentage = (red_trades / total_checks) * 100

    
    print(f"greenp {green_percentage}")
    print(f"redp{red_percentage}")
    return green_percentage, red_percentage

# Function to place a stop-loss order 10 cents below the buy price
def place_stop_loss_order(ticker, qty, buy_price):
    url = "https://paper-api.alpaca.markets/v2/orders"
    # 10 cents below buy price
    buy_price=float(buy_price)
    stop_price = round(buy_price - 0.10,2)
    id=sell_order(ticker,qty,"stop",stop_price)
    print(f'Stop-loss order placed for {ticker} at ${stop_price}')
    return id

# Function to sell full position if price doesn't go up by 10 cents or if tape turns red
def monitor_price_and_tape(ticker, qty, buy_price,sl_id):
    time.sleep(45)
    # Check the open price after 1 minute
    latest_data = get_stock_data(ticker)
    current_open_price = latest_data.iloc[-1]['open']
    if current_open_price <= round(float(buy_price) + 0.10,2):
        if get_postions(ticker):
            print(f'{ticker}: Price did not increase by 10 cents. Selling full position...')
            cancel_order(sl_id)
            sell_order(ticker,qty,"market",0)
            print(f'Full position sold for {ticker}')
            return
        else: return
    while get_postions(ticker):
        time.sleep(15)  # Wait for 15 seconds
        # Check the open price after 15 seconds
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
                            print(buy_price)

                            # Place a stop-loss order 10 cents below the buy price
                            stop_loss_id=place_stop_loss_order(ticker, qty, buy_price)
                        
                            # Monitor the price and tape, and sell if conditions are not met
                            monitor_price_and_tape(ticker, qty, buy_price,stop_loss_id)

