from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

def stretch_pull(base_pull, time_scale):
    variant = base_pull.copy()

    elapsed = variant["Time"] - variant["Time"].iloc[0]
    variant["Time"] = elapsed * time_scale

    groups = variant.groupby("segment_id")
    variant["rpm_rate"] = (
        groups["RPM"].diff() / groups["Time"].diff()
    )

    variant["time_scale"] = time_scale

    return variant

PROJECT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_DIR / "data"

pull_windows = pd.read_csv(DATA_DIR / "pull_windows.csv")
development = pull_windows[pull_windows["split"] == "development"]

print(development[["event_id", "start_s", "end_s"]])

for _, window in development.iterrows():

    df = pd.read_csv(DATA_DIR / "processed" / window["log"])

    b = (
        (df["segment_id"] == window["segment_id"])
        & (df["Time"] >= window["start_s"])
        & (df["Time"] <= window["end_s"])
    )

    base_pull = df[b].copy()

    print(f"Base: {window['event_id']}")
    print(f"Rows: {len(base_pull)}")
    print(base_pull[["Time", "RPM", "MAP", "TPS"]].head())

    for time_scale in [0.80, 0.90, 1.05, 1.10, 1.15 ]:
        variant = stretch_pull(base_pull, time_scale)

        variant_id = (
            f"{window['event_id']}_stretch_{time_scale:.2f}"
        )

        variant["source_log"] = window["log"]
        variant["source_event"] = window["event_id"]
        variant["split"] = window["split"]
        variant["variant_id"] = variant_id

        output_path = (
            DATA_DIR / "synthetic" / f"{variant_id}.csv"
        )

        variant.to_csv(output_path, index=False)
        print(f"Saved: {output_path}")

elapsed = base_pull["Time"] - base_pull["Time"].iloc[0]

#Display
fig, axes = plt.subplots(3, 1, figsize=(12, 8), sharex=True)#sharex=similar time scale for all the graphs, so they are comparable

for ax, sensor in zip(axes, ["RPM", "MAP", "TPS"]):
    ax.plot(elapsed, base_pull[sensor], label="Original")
    ax.plot(variant["Time"], variant[sensor], label="Stretched")

    ax.set_ylabel(sensor)
    ax.legend()
    ax.grid(True)

axes[-1].set_xlabel("Elapsed time (s)")
plt.tight_layout()
plt.show()

