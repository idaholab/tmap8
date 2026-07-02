import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
import pandas as pd
from scipy import special
from scipy.integrate import quad
import os

# Changes working directory to script directory (for consistent MooseDocs usage)
script_folder = os.path.dirname(__file__)
os.chdir(script_folder)

# ===============================================================================


def analytical_solution_temperature(
    LHR,
    fuel_radius,
    gap_thickness,
    clad_thickness,
    k_fuel,
    k_clad,
    gap_conductance,
    water_htc,
    coolant_temperature,
    location,
):
    """
    Analytical solution for temperature profile to couple to diffusion with Soret effect.

    Solve steady state heat transfer equations for radial heat transfer across the center of a
    fuel pin with gap, cladding and water coolant

    Args:
        LHR (float): Linear heating rate in W/m
        fuel_radius (float): radius of the fuel pin in meters
        gap_thickness (float): thickness of the gap in meters
        clad_thickness (float): thickness of the cladding in meters
        k_fuel (float): Thermal conductivity of the fuel in W/m/K
        k_clad (float): Thermal conductivity of the cladding in W/m/K
        gap_conductance (float): Conductance through the gap (constant) in W/m^2/K
        water_htc (float): Heat transfer coefficient of the coolant water in W/m^2/K
        coolant_temperature (float): Bulk temperature of the coolant water in K
        location (float): Location on the line across the fuel pin, between 0 and fuel_radius in m

    Returns:
        float: Steady state temperature at given location(s) in K
    """
    r_gap_outer = fuel_radius + gap_thickness
    r_clad_outer = r_gap_outer + clad_thickness

    # thermal resistances
    R_gap = 1.0 / (2 * np.pi * fuel_radius * gap_conductance)
    R_clad = np.log(r_clad_outer / r_gap_outer) / (2 * np.pi * k_clad)
    R_cool = 1.0 / (2 * np.pi * r_clad_outer * water_htc)

    T_center = (
        coolant_temperature
        + LHR * 100 * (R_gap + R_clad + R_cool)
        + LHR * 100 / (4 * np.pi * k_fuel)
    )
    A = LHR * 100 / (4 * np.pi * k_fuel * fuel_radius**2)
    T_of_x = T_center - A * location**2

    return T_of_x


def analytical_solution_ss_concentration(
    heat_of_transport,
    temperature_profile,
    initial_concentration,
    pin_radius,
    gas_constant,
    location,
):
    """
    Analytical solution of hydrogen diffusion with Soret effect.

    Solve steady state diffusion equation with Soret term across the center of a
    fuel pin, with an imposed temperature profile and initial uniform hydrogen distribution

    Args:
        heat_of_transport (float): heat of transport value for H in Zr in J/mol
        temperature_profile (function): function that fives the temperature in K as a function of x
        initial_concentration (float): initial uniform hydrogen concentration in terms of atom ratio H/M where M is the metal
        pin_radius (float): radius of the fuel pin in meters
        gas_constant (float): gas constant in J/mol/K
        location (float): Location on the line across the fuel pin, between 0 and fuel_radius in m

    Returns:
        float: Steady state temperature at given location(s) in K
    """

    # numerical integration for mass conservation normalization

    integrand = lambda x: x * np.exp(
        heat_of_transport / (gas_constant * temperature_profile(x))
    )

    norm, _ = quad(integrand, 0.0, pin_radius)

    c0 = (initial_concentration * 0.5 * pin_radius**2) / norm

    # steady state solution to diffusion equation: c0*e^(Q/RT)
    c_of_x_ss = c0 * np.exp(
        heat_of_transport / (gas_constant * temperature_profile(location))
    )

    return c_of_x_ss


# necessary parameters
fuel_radius = 0.005  # m
gap_thickness = 0.0001  # m
clad_thickness = 0.001  # m
k_fuel = 17.6  # W/m/K
k_clad = 16.5  # W/m/K
gap_conductance = 7.381e3  # W/m^2/K
water_htc = 18000  # W/m^2/K
coolant_temperature = 563.15  # K
heat_of_transport = 5.3e3  # J/mol
initial_concentration = 1.6  # H/M atom ratio
gas_constant = 8.31446261815324  # J/mol/K
LHRs = [150, 200, 250, 300]  # W/cm
locations = np.linspace(0, fuel_radius, 101)  # m

# Steady state concentration profiles
if "/tmap8/doc/" in script_folder.lower():  # if in documentation folder
    huang_csv = f"../../../../test/tests/ver-1m/gold/ver-1m_huang_ss_data.csv"
else:  # if in test folder
    huang_csv = f"./gold/ver-1m_huang_ss_data.csv"

huang_df = pd.read_csv(huang_csv)

fig = plt.figure(figsize=(10, 8))
gs = gridspec.GridSpec(2, 2, wspace=0.25, hspace=0.25)
axes = [fig.add_subplot(gs[i]) for i in range(4)]
panel_labels = ["(a)", "(b)", "(c)", "(d)"]

for ax, LHR, label in zip(axes, LHRs, panel_labels):
    # TMAP8 data: Extract concentration at location data from 'gold' TMAP8 run
    if "/tmap8/doc/" in script_folder.lower():  # if in documentation folder
        csv_folder = f"../../../../test/tests/ver-1m/gold/ver-1m_out_{LHR}_end_hydrogen_profile.csv"
    else:  # if in test folder
        csv_folder = f"./gold/ver-1m_out_{LHR}_end_hydrogen_profile.csv"
    tmap8_prediction = pd.read_csv(csv_folder)
    tmap8_location = tmap8_prediction["x"].values
    tmap8_concentration = tmap8_prediction["hydrogen_concentration"].values

    # analytical solution: steady state concentration profile
    temperature_profile = lambda x: analytical_solution_temperature(
        LHR,
        fuel_radius,
        gap_thickness,
        clad_thickness,
        k_fuel,
        k_clad,
        gap_conductance,
        water_htc,
        coolant_temperature,
        x,
    )

    analytical_concentration = analytical_solution_ss_concentration(
        heat_of_transport,
        temperature_profile,
        initial_concentration,
        fuel_radius,
        gas_constant,
        locations,
    )

    # Plot comparison of TMAP8 vs analytical solution: concentration vs location
    ax.plot(tmap8_location * 1000, tmap8_concentration, label="TMAP8", c="tab:gray")
    ax.plot(
        locations * 1000, analytical_concentration, label="Analytical", c="k", ls="--"
    )
    ax.text(0.1, 1.685, label, fontsize=12, fontweight="bold")

    ax.set_title(f"LHR = {LHR} W/cm")
    ax.grid(which="major", color="0.65", linestyle="--", alpha=0.3)
    ax.minorticks_on()
    RMSE = np.sqrt(np.mean((tmap8_concentration - analytical_concentration) ** 2))
    RMSPE = RMSE * 100 / np.mean(analytical_concentration)
    ax.text(0.6, 1.6, "RMSPE = %.2f " % RMSPE + "%", fontweight="bold")

    ax.set_xlim(left=0)
    ax.set_xlim(right=5)
    ax.set_ylim(bottom=1.5)
    ax.set_ylim(top=1.7)

    # Add data from Huang et al. for comparison
    loc_col = f"Location_{LHR}"
    h_col = f"H_{LHR}"

    if loc_col in huang_df.columns and h_col in huang_df.columns:
        huang_loc = huang_df[loc_col].values
        huang_H = huang_df[h_col].values
        ax.plot(huang_loc, huang_H, c="red", lw=0.75, label="Huang")
    else:
        print(f"Warning: Huang columns missing for LHR = {LHR}")

fig.text(0.5, 0.04, "Distance from Pin Center (mm)", ha="center", fontsize=12)
fig.text(
    0.04,
    0.5,
    "Concentration (H/Zr Ratio)",
    va="center",
    rotation="vertical",
    fontsize=12,
)

handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 0.95))

plt.savefig(
    "ver-1m_comparison_analytical_concentration_location.png",
    bbox_inches="tight",
    dpi=300,
)
plt.close(fig)

# Steady state temperature profiles
fig = plt.figure(figsize=(10, 8))
gs = gridspec.GridSpec(2, 2, wspace=0.25, hspace=0.25)
axes = [fig.add_subplot(gs[i]) for i in range(4)]
panel_labels = ["(a)", "(b)", "(c)", "(d)"]

for ax, LHR, label in zip(axes, LHRs, panel_labels):
    # TMAP8 data: Extract concentration at location data from 'gold' TMAP8 run
    if "/tmap8/doc/" in script_folder.lower():  # if in documentation folder
        csv_folder = f"../../../../test/tests/ver-1m/gold/ver-1m_out_{LHR}_end_temperature_profile.csv"
    else:  # if in test folder
        csv_folder = f"./gold/ver-1m_out_{LHR}_end_temperature_profile.csv"
    tmap8_prediction = pd.read_csv(csv_folder)
    tmap8_location = tmap8_prediction["x"].values
    tmap8_temperature = tmap8_prediction["temperature"].values

    # analytical solution: steady state concentration profile
    temperature_profile = lambda x: analytical_solution_temperature(
        LHR,
        fuel_radius,
        gap_thickness,
        clad_thickness,
        k_fuel,
        k_clad,
        gap_conductance,
        water_htc,
        coolant_temperature,
        x,
    )

    # Plot comparison of TMAP8 vs analytical solution: concentration vs location
    ax.plot(tmap8_location * 1000, tmap8_temperature, label="TMAP8", c="tab:gray")
    ax.plot(
        locations * 1000,
        temperature_profile(locations),
        label="Analytical",
        c="k",
        ls="--",
    )
    ax.text(0.1, 930, label, fontsize=12, fontweight="bold")

    ax.set_title(f"LHR = {LHR} W/cm")
    ax.grid(which="major", color="0.65", linestyle="--", alpha=0.3)
    ax.minorticks_on()
    RMSE = np.sqrt(np.mean((tmap8_temperature - temperature_profile(locations)) ** 2))
    RMSPE = RMSE * 100 / np.mean(temperature_profile(locations))
    ax.text(0.6, 670, "RMSPE = %.2f " % RMSPE + "%", fontweight="bold")

    ax.set_xlim(left=0)
    ax.set_xlim(right=5)
    ax.set_ylim(bottom=650)
    ax.set_ylim(top=950)

fig.text(0.5, 0.04, "Distance from Pin Center (mm)", ha="center", fontsize=12)
fig.text(0.04, 0.5, "Temperature (K)", va="center", rotation="vertical", fontsize=12)

handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles, labels, loc="upper center", ncol=3, bbox_to_anchor=(0.5, 0.95))

plt.savefig(
    "ver-1m_comparison_analytical_temperature_location.png",
    bbox_inches="tight",
    dpi=300,
)
plt.close()
