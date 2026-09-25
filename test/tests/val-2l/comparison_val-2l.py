"""
This is the main comparison script for val-2l, and computes the following plots:

1: plot_temperature_history() shows the temperature profile over the entire time of experiment, as well as an inlet graph that zooms in on temperature anomolies observed during the experiment
2: plot_mass_conservation() shows the evolution of the mass conservation residual relative to the initial mass at the start of the TDS experiment
3: plot_inventory() shows the deuterium present in traps and as a mobile concentration
4: plot_unirradiated_desorption() plots the simulated against experimental desorbed flux from the upstream and downstream surfaces, performing RMSPE calculations to measure the goodness of fit
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import pandas as pd
import os

# Changes working directory to script directory (for consistent MooseDocs usage)
script_folder = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_folder)

# Geometry
disc_area = np.pi * (3e3) ** 2  # 6 mm diameter gives 3e3 mum radius

# ================================= Functions ================================ #


def read_csv_from_TMAP8(file_name, parameter_names):
    """Read simulation output columns from a gold CSV file into a numpy array

    Args:
        file_name (str): name of the CSV file in the gold directory
        parameter_names (list of str): column names to extract, in desired order

    Returns:
        ndarray: 2D array of shape (len(parameter_names), n_timesteps)
    """
    if "/tmap8/doc/" in script_folder.lower():  # if in documentation folder
        csv_folder = f"../../../../test/tests/val-2l/gold/{file_name}"
    else:  # if in test folder
        csv_folder = f"./{file_name}"
        # csv_folder = f"./gold/{file_name}"

    simulation_data = pd.read_csv(csv_folder)
    return np.array([simulation_data[name] for name in parameter_names])


def numerical_solution_on_experiment_input(experiment_input, tmap_input, tmap_output):
    """Get new numerical solution based on the experimental input data points

    Args:
        experiment_input (float, ndarray): experimental input data points
        tmap_input (float, ndarray): numerical input data points
        tmap_output (float, ndarray): numerical output data points

    Returns:
        float, ndarray: updated tmap_output based on the data points in experiment_input
    """
    new_tmap_output = np.zeros(len(experiment_input))
    for i in range(len(experiment_input)):
        left_limit = np.argwhere((np.diff(tmap_input < experiment_input[i])))[0][0]
        right_limit = left_limit + 1
        new_tmap_output[i] = (experiment_input[i] - tmap_input[left_limit]) / (
            tmap_input[right_limit] - tmap_input[left_limit]
        ) * (tmap_output[right_limit] - tmap_output[left_limit]) + tmap_output[
            left_limit
        ]
    return new_tmap_output


def compute_rmspe(simulated, reference):
    """Compute the Root Mean Square Percentage Error between two arrays

    Args:
        simulated (float, ndarray): simulated values
        reference (float, ndarray): reference values used as the denominator

    Returns:
        float: RMSPE in percent
    """
    RMSE = np.sqrt(np.mean((simulated - reference) ** 2))
    return RMSE * 100 / np.mean(reference)


def annotate_rmspe(simulated, reference, x_pos, y_pos):
    """Compute RMSPE and annotate it as bold text on the current matplotlib axes

    Args:
        simulated (float, ndarray): simulated values
        reference (float, ndarray): reference values used as the denominator
        x_pos (float): x-coordinate of the annotation
        y_pos (float): y-coordinate of the annotation
    """
    RMSPE = compute_rmspe(simulated, reference)
    plt.text(x_pos, y_pos, "RMSPE = %.2f %%" % RMSPE, fontweight="bold", color="blue")


def plot_temperature_history(
    simulation_file="val-2l_out.csv",
    filename="val-2l_temperature_history.png",
    zoom_end=350,
    zoom_ylim=(270, 370),
):
    """Plot the simulated temperature ramp versus time with a zoomed inset

    The inset is placed in the lower-right corner of the main axes and shows
    the first zoom_end seconds with fixed y-limits to highlight the early-time
    deviation from the analytic ramp.

    Args:
        simulation_file (str): TMAP8 CSV with "time" (s) and "temperature" (K) columns
        filename (str): output PNG filename
        zoom_end (float): upper time limit (s) for the inset
        zoom_ylim (tuple): (y_min, y_max) in K for the inset y-axis
    """
    time, temperature = read_csv_from_TMAP8(simulation_file, ["time", "temperature"])

    # ---- Full history ----
    fig, ax = plt.subplots(figsize=(6.5, 4.8))
    ax.plot(
        time,
        temperature,
        color="tab:red",
        linewidth=1.8,
        label="TMAP8 temperature ramp",
    )
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Temperature (K)")
    ax.set_xlim(0, time.max())
    ax.set_ylim(bottom=0)
    ax.grid(visible=True, which="major", color="0.65", linestyle="--", alpha=0.3)
    ax.set_title("Unirradiated Sample: TDS Temperature History")
    ax.minorticks_on()
    ax.legend()

    # ---- Inset: lower-right, first zoom_end seconds ----
    # Coordinates are in axes-fraction space: [left, bottom, width, height]
    ax_inset = ax.inset_axes([0.55, 0.05, 0.42, 0.42])
    mask = time <= zoom_end
    ax_inset.plot(time[mask], temperature[mask], color="tab:red", linewidth=1.2)
    ax_inset.set_xlim(0, zoom_end)
    ax_inset.set_ylim(*zoom_ylim)
    ax_inset.set_xlabel("Time (s)", fontsize=7)
    ax_inset.set_ylabel("Temperature (K)", fontsize=7)
    ax_inset.tick_params(labelsize=7)
    ax_inset.grid(visible=True, which="major", color="0.65", linestyle="--", alpha=0.3)

    plt.tight_layout()
    plt.savefig(filename, bbox_inches="tight", dpi=300)
    plt.close(fig)


def plot_mass_conservation(
    simulation_file="val-2l_out.csv",
    filename="val-2l_mass_conservation.png",
):
    """Plot the relative deuterium mass-balance residual over time

    The residual (inventory_change + released) is normalized by the initial inventory
    M(0) and should remain close to zero if mass is conserved (cf. val-2k Stage 6).

    Args:
        simulation_file (str): TMAP8 CSV with "time", "total_deuterium_retention", and
            "deuterium_mass_conservation_residual" columns
        filename (str): output PNG filename
    """
    time, total_retention, residual = read_csv_from_TMAP8(
        simulation_file,
        ["time", "total_deuterium_retention", "deuterium_mass_conservation_residual"],
    )
    initial_inventory = total_retention[0]
    relative_residual = residual / initial_inventory

    fig, ax = plt.subplots(figsize=(6.5, 4.8))
    ax.plot(time, relative_residual, color="tab:blue", linewidth=1.8)
    ax.axhline(0.0, color="0.35", linewidth=1.0, linestyle="--")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Deuterium mass-balance residual / initial inventory (-)")
    ax.set_xlim(0, time.max())
    ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    ax.grid(visible=True, which="major", color="0.65", linestyle="--", alpha=0.3)
    ax.minorticks_on()
    ax.set_title("Unirradiated Sample: Conservation of Mass")
    plt.tight_layout()
    plt.savefig(filename, bbox_inches="tight", dpi=300)
    plt.close(fig)


def plot_inventory(
    simulation_file="val-2l_out.csv",
    filename="val-2l_inventory.png",
):
    """Plot the stacked deuterium inventory (mobile + trapped) with temperature history

    The MOOSE postprocessors output surface densities (at/µm²). The mobile retention
    is converted to atoms by multiplying by disc_area. The trapped variable is stored
    rescaled by 1/trap_per_free in MOOSE, so it is multiplied by both trap_per_free
    and disc_area to recover the physical atom count.

    Args:
        simulation_file (str): TMAP8 CSV with "time", "temperature",
            "total_mobile_retention", and "total_trapped_retention" columns
        filename (str): output PNG filename
    """
    time, temperature, mobile_raw, trapped_raw, trap_per_free = read_csv_from_TMAP8(
        simulation_file,
        [
            "time",
            "temperature",
            "total_mobile_retention",
            "total_trapped_retention",
            "trap_per_free",
        ],
    )
    mobile = mobile_raw * disc_area
    trapped = trapped_raw * trap_per_free[0] * disc_area

    # Stacked bottom-up: largest / most stable contribution first
    inventory_series = [
        ("Trapped D (trap 1, 1.35 eV)", trapped, plt.get_cmap("viridis")(0.45)),
        ("Mobile D", mobile, plt.get_cmap("viridis")(0.95)),
    ]

    fig, ax = plt.subplots(figsize=(6.5, 5.5))
    bottom = np.zeros_like(time)
    legend_patches = []
    for label, values, color in inventory_series:
        ax.fill_between(time, bottom, bottom + values, color=color, alpha=0.3)
        ax.plot(time, bottom + values, color=color, linewidth=1.0)
        bottom = bottom + values
        legend_patches.append(Patch(color=color, alpha=0.5, label=label))

    total_handle = ax.plot(
        time, bottom, color="tab:green", linewidth=1.5, label="Total D inventory"
    )[0]

    ax_T = ax.twinx()
    temperature_handle = ax_T.plot(
        time,
        temperature,
        linestyle="-",
        color="k",
        linewidth=1.5,
        label="TMAP8 temperature history",
    )[0]

    ax.set_xlabel("Time (s)")
    ax.set_ylabel(r"Deuterium inventory (atoms)")
    ax.set_xlim(0, time.max())
    ax.set_ylim(bottom=0)
    ax.set_title("Unirradiated Sample: Deuterium Inventory")
    ax.grid(visible=True, which="major", color="0.65", linestyle="--", alpha=0.3)
    ax_T.set_ylabel("Temperature (K)")
    ax.legend(
        handles=[total_handle, temperature_handle] + legend_patches[::-1],
        loc="lower right",
    )
    ax.minorticks_on()
    plt.tight_layout()
    plt.savefig(filename, bbox_inches="tight", dpi=300)
    plt.close(fig)


def plot_unirradiated_desorption(
    experiment_file="unirradiated_data.csv",
    benchmark_file="tmap7_fit_a_data.csv",
    simulation_file="val-2l_out.csv",
    simulation_flux_column="deuterium_release_flux_total",
    comparison_plot="val-2l_comparison_desorption.png",
):
    """Plot the Shimada (2010) unirradiated desorption data against TMAP7 and TMAP8.

    Args:
        experiment_file (str): two-column CSV of experimental
            (time [s], desorbed flux [m^-2 s^-1])
        benchmark_file (str): two-column CSV of TMAP7 fit A
            (time [s], desorbed flux [m^-2 s^-1])
        simulation_file (str): TMAP8 CSV output holding "time" and
            the desorbed-flux column
        simulation_flux_column (str): name of the desorbed-flux column in
            simulation_file. TMAP8 reports it in at/µm^2/s; converted to at/m^2/s.
        comparison_plot (str): output PNG filename
    """

    experiment = np.loadtxt(experiment_file, skiprows=1, delimiter=",")
    experiment_time, experiment_flux = experiment[:, 0], experiment[:, 1]

    benchmark = np.loadtxt(benchmark_file, skiprows=1, delimiter=",")
    benchmark_time, benchmark_flux = benchmark[:, 0], benchmark[:, 1]

    simulation_time, simulation_flux = read_csv_from_TMAP8(
        simulation_file, ["time", simulation_flux_column]
    )
    simulation_flux = simulation_flux * 1e12  # at/µm^2/s -> at/m^2/s

    # Truncate experiment to simulation time range
    in_sim_range = experiment_time <= simulation_time.max()
    experiment_time = experiment_time[in_sim_range]
    experiment_flux = experiment_flux[in_sim_range]

    # Interpolate simulated flux at experimental time points for RMSPE
    mapped_simulation_flux = np.interp(
        experiment_time, simulation_time, simulation_flux
    )

    tmin, tmax = 500, 3000
    rmspe_region = (experiment_time >= tmin) & (experiment_time <= tmax)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(
        experiment_time,
        experiment_flux,
        "ko",
        label="Experiment (Shimada 2010, 0 dpa)",
    )
    ax.plot(
        benchmark_time,
        benchmark_flux,
        color="red",
        linestyle="--",
        label="TMAP7 fit A",
    )
    ax.plot(simulation_time, simulation_flux, "b-", label="TMAP8")

    if rmspe_region.any():
        ax.axvline(
            experiment_time[rmspe_region].min(),
            color="black",
            linestyle="--",
            linewidth=1.2,
            label="RMSPE region",
        )
        ax.axvline(
            experiment_time[rmspe_region].max(),
            color="black",
            linestyle="--",
            linewidth=1.2,
        )
        annotate_rmspe(
            mapped_simulation_flux[rmspe_region],
            experiment_flux[rmspe_region],
            experiment_time.max() / 2,
            experiment_flux.max() / 2,
        )

    ax.set_xlabel("Time (s)")
    ax.set_ylabel(r"Desorbed flux (m$^{-2}$s$^{-1}$)")
    ax.set_title(
        "Unirradiated Sample: Deuterium Desorption: " "TMAP8 and TMAP7 vs Experiment"
    )
    ax.set_xlim(experiment_time.min(), experiment_time.max())
    ax.set_ylim(bottom=0)
    ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    ax.legend()
    ax.grid(True)

    plt.tight_layout()
    plt.savefig(comparison_plot, bbox_inches="tight", dpi=300)
    plt.close(fig)


# ========================== Plot calls ========================== #

plot_temperature_history()
plot_mass_conservation()
plot_inventory()

if "/tmap8/doc/" in script_folder.lower():  # if in documentation folder
    unirradiated_data_file = "../../../../test/tests/val-2l/gold/unirradiated_data.csv"
    benchmark_data_file = "../../../../test/tests/val-2l/gold/tmap7_fit_a_data.csv"
else:  # if in test folder
    unirradiated_data_file = "./gold/unirradiated_data.csv"
    benchmark_data_file = "./gold/tmap7_fit_a_data.csv"

plot_unirradiated_desorption(
    experiment_file=unirradiated_data_file, benchmark_file=benchmark_data_file
)
