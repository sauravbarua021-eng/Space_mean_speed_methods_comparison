import pandas as pd
import matplotlib.pyplot as plt

# Load the Excel file
file_path = "trajectory_1s_final.xlsx"
df = pd.read_excel(file_path)

# Ensure proper sorting
df = df.sort_values(by=["Track ID", "Time [s]"])

# Create plot
plt.figure(figsize=(10, 6))

# Plot for each Track ID
for track_id, group in df.groupby("Track ID"):
    plt.plot(group["Time [s]"], group["cumulative_distance"])

# Labels and title
plt.xlabel("Time [s]")
plt.ylabel("Cumulative Distance [m]")
plt.title("Cumulative Distance vs Time")

# Grid
plt.grid(True)

# Show plot
plt.show()