
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
from scipy import stats

pd.set_option("display.max_columns", 100)
pd.set_option("display.width", 120)

# %%
START_DATE = "2010-01-01"
END_DATE = None

SPY_TICKER = "SPY"
VIX_TICKER = "^VIX"

# %%
# %%
spy = yf.download(SPY_TICKER, start=START_DATE, end=END_DATE, auto_adjust=True)
vix = yf.download(VIX_TICKER, start=START_DATE, end=END_DATE, auto_adjust=True)
# Fix multi-index columns from yfinance
spy.columns = spy.columns.get_level_values(0)
vix.columns = vix.columns.get_level_values(0)
spy = spy[["Close"]].rename(columns={"Close": "spy_close"})
vix = vix[["Close"]].rename(columns={"Close": "vix_close"})

df = spy.join(vix, how="inner").dropna()
df.head()



df["spy_ret_1d"] = df["spy_close"].pct_change()
df["vix_ret_1d"] = df["vix_close"].pct_change()
df["vix_change"] = df["vix_close"].diff()

# forward returns
for horizon in [1, 5, 20]:
    df[f"spy_fwd_ret_{horizon}d"] = df["spy_close"].shift(-horizon) / df["spy_close"] - 1

# future realized vol using daily returns
for horizon in [5, 20]:
    df[f"realized_vol_{horizon}d"] = (
        df["spy_ret_1d"].rolling(horizon).std().shift(-horizon + 1) * np.sqrt(252)
    )

df = df.dropna().copy()
df = df.reset_index()
df.columns.name = None
df.head()
#df['vix_close']

def classify_vix_regime(vix):
    if vix < 15.0:
        return "Low Vol"
    elif vix < 20.0:
        return "Normal Vol"
    elif vix < 30.0:
        return "Elevated Vol"
    else:
        return "Stress Vol"

df["vix_regime"] = df["vix_close"].apply(classify_vix_regime)

df["vix_regime"].value_counts()


regime_summary = (
    df.groupby("vix_regime")[["spy_fwd_ret_1d", "spy_fwd_ret_5d", "spy_fwd_ret_20d"]]
      .mean()
      .sort_index()
)

regime_summary

hit_rate_summary = (
    df.groupby("vix_regime")[["spy_fwd_ret_1d", "spy_fwd_ret_5d", "spy_fwd_ret_20d"]]
      .apply(lambda x: (x > 0).mean())
)

hit_rate_summary
spike_threshold = df["vix_ret_1d"].quantile(0.95)
df["vix_spike"] = df["vix_ret_1d"] >= spike_threshold

df["vix_spike"].value_counts()
print("Spike threshold:", spike_threshold)


spike_summary = df.groupby("vix_spike")[["spy_fwd_ret_1d", "spy_fwd_ret_5d", "spy_fwd_ret_20d"]].mean()
spike_summary.index = ["Non-Spike Days", "Spike Days"]
spike_summary


vol_summary = (
    df.groupby("vix_regime")[["realized_vol_5d", "realized_vol_20d"]]
      .mean()
      .sort_index()
)

vol_summary


spike_days = df.loc[df["vix_spike"], "spy_fwd_ret_5d"]
non_spike_days = df.loc[~df["vix_spike"], "spy_fwd_ret_5d"]

t_stat, p_value = stats.ttest_ind(spike_days, non_spike_days, equal_var=False, nan_policy="omit")

print("5D forward return after VIX spike vs non-spike")
print("t-stat:", round(t_stat, 4))
print("p-value:", round(p_value, 4))


fig, ax1 = plt.subplots(figsize=(12, 6))

ax1.plot(df.index, df["spy_close"], label="SPY")
ax1.set_ylabel("SPY")

ax2 = ax1.twinx()
ax2.plot(df.index, df["vix_close"], label="VIX")
ax2.set_ylabel("VIX")

plt.title("SPY and VIX Over Time")
plt.show()


regime_summary.plot(kind="bar", figsize=(10, 6))
plt.title("Average SPY Forward Returns by VIX Regime")
plt.ylabel("Average Return")
plt.xticks(rotation=0)
plt.axhline(0, linewidth=1)
plt.show()


vol_summary.plot(kind="bar", figsize=(10, 6))
plt.title("Future Realized Volatility by Starting VIX Regime")
plt.ylabel("Annualized Volatility")
plt.xticks(rotation=0)
plt.show()


spike_summary.plot(kind="bar", figsize=(10, 6))
plt.title("SPY Forward Returns After VIX Spike vs Non-Spike Days")
plt.ylabel("Average Return")
plt.xticks(rotation=0)
plt.axhline(0, linewidth=1)
plt.show()


plt.figure(figsize=(10, 6))
plt.scatter(df["vix_close"], df["spy_fwd_ret_5d"], alpha=0.4)
plt.title("VIX Level vs Next 5-Day SPY Return")
plt.xlabel("VIX Level")
plt.ylabel("Next 5-Day SPY Return")
plt.axhline(0, linewidth=1)
plt.show()


print("\n=== Average Forward Returns by VIX Regime ===")
display(regime_summary)

print("\n=== Hit Rate by VIX Regime ===")
display(hit_rate_summary)

print("\n=== Future Realized Volatility by VIX Regime ===")
display(vol_summary)

print("\n=== Returns After VIX Spike vs Non-Spike Days ===")
display(spike_summary)


regime_stats = (
    df.groupby("vix_regime")[["spy_fwd_ret_5d", "spy_fwd_ret_20d"]]
    .agg(["mean", "std"])
)

# compute Sharpe
regime_stats[("spy_fwd_ret_5d", "sharpe")] = (
    regime_stats[("spy_fwd_ret_5d", "mean")] /
    regime_stats[("spy_fwd_ret_5d", "std")]
)

regime_stats[("spy_fwd_ret_20d", "sharpe")] = (
    regime_stats[("spy_fwd_ret_20d", "mean")] /
    regime_stats[("spy_fwd_ret_20d", "std")]
)

regime_stats


import os

# create folder
os.makedirs("figures", exist_ok=True)

# 1. SPY vs VIX
fig, ax1 = plt.subplots(figsize=(12,6))
ax1.plot(df.index, df["spy_close"], label="SPY")
ax2 = ax1.twinx()
ax2.plot(df.index, df["vix_close"], label="VIX")

plt.title("SPY and VIX Over Time")
plt.savefig("figures/spy_vix_over_time.png", dpi=300, bbox_inches="tight")
plt.close()

# 2. Forward returns by regime
regime_summary.plot(kind="bar", figsize=(10,6))
plt.title("Average SPY Forward Returns by VIX Regime")
plt.savefig("figures/avg_forward_returns_by_regime.png", dpi=300, bbox_inches="tight")
plt.close()


# 3. Realized vol
realized_vol_summary = (
    df.groupby("vix_regime")[["realized_vol_5d", "realized_vol_20d"]]
    .mean()
    .sort_index()
)

realized_vol_summary.plot(kind="bar", figsize=(10,6))
plt.title("Future Realized Volatility by Regime")
plt.savefig("figures/future_realized_vol_by_regime.png", dpi=300, bbox_inches="tight")
plt.close()

# 4. Spike vs non-spike
spike_summary.plot(kind="bar", figsize=(10,6))
plt.title("SPY Returns After VIX Spike vs Non-Spike")
plt.savefig("figures/returns_after_vix_spike.png", dpi=300, bbox_inches="tight")
plt.close()

# 5. Scatter
plt.figure(figsize=(8,6))
plt.scatter(df["vix_close"], df["spy_fwd_ret_5d"], alpha=0.4)
plt.axhline(0)
plt.xlabel("VIX Level")
plt.ylabel("Next 5-Day SPY Return")
plt.title("VIX vs Next 5-Day Return")
plt.savefig("figures/vix_vs_next_5d_return.png", dpi=300, bbox_inches="tight")
plt.close()





