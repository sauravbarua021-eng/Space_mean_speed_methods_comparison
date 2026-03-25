import pandas as pd

# ---- STEP 1: Load CSV safely ----
file_path = "cross_test2.csv"

df = pd.read_csv(file_path, low_memory=False)

# Clean column names (remove spaces, quotes)
df.columns = df.columns.str.strip().str.replace('"', '')

print("Columns detected:\n", df.columns.tolist())

# ---- STEP 2: Identify base columns automatically ----
# Assume first 8 columns are fixed (based on your structure)
base_cols = df.columns[:8]
traj_cols = df.columns[8:]

print("\nBase columns:\n", base_cols)
print("\nTrajectory columns count:", len(traj_cols))

# ---- STEP 3: Pivot repeated 6-column trajectory blocks ----
block_size = 6
trajectory_data = []

for idx, row in df.iterrows():
    base_info = row[base_cols].to_dict()
    
    for i in range(0, len(traj_cols), block_size):
        block = traj_cols[i:i+block_size]
        
        if len(block) < block_size:
            continue
        
        values = row[block].values
        
        # Skip empty blocks
        if pd.isnull(values).all():
            continue
        
        record = base_info.copy()
        
        record.update({
            "x [m]": values[0],
            "y [m]": values[1],
            "Speed [km/h]": values[2],
            "Tan. Acc. [m/s2]": values[3],
            "Lat. Acc. [m/s2]": values[4],
            "Time [s]": values[5]
        })
        
        trajectory_data.append(record)

# ---- STEP 4: Create dataframe ----
df_long = pd.DataFrame(trajectory_data)

# ---- STEP 5: Sort ----
if "Track ID" in df_long.columns and "Time [s]" in df_long.columns:
    df_long = df_long.sort_values(by=["Track ID", "Time [s]"])

# ---- STEP 6: Save ----
output_file = "cross_test2_pivoted.xlsx"
df_long.to_excel(output_file, index=False)

print(f"\n✅ Done! File saved as: {output_file}")