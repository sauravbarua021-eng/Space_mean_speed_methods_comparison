import pandas as pd
import numpy as np

# ==============================
# Load data
# ==============================
file_path = "trajectory_1s_final.xlsx"
df = pd.read_excel(file_path)

# Clean columns
df.columns = df.columns.str.strip()

# Sort properly
df = df.sort_values(by=["Track ID", "Time [s]"]).copy()

# ==============================
# Define road segment
# ==============================
x_min = df["cumulative_distance"].min()
x_max = df["cumulative_distance"].max()
road_length = x_max - x_min

print(f"Road Length (m): {road_length:.2f}")

# ==============================
# Detect ENTRY events
# ==============================
df["prev_pos"] = df.groupby("Track ID")["cumulative_distance"].shift(1)

# Entry condition
df["is_entry"] = (
    (df["prev_pos"] < x_min) &
    (df["cumulative_distance"] >= x_min)
)

# First appearance (important for vehicles starting inside)
first_obs = df.groupby("Track ID").head(1).copy()
first_obs["is_entry"] = first_obs["cumulative_distance"] >= x_min

# Combine
df.loc[first_obs.index, "is_entry"] = first_obs["is_entry"]

# ==============================
# Aggregation intervals
# ==============================
intervals = [1, 2, 5, 10, 20, 30, 40, 60]

all_results = {}

# ==============================
# Loop over intervals
# ==============================
for interval in intervals:
    
    df["time_bin"] = (df["Time [s]"] // interval) * interval
    
    grouped = df.groupby("time_bin")
    
    results = []
    
    for t, group in grouped:
        
        T = interval
        
        # ENTRY COUNT (Flow)
        entry_count = group["is_entry"].sum()
        flow = entry_count / T  # veh/s
        
        # DENSITY (vehicles present)
        N_present = group["Track ID"].nunique()
        density = N_present / road_length  # veh/m
        
        # Avoid division by zero
        if density == 0:
            speed_kmh = np.nan
        else:
            speed_mps = flow / density
            speed_kmh = speed_mps * 3.6
        
        results.append({
            "time_bin": t,
            "entry_count": entry_count,
            "vehicles_present": N_present,
            "flow_veh_per_s": flow,
            "density_veh_per_m": density,
            "space_mean_speed_kmh": speed_kmh
        })
    
    result_df = pd.DataFrame(results)
    all_results[f"{interval}s"] = result_df

# ==============================
# Summary
# ==============================
summary = []

for key, df_res in all_results.items():
    
    df_valid = df_res.dropna()
    
    if len(df_valid) == 0:
        continue
    
    summary.append({
        "interval": key,
        "avg_flow_veh_per_s": df_valid["flow_veh_per_s"].mean(),
        "avg_density_veh_per_m": df_valid["density_veh_per_m"].mean(),
        "avg_space_mean_speed_kmh": df_valid["space_mean_speed_kmh"].mean()
    })

summary_df = pd.DataFrame(summary)

# ==============================
# Save to Excel
# ==============================
output_file = "classical_entry_based_sms.xlsx"

with pd.ExcelWriter(output_file, engine="openpyxl") as writer:
    
    for name, df_res in all_results.items():
        df_res.to_excel(writer, sheet_name=name, index=False)
    
    summary_df.to_excel(writer, sheet_name="Summary", index=False)

print(f"Results saved to {output_file}")