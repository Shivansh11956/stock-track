import os
from flask import Flask, render_template
import yfinance as yf
import pandas as pd

app = Flask(__name__)

# Load stock symbols
stock_df = pd.read_csv("stock_list.csv")

def get_breakouts():
    breakout_stocks = []
    for _, row in stock_df.iterrows():
        symbol = row['symbol']
        name = row['name']
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")

            if data.empty:
                continue

            current_price = data['Close'].iloc[-1]
            today_high = data['High'].max()
            today_low = data['Low'].min()

            if current_price > today_high:
                breakout_stocks.append((symbol, name, "Above High", current_price))
            elif current_price < today_low:
                breakout_stocks.append((symbol, name, "Below Low", current_price))

        except Exception as e:
            # print(f"Error with {symbol}: {e}")
            continue
    return breakout_stocks

@app.route('/')
def index():
    breakouts = get_breakouts()
    return render_template("index.html", stocks=breakouts)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # fallback to 5000 for local
    app.run(host='0.0.0.0', port=port, debug=True)