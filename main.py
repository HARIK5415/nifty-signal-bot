import time
from strategy1 import execute_strategy

symbol = "NIFTY"

while True:
    try:
        print("🔄 Checking breakout condition for", symbol)
        execute_strategy(symbol)
    except Exception as e:
        print("❌ Error:", e)

    time.sleep(60)  # check every minute
