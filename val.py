import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import datetime
import getBalance as gb
import sys

# --- Command-line arguments ---
args = sys.argv
TOKEN = args[1]
#ISS = args[2]
my_a = "UNKW"

fp = 0
for ii in range(len(args)):
    if args[ii] == "-p":
        fp = 1
        my_a = args[ii + 1]

# --- Prepare figure and axes ---
fig, ax1 = plt.subplots()          # Left axis for rate
ax2 = ax1.twinx()                  # Right axis for balance

# Data lists
x_data = []
rate_data = []
bal_data = []

# Create line objects
line_rate, = ax1.plot([], [], color='tab:blue', label='Rate')
line_bal, = ax2.plot([], [], color='tab:orange', label='Balance')

# --- Animation update function ---
def animate(i):
    new_x = datetime.datetime.now()
    HORIZON_URL = "https://api.testnet.minepi.com"

    if fp:
        balnc, rate = gb.share2native(gb.HORIZON_URL, my_a, TOKEN)
        new_rate = rate
        new_bal = balnc
    else:
        new_rate = gb.getPrice(gb.HORIZON_URL, TOKEN)
        new_bal = None

    # Append data
    x_data.append(new_x)
    rate_data.append(new_rate)
    if fp:
        bal_data.append(new_bal)

    # Limit X-axis range
    if len(x_data) > 1000:
        ax1.set_xlim(x_data[-1000], x_data[-1])
    else:
        ax1.set_xlim(x_data[0], x_data[-1])

    # Update Y-axis ranges
    ax1.set_ylim(min(rate_data) * 0.95, max(rate_data) * 1.05)
    if fp and len(bal_data) > 0:
        ax2.set_ylim(min(bal_data) * 0.95, max(bal_data) * 1.05)

    # Update line data
    line_rate.set_data(x_data, rate_data)
    if fp:
        line_bal.set_data(x_data, bal_data)

    # Auto-format X-axis time labels
    plt.gcf().autofmt_xdate()

    # Debug print
    if fp:
        print(f"{TOKEN}, {new_x}, rate={new_rate:.4f}, balance={new_bal:.4f}")
    else:
        print(f"{TOKEN}, {new_x}, rate={new_rate:.4f}")

# --- Animation setup ---
#ani = FuncAnimation(fig, animate, interval=1000)
ani = FuncAnimation(fig, animate, interval=60000)

# --- Labels and titles ---
ax1.set_xlabel("Time")
ax1.set_ylabel("Rate", color='tab:blue')
ax2.set_ylabel("Balance", color='tab:orange')
aaa=f"{my_a[0]}{my_a[1]}{my_a[2]}{my_a[3]}"
plt.title(f"{TOKEN}/testPi Rate & Liquidity Pool Balance({aaa})")

# --- Legends ---
lines = [line_rate]
if fp:
    lines.append(line_bal)
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper left')

# --- Show graph ---
plt.show()

