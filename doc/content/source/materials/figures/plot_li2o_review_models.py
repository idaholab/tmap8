#!/usr/bin/env python3

"""
Plot the Li$_2$O tritium diffusivity and hydrogen isotope solubility correlations implemented in
TMAP8 (TritiumDiffusivityLi2O and TritiumSolubilityLi2O).

Intended use: regenerate the two documentation figures that are included with `!media` in
TritiumDiffusivityLi2O.md and TritiumSolubilityLi2O.md. Run it from any directory:

    python plot_li2o_review_models.py

Outputs (written next to this script):
    li2o_diffusivity_models.png  -- D (m^2/s) versus 1000/T, one curve per model
    li2o_solubility_models.png   -- K_s (atm^1/2) versus 1000/T, one curve per model

Each curve is drawn only over the documented temperature range of its model. The coefficients and
temperature ranges are read from include/materials/Li2OPropertyHelper.h (the switch statements in
diffusivityModelData and solubilityModelData), and the ideal gas constant from MOOSE's
PhysicalConstants.h, so the figures cannot drift from the C++. Only the
plot labels and the functional forms, D = D0 exp(-Ea / (R T)) and log10(K_s) = a / T + b, are defined
here; if the header's structs or switch layout change, update parse_helper_header accordingly.
Temperatures are in K, activation energies in J/mol and the diffusivity in m^2/s.
"""

import ast
import operator
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec

SCRIPT_DIR = Path(__file__).resolve().parent
FIG_DIR = SCRIPT_DIR
REPO_DIR = SCRIPT_DIR.parents[4]
HELPER_HEADER = REPO_DIR / "include" / "materials" / "Li2OPropertyHelper.h"
# Header defining PhysicalConstants::ideal_gas_constant, which Li2OPropertyHelper.h uses through
# TMAP8PhysicalConstants.h
CONSTANTS_HEADER = REPO_DIR / "moose" / "modules" / "misc" / "include" / "utils" / "PhysicalConstants.h"

# Plot labels, keyed by the model names used in Li2OPropertyHelper.h
DIFFUSIVITY_LABELS = {
    "Ohira1989": "Ohira1989, unirradiated single crystal",
    "Tanifuji1987": "Tanifuji1987, neutron-irradiated single crystal",
    "Kurasawa1991": "Kurasawa1991, in-situ single crystal",
    "Terai1988Grain": "Terai1988Grain, neutron-irradiated polycrystal grain",
    "Terai1988GrainBoundary": (
        "Terai1988GrainBoundary, neutron-irradiated polycrystal grain boundary"
    ),
}

SOLUBILITY_LABELS = {
    "Ohira1989Tritium": "Ohira1989Tritium, tritium in unirradiated single crystal",
    "Ohira1989Hydrogen": "Ohira1989Hydrogen, hydrogen in unirradiated single crystal",
}


def evaluate_number(expression: str) -> float:
    """Evaluate a C++ numeric literal or simple arithmetic such as `450.0 + 273.15`."""

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            value = visit(node.operand)
            return -value if isinstance(node.op, ast.USub) else value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
            return _OPERATORS[type(node.op)](visit(node.left), visit(node.right))
        raise ValueError(f"Unsupported expression in {HELPER_HEADER.name}: {expression!r}")

    return visit(ast.parse(expression.strip(), mode="eval"))


_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}


def parse_ideal_gas_constant(header: Path) -> float:
    """Read PhysicalConstants::ideal_gas_constant (J/mol/K) from the MOOSE constants header."""
    match = re.search(r"ideal_gas_constant\s*=\s*([^;]+);", header.read_text())
    if match is None:
        raise ValueError(f"Could not find ideal_gas_constant in {header}")
    return evaluate_number(match.group(1))


def parse_helper_header(header: Path):
    """
    Read the model coefficients and temperature ranges from Li2OPropertyHelper.h.

    Each model is a `case <Enum>::<Name>: return {{citation, min_T, max_T, note}, c1, c2};` entry
    in diffusivityModelData / solubilityModelData. The string literals are dropped and the
    remaining numbers are, in order: min_T, max_T, then the two model coefficients.
    """
    text = header.read_text()
    models = {"Diffusivity": {}, "Solubility": {}}
    pattern = re.compile(
        r"case\s+(Diffusivity|Solubility)Model::(\w+)\s*:\s*return\s*\{(.*?)\};", re.DOTALL
    )
    for kind, name, body in pattern.findall(text):
        body = re.sub(r'"(?:[^"\\]|\\.)*"', "", body)  # drop (concatenated) string literals
        numbers = [
            evaluate_number(item)
            for item in body.replace("{", "").replace("}", "").split(",")
            if item.strip()
        ]
        if len(numbers) != 4:
            raise ValueError(
                f"Expected 4 numbers for {kind}Model::{name} in {header.name}, got {numbers}"
            )
        models[kind][name] = numbers
    return models["Diffusivity"], models["Solubility"]


def build_models():
    """Combine the numbers parsed from the C++ header with the plot labels defined here."""
    diffusivity, solubility = parse_helper_header(HELPER_HEADER)
    if set(diffusivity) != set(DIFFUSIVITY_LABELS) or set(solubility) != set(SOLUBILITY_LABELS):
        raise ValueError(
            f"Models in {HELPER_HEADER.name} do not match the labels in this script: "
            f"{sorted(diffusivity)} / {sorted(solubility)}"
        )
    diffusivity_models = {
        name: {
            "temp_range_k": (t_min, t_max),
            "prefactor_m2_s": prefactor,
            "activation_j_mol": activation,
            "label": DIFFUSIVITY_LABELS[name],
        }
        for name, (t_min, t_max, prefactor, activation) in diffusivity.items()
    }
    solubility_models = {
        name: {
            "temp_range_k": (t_min, t_max),
            "a": a,
            "b": b,
            "label": SOLUBILITY_LABELS[name],
        }
        for name, (t_min, t_max, a, b) in solubility.items()
    }
    return diffusivity_models, solubility_models


R = parse_ideal_gas_constant(CONSTANTS_HEADER)  # J/mol/K
DIFFUSIVITY_MODELS, SOLUBILITY_MODELS = build_models()


def apply_validation_style():
    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.labelsize": 11,
            "xtick.labelsize": 11,
            "ytick.labelsize": 11,
            "legend.fontsize": 10,
        }
    )


def diffusivity_m2_s(
    prefactor_m2_s: float, activation_j_mol: float, temperature_k: np.ndarray
):
    return prefactor_m2_s * np.exp(-activation_j_mol / (R * temperature_k))


def solubility_atm_0_5(a: float, b: float, temperature_k: np.ndarray):
    return 10.0 ** (a / temperature_k + b)


def inverse_temperature_axis(temperature_k: np.ndarray):
    return 1000.0 / temperature_k


def temperature_from_inverse_axis(inverse_temperature):
    inverse_temperature = np.asarray(inverse_temperature)
    result = np.full_like(inverse_temperature, np.nan, dtype=float)
    mask = inverse_temperature != 0.0
    result[mask] = 1000.0 / inverse_temperature[mask]
    return result


def inverse_axis_from_temperature(temperature_k):
    temperature_k = np.asarray(temperature_k)
    result = np.full_like(temperature_k, np.nan, dtype=float)
    mask = temperature_k != 0.0
    result[mask] = 1000.0 / temperature_k[mask]
    return result


def add_temperature_top_axis(ax, temperature_ticks_k):
    secax = ax.secondary_xaxis(
        "top", functions=(temperature_from_inverse_axis, inverse_axis_from_temperature)
    )
    secax.set_xlabel("Temperature (K)")
    secax.set_xticks(temperature_ticks_k)
    secax.set_xticklabels([f"{tick:.0f}" for tick in temperature_ticks_k])
    return secax


def apply_axes_style(ax, xlabel: str, ylabel: str):
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(visible=True, which="major", color="0.65", linestyle="--", alpha=0.3)
    ax.minorticks_on()


def order_legend_by_reference_y(line_info, reference_temperature_k: float):
    ordered = sorted(
        line_info,
        key=lambda item: np.interp(
            reference_temperature_k, item["temperature_k"], item["y_values"]
        ),
        reverse=True,
    )
    handles = [item["handle"] for item in ordered]
    labels = [item["label"] for item in ordered]
    return handles, labels


def plot_diffusivity():
    fig = plt.figure(figsize=[6.5, 7.0])
    gs = gridspec.GridSpec(1, 1)
    ax = fig.add_subplot(gs[0])
    line_info = []

    for model in DIFFUSIVITY_MODELS.values():
        t_min, t_max = model["temp_range_k"]
        temperature = np.linspace(t_min, t_max, 250)
        inverse_temperature = inverse_temperature_axis(temperature)
        diffusivity = diffusivity_m2_s(
            model["prefactor_m2_s"], model["activation_j_mol"], temperature
        )
        (line,) = ax.plot(
            inverse_temperature, diffusivity, linewidth=2.0, label=model["label"]
        )
        line_info.append(
            {
                "handle": line,
                "label": model["label"],
                "temperature_k": temperature,
                "y_values": diffusivity,
            }
        )

    ax.set_yscale("log")
    apply_axes_style(
        ax,
        r"1000 / Temperature (K$^{-1}$)",
        r"$D$ (m$^2$/s)",
    )
    add_temperature_top_axis(ax, [600.0, 700.0, 800.0, 900.0, 1000.0])
    handles, labels = order_legend_by_reference_y(line_info, 700.0)
    ax.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        borderaxespad=0.0,
        ncol=1,
    )
    fig.tight_layout()
    fig.savefig(FIG_DIR / "li2o_diffusivity_models.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_solubility():
    fig = plt.figure(figsize=[6.5, 5.5])
    gs = gridspec.GridSpec(1, 1)
    ax = fig.add_subplot(gs[0])
    line_info = []

    for model in SOLUBILITY_MODELS.values():
        t_min, t_max = model["temp_range_k"]
        temperature = np.linspace(t_min, t_max, 250)
        inverse_temperature = inverse_temperature_axis(temperature)
        solubility = solubility_atm_0_5(model["a"], model["b"], temperature)
        (line,) = ax.plot(
            inverse_temperature, solubility, linewidth=2.0, label=model["label"]
        )
        line_info.append(
            {
                "handle": line,
                "label": model["label"],
                "temperature_k": temperature,
                "y_values": solubility,
            }
        )

    ax.set_yscale("log")
    apply_axes_style(
        ax,
        r"1000 / Temperature (K$^{-1}$)",
        r"$K_s$ (atm$^{1/2}$)",
    )
    add_temperature_top_axis(
        ax, [400.0, 500.0, 600.0, 700.0, 800.0, 900.0, 1000.0, 1100.0]
    )
    handles, labels = order_legend_by_reference_y(line_info, 700.0)
    ax.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        borderaxespad=0.0,
        ncol=1,
    )
    fig.tight_layout()
    fig.savefig(FIG_DIR / "li2o_solubility_models.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    apply_validation_style()
    plot_diffusivity()
    plot_solubility()


if __name__ == "__main__":
    main()
