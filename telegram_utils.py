import requests
import pandas as pd
import datetime
import os

BOT_TOKEN = '8079023940:AAEEMdGX7hwy4XQauIW8cZd0ar_FEuFgKtg'
CHAT_ID = '1325518909'

def send_telegram_message(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={'chat_id': CHAT_ID, 'text': msg})

def log_signal_to_csv(date, symbol, signal, entry, sl, target):
    row = {
        "Date": date,
        "Symbol": symbol,
        "Signal": signal,
        "Entry": entry,
        "SL": sl,
        "Target": target
    }
    file = "pro_option_signals.csv"
    df = pd.DataFrame([row])
    df.to_csv(file, mode='a', header=not os.path.exists(file), index=False)
