"""
This is the main comparison script for val-2l, and computes the following plots:
1: plot_timestep_behavior() visualizes the adaptive timestepper based on critical temperature regions and measured fluxes
1: plot_temperature_history() shows the temperature profile over the entire time of experiment, as well as an inlet graph that zooms in on temperature anomolies observed during the experiment
2: plot_mass_conservation() shows the evolution of the mass conservation residual relative to the initial mass at the start of the TDS experiment
3: plot_inventory() shows the deuterium present in traps and as a mobile concentration
4: plot_diffusivity_vs_temperature() shows the diffusivity as a function of reciprocal temperature, which should be linear
5: plot_unirradiated_desorption() plots the simulated against experimental desorbed flux from the upstream and downstream surfaces, performing RMSPE calculations to measure the goodness of fit
"""

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
from matplotlib.patches import Patch
import pandas as pd
from scipy import special
import scipy.stats as stats
import os

# Changes working directory to script directory (for consistent MooseDocs usage)
script_folder = os.path.dirname(__file__)
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
    plt.text(x_pos, y_pos, "RMSPE = %.2f %%" % RMSPE, fontweight="bold")


def plot_timestep_behavior(
    simulation_file="val-2l_out.csv",
    filename="val-2l_timestep_behavior.png",
    temperature_window=(100.0, 350.0),
):
    """Plot temperature, desorbed flux, and timestep size over time.

    The shaded regions identify the two timestep-limiting conditions:

    1. The fixed temperature-resolution interval.
    2. Times when the magnitude of the desorbed flux exceeds the specified
       threshold.

    Args:
        simulation_file (str): TMAP8 CSV with "time", "dt", "temperature", and
            "desorbed_flux" columns.
        filename (str): Output PNG filename.
        flux_threshold (float): Flux magnitude above which fine timesteps are used
            in at/m^2/s.
        temperature_window (tuple[float, float]): Start and end times of the fixed
            fine-timestep interval in seconds.
    """
    time, dt, temperature, desorbed_flux, flux_threshold = read_csv_from_TMAP8(
        simulation_file,
        ["time", "dt", "temperature", "deuterium_release_flux_total", "flux_threshold"],
    )

    # Remove a possible initial-output row where TimestepSize has not yet been set.
    valid = (
        np.isfinite(time)
        & np.isfinite(dt)
        & np.isfinite(temperature)
        & np.isfinite(desorbed_flux)
        & (dt > 0.0)
    )
    time = time[valid]
    dt = dt[valid]
    temperature = temperature[valid]
    desorbed_flux = desorbed_flux[valid]
    flux_threshold = flux_threshold[0] * 1e12

    flux_active = np.abs(desorbed_flux) >= flux_threshold
    temperature_start, temperature_end = temperature_window

    fig, axes = plt.subplots(
        nrows=3,
        ncols=1,
        figsize=(7.0, 8.0),
        sharex=True,
    )
    ax_temperature, ax_flux, ax_dt = axes

    # Temperature history
    ax_temperature.plot(
        time,
        temperature,
        color="black",
        linewidth=1.8,
    )
    ax_temperature.set_ylabel("Temperature (K)")
    ax_temperature.set_title("Unirradiated Sample: Timestep-Limiting Regions")

    # Desorbed flux history
    ax_flux.plot(
        time,
        desorbed_flux * 1e12,
        color="tab:green",
        linewidth=1.8,
    )
    ax_flux.axhline(
        flux_threshold,
        color="tab:red",
        linewidth=1.1,
        linestyle="--",
        label=rf"Flux threshold: {flux_threshold:.1e} at/m$^2$/s",
    )
    ax_flux.set_ylabel(r"Desorbed flux (at/m$^2$/s)")
    ax_flux.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    ax_flux.legend(loc="best")

    # Actual timestep used over each interval.
    ax_dt.step(
        time,
        dt,
        where="pre",
        color="tab:blue",
        linewidth=1.8,
    )
    ax_dt.set_xlabel("Time (s)")
    ax_dt.set_ylabel("Timestep size (s)")

    # A logarithmic axis makes reductions easier to see when dt spans
    # multiple orders of magnitude.
    ax_dt.set_yscale("log")

    # Shade the two timestep-limiting regions on every panel.
    for index, ax in enumerate(axes):
        ax.axvspan(
            temperature_start,
            temperature_end,
            color="tab:orange",
            alpha=0.14,
            linewidth=0.0,
            label="Temperature refinement" if index == 0 else None,
        )
        ax.fill_between(
            time,
            0.0,
            1.0,
            where=flux_active,
            step="pre",
            transform=ax.get_xaxis_transform(),
            color="tab:red",
            alpha=0.09,
            linewidth=0.0,
        )

        ax.grid(
            visible=True,
            which="major",
            color="0.65",
            linestyle="--",
            alpha=0.3,
        )
        ax.minorticks_on()

    ax_temperature.legend(loc="best")
    ax_dt.set_xlim(0.0, time.max())

    plt.tight_layout()
    plt.savefig(filename, bbox_inches="tight", dpi=300)
    plt.close(fig)


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


def plot_diffusivity_vs_temperature(
    simulation_file="val-2l_out.csv",
    filename="val-2l_diffusivity_vs_temperature.png",
):
    """Plot the deuterium diffusivity in tungsten against temperature

    The diffusivity is spatially uniform (it depends only on temperature), so the
    ``diffusivity_pp`` and ``temperature`` postprocessors from the TMAP8 output fully
    describe D(T) over the simulated TDS ramp. Reading them straight from the CSV
    keeps the Arrhenius law defined in exactly one place (val-2l.i). It is the
    Frauenfelder relation corrected for deuterium, Shimada et al. 2010
    (p. S668, Section 3): D = 2.9e-7 * exp(-0.39 eV / (k_B T)) m^2/s.

    Args:
        simulation_file (str): TMAP8 CSV with "temperature" (K) and "diffusivity_pp"
            (µm²/s) columns
        filename (str): output PNG filename
    """
    temperature, diffusivity = read_csv_from_TMAP8(
        simulation_file, ["temperature", "diffusivity_pp"]
    )
    # Drop the INITIAL row (t = 0), where postprocessors are still 0, then sort by T.
    valid = diffusivity > 0
    temperature, diffusivity = temperature[valid], diffusivity[valid]
    order = np.argsort(temperature)
    temperature, diffusivity = temperature[order], diffusivity[order]
    diffusivity_m2_s = diffusivity * 1e-12  # µm²/s -> m²/s
    reciprocal_temperature = 1000.0 / temperature  # 1000/T (1/K)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.semilogy(
        reciprocal_temperature, diffusivity_m2_s, color="steelblue", linewidth=2
    )
    ax.set_xlabel(r"Reciprocal temperature 1000/T (K$^{-1}$)")
    ax.set_ylabel(r"Diffusivity (m$^2$/s)")
    ax.set_title("Deuterium Diffusivity in Tungsten")
    ax.grid(True, which="both", linestyle="--", alpha=0.4)
    plt.tight_layout()
    plt.savefig(filename, bbox_inches="tight", dpi=300)
    plt.close(fig)


def plot_unirradiated_desorption(
    experiment_file="unirradiated_data.csv",
    simulation_file="val-2l_out.csv",
    simulation_flux_column="deuterium_release_flux_total",
    comparison_plot="val-2l_comparison_desorption.png",
):
    """Plot the Shimada (2010) unirradiated desorption data against TMAP8

    The simulated and experimental desorbed fluxes are plotted versus time,
    with the RMSPE annotated over the region tmin–tmax seconds.

    Args:
        experiment_file (str): two-column, header-less CSV of
            (time [s], desorbed flux [m^-2 s^-1])
        simulation_file (str): TMAP8 CSV output holding "time" and
            the desorbed-flux column
        simulation_flux_column (str): name of the desorbed-flux column in
            simulation_file. TMAP8 reports it in at/µm^2/s; converted to at/m^2/s.
        comparison_plot (str): output PNG filename
    """
    experiment = np.loadtxt(experiment_file, delimiter=",")
    experiment_time, experiment_flux = experiment[:, 0], experiment[:, 1]

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

    plt.figure(figsize=(10, 6))
    plt.plot(
        experiment_time,
        experiment_flux,
        "ro",
        label="Experiment (Shimada 2010, 0 dpa)",
    )
    plt.plot(simulation_time, simulation_flux, "b-", label="TMAP8")
    if rmspe_region.any():
        plt.axvline(
            experiment_time[rmspe_region].min(),
            color="green",
            linestyle="--",
            linewidth=1.2,
            label="RMSPE region",
        )
        plt.axvline(
            experiment_time[rmspe_region].max(),
            color="green",
            linestyle="--",
            linewidth=1.2,
        )
        annotate_rmspe(
            mapped_simulation_flux[rmspe_region],
            experiment_flux[rmspe_region],
            experiment_time[rmspe_region].mean(),
            experiment_flux.max() / 4,
        )
    plt.xlabel("Time (s)")
    plt.ylabel(r"Desorbed flux (m$^{-2}$s$^{-1}$)")
    plt.title("Unirradiated Sample: Deuterium Desorption: TMAP8 vs Experiment")
    plt.xlim(experiment_time.min(), experiment_time.max())
    plt.ylim(0)
    plt.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(comparison_plot, bbox_inches="tight", dpi=300)


# ========================== Plot calls ========================== #

# plot_temperature_history(simulation_file="temperature_data.csv")
plot_timestep_behavior()
plot_temperature_history()
plot_mass_conservation()
plot_inventory()
plot_diffusivity_vs_temperature()
if "/tmap8/doc/" in script_folder.lower():  # if in documentation folder
    unirradiated_data_file = "../../../../test/tests/val-2l/gold/unirradiated_data.csv"
else:  # if in test folder
    unirradiated_data_file = "./gold/unirradiated_data.csv"

plot_unirradiated_desorption(experiment_file=unirradiated_data_file)

data = pd.read_csv("val-2l_out.csv")
flux_column = "deuterium_release_flux_total"

i_max = data[flux_column].abs().idxmax()

print(
    data.loc[
        i_max,
        ["time", "dt", "temperature", flux_column, "flux_threshold"],
    ]
)
