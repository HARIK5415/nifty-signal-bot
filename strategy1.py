import datetime
from strategy_common import (
    get_latest_ohlc,
    load_previous_day_high_low,
    calculate_intraday_median_volume,
    calculate_intraday_max_range,
    already_alerted_today,
    mark_alerted_today,
)
from telegram_utils import send_telegram_message, log_signal_to_csv

SL_POINTS = 125
TP_POINTS = 270

def execute_strategy(symbol, interval="15minute"):
    now = datetime.datetime.now()
    allowed_start = datetime.time(9, 30)
    allowed_end = datetime.time(15, 0)

    if not (allowed_start <= now.time() <= allowed_end):
        print("⏳ Outside trading window (9:30 AM – 3:00 PM). Skipping...")
        return
    today = now.date()

    ohlc = get_latest_ohlc(symbol, interval)
    if not ohlc or len(ohlc) < 2:
        print(f"⚠️ Not enough candles for {symbol}")
        return

    last_candle = ohlc[-1]
    high = float(last_candle["high"])
    low = float(last_candle["low"])
    close = float(last_candle["close"])
    volume = float(last_candle.get("volume", 0))
    candle_range = high - low
    candle_time = last_candle["datetime"]

    prev_high, prev_low = load_previous_day_high_low(symbol, today)
    median_vol = calculate_intraday_median_volume(ohlc)
    max_range = calculate_intraday_max_range(ohlc)
    range_threshold = 0.75 * max_range

    if already_alerted_today(symbol, today):
        print(f"✅ Already alerted today for {symbol}")
        return

    if volume > median_vol and candle_range > range_threshold:
        signal = None
        sl = None
        target = None

        if high > prev_high:
            signal = "BUY"
            sl = close - SL_POINTS
            target = close + TP_POINTS
        elif low < prev_low:
            signal = "SELL"
            sl = close + SL_POINTS
            target = close - TP_POINTS

        if signal:
            message = (
                f"📈 NIFTY BREAKOUT SIGNAL ({signal})\n\n"
                f"🕒 Time: {candle_time}\n"
                f"📊 Price: {close}\n"
                f"🔼 SL: {round(sl, 2)}\n"
                f"🎯 Target: {round(target, 2)}\n"
                f"🔍 Volume: {int(volume)} > Median: {int(median_vol)}\n"
                f"📏 Range: {round(candle_range, 2)} > 75% of Max: {round(range_threshold, 2)}"
            )

            send_telegram_message(message)
            log_signal_to_csv(today, symbol, signal, close, sl, target)
            mark_alerted_today(symbol, today)
            print("📤 Signal sent:", signal)
    else:
        print(f"⏳ No valid breakout yet for {symbol}")
