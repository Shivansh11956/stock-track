import os
from flask import Flask, render_template
import yfinance as yf
import pandas as pd

app = Flask(__name__)

csv_path = os.path.join(os.path.dirname(__file__), "stock_list.csv")
stock_df = pd.read_csv(csv_path)

def get_breakouts():
    bullish_stocks = []
    bearish_stocks = []
    remaining_stocks = []
    for _, row in stock_df.iterrows():
        symbol = row['symbol']
        name = row['name']

        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="2d", interval="1m")

            if data.empty or len(data) < 2:
                continue

            data['Date'] = data.index.date
            dates = sorted(data['Date'].unique())

            if len(dates) < 2:
                continue

            yesterday_data = data[data['Date'] == dates[0]]
            today_data = data[data['Date'] == dates[1]]

            if today_data.empty or yesterday_data.empty:
                continue

            current_price = today_data['Close'].iloc[-1]
            today_high = today_data['High'].max()
            today_low = today_data['Low'].min()
            yesterday_high = yesterday_data['High'].max()
            yesterday_low = yesterday_data['Low'].min()
            body = abs(today_data['Close'].iloc[-1] - today_data['Open'].iloc[0])

            # Bullish (Above High)
            if current_price > today_high:
                if today_high > yesterday_high and body > 0.002 * current_price:
                    bullish_stocks.append({
                        'symbol': symbol,
                        'name': name,
                        'status': "Breakout",
                        'current_price': round(current_price, 2),
                        'today_high': round(today_high, 2),
                        'today_low': round(today_low, 2),
                        'yesterday_high': round(yesterday_high, 2),
                        'yesterday_low': round(yesterday_low, 2)
                    })

            # Bearish (Below Low)
            elif current_price < today_low:
                if today_low < yesterday_low and body > 0.002 * current_price:
                    bearish_stocks.append({
                        'symbol': symbol,
                        'name': name,
                        'status': "Breakdown",
                        'current_price': round(current_price, 2),
                        'today_high': round(today_high, 2),
                        'today_low': round(today_low, 2),
                        'yesterday_high': round(yesterday_high, 2),
                        'yesterday_low': round(yesterday_low, 2)
                    })
            elif abs(current_price - today_high) / today_high < 0.003 and today_high > yesterday_high:
                # Stock pulled back near today’s high (from breakout)
                bullish_stocks.append({
                    'symbol': symbol,
                    'name': name,
                    'status': "Pullback Near High (Weak Confirm)",
                    'current_price': round(current_price, 2),
                    'today_high': round(today_high, 2),
                    'today_low': round(today_low, 2),
                    'yesterday_high': round(yesterday_high, 2),
                    'yesterday_low': round(yesterday_low, 2)
                })

            elif abs(current_price - today_low) / today_low < 0.003 and today_low < yesterday_low:
                # Stock pulled back near today’s low (from breakdown)
                bearish_stocks.append({
                    'symbol': symbol,
                    'name': name,
                    'status': "Pullback Near Low (Weak Confirm)",
                    'current_price': round(current_price, 2),
                    'today_high': round(today_high, 2),
                    'today_low': round(today_low, 2),
                    'yesterday_high': round(yesterday_high, 2),
                    'yesterday_low': round(yesterday_low, 2)
                })
            else :
                remaining_stocks.append({
                    'symbol': symbol,
                    'name': name,
                    'status': "NULL",
                    'current_price': round(current_price, 2),
                    'today_high': round(today_high, 2),
                    'today_low': round(today_low, 2),
                    'yesterday_high': round(yesterday_high, 2),
                    'yesterday_low': round(yesterday_low, 2)
                })
        except Exception:
            continue

    return bullish_stocks, bearish_stocks, remaining_stocks


@app.route('/')
def index():
    bullish, bearish, remaining = get_breakouts()
    return render_template("index.html", bullish_stocks=bullish, bearish_stocks=bearish, remaining_stocks = remaining)


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
