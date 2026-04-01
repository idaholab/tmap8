# Import Required Libraries
# Import the necessary libraries, including pandas.

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from mpl_toolkits.mplot3d import Axes3D
import os

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


# ============================================================================ #
# Fit the high pressures as a function of temperature
def atom_ratio_eq_upper_func(temperature, pressure):
    return 2 - (
        1
        + np.exp(
            21.6
            - 0.0225 * temperature
            + (-0.0445 + 7.18 * 10 ** (-4) * temperature)
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
        return (1.01e-6 * np.square(T) - 2.55e-3 * T + 2.156) - 10 * (
            0.001 + np.exp(-50.0 + 5.73e-2 * T + (0.830 - 2.69e-3 * T) * np.log(arg))
        ) ** (-1)


# Read low-pressure TMAP8 outputs and compute analytical low-fit values
low_files = {
    "YHx_PCT_T1573_P5e3_out.csv",
    "YHx_PCT_T1473_P3e3_out.csv",
    "YHx_PCT_T1273_P3e2_out.csv",
    "YHx_PCT_T1573_P6e2_out.csv",
}

low_predictions = []  # store tuples for plotting later

for fname in low_files:
    df = pd.read_csv(csv_folder + fname)

    T = df["temperature"].iat[-1]
    P = df["pressure_H2_enclosure_1_at_interface"].iat[-1]
    xH = df["atomic_fraction_H_enclosure_2_at_interface"].iat[-1]

    xH_model_low = atom_ratio_eq_lower_func(T, P)

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

# ============================================================================ #
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


# ============================================================================ #
# Plot the experimental data, the fit, and the TMAP8 results on a 3D plot
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
tmap_high_handles, tmap_high_labels = [], []
tmap_low_handles, tmap_low_labels = [], []

for i, temperature in enumerate(temperature_list):
    # Extract the data points for the current temperature
    expData = list_expData[i]
    pressures = expData["Partial Pressure (Pa)"]
    atom_ratios = expData["Atom Ratio (-)"]

    # color by temperature
    color_T = color_for_T(temperature, i)

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

        # Plot the data points
        sc_hi = plt.scatter(
            pressures_upper,
            atom_ratios_upper,
            color=color_T,
            s=16,
        )
        high_data_handles.append(sc_hi)
        high_data_labels.append(f"{temperature} K Data")

        # Plot the fit function
        (ln_hi,) = plt.plot(
            pressures_upper,
            fit_values_upper,
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

    # Ensure we have arrays
    pressures_arr = np.asarray(pressures, dtype=float)
    atom_ratios_arr = np.asarray(atom_ratios, dtype=float)

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

        # Plot the lower data -- keep plotted, but do NOT include in legend
        plt.scatter(pressures_lower, atom_ratios_lower, color=color_T, s=16)

        # Plot the lower fit -- dashed style + color and collect handle
        (ln_lo,) = plt.plot(
            pressures_lower,
            fit_values_lower,
            color=color_T,
            linestyle="--",
            label=f"{temperature} K Low P Fit RMSE {RMSE:.2f}",
        )

        # Include RMSE in low fit legend ordering
        low_fit_handles.append(ln_lo)
        low_fit_labels.append(f"{temperature} K Low P Fit RMSE {RMSE:.2f}")
# plot the TMAP8 predictions
error = (
    abs(
        TMAP8_prediction_T1273_P3e3_atomic_fraction
        - analytical_equation_T1273_P3e3_atomic_fraction
    )
    / analytical_equation_T1273_P3e3_atomic_fraction
    * 100
)
h = plt.scatter(
    TMAP8_prediction_T1273_P3e3_pressure,
    TMAP8_prediction_T1273_P3e3_atomic_fraction,
    marker="x",
    color="k",
    s=90,
)
tmap_high_handles.append(h)
tmap_high_labels.append(
    f"{TMAP8_prediction_T1273_P3e3_temperature} K and {TMAP8_prediction_T1273_P3e3_pressure:.2f} Pa prediction (high-fit error: {error:.2f} %)"
)

error = (
    abs(
        TMAP8_prediction_T1173_P1e3_atomic_fraction
        - analytical_equation_T1173_P1e3_atomic_fraction
    )
    / analytical_equation_T1173_P1e3_atomic_fraction
    * 100
)
h = plt.scatter(
    TMAP8_prediction_T1173_P1e3_pressure,
    TMAP8_prediction_T1173_P1e3_atomic_fraction,
    marker="x",
    color="k",
    s=90,
)
tmap_high_handles.append(h)
tmap_high_labels.append(
    f"{TMAP8_prediction_T1173_P1e3_temperature} K and {TMAP8_prediction_T1173_P1e3_pressure:.2f} Pa prediction (high-fit error: {error:.2f} %)"
)

error = (
    abs(
        TMAP8_prediction_T1173_P1e4_atomic_fraction
        - analytical_equation_T1173_P1e4_atomic_fraction
    )
    / analytical_equation_T1173_P1e4_atomic_fraction
    * 100
)
h = plt.scatter(
    TMAP8_prediction_T1173_P1e4_pressure,
    TMAP8_prediction_T1173_P1e4_atomic_fraction,
    marker="x",
    color="k",
    s=90,
)
tmap_high_handles.append(h)
tmap_high_labels.append(
    f"{TMAP8_prediction_T1173_P1e4_temperature} K and {TMAP8_prediction_T1173_P1e4_pressure:.2f} Pa prediction (high-fit error: {error:.2f} %)"
)

error = (
    abs(
        TMAP8_prediction_T1173_P5e4_atomic_fraction
        - analytical_equation_T1173_P5e4_atomic_fraction
    )
    / analytical_equation_T1173_P5e4_atomic_fraction
    * 100
)
h = plt.scatter(
    TMAP8_prediction_T1173_P5e4_pressure,
    TMAP8_prediction_T1173_P5e4_atomic_fraction,
    marker="x",
    color="k",
    s=90,
)
tmap_high_handles.append(h)
tmap_high_labels.append(
    f"{TMAP8_prediction_T1173_P5e4_temperature} K and {TMAP8_prediction_T1173_P5e4_pressure:.2f} Pa prediction (high-fit error: {error:.2f} %)"
)

# plot low-pressure TMAP8 predictions using the lower fit with star marker and collect handles
for item in low_predictions:
    T = item["T"]
    P = item["P"]
    xH = item["xH"]
    err = item["error_pct"]

    label_txt = (
        f"{T} K and {P:.2f} Pa prediction (low-fit error: {err:.2f} %)"
        if np.isfinite(err)
        else f"{T} K and {P:.2f} Pa prediction (low-fit error: n/a)"
    )
    h = plt.scatter(P, xH, marker="*", color="k", s=90)
    tmap_low_handles.append(h)
    tmap_low_labels.append(label_txt)

plt.xlabel("Partial Pressure (Pa)")
plt.ylabel("Atom Ratio (-)")
plt.xscale("log")
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
average_rmse = np.mean(list(RMSE_values_high.values()))
print(f"Average RMSE: {average_rmse:.2f}")


# print the Low RMSE values for each temperature
print("temperatures (K) and RMSE Low values: ", RMSE_values_low)

# print the average RMSE value
average_rmse = np.mean(list(RMSE_values_low.values()))
print(f"Average RMSE: {average_rmse:.2f}")


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
plt.ylabel("Partial Pressure (Pa)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("YHx_PCT_Data.png", dpi=300)
plt.close(fig)


# ------------------------------------------------------------------------------
# Raw plot (experimental data as solid lines) + Ar_Max_Low_P(T) dashed line
# with two legends: temperature legend outside-top, ar-max fit legend inside
# ------------------------------------------------------------------------------

fig = plt.figure(figsize=(10, 6))
ax = plt.gca()


# If not already defined earlier in your script:
def ar_max_low_p(T):
    """
    Temperature-dependent maximum atom ratio for the low-pressure branch:
    Ar_Max_Low_P(T) = 1.01e-6 * T^2 - 2.55e-3 * T + 2.156
    """
    T = float(T)
    return 1.01e-6 * (T**2) - 2.55e-3 * T + 2.156


# Collect for the dashed line (x: atom ratio threshold, y: plateau pressure)
ar_line_x, ar_line_y, temp_order = [], [], []

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

    # Build dashed line point for this temperature
    ar_line_x.append(ar_max_low_p(T))
    ar_line_y.append(float(p0_lim_func(T)))  # plateau pressure fit
    temp_order.append(T)

# Sort dashed line by temperature to ensure a clean curve
order = np.argsort(np.array(temp_order))
ar_line_x = np.array(ar_line_x)[order]
ar_line_y = np.array(ar_line_y)[order]

# Plot the dashed line (ar max vs plateau p0)
(ar_handle,) = ax.plot(
    ar_line_x,
    ar_line_y,
    linestyle="--",
    color="k",
    linewidth=1.6,
    label="Fitted Maximum Atomic Ratio in the Low‑Pressure Regime",
)

# Axes formatting
ax.set_yscale("log")
ax.set_xlabel("Atom Ratio (-)")
ax.set_ylabel("Partial Pressure (Pa)")
ax.grid(True)

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

# 2) Inside axes legend for the dashed Ar_Max_Low_P fit
legend_ar = ax.legend(
    handles=[ar_handle],
    labels=["Fitted Maximum Atomic Ratio in the Low‑Pressure Regime"],
    loc="best",
    fontsize=9,
    frameon=True,
)

# Save
plt.savefig("YHx_PCT_Data_Vs_ArMaxFit.png", dpi=300, bbox_inches="tight")
plt.close(fig)
