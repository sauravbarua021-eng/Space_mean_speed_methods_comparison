import pandas as pd
import numpy as np

# =========================
# 1. Load & Clean Data
# =========================
file_path = "cross_test2_pivoted.xlsx"
df = pd.read_excel(file_path)

# Convert to numeric (fix type errors)
cols = ["x [m]", "y [m]", "Speed [km/h]", "Time [s]"]
for c in cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")

df = df.dropna(subset=cols)

df = df.sort_values(by=["Track ID", "Time [s]"]).reset_index(drop=True)

# =========================
# 2. Kalman CV + ZVD
# =========================
def kalman_cv_zvd(group):
    group = group.sort_values("Time [s]").reset_index(drop=True)

    x = group["x [m]"].values
    y = group["y [m]"].values
    speed = group["Speed [km/h]"].values

    n = len(group)

    X = np.zeros((4, n))  # [x, y, vx, vy]
    P = np.eye(4)

    X[0, 0] = x[0]
    X[1, 0] = y[0]

    Q_base = np.diag([0.1, 0.1, 1, 1])
    R = np.diag([5, 5])

    H = np.array([[1, 0, 0, 0],
                  [0, 1, 0, 0]])

    for i in range(1, n):
        dt = group["Time [s]"].iloc[i] - group["Time [s]"].iloc[i-1]
        if dt <= 0:
            dt = 0.033

        F = np.array([
            [1, 0, dt, 0],
            [0, 1, 0, dt],
            [0, 0, 1, 0 ],
            [0, 0, 0, 1 ]
        ])

        dx = x[i] - x[i-1]
        dy = y[i] - y[i-1]
        displacement = np.sqrt(dx**2 + dy**2)

        is_stop = (speed[i] < 0.5) and (displacement < 0.1)

        Q = Q_base * (0.01 if is_stop else 1)

        # Prediction
        X_pred = F @ X[:, i-1]
        P_pred = F @ P @ F.T + Q

        # Update
        Z = np.array([x[i], y[i]])
        Y = Z - H @ X_pred
        S = H @ P_pred @ H.T + R
        K = P_pred @ H.T @ np.linalg.inv(S)

        X[:, i] = X_pred + K @ Y
        P = (np.eye(4) - K @ H) @ P_pred

        # Zero velocity enforcement
        if is_stop:
            X[2, i] = 0
            X[3, i] = 0

    group["x_smooth"] = X[0]
    group["y_smooth"] = X[1]

    return group

df = df.groupby("Track ID", group_keys=False).apply(kalman_cv_zvd)

# =========================
# 3. Interpolate to INTEGER seconds (NO EXTRAPOLATION)
# =========================
interp_list = []

for track_id, group in df.groupby("Track ID"):
    group = group.set_index("Time [s]")

    # ✅ FIX: remove extrapolation
    t_min = int(np.ceil(group.index.min()))
    t_max = int(np.floor(group.index.max()))

    if t_min > t_max:
        continue

    new_time = np.arange(t_min, t_max + 1, 1)

    group_interp = group.reindex(group.index.union(new_time))
    group_interp = group_interp.interpolate(method="linear")

    group_interp = group_interp.loc[new_time]

    # Drop any remaining NaNs (extra safety)
    group_interp = group_interp.dropna(subset=["x_smooth", "y_smooth"])

    group_interp["Track ID"] = track_id

    interp_list.append(group_interp.reset_index())

df_interp = pd.concat(interp_list, ignore_index=True)

# =========================
# 4. Distance Calculation
# =========================
def compute_distance(group):
    dx = group["x_smooth"].diff()
    dy = group["y_smooth"].diff()
    return np.sqrt(dx**2 + dy**2).fillna(0)

df_interp["step_distance"] = df_interp.groupby("Track ID").apply(
    compute_distance
).reset_index(level=0, drop=True)

df_interp["cumulative_distance"] = df_interp.groupby("Track ID")[
    "step_distance"
].cumsum()

# =========================
# 5. Drop unwanted columns
# =========================
drop_cols = [
    "Entry Gate", "Entry Time [s]", "Exit Gate", "Exit Time [s]",
    "Traveled Dist. [m]", "Avg. Speed [km/h]",
    "Tan. Acc. [m/s2]", "Lat. Acc. [m/s2]"
]

df_interp = df_interp.drop(columns=[c for c in drop_cols if c in df_interp.columns])

# =========================
# 6. Save Output
# =========================
output_file = "trajectory_1s_final.xlsx"
df_interp.to_excel(output_file, index=False)

print(f"✅ Final clean dataset saved: {output_file}")