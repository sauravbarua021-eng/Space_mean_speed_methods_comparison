import pandas as pd
import matplotlib.pyplot as plt

# =========================
# Load data
# =========================

# Method 1 & 2
file_m12 = "space_mean_speed_results_corrected.xlsx"
df_m12 = pd.read_excel(file_m12, sheet_name="Overall Results")

method1_speed = df_m12.loc[
    df_m12["Method"] == "Method 1",
    "Space Mean Speed (km/h)"
].values[0]

method2_speed = df_m12.loc[
    df_m12["Method"].str.contains("Method 2"),
    "Space Mean Speed (km/h)"
].values[0]

# Method 3 (Entry-based aggregation)
file_m3 = "classical_entry_based_sms.xlsx"
df_m3 = pd.read_excel(file_m3, sheet_name="Summary")

# =========================
# Clean interval column (remove 's')
# =========================

df_m3["interval_s"] = df_m3["interval"].astype(str).str.replace("s", "").astype(float)

# =========================
# Plot
# =========================

plt.figure(figsize=(11, 6))

# Colors
color_m1 = 'red'
color_m2 = 'blue'
color_m3 = 'purple'

# --- Method 3: Bar Plot ---
bars = plt.bar(
    df_m3["interval_s"],
    df_m3["avg_space_mean_speed_kmh"],
    width=2.5,
    color=color_m3,
    alpha=0.65,
    label="Method 4: Entry-based count aggregation"
)

# --- Vertical labels ---
for bar in bars:
    height = bar.get_height()
    plt.text(
        bar.get_x() + bar.get_width()/2,
        height + 0.1,
        f"{height:.2f}",
        ha='center',
        va='bottom',
        rotation=90,
        fontsize=9
    )

# --- Method 1 ---
plt.axhline(
    y=method1_speed,
    color=color_m1,
    linestyle='--',
    linewidth=2,
    label="Method 1: Travel-time based SMS"
)

# --- Method 2 ---
plt.axhline(
    y=method2_speed,
    color=color_m2,
    linestyle=':',
    linewidth=2,
    label="Method 2: Instantaneous speed-based SMS"
)

# =========================
# Line value annotations
# =========================

x_pos = df_m3["interval_s"].max() + 3

plt.text(
    x_pos,
    method1_speed + 0.2,
    f"{method1_speed:.2f}",
    color=color_m1,
    fontsize=10,
    fontweight='bold'
)

plt.text(
    x_pos,
    method2_speed - 0.2,
    f"{method2_speed:.2f}",
    color=color_m2,
    fontsize=10,
    fontweight='bold'
)

# =========================
# Labels & Title
# =========================

plt.xlabel("Aggregation Interval (s)", fontsize=12)
plt.ylabel("Space Mean Speed (km/h)", fontsize=12)

plt.title(
    "Impact of Aggregation Interval on Space Mean Speed Estimation",
    fontsize=14,
    fontweight='bold'
)

plt.grid(True, linestyle='--', alpha=0.5)
plt.legend()

plt.xlim(0, df_m3["interval_s"].max() + 10)

plt.tight_layout()
plt.show()