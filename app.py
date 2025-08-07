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

            # Get 2 days of 1-min data
            data = ticker.history(period="2d", interval="1m")

            if data.empty or len(data) < 2:
                continue

            # Separate by date
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

            # Step 2 + 3: Full Confirmation for breakout/breakdown
            if current_price > today_high:
                if today_high > yesterday_high and body > 0.002 * current_price:
                    breakout_stocks.append({
                        'symbol': symbol,
                        'name': name,
                        'status': "Above High (Breakout)",
                        'current_price': round(current_price, 2),
                        'today_high': round(today_high, 2),
                        'today_low': round(today_low, 2),
                        'yesterday_high': round(yesterday_high, 2),
                        'yesterday_low': round(yesterday_low, 2)
                    })

            elif current_price < today_low:
                if today_low < yesterday_low and body > 0.002 * current_price:
                    breakout_stocks.append({
                        'symbol': symbol,
                        'name': name,
                        'status': "Below Low (Breakdown)",
                        'current_price': round(current_price, 2),
                        'today_high': round(today_high, 2),
                        'today_low': round(today_low, 2),
                        'yesterday_high': round(yesterday_high, 2),
                        'yesterday_low': round(yesterday_low, 2)
                    })

            # 🔄 Step 4: Pullback Confirmation (weak confirmation)
            elif abs(current_price - today_high) / today_high < 0.003 and today_high > yesterday_high:
                # Stock pulled back near today’s high (from breakout)
                breakout_stocks.append({
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
                breakout_stocks.append({
                    'symbol': symbol,
                    'name': name,
                    'status': "Pullback Near Low (Weak Confirm)",
                    'current_price': round(current_price, 2),
                    'today_high': round(today_high, 2),
                    'today_low': round(today_low, 2),
                    'yesterday_high': round(yesterday_high, 2),
                    'yesterday_low': round(yesterday_low, 2)
                })

        except Exception as e:
            continue

    return breakout_stocks

@app.route('/')
def index():
    breakouts = get_breakouts()
    return render_template("index.html", stocks=breakouts)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
