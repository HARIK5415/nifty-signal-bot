import os
import json
import numpy as np
import pandas as pd
from datetime import datetime
from tvDatafeed import TvDatafeed, Interval

# ----------- Login with Username/Password -----------
USERNAME = "harik5415"
PASSWORD = "256256789Hari#"

tv = TvDatafeed(username=USERNAME, password=PASSWORD)

ALERT_TRACK_FILE = "alerted_today.json"

# ----------- Live OHLC from TradingView -------------
def get_latest_ohlc(symbol="NIFTY", interval="15minute"):
    try:
        tf_map = {
            "1minute": Interval.in_1_minute,
            "3minute": Interval.in_3_minute,
            "5minute": Interval.in_5_minute,
            "15minute": Interval.in_15_minute,
            "1hour": Interval.in_1_hour,
            "1day": Interval.in_daily
        }
        tf = tf_map.get(interval.lower(), Interval.in_15_minute)
        df = tv.get_hist(symbol=symbol, exchange="NSE", interval=tf, n_bars=20)

        if df is None or df.empty:
            return []

        candles = []
        for dt, row in df.iterrows():
            candles.append({
                "datetime": str(dt),
                "open": float(row["open"]),
                "high": float(row["high"]),
                "low": float(row["low"]),
                "close": float(row["close"]),
                "volume": float(row["volume"])
            })
        return candles
    except Exception as e:
        print("❌ Error fetching live OHLC:", e)
        return []

# ----------- Previous Day High/Low ------------------
def load_previous_day_high_low(symbol, current_date):
    try:
        df = tv.get_hist(symbol=symbol, exchange="NSE", interval=Interval.in_daily, n_bars=3)
        df = df.reset_index()
        df["date"] = pd.to_datetime(df["datetime"]).dt.date
        prev_day = df[df["date"] < current_date].iloc[-1]
        return float(prev_day["high"]), float(prev_day["low"])
    except Exception as e:
        print("❌ Error fetching prev day H/L:", e)
        return (0, 0)

# ----------- Volume & Range Stats -------------------
def calculate_intraday_median_volume(ohlc):
    volumes = [float(c["volume"]) for c in ohlc if "volume" in c]
    return np.median(volumes)

def calculate_intraday_max_range(ohlc):
    ranges = [(float(c["high"]) - float(c["low"])) for c in ohlc]
    return max(ranges) if ranges else 0

# ----------- Alert Tracking -------------------------
def already_alerted_today(symbol, date):
    if not os.path.exists(ALERT_TRACK_FILE):
        return False
    with open(ALERT_TRACK_FILE, "r") as f:
        data = json.load(f)
    return data.get(symbol) == str(date)

def mark_alerted_today(symbol, date):
    data = {}
    if os.path.exists(ALERT_TRACK_FILE):
        with open(ALERT_TRACK_FILE, "r") as f:
            data = json.load(f)
    data[symbol] = str(date)
    with open(ALERT_TRACK_FILE, "w") as f:
        json.dump(data, f)
