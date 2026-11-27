import os
import re
import tempfile
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", tempfile.mkdtemp(prefix="matplotlib-val-2k-"))

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import Patch

# Stage 1: resolve all file paths from the script directory so MooseDocs and
# local test runs use the same relative paths.
script_folder = os.path.dirname(__file__)
os.chdir(script_folder)


def get_repo_relative_path(test_path):
    if "/tmap8/doc/" in script_folder.lower():
        return os.path.join("../../../../test/tests/val-2k", test_path)
    return os.path.join(".", test_path)


def get_output_candidates(filename):
    return [
        Path(get_repo_relative_path(f"../../../{filename}")),
        Path(get_repo_relative_path(filename)),
        Path(get_repo_relative_path(f"gold/{filename}")),
    ]


def output_exists(filename):
    return any(candidate.exists() for candidate in get_output_candidates(filename))


def get_output_path(filename):
    candidates = get_output_candidates(filename)
    existing_candidates = [candidate for candidate in candidates if candidate.exists()]
    if existing_candidates:
        return max(existing_candidates, key=lambda path: path.stat().st_mtime)
    return candidates[-1]


def search_parameter(path, visited, parameter_name):
    if path in visited:
        return None
    visited.add(path)
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if stripped.startswith("!include "):
                include_name = stripped.split(maxsplit=1)[1]
                include_path = os.path.join(os.path.dirname(path), include_name)
                result = search_parameter(include_path, visited, parameter_name)
                if result is not None:
                    return result
            if stripped.startswith(f"{parameter_name} ="):
                return stripped.split("=", maxsplit=1)[1].strip().strip("'")
    return None


def get_raw_parameter_value(parameter_name, source_file="val-2k_natural_oxide.i"):
    parameters_file = get_repo_relative_path(source_file)
    result = search_parameter(parameters_file, set(), parameter_name)
    if result is None:
        raise KeyError(
            f"Could not find parameter {parameter_name} in {parameters_file}"
        )
    return result


def parse_numeric_value(value, output_unit=None):
    if value.startswith("${units ") and value.endswith("}"):
        units_expr = value[len("${units ") : -1].strip()
        match = re.fullmatch(
            r"([0-9eE.+-]+)\s+([A-Za-z0-9^/]+)(?:\s*->\s*([A-Za-z0-9^/]+))?",
            units_expr,
        )
        if not match:
            raise ValueError(f"Unsupported units expression: {value}")
        numeric_value = float(match.group(1))
        from_unit = match.group(2)
        to_unit = match.group(3)
        target_unit = output_unit
        if target_unit is None:
            if to_unit is None or from_unit == to_unit:
                return numeric_value
            target_unit = to_unit
        if from_unit == target_unit:
            return numeric_value
        supported_conversions = {
            ("h", "s"): 3600.0,
            ("s", "h"): 1.0 / 3600.0,
            ("nm", "mum"): 1e-3,
            ("m", "mum"): 1e6,
            ("m^4/at/s", "mum^4/at/s"): 1e24,
            ("mum^4/at/s", "m^4/at/s"): 1e-24,
        }
        factor = supported_conversions.get((from_unit, target_unit))
        if factor is None:
            raise ValueError(f"Unsupported conversion in units expression: {value}")
        return numeric_value * factor
    return float(value)


def get_numeric_parameter(
    parameter_name, source_file="val-2k_natural_oxide.i", output_unit=None
):
    raw_value = get_raw_parameter_value(parameter_name, source_file)
    return parse_numeric_value(raw_value, output_unit)


def load_experimental_curve(filename):
    return pd.read_csv(get_repo_relative_path(f"gold/{filename}"))


def load_simulation_case(csv_name):
    simulation_data = pd.read_csv(get_output_path(csv_name))
    time_s = simulation_data["time"] * time_reference
    release_flux_d2 = (
        simulation_data["scaled_flux_surface_left_d2"]
        + simulation_data["scaled_flux_surface_right_d2"]
    )
    release_flux_d2o = (
        simulation_data["scaled_flux_surface_left_d2o"]
        + simulation_data["scaled_flux_surface_right_d2o"]
    )
    initial_inventory = simulation_data["deuterium_inventory_in_sample_physical"].iloc[
        0
    ]
    oxygen_initial_inventory = None
    if "oxygen_initial_inventory_in_sample_physical" in simulation_data.columns:
        oxygen_initial_inventory = simulation_data[
            "oxygen_initial_inventory_in_sample_physical"
        ].iloc[0]
    elif "oxygen_inventory_in_sample_physical" in simulation_data.columns:
        oxygen_initial_inventory = simulation_data[
            "oxygen_inventory_in_sample_physical"
        ].iloc[0]

    oxygen_inventory_in_sample = simulation_data.get(
        "oxygen_inventory_in_sample_physical"
    )
    oxygen_released = simulation_data.get("oxygen_released_physical")
    oxygen_mass_residual = simulation_data.get("oxygen_mass_conservation_residual")
    return {
        "data": simulation_data,
        "time_s": time_s,
        "time_h": time_s / 3600.0,
        "temperature_k": simulation_data["temperature_pps"],
        "initial_inventory": initial_inventory,
        "inventory_in_sample": simulation_data[
            "deuterium_inventory_in_sample_physical"
        ],
        "released_inventory": simulation_data["deuterium_released_physical"],
        "mass_conservation_residual": simulation_data[
            "deuterium_mass_conservation_residual"
        ],
        "relative_mass_conservation_residual": simulation_data[
            "deuterium_mass_conservation_residual"
        ]
        / initial_inventory,
        "oxygen_initial_inventory": oxygen_initial_inventory,
        "oxygen_inventory_in_sample": oxygen_inventory_in_sample,
        "oxygen_released": oxygen_released,
        "oxygen_mass_conservation_residual": oxygen_mass_residual,
        "relative_oxygen_mass_conservation_residual": (
            oxygen_mass_residual / oxygen_initial_inventory
            if oxygen_mass_residual is not None
            and oxygen_initial_inventory not in (None, 0.0)
            else None
        ),
        "mobile_inventory": simulation_data["mobile_inventory_physical"],
        "trapped_intrinsic_inventory": simulation_data[
            "trapped_deuterium_intrinsic_physical"
        ],
        "trapped_1_inventory": simulation_data["trapped_deuterium_1_physical"],
        "trapped_2_inventory": simulation_data["trapped_deuterium_2_physical"],
        "trapped_3_inventory": simulation_data["trapped_deuterium_3_physical"],
        "trapped_4_inventory": simulation_data["trapped_deuterium_4_physical"],
        "trapped_5_inventory": simulation_data["trapped_deuterium_5_physical"],
        "release_rate_d2": release_flux_d2 * sample_surface_area_m2 / 1e13,
        "release_rate_d2o": release_flux_d2o * sample_surface_area_m2 / 1e13,
        "release_rate_total": (release_flux_d2 + release_flux_d2o)
        * sample_surface_area_m2
        / 1e13,
    }


def compute_rmspe(case_time_h, case_release_rate, experimental_curve):
    experiment_time = experimental_curve["time (h)"]
    experiment_flux = experimental_curve["release flux (10^13 D atoms/s)"]
    simulated_on_experiment_grid = np.interp(
        experiment_time, case_time_h, case_release_rate
    )
    rmse = np.sqrt(np.mean((simulated_on_experiment_grid - experiment_flux) ** 2))
    return rmse * 100.0 / np.mean(experiment_flux)


def add_temperature_top_axis(ax, temperature_ticks_k):
    ax_top = ax.twiny()
    ax_top.set_xlim(ax.get_xlim())
    tick_temperatures = np.asarray(temperature_ticks_k, dtype=float)
    ax_top.set_xticks(1000.0 / tick_temperatures)
    ax_top.set_xticklabels([str(int(tick)) for tick in tick_temperatures])
    ax_top.set_xlabel("Temperature (K)")
    return ax_top


def create_tds_figure(case_specs_to_plot, image_name, figure_caption_lines=None):
    is_single_case_view = len(case_specs_to_plot) == 1
    fig, ax = plt.subplots(figsize=(7.2, 8.2))
    fig.subplots_adjust(top=0.8, bottom=0.42 if is_single_case_view else 0.38)
    axis_label_fontsize = 16 if is_single_case_view else None
    tick_label_fontsize = 14 if is_single_case_view else None
    legend_fontsize = 14 if is_single_case_view else None
    text_fontsize = 14 if is_single_case_view else None

    tds_handles = []
    tds_labels = []
    rmspe_lines = []

    for spec in case_specs_to_plot:
        case = spec["simulation"]
        color = spec["color"]
        experimental_d2 = spec["experimental_d2"]
        experimental_d2o = spec["experimental_d2o"]

        simulated_d2_handle = ax.plot(
            case["time_h"],
            case["release_rate_d2"],
            linestyle="-",
            color=color,
            label=(
                r"TMAP8 D$_2$"
                if is_single_case_view
                else f"TMAP8 D$_2$, {spec['display_label']}"
            ),
        )[0]
        simulated_d2o_handle = ax.plot(
            case["time_h"],
            case["release_rate_d2o"],
            linestyle="--",
            color=color,
            label=(
                r"TMAP8 D$_2$O"
                if is_single_case_view
                else f"TMAP8 D$_2$O, {spec['display_label']}"
            ),
        )[0]
        experimental_d2_handle = ax.plot(
            experimental_d2["time (h)"],
            experimental_d2["release flux (10^13 D atoms/s)"],
            linestyle="-.",
            color=color,
            label=(
                r"Exp. HD + D$_2$"
                if is_single_case_view
                else f"Experimental HD + D$_2$ ({spec['display_label']})"
            ),
        )[0]
        experimental_d2o_handle = ax.plot(
            experimental_d2o["time (h)"],
            experimental_d2o["release flux (10^13 D atoms/s)"],
            linestyle=":",
            color=color,
            label=(
                r"Exp. HDO + D$_2$O"
                if is_single_case_view
                else f"Experimental HDO + D$_2$O ({spec['display_label']})"
            ),
        )[0]

        tds_handles.extend(
            [
                simulated_d2_handle,
                simulated_d2o_handle,
                experimental_d2_handle,
                experimental_d2o_handle,
            ]
        )
        tds_labels.extend(handle.get_label() for handle in tds_handles[-4:])

        rmspe_d2 = compute_rmspe(
            case["time_h"], case["release_rate_d2"], experimental_d2
        )
        rmspe_d2o = compute_rmspe(
            case["time_h"], case["release_rate_d2o"], experimental_d2o
        )
        rmspe_lines.append(
            f"{spec['rmspe_label']} RMSPEs: D$_2$={rmspe_d2:.2f} %, D$_2$O={rmspe_d2o:.2f} %"
        )

    ax_temperature = ax.twinx()
    temperature_handle = ax_temperature.plot(
        baseline_case["time_h"],
        baseline_case["temperature_k"],
        linestyle="-",
        color="k",
        linewidth=1.5,
        label="Temperature" if is_single_case_view else "TMAP8 temperature history",
    )[0]
    if figure_caption_lines is None:
        figure_caption_lines = rmspe_lines
    fig.text(
        0.5,
        0.83 if is_single_case_view else 0.88,
        "\n".join(figure_caption_lines),
        ha="center",
        va="top",
        fontsize=text_fontsize,
    )

    ax.set_xlabel("Time (h)", fontsize=axis_label_fontsize)
    ax.set_ylabel("Release rate (10$^{13}$ D atoms/s)", fontsize=axis_label_fontsize)
    ax.set_xlim(0, 4.2)
    ax.set_ylim(bottom=0)
    ax.grid(visible=True, which="major", color="0.65", linestyle="--", alpha=0.3)
    ax_temperature.set_ylabel("Temperature (K)", fontsize=axis_label_fontsize)
    ax_temperature.set_ylim(280, 1100)
    if is_single_case_view:
        ax.tick_params(axis="both", which="both", labelsize=tick_label_fontsize)
        ax_temperature.tick_params(
            axis="both", which="both", labelsize=tick_label_fontsize
        )
        unique_legend_handles = []
        unique_legend_labels = []
        for handle, label in zip(
            tds_handles + [temperature_handle],
            tds_labels + [temperature_handle.get_label()],
        ):
            if label not in unique_legend_labels:
                unique_legend_handles.append(handle)
                unique_legend_labels.append(label)
    else:
        unique_legend_handles = tds_handles + [temperature_handle]
        unique_legend_labels = tds_labels + [temperature_handle.get_label()]
    fig.legend(
        unique_legend_handles,
        unique_legend_labels,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.2 if is_single_case_view else 0.081),
        ncol=2,
        frameon=True,
        fontsize=legend_fontsize,
    )
    ax.minorticks_on()

    plt.savefig(image_name, bbox_inches="tight", dpi=300)
    plt.close(fig)


# Stage 2: load the simulated outputs for the currently available oxygen-field
# cases together with the experimental curves from Fig. 6. in Kremer et al. 2022
#  https://doi.org/10.1016/j.nme.2022.101137
time_reference = get_numeric_parameter("time_reference")
sample_surface_area_m2 = 10e-3 * 14e-3

case_specs = [
    {
        "key": "natural_oxide",
        "focused_figure_name": "val-2k_natural_oxide_case_comparison.png",
        "display_label": "1 nm oxide",
        "rmspe_label": "Nat. oxide",
        "color": "tab:blue",
        "simulation_csv": "gold/val-2k_natural_oxide_out.csv",
        "profile_csv": "gold/val-2k_profile_initial_out_line_profile_0000.csv",
        "experimental_d2_csv": "experimental_HD_D2_nat_oxide.csv",
        "experimental_d2o_csv": "experimental_HDO_D2O_nat_oxide.csv",
    },
    {
        "key": "oxide_5nm",
        "focused_figure_name": "val-2k_5nm_oxide_case_comparison.png",
        "display_label": "5 nm oxide",
        "rmspe_label": "5 nm oxide",
        "color": "tab:green",
        "simulation_csv": "gold/val-2k_5nm_oxide_out.csv",
        "profile_csv": "gold/val-2k_5nm_oxide_profile_initial_out_line_profile_0000.csv",
        "experimental_d2_csv": "experimental_HD_D2_5nm.csv",
        "experimental_d2o_csv": "experimental_HDO_D2O_5nm.csv",
    },
    {
        "key": "oxide_10nm",
        "focused_figure_name": "val-2k_10nm_oxide_case_comparison.png",
        "display_label": "10 nm oxide",
        "rmspe_label": "10 nm oxide",
        "color": "tab:orange",
        "simulation_csv": "gold/val-2k_10nm_oxide_out.csv",
        "profile_csv": "gold/val-2k_10nm_oxide_profile_initial_out_line_profile_0000.csv",
        "experimental_d2_csv": "experimental_HD_D2_10nm.csv",
        "experimental_d2o_csv": "experimental_HDO_D2O_10nm.csv",
    },
    {
        "key": "oxide_15nm",
        "focused_figure_name": "val-2k_15nm_oxide_case_comparison.png",
        "display_label": "15 nm oxide",
        "rmspe_label": "15 nm oxide",
        "color": "tab:red",
        "simulation_csv": "gold/val-2k_15nm_oxide_out.csv",
        "profile_csv": "gold/val-2k_15nm_oxide_profile_initial_out_line_profile_0000.csv",
        "experimental_d2_csv": "experimental_HD_D2_15nm.csv",
        "experimental_d2o_csv": "experimental_HDO_D2O_15nm.csv",
    },
]

available_cases = []
for spec in case_specs:
    spec["experimental_d2"] = load_experimental_curve(spec["experimental_d2_csv"])
    spec["experimental_d2o"] = load_experimental_curve(spec["experimental_d2o_csv"])
    if output_exists(spec["simulation_csv"]):
        spec["simulation"] = load_simulation_case(spec["simulation_csv"])
        available_cases.append(spec)

baseline_case = available_cases[0]["simulation"]
profile_case_spec = next(
    (spec for spec in available_cases if spec["key"] == "oxide_15nm"),
    available_cases[-1],
)
profile_case = pd.read_csv(get_output_path(profile_case_spec["profile_csv"]))
oxide_thickness_profile_um = get_numeric_parameter(
    "oxide_thickness", "val-2k_15nm_oxide.i"
)
damage_depth_um = get_numeric_parameter("damage_depth")
profile_depth_um = get_numeric_parameter("profile_depth")
d2_recombination_coefficient_m4 = get_numeric_parameter(
    "d2_recombination_coefficient", output_unit="m^4/at/s"
)
d2_recombination_energy_ev = get_numeric_parameter("d2_recombination_energy")
d2o_recombination_coefficient_m4 = get_numeric_parameter(
    "d2o_recombination_coefficient", output_unit="m^4/at/s"
)
d2o_recombination_energy_ev = get_numeric_parameter("d2o_recombination_energy")
temperature_bounds_k = np.array(
    [
        baseline_case["temperature_k"].min(),
        baseline_case["temperature_k"].max(),
    ]
)
temperature_plot_k = np.linspace(
    temperature_bounds_k.min(), temperature_bounds_k.max(), 500
)
inverse_temperature_plot = 1000.0 / temperature_plot_k
boltzmann_constant_ev = 8.617333262e-5
temperature_ticks_k = np.array([1000, 900, 800, 700, 600, 500, 400, 300])
temperature_ticks_k = temperature_ticks_k[
    (temperature_ticks_k >= np.floor(temperature_bounds_k.min()))
    & (temperature_ticks_k <= np.ceil(temperature_bounds_k.max()))
]
recombination_temperature_ticks_k = temperature_ticks_k[temperature_ticks_k != 900]

# Stage 3: generate the desorption comparison figure for all currently modeled
# cases together with four companion views that isolate each case.
create_tds_figure(
    available_cases,
    "val-2k_comparison.png",
)
for spec in available_cases:
    create_tds_figure(
        [spec],
        spec["focused_figure_name"],
    )

# Stage 4: show the D2 and D2O surface recombination coefficients over the
# experimental temperature range in Arrhenius form.
fig, ax = plt.subplots(figsize=(6.5, 4.8))

d2_recombination_rate = d2_recombination_coefficient_m4 * np.exp(
    -d2_recombination_energy_ev / (boltzmann_constant_ev * temperature_plot_k)
)
d2o_recombination_rate = d2o_recombination_coefficient_m4 * np.exp(
    -d2o_recombination_energy_ev / (boltzmann_constant_ev * temperature_plot_k)
)

ax.semilogy(
    inverse_temperature_plot,
    d2_recombination_rate,
    color="tab:blue",
    linewidth=2.0,
    label=r"D$_2$ recombination",
)
ax.semilogy(
    inverse_temperature_plot,
    d2o_recombination_rate,
    color="tab:orange",
    linewidth=2.0,
    linestyle="--",
    label=r"D$_2$O recombination",
)
ax.set_xlabel("1000/T (1/K)")
ax.set_ylabel(r"Surface recombination coefficient (m$^4$/at/s)")
ax.grid(visible=True, which="major", color="0.65", linestyle="--", alpha=0.3)
ax.legend(loc="best")
ax.minorticks_on()
add_temperature_top_axis(ax, recombination_temperature_ticks_k)

plt.savefig(
    "val-2k_natural_oxide_recombination_rates.png",
    bbox_inches="tight",
    dpi=300,
)
plt.close(fig)

# Stage 5: generate the baseline inventory history figure showing the cumulative
# deuterium inventory and the contribution of each trap family.
fig, ax = plt.subplots(figsize=(6.5, 5.5))
cmap = plt.get_cmap("viridis")
inventory_colors = cmap(np.linspace(0, 1, 7))
inventory_series = [
    ("Trap 5 D", baseline_case["trapped_5_inventory"], inventory_colors[0]),
    ("Trap 4 D", baseline_case["trapped_4_inventory"], inventory_colors[1]),
    ("Trap 3 D", baseline_case["trapped_3_inventory"], inventory_colors[2]),
    ("Trap 2 D", baseline_case["trapped_2_inventory"], inventory_colors[3]),
    (
        "Intrinsic trap D",
        baseline_case["trapped_intrinsic_inventory"],
        inventory_colors[4],
    ),
    ("Trap 1 D", baseline_case["trapped_1_inventory"], inventory_colors[5]),
    ("Mobile D", baseline_case["mobile_inventory"], inventory_colors[6]),
]
inventory_bottom = np.zeros_like(baseline_case["mobile_inventory"])
legend_patches = []

for label, values, color in inventory_series:
    ax.fill_between(
        baseline_case["time_h"],
        inventory_bottom,
        inventory_bottom + values,
        color=color,
        alpha=0.3,
    )
    ax.plot(
        baseline_case["time_h"], inventory_bottom + values, color=color, linewidth=1.0
    )
    inventory_bottom += values
    legend_patches.append(Patch(color=color, alpha=0.5, label=label))

total_inventory = inventory_bottom.copy()
total_handle = ax.plot(
    baseline_case["time_h"],
    total_inventory,
    color="tab:green",
    linewidth=1.5,
    label="Total D inventory",
)[0]

ax_temperature = ax.twinx()
temperature_handle = ax_temperature.plot(
    baseline_case["time_h"],
    baseline_case["temperature_k"],
    linestyle="-",
    color="k",
    linewidth=1.5,
    label="TMAP8 temperature history",
)[0]

ax.set_xlabel("Time (h)")
ax.set_ylabel("Deuterium inventory (atoms)")
ax.set_xlim(0, 4.2)
ax.set_ylim(bottom=0)
ax.grid(visible=True, which="major", color="0.65", linestyle="--", alpha=0.3)
ax_temperature.set_ylabel("Temperature (K)")
ax_temperature.set_ylim(280, 1100)
ax.legend(
    [
        total_handle,
        temperature_handle,
        legend_patches[-1],
        legend_patches[-2],
        legend_patches[-3],
        legend_patches[-4],
        legend_patches[-5],
        legend_patches[-6],
        legend_patches[-7],
    ],
    [
        total_handle.get_label(),
        temperature_handle.get_label(),
        legend_patches[-1].get_label(),
        legend_patches[-2].get_label(),
        legend_patches[-3].get_label(),
        legend_patches[-4].get_label(),
        legend_patches[-5].get_label(),
        legend_patches[-6].get_label(),
        legend_patches[-7].get_label(),
    ],
    loc="upper center",
    bbox_to_anchor=(0.65, 1),
    framealpha=0.8,
)
ax.minorticks_on()

plt.savefig("val-2k_natural_oxide_inventory.png", bbox_inches="tight", dpi=300)
plt.close(fig)

# Stage 6: compare the relative deuterium mass-balance residual for all
# currently available modeled cases using the postprocessors written by the
# transient solves.
fig, ax = plt.subplots(figsize=(6.5, 4.8))

mass_handles = []
for spec in available_cases:
    mass_handles.append(
        ax.plot(
            spec["simulation"]["time_h"],
            spec["simulation"]["relative_mass_conservation_residual"],
            color=spec["color"],
            linewidth=1.8,
            label=spec["display_label"],
        )[0]
    )

ax.axhline(0.0, color="0.35", linewidth=1.0, linestyle="--")
ax.set_xlabel("Time (h)")
ax.set_ylabel("Deuterium mass-balance residual / initial inventory (-)")
ax.set_xlim(0, 4.2)
ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
ax.grid(visible=True, which="major", color="0.65", linestyle="--", alpha=0.3)
ax.legend(handles=mass_handles, loc="best")
ax.minorticks_on()

plt.savefig(
    "val-2k_natural_oxide_mass_conservation.png",
    bbox_inches="tight",
    dpi=300,
)
plt.close(fig)

# Stage 7: track the total oxygen inventory in the sample for each available
# oxygen-field case using the same case colors as the TDS comparison figure.
oxygen_cases = [
    spec
    for spec in available_cases
    if spec["simulation"]["oxygen_inventory_in_sample"] is not None
]
if oxygen_cases:
    fig, ax = plt.subplots(figsize=(6.5, 4.8))

    oxygen_handles = []
    for spec in oxygen_cases:
        oxygen_handles.append(
            ax.plot(
                spec["simulation"]["time_h"],
                spec["simulation"]["oxygen_inventory_in_sample"],
                color=spec["color"],
                linewidth=1.8,
                label=spec["display_label"],
            )[0]
        )

    ax.set_xlabel("Time (h)")
    ax.set_ylabel("Oxygen inventory in sample (atoms/m$^2$)")
    ax.set_xlim(0, 4.2)
    ax.set_ylim(bottom=0)
    ax.grid(visible=True, which="major", color="0.65", linestyle="--", alpha=0.3)

    ax_temperature = ax.twinx()
    temperature_handle = ax_temperature.plot(
        baseline_case["time_h"],
        baseline_case["temperature_k"],
        linestyle="-",
        color="k",
        linewidth=1.5,
        label="TMAP8 temperature history",
    )[0]

    ax_temperature.set_ylabel("Temperature (K)")
    ax_temperature.set_ylim(280, 1100)
    ax.legend(handles=oxygen_handles + [temperature_handle], loc="best")
    ax.minorticks_on()

    plt.savefig(
        "val-2k_natural_oxide_oxygen_inventory.png",
        bbox_inches="tight",
        dpi=300,
    )
    plt.close(fig)

# Stage 8: plot the oxygen conservation residual for every oxygen-field case
# that has the required bookkeeping columns.
oxygen_cases = [
    spec
    for spec in available_cases
    if spec["simulation"]["relative_oxygen_mass_conservation_residual"] is not None
]
if oxygen_cases:
    fig, ax = plt.subplots(figsize=(6.5, 4.8))

    oxygen_handles = []
    for spec in oxygen_cases:
        oxygen_handles.append(
            ax.plot(
                spec["simulation"]["time_h"],
                spec["simulation"]["relative_oxygen_mass_conservation_residual"],
                color=spec["color"],
                linewidth=1.8,
                label=spec["display_label"],
            )[0]
        )

    ax.axhline(0.0, color="0.35", linewidth=1.0, linestyle="--")
    ax.set_xlabel("Time (h)")
    ax.set_ylabel("Oxygen conservation residual / initial inventory (-)")
    ax.set_xlim(0, 4.2)
    ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
    ax.grid(visible=True, which="major", color="0.65", linestyle="--", alpha=0.3)
    ax.legend(handles=oxygen_handles, loc="best")
    ax.minorticks_on()

    plt.savefig(
        "val-2k_natural_oxide_oxygen_conservation.png",
        bbox_inches="tight",
        dpi=300,
    )
    plt.close(fig)

# Stage 9: generate the 15 nm initial concentration profile used to start the
# desorption calculation and mark the oxide, damaged tungsten, and bulk
# sections in the plotted depth range.
distance_to_surface_microns = profile_case["x"]
deuterium_total = profile_case["deuterium_total_physical"]
deuterium_mobile = profile_case["deuterium_mobile_physical"]
deuterium_trapped_intrinsic = profile_case["deuterium_trapped_intrinsic_physical"]
deuterium_trapped_1 = profile_case["deuterium_trapped_1_physical"]
deuterium_trapped_2 = profile_case["deuterium_trapped_2_physical"]
deuterium_trapped_3 = profile_case["deuterium_trapped_3_physical"]
deuterium_trapped_4 = profile_case["deuterium_trapped_4_physical"]
deuterium_trapped_5 = profile_case["deuterium_trapped_5_physical"]

fig, ax = plt.subplots(figsize=(6.5, 5.5))
xmax_profile = max(profile_depth_um, float(np.max(distance_to_surface_microns)))
ax.axvspan(0.0, oxide_thickness_profile_um, color="0.72", alpha=0.95)
ax.axvspan(
    oxide_thickness_profile_um,
    damage_depth_um,
    color="0.84",
    alpha=0.9,
)
ax.axvspan(damage_depth_um, xmax_profile, color="0.93", alpha=0.95)
ax.axvline(oxide_thickness_profile_um, color="0.4", linewidth=1.0, linestyle="--")
ax.axvline(damage_depth_um, color="0.4", linewidth=1.0, linestyle="--")
ax.plot(
    distance_to_surface_microns,
    deuterium_total,
    color="k",
    linewidth=2.0,
    label="Total D",
)
ax.plot(
    distance_to_surface_microns,
    deuterium_mobile,
    color="tab:blue",
    linestyle="--",
    label="Mobile D",
)
ax.plot(
    distance_to_surface_microns,
    deuterium_trapped_intrinsic,
    color="tab:purple",
    label="Intrinsic trap D",
)
ax.plot(
    distance_to_surface_microns,
    deuterium_trapped_1,
    color="tab:orange",
    label="Trap 1 D",
)
ax.plot(
    distance_to_surface_microns,
    deuterium_trapped_2,
    color="tab:green",
    label="Trap 2 D",
)
ax.plot(
    distance_to_surface_microns,
    deuterium_trapped_3,
    color="tab:red",
    label="Trap 3 D",
)
ax.plot(
    distance_to_surface_microns,
    deuterium_trapped_4,
    color="tab:brown",
    label="Trap 4 D",
)
ax.plot(
    distance_to_surface_microns,
    deuterium_trapped_5,
    color="tab:pink",
    label="Trap 5 D",
)

ax.set_xlabel("Distance to tungsten surface (um)")
ax.set_ylabel("Deuterium concentration (atoms/m$^3$)")
ax.set_xlim(0, xmax_profile)
ax.set_ylim(0, 10.2e26)
ymax = ax.get_ylim()[1]
ax.text(10.1 * oxide_thickness_profile_um, 0.97 * ymax, "Oxide", ha="center", va="top")
ax.text(
    0.5 * (oxide_thickness_profile_um + damage_depth_um),
    0.97 * ymax,
    "Damaged W",
    ha="center",
    va="top",
)
ax.text(
    0.5 * (damage_depth_um + xmax_profile),
    0.97 * ymax,
    "Bulk W",
    ha="center",
    va="top",
)
ax.grid(visible=True, which="major", color="0.65", linestyle="--", alpha=0.3)
ax.legend(loc="center right")
ax.minorticks_on()

plt.savefig("val-2k_natural_oxide_profile.png", bbox_inches="tight", dpi=300)
plt.close(fig)
