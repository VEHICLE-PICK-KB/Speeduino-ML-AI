from pathlib import Path
import pandas as pd
import matplotlib.pylab as plt

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data" / "csv"

windows = pd.read_csv(PROJECT_DIR / "data" / "keep_windows.csv")

for log_name, log_windows in windows.groupby("log", sort=False):
    df = pd.read_csv(DATA_DIR / log_name)

    b = pd.Series(False, index=df.index)
    for _, window in log_windows.iterrows():
        b = b | (
            (df["Time"] >= window["start_s"])
            & (df["Time"] <= window["end_s"])
        )

    cleaned = df[b].copy()
    cleaned.to_csv(
        PROJECT_DIR / "data" / "processed" / log_name,
            index=False
        )
    print(f"Log: {log_name}")
    print(f"Rows before: {len(df)}")
    print(f"Rows after: {len(cleaned)}")
    print(f"Start(s): {cleaned['Time'].iloc[0]}")
    print(f"End(s): {cleaned['Time'].iloc[-1]}")


cleaned.plot(
    x="Time",
    y=["RPM", "MAP", "Battery V"],
    subplots=True,
    figsize=(10, 7),
    title=log_name
)
plt.show()
