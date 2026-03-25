import pandas as pd
import numpy as np

# ==============================
# Load data
# ==============================
file_path = "trajectory_1s_final.xlsx"
df = pd.read_excel(file_path)

# Sort data
df = df.sort_values(by=["Track ID", "Time [s]"])

# ==============================
# Parameters
# ==============================
intervals = [1, 2, 5, 10, 20, 30, 40, 60]

# Fixed road length (IMPORTANT)
road_length = df["cumulative_distance"].max() - df["cumulative_distance"].min()

summary_results = []

# ==============================
# Excel writer
# ==============================
output_file = "edie_method_all_intervals.xlsx"
writer = pd.ExcelWriter(output_file, engine="openpyxl")

# ==============================
# Process each interval
# ==============================
for interval in intervals:

    df_copy = df.copy()

    # Create time bins
    df_copy["time_bin"] = (df_copy["Time [s]"] // interval) * interval

    # ==============================
    # Aggregate Edie components
    # ==============================
    agg = df_copy.groupby("time_bin").agg(
        total_distance=("step_distance", "sum"),   # Σ d_i
        total_time=("step_distance", "count")      # Σ t_i (1 row = 1 sec)
    ).reset_index()

    # Convert time to seconds
    agg["total_time_sec"] = agg["total_time"]  # since 1 row = 1 second

    # ==============================
    # Edie definitions
    # ==============================
    # Flow (veh/s)
    agg["flow"] = agg["total_distance"] / (road_length * interval)

    # Density (veh/m)
    agg["density"] = agg["total_time_sec"] / (road_length * interval)

    # Speed (m/s)
    agg["speed_mps"] = agg["total_distance"] / agg["total_time_sec"]

    # Convert speed
    agg["speed_kmh"] = agg["speed_mps"] * 3.6

    # Clean
    agg.replace([np.inf, -np.inf], np.nan, inplace=True)

    # ==============================
    # Summary
    # ==============================
    summary = {
        "interval_s": interval,
        "avg_flow_veh_per_s": agg["flow"].mean(),
        "avg_density_veh_per_m": agg["density"].mean(),
        "avg_speed_kmh": agg["speed_kmh"].mean(),
        "space_mean_speed_kmh": agg["speed_kmh"].mean()  # already correct in Edie
    }

    summary_results.append(summary)

    # Save sheet
    agg.to_excel(writer, sheet_name=f"{interval}s", index=False)

# ==============================
# Summary sheet
# ==============================
summary_df = pd.DataFrame(summary_results)
summary_df.to_excel(writer, sheet_name="summary", index=False)

writer.close()

print(f"Edie method results saved in: {output_file}")