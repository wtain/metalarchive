from datetime import datetime

import pandas as pd
import glob
import os

from storage_client.posts import save_posts_from_df
from storage_client.subscribers import save_subscribers_from_df


def load_snapshots(folder, mask):
    """
    Load all CSV files in a folder matching a mask into one DataFrame.
    Adds a 'snapshot' column with timestamp extracted from filename.
    """
    files = sorted(glob.glob(os.path.join(folder, mask)))
    dfs = []

    for file in files:
        # Extract timestamp part from filename (e.g., after last '_')
        base = os.path.basename(file)
        snapshot = os.path.splitext(base)[0].split("_")[-1]

        df = pd.read_csv(file)
        df["snapshot"] = snapshot
        dfs.append(df)

    if dfs:
        return pd.concat(dfs, ignore_index=True)
    else:
        return pd.DataFrame()  # empty if no matches


def load_snapshots_timeseries(folder, mask, time_format="%Y%m%d_%H%M%S"):
    """
    Load CSV snapshots into a dict keyed by timestamp.
    Returns:
        snapshots: dict[timestamp -> DataFrame]
        combined: DataFrame with MultiIndex (timestamp, row index)
    """
    files = sorted(glob.glob(os.path.join(folder, mask)))
    snapshots = {}

    for file in files:
        base = os.path.basename(file)
        timestamp_str = "_".join(base.split("_")[1:])  # e.g. subscribers_20250914_120000.csv → 20250914_120000
        timestamp_str = os.path.splitext(timestamp_str)[0]
        timestamp = datetime.strptime(timestamp_str, time_format)

        df = pd.read_csv(file)
        snapshots[timestamp] = df

    # Build combined DataFrame (stack snapshots with timestamp index)
    combined = pd.concat(
        {ts: df for ts, df in snapshots.items()},
        names=["timestamp", "row"]
    )

    return snapshots, combined

# Example usage:
subscribers_df = load_snapshots("results/subscribers", "subscribers_*.csv")
posts_df = load_snapshots("results/posts", "posts_*.csv")

print(subscribers_df.head())
print(posts_df.head())


# Load subscribers snapshots
subs_snapshots, subs_combined = load_snapshots_timeseries("results/subscribers", "subscribers_*.csv")

# Load posts snapshots
posts_snapshots, posts_combined = load_snapshots_timeseries("results/posts", "posts_*.csv")

print("📌 Individual snapshot access:")
print(subs_snapshots.keys())  # dict of timestamps
print(subs_snapshots[list(subs_snapshots.keys())[0]].head())  # first snapshot DF

print("\n📌 Combined multi-index dataframe:")
print(subs_combined.head())

save_posts_from_df(posts_combined)
save_subscribers_from_df(subs_combined)
