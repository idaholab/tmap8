import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
import os

from yhx_pct_metrics import (
    atom_ratio_eq_upper_func,
    compute_prediction_rmspe,
    load_prediction_points,
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
tolerance = 1.148
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
    print(expData)
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


# Define fitting function
def p0_lim_func(temperature):
    return np.exp(
        -26.1
        + 3.88 * 10 ** (-2) * np.array(temperature)
        - 9.7 * 10 ** (-6) * np.square(temperature)
    )


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


# Local helper: minimum AR for the high-pressure branch (same form as used later in script)
def ar_min_high_p(T):
    """
    Temperature-dependent minimum atom ratio for the high-pressure branch:
    Ar_Min_High_P(T) = -1.01e-6 * T^2 + 2.55e-3 * T - 0.5616
    """
    T = float(T)
    return -1.01e-6 * (T**2) + 2.55e-3 * T - 0.5616


# ============================================================================ #
# Fit the high pressures as a function of temperature
def atom_ratio_eq_upper_func(temperature, pressure):
    AR_min = (
        -1.01e-6 * temperature**2 + 2.55e-3 * temperature - 0.56166
    )  # AR minimum at high P
    return 2 - 1.0015 * (
        AR_min
        + np.exp(
            24.8902
            - 0.0253 * temperature
            + (-0.3981 + 0.001 * temperature)
            * (np.log(pressure - p0_lim_func(temperature)))
        )
    ) ** (-1)


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

# High pressure files
TMAP8_prediction_T1273_P3e3 = pd.read_csv(csv_folder + "YHx_PCT_T1273_P3e3_out.csv")
TMAP8_prediction_T1173_P1e3 = pd.read_csv(csv_folder + "YHx_PCT_T1173_P1e3_out.csv")
TMAP8_prediction_T1173_P1e4 = pd.read_csv(csv_folder + "YHx_PCT_T1173_P1e4_out.csv")
TMAP8_prediction_T1173_P5e4 = pd.read_csv(csv_folder + "YHx_PCT_T1173_P5e4_out.csv")

TMAP8_prediction_T1273_P3e3_temperature = TMAP8_prediction_T1273_P3e3[
    "temperature"
].iat[-1]
TMAP8_prediction_T1273_P3e3_pressure = TMAP8_prediction_T1273_P3e3[
    "pressure_H2_enclosure_1_at_interface"
].iat[-1]
TMAP8_prediction_T1273_P3e3_atomic_fraction = TMAP8_prediction_T1273_P3e3[
    "atomic_fraction_H_enclosure_2_at_interface"
].iat[-1]
analytical_equation_T1273_P3e3_atomic_fraction = atom_ratio_eq_upper_func(
    TMAP8_prediction_T1273_P3e3_temperature, TMAP8_prediction_T1273_P3e3_pressure
)

TMAP8_prediction_T1173_P1e3_temperature = TMAP8_prediction_T1173_P1e3[
    "temperature"
].iat[-1]
TMAP8_prediction_T1173_P1e3_pressure = TMAP8_prediction_T1173_P1e3[
    "pressure_H2_enclosure_1_at_interface"
].iat[-1]
TMAP8_prediction_T1173_P1e3_atomic_fraction = TMAP8_prediction_T1173_P1e3[
    "atomic_fraction_H_enclosure_2_at_interface"
].iat[-1]
analytical_equation_T1173_P1e3_atomic_fraction = atom_ratio_eq_upper_func(
    TMAP8_prediction_T1173_P1e3_temperature, TMAP8_prediction_T1173_P1e3_pressure
)

TMAP8_prediction_T1173_P1e4_temperature = TMAP8_prediction_T1173_P1e4[
    "temperature"
].iat[-1]
TMAP8_prediction_T1173_P1e4_pressure = TMAP8_prediction_T1173_P1e4[
    "pressure_H2_enclosure_1_at_interface"
].iat[-1]
TMAP8_prediction_T1173_P1e4_atomic_fraction = TMAP8_prediction_T1173_P1e4[
    "atomic_fraction_H_enclosure_2_at_interface"
].iat[-1]
analytical_equation_T1173_P1e4_atomic_fraction = atom_ratio_eq_upper_func(
    TMAP8_prediction_T1173_P1e4_temperature, TMAP8_prediction_T1173_P1e4_pressure
)

TMAP8_prediction_T1173_P5e4_temperature = TMAP8_prediction_T1173_P5e4[
    "temperature"
].iat[-1]
TMAP8_prediction_T1173_P5e4_pressure = TMAP8_prediction_T1173_P5e4[
    "pressure_H2_enclosure_1_at_interface"
].iat[-1]
TMAP8_prediction_T1173_P5e4_atomic_fraction = TMAP8_prediction_T1173_P5e4[
    "atomic_fraction_H_enclosure_2_at_interface"
].iat[-1]
analytical_equation_T1173_P5e4_atomic_fraction = atom_ratio_eq_upper_func(
    TMAP8_prediction_T1173_P5e4_temperature, TMAP8_prediction_T1173_P5e4_pressure
)


# Low-pressure fit
def atom_ratio_eq_lower_func(T, P):
    p0 = p0_lim_func(T)
    arg = np.maximum(p0 - P, 1e-12)
    with np.errstate(divide="ignore", invalid="ignore"):
        return (1.01e-6 * np.square(T) - 2.556e-3 * T + 2.156) - 10 * (
            0.001 + np.exp(-50.0 + 5.73e-2 * T + (0.8296 - 2.69e-3 * T) * np.log(arg))
        ) ** (-1)


def atom_ratio_eq_upper_func(T, P):
    p0 = p0_lim_func(T)
    arg = np.maximum(P - p0, 1e-12)
    with np.errstate(divide="ignore", invalid="ignore"):
        return 2.0 - (
            1.0 + np.exp(21.6 - 0.0225 * T + (-0.0445 + 7.18e-4 * T) * np.log(arg))
        ) ** (-1)


def rmse(y_true, y_pred):
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


# ------------------------------------------------------------------------------
# Load experimental data
# ------------------------------------------------------------------------------

data_by_temp = {}

for T in TEMPERATURES_K:
    path_k = os.path.join(exp_data_dir, f"{int(T)}.csv")
    path_c = os.path.join(exp_data_dir, f"{int(round(T - 273.15))}.csv")
    f = path_k if os.path.exists(path_k) else path_c

    if not os.path.exists(f):
        print(
            f"WARNING: missing experimental CSV for {T} K -> tried {path_k} and {path_c}"
        )
        continue

    df = pd.read_csv(f)

    # Pressure columns accepted: log10(Pa), Pa, or mmHg
    if COL_PRESSURE_EXP_LOG in df.columns:
        df[COL_PRESSURE_PA] = 10 ** df[COL_PRESSURE_EXP_LOG]
    elif COL_PRESSURE_PA in df.columns:
        df[COL_PRESSURE_PA] = df[COL_PRESSURE_PA].astype(float)
    elif COL_PRESSURE_MMHG in df.columns:
        df[COL_PRESSURE_PA] = df[COL_PRESSURE_MMHG].astype(float) * MMHG_TO_PA
    else:
        raise ValueError(f"CSV {f} missing pressure columns")

    # Atom ratio harmonization
    if COL_ATOM_RATIO not in df.columns:
        if "Atom Ratio (-)" in df.columns:
            df[COL_ATOM_RATIO] = df["Atom Ratio (-)"]
        else:
            raise ValueError(f"CSV {f} missing atom ratio column")

    df = df[[COL_PRESSURE_PA, COL_ATOM_RATIO]].dropna().sort_values(COL_PRESSURE_PA)
    data_by_temp[T] = df.reset_index(drop=True)

# ------------------------------------------------------------------------------
# Raw plot
# ------------------------------------------------------------------------------

fig = plt.figure(figsize=(10, 6))
for T in TEMPERATURES_K:
    df = data_by_temp.get(T)
    if df is None:
        continue
    plt.scatter(df[COL_ATOM_RATIO], df[COL_PRESSURE_PA], s=16, label=f"{T}.15 K")
    plt.plot(df[COL_ATOM_RATIO], df[COL_PRESSURE_PA])

p0_lim = p0_lim_func(temperature_list)

for T in TEMPERATURES_K:
    df = data_by_temp.get(T)
    if df is None:
        continue
    AR = df[COL_ATOM_RATIO].values
    P = df[COL_PRESSURE_PA].values
    idx = np.where(AR > ATOM_RATIO_LOW)[0]
    if idx.size:
        sel_T.append(T)
        sel_P.append(P[idx[0]])

fig = plt.figure(figsize=(5, 5))
plt.plot(TEMPERATURES_K, p0_vals, "--", label="Fit")
if sel_T:
    plt.scatter(sel_T, sel_P, color="red", s=24, label="Plateau Pressures")
plt.yscale("log")
plt.xlabel("Temperature (K)")
plt.ylabel("Pressure (Pa)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("YHx_PCT_plateau_pressure_fit.png", dpi=FIG_DPI)
plt.close(fig)

# ------------------------------------------------------------------------------
# TMAP8 Data
# ------------------------------------------------------------------------------

# ============================================================================ #
# Create a meshgrid for the fit surface
pressure_range = np.linspace(
    (min(list_expData[0].iloc[:, 1])), (max(list_expData[0].iloc[:, 1])), 100
)
temperature_range = np.linspace(min(temperature_list), max(temperature_list), 100)
pressure_mesh, temperature_mesh = np.meshgrid(pressure_range, temperature_range)

    T = df["temperature"].iat[-1]
    P = df["pressure_H2_enclosure_1_at_interface"].iat[-1]
    xH = df["atomic_fraction_H_enclosure_2_at_interface"].iat[-1]

    xH_model_low = atom_ratio_eq_lower_func(T, P)

<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
prediction_points = load_prediction_points(csv_folder)
prediction_rmspe = compute_prediction_rmspe(csv_folder)

=======
# ------------------------------------------------------------------------------
=======
    low_predictions.append({
        "file": fname,
        "T": T,
        "P": P,
        "xH": xH,
        "xH_model": xH_model_low,
        "error_pct": (abs(xH - xH_model_low) / xH_model_low * 100),
    })
=======
    low_predictions.append(
        {
            "file": fname,
            "T": T,
            "P": P,
            "xH": xH,
            "xH_model": xH_model_low,
            "error_pct": (abs(xH - xH_model_low) / xH_model_low * 100),
        }
    )
>>>>>>> 3c02387f (Formatting)

# ============================================================================ #
>>>>>>> fdf51b49 (Improvement to low pressure fit and corrections to python file)
# Colors (consistent palette by temperature)
TEMP_COLOR_MAP = {
    1173: "#1f77b4",  # blue
    1273: "#ff7f0e",  # orange
    1373: "#2ca02c",  # green
    1473: "#d62728",  # red
    1573: "#9467bd",  # purple
}


def color_for_T(T, idx):
    Ti = int(T)
    if Ti in TEMP_COLOR_MAP:
        return TEMP_COLOR_MAP[Ti]
    palette = plt.cm.tab20
    return palette(idx % 20)

<<<<<<< HEAD
<<<<<<< HEAD

# ------------------------------------------------------------------------------
# Combined 2D Fit Figure
# ------------------------------------------------------------------------------
>>>>>>> 6de057a7 (Appling patches to python and C files)

# ============================================================================ #
# Plot the experimental data, the fit, and the TMAP8 results
=======
=======

>>>>>>> 3c02387f (Formatting)
# ============================================================================ #
# Plot the experimental data, the fit, and the TMAP8 results on a 3D plot
>>>>>>> fdf51b49 (Improvement to low pressure fit and corrections to python file)
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection="3d")

# Plot all the data points (colored by temperature)
for i, expData in enumerate(list_expData):
    T = expData["Temperature (K)"].iloc[0]
    color_T = color_for_T(T, i)
    ax.scatter(
        expData["Partial Pressure (Pa)"],
        expData["Temperature (K)"],
        expData["Atom Ratio (-)"],
        label=f"{T} K",
        color=color_T,
        s=16,
    )

# Initialize atom_ratio_mesh with the correct dimensions (High Pressure)
atom_ratio_eq_upper_mesh = np.zeros_like(pressure_mesh)

# Create a surface for the fit (High Pressure)
for i, pressure in enumerate(pressure_range):
    for j, temperature in enumerate(temperature_range):
        atom_ratio_eq_upper_mesh[j, i] = (
            atom_ratio_eq_upper_func(temperature, pressure)
            if pressure > p0_lim_func(temperature)
            else 0
        )

# Initialize atom_ratio_mesh with the correct dimensions (Low Pressure)
atom_ratio_eq_lower_mesh = np.zeros_like(pressure_mesh)

# Create a surface for the fit (Low Pressure)
for i, pressure in enumerate(pressure_range):
    for j, temperature in enumerate(temperature_range):
        if pressure <= p0_lim_func(temperature):
            atom_ratio_eq_lower_mesh[j, i] = (
                atom_ratio_eq_lower_func(temperature, pressure)
                if pressure < p0_lim_func(temperature)
                else 0
            )

# Plot the fit surface (High Pressure)
ax.plot_surface(
    pressure_mesh, temperature_mesh, atom_ratio_eq_upper_mesh, color="blue", alpha=0.3
)
# Plot the fit surface (Low Pressure)
ax.plot_surface(
    pressure_mesh, temperature_mesh, atom_ratio_eq_lower_mesh, color="green", alpha=0.3
)

ax.set_xlabel("Pressure (Pa)")
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

# Initialize a dictionary to store RMSE values for each temperature
RMSE_values_high = {}  # (High pressure)
RMSE_values_low = {}  # (Low pressure)

# Plot the data points and the fit function for each temperature
fig = plt.figure(figsize=(12, 6))

print("temperature_list", temperature_list)
# -------------------- Legend collections --------------------
high_data_handles, high_data_labels = [], []
high_fit_handles, high_fit_labels = [], []
low_fit_handles, low_fit_labels = [], []

# NEW: distinct legend group for Plateau region
plateau_fit_handles, plateau_fit_labels = [], []

tmap_high_handles, tmap_high_labels = [], []
tmap_low_handles, tmap_low_labels = [], []

for i, temperature in enumerate(temperature_list):
    # Extract the data points for the current temperature
    expData = list_expData[i]
    pressures = expData["Partial Pressure (Pa)"]
    atom_ratios = expData["Atom Ratio (-)"]

    # color by temperature
    color_T = color_for_T(temperature, i)

    # Ensure we have arrays
    pressures_arr = np.asarray(pressures, dtype=float)
    atom_ratios_arr = np.asarray(atom_ratios, dtype=float)

    # --------------------  plot FULL experimental data --------------------
    # CHANGED: swapped axes — x=atom_ratios_arr, y=pressures_arr
    sc_all = plt.scatter(
        atom_ratios_arr,
        pressures_arr,
        color=color_T,
        s=16,
    )
    high_data_handles.append(sc_all)
    high_data_labels.append(f"{temperature} K Data")
    # --------------------------------------------------------------------------------------------

    index_limit = plateau_positions[temperature]["end_index"]
    if index_limit is not None:
        # Select only the values that are above the transition region
        pressures_upper = pressures[index_limit:]
        atom_ratios_upper = atom_ratios[index_limit:]

        # Calculate the fit values using the function
        fit_values_upper = atom_ratio_eq_upper_func(temperature, pressures_upper)

        # remove nan values from fit_values_upper and the corresponding index from atom_ratios_upper and pressures_upper
        index_not_nan = ~np.isnan(fit_values_upper)
        fit_values_upper = fit_values_upper[index_not_nan]
        atom_ratios_upper = atom_ratios_upper[index_not_nan]
        pressures_upper = pressures_upper[index_not_nan]

        # Calculate the RMSE for the current temperature (high)
        RMSE = np.sqrt(
            np.mean((np.array(atom_ratios_upper) - np.array(fit_values_upper)) ** 2)
        )
        RMSE_values_high[temperature] = RMSE

        # CHANGED: swapped axes — x=fit_values_upper, y=pressures_upper
        (ln_hi,) = plt.plot(
            fit_values_upper,
            pressures_upper,
            color=color_T,
            linestyle="-",
        )
        high_fit_handles.append(ln_hi)
        high_fit_labels.append(f"{temperature} K High P Fit RMSE {RMSE:.2f}")

    def ar_max_low_p(T):
        """
        Temperature-dependent maximum atom ratio for the low-pressure branch:
        Ar_Max_Low_P(T) = 1.01e-6 * T^2 - 2.55e-3 * T + 2.156
        """
        T = float(T)
        return 1.01e-6 * (T**2) - 2.55e-3 * T + 2.156

    # Compute threshold for low-pressure regime using Ar_Max_Low_P(T)
    Ar_Max_Low_P_T = ar_max_low_p(temperature)

    # Find the last index where Atom Ratio <= Ar_Max_Low_P(T)
    mask = atom_ratios_arr <= Ar_Max_Low_P_T
    low_p_index = np.where(mask)[0][-1] if np.any(mask) else None

    # plot the lower-pressure fit and data below the plateau with RMSE
    if low_p_index is not None:
        # Values at and below the threshold index (include low_p_index to capture edge)
        pressures_lower = pressures_arr[: low_p_index + 1]
        atom_ratios_lower = atom_ratios_arr[: low_p_index + 1]

        # Compute the lower-fit values
        fit_values_lower = atom_ratio_eq_lower_func(temperature, pressures_lower)

        # Remove NaNs (domain or numerical issues)
        index_not_nan_low = ~np.isnan(fit_values_lower)
        fit_values_lower = fit_values_lower[index_not_nan_low]
        atom_ratios_lower = atom_ratios_lower[index_not_nan_low]
        pressures_lower = pressures_lower[index_not_nan_low]

        # Calculate the RMSE for the current temperature (low)
        RMSE = np.sqrt(
            np.mean((np.array(atom_ratios_lower) - np.array(fit_values_lower)) ** 2)
        )
        RMSE_values_low[temperature] = RMSE

        # CHANGED: swapped axes — x=fit_values_lower, y=pressures_lower
        (ln_lo,) = plt.plot(
            fit_values_lower,
            pressures_lower,
            color=color_T,
            linestyle="--",
            label=f"{temperature} K Low P Fit RMSE {RMSE:.2f}",
        )

<<<<<<< HEAD
        # Plot the data points
        plt.scatter(pressures_upper, atom_ratios_upper, label=f"{temperature} K Data")

        # Plot the fit function
        plt.plot(
            pressures_upper,
            fit_values_upper,
            label=f"{temperature} K Fit (RMSE: {RMSE:.2f})",
        )

# plot the TMAP8 predictions
for point in prediction_points:
    error = abs(point["prediction"] - point["reference"]) / point["reference"] * 100
    plt.scatter(
        point["pressure"],
        point["prediction"],
        label=(
            f'{point["temperature"]} K and {point["pressure"]:.2f} Pa prediction '
            f"(error: {error:.2f} %)"
        ),
        marker="x",
        color="k",
        s=90,
    )
=======
        # Include RMSE in low fit legend ordering
        low_fit_handles.append(ln_lo)
        low_fit_labels.append(f"{temperature} K Low P Fit RMSE {RMSE:.2f}")


# -------------------- Combined fit: Low ↔ Plateau ↔ High (by AR thresholds) --------------------
# Local helper: plateau-region fit (identical to the later section; included here to avoid reordering)
def atom_ratio_plateau_region_fit(T, P):

    T = float(T)
    p0 = float(p0_lim_func(T))  # plateau pressure reference
    denom = max(tolerance * p0, 1e-20)
    arg = np.maximum(np.asarray(P, dtype=float) / denom, 1e-12)
    return (1.325 - 2.177e-04 * T) + (1.056e01 - 4.35e-03 * T) * np.log(arg)


# Local helper: minimum AR for the high-pressure branch (same form as used later in script)
def ar_min_high_p(T):
    """
    Temperature-dependent minimum atom ratio for the high-pressure branch:
    Ar_Min_High_P(T) = -1.01e-6 * T^2 + 2.55e-3 * T - 0.5616
    """
    T = float(T)
    return -1.01e-6 * (T**2) + 2.55e-3 * T - 0.5616


# Helper: branch selection for a single (T, P) using same domain + AR-threshold rules
def select_branch(T, P):
    T = float(T)
    P = float(P)
    p0_T = float(p0_lim_func(T))

    # Evaluate the three branches at this point
    AR_low = atom_ratio_eq_lower_func(T, np.array([P]))
    AR_high = atom_ratio_eq_upper_func(T, np.array([P]))
    AR_plateau = atom_ratio_plateau_region_fit(T, np.array([P]))

    AR_low = AR_low[0] if np.size(AR_low) else np.nan
    AR_high = AR_high[0] if np.size(AR_high) else np.nan
    AR_plateau = AR_plateau[0] if np.size(AR_plateau) else np.nan

    # Thresholds
    AR_low_max = ar_max_low_p(T)
    AR_high_min = ar_min_high_p(T)

    # Domains
    is_low_dom = (P / p0_T) < tolerance
    is_high_dom = (P / p0_T) > tolerance

    use_low = np.isfinite(AR_low) and is_low_dom and (AR_low <= AR_low_max)
    use_high = np.isfinite(AR_high) and is_high_dom and (AR_high >= AR_high_min)
    use_plat = (
        np.isfinite(AR_plateau)
        and (AR_plateau > AR_low_max)
        and (AR_plateau < AR_high_min)
    )

    if use_low:
        return "low"
    if use_high:
        return "high"
    return "plateau"


# Create a unified pressure span for this temperature (covering the experimental range)
Pmin = max(np.nanmin(np.asarray(pressures, dtype=float)), 1e-12)
Pmax = np.nanmax(np.asarray(pressures, dtype=float))
if np.isfinite(Pmin) and np.isfinite(Pmax) and Pmax > Pmin:
    P_line = np.logspace(np.log10(Pmin), np.log10(Pmax), 400)
else:
    # Fallback to a reasonable span around p0 if experimental range is odd
    p0_T = float(p0_lim_func(temperature))
    P_line = np.logspace(np.log10(max(p0_T / 10.0, 1e-12)), np.log10(p0_T * 10.0), 400)

# Compute fits on their natural domains
p0_T = float(p0_lim_func(temperature))
AR_low_line = np.full_like(P_line, np.nan, dtype=float)
AR_high_line = np.full_like(P_line, np.nan, dtype=float)
AR_plateau_line = np.full_like(P_line, np.nan, dtype=float)

# Low-branch (domain)
mask_low_domain = (P_line / p0_T) < tolerance
AR_low_line[mask_low_domain] = atom_ratio_eq_lower_func(
    temperature, P_line[mask_low_domain]
)

# Plateau branch (defined for all P, will be clipped by AR thresholds)
AR_plateau_line[:] = atom_ratio_plateau_region_fit(temperature, P_line)

# High-branch (domain)
mask_high_domain = (P_line / p0_T) > tolerance
AR_high_line[mask_high_domain] = atom_ratio_eq_upper_func(
    temperature, P_line[mask_high_domain]
)

# Thresholds for switching
AR_low_max = ar_max_low_p(temperature)  # upper bound for low branch
AR_high_min = 1.0  # lower bound for high branch

# Apply switching by AR thresholds (and domains) on line spans
mask_low_use = np.isfinite(AR_low_line) & (AR_low_line <= AR_low_max)
mask_plat_use = (
    np.isfinite(AR_plateau_line)
    & (AR_plateau_line > AR_low_max)
    & (AR_plateau_line < AR_high_min)
)
mask_high_use = np.isfinite(AR_high_line) & (AR_high_line >= AR_high_min)

# --- Also compute switching masks on the experimental data, for RMSE ---
pred_low_data = atom_ratio_eq_lower_func(temperature, pressures_arr)
pred_high_data = atom_ratio_eq_upper_func(temperature, pressures_arr)
pred_plateau_data = atom_ratio_plateau_region_fit(temperature, pressures_arr)

mask_low_use_data = (
    np.isfinite(pred_low_data)
    & ((pressures_arr / p0_T) < tolerance)
    & (pred_low_data <= AR_low_max)
)
mask_high_use_data = (
    np.isfinite(pred_high_data)
    & ((pressures_arr / p0_T) > tolerance)
    & (pred_high_data >= AR_high_min)
)
mask_plat_use_data = (
    np.isfinite(pred_plateau_data)
    & (pred_plateau_data > AR_low_max)
    & (pred_plateau_data < AR_high_min)
)

# --- RMSEs computed with the same switch (on EXP points) ---
RMSE_low = np.nan
RMSE_high = np.nan
if np.any(mask_low_use_data):
    RMSE_low = np.sqrt(
        np.mean(
            (atom_ratios_arr[mask_low_use_data] - pred_low_data[mask_low_use_data]) ** 2
        )
    )
    RMSE_values_low[temperature] = RMSE_low
if np.any(mask_high_use_data):
    RMSE_high = np.sqrt(
        np.mean(
            (atom_ratios_arr[mask_high_use_data] - pred_high_data[mask_high_use_data])
            ** 2
        )
    )
    RMSE_values_high[temperature] = RMSE_high

# Plot the three segments (capture handles for legend)
# CHANGED: swapped axes in both plot calls — x=AR_*_line, y=P_line
ln_lo = ln_plat = ln_hi = None
if np.any(mask_low_use):
    (ln_lo,) = plt.plot(
        AR_low_line[mask_low_use],
        P_line[mask_low_use],
        color=color_T,
        linestyle="--",
        linewidth=1.8,
        label=(
            f"{temperature} K Low P Fit RMSE {RMSE_low:.2f}"
            if np.isfinite(RMSE_low)
            else f"{temperature} K Low P Fit RMSE n/a"
        ),
    )
if np.any(mask_high_use):
    (ln_hi,) = plt.plot(
        AR_high_line[mask_high_use],
        P_line[mask_high_use],
        color=color_T,
        linestyle="-",
        linewidth=1.8,
        label=(
            f"{temperature} K High P Fit RMSE {RMSE_high:.2f}"
            if np.isfinite(RMSE_high)
            else f"{temperature} K High P Fit RMSE n/a"
        ),
    )

# Collect handles for legends (respect your grouping scheme)
if ln_hi is not None:
    high_fit_handles.append(ln_hi)
    high_fit_labels.append(
        f"{temperature} K High P Fit RMSE {RMSE_high:.2f}"
        if np.isfinite(RMSE_high)
        else f"{temperature} K High P Fit RMSE n/a"
    )

if ln_plat is not None:
    plateau_fit_handles.append(ln_plat)
    plateau_fit_labels.append(f"{temperature} K Plateau Fit")

if ln_lo is not None:
    low_fit_handles.append(ln_lo)
    low_fit_labels.append(
        f"{temperature} K Low P Fit RMSE {RMSE_low:.2f}"
        if np.isfinite(RMSE_low)
        else f"{temperature} K Low P Fit RMSE n/a"
    )

# -------------------- TMAP8 predictions: classify by the same switch --------------------
# NEW: distinct legend group for Plateau TMAP (to mirror the plateau fits group)
tmap_plat_handles, tmap_plat_labels = [], []


def add_tmap_point(T, P, xH):
    branch = select_branch(T, P)
    # Reference value from the proper branch
    if branch == "low":
        ref = atom_ratio_eq_lower_func(T, np.array([P]))[0]
        err = (
            (abs(xH - ref) / ref * 100.0)
            if (np.isfinite(ref) and ref != 0.0)
            else np.nan
        )
        # CHANGED: swapped axes — x=xH, y=P
        h = plt.scatter(xH, P, marker="*", color="k", s=90)
        tmap_low_handles.append(h)
        tmap_low_labels.append(
            f"{T} K and {P:.2f} Pa prediction (low-fit error: {err:.2f} %)"
            if np.isfinite(err)
            else f"{T} K and {P:.2f} Pa prediction (low-fit error: n/a)"
        )
    elif branch == "high":
        ref = atom_ratio_eq_upper_func(T, np.array([P]))[0]
        err = (
            (abs(xH - ref) / ref * 100.0)
            if (np.isfinite(ref) and ref != 0.0)
            else np.nan
        )
        # CHANGED: swapped axes — x=xH, y=P
        h = plt.scatter(xH, P, marker="x", color="k", s=90)
        tmap_high_handles.append(h)
        tmap_high_labels.append(
            f"{T} K and {P:.2f} Pa prediction (high-fit error: {err:.2f} %)"
            if np.isfinite(err)
            else f"{T} K and {P:.2f} Pa prediction (high-fit error: n/a)"
        )
    else:  # plateau
        ref = atom_ratio_plateau_region_fit(T, np.array([P]))[0]
        err = (
            (abs(xH - ref) / ref * 100.0)
            if (np.isfinite(ref) and ref != 0.0)
            else np.nan
        )
        # CHANGED: swapped axes — x=xH, y=P
        h = plt.scatter(xH, P, marker="o", color="k", s=90)
        tmap_plat_handles.append(h)
        tmap_plat_labels.append(
            f"{T} K and {P:.2f} Pa prediction (plateau-fit error: {err:.2f} %)"
            if np.isfinite(err)
            else f"{T} K and {P:.2f} Pa prediction (plateau-fit error: n/a)"
        )


# Existing specific TMAP8 points (auto-classified now)
add_tmap_point(
    TMAP8_prediction_T1273_P3e3_temperature,
    TMAP8_prediction_T1273_P3e3_pressure,
    TMAP8_prediction_T1273_P3e3_atomic_fraction,
)

add_tmap_point(
    TMAP8_prediction_T1173_P1e3_temperature,
    TMAP8_prediction_T1173_P1e3_pressure,
    TMAP8_prediction_T1173_P1e3_atomic_fraction,
)

add_tmap_point(
    TMAP8_prediction_T1173_P1e4_temperature,
    TMAP8_prediction_T1173_P1e4_pressure,
    TMAP8_prediction_T1173_P1e4_atomic_fraction,
)

add_tmap_point(
    TMAP8_prediction_T1173_P5e4_temperature,
    TMAP8_prediction_T1173_P5e4_pressure,
    TMAP8_prediction_T1173_P5e4_atomic_fraction,
)

# Existing low-predictions loop (also auto-classified; will fall into low/plateau/high groups as appropriate)
for item in low_predictions:
    T = item["T"]
    P = item["P"]
    xH = item["xH"]
    add_tmap_point(T, P, xH)

<<<<<<< HEAD
    label_txt = (
        f"{T} K and {P:.2f} Pa prediction (low-fit error: {err:.2f} %)"
        if np.isfinite(err)
        else f"{T} K and {P:.2f} Pa prediction (low-fit error: n/a)"
    )
    h = plt.scatter(P, xH, marker="*", color="k", s=90)
    tmap_low_handles.append(h)
    tmap_low_labels.append(label_txt)
>>>>>>> fdf51b49 (Improvement to low pressure fit and corrections to python file)

plt.xlabel("Partial Pressure (Pa)")
plt.ylabel("Atom Ratio (-)")
plt.xscale("log")
<<<<<<< HEAD
plt.text(
    0.02,
    0.98,
    f"TMAP8 prediction RMSPE = {prediction_rmspe:.3f} %",
    transform=plt.gca().transAxes,
    va="top",
    bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "none"},
)
plt.legend(bbox_to_anchor=(1.1, 1.05))
=======
>>>>>>> fdf51b49 (Improvement to low pressure fit and corrections to python file)
=======
# CHANGED: swapped axis labels and moved log scale to y-axis
plt.xlabel("Atom Ratio (-)")
plt.ylabel("Pressure (Pa)")
plt.yscale("log")
>>>>>>> 2f64bdd9 (Including full ranges PCT modelling for YHx)
plt.grid(True)
plt.tight_layout()

# -------------------- Legend assembly (single column, ordered groups) --------------------
combined_handles = []
combined_labels = []

# 1) High Pressure: Data, then Fit
for h, l in zip(high_data_handles, high_data_labels):
    combined_handles.append(h)
    combined_labels.append(l)
for h, l in zip(high_fit_handles, high_fit_labels):
    combined_handles.append(h)
    combined_labels.append(l)

# NEW: Plateau region fits (distinct group, shown in between)
for h, l in zip(plateau_fit_handles, plateau_fit_labels):
    combined_handles.append(h)
    combined_labels.append(l)

# NEW: TMAP8 Plateau predictions (keep alongside plateau fits)
for h, l in zip(tmap_plat_handles, tmap_plat_labels):
    combined_handles.append(h)
    combined_labels.append(l)

# 2) TMAP8 High
for h, l in zip(tmap_high_handles, tmap_high_labels):
    combined_handles.append(h)
    combined_labels.append(l)

# 3) Low Pressure: Fit only (no Low Data legend)
for h, l in zip(low_fit_handles, low_fit_labels):
    combined_handles.append(h)
    combined_labels.append(l)

# 4) TMAP8 Low
for h, l in zip(tmap_low_handles, tmap_low_labels):
    combined_handles.append(h)
    combined_labels.append(l)

# Reserve a bit of margin on the right side for the outside legend
plt.subplots_adjust(right=0.78)

legend = plt.legend(
    combined_handles,
    combined_labels,
    ncols=1,
    loc="center left",  # anchor the center-left of the legend...
    bbox_to_anchor=(1.02, 0.5),  # ...just outside the axes at 102% x, 50% y
    fontsize=8,
    frameon=True,
    borderaxespad=0.0,  # reduce extra padding between axes and legend
)

plt.savefig("YHx_PCT_fit_2D.png", bbox_inches="tight", dpi=300)
plt.close(fig)

# print the High RMSE values for each temperature
print("temperatures (K) and RMSE High values: ", RMSE_values_high)

# print the average RMSE value
average_rmse = (
    np.mean(list(RMSE_values_high.values())) if len(RMSE_values_high) > 0 else np.nan
)
print(
    f"Average RMSE (High): {average_rmse:.2f}"
    if np.isfinite(average_rmse)
    else "Average RMSE (High): n/a"
)

# print the Low RMSE values for each temperature
print("temperatures (K) and RMSE Low values: ", RMSE_values_low)

# print the average RMSE value
average_rmse = (
    np.mean(list(RMSE_values_low.values())) if len(RMSE_values_low) > 0 else np.nan
)
print(
    f"Average RMSE (Low): {average_rmse:.2f}"
    if np.isfinite(average_rmse)
    else "Average RMSE (Low): n/a"
)


# ------------------------------------------------------------------------------
# Raw plot (experimental data only)
# ------------------------------------------------------------------------------

fig = plt.figure(figsize=(10, 6))

for i, expData in enumerate(list_expData):
    # Get temperature and (optional) color mapping if available
    T = expData["Temperature (K)"].iloc[0]
    try:
        color_T = color_for_T(T, i)  # uses the temp-color palette if defined earlier
    except NameError:
        color_T = None  # fallback: let Matplotlib choose default colors

    # Scatter (Atom Ratio vs Partial Pressure) and connecting line
    x = expData["Atom Ratio (-)"].values
    y = expData["Partial Pressure (Pa)"].values

    plt.scatter(x, y, s=16, label=f"{int(T)} K", color=color_T)
    plt.plot(x, y, color=color_T)

plt.yscale("log")
plt.xlabel("Atom Ratio (-)")
plt.ylabel("Pressure (Pa)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("YHx_PCT_Data.png", dpi=300)
plt.close(fig)

# ------------------------------------------------------------------------------
# Raw plot (experimental data as solid lines) + Ar_Max_Low_P(T) dashed line
# + Ar_Min_High_P(T) dashed line, with two legends:
#   - temperature legend outside-top
#   - fit legend inside
# ------------------------------------------------------------------------------

fig = plt.figure(figsize=(10, 6))
ax = plt.gca()


# --- Provided low-pressure AR limit function ---
def ar_max_low_p(T):
    """
    Temperature-dependent maximum atom ratio for the low-pressure branch:
    Ar_Max_Low_P(T) = 1.01e-6 * T^2 - 2.55e-3 * T + 2.156
    """
    T = float(T)
    return 1.01e-6 * (T**2) - 2.55e-3 * T + 2.156


# --- Provided high-pressure AR minimum function ---
def ar_min_high_p(T):
    """
    Temperature-dependent minimum atom ratio for the high-pressure branch:
    Ar_Min_High_P(T) = -1.01e-6 * T^2 + 2.55e-3 * T - 0.5616
    """
    T = float(T)
    return -1.01e-6 * (T**2) + 2.55e-3 * T - 0.5616


# Collect for dashed lines (x: atom ratio threshold, y: plateau pressure)
ar_max_x, ar_max_y, temp_order = [], [], []
ar_min_x, ar_min_y = [], []

# Collect temperature plot handles for the outside legend
temp_handles, temp_labels = [], []

for i, expData in enumerate(list_expData):
    # Temperature and color
    T = float(expData["Temperature (K)"].iloc[0])
    try:
        color_T = color_for_T(T, i)  # if defined earlier
    except NameError:
        color_T = None

    # Experimental curves: Atom Ratio vs Partial Pressure (lines only)
    x = expData["Atom Ratio (-)"].values.astype(float)
    y = expData["Partial Pressure (Pa)"].values.astype(float)

    # Plot experimental as solid lines (no scatter)
    (ln_temp,) = ax.plot(x, y, color=color_T, linewidth=1.8, label=f"{int(T)} K")
    temp_handles.append(ln_temp)
    temp_labels.append(f"{int(T)} K")

    # Build dashed line points for this temperature
    # Use the same plateau pressure fit (p0_lim_func) for the y-values
    p0_T = float(p0_lim_func(T))
    ar_max_x.append(ar_max_low_p(T))
    ar_max_y.append(p0_T)

    ar_min_x.append(ar_min_high_p(T))
    ar_min_y.append(p0_T)

    temp_order.append(T)

# Sort dashed lines by temperature to ensure clean curves
order = np.argsort(np.array(temp_order))
ar_max_x = np.array(ar_max_x)[order]
ar_max_y = np.array(ar_max_y)[order]
ar_min_x = np.array(ar_min_x)[order]
ar_min_y = np.array(ar_min_y)[order]

# Plot the dashed lines
(ar_max_handle,) = ax.plot(
    ar_max_x,
    ar_max_y,
    linestyle="--",
    color="k",
    linewidth=1.6,
    label="Fitted Maximum Atomic Ratio in the Low‑Pressure Regime",
)
(ar_min_handle,) = ax.plot(
    ar_min_x,
    ar_min_y,
    linestyle="--",
    color="purple",
    linewidth=1.6,
    label="Fitted Minimum Atomic Ratio in the High‑Pressure Regime",
)

# Axes formatting
ax.set_yscale("log")
ax.set_xlabel("Atom Ratio (-)")
ax.set_ylabel("Pressure (Pa)")
ax.grid(True, which="both", linestyle=":", alpha=0.6)

# -------------------- Legends --------------------
# 1) Outside-top temperature legend (use fig.legend and leave margin at top)
ncols_temp = min(len(temp_handles), 5)  # choose a sensible number of columns
legend_temp = fig.legend(
    temp_handles,
    temp_labels,
    ncols=ncols_temp,
    loc="upper center",
    bbox_to_anchor=(0.5, 1.06),
    fontsize=9,
    frameon=True,
)

# Make room at the top for the outside legend
plt.tight_layout(rect=[0, 0, 1, 0.94])

# 2) Inside axes legend for both dashed fits
legend_ar = ax.legend(
    handles=[ar_max_handle, ar_min_handle],
    labels=[
        "Fitted Maximum Atomic Ratio in the Low‑Pressure Regime",
        "Fitted Minimum Atomic Ratio in the High‑Pressure Regime",
    ],
    loc="best",
    fontsize=9,
    frameon=True,
)

# --- Annotate the equations on the axes (top-left corner) ---
eqn_max = r"Ar$_{\rm Max,LowP}$(T) = 1.01×10$^{-6}$·T$^2$ − 2.55×10$^{-3}$·T + 2.156"
eqn_min = r"Ar$_{\rm Min,HighP}$(T) = −1.01×10$^{-6}$·T$^2$ + 2.55×10$^{-3}$·T − 0.5616"
ax.text(0.02, 0.97, eqn_max, transform=ax.transAxes, fontsize=9, va="top", color="k")
ax.text(
    0.02, 0.90, eqn_min, transform=ax.transAxes, fontsize=9, va="top", color="purple"
)

# Save
plt.savefig("YHx_PCT_Plateau_EndPoints_comparison.png", dpi=300, bbox_inches="tight")
plt.close(fig)


# ------------------------------------------------------------------------------
#                   PLOTTING THE PLATEAU REGION FIT VERSUS PCT DATA
# ------------------------------------------------------------------------------
import numpy as np
import matplotlib.pyplot as plt


# --- Plateau-region log-linear fit (your function) ---
def atom_ratio_plateau_region_fit(T, P):
    T = float(T)
    p0 = float(p0_lim_func(T))  # plateau pressure reference
    denom = max(tolerance * p0, 1e-20)
    arg = np.maximum(np.asarray(P, dtype=float) / denom, 1e-12)
    return (1.325 - 2.177e-04 * T) + (3.495 - 1.44e-03 * T) * np.log(arg)


# ---------------------- Compute AR bounds ----------------------------

# Use the minimum temperature across datasets for the lower bound
all_T = [float(expData["Temperature (K)"].iloc[0]) for expData in list_expData]
min_T = float(np.min(all_T))
max_T = float(np.max(all_T))
ar_lower = float(ar_max_low_p(min_T))
ar_upper = float(ar_min_high_p(max_T))

# ---------------------- Plotting ----------------------------

fig, ax = plt.subplots(figsize=(10, 8))

full_color = (0.55, 0.55, 0.55, 0.30)
fit_linewidth = 2.2

for i, expData in enumerate(list_expData):

    T = float(expData["Temperature (K)"].iloc[0])

    try:
        color_T = color_for_T(T, i)
    except NameError:
        color_T = None

    # --- Experimental data (scatter) UNCHANGED ---
    AR = expData["Atom Ratio (-)"].values.astype(float)
    P = expData["Partial Pressure (Pa)"].values.astype(float)
    ax.scatter(AR, P, s=10, alpha=full_color[3], color=full_color[:3])

    # --- Fitted curve (plateau-region model), CLIPPED to [ar_lower, ar_upper] ---
    p0_T = float(p0_lim_func(T))

    # Pressure span around p0(T); adjust factors to widen/narrow window if needed
    P_line = np.logspace(
        np.log10(max(p0_T / 2.5, 1e-12)), np.log10(max(p0_T * 2.5, 1e-12)), 400
    )

    AR_line = atom_ratio_plateau_region_fit(T, P_line)

    # Clip the fit curve to the requested AR range only
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


# ---------------------- Axes & styling ----------------------------
ax.set_yscale("log")
ax.set_ylabel("Pressure (Pa)")
ax.set_xlabel("Atom Ratio (–)")
ax.set_title(
    "Plateau-Region AR(P,T): Fit Curves Clipped to Specified AR Range\n(Experimental Data Unchanged)"
)
ax.grid(True, which="both", ls="--", alpha=0.4)

ax.legend(bbox_to_anchor=(1.04, 1.0), fontsize=9)
plt.tight_layout()

# --- Equation textbox (fit model) ---
eqn_text = (
    r"$\mathrm{AR}(P,T) = (1.325 - 2.177\times 10^{-4}\,T)"
    r" + (5.265 - 2.17\times 10^{-3}\,T)\,\ln\!\left(\frac{P}{1.10\,p_0(T)}\right)$"
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

# Save & show
plt.savefig("YHx_PCT_AR_plateau_fit.png", dpi=300, bbox_inches="tight")
plt.close(fig)


"""
• Plots exp scatter vs TMAP8 dashed
• Calculates MAPE on overlapping atomic‑ratio range
"""

from pathlib import Path

gold_dir = os.path.join(folderPath, "gold")

EPS = 1e-12


def compute_mape(ar_t, p_t, ar_e, p_e):
    # Sort the TMAP8 curve
    ar_t = ar_t[np.argsort(ar_t)]
    p_t = p_t[np.argsort(ar_t)]
    # Sort the Experimental curve
    ar_e = ar_e[np.argsort(ar_e)]
    p_e = p_e[np.argsort(p_e)]

    # Determine the overlapping x-range between the two curves
    lo = max(ar_e.min(), ar_t.min())
    hi = min(ar_e.max(), ar_t.max())

    # Keep only experimental points that fall within the overlapping range
    mask = (ar_e >= lo) & (ar_e <= hi)
    ar_e2 = ar_e[mask]
    p_e2 = p_e[mask]

    # Interpolate experimental curve values at the x-locations of TMAP8 curves
    p_interp = np.interp(ar_e2, ar_t, p_t)
    return np.mean(np.abs((p_interp - p_e2) / p_e2)) * 100


fig, ax = plt.subplots(figsize=(12, 8))


for i, Tk in enumerate(temperature_list):

    exp_subset = list_expData[i]  # get the correct experimental data

    ar_exp = exp_subset["Atom Ratio (-)"].to_numpy()
    p_exp = exp_subset["Partial Pressure (Pa)"].to_numpy()

    # Clean experimental arrays
    mask_e = np.isfinite(ar_exp) & np.isfinite(p_exp) & (p_exp > EPS)
    ar_exp, p_exp = ar_exp[mask_e], p_exp[mask_e]
    ord_e = np.argsort(ar_exp)
    ar_exp, p_exp = ar_exp[ord_e], p_exp[ord_e]

    # ---------------------------
    # Load TMAP8
    # ---------------------------
    tmap_name = f"YHx_PCT_Low_to_High_{int(Tk)}K.csv"
    tmap_path = os.path.join(gold_dir, tmap_name)
    df_tmap = pd.read_csv(tmap_path)

    ar_tmap = (
        df_tmap["atomic_fraction_H_enclosure_2_at_interface"].astype(float).to_numpy()
    )
    p_tmap = df_tmap["pressure_H2_enclosure_1_at_interface"].astype(float).to_numpy()

    mask = np.isfinite(ar_tmap) & np.isfinite(p_tmap) & (p_tmap > 1e-12)
    ar_tmap = ar_tmap[mask]
    p_tmap = p_tmap[mask]

    # ---------------------------
    # MAPE
    # ---------------------------
    mape = compute_mape(ar_tmap, p_tmap, ar_exp, p_exp)

    # --- Plot ---
    ax.scatter(ar_exp, p_exp, s=28, label=f"Exp {int(Tk)}.15 K")
    order = np.argsort(ar_tmap)
    ax.plot(
        ar_tmap[order],
        p_tmap[order],
        ls="--",
        lw=2.0,
        label=f"TMAP8 {int(Tk)}.15 K (err={mape:.2f}%)",
    )

# --- Finalize figure ---
ax.set_yscale("log")
ax.set_xlabel("Atom Ratio (–)")
ax.set_ylabel("Pressure (Pa)")
ax.grid(True, which="both", ls="--", alpha=0.6)
ax.legend(fontsize=9, loc="best", ncol=2)
fig.tight_layout()

fig.savefig("PCT_all_temperatures_experimental_vs_TMAP8_YHx.png", dpi=300)
plt.close(fig)

# print the RMSE values for each temperature
print("temperatures (K) and RMSE values: ", RMSE_values)

# print the average RMSE value
average_rmse = np.mean(list(RMSE_values.values()))
print(f"Average RMSE: {average_rmse:.2f}")
print(f"TMAP8 prediction RMSPE: {prediction_rmspe:.6f} %")
