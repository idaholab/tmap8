import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
from pathlib import Path

# Use larger fonts everywhere (~2x matplotlib default of 10) per reviewer request
plt.rcParams.update({'font.size': 15})

# Changes working directory to script directory (for consistent MooseDocs usage)
SCRIPT_FOLDER = Path(__file__).resolve().parent
os.chdir(str(SCRIPT_FOLDER))

# ===============================================================================
# Physical constants and material properties

HALF_LENGTH = 5.0e-3  # m, half-slab thickness (symmetry domain)
FULL_LENGTH = 10.0e-3  # m, full PCC slab thickness
SURFACE_TEMPERATURE = 773.0  # K, prescribed left-surface temperature
THERMAL_CONDUCTIVITY = 0.014  # W/m/K
SIGMA_REF = 1e-03  # S/m, electrical conductivity
VOLTAGE_TOTAL = 20.0  # V, voltage drop across the full 10 mm slab
DENSITY = 6.154e3  # kg/m^3
SPECIFIC_HEAT_MOLAR = 120.0  # J/mol/K
MOLAR_MASS_BCY20 = 283.42e-3  # kg/mol
NUM_SERIES_TERMS = 2000  # number of Fourier series terms for convergence
PROFILE_TIMES = (1000.0, 20000.0)  # s, output times for spatial profile comparison

SPECIFIC_HEAT = SPECIFIC_HEAT_MOLAR / MOLAR_MASS_BCY20  # J/kg/K
THERMAL_DIFFUSIVITY = THERMAL_CONDUCTIVITY / (DENSITY * SPECIFIC_HEAT)  # m^2/s
HEAT_SOURCE = SIGMA_REF * (VOLTAGE_TOTAL / FULL_LENGTH) ** 2  # W/m^3, uniform Joule source
LAMBDA_N = (np.arange(NUM_SERIES_TERMS, dtype=float) + 0.5) * np.pi  # eigenvalues: (n+1/2)*pi

# ===============================================================================
# Analytical solution functions


def get_analytical_solution(x_m, time_s):
    """Return the transient half-slab temperature profile in kelvin.

    x_m is measured from the prescribed-temperature surface at x = 0.
    """
    x_array = np.atleast_1d(np.asarray(x_m, dtype=float))
    if np.isscalar(time_s) and time_s <= 0.0:
        return np.full_like(x_array, SURFACE_TEMPERATURE)

    y = x_array / HALF_LENGTH
    fourier_number = THERMAL_DIFFUSIVITY * float(time_s) / HALF_LENGTH**2
    sine_term = np.sin(np.outer(LAMBDA_N, y))
    decay_term = np.exp(-(LAMBDA_N**2) * fourier_number)
    transient_sum = np.sum(
        sine_term * decay_term[:, np.newaxis] / (LAMBDA_N[:, np.newaxis] ** 3),
        axis=0,
    )
    temperature_rise = (
        HEAT_SOURCE
        * HALF_LENGTH**2
        / THERMAL_CONDUCTIVITY
        * (y - 0.5 * y**2 - 2.0 * transient_sum)
    )
    return SURFACE_TEMPERATURE + temperature_rise


def get_analytical_delta_t_history(time_s):
    """Return the maximum temperature rise history at the insulated face x = L."""
    times = np.asarray(time_s, dtype=float)
    delta_t = np.zeros_like(times)
    positive_mask = times > 0.0
    if not np.any(positive_mask):
        return delta_t

    fourier_numbers = THERMAL_DIFFUSIVITY * times[positive_mask] / HALF_LENGTH**2
    sine_at_right = np.sin(LAMBDA_N)
    decay_term = np.exp(-np.outer(LAMBDA_N**2, fourier_numbers))
    transient_sum = np.sum(
        sine_at_right[:, np.newaxis] * decay_term / (LAMBDA_N[:, np.newaxis] ** 3),
        axis=0,
    )
    delta_t[positive_mask] = (
        HEAT_SOURCE
        * HALF_LENGTH**2
        / THERMAL_CONDUCTIVITY
        * (0.5 - 2.0 * transient_sum)
    )
    return delta_t

# ===============================================================================
# Extract TMAP8 results

if "/tmap8/doc/" in str(SCRIPT_FOLDER).lower():  # if in documentation folder
    results_folder = (SCRIPT_FOLDER / "../../../../test/tests/ver-1o/gold").resolve()
else:  # if in test folder
    results_folder = SCRIPT_FOLDER / "gold"

# one CSV per profile time, named by sync time and timestep index
profile_csvs = {
    t: next(results_folder.glob(f"ver-1o_vector_postproc_{int(t)}s_line_*.csv"))
    for t in PROFILE_TIMES
}

# time-history postprocessor output
time_data = pd.read_csv(results_folder / "ver-1o_out.csv")
time_history = time_data["time"].to_numpy(dtype=float)
tmap_delta_t_history = (
    time_data["delta_T"].to_numpy(dtype=float)
    if "delta_T" in time_data
    else time_data["temperature_max"].to_numpy(dtype=float) - SURFACE_TEMPERATURE
)

# ===============================================================================
# Compute RMSPE for temperature-rise history

analytical_delta_t_history = get_analytical_delta_t_history(time_history)
history_mask = time_history > 0.0
history_rmse = np.sqrt(
    np.mean((tmap_delta_t_history[history_mask] - analytical_delta_t_history[history_mask]) ** 2)
)
history_rmspe = history_rmse * 100.0 / np.mean(analytical_delta_t_history[history_mask])

# print(f"Using results folder: {results_folder}")
# print(f"Time-history RMSPE = {history_rmspe:.4f} %")
# for time_s in PROFILE_TIMES:
#     line_csv = profile_csvs[time_s]
#     line_data = pd.read_csv(line_csv)
#     x_m = line_data["x"].to_numpy(dtype=float) * 1e-6
#     tmap_temperature = line_data["temperature"].to_numpy(dtype=float)
#     analytical_temperature = get_analytical_solution(x_m, time_s)
#     rmse = np.sqrt(np.mean((tmap_temperature - analytical_temperature) ** 2))
#     rmspe = rmse * 100.0 / np.mean(analytical_temperature)
#     print(f"Profile RMSPE at t = {time_s:.0f} s: {rmspe:.4f} % ({line_csv.name})")

# ===============================================================================
# Plot temperature-rise history

fig, ax_history = plt.subplots(figsize=(6.5, 5.5))
ax_history.plot(
    time_history[history_mask],
    tmap_delta_t_history[history_mask],
    label="TMAP8",
    c="tab:gray",
    linewidth=2,
)
ax_history.plot(
    time_history[history_mask],
    analytical_delta_t_history[history_mask],
    linestyle="--",
    label="Analytical",
    c="k",
    linewidth=2,
)
ax_history.set_xscale("log")
ax_history.set_xlabel("Time (s)", fontsize=15)
ax_history.set_ylabel(r"$\Delta T_{\max}$ (K)", fontsize=15)
ax_history.set_ylim(bottom=0)
ax_history.set_xlim(left=1)
ax_history.legend(loc="lower right", fontsize=15)
ax_history.grid(visible=True, which="major", color="0.65", linestyle="--", alpha=0.3)
ax_history.text(
    0.03,
    0.93,
    f"RMSPE = {history_rmspe:.2f} %",
    transform=ax_history.transAxes,
    fontweight="bold",
    fontsize=15,
    va="top",
)
ax_history.minorticks_on()
plt.tight_layout()
plt.savefig("ver-1o_comparison_temperature_history.png", bbox_inches="tight", dpi=300)
plt.close(fig)

# ===============================================================================
# Plot spatial temperature profiles at selected times

fig, ax_profiles = plt.subplots(figsize=(6.5, 5.5))
profile_colors = {1000.0: "C0", 20000.0: "C1"}
for time_s in PROFILE_TIMES:
    line_csv = profile_csvs[time_s]
    line_data = pd.read_csv(line_csv)
    x_m = line_data["x"].to_numpy(dtype=float) * 1e-6
    tmap_temperature = line_data["temperature"].to_numpy(dtype=float)
    analytical_temperature = get_analytical_solution(x_m, time_s)
    rmse = np.sqrt(np.mean((tmap_temperature - analytical_temperature) ** 2))
    rmspe = rmse * 100.0 / np.mean(analytical_temperature)
    x_mm = x_m * 1e3
    color = profile_colors[time_s]
    ax_profiles.plot(
        x_mm,
        tmap_temperature,
        label=f"TMAP8 {time_s:.0f} s",
        c=color,
        linewidth=2,
        alpha=0.5,
    )
    ax_profiles.plot(
        x_mm,
        analytical_temperature,
        label=f"Analytical {time_s:.0f} s",
        c=color,
        linestyle="--",
        linewidth=2,
    )
    # place RMSPE label near the right end of the curve, colored to match
    ax_profiles.text(
        x_mm[-1] * 0.85,
        (tmap_temperature[-1] + analytical_temperature[-1]) / 2 + 0.1,
        f"RMSPE = {rmspe:.2f} %",
        color=color,
        fontsize=15,
        fontweight="bold",
        ha="right",
        va="center",
    )

ax_profiles.set_xlabel("Location (mm)", fontsize=15)
ax_profiles.set_ylabel("Temperature (K)", fontsize=15)
ax_profiles.set_xlim(left=0.0, right=HALF_LENGTH * 1e3)
ax_profiles.set_ylim(bottom=771.7, top=777)
ax_profiles.grid(visible=True, which="major", color="0.65", linestyle="--", alpha=0.3)
ax_profiles.legend(loc=[0.3, 0.01], fontsize=15, ncol=1)
ax_profiles.minorticks_on()
plt.tight_layout()
plt.savefig("ver-1o_comparison_temperature_profiles.png", bbox_inches="tight", dpi=300)
plt.close(fig)
