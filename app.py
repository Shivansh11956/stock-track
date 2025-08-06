from flask import Flask, render_template
import yfinance as yf
import pandas as pd

app = Flask(__name__)

# Load stock list
stock_df = pd.read_csv("stock_list.csv")  # Should have columns: symbol,name

def get_breakouts():
    breakout_stocks = []
    for _, row in stock_df.iterrows():
        symbol = row['symbol']
        name = row['name']
        print(f"Checking: {symbol}")

        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")

            if data.empty:
                print(f"⚠ No data for {symbol} — likely because market is closed")
                continue

            current_price = data['Close'].iloc[-1]
            today_high = data['High'].max()
            today_low = data['Low'].min()

            status = None
            if current_price > today_high:
                status = "Above High"
            elif current_price < today_low:
                status = "Below Low"

            if status:
                breakout_stocks.append({
                    'symbol': symbol,
                    'name': name,
                    'status': status,
                    'price': round(current_price, 2),
                    'high': round(today_high, 2),
                    'low': round(today_low, 2)
                })

        except Exception as e:
            print(f"Error with {symbol}: {e}")
            continue

    return breakout_stocks

@app.route('/')
def index():
    stocks = get_breakouts()
    return render_template("index.html", stocks=stocks)

if __name__ == '__main__':
    app.run(debug=True)