from pathlib import Path
import pandas as pd
import matplotlib.pylab as plt

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data" / "csv"

windows = pd.read_csv(PROJECT_DIR / "data" / "keep_windows.csv")

sensor_columns = [
    "RPM", "rpm/s", "MAP", "AFR", "TPS", "IAT",
    "PW", "Advance", "Dwell", "Battery V", "Boost PSI"
]

for log_name, log_windows in windows.groupby("log", sort=False):
    df = pd.read_csv(DATA_DIR / log_name)

    b = pd.Series(False, index=df.index)
    for _, window in log_windows.iterrows():
        b = b | (
            (df["Time"] >= window["start_s"])
            & (df["Time"] <= window["end_s"])
        )

    cleaned = df[b].copy()
    b_running = cleaned["RPM"] > 600
    cleaned = cleaned[b_running].copy()

    #Segment the data based on time gaps more than 1 second
    dt = cleaned["Time"].diff()
    cleaned["segment_id"] = (dt > 1).cumsum()

    cleaned = (
        cleaned.groupby(["segment_id", "Time"], as_index=False)[sensor_columns]
        .mean()
    )

    groups = cleaned.groupby("segment_id")

    dt = groups["Time"].diff()
    rpm_change = groups["RPM"].diff()

    cleaned["rpm_rate"] = rpm_change / dt



    cleaned.to_csv(
        PROJECT_DIR / "data" / "processed" / log_name,
            index=False
        )
    print(f"Log: {log_name}")
    print(f"Rows before: {len(df)}")
    print(f"Rows after: {len(cleaned)}")
    print(f"Start(s): {cleaned['Time'].iloc[0]}")
    print(f"End(s): {cleaned['Time'].iloc[-1]}")
    print(cleaned.groupby("segment_id")["Time"].agg(["min", "max", "count"])) #First and last timestamp of each segment and number of rows in each segment.


cleaned.plot(
    x="Time",
    y=["RPM", "MAP", "Battery V"],
    subplots=True,
    figsize=(10, 7),
    title=log_name
)
plt.show()
