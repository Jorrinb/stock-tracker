import yfinance as yf
import pandas as pd
from candle_analysis import add_candlestick_features

def get_stock_data(symbol, interval="1m", period="1d"):

    # Fetch historical data using yfinance
    ticker = yf.Ticker(symbol)
    data = ticker.history(interval=interval, period=period)
    # Ensure the data is not empty
    if data.empty:
        print(f"No data found for symbol: {symbol}")
        return pd.DataFrame()  # Return an empty DataFrame if no data is found

    # Prepare the DataFrame in a similar structure to what Alpaca API would provide
    data = data.reset_index()
    data['time'] = data['Datetime'].dt.time
    data= add_candlestick_features(data)
    data = data.rename(columns={
        'Open': 'open',
        'High': 'high',
        'Low': 'low',
        'Close': 'close',
        'Volume': 'volume',
        'Lower_Shadow': 'ls',
        'Upper_Shadow': 'us',
        'Body_Size': 'bs'
    })
    # Select relevant columns
    return data[['time', 'open', 'high', 'low', 'close', 'volume','ls','us','bs']]