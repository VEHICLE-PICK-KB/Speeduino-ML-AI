# %%
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


#Directory and path for csv files inside the project folder
#__file__ is for this document
#.resolve changes to abolute path.
#.parents[1] goes to the project root
#add "data/processed" to the path
DATA_DIR = Path(__file__).resolve().parents[1] / "data" / "processed"

#Application start
def main():
    #For each log, here we store useful information at first.
    #Dict format
    #Later it will be transformed to a DataFrame
    summaries = []

    # Read each log / .glob removes manual listing of files.
    for path in DATA_DIR.glob("*.csv"):
        df = pd.read_csv(path)

        # Calculate the time difference between rows to identify gaps and unwanted values (0, negative, etc.)
        # Used later for cleaning the data and for summaries. 
        dt = df["Time"].diff()
        # Drop time = 0 or NaN
        b = df["Time"].isna()
        valid_time = df["Time"][~b]

        #Add summary of each log to the list.
        summaries.append({
            "Log": path.name,
            "Rows": df.shape[0],
            "Columns": df.shape[1],
            "Duration (s)": valid_time.iloc[-1] - valid_time.iloc[0], #Negative index starts at the end of the data.
            "Missing values": df.isna().sum().sum(), #Any missing value cell.
            "Repeated time": (dt == 0).sum(), #Difference between 2 stamps is 0, meaning repeated time.
            "Backward time": (dt < 0).sum(), #Very rare, but reveals problems with the data itself or other markings / issues.
            "Gaps > 1 s": (dt > 1).sum(), #If the logger works correctly, this shouldn't get any hits.
            "Largest gap (s)": dt.max(), #See above.
            "RPM = 0 rows": (df["RPM"] == 0).sum(), # Possibly for shutdowns, but can also be signal disturbance.
            "RPM = 0 (%)": (df["RPM"] == 0).mean() * 100, #Helps to filter data and see if there are useless logs where engine is mostly not running.
        })

    if not summaries:
        raise FileNotFoundError(f"No CSV files found in {DATA_DIR}")

    # Transform to DataFrame.
    summary = pd.DataFrame(summaries)
    print(f"\nTotal logs: {len(summary)}") #Log amount
    print(f"Total rows: {summary['Rows'].sum()}") #Total rows in the current data.
    return summary

# %%
if __name__ == "__main__":
     summary = main()




# %%
#Checking logs one by one for cleanup.
#log_name = "troubleshoot.csv" #Log name here
#df = pd.read_csv(DATA_DIR / log_name)
#df.plot(x="Time", y=["RPM", "MAP", "Battery V"], subplots=True, figsize=(10, 7), title=log_name
#)
#plt.show()

# %%
log_name = "night.csv"
df = pd.read_csv(DATA_DIR / log_name)

sensors = df[["RPM", "MAP", "AFR"]] #New DataFrame with only the sensors we want to plot first.
stats = sensors.describe()
print(stats.round(2))

sensors.hist(bins=30, figsize=(10, 6))
plt.tight_layout()
plt.show()

# %%
frames = []
sensor_columns = [
    "RPM", "rpm/s", "MAP", "AFR", "TPS", "IAT",
    "PW", "Advance", "Dwell", "Battery V", "Boost PSI"
]
for path in sorted(DATA_DIR.glob("*.csv")):
    df = pd.read_csv(path)
    frames.append(df[sensor_columns])

all_sensors = pd.concat(frames, ignore_index=True)

all_stats = all_sensors.describe()
print(all_stats.round(2))

all_sensors.hist(bins=30, figsize=(12, 12), layout=(4, 3))
plt.tight_layout()
plt.show() #histograms for better data visualization

# %%
print(all_sensors["Boost PSI"].max()) #Inspecting unnatural max boost value.
# %%

# %%
for path in sorted(DATA_DIR.glob("*.csv")):
    df = pd.read_csv(path)
    b = df["MAP"] > 180
  #Locating the max boost values
    if b.any():
        print(f"\nLog: {path.name}")
        print(df.loc[b, ["Time", "RPM", "MAP", "Boost PSI", "TPS"]])

# %%
inspection_frames = []
#Inspection of all max values of the possible final features to check for any unnatural occurences that should be cleaned.
for path in sorted(DATA_DIR.glob("*.csv")):
    df = pd.read_csv(path)

    selected = df[["Time"] + sensor_columns].copy()
    selected["source_log"] = path.name
    inspection_frames.append(selected)

inspection = pd.concat(inspection_frames, ignore_index=True)

for sensor in sensor_columns:
    columns = ["source_log", "Time", sensor, "RPM", "MAP"] # RPM and map value is added to have more perspective of the min and max values.
    columns = list(dict.fromkeys(columns))

    print(f"\nLargest values: {sensor}")
    print(inspection.nlargest(5, sensor)[columns].to_string(index=False))

    print(f"\nSmallest values: {sensor}")
    print(inspection.nsmallest(5, sensor)[columns].to_string(index=False))



# %%
#For locating rpm = 0 rows, to be removed because of inaccurate measurement.
#Second run after the csv files have been cleaned, to make sure that no rpm 0 lines are left.
for path in sorted(DATA_DIR.glob("*.csv")):
    df = pd.read_csv(path)

    b = df["RPM"] == 0
    zero_count = b.sum()
    zero_percent = 100 * zero_count / len(df)

    print(f"\nLog: {path.name}")
    print(f"Rows: {len(df)}")
    print(f"RPM = 0: {zero_count} ({zero_percent:.2f} %)")

# %%
#For removing repeating time stamps
#value will be an average of the two.
for path in sorted(DATA_DIR.glob("*.csv")):
    df = pd.read_csv(path)

    b = df.duplicated(subset=["segment_id", "Time"])
    duplicate_count = b.sum()

    print(f"\nLog: {path.name}")
    print(f"Extra rows with the same timestamp: {duplicate_count}")

# %%
for path in sorted(DATA_DIR.glob("*.csv")):
    df = pd.read_csv(path)

    b = df["RPM"] < 600

    print(f"\nLog: {path.name}")
    print(f"RPM below 700: {b.sum()}")
    print(df.loc[b, ["Time", "RPM", "MAP", "Battery V"]].head(10))

# %%
for path in sorted(DATA_DIR.glob("*.csv")):
    df = pd.read_csv(path)
    print(f"{path.name}: min RPM = {df['RPM'].min()}")

# %%
for path in sorted(DATA_DIR.glob("*.csv")):
    df = pd.read_csv(path)

    dt = df.groupby("segment_id")["Time"].diff()

    print(f"\nLog: {path.name}")
    print(dt.describe().round(3))

# %%
df = pd.read_csv(
    r"C:\Users\matia\Desktop\UWASA\Applied Machine Learning\Speeduino_ML_AI\data\csv\05092026wires.csv"
)
print([column for column in df.columns if "rpm" in column.lower()])



# %%
df = pd.read_csv(DATA_DIR / "misfire_driving 2.csv")

b = (df["Time"] >= 18.3) & (df["Time"] <= 19.1)

print(
    df.loc[b, ["Time", "RPM", "rpm/s", "MAP", "TPS"]]
    .to_string(index=False)
)


# %%
df = pd.read_csv(DATA_DIR / "misfire_driving 2.csv")

groups = df.groupby("segment_id")
dt = groups["Time"].diff()
rpm_change = groups["RPM"].diff()

df["rpm_rate"] = rpm_change / dt

b = (df["Time"] >= 18.3) & (df["Time"] <= 19.1)

print(
    df.loc[b, ["Time", "RPM", "rpm/s", "rpm_rate"]]
    .round(2)
    .to_string(index=False)
)

# %%
df = pd.read_csv(DATA_DIR / "misfire_driving 2.csv")

b = (df["Time"] >= 18.3) & (df["Time"] <= 19.1)

print(
    df.loc[b, ["Time", "RPM", "rpm_rate"]]
    .to_string(index=False)
)

# %%
for path in sorted(DATA_DIR.glob("*.csv")):
    df = pd.read_csv(path)

    missing = df["rpm_rate"].isna().sum()
    segments = df["segment_id"].nunique()

    print(f"{path.name}: missing={missing}, segments={segments}")

# %%
#Starting to check how the different driving conditions are distributed across the cleaned data.
#This section is for planning how to divide different datasets for the model.
rows = []

for path in sorted(DATA_DIR.glob("*.csv")):
    df = pd.read_csv(path)

    rows.append({
        "log": path.name,
        "rows": len(df),
        "max_RPM": df["RPM"].max(),
        "max_MAP": df["MAP"].max(),
        "max_TPS": df["TPS"].max(),
        "TPS_80plus": (df["TPS"] >= 80).sum()
    })

print(pd.DataFrame(rows).to_string(index=False))


# %%
#Analyzing night.csv, since it is the only real log that contains more diverse driving data.
df = pd.read_csv(DATA_DIR / "night.csv")

for segment_id, segment in df.groupby("segment_id"):
    segment.plot(
        x="Time",
        y=["RPM", "MAP", "TPS"],
        subplots=True,
        figsize=(12, 8),
        title=f"night.csv — segment {segment_id}"
    )

    plt.tight_layout()
    plt.show()
# %%
#this block is for checking the data from the marked sections to see that the cropping was correct.
pull_windows = pd.read_csv(DATA_DIR.parent / "pull_windows.csv")
df = pd.read_csv(DATA_DIR / "night.csv")

for _, window in pull_windows.iterrows():
    b = (
        (df["segment_id"] == window["segment_id"])
        & (df["Time"] >= window["start_s"])
        & (df["Time"] <= window["end_s"])
    )
    pull = df[b]

    print(
        f"{window['event_id']}: rows={len(pull)}, "
        f"max RPM={pull['RPM'].max()}, "
        f"max MAP={pull['MAP'].max()}, "
        f"max TPS={pull['TPS'].max()}"
    )

# %%
#Pull event categorization test
pull_windows = pd.read_csv(DATA_DIR.parent / "pull_windows.csv")

print(pull_windows[["event_id", "split"]].to_string(index=False))
