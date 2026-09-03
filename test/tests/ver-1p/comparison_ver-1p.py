#!/usr/bin/env python3

"""Analytical comparison for the Fuerst et al. (2023) PAV test."""

from __future__ import annotations

import csv
import math
import os
import re
import sys
from pathlib import Path
from matplotlib.patches import Rectangle

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from scipy.optimize import brentq

SCRIPT_FOLDER = Path(os.path.abspath(__file__)).parent
os.chdir(SCRIPT_FOLDER)

_NUMERIC_LITERAL = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?")


def locate_input_file() -> Path:
    """Return the location of the ver-1p input file."""
    candidates = [SCRIPT_FOLDER / "ver-1p.i"]
    candidates.extend(
        parent / "test" / "tests" / "ver-1p" / "ver-1p.i"
        for parent in SCRIPT_FOLDER.parents
    )

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    searched = "\n  ".join(str(path) for path in candidates)
    raise FileNotFoundError(
        f"Could not find ver-1p input file. Searched:\n  {searched}"
    )


def get_numeric_parameter(parameter_name: str) -> float:
    """Read a numerical top level parameter from ver-1p.i."""
    input_file = locate_input_file()

    with input_file.open(encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped.startswith(f"{parameter_name} ="):
                continue

            raw_value = stripped.split("=", maxsplit=1)[1]
            raw_value = raw_value.split("#", maxsplit=1)[0].strip()

            if (
                len(raw_value) >= 2
                and raw_value[0] == raw_value[-1]
                and raw_value[0] in {"'", '"'}
            ):
                raw_value = raw_value[1:-1].strip()

            if raw_value.startswith("${units"):
                raw_value = raw_value[len("${units") :].lstrip()

            match = _NUMERIC_LITERAL.match(raw_value)
            if match is None:
                raise ValueError(
                    f"Parameter {parameter_name!r} in {input_file} is not a "
                    "direct numerical value that this script can read."
                )

            return float(match.group(0))

    raise KeyError(f"Could not find parameter {parameter_name!r} in {input_file}")


# Model parameters read from ver-1p.i
TEMPERATURE = get_numeric_parameter("temperature")
GAS_CONSTANT = get_numeric_parameter("gas_constant")
CONCENTRATION_INLET = get_numeric_parameter("concentration_inlet")
REYNOLDS_NUMBER = get_numeric_parameter("reynolds_number")
TUBE_LENGTH = get_numeric_parameter("tube_length")
RADIUS_INNER_WALL = get_numeric_parameter("radius_inner_wall")
RADIUS_OUTER_WALL = get_numeric_parameter("radius_outer_wall")
NUMBER_AXIAL_SEGMENTS = int(get_numeric_parameter("number_axial_segments"))
VELOCITY_PBLI = get_numeric_parameter("velocity_PbLi")
SOLUBILITY_FACTOR_PBLI = get_numeric_parameter("solubility_factor_PbLi")
RECOMBINATION_COEFFICIENT = get_numeric_parameter("recombination_coefficient")
MOLAR_MASS_PBLI_ATOM = get_numeric_parameter("molar_mass_PbLi_atom")

OUTER_TO_INNER_AREA_RATIO = RADIUS_OUTER_WALL / RADIUS_INNER_WALL
RECOMBINATION_COEFFICIENT_INNER_AREA = (
    OUTER_TO_INNER_AREA_RATIO * RECOMBINATION_COEFFICIENT
)

# Verification criterion for the 20 segment solution
MAX_ERROR_PERCENT = 1.0


def locate_gold_csv() -> Path:
    """Return the location of the ver-1p gold CSV file."""
    candidates = [SCRIPT_FOLDER / "gold" / "ver-1p_out.csv"]
    candidates.extend(
        parent / "test" / "tests" / "ver-1p" / "gold" / "ver-1p_out.csv"
        for parent in SCRIPT_FOLDER.parents
    )

    for candidate in candidates:
        if candidate.is_file():
            return candidate

    searched = "\n  ".join(str(path) for path in candidates)
    raise FileNotFoundError(f"Could not find ver-1p gold CSV. Searched:\n  {searched}")


def surface_concentration(
    concentration_bulk: float,
    partition_ratio: float,
    radial_transport_coefficient: float,
) -> float:
    """Return the vanadium concentration at the vacuum surface."""
    radical = (
        1.0
        + 4.0
        * radial_transport_coefficient
        * RECOMBINATION_COEFFICIENT_INNER_AREA
        * partition_ratio
        * concentration_bulk
    )
    return 2.0 * partition_ratio * concentration_bulk / (1.0 + math.sqrt(radical))


def analytical_solution() -> dict[str, object]:
    """Return the continuous analytical axial concentration solution."""
    # PbLi properties.
    diffusivity_pbli = 8.30e-9 * math.exp(-7.37e3 / (GAS_CONSTANT * TEMPERATURE))
    density_pbli = 10520.35 - 1.19051 * TEMPERATURE
    atomic_concentration_pbli = density_pbli / MOLAR_MASS_PBLI_ATOM
    solubility_pbli = SOLUBILITY_FACTOR_PBLI * atomic_concentration_pbli

    # Vanadium properties.
    diffusivity_vanadium = 2.90e-8 * math.exp(-4.2e3 / (GAS_CONSTANT * TEMPERATURE))
    solubility_vanadium = 0.138 * math.exp(29.0e3 / (GAS_CONSTANT * TEMPERATURE))

    # Liquid mass transfer.
    hydraulic_diameter = 2.0 * RADIUS_INNER_WALL
    volumetric_flow_rate_pbli = VELOCITY_PBLI * math.pi * RADIUS_INNER_WALL**2
    kinematic_viscosity_pbli = VELOCITY_PBLI * hydraulic_diameter / REYNOLDS_NUMBER
    schmidt_number = kinematic_viscosity_pbli / diffusivity_pbli
    sherwood_number = 0.023 * REYNOLDS_NUMBER**0.83 * schmidt_number ** (1.0 / 3.0)
    mass_transfer_coefficient_pbli = (
        sherwood_number * diffusivity_pbli / hydraulic_diameter
    )

    # Radial transport parameters.
    partition_ratio = solubility_vanadium / solubility_pbli
    membrane_resistance = (
        RADIUS_INNER_WALL
        * math.log(RADIUS_OUTER_WALL / RADIUS_INNER_WALL)
        / diffusivity_vanadium
    )
    radial_transport_coefficient = (
        partition_ratio / mass_transfer_coefficient_pbli + membrane_resistance
    )

    surface_concentration_inlet = surface_concentration(
        CONCENTRATION_INLET,
        partition_ratio,
        radial_transport_coefficient,
    )

    def axial_residual(
        surface_concentration_value: float,
        axial_position: float,
    ) -> float:
        return (
            1.0 / surface_concentration_value
            - 1.0 / surface_concentration_inlet
            - 2.0
            * radial_transport_coefficient
            * RECOMBINATION_COEFFICIENT_INNER_AREA
            * math.log(surface_concentration_value / surface_concentration_inlet)
            - (
                2.0
                * math.pi
                * RADIUS_INNER_WALL
                * partition_ratio
                * RECOMBINATION_COEFFICIENT_INNER_AREA
                / volumetric_flow_rate_pbli
            )
            * axial_position
        )

    concentrations = []
    for index in range(1, NUMBER_AXIAL_SEGMENTS + 1):
        axial_position = index * TUBE_LENGTH / NUMBER_AXIAL_SEGMENTS
        surface_concentration_value = brentq(
            axial_residual,
            surface_concentration_inlet * 1.0e-8,
            surface_concentration_inlet,
            args=(axial_position,),
            xtol=1.0e-14,
            rtol=1.0e-14,
        )
        concentration_bulk = (
            surface_concentration_value
            + radial_transport_coefficient
            * RECOMBINATION_COEFFICIENT_INNER_AREA
            * surface_concentration_value**2
        ) / partition_ratio
        concentrations.append(concentration_bulk)

    concentration_outlet = concentrations[-1]
    efficiency = 1.0 - concentration_outlet / CONCENTRATION_INLET

    # Average flux on the inner surface.
    total_permeation_area = 2.0 * math.pi * RADIUS_INNER_WALL * TUBE_LENGTH
    average_permeation_flux = (
        volumetric_flow_rate_pbli
        * (CONCENTRATION_INLET - concentration_outlet)
        / total_permeation_area
    )

    return {
        "concentrations": concentrations,
        "outlet": concentration_outlet,
        "efficiency": efficiency,
        "average_flux": average_permeation_flux,
    }


def read_last_csv_row(path: Path) -> dict[str, str]:
    """Return the final data row in a CSV file."""
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))

    if not rows:
        raise RuntimeError(f"No data rows found in {path}")

    return rows[-1]


def value(row: dict[str, str], name: str) -> float:
    """Return a named CSV value as a float."""
    if name not in row:
        raise KeyError(f"Column {name!r} is missing from the TMAP8 CSV")

    return float(row[name])


def relative_error_percent(
    actual: float,
    expected: float,
) -> float:
    """Return the absolute relative error as a percentage."""
    return abs((actual - expected) / expected) * 100.0


def make_schematic() -> None:
    """Generate a schematic of the segmented PAV verification model."""
    figure = plt.figure(figsize=(11.0, 6.4))
    axis = figure.add_axes((0.03, 0.04, 0.94, 0.92))

    axis.set_xlim(0.0, 12.0)
    axis.set_ylim(0.0, 7.0)
    axis.axis("off")

    highlight_color = "#dce8f5"
    highlight_edge = "#6f8fae"
    membrane_color = "#d9d9d9"
    vacuum_color = "#eef5e9"
    radial_arrow_color = "#b94a48"

    # ------------------------------------------------------------------
    # Vertical axial permeator
    # ------------------------------------------------------------------
    pipe_left = 2.55
    pipe_bottom = 0.85
    pipe_width = 1.00
    pipe_height = 5.20

    pipe_right = pipe_left + pipe_width
    pipe_top = pipe_bottom + pipe_height
    pipe_center = pipe_left + pipe_width / 2.0

    segment_height = pipe_height / NUMBER_AXIAL_SEGMENTS

    axis.add_patch(
        Rectangle(
            (pipe_left, pipe_bottom),
            pipe_width,
            pipe_height,
            facecolor="white",
            edgecolor="black",
            linewidth=1.8,
            zorder=1,
        )
    )

    for segment_index in range(1, NUMBER_AXIAL_SEGMENTS):
        y_position = pipe_bottom + segment_index * segment_height

        axis.plot(
            [pipe_left, pipe_right],
            [y_position, y_position],
            color="0.70",
            linewidth=0.6,
            zorder=2,
        )

    # ------------------------------------------------------------------
    # Axial PbLi flow
    # ------------------------------------------------------------------
    axis.annotate(
        "",
        xy=(pipe_center, pipe_top - 0.16),
        xytext=(pipe_center, pipe_bottom + 0.16),
        arrowprops={
            "arrowstyle": "->",
            "linewidth": 2.0,
            "color": "black",
        },
        zorder=4,
    )

    axis.text(
        pipe_center,
        pipe_bottom - 0.48,
        "PbLi + T",
        ha="center",
        va="top",
        fontsize=11,
    )

    axis.text(
        pipe_left - 0.15,
        pipe_bottom,
        r"$z=0$",
        ha="right",
        va="center",
        fontsize=10,
    )

    axis.text(
        pipe_left - 0.15,
        pipe_top,
        rf"$z={TUBE_LENGTH:.0f}\ \mathrm{{m}}$",
        ha="right",
        va="center",
        fontsize=10,
    )

    axis.text(
        pipe_right + 0.16,
        pipe_bottom,
        r"$C_{\mathrm{in}}$",
        ha="left",
        va="center",
        fontsize=12,
    )

    axis.text(
        pipe_right + 0.16,
        pipe_top,
        r"$C_{\mathrm{out}}$",
        ha="left",
        va="center",
        fontsize=12,
    )

    axis.text(
        pipe_center,
        pipe_top + 0.45,
        "20 axial control volumes",
        ha="center",
        fontsize=12,
        fontweight="bold",
    )

    # ------------------------------------------------------------------
    # Show one representative axial control volume
    # ------------------------------------------------------------------
    selected_segment = NUMBER_AXIAL_SEGMENTS // 2

    selected_bottom = pipe_bottom + selected_segment * segment_height
    selected_top = selected_bottom + segment_height
    selected_center = (selected_bottom + selected_top) / 2.0

    highlight_padding_x = 0.12
    highlight_padding_y = 0.07

    highlighted_left = pipe_left - highlight_padding_x
    highlighted_right = pipe_right + highlight_padding_x
    highlighted_bottom = selected_bottom - highlight_padding_y
    highlighted_top = selected_top + highlight_padding_y

    axis.add_patch(
        Rectangle(
            (highlighted_left, highlighted_bottom),
            highlighted_right - highlighted_left,
            highlighted_top - highlighted_bottom,
            facecolor=highlight_color,
            edgecolor=highlight_edge,
            linewidth=2.2,
            zorder=3,
        )
    )

    # Redraw axial flow through the highlighted segment.
    axis.annotate(
        "",
        xy=(pipe_center, selected_top - 0.02),
        xytext=(pipe_center, selected_bottom + 0.02),
        arrowprops={
            "arrowstyle": "->",
            "linewidth": 1.5,
            "color": "black",
        },
        zorder=5,
    )

    # ------------------------------------------------------------------
    # Axial segment balance
    # ------------------------------------------------------------------
    relationship_x = 1.18

    axis.text(
        relationship_x,
        selected_center + 0.68,
        "Axial segment balance",
        ha="center",
        va="center",
        fontsize=10,
        fontweight="bold",
    )

    axis.text(
        relationship_x,
        selected_center + 0.20,
        (r"$C_i-C_{i-1}" r"+\frac{A_{\mathrm{seg}}}{Q}" r"J(C_{i-1})=0$"),
        ha="center",
        va="center",
        fontsize=10,
    )

    axis.text(
        relationship_x,
        selected_center - 0.45,
        "Outlet of segment $i-1$\n" "is the inlet of segment $i$",
        ha="center",
        va="center",
        fontsize=8.5,
    )

    segment_length = TUBE_LENGTH / NUMBER_AXIAL_SEGMENTS

    # ------------------------------------------------------------------
    # Symmetric radial permeation from the selected axial segment
    # ------------------------------------------------------------------
    radial_arrow_y = (
        selected_center - 0.07,
        selected_center,
        selected_center + 0.07,
    )

    for y_position in radial_arrow_y:
        axis.annotate(
            "",
            xy=(highlighted_left - 0.18, y_position),
            xytext=(highlighted_left + 0.05, y_position),
            arrowprops={
                "arrowstyle": "->",
                "linewidth": 1.3,
                "color": radial_arrow_color,
            },
            zorder=5,
        )

        axis.annotate(
            "",
            xy=(highlighted_right + 0.18, y_position),
            xytext=(highlighted_right - 0.05, y_position),
            arrowprops={
                "arrowstyle": "->",
                "linewidth": 1.3,
                "color": radial_arrow_color,
            },
            zorder=5,
        )

    model_left = 4.70
    model_right = 11.60
    model_bottom = 0.85
    model_top = 5.75

    axis.add_patch(
        Rectangle(
            (model_left, model_bottom),
            model_right - model_left,
            model_top - model_bottom,
            facecolor=highlight_color,
            edgecolor=highlight_edge,
            linewidth=1.8,
            zorder=-3,
        )
    )

    # Connector lines from the highlighted axial segment.
    axis.plot(
        [highlighted_right, model_left],
        [highlighted_top, model_top - 0.40],
        color=highlight_edge,
        linewidth=1.2,
    )

    axis.plot(
        [highlighted_right, model_left],
        [highlighted_bottom, model_bottom + 0.40],
        color=highlight_edge,
        linewidth=1.2,
    )

    axis.text(
        (model_left + model_right) / 2.0,
        model_top - 0.28,
        "Radial transport within one axial control volume",
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold",
    )

    # ------------------------------------------------------------------
    # Radial regions
    # ------------------------------------------------------------------
    pbli_left = 5.05
    radius_inner_location = 7.75
    radius_outer_location = 9.65
    vacuum_right = 11.25

    region_bottom = 1.20
    region_top = 4.95

    axis.add_patch(
        Rectangle(
            (pbli_left, region_bottom),
            radius_inner_location - pbli_left,
            region_top - region_bottom,
            facecolor=highlight_color,
            edgecolor="none",
            zorder=-2,
        )
    )

    axis.add_patch(
        Rectangle(
            (radius_inner_location, region_bottom),
            radius_outer_location - radius_inner_location,
            region_top - region_bottom,
            facecolor=membrane_color,
            edgecolor="none",
            zorder=-2,
        )
    )

    axis.add_patch(
        Rectangle(
            (radius_outer_location, region_bottom),
            vacuum_right - radius_outer_location,
            region_top - region_bottom,
            facecolor=vacuum_color,
            edgecolor="none",
            zorder=-2,
        )
    )

    # Interface boundaries.
    axis.plot(
        [radius_inner_location, radius_inner_location],
        [region_bottom, region_top],
        color="black",
        linewidth=1.3,
    )

    axis.plot(
        [radius_outer_location, radius_outer_location],
        [region_bottom, region_top],
        color="black",
        linewidth=1.3,
    )

    # Region centers.
    pbli_center = (pbli_left + radius_inner_location) / 2.0

    membrane_center = (radius_inner_location + radius_outer_location) / 2.0

    vacuum_center = (radius_outer_location + vacuum_right) / 2.0

    # ------------------------------------------------------------------
    # Region titles
    # ------------------------------------------------------------------
    axis.text(
        pbli_center,
        4.62,
        "Bulk PbLi",
        ha="center",
        fontsize=11,
        fontweight="bold",
    )

    axis.text(
        membrane_center,
        4.62,
        "Membrane",
        ha="center",
        fontsize=11,
        fontweight="bold",
    )

    axis.text(
        vacuum_center,
        4.62,
        "Vacuum",
        ha="center",
        fontsize=11,
        fontweight="bold",
    )

    # ------------------------------------------------------------------
    # Process descriptions
    # ------------------------------------------------------------------
    axis.text(
        pbli_center,
        3.88,
        "Liquid mass transfer",
        ha="center",
        fontsize=9,
    )

    axis.text(
        membrane_center,
        3.88,
        "Cylindrical diffusion",
        ha="center",
        fontsize=9,
    )

    transport_y = 3.22

    axis.annotate(
        "",
        xy=(10.95, transport_y),
        xytext=(5.30, transport_y),
        arrowprops={
            "arrowstyle": "->",
            "linewidth": 2.0,
            "color": "black",
        },
    )

    # ------------------------------------------------------------------
    # Transport equations
    # ------------------------------------------------------------------
    axis.text(
        pbli_center,
        2.62,
        r"$J_i=K_T(C-C_{L2})$",
        ha="center",
        fontsize=10,
    )

    axis.text(
        membrane_center,
        2.62,
        r"$C_S$",
        ha="center",
        fontsize=11,
    )

    axis.text(
        vacuum_center,
        2.62,
        r"$J_o=K_R C_{S2}^{\,2}$",
        ha="center",
        fontsize=10,
    )

    # ------------------------------------------------------------------
    # Interface information

    axis.text(
        radius_inner_location - 0.28,
        2.04,
        "PbLi / V interface",
        ha="right",
        va="center",
        fontsize=9,
    )

    axis.text(
        radius_inner_location - 0.28,
        1.66,
        r"$C_{S1}=(K_S/K_L)C_{L2}$",
        ha="right",
        va="center",
        fontsize=9,
    )

    axis.text(
        radius_inner_location - 0.18,
        1.32,
        r"$r=r_i$",
        ha="right",
        fontsize=10,
    )

    axis.text(
        radius_outer_location + 0.28,
        2.04,
        "Vacuum surface",
        ha="left",
        va="center",
        fontsize=9,
    )

    axis.text(
        vacuum_center,
        1.66,
        r"$p_{\mathrm{vac}}=0$",
        ha="center",
        va="center",
        fontsize=9,
    )

    axis.text(
        radius_outer_location + 0.18,
        1.32,
        r"$r=r_o$",
        ha="left",
        fontsize=10,
    )

    figure.savefig(
        "ver-1p_schematic.png",
        dpi=300,
        bbox_inches="tight",
    )
    plt.close(figure)


def make_plot(
    actual: dict[str, str],
    expected: dict[str, object],
) -> float:
    """Plot TMAP8 and analytical concentration profiles."""
    axial_positions = np.linspace(
        0.0,
        TUBE_LENGTH,
        NUMBER_AXIAL_SEGMENTS + 1,
    )
    tmap8_concentrations = np.array(
        [value(actual, "concentration_inlet_pp")]
        + [
            value(actual, f"concentration_segment_{index:02d}_pp")
            for index in range(1, NUMBER_AXIAL_SEGMENTS + 1)
        ]
    )
    analytical_concentrations = np.array(
        [CONCENTRATION_INLET] + list(expected["concentrations"])
    )

    relative_difference = (
        tmap8_concentrations - analytical_concentrations
    ) / analytical_concentrations
    rmspe = float(np.sqrt(np.mean(relative_difference**2)) * 100.0)

    plt.figure(figsize=(8, 5.4))
    plt.plot(
        axial_positions,
        tmap8_concentrations,
        label=f"TMAP8 ({NUMBER_AXIAL_SEGMENTS} segments)",
        linewidth=2.2,
    )
    plt.plot(
        axial_positions,
        analytical_concentrations,
        "--",
        label="Analytical",
        linewidth=2.0,
    )
    plt.xlabel("Axial location (m)")
    plt.xlim(0.0, TUBE_LENGTH)
    plt.ylabel(r"Bulk concentration (mol m$^{-3}$)")
    plt.grid(
        which="major",
        linestyle="--",
        alpha=0.3,
    )
    plt.minorticks_on()
    plt.legend()
    plt.text(
        0.05,
        0.08,
        f"RMSPE = {rmspe:.3f}%",
        transform=plt.gca().transAxes,
    )
    plt.tight_layout()
    plt.savefig(
        "ver-1p_comparison_analytical_concentration.png",
        dpi=300,
    )
    plt.close()

    return rmspe


def main() -> int:
    """Run the analytical comparison and return an exit status."""
    try:
        gold_csv = locate_gold_csv()
        analytical = analytical_solution()
        actual = read_last_csv_row(gold_csv)
    except (
        FileNotFoundError,
        KeyError,
        OSError,
        RuntimeError,
        ValueError,
    ) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 2

    rmspe = make_plot(actual, analytical)
    make_schematic()
    tmap8_outlet = value(actual, "concentration_segment_20_pp")
    tmap8_efficiency = value(actual, "extraction_efficiency")
    tmap8_flux = value(actual, "average_permeation_flux_mol_m2_s")

    outlet_error = relative_error_percent(
        tmap8_outlet,
        analytical["outlet"],
    )
    efficiency_error = relative_error_percent(
        tmap8_efficiency,
        analytical["efficiency"],
    )
    flux_error = relative_error_percent(
        tmap8_flux,
        analytical["average_flux"],
    )

    print(f"Gold CSV: {gold_csv}")
    print("Analytical outlet concentration: " f"{analytical['outlet']:.12e} mol/m^3")
    print(f"TMAP8 outlet concentration:       {tmap8_outlet:.12e} mol/m^3")
    print(f"Outlet relative error:             {outlet_error:.6f}%")
    print("Analytical extraction efficiency: " f"{analytical['efficiency']:.12e}")
    print(f"TMAP8 extraction efficiency:       {tmap8_efficiency:.12e}")
    print(f"Efficiency relative error:         {efficiency_error:.6f}%")
    print(
        "Analytical average permeation flux: "
        f"{analytical['average_flux']:.12e} mol/m^2/s"
    )
    print("TMAP8 average permeation flux:       " f"{tmap8_flux:.12e} mol/m^2/s")
    print(f"Flux relative error:                 {flux_error:.6f}%")
    print(f"Concentration profile RMSPE:         {rmspe:.6f}%")

    failures = []
    if rmspe > MAX_ERROR_PERCENT:
        failures.append(f"profile RMSPE = {rmspe:.6f}%")
    if outlet_error > MAX_ERROR_PERCENT:
        failures.append(f"outlet error = {outlet_error:.6f}%")
    if efficiency_error > MAX_ERROR_PERCENT:
        failures.append(f"efficiency error = {efficiency_error:.6f}%")
    if flux_error > MAX_ERROR_PERCENT:
        failures.append(f"average flux error = {flux_error:.6f}%")

    if failures:
        print("\nFAILED analytical comparison:", file=sys.stderr)
        for failure in failures:
            print(f"  {failure}", file=sys.stderr)
        print(
            f"Allowed error = {MAX_ERROR_PERCENT:.2f}%",
            file=sys.stderr,
        )
        return 1

    print(
        "TMAP8 agrees with the continuous analytical "
        f"solution within {MAX_ERROR_PERCENT:.1f}%."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
