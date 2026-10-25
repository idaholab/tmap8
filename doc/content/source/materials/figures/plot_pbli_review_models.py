#!/usr/bin/env python3

"""
Plot the PbLi hydrogen isotope diffusivity and solubility correlations implemented in TMAP8
(TritiumDiffusivityPbLi and TritiumSolubilityPbLi).

Intended use: regenerate the three documentation figures that are included with `!media` in
DensityPbLi.md, TritiumDiffusivityPbLi.md and TritiumSolubilityPbLi.md. Run it from any directory:

    python plot_pbli_review_models.py

Outputs (written next to this script):
    pbli_density_models.png      -- rho (g/m^3) versus T
    pbli_diffusivity_models.png  -- D (m^2/s) versus 1000/T, one curve per model
    pbli_solubility_models.png   -- K_s (atoms m^-3 Pa^-1/2) versus 1000/T, one curve per model

Each curve is drawn only over the documented temperature range of its model. The coefficients,
temperature ranges and solubility bases are read from include/materials/PbLiPropertyHelper.h (the
switch statements in diffusivityModelData, solubilityModelData and densityModelData), the molar
masses from the same header, the ideal gas constant and the Avogadro number from MOOSE's
PhysicalConstants.h, so the figures cannot drift from the C++. Only the plot labels and the
functional forms are defined here; if the header's structs or switch layout change, update
parse_model_cases accordingly. Fukada2013MixingRule is not plotted because it depends on
user-provided Sieverts constants.

The diffusivity is D = D0 exp(-Ea / (R T)), with T in K, Ea in J/mol and D in m^2/s. The solubility
is K_s = K0 exp(-Ea / (R T)) B(T) in atoms m^-3 Pa^-1/2, where B = 1 for fits already in atoms,
B = N_A for fits in mol m^-3, and B = N(T) = rho(T) N_A / M for atom-fraction fits, with
rho(T) = rho_0 (1 - beta T) the PbLi density and M the mean atomic mass
(PbLiPropertyHelper::computeSolubility and pbliAtomDensity).
"""

import ast
import math
import operator
import re
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec

SCRIPT_DIR = Path(__file__).resolve().parent
FIG_DIR = SCRIPT_DIR
REPO_DIR = SCRIPT_DIR.parents[4]
HELPER_HEADER = REPO_DIR / "include" / "materials" / "PbLiPropertyHelper.h"
# Header defining PhysicalConstants::ideal_gas_constant and avogadro_number
CONSTANTS_HEADER = (
    REPO_DIR
    / "moose"
    / "modules"
    / "misc"
    / "include"
    / "utils"
    / "PhysicalConstants.h"
)

# Lithium atomic fraction used for the atom-fraction conversion in the figure
LITHIUM_FRACTION = 0.17
# Temperature range (K) over which the density is drawn, since the model has no documented range
DENSITY_PLOT_RANGE_K = (500.0, 1000.0)
# Models documented for a single composition, plotted at that composition
LITHIUM_FRACTION_OVERRIDE = {"Penalva2024": 0.157}

# Plot labels, keyed by the model names used in PbLiPropertyHelper.h
DIFFUSIVITY_LABELS = {
    "Fauvet1988": "Fauvet1988, H (single datum)",
    "Reiter1991": "Reiter1991, H",
    "Terai1992": "Terai1992, T",
    "Maeda2008": "Maeda2008, H",
}

SOLUBILITY_LABELS = {
    "Katsuta1985": "Katsuta1985, H",
    "Fauvet1988": "Fauvet1988, H (single datum)",
    "Maeda2008": "Maeda2008, H",
    "Reiter1991": "Reiter1991, H",
    "Penalva2024": "Penalva2024, H (Pb-15.7Li)",
}

_OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_FUNCTIONS = {"exp": math.exp, "sqrt": math.sqrt, "log": math.log}


def evaluate_number(expression: str, names: dict | None = None) -> float:
    """
    Evaluate a C++ numeric expression such as `450.0 + 273.15` or `std::exp(-8.17) /
    std::sqrt(1.0e5)`, with optional named constants (e.g. `ideal_gas_constant`).
    """
    names = names or {}

    def visit(node):
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.Name) and node.id in names:
            return float(names[node.id])
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.USub, ast.UAdd)):
            value = visit(node.operand)
            return -value if isinstance(node.op, ast.USub) else value
        if isinstance(node, ast.BinOp) and type(node.op) in _OPERATORS:
            return _OPERATORS[type(node.op)](visit(node.left), visit(node.right))
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in _FUNCTIONS
            and len(node.args) == 1
        ):
            return _FUNCTIONS[node.func.id](visit(node.args[0]))
        raise ValueError(
            f"Unsupported expression in {HELPER_HEADER.name}: {expression!r}"
        )

    return visit(ast.parse(expression.replace("std::", "").strip(), mode="eval"))


def parse_constant(header: Path, name: str) -> float:
    """Read the numeric value of `const ... <name> = <number>;` from a C++ header."""
    match = re.search(rf"\b{name}\s*=\s*([^;]+);", header.read_text())
    if match is None:
        raise ValueError(f"Could not find {name} in {header}")
    return evaluate_number(match.group(1))


def split_top_level(text: str) -> list:
    """Split on commas that are outside parentheses, braces and string literals."""
    parts, depth, current, in_string, escaped = [], 0, [], False, False
    for char in text:
        if in_string:
            current.append(char)
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char in "({":
            depth += 1
        elif char in ")}":
            depth -= 1
        elif char == "," and depth == 0:
            parts.append("".join(current).strip())
            current = []
            continue
        current.append(char)
    if "".join(current).strip():
        parts.append("".join(current).strip())
    return parts


def match_parenthesis(text: str, start: int) -> int:
    """Return the index of the parenthesis closing the one at `start`, ignoring strings."""
    depth, in_string, escaped = 0, False, False
    for index in range(start, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue
        if char == '"':
            in_string = True
        elif char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return index
    raise ValueError("Unbalanced parentheses in the helper header")


def parse_model_cases(header: Path, function: str, names: dict) -> dict:
    """
    Read the cases of a `<function>(const <Kind>Model model)` switch in PbLiPropertyHelper.h.

    Each case returns `{pbliMetadata(citation, min_T, max_T, note[, min_x, max_x]), <fields...>}`.
    Returns {model name: (min_T, max_T, [the evaluated numeric fields], [the raw fields])}.
    Comments are dropped, and the string literals in pbliMetadata are skipped.
    """
    text = re.sub(r"//[^\n]*", "", header.read_text())
    start = text.index(function + "(")
    end = text.index("mooseError(", start)
    body = text[start:end]

    cases = {}
    for chunk in re.split(r"\bcase\s+\w+Model::", body)[1:]:
        name = chunk.split(":", 1)[0].strip()
        call = chunk.index("pbliMetadata(")
        open_index = call + len("pbliMetadata")
        close_index = match_parenthesis(chunk, open_index)
        metadata = split_top_level(chunk[open_index + 1 : close_index])
        min_t = evaluate_number(metadata[1], names)
        max_t = evaluate_number(metadata[2], names)
        rest = chunk[close_index + 1 :]
        rest = rest[: rest.index("}")] if "}" in rest else rest
        fields = [f for f in split_top_level(rest.lstrip(" ,\n")) if f]
        cases[name] = (min_t, max_t, fields)
    return cases


def header_names() -> dict:
    """
    Named constants that appear in the model cases of the helper header. The upper bound of models
    without a documented temperature range, `std::numeric_limits<Real>::max()`, is infinity here.
    """
    return {
        "ideal_gas_constant": parse_constant(CONSTANTS_HEADER, "ideal_gas_constant"),
        "no_min_temperature": parse_constant(HELPER_HEADER, "no_min_temperature"),
        "no_max_temperature": float("inf"),
    }


def build_models():
    """Combine the numbers parsed from the C++ header with the plot labels defined here."""
    names = header_names()

    diffusivity = {}
    for name, (t_min, t_max, fields) in parse_model_cases(
        HELPER_HEADER, "diffusivityModelData", names
    ).items():
        # fields: prefactor, activation energy, Isotope::X
        diffusivity[name] = {
            "temp_range_k": (t_min, t_max),
            "prefactor": evaluate_number(fields[0], names),
            "activation_j_mol": evaluate_number(fields[1], names),
            "label": DIFFUSIVITY_LABELS[name],
        }

    solubility = {}
    for name, (t_min, t_max, fields) in parse_model_cases(
        HELPER_HEADER, "solubilityModelData", names
    ).items():
        if name not in SOLUBILITY_LABELS:  # the mixing rule has user-provided inputs
            continue
        # fields: SolubilityBasis::X, prefactor, activation energy, Isotope::X
        solubility[name] = {
            "temp_range_k": (t_min, t_max),
            "basis": fields[0].split("::")[-1],
            "prefactor": evaluate_number(fields[1], names),
            "activation_j_mol": evaluate_number(fields[2], names),
            "label": SOLUBILITY_LABELS[name],
        }

    if set(diffusivity) != set(DIFFUSIVITY_LABELS) or set(solubility) != set(
        SOLUBILITY_LABELS
    ):
        raise ValueError(
            f"Models in {HELPER_HEADER.name} do not match the labels in this script: "
            f"{sorted(diffusivity)} / {sorted(solubility)}"
        )
    return diffusivity, solubility


def parse_density():
    """Read the linear density model rho_0 (1 - beta T) from densityModelData."""
    names = header_names()
    _, _, fields = parse_model_cases(HELPER_HEADER, "densityModelData", names)[
        "LinearExpansion"
    ]
    return evaluate_number(fields[0], names), evaluate_number(fields[1], names)


R = parse_constant(CONSTANTS_HEADER, "ideal_gas_constant")  # J/mol/K
AVOGADRO = parse_constant(CONSTANTS_HEADER, "avogadro_number")  # 1/mol
LITHIUM_MOLAR_MASS = parse_constant(HELPER_HEADER, "lithium_molar_mass")  # g/mol
LEAD_MOLAR_MASS = parse_constant(HELPER_HEADER, "lead_molar_mass")  # g/mol
DENSITY_REFERENCE, DENSITY_EXPANSION = parse_density()  # g/m^3, 1/K
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


def arrhenius(prefactor: float, activation_j_mol: float, temperature_k: np.ndarray):
    return prefactor * np.exp(-activation_j_mol / (R * temperature_k))


def atom_density(temperature_k: np.ndarray, lithium_fraction: float):
    """Number density N(T) = rho(T) N_A / M of metal atoms (atoms/m^3), as pbliAtomDensity."""
    density = DENSITY_REFERENCE * (1.0 - DENSITY_EXPANSION * temperature_k)
    mean_mass = (
        lithium_fraction * LITHIUM_MOLAR_MASS
        + (1.0 - lithium_fraction) * LEAD_MOLAR_MASS
    )
    return density * AVOGADRO / mean_mass


def solubility_atoms_m3_pa0_5(name: str, model: dict, temperature_k: np.ndarray):
    """Sieverts solubility K_s (atoms m^-3 Pa^-1/2), as PbLiPropertyHelper::computeSolubility."""
    value = arrhenius(model["prefactor"], model["activation_j_mol"], temperature_k)
    if model["basis"] == "AtomsPerVolume":
        return value
    if model["basis"] == "MolesPerVolume":
        return value * AVOGADRO
    if model["basis"] == "AtomFraction":
        fraction = LITHIUM_FRACTION_OVERRIDE.get(name, LITHIUM_FRACTION)
        return value * atom_density(temperature_k, fraction)
    raise ValueError(f"Unsupported solubility basis {model['basis']}")


def inverse_temperature_axis(temperature_k: np.ndarray):
    return 1000.0 / temperature_k


def temperature_from_inverse_axis(inverse_temperature):
    inverse_temperature = np.asarray(inverse_temperature)
    result = np.full_like(inverse_temperature, np.nan, dtype=float)
    mask = inverse_temperature != 0.0
    result[mask] = 1000.0 / inverse_temperature[mask]
    return result


def add_temperature_top_axis(ax, temperature_ticks_k):
    secax = ax.secondary_xaxis(
        "top", functions=(temperature_from_inverse_axis, temperature_from_inverse_axis)
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
    """Order the legend by decreasing value at the reference temperature (or the nearest end)."""
    ordered = sorted(
        line_info,
        key=lambda item: np.interp(
            reference_temperature_k, item["temperature_k"], item["y_values"]
        ),
        reverse=True,
    )
    return [item["handle"] for item in ordered], [item["label"] for item in ordered]


def finish_figure(fig, ax, line_info, top_ticks, y_label, file_name):
    ax.set_yscale("log")
    apply_axes_style(ax, r"1000 / Temperature (K$^{-1}$)", y_label)
    add_temperature_top_axis(ax, top_ticks)
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
    fig.savefig(FIG_DIR / file_name, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_models(models, value_function, y_label, file_name, top_ticks, figsize):
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(gridspec.GridSpec(1, 1)[0])
    line_info = []
    for name, model in models.items():
        t_min, t_max = model["temp_range_k"]
        temperature = np.linspace(t_min, t_max, 250)
        values = value_function(name, model, temperature)
        (line,) = ax.plot(
            inverse_temperature_axis(temperature),
            values,
            linewidth=2.0,
            label=model["label"],
        )
        line_info.append(
            {
                "handle": line,
                "label": model["label"],
                "temperature_k": temperature,
                "y_values": values,
            }
        )
    finish_figure(fig, ax, line_info, top_ticks, y_label, file_name)


def plot_density():
    fig = plt.figure(figsize=[6.5, 4.5])
    ax = fig.add_subplot(gridspec.GridSpec(1, 1)[0])
    temperature = np.linspace(*DENSITY_PLOT_RANGE_K, 250)
    density = DENSITY_REFERENCE * (1.0 - DENSITY_EXPANSION * temperature)
    ax.plot(temperature, density, linewidth=2.0, label="LinearExpansion")
    apply_axes_style(ax, "Temperature (K)", r"$\rho$ (g/m$^3$)")
    ax.legend(loc="upper right")
    fig.tight_layout()
    fig.savefig(FIG_DIR / "pbli_density_models.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    apply_validation_style()
    plot_density()
    plot_models(
        DIFFUSIVITY_MODELS,
        lambda name, model, t: np.broadcast_to(
            arrhenius(model["prefactor"], model["activation_j_mol"], t), t.shape
        ),
        r"$D$ (m$^2$/s)",
        "pbli_diffusivity_models.png",
        [500.0, 600.0, 700.0, 800.0, 900.0, 1000.0],
        [6.5, 6.0],
    )
    plot_models(
        SOLUBILITY_MODELS,
        lambda name, model, t: np.broadcast_to(
            solubility_atoms_m3_pa0_5(name, model, t), t.shape
        ),
        r"$K_s$ (atoms m$^{-3}$ Pa$^{-1/2}$)",
        "pbli_solubility_models.png",
        [500.0, 600.0, 700.0, 800.0, 900.0],
        [6.5, 6.0],
    )


if __name__ == "__main__":
    main()
