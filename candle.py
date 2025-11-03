# Realtime 1H candlestick chart for Liquidity Pool Rate (second_per_first)
# Replace HORIZON_URL and POOL_ID before running.
# Requirements: requests, pandas, matplotlib
# pip install requests pandas matplotlib

import requests
import time
from datetime import datetime, timezone
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Rectangle
from matplotlib.animation import FuncAnimation
import getBalance as gb
import sys
args = sys.argv
TOKEN = args[1]
ISS   = args[2]

# ---------- CONFIG ----------
HORIZON_URL = "https://api.testnet.minepi.com"   # replace with your Horizon endpoint
#POOL_ID = "1838e29e36a35b82f1dfbe9d1d00471616eb5a08fdf14b2899b159061d5212b4"     # Archimedes/testPi
#SAMPLE_INTERVAL_SEC = 1     # how often to sample the pool rate (seconds)
#SAMPLE_INTERVAL_SEC = 5     # how often to sample the pool rate (seconds)
#SAMPLE_INTERVAL_SEC = 15     # how often to sample the pool rate (seconds)
SAMPLE_INTERVAL_SEC = 30     # how often to sample the pool rate (seconds)
#WINDOW_HOURS = 24            # how many hours to show on the chart
WINDOW_HOURS = 100            # how many hours to show on the chart
#TOKEN = "BALL"
#ISS   = "GDJDJ2MLP7NJLSU5FLP2CEPNHQ5FKBCYF47BCQHBUOQKQEAKSYIBSQRR"
# ----------------------------

#def fetch_pool_rate(horizon_url, pool_id):
def fetch_pool_rate(horizon_url):
    """
    Fetch liquidity pool info and compute rate = second_per_first.
    We interpret reserves[0] as first token, reserves[1] as second token:
      rate = reserve_second / reserve_first
    Returns (timestamp, rate) or (None, None) on failure.
    """
    try:
        #url = f"{horizon_url}/liquidity_pools/{pool_id}"
        #r = requests.get(url, timeout=10)
        #r.raise_for_status()
        #data = r.json()
        #reserves = data.get("reserves", [])
        #if len(reserves) < 2:
        #    return None, None
        ## Guarantee numeric amounts
        #amt0 = float(reserves[0]["amount"])
        #amt1 = float(reserves[1]["amount"])
        #if amt0 == 0:
        #    return None, None
        #rate = amt1 / amt0
        
        """"""""""""""""""""""""""""""""""""""""""""""""
        HORIZON_URL = horizon_url
        BASE = {
            "asset_type": "credit_alphanum4",  # Token type (SCP-style asset)
            "asset_code": TOKEN,               # Token symbol
            "asset_issuer": ISS
        }
        COUNTER = {"asset_type": "native"}
        url = f"{HORIZON_URL}/trades"
        params = {
            "base_asset_type": BASE["asset_type"],
            "base_asset_code": BASE["asset_code"],
            "base_asset_issuer": BASE["asset_issuer"],
            "counter_asset_type": COUNTER["asset_type"],
            "limit": 1,       # Fetch only 1 trade
            "order": "desc"   # Descending order (most recent first)
        }
        response = requests.get(url, params=params).json()
        records = response["_embedded"]["records"]
        price_obj = records[0]["price"]
        #price = float(price_obj["n"]) / float(price_obj["d"])
        rate   = float(price_obj["n"]) / float(price_obj["d"])
        """"""""""""""""""""""""""""""""""""""""""""""""
        rate   = gb.getPrice(gb.HORIZON_URL,TOKEN)
        #if rate < rate_*0.05:
        #  rate = rate_
        #rate_ = rate
        ts = datetime.now(timezone.utc)
        print(TOKEN+", "+str(ts)+", "+str(rate))
        return ts, rate
    except Exception as e:
        # In production, log error
        print("fetch error:", e)
        return None, None

def make_ohlc(df_rates_1min):
    """
    Convert a series of timestamped rates (1-minute or raw samples) to 1H OHLC DataFrame.
    df_rates_1min: DataFrame with index as DatetimeIndex (UTC) and column 'rate'
    Returns OHLC DataFrame indexed by hour.
    """
    # Resample to 1H using standard OHLC aggregation
    ohlc = df_rates_1min['rate'].resample('1H').agg(['first','max','min','last'])
    #ohlc = df_rates_1min['rate'].resample('1min').agg(['first','max','min','last'])
    ohlc = ohlc.rename(columns={'first':'open','max':'high','min':'low','last':'close'})
    # drop hours with no data
    ohlc = ohlc.dropna()
    return ohlc

def draw_candles(ax, ohlc):
    """
    Draw simple candlesticks on ax using ohlc DataFrame (columns open/high/low/close).
    """
    ax.clear()
    ax.set_title(f"Liquidity Pool Rate  {TOKEN}/TestPi")
    #ax.set_ylabel(f"Liquidity Pool Rate  {TOKEN}/TestPi")
    ax.grid(True, linestyle=':', linewidth=0.5)

    if ohlc.empty:
        ax.text(0.5, 0.5, "No data yet", transform=ax.transAxes, ha='center')
        return

    dates = mdates.date2num(ohlc.index.to_pydatetime())
    #width = 0.03 * (dates[-1] - dates[0]) if len(dates) > 1 else 0.01
    width = 0.005 * (dates[-1] - dates[0]) if len(dates) > 1 else 0.001

    for idx, (dt, row) in enumerate(ohlc.iterrows()):
        openp, highp, lowp, closep = row['open'], row['high'], row['low'], row['close']
        x = dates[idx]
        # candle body
        lower = min(openp, closep)
        height = abs(closep - openp)
        # choose color automatically by comparison (no explicit color constants)
        color = 'g' if closep >= openp else 'r'
        rect = Rectangle((x - width/2, lower), width, height if height>0 else 0.0000001,
                         facecolor=color, edgecolor='k', linewidth=0.5)
        ax.add_patch(rect)
        # wick
        ax.plot([x, x], [lowp, highp], linewidth=0.8, color='k')

    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d\n%H:%M', tz=timezone.utc))
    plt.setp(ax.get_xticklabels(), rotation=25, ha='right')

def main():
    # store samples in a DataFrame (timestamp -> rate)
    samples = []
    last_sample_time = None
    #last_rate=0

    # Prepare plotting
    fig, ax = plt.subplots(figsize=(10,6))
    plt.gcf().autofmt_xdate(rotation=25)
    plt.tight_layout()

    # We'll use a closure to keep state for animation
    def update(frame):
        nonlocal last_sample_time, samples
        # sample current rate
        #ts, rate = fetch_pool_rate(HORIZON_URL, POOL_ID)
        ts, rate = fetch_pool_rate(HORIZON_URL)
        #if rate < 0.02*last_rate:
        #  rate = last_rate
        #last_rate = rate
        if ts is not None and rate is not None:
            samples.append((ts, rate))
            # keep only WINDOW_HOURS + spare data (samples may be more frequent than 1 per minute)
            cutoff = datetime.now(timezone.utc) - pd.Timedelta(hours=WINDOW_HOURS + 1)
            samples = [(t,r) for (t,r) in samples if t >= cutoff]

        if not samples:
            draw_candles(ax, pd.DataFrame())  # no data yet
            return

        # assemble DataFrame
        df = pd.DataFrame(samples, columns=['ts','rate'])
        df = df.set_index(pd.DatetimeIndex(df['ts']).tz_convert(None))  # naive index in local tz context; resample uses this
        df = df[['rate']]

        # create 1H OHLC
        ohlc = make_ohlc(df)
        # show only last WINDOW_HOURS
        if not ohlc.empty:
            ohlc = ohlc.tail(WINDOW_HOURS)
        draw_candles(ax, ohlc)

    # Use FuncAnimation to update every SAMPLE_INTERVAL_SEC seconds (interval in ms)
    ani = FuncAnimation(plt.gcf(), update, interval=SAMPLE_INTERVAL_SEC * 1000)
    #fig.subplots_adjust(left=0.2)
    fig.subplots_adjust(left=0.1,bottom=0.15,top=0.9)
    #plt.style.use('dark_background')
    plt.show()

#if __name__ == "__main__":
main()
