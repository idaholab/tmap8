import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
import os
from matplotlib.lines import Line2D

from yhx_pct_metrics import (
    TOLERANCE,
    ar_max_low_p,
    ar_min_high_p,
    atom_ratio_eq_lower_func,
    atom_ratio_eq_upper_func,
    atom_ratio_plateau_region_fit,
    compute_all_fit_rmse,
    compute_mape,
    high_compute_prediction_rmspe,
    low_compute_prediction_rmspe,
    load_low_prediction_points,
    load_high_prediction_points,
    p0_lim_func,
)

# Changes working directory to script directory (for consistent MooseDocs usage)
script_folder = os.path.dirname(__file__)
os.chdir(script_folder)

# ============================================================================= #
# General parameters
mmHg_to_Pa = 133.322  # 1 mmHg = 133.322 Pa
C_to_K = 273.15  # 0 C = 273.15 K
temperature_list = [900, 950, 1000, 1050, 1100, 1150, 1200, 1250, 1300]  # C
temperature_list = [x + 273.15 for x in temperature_list]  # K

# ============================================================================ #
# Extract data from experiments
if "/tmap8/doc/" in script_folder.lower():  # if in documentation folder
    folderPath = "../../../../../test/tests/yttrium_hydrogen_system/"
else:  # if in test folder
    folderPath = ""
folderNameExpData = "PCT_data"
list_expData = []
for temperature in temperature_list:
    # Read the CSV file into a DataFrame
    expData = pd.read_csv(
        folderPath + folderNameExpData + "/" + str(int(temperature - C_to_K)) + ".csv"
    )
    # Update units from mm HG to Pa
    expData["Partial Pressure (Pa)"] = expData["Partial Pressure (mm Hg)"] * mmHg_to_Pa
    # Delete column with pressure in mm Hg
    expData = expData.drop(columns=["Partial Pressure (mm Hg)"])
    # Add a column for temperature
    expData["Temperature (K)"] = temperature
    # Organize by increasing order of atom ratio
    expData = expData.sort_values(by="Atom Ratio (-)")
    # print(expData)
    list_expData.append(expData)

# ============================================================================ #
# Identify plateau region


# Method to calculate the numerical derivative
def calculate_derivative(expData, x_col, y_col):
    x = expData.iloc[:, x_col]
    y = expData.iloc[:, y_col]
    dy_dx = np.gradient(y, x)
    return dy_dx


# List to store plateau positions for each temperature
plateau_positions = {}

# Loop through each temperature and calculate the derivative
for i, temperature in enumerate(temperature_list):
    x_col = 0  # atom ratio
    y_col = 1  # pressure
    dy_dx = calculate_derivative(list_expData[i], x_col, y_col)  # derivative
    dy_dx_y = dy_dx / list_expData[i].iloc[:, y_col]

    # Identify the range of derivatives that correspond to the plateau region
    plateau_threshold = 1  # Define a threshold for the plateau region
    plateau_edges = np.where(dy_dx_y < plateau_threshold)[0]

    # Find the start and end indices of the plateau region
    if len(plateau_edges) > 0:
        start_index = plateau_edges[0]
        end_index = plateau_edges[-1]
    else:
        start_index = end_index = None

    # Store the plateau edges
    plateau_positions[temperature] = {
        "start_index": int(start_index) if start_index is not None else None,
        "start": (
            list_expData[i].iloc[start_index, [x_col, y_col]]
            if start_index is not None
            else None
        ),
        "end_index": int(end_index) if end_index is not None else None,
        "end": (
            list_expData[i].iloc[end_index, [x_col, y_col]]
            if end_index is not None
            else None
        ),
    }

# ============================================================================ #
# Fit the plateau pressure as a function of temperature

# Calculate the average pressure on the plateau for each temperature
average_plateau_pressures = [
    (
        list_expData[i]
        .iloc[
            plateau_positions[temperature]["start_index"] : plateau_positions[
                temperature
            ]["end_index"]
            + 1,
            1,
        ]
        .mean()
        if plateau_positions[temperature]["start_index"] is not None
        and plateau_positions[temperature]["end_index"] is not None
        else None
    )
    for i, temperature in enumerate(temperature_list)
]

p0_lim = p0_lim_func(temperature_list)

# Plot the fit along with the data from the plateau pressure as a function of temperature
# Extract the plateau pressures for each temperature
plateau_pressures = average_plateau_pressures
# Filter out None values
filtered_temperatures = [
    temperature
    for temperature, pressure in zip(temperature_list, plateau_pressures)
    if pressure is not None
]
filtered_pressures = [
    pressure for pressure in plateau_pressures if pressure is not None
]

# ============================================================================ #
# Plot the fit and the plateau pressures
fig = plt.figure(figsize=(5, 5))
plt.plot(temperature_list, p0_lim, label="Fit", linestyle="--")
plt.scatter(
    filtered_temperatures, filtered_pressures, color="red", label="Plateau Pressures"
)
plt.xlabel("Temperature (K)")
plt.ylabel("Pressure (Pa)")
plt.yscale("log")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("YHx_PCT_plateau_pressure_fit.png", bbox_inches="tight", dpi=300)
plt.close(fig)

# ============================================================================ #
# Colors
TEMP_COLOR_MAP = {
    1173: "#1f77b4",
    1273: "#ff7f0e",
    1373: "#2ca02c",
    1473: "#d62728",
    1573: "#9467bd",
}


def color_for_T(T, idx):
    Ti = int(T)
    if Ti in TEMP_COLOR_MAP:
        return TEMP_COLOR_MAP[Ti]
    palette = plt.cm.tab20
    return palette(idx % 20)


# ============================================================================ #
# Create a meshgrid for the fit surface
pressure_range = np.linspace(
    (min(list_expData[0].iloc[:, 1])), (max(list_expData[0].iloc[:, 1])), 100
)
temperature_range = np.linspace(min(temperature_list), max(temperature_list), 100)
pressure_mesh, temperature_mesh = np.meshgrid(pressure_range, temperature_range)

atom_ratio_eq_upper = atom_ratio_eq_upper_func(temperature_range, pressure_range)

# ============================================================================ #
# Compare simulation data against model
# Read simulation data
if "/tmap8/doc/" in script_folder.lower():  # if in documentation folder
    csv_folder = "../../../../../test/tests/yttrium_hydrogen_system/gold/"
else:  # if in test folder
    csv_folder = "./gold/"

# Read high-pressure simulation data
high_prediction_points = load_high_prediction_points(csv_folder)
high_prediction_rmspe = high_compute_prediction_rmspe(csv_folder)

# Read low-pressure simulation data
low_predictions = load_low_prediction_points(csv_folder)
low_prediction_rmspe = low_compute_prediction_rmspe(csv_folder)

# Directory for the full low-to-high TMAP8
gold_dir = os.path.join(folderPath, "gold")
EPS = 1e-12  # Safety factor for analytical fits

# ============================================================================ #
# Plot the experimental data, the fit, and the TMAP8 results
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection="3d")

# Plot all the data points
for expData in list_expData:
    ax.scatter(
        expData["Partial Pressure (Pa)"],
        expData["Temperature (K)"],
        expData["Atom Ratio (-)"],
        label=f'{expData["Temperature (K)"].iloc[0]} K',
    )

# Initialize atom_ratio_mesh with the correct dimensions
atom_ratio_eq_upper_mesh = np.zeros_like(pressure_mesh)

# Create a surface for the fit
for i, pressure in enumerate(pressure_range):
    for j, temperature in enumerate(temperature_range):
        atom_ratio_eq_upper_mesh[j, i] = (
            atom_ratio_eq_upper_func(temperature, pressure)
            if pressure > p0_lim_func(temperature)
            else 0
        )

# Plot the fit surface
ax.plot_surface(
    pressure_mesh, temperature_mesh, atom_ratio_eq_upper_mesh, color="blue", alpha=0.3
)

# Initialize atom_ratio_mesh with the correct dimensions (low-pressure branch)
atom_ratio_eq_lower_mesh = np.zeros_like(pressure_mesh)

# Create a surface for the low-pressure fit
for i, pressure in enumerate(pressure_range):
    for j, temperature in enumerate(temperature_range):
        if pressure <= p0_lim_func(temperature):
            atom_ratio_eq_lower_mesh[j, i] = (
                atom_ratio_eq_lower_func(temperature, pressure)
                if pressure < p0_lim_func(temperature)
                else 0
            )

# Plot the low-pressure fit surface
ax.plot_surface(
    pressure_mesh, temperature_mesh, atom_ratio_eq_lower_mesh, color="green", alpha=0.3
)

ax.set_xlabel("Partial Pressure (Pa)")
ax.set_ylabel("Temperature (K)")
ax.set_zlabel("Atom Ratio (-)")
ax.set_title(
    "3D Plot of Partial Pressure, Temperature, and Atom Ratio with Fit Surface"
)
ax.set_zlim(0, 2)
ax.legend(loc="upper center", ncols=5)
plt.tight_layout()
ax.set_box_aspect(None, zoom=0.95)
plt.savefig("YHx_PCT_fit_3D.png", bbox_inches="tight", dpi=300)
plt.close(fig)

# Compute the low- and high-pressure branch fit RMSE against experimental data
RMSE_values_low, RMSE_values_high = compute_all_fit_rmse(list_expData, temperature_list)

# Plot the data points and the fit function for each temperature
fig = plt.figure(figsize=(12, 8))


high_data_handles, high_data_labels = [], []
fit_handles, fit_labels = [], []
tmap_handles, tmap_labels = [], []

for i, temperature in enumerate(temperature_list):
    # Extract the data points for the current temperature
    expData = list_expData[i]
    pressures = expData["Partial Pressure (Pa)"].to_numpy(dtype=float)
    atom_ratios = expData["Atom Ratio (-)"].to_numpy(dtype=float)
    color_T = color_for_T(temperature, i)

    # Plot the data points
    sc = plt.scatter(atom_ratios, pressures, color=color_T, s=16)
    high_data_handles.append(sc)
    high_data_labels.append(f"{temperature} K Data")

    p0_T = float(p0_lim_func(temperature))

    # Calculate the fit values using the function, over the pressure range spanned by the data
    P_line = np.logspace(
        np.log10(max(pressures.min(), 1e-12)), np.log10(pressures.max()), 400
    )
    AR_low_line = atom_ratio_eq_lower_func(temperature, P_line)
    AR_high_line = atom_ratio_eq_upper_func(temperature, P_line)

    # remove nan values and restrict each branch to the domain it's valid in
    mask_low_use = (
        np.isfinite(AR_low_line)
        & ((P_line / p0_T) < TOLERANCE)
        & (AR_low_line <= ar_max_low_p(temperature))
    )
    mask_high_use = (
        np.isfinite(AR_high_line)
        & ((P_line / p0_T) > TOLERANCE)
        & (AR_high_line >= 1.0)
    )

    # Calculate the RMSE for the current temperature (computed in yhx_pct_metrics.py)
    RMSE_low = RMSE_values_low.get(temperature, np.nan)
    RMSE_high = RMSE_values_high.get(temperature, np.nan)

    # Plot the fit function (low-pressure branch)
    if np.any(mask_low_use):
        (ln_lo,) = plt.plot(
            AR_low_line[mask_low_use],
            P_line[mask_low_use],
            color=color_T,
            linestyle="--",
            linewidth=1.8,
        )
        fit_handles.append(ln_lo)
        fit_labels.append(
            f"{temperature} K Low P Fit (RMSE: {RMSE_low:.2f})"
            if np.isfinite(RMSE_low)
            else f"{temperature} K Low P Fit (RMSE: n/a)"
        )

    # Plot the fit function (high-pressure branch)
    if np.any(mask_high_use):
        (ln_hi,) = plt.plot(
            AR_high_line[mask_high_use],
            P_line[mask_high_use],
            color=color_T,
            linestyle="-",
            linewidth=1.8,
        )
        fit_handles.append(ln_hi)
        fit_labels.append(
            f"{temperature} K High P Fit (RMSE: {RMSE_high:.2f})"
            if np.isfinite(RMSE_high)
            else f"{temperature} K High P Fit (RMSE: n/a)"
        )

    # --- Full low-to-high TMAP8 with comparison to experimental data ---
    tmap_name = f"YHx_PCT_Low_to_High_{int(temperature)}K.csv"
    tmap_path = os.path.join(gold_dir, tmap_name)
    df_tmap = pd.read_csv(tmap_path)

    ar_tmap = (
        df_tmap["atomic_fraction_H_enclosure_2_at_interface"].astype(float).to_numpy()
    )
    p_tmap = df_tmap["pressure_H2_enclosure_1_at_interface"].astype(float).to_numpy()

    mask_sweep = np.isfinite(ar_tmap) & np.isfinite(p_tmap) & (p_tmap > EPS)
    ar_tmap, p_tmap = ar_tmap[mask_sweep], p_tmap[mask_sweep]

    mask_exp_mape = (
        np.isfinite(atom_ratios) & np.isfinite(pressures) & (pressures > EPS)
    )
    ar_exp_mape = atom_ratios[mask_exp_mape]
    p_exp_mape = pressures[mask_exp_mape]
    order_exp_mape = np.argsort(ar_exp_mape)
    ar_exp_mape, p_exp_mape = ar_exp_mape[order_exp_mape], p_exp_mape[order_exp_mape]

    mape = compute_mape(ar_tmap, p_tmap, ar_exp_mape, p_exp_mape)

    order_sweep = np.argsort(ar_tmap)
    (ln_sweep,) = plt.plot(
        ar_tmap[order_sweep],
        p_tmap[order_sweep],
        color=color_T,
        linestyle=":",
        linewidth=2.0,
    )
    tmap_handles.append(ln_sweep)
    tmap_labels.append(f"{int(temperature)}.15 K TMAP8 (err={mape:.2f}%)")

# plot the TMAP8 predictions (high-pressure)
for point in high_prediction_points:
    error = abs(point["prediction"] - point["reference"]) / point["reference"] * 100
    h = plt.scatter(point["prediction"], point["pressure"], marker="x", color="k", s=90)
    tmap_handles.append(h)
    tmap_labels.append(
        f'{point["temperature"]} K and {point["pressure"]:.2f} Pa '
        f"(error: {error:.2f} %)"
    )

# plot the TMAP8 predictions (low-pressure)
for point in low_predictions:
    error = abs(point["prediction"] - point["reference"]) / point["reference"] * 100
    h = plt.scatter(point["prediction"], point["pressure"], marker="*", color="k", s=90)
    tmap_handles.append(h)
    tmap_labels.append(
        f'{point["temperature"]} K and {point["pressure"]:.2f} Pa '
        f"(error: {error:.2f} %)"
    )

plt.xlabel("Atom Ratio (-)")
plt.ylabel("Partial Pressure (Pa)")
plt.yscale("log")
plt.grid(True)

# Build 3-column legend: col 1 = experimental data, col 2 = fits, col 3 = TMAP8 results
nrows = max(len(high_data_handles), len(fit_handles), len(tmap_handles), 1)


def pad_column(handles, labels, n):
    blank_handle = Line2D([], [], color="none")
    handles = list(handles) + [blank_handle] * (n - len(handles))
    labels = list(labels) + [""] * (n - len(labels))
    return handles, labels


col1_handles, col1_labels = pad_column(high_data_handles, high_data_labels, nrows)
col2_handles, col2_labels = pad_column(fit_handles, fit_labels, nrows)
col3_handles, col3_labels = pad_column(tmap_handles, tmap_labels, nrows)

combined_handles = col1_handles + col2_handles + col3_handles
combined_labels = col1_labels + col2_labels + col3_labels

plt.subplots_adjust(bottom=0.32)
plt.legend(
    combined_handles,
    combined_labels,
    ncols=3,
    loc="upper center",
    bbox_to_anchor=(0.5, -0.15),
    fontsize=8,
    frameon=True,
    borderaxespad=0.0,
)
plt.savefig("YHx_PCT_fit_2D.png", bbox_inches="tight", dpi=300)
plt.close(fig)

# print the RMSE values for each temperature
print("temperatures (K) and RMSE values (low): ", RMSE_values_low)
print("temperatures (K) and RMSE values (high): ", RMSE_values_high)

# print the average RMSE value
average_rmse_low = (
    np.mean(list(RMSE_values_low.values())) if RMSE_values_low else np.nan
)
average_rmse_high = (
    np.mean(list(RMSE_values_high.values())) if RMSE_values_high else np.nan
)
print(
    f"Average RMSE (Low): {average_rmse_low:.2f}"
    if np.isfinite(average_rmse_low)
    else "Average RMSE (Low): n/a"
)
print(
    f"Average RMSE (High): {average_rmse_high:.2f}"
    if np.isfinite(average_rmse_high)
    else "Average RMSE (High): n/a"
)
print(f"TMAP8 high pressure prediction RMSPE: {high_prediction_rmspe:.6f} %")
print(f"TMAP8 low pressure prediction RMSPE: {low_prediction_rmspe:.6f} %")

# ============================================================================ #
# Raw plot (experimental data only)
fig = plt.figure(figsize=(10, 6))
for i, expData in enumerate(list_expData):
    T = expData["Temperature (K)"].iloc[0]
    color_T = color_for_T(T, i)
    x = expData["Atom Ratio (-)"].values
    y = expData["Partial Pressure (Pa)"].values
    plt.scatter(x, y, s=16, label=f"{int(T)} K", color=color_T)
    plt.plot(x, y, color=color_T)

plt.yscale("log")
plt.xlabel("Atom Ratio (-)")
plt.ylabel("Partial Pressure (Pa)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("YHx_PCT_Data.png", dpi=300)
plt.close(fig)

# ============================================================================ #
# Raw plot with Ar_Max_Low_P(T) and Ar_Min_High_P(T) dashed boundary lines
fig = plt.figure(figsize=(10, 6))
ax = plt.gca()

ar_max_x, ar_max_y, temp_order = [], [], []
ar_min_x, ar_min_y = [], []
temp_handles, temp_labels = [], []

for i, expData in enumerate(list_expData):
    T = float(expData["Temperature (K)"].iloc[0])
    color_T = color_for_T(T, i)

    x = expData["Atom Ratio (-)"].values.astype(float)
    y = expData["Partial Pressure (Pa)"].values.astype(float)

    (ln_temp,) = ax.plot(x, y, color=color_T, linewidth=1.8, label=f"{int(T)} K")
    temp_handles.append(ln_temp)
    temp_labels.append(f"{int(T)} K")

    p0_T = float(p0_lim_func(T))
    ar_max_x.append(ar_max_low_p(T))
    ar_max_y.append(p0_T)
    ar_min_x.append(ar_min_high_p(T))
    ar_min_y.append(p0_T)
    temp_order.append(T)

order = np.argsort(np.array(temp_order))
ar_max_x = np.array(ar_max_x)[order]
ar_max_y = np.array(ar_max_y)[order]
ar_min_x = np.array(ar_min_x)[order]
ar_min_y = np.array(ar_min_y)[order]

(ar_max_handle,) = ax.plot(
    ar_max_x,
    ar_max_y,
    linestyle="--",
    color="k",
    linewidth=1.6,
    label="Fitted Maximum Atomic Ratio in the Low-Pressure Regime",
)
(ar_min_handle,) = ax.plot(
    ar_min_x,
    ar_min_y,
    linestyle="--",
    color="purple",
    linewidth=1.6,
    label="Fitted Minimum Atomic Ratio in the High-Pressure Regime",
)

ax.set_yscale("log")
ax.set_xlabel("Atom Ratio (-)")
ax.set_ylabel("Partial Pressure (Pa)")
ax.grid(True, which="both", linestyle=":", alpha=0.6)

ncols_temp = min(len(temp_handles), 5)
fig.legend(
    temp_handles,
    temp_labels,
    ncols=ncols_temp,
    loc="upper center",
    bbox_to_anchor=(0.5, 1.06),
    fontsize=9,
    frameon=True,
)
plt.tight_layout(rect=[0, 0, 1, 0.94])

ax.legend(
    handles=[ar_max_handle, ar_min_handle],
    labels=[
        "Fitted Maximum Atomic Ratio in the Low-Pressure Regime",
        "Fitted Minimum Atomic Ratio in the High-Pressure Regime",
    ],
    loc="best",
    fontsize=9,
    frameon=True,
)

eqn_max = r"Ar$_{\rm Max,LowP}$(T) = 1.01×10$^{-6}$·T$^2$ − 2.55×10$^{-3}$·T + 2.16"
eqn_min = r"Ar$_{\rm Min,HighP}$(T) = −1.01×10$^{-6}$·T$^2$ + 2.55×10$^{-3}$·T − 0.56"
ax.text(0.02, 0.97, eqn_max, transform=ax.transAxes, fontsize=9, va="top", color="k")
ax.text(
    0.02, 0.90, eqn_min, transform=ax.transAxes, fontsize=9, va="top", color="purple"
)

plt.savefig("YHx_PCT_Plateau_EndPoints_comparison.png", dpi=300, bbox_inches="tight")
plt.close(fig)

# ============================================================================ #
# Plateau-region fit vs PCT data
all_T = [float(expData["Temperature (K)"].iloc[0]) for expData in list_expData]
min_T = float(np.min(all_T))
max_T = float(np.max(all_T))
ar_lower = float(ar_max_low_p(min_T))
ar_upper = float(ar_min_high_p(max_T))

fig, ax = plt.subplots(figsize=(10, 8))
full_color = (0.55, 0.55, 0.55, 0.30)
fit_linewidth = 2.2

for i, expData in enumerate(list_expData):
    T = float(expData["Temperature (K)"].iloc[0])
    color_T = color_for_T(T, i)

    AR = expData["Atom Ratio (-)"].values.astype(float)
    P = expData["Partial Pressure (Pa)"].values.astype(float)
    ax.scatter(AR, P, s=10, alpha=full_color[3], color=full_color[:3])

    p0_T = float(p0_lim_func(T))
    P_line = np.logspace(
        np.log10(max(p0_T / 2.5, 1e-12)), np.log10(max(p0_T * 2.5, 1e-12)), 400
    )
    AR_line = atom_ratio_plateau_region_fit(T, P_line)

    mask_fit = np.isfinite(AR_line) & (AR_line >= ar_lower) & (AR_line <= ar_upper)
    if np.any(mask_fit):
        ax.plot(
            AR_line[mask_fit],
            P_line[mask_fit],
            "-",
            linewidth=fit_linewidth,
            color=color_T,
            label=f"{int(T)} K",
        )

ax.set_yscale("log")
ax.set_ylabel("Partial Pressure (Pa)")
ax.set_xlabel("Atom Ratio (\u2013)")
ax.set_title(
    "Plateau-Region AR(P,T): Fit Curves Clipped to Specified AR Range\n(Experimental Data Unchanged)"
)
ax.grid(True, which="both", ls="--", alpha=0.4)
ax.legend(bbox_to_anchor=(1.04, 1.0), fontsize=9)
plt.tight_layout()

eqn_text = (
    r"$\mathrm{AR}(P,T) = (1.33 - 2.18\times 10^{-4}\,T)"
    r" + (1.06e01 - 4.35\times 10^{-3}\,T)\,\ln\!\left(\frac{P}{1.15\,p_0(T)}\right)$"
    "\n"
    rf"Fit shown only for $AR \in [{ar_lower:.3f},\,{ar_upper:.3f}]$ (lower bound at $T_{{\min}}={min_T:.0f}\,\mathrm{{K}}$)"
)
ax.text(
    0.02,
    0.98,
    eqn_text,
    transform=ax.transAxes,
    fontsize=10,
    va="top",
    ha="left",
    color="black",
    bbox=dict(
        boxstyle="round", facecolor="white", alpha=0.85, edgecolor="gray", pad=0.35
    ),
)

plt.savefig("YHx_PCT_AR_plateau_fit.png", dpi=300, bbox_inches="tight")
plt.close(fig)
