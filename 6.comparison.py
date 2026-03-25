import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Load data
# =========================

# Method 1 & 2
file_m12 = "space_mean_speed_results_corrected.xlsx"
df_m12 = pd.read_excel(file_m12, sheet_name="Overall Results")

method1_speed = df_m12.loc[df_m12["Method"] == "Method 1", "Space Mean Speed (km/h)"].values[0]
method2_speed = df_m12.loc[df_m12["Method"].str.contains("Method 2"), "Space Mean Speed (km/h)"].values[0]

# Method 3
file_m3 = "edie_method_all_intervals.xlsx"
df_m3 = pd.read_excel(file_m3, sheet_name="summary")

# =========================
# Plot
# =========================

plt.figure(figsize=(11, 6))

# Colors
color_m1 = 'red'
color_m2 = 'blue'
color_m3 = 'green'

# --- Method 3: Bar Plot ---
bars = plt.bar(df_m3["interval_s"],
               df_m3["space_mean_speed_kmh"],
               width=3,
               color=color_m3,
               alpha=0.6,
               label="Method 3: Trajectory based aggregation of Edie's Space Mean Speed")

# --- Rotated vertical labels for Method 3 ---
for bar in bars:
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2,
             height + 0.05,
             f"{height:.2f}",
             ha='center',
             va='bottom',
             rotation=90,
             fontsize=9)

# --- Method 1 line ---
plt.axhline(y=method1_speed,
            color=color_m1,
            linestyle='--',
            linewidth=2,
            label="Method 1: Entry-Exit travel time based Space Mean Speed")

# --- Method 2 line ---
plt.axhline(y=method2_speed,
            color=color_m2,
            linestyle=':',
            linewidth=2,
            label="Method 2: Instantaneous speed based Space Mean Speed")

# =========================
# Line labels (no overlap)
# =========================

x_pos = df_m3["interval_s"].max() + 3

plt.text(x_pos,
         method1_speed + 0.25,
         f"{method1_speed:.2f}",
         color=color_m1,
         va='center',
         fontsize=10,
         fontweight='bold')

plt.text(x_pos,
         method2_speed - 0.25,
         f"{method2_speed:.2f}",
         color=color_m2,
         va='center',
         fontsize=10,
         fontweight='bold')

# =========================
# Labels & Title
# =========================

plt.xlabel("Time Interval (s)", fontsize=12)
plt.ylabel("Space Mean Speed (km/h)", fontsize=12)
plt.title("Comparison of Space Mean Speed Estimation Methods", fontsize=14)

plt.legend()
plt.grid(True, linestyle='--', alpha=0.5)

plt.xlim(0, df_m3["interval_s"].max() + 12)

plt.tight_layout()
plt.show()