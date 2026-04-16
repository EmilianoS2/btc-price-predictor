import yfinance as yf
import requests

def fetch_sp500():
   ticker = yf.Ticker("^GSPC")
   hist = ticker.history(period="10d")
   close = hist['Close'].iloc[-1]
   close7d = hist['Close'].iloc[-8]
   percentage = (close-close7d) / close7d * 100
   percentage = round(percentage, 2)
   return {"sp500_7d_change_pct": float(percentage)}

def fetch_fear_greed():
   url = "https://api.alternative.me/fng/?limit=1"
   response = requests.get(url)
   index = response.json()
   data = index['data'][0]
   value = data['value']
   value_classification = data['value_classification']
   return {"fear_greed_index": int(value), "fear_greed_label": value_classification}

def fetch_btc_price():
   url = "https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=30"
   response = requests.get(url)
   btc_price = response.json()
   current_price = btc_price['prices'][-1][1]
   past_price = btc_price['prices'][0][1]
   percent = ((current_price - past_price) / past_price) * 100
   return {"btc_price_usd": float(current_price), "btc_30d_change_pct": round(percent, 2)}

def collect_macro_context():
   fetch_fear = fetch_fear_greed()
   sp500 = fetch_sp500()
   btc = fetch_btc_price()
   macro_data = {**fetch_fear, **sp500, **btc}
   return macro_data

