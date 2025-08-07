import os
from flask import Flask, render_template
import yfinance as yf
import pandas as pd

app = Flask(__name__)


csv_path = os.path.join(os.path.dirname(__file__), "stock_list.csv")
stock_df = pd.read_csv(csv_path)

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
            today_high = data['High'].iloc[:-1].max()
            today_low = data['Low'].iloc[:-1].min()

            if current_price > today_high:
                status = "Above High"
            elif current_price < today_low:
                status = "below Low"
            else:
                continue

            breakout_stocks.append({
                'symbol': symbol,
                'name': name,
                'status': status,
                'current_price': round(current_price, 2),
                'today_high': round(today_high, 2),
                'today_low': round(today_low, 2)
            })

        except Exception:
            continue

    return breakout_stocks

@app.route('/')
def index():
    breakouts = get_breakouts()
    return render_template("index.html", stocks=breakouts)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
