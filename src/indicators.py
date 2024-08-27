import requests
import pandas as pd
import yfinance as yf
from datetime import date, timedelta,datetime,time

headers={
    "accept": "application/json",
    "APCA-API-KEY-ID": "PKFAJUYNZFD6NMBTWAWE",
    "APCA-API-SECRET-KEY": "PjL6xPoDYsg9o2u3KAEFKQVoFecL9ayVlOoambgT"
    }

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


def calculate_macd(df):
    fast_period=12
    slow_period=26
    signal_period=9
    """Calculate MACD and Signal Line."""
    # Calculate the Fast and Slow EMAs
    df['Fast_EMA'] = df['close'].ewm(span=fast_period, adjust=False).mean()
    df['Slow_EMA'] = df['close'].ewm(span=slow_period, adjust=False).mean()

    # Calculate the MACD Line
    df['MACD'] = df['Fast_EMA'] - df['Slow_EMA']

    # Calculate the Signal Line
    df['Signal_Line'] = df['MACD'].ewm(span=signal_period, adjust=False).mean()

    return df

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
