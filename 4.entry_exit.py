import pandas as pd
import numpy as np

# Load file
file_path = "cross_test2_pivoted.xlsx"
df = pd.read_excel(file_path)

# Clean column names
df.columns = df.columns.str.strip()

# Sort properly (VERY IMPORTANT)
df = df.sort_values(by=["Track ID", "Time [s]"]).copy()

# =========================================================
# METHOD 1: Distance / Travel Time (unchanged)
# =========================================================

df_unique = df.drop_duplicates(subset=["Track ID"]).copy()

df_unique["travel_time_s"] = df_unique["Exit Time [s]"] - df_unique["Entry Time [s]"]
df_unique = df_unique[df_unique["travel_time_s"] > 0]

df_unique["SMS_Method1_kmh"] = (
    df_unique["Traveled Dist. [m]"] / df_unique["travel_time_s"]
) * 3.6

sms_method1 = len(df_unique) / np.sum(1 / df_unique["SMS_Method1_kmh"])


# =========================================================
# METHOD 2: CORRECT (distance-weighted from time-series)
# =========================================================

# Time difference per vehicle
df["dt"] = df.groupby("Track ID")["Time [s]"].diff()

# Remove first NaN rows
df = df[df["dt"].notna()]

# Remove invalid dt
df = df[df["dt"] > 0]

# Convert speed to m/s
df["speed_mps"] = df["Speed [km/h]"] / 3.6

# Step distance
df["step_distance"] = df["speed_mps"] * df["dt"]

# --- Per vehicle SMS (correct) ---
per_vehicle = df.groupby("Track ID").agg(
    total_distance=("step_distance", "sum"),
    total_time=("dt", "sum")
).reset_index()

per_vehicle["SMS_Method2_kmh"] = (
    per_vehicle["total_distance"] / per_vehicle["total_time"]
) * 3.6

# --- Overall SMS (correct) ---
total_distance_all = per_vehicle["total_distance"].sum()
total_time_all = per_vehicle["total_time"].sum()

sms_method2 = (total_distance_all / total_time_all) * 3.6


# =========================================================
# MERGE PER VEHICLE RESULTS
# =========================================================

method1_per_vehicle = df_unique[["Track ID", "SMS_Method1_kmh"]]

per_vehicle_results = pd.merge(
    method1_per_vehicle,
    per_vehicle[["Track ID", "SMS_Method2_kmh"]],
    on="Track ID",
    how="outer"
)


# =========================================================
# OVERALL RESULTS
# =========================================================

overall_results = pd.DataFrame({
    "Method": ["Method 1", "Method 2 (Corrected)"],
    "Space Mean Speed (km/h)": [sms_method1, sms_method2]
})


# =========================================================
# SAVE TO EXCEL
# =========================================================

output_file = "space_mean_speed_results_corrected.xlsx"

with pd.ExcelWriter(output_file) as writer:
    overall_results.to_excel(writer, sheet_name="Overall Results", index=False)
    per_vehicle_results.to_excel(writer, sheet_name="Per Vehicle Results", index=False)

print(f"Corrected results saved to {output_file}")