import requests
import json
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def get_price(symbol):
    try:
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
        return float(requests.get(url, timeout=10).json()["price"])
    except:
        return None

def get_history(symbol, days=7):
    try:
        end = int(datetime.now().timestamp() * 1000)
        start = int((datetime.now() - timedelta(days=days)).timestamp() * 1000)
        url = f"https://api.binance.com/api/v3/klines?symbol={symbol}USDT&interval=1d&startTime={start}&endTime={end}"
        data = requests.get(url).json()
        df = pd.DataFrame(data, columns=['ts', 'open',  'high',  'low',  'close',  'v',  'ct',  'qav',  'trades',  'tb',  'tq',  'ignore'])
        df['close'] = df['close'].astype(float)
        df['date'] = pd.to_datetime(df['ts'], unit='ms').dt.strftime('%m-%d')
        return df[['date', 'close']]
    except:
        return pd.DataFrame()

# Load portfolio
with open("portfolio.json") as f:
    assets = json.load(f)["assets"]

total_value = 0
total_invested = 0
print("Your Crypto Portfolio")
print("-" * 55)

for a in assets:
    symbol = a["symbol"]
    amount = a["amount"]
    buy_price = a["buy_price"]
    current = get_price(symbol)
    
    if current:
        value = amount * current
        invested = amount * buy_price
        profit = value - invested
        total_value += value
        total_invested += invested
        
        print(f"{symbol:4} × {amount:8} → ${current:9,.2f} | Bought @ ${buy_price:,} | P&L: ${profit:+8,.2f}")
    else:
        print(f"{symbol:4} — failed to fetch price")

print("-" * 55)
if total_invested > 0:
    pnl = total_value - total_invested
    pnl_pct = pnl / total_invested * 100
    print(f"Total portfolio value:  ${total_value:,.2f}")
    print(f"Total invested:         ${total_invested:,.2f}")
    print(f"Profit/Loss:            ${pnl:+,.2f} ({pnl_pct:+.2f}%)")
print()

# BTC 7-day chart
print("Generating 7-day BTC price chart...")
df = get_history("BTC")
if not df.empty:
    plt.figure(figsize=(10, 6))
    plt.plot(df['date'], df['close'], marker='o', color='#f7931a', linewidth=2.5)
    plt.title('Bitcoin (BTC) — 7 Day Price History', fontsize=16, fontweight='bold')
    plt.xlabel('Date')
    plt.ylabel('Price (USDT)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig("btc_chart.png", dpi=200, bbox_inches='tight')
    plt.show()
    print("Chart saved as btc_chart.png")
else:
    print("Failed to load historical data")
