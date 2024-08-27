import requests

def add_candlestick_features(df):
    """Add body size, upper shadow, and lower shadow to the DataFrame."""
    df['Body_Size'] = abs(df['Close'] - df['Open'])
    df['Upper_Shadow'] = df['High'] - df[['Close', 'Open']].max(axis=1)
    df['Lower_Shadow'] = df[['Close', 'Open']].min(axis=1) - df['Low']
    return df

def detect_green_shooting_star(df):
    """Check if there's a green shooting star pattern in the last two bars."""
    # Calculate the conditions for a green shooting star
    conditions = (
        (df['bs'] < df['us'] * 0.3) &  # Small body relative to upper shadow
        (df['us'] > 2 * df['bs']) &  # Long upper shadow
        (df['ls'] < df['bs'] * 0.2)  # Small lower shadow
    )

    # Check the last two bars
    last_two_bars = conditions[-2:]  # Get the conditions for the last two bars

    # If any of the last two bars are a green shooting star, return False
    if last_two_bars.any():
        return False
    else:
        return True
    
def detect_hammer(df):
    """Check for red hammer patterns in the last two bars."""
    if df.empty:return False
    conditions = (
        (df['ls'] > 2 * df['bs']) &  # Long lower shadow
        (df['us'] < df['bs'] * 0.2)  # Small upper shadow
    )

    # Check the last two bars
    last_two_bars = conditions[-2:]  # Get the conditions for the last two bars

    # If any of the last two bars are a red hammer, return True
    if last_two_bars.any():
        return True
    else:
        return False