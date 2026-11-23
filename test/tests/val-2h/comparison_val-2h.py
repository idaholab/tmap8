import numpy as np
import pandas as pd
import os
from matplotlib import gridspec
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter

# Changes working directory to script directory (for consistent MooseDocs usage)
script_folder = os.path.dirname(__file__)
os.chdir(script_folder)

#===============================================================================
# Load experimental data

if "/tmap8/doc/" in script_folder.lower():  # if in documentation folder
    data_folder = "../../../../test/tests/val-2h/gold/"
else:                                       # if in test folder
    data_folder = "./gold/"
data_by_temperature = {}

#===============================================================================
# General parameters

R = 8.31446261815324 # J/mol/K ideal gas constant from PhysicalConstants.h
temperature = 973 # 823 # K
n_sieverts = 0.5 # Sieverts' law

#===============================================================================
# 1D case without any layer: Tritium permeation flux as a function of tritium partial pressure
# for a range of temperatures and initial pressures

fig = plt.figure(figsize=[6.5, 5.5])
gs = gridspec.GridSpec(1, 1)
ax = fig.add_subplot(gs[0])

for filename in os.listdir(data_folder):
    if filename.endswith(".csv") and filename.startswith("val-2h_1D_"):
        parts = filename.replace(".csv", "").split("_")
        try:
            T = int(parts[2][:-1])  # Remove 'K'
            P = int(parts[3][:-2])  # Remove 'Pa'
            df = pd.read_csv(os.path.join(data_folder, filename))
            average_flux = df["right_flux_membrane"].iloc[-1]
            data_by_temperature.setdefault(T, []).append((P, average_flux))
        except Exception as e:
            print(f"Skipping {filename}: {e}")

# Define consistent color and marker maps based on temperature in Celsius
temperatures_C = [550, 600, 650, 700]
temperature_color_map = {T: f"C{i}" for i, T in enumerate(temperatures_C)}
temperature_marker_map = {550: 'o', 600: 's', 650: 'D', 700: '^'}

# Experimental data
exp_data = pd.DataFrame({
    "pressure": [170, 316, 316, 538, 538, 538, 1210, 1210, 1210, 1210],
    "flux": np.array([
        1.0684039087947879,
        1.0423452768729637,
        2.0325732899022793,
        1.1465798045602602,
        1.745928338762214,
        2.866449511400651,
        3.6351791530944624,
        2.5146579804560254,
        1.7068403908794778,
        1.1596091205211714
    ]) * 1e-7,
    "temperature": [700, 650, 700, 600, 650, 700, 700, 650, 600, 550]
})

for T_C in reversed(sorted(exp_data["temperature"].unique())):
    subset = exp_data[exp_data["temperature"] == T_C]
    ax.scatter(
        subset["pressure"],
        subset["flux"],
        marker=temperature_marker_map[T_C],
        facecolors='none',
        edgecolors=temperature_color_map[T_C],
        label=f"{T_C} °C exp"
    )

# Plot TMAP8 data
for T in reversed(sorted(data_by_temperature.keys())):
    T_C = T - 273
    values = sorted(data_by_temperature[T])
    pressures, fluxes = zip(*values)
    ax.scatter(
        pressures,
        fluxes,
        marker=temperature_marker_map.get(T_C, 'x'),
        color=temperature_color_map.get(T_C, 'k'),
        label=f"{T_C} °C (TMAP8)"
    )

# Styling
ax.set_xlabel(r"$T_2$ partial pressure (Pa)")
ax.set_ylabel(r"Tritium molar flux (mol/m$^2$/s)")
ax.legend(loc="best")
ax.grid(which='major', color='0.65', linestyle='--', alpha=0.3)
fig.savefig('val-2h_tritium_flux_1D.png', bbox_inches='tight', dpi=300)

#===============================================================================
# 2D case with a Ni layer: Tritium permeation flux as a function of tritium partial pressure
# for a range of temperatures and initial pressures

data_density = {}  # from _out.csv
data_total = {}    # from _1D_*.csv

fig = plt.figure(figsize=[6.5, 5.5])
gs = gridspec.GridSpec(1, 1)
ax = fig.add_subplot(gs[0])

# Loop through files
for filename in os.listdir(data_folder):
    if filename.endswith(".csv") and filename.startswith("val-2h_"):
        try:
            parts = filename.replace(".csv", "").split("_")

            # Extract temperature and pressure from parts
            T = next(int(p[:-1]) for p in parts if p.endswith("K"))
            P = next(int(p[:-2]) for p in parts if p.endswith("Pa"))

            df = pd.read_csv(os.path.join(data_folder, filename))

            if "_1D_" in filename:
                flux = df["right_flux_membrane"].iloc[-1]
                data_total.setdefault(T, []).append((P, flux))

            elif filename.endswith("_out.csv"):
                flux = df["right_flux_density_membrane"].iloc[-1]
                data_density.setdefault(T, []).append((P, flux))

        except Exception as e:
            print(f"Skipping {filename}: {e}")

# Color and marker maps
temperatures_C = [550, 600, 650, 700]
temperature_color_map = {T: f"C{i}" for i, T in enumerate(temperatures_C)}
temperature_marker_map = {550: 'o', 600: 's', 650: 'D', 700: '^'}

# Experimental data
exp_data = pd.DataFrame({
    "pressure": [170, 316, 316, 538, 538, 538, 1210, 1210, 1210, 1210],
    "flux": np.array([
        1.0684039087947879,
        1.0423452768729637,
        2.0325732899022793,
        1.1465798045602602,
        1.745928338762214,
        2.866449511400651,
        3.6351791530944624,
        2.5146579804560254,
        1.7068403908794778,
        1.1596091205211714
    ]) * 1e-7,
    "temperature": [700, 650, 700, 600, 650, 700, 700, 650, 600, 550]
})

# Plot experimental
for T_C in reversed(sorted(exp_data["temperature"].unique())):
    subset = exp_data[exp_data["temperature"] == T_C]
    ax.scatter(
        subset["pressure"],
        subset["flux"],
        marker=temperature_marker_map[T_C],
        facecolors='none',
        edgecolors=temperature_color_map[T_C],
        label=f"{T_C} °C exp"
    )

# Plot _1D_ data (total flux)
for T in sorted(data_total.keys(), reverse=True):
    T_C = T - 273
    values = sorted(data_total[T])
    pressures, fluxes = zip(*values)
    ax.scatter(
        pressures,
        fluxes,
        marker=temperature_marker_map.get(T_C, 'x'),
        color=temperature_color_map.get(T_C, 'k'),
        alpha=0.5
    )

# Plot _out data (flux density)
for T in sorted(data_density.keys(), reverse=True):
    T_C = T - 273
    values = sorted(data_density[T])
    pressures, fluxes = zip(*values)
    ax.scatter(
        pressures,
        fluxes,
        marker=temperature_marker_map.get(T_C, 'x'),
        color=temperature_color_map.get(T_C, 'k'),
        label=f"{T_C} °C (TMAP8)"
    )

# Styling
ax.set_xlabel(r"$T_2$ partial pressure (Pa)")
ax.set_ylabel(r"Tritium molar flux (mol/m$^2$/s)")
ax.legend(loc="best")
ax.grid(which='major', color='0.65', linestyle='--', alpha=0.3)
fig.savefig('val-2h_tritium_flux_2D.png', bbox_inches='tight', dpi=300)

#===============================================================================
# 2D case without FLiBe: Tritium permeation flux as a function of tritium partial pressure
# for a range of temperatures and initial pressures

fig = plt.figure(figsize=[6.5, 5.5])
gs = gridspec.GridSpec(1, 1)
ax = fig.add_subplot(gs[0])
data_by_temperature_no_FLiBe = {}
for filename in os.listdir(data_folder):
    if filename.endswith(".csv") and "no_FLiBe" in filename and filename.startswith("val-2h_"):
        parts = filename.replace(".csv", "").split("_")
        try:
            # Extract temperature and pressure from parts ending with 'K' and 'Pa'
            T = next(int(p[:-1]) for p in parts if p.endswith("K"))
            P = next(int(p[:-2]) for p in parts if p.endswith("Pa"))

            df = pd.read_csv(os.path.join(data_folder, filename))
            average_flux = df["flux_density_right"].iloc[-1]
            data_by_temperature_no_FLiBe.setdefault(T, []).append((P, average_flux))

        except Exception as e:
            print(f"Skipping {filename}: {e}")

# Define consistent color and marker maps based on temperature in Celsius
temperatures_C = [550, 600, 650, 700]
temperature_color_map = {T: f"C{i}" for i, T in enumerate(temperatures_C)}
temperature_marker_map = {550: 'o', 600: 's', 650: 'D', 700: '^'}

# Experimental data
exp_data = pd.DataFrame({
    "pressure": [170, 316, 316, 538, 538, 538, 1210, 1210, 1210, 1210],
    "flux": np.array([
        1.0684039087947879,
        1.0423452768729637,
        2.0325732899022793,
        1.1465798045602602,
        1.745928338762214,
        2.866449511400651,
        3.6351791530944624,
        2.5146579804560254,
        1.7068403908794778,
        1.1596091205211714
    ]) * 1e-7,
    "temperature": [700, 650, 700, 600, 650, 700, 700, 650, 600, 550]
})

for T_C in reversed(sorted(exp_data["temperature"].unique())):
    subset = exp_data[exp_data["temperature"] == T_C]
    ax.scatter(
        subset["pressure"],
        subset["flux"],
        marker=temperature_marker_map[T_C],
        facecolors='none',
        edgecolors=temperature_color_map[T_C],
        label=f"{T_C} °C exp"
    )

# Plot TMAP8 data
for T in reversed(sorted(data_by_temperature_no_FLiBe.keys())):
    T_C = T - 273
    values = sorted(data_by_temperature_no_FLiBe[T])
    pressures, fluxes = zip(*values)
    ax.scatter(
        pressures,
        fluxes,
        marker=temperature_marker_map.get(T_C, 'x'),
        color=temperature_color_map.get(T_C, 'k'),
        label=f"{T_C} °C (TMAP8)"
    )

# Styling
ax.set_xlabel(r"$T_2$ partial pressure (Pa)")
ax.set_ylabel(r"Tritium molar flux (mol/m$^2$/s)")
ax.legend(loc="best")
ax.grid(which='major', color='0.65', linestyle='--', alpha=0.3)
fig.savefig('val-2h_tritium_flux_2D_no_FLiBe.png', bbox_inches='tight', dpi=300)

#===============================================================================
# Mass conservation check

if "/tmap8/doc/" in script_folder.lower():  # if in documentation folder
    data_folder = "../../../../test/tests/val-2h/gold/val-2h_823K_1210Pa_out.csv"
else:                                       # if in test folder
    data_folder = "./gold/val-2h_823K_1210Pa_out.csv"
data_by_temperature = {}
# Load data
df = pd.read_csv(data_folder)

# Define start time to skip early points
start_time = 1000  # Adjust this as needed

# Extract relevant columns
time = df['time'].values
n = df['tritium_amount'].values
phi_in = - df['left_flux'].values
phi_right = df['right_flux'].values
phi_top = df['top_flux'].values
phi_out = phi_right + phi_top

# Compute dn/dt and time midpoints
dt = np.diff(time)
dn = np.diff(n)
dndt = dn / dt
time_mid = 0.5 * (time[1:] + time[:-1])

# Compute phi_in - phi_out and interpolate to time_mid
phi_balance = phi_in - phi_out
phi_balance_mid = 0.5 * (phi_balance[1:] + phi_balance[:-1])
phi_top_mid = 0.5 * (phi_top[1:] + phi_top[:-1])
phi_right_mid = 0.5 * (phi_right[1:] + phi_right[:-1])

# Filter based on start_time
mask = time_mid >= start_time
time_mid = time_mid[mask]
dndt = dndt[mask]
phi_balance_mid = phi_balance_mid[mask]
phi_top_mid = phi_top_mid[mask]
phi_right_mid = phi_right_mid[mask]

# Compute RMSE and RMSPE
rmse = np.sqrt(np.mean((dndt - phi_balance_mid) ** 2))
rmspe = rmse * 100 / np.mean(np.abs(dndt))

# Plotting
fig = plt.figure(figsize=[6.5, 5.5])
gs = gridspec.GridSpec(1, 1)
ax = fig.add_subplot(gs[0])

ax.plot(time_mid, dndt, label='dn/dt (mol/s)')
ax.plot(time_mid, phi_balance_mid, '--', label='flux_in - flux_out (mol/s)')
ax.plot(time_mid, phi_top_mid, ':', label='top_flux (mol/s)')
ax.plot(time_mid, phi_right_mid, ':', label='right_flux (mol/s)')


ax.set_xlabel('Time (s)')
ax.set_ylabel('Rate (mol/s)')
ax.legend()
ax.grid(which='major', color='0.65', linestyle='--', alpha=0.3)

# Add RMSPE annotation at right-middle
ax.text(0.95, 0.5, f'RMSPE = {rmspe:.2f} %', transform=ax.transAxes,
        fontsize=10, verticalalignment='center', horizontalalignment='right', fontweight='bold')

plt.tight_layout()
plt.savefig("val-2h_mass_conservation_2D_with_layer.png", dpi=300)
