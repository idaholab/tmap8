"""
This is the main comparison script for val-2l, and computes the following plots:

1: plot_temperature_history() shows the prescribed temperature profile against the experimental temperature data, as well as an inlet graph that zooms in on temperature anomolies observed during the experiment
2: plot_mass_conservation() shows the evolution of the mass conservation residual relative to the initial mass at the start of the TDS experiment
3: plot_inventory() shows the deuterium present in traps and as a mobile concentration over time
4: plot_flux_vs_time() plots the desorbed flux vs time for TMAP8, TMAP7 fit A, and experimental data, with the TMAP8 temperature history on a secondary axis, performing RMSPE calculations to measure the goodness of fit

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
    else:
        csv_folder = f"./gold/{file_name}"
    simulation_data = pd.read_csv(csv_folder)
    return np.array([simulation_data[name] for name in parameter_names])


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


def plot_temperature_history(
    experiment_file="val-2l_experimental_data.csv",
    simulation_file="val-2l_out.csv",
    filename="val-2l_temperature_history.png",
    zoom_end=350,
    zoom_ylim=(270, 370),
):
    """Plot the prescribed and experimental temperature history versus time with a zoomed inset

    Args:
        experiment_file (str): name of the experimental CSV in the gold directory; the
            measured temperature (time [s], temperature [K]) is used
        simulation_file (str): TMAP8 CSV with "time" (s) and "temperature" (K) columns,
            where temperature is the idealized ramp prescribed in val-2l.i
        filename (str): output PNG filename
        zoom_end (float): upper time limit (s) for the inset
        zoom_ylim (tuple): (y_min, y_max) in K for the inset y-axis
    """
    time, temperature = read_csv_from_TMAP8(simulation_file, ["time", "temperature"])
    experiment_time, experiment_temperature = read_csv_from_TMAP8(
        experiment_file, ["exp:time [s]", "exp:temperature [K]"]
    )

    # RMSPE of the prescribed temperature at the experimental times
    mapped_temperature = np.interp(experiment_time, time, temperature)
    rmspe_temperature = compute_rmspe(mapped_temperature, experiment_temperature)

    # ---- Full history ----
    fig, ax = plt.subplots(figsize=(6.5, 4.8))
    ax.plot(
        experiment_time,
        experiment_temperature,
        "ko",
        markersize=3,
        label="Experiment (Shimada 2011, 0 dpa)",
    )
    ax.plot(
        time,
        temperature,
        color="tab:red",
        linewidth=1.8,
        label="TMAP8 prescribed temperature",
    )
    ax.text(
        0.98,
        0.56,
        f"Temperature RMSPE = {rmspe_temperature:.2f}%",
        transform=ax.transAxes,
        fontweight="bold",
        color="tab:red",
        verticalalignment="center",
        horizontalalignment="right",
        fontsize=11,
    )
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Temperature (K)")
    ax.set_xlim(0, time.max())
    ax.set_ylim(bottom=0)
    ax.grid(visible=True, which="major", color="0.65", linestyle="--", alpha=0.3)
    ax.set_title("Unirradiated Sample: TDS Temperature History")
    ax.minorticks_on()
    ax.legend(loc="upper left")

    # ---- Inset: lower-right, first zoom_end seconds ----
    # Coordinates are in axes-fraction space: [left, bottom, width, height]
    ax_inset = ax.inset_axes([0.55, 0.14, 0.42, 0.38])
    experiment_mask = experiment_time <= zoom_end
    mask = time <= zoom_end
    ax_inset.plot(
        experiment_time[experiment_mask],
        experiment_temperature[experiment_mask],
        "ko",
        markersize=2,
    )
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
    M(0) and should remain close to zero if mass is conserved.

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
    trap_labels=("Trapped D (trap 1, 1.35 eV)",),
):
    """Plot the stacked deuterium inventory (mobile + trapped) with temperature history

    Args:
        simulation_file (str): TMAP8 CSV with "time", "temperature", "trap_per_free",
            "total_mobile_retention", and one trapped-retention column per trap:
            "total_trapped_retention" (trap 1), "total_trapped_retention_2", ...
        filename (str): output PNG filename
        trap_labels (tuple of str): legend label of each trap, in trap order. The number
            of labels sets the number of traps read from simulation_file.
    """
    trap_columns = ["total_trapped_retention"] + [
        f"total_trapped_retention_{i}" for i in range(2, len(trap_labels) + 1)
    ]
    time, temperature, mobile_raw, trap_per_free, *trapped_raw = read_csv_from_TMAP8(
        simulation_file,
        ["time", "temperature", "total_mobile_retention", "trap_per_free"]
        + trap_columns,
    )
    mobile = mobile_raw * disc_area

    # Stacked bottom-up: trap 1 first, then the other traps, then the mobile deuterium
    trap_colors = plt.get_cmap("viridis")(np.linspace(0.45, 0.1, len(trap_labels)))
    inventory_series = [
        (label, raw * trap_per_free[0] * disc_area, color)
        for label, raw, color in zip(trap_labels, trapped_raw, trap_colors)
    ]
    inventory_series.append(("Mobile D", mobile, plt.get_cmap("viridis")(0.95)))

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


def plot_flux_vs_time(
    experiment_file="val-2l_experimental_data.csv",
    tmap7_file="val-2l_tmap7_fita.csv",
    simulation_file="val-2l_out.csv",
    simulation_flux_column="deuterium_release_flux_total",
    comparison_plot="val-2l_comparison_flux_vs_time.png",
    rmspe_window=[900, 2650],
):
    """Plot desorption flux vs time for Shimada (2011) data, TMAP7 fit A, and TMAP8, with the
    TMAP8 temperature history on a secondary y-axis.

    The TMAP8 and TMAP7 fit A fluxes are compared with the experiment at the experimental
    times. TMAP8 is compared with TMAP7 fit A at the TMAP7 times.

    Args:
        experiment_file (str): name of the experimental CSV in the gold directory
            (time [s], temperature [K], desorbed flux [m^-2 s^-1])
        tmap7_file (str): name of the TMAP7 fit A CSV in the gold directory
            (time [s], temperature [K], desorbed flux [m^-2 s^-1])
        simulation_file (str): TMAP8 CSV output holding "time", "temperature" and
            the desorbed-flux column
        simulation_flux_column (str): name of the desorbed-flux column in
            simulation_file. TMAP8 reports it in at/µm^2/s; converted to at/m^2/s.
        comparison_plot (str): output PNG filename
        rmspe_window (tuple, optional): (t_min, t_max) in s of the points used in the
            RMSPE, shaded on the plot. Defaults to None, which uses the entire time range.
    """

    experiment_time, experiment_flux = read_csv_from_TMAP8(
        experiment_file,
        ["exp:time [s]", "exp:W103 desorbed D flux [m^-2 s^-1]"],
    )
    # Shimada (2011) provides the TMAP7 fit A flux as a function of temperature only. The time
    # column was reconstructed from the TMAP7 input, whose temperature ramps linearly from 293 K
    # to 1173 K in 5400 s and then holds 1173 K until 7200 s.
    tmap7_time, tmap7_flux = read_csv_from_TMAP8(
        tmap7_file,
        ["TMAP_fit_A:time [s]", "TMAP_fit_A:W103_good TMAP flux [m^-2 s^-1]"],
    )

    simulation_time, simulation_temperature, simulation_flux = read_csv_from_TMAP8(
        simulation_file, ["time", "temperature", simulation_flux_column]
    )
    simulation_flux = simulation_flux * 1e12  # at/µm^2/s -> at/m^2/s

    # Interpolate TMAP7 fit A and TMAP8 flux at the experimental times
    mapped_tmap7_flux = np.interp(experiment_time, tmap7_time, tmap7_flux)
    mapped_simulation_flux = np.interp(
        experiment_time, simulation_time, simulation_flux
    )

    # Points used for the RMSPE: default is the entire time range
    if rmspe_window is None:
        rmspe_region = np.ones_like(experiment_time, dtype=bool)
    else:
        rmspe_region = (experiment_time >= rmspe_window[0]) & (
            experiment_time <= rmspe_window[1]
        )

    rmspe_tmap8 = compute_rmspe(
        mapped_simulation_flux[rmspe_region], experiment_flux[rmspe_region]
    )
    rmspe_tmap7 = compute_rmspe(
        mapped_tmap7_flux[rmspe_region], experiment_flux[rmspe_region]
    )

    # TMAP8 against TMAP7 fit A (reference solution) at the TMAP7 times
    mapped_simulation_flux_on_tmap7 = np.interp(
        tmap7_time, simulation_time, simulation_flux
    )
    if rmspe_window is None:
        tmap7_region = np.ones_like(tmap7_time, dtype=bool)
    else:
        tmap7_region = (tmap7_time >= rmspe_window[0]) & (tmap7_time <= rmspe_window[1])
    rmspe_tmap8_vs_tmap7 = compute_rmspe(
        mapped_simulation_flux_on_tmap7[tmap7_region], tmap7_flux[tmap7_region]
    )

    fig, ax = plt.subplots(figsize=(10, 6))

    experiment_handle = ax.plot(
        experiment_time,
        experiment_flux,
        "ko",
        label="Experiment (Shimada 2011, 0 dpa)",
    )[0]
    tmap7_handle = ax.plot(
        tmap7_time,
        tmap7_flux,
        color="red",
        linestyle="--",
        label="TMAP7 fit A",
    )[0]
    tmap8_handle = ax.plot(simulation_time, simulation_flux, "b-", label="TMAP8")[0]
    handles = [experiment_handle, tmap7_handle, tmap8_handle]

    if rmspe_window is not None:
        # Add shaded region to indicate RMSPE evaluation window
        ax.axvspan(
            rmspe_window[0],
            rmspe_window[1],
            alpha=0.1,
            color="gray",
        )
        handles.append(
            Patch(
                color="gray",
                alpha=0.1,
                label=f"RMSPE window ({rmspe_window[0]:.0f}-{rmspe_window[1]:.0f} s)",
            )
        )

    # Temperature history on the secondary y-axis
    ax_T = ax.twinx()
    handles.append(
        ax_T.plot(
            simulation_time,
            simulation_temperature,
            linestyle="-",
            color="k",
            linewidth=1.5,
            label="TMAP8 temperature history",
        )[0]
    )
    ax_T.set_ylabel("Temperature (K)")

    # Add color-coded RMSPE annotations to center right
    ax.text(
        0.98,
        0.55,
        f"TMAP8 RMSPE = {rmspe_tmap8:.2f}%",
        transform=ax.transAxes,
        fontweight="bold",
        color="blue",
        verticalalignment="center",
        horizontalalignment="right",
        fontsize=11,
    )
    ax.text(
        0.98,
        0.47,
        f"TMAP7 fit A RMSPE = {rmspe_tmap7:.2f}%",
        transform=ax.transAxes,
        fontweight="bold",
        color="red",
        verticalalignment="center",
        horizontalalignment="right",
        fontsize=11,
    )
    ax.text(
        0.98,
        0.39,
        f"TMAP8 Benchmark RMSPE = {rmspe_tmap8_vs_tmap7:.2f}%",
        transform=ax.transAxes,
        fontweight="bold",
        color="purple",
        verticalalignment="center",
        horizontalalignment="right",
        fontsize=11,
    )

    ax.set_xlabel("Time (s)")
    ax.set_ylabel(r"Desorbed flux (m$^{-2}$s$^{-1}$)")
    ax.set_title("Unirradiated Sample: Deuterium Desorption vs Time")
    ax.set_xlim(0, simulation_time.max())
    ax.set_ylim(
        0, 1.2 * simulation_flux.max()
    )  # headroom keeps the legend clear of the peak
    ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    ax.legend(handles=handles, loc="upper left", fontsize=7)
    ax.grid(True)

    plt.tight_layout()
    plt.savefig(comparison_plot, bbox_inches="tight", dpi=300)
    plt.close(fig)


# ========================== Plot calls ========================== #

# Guarded so comparison_val-2l_multi_trap.py can import the functions without re-plotting
if __name__ == "__main__":
    plot_temperature_history()
    plot_mass_conservation()
    plot_inventory()
    plot_flux_vs_time()
