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
