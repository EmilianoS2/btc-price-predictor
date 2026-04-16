import requests
import pandas as pd
import ta

def fetch_btc_data():
    prices = []
    volumes = []
    url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=30"
    response = requests.get(url)
    data = response.json()
    for price in data['prices']:
        prices.append(price[1])
    for volume in data['total_volumes']:
        volumes.append(volume[1])
    df = pd.DataFrame(prices, columns=["close"])
    df['rsi'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
    df['ema'] = ta.trend.EMAIndicator(close=df['close'], window=14).ema_indicator()
    df['volume'] = volumes 
    df['vwap'] = (df['close'] * df['volume']).cumsum() / df['volume'].cumsum()
    df = df.iloc[-1][['rsi', 'ema', 'vwap']]
    return df

def analyze_indicators():
    indicators = fetch_btc_data()
    return indicators.to_dict()
