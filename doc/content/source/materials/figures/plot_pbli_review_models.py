#!/usr/bin/env python3

"""
Plot the PbLi hydrogen isotope diffusivity and solubility correlations implemented in TMAP8
(TritiumDiffusivityPbLi and TritiumSolubilityPbLi).

Intended use: regenerate the two documentation figures that are included with `!media` in
TritiumDiffusivityPbLi.md and TritiumSolubilityPbLi.md. Run it from any directory:

    python plot_pbli_review_models.py

Outputs (written next to this script):
    pbli_diffusivity_models.png  -- D (m^2/s) versus 1000/T, one curve per model, and the three
                                    published values of Shibuya1987
    pbli_solubility_models.png   -- K_s (atoms m^-3 Pa^-1/2) versus 1000/T, one curve per model

Each curve is drawn only over the documented temperature range of its model. The coefficients,
temperature ranges and solubility bases are read from include/materials/PbLiPropertyHelper.h (the
switch statements in diffusivityModelData and solubilityModelData), the molar masses from the same
header, the PbLi density from MOOSE's LeadLithiumFluidProperties, the ideal gas constant and the
Avogadro number from MOOSE's PhysicalConstants.h, so the figures cannot drift from the C++. Only
the plot labels and the functional forms are defined here; if the header's structs or switch
layout change, update parse_model_cases accordingly. Fukada2013MixingRule is not plotted because it
depends on user-provided Sieverts constants.

The diffusivity is D = D0 exp(-Ea / (R T)), with T in K, Ea in J/mol and D in m^2/s. The solubility
is K_s = K0 exp(-Ea / (R T)) B(T) in atoms m^-3 Pa^-1/2, where B = 1 for fits already in atoms,
B = N_A for fits in mol m^-3, and B = N(T) = rho(T) N_A / M for atom-fraction fits, with
rho(T) the PbLi density of LeadLithiumFluidProperties (converted from kg/m^3 to g/m^3) and M the
mean atomic mass (TritiumSolubilityPbLi and PbLiPropertyHelper::computeSolubility).
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

# Header defining PhysicalConstants::atm_to_Pa
TMAP8_CONSTANTS_HEADER = REPO_DIR / "include" / "utils" / "TMAP8PhysicalConstants.h"
# Source of the PbLi density, rho = a - b T in kg/m^3, used to convert atom-fraction solubilities
DENSITY_SOURCE = (
    REPO_DIR
    / "moose"
    / "modules"
    / "fluid_properties"
    / "src"
    / "fluidproperties"
    / "LeadLithiumFluidProperties.C"
)

# Lithium atomic fraction used for the atom-fraction conversion in the figure, unless the model is
# documented for a single composition, in which case it is plotted at that composition
LITHIUM_FRACTION = 0.17
# Models with user-provided inputs, which cannot be plotted
NOT_PLOTTED = {"Fukada2013MixingRule"}

# Published diffusivity values of Shibuya1987 (temperature in K, diffusivity in m^2/s), of which
# the Arrhenius form of the model is a least-squares fit
SHIBUYA1987_DATA = {
    "temperature_k": np.array([573.0, 673.0, 773.0]),
    "diffusivity_m2_s": np.array([6.6e-10, 7.8e-10, 9.5e-10]),
}

ISOTOPE_NAMES = {"H": "hydrogen", "D": "deuterium", "T": "tritium"}


def model_label(name: str, isotope: str) -> str:
    """
    Legend label from the model name and the isotope the model was measured for, which is only
    added if the model name does not already contain it.
    """
    isotope_name = ISOTOPE_NAMES[isotope]
    if isotope_name.capitalize() in name:
        return name
    return f"{name}, {isotope_name}"


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

    expression = expression.replace("std::", "").replace("PhysicalConstants::", "")
    return visit(ast.parse(expression.strip(), mode="eval"))


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
    Returns {model name: (min_T, max_T, [the raw fields], (min_x, max_x))}.
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
        rest_start = close_index + 1
        # Models with a documented pressure range wrap the metadata:
        # withPressureRange(pbliMetadata(...), min_pressure, max_pressure)
        wrapper = "withPressureRange("
        if chunk[:call].rstrip().endswith(wrapper):
            wrapper_open = chunk[:call].rindex(wrapper) + len(wrapper) - 1
            rest_start = match_parenthesis(chunk, wrapper_open) + 1
        rest = chunk[rest_start:]
        rest = rest[: rest.index("}")] if "}" in rest else rest
        fields = [f for f in split_top_level(rest.lstrip(" ,\n")) if f]
        if len(metadata) > 5:
            composition = (
                evaluate_number(metadata[4], names),
                evaluate_number(metadata[5], names),
            )
        else:  # default argument of pbliMetadata: the eutectic composition range
            composition = (
                parse_constant(HELPER_HEADER, "eutectic_min_lithium_fraction"),
                parse_constant(HELPER_HEADER, "eutectic_max_lithium_fraction"),
            )
        cases[name] = (min_t, max_t, fields, composition)
    return cases


def header_names() -> dict:
    """
    Named constants that appear in the model cases of the helper header. The upper bound of models
    without a documented temperature range, `std::numeric_limits<Real>::max()`, is infinity here.
    """
    return {
        "ideal_gas_constant": parse_constant(CONSTANTS_HEADER, "ideal_gas_constant"),
        "atm_to_Pa": parse_constant(TMAP8_CONSTANTS_HEADER, "atm_to_Pa"),
        "no_min_temperature": parse_constant(HELPER_HEADER, "no_min_temperature"),
        "no_max_temperature": float("inf"),
    }


def build_models():
    """Combine the numbers parsed from the C++ header with the plot labels defined here."""
    names = header_names()

    diffusivity = {}
    for name, (t_min, t_max, fields, composition) in parse_model_cases(
        HELPER_HEADER, "diffusivityModelData", names
    ).items():
        # fields: prefactor, activation energy, Isotope::X
        isotope = fields[2].split("::")[-1]
        diffusivity[name] = {
            "temp_range_k": (t_min, t_max),
            "prefactor": evaluate_number(fields[0], names),
            "activation_j_mol": evaluate_number(fields[1], names),
            "composition": composition,
            "label": model_label(name, isotope),
        }

    solubility = {}
    for name, (t_min, t_max, fields, composition) in parse_model_cases(
        HELPER_HEADER, "solubilityModelData", names
    ).items():
        if name in NOT_PLOTTED:
            continue
        # fields: SolubilityBasis::X, prefactor, activation energy, Isotope::X
        isotope = fields[3].split("::")[-1]
        solubility[name] = {
            "temp_range_k": (t_min, t_max),
            "basis": fields[0].split("::")[-1],
            "prefactor": evaluate_number(fields[1], names),
            "activation_j_mol": evaluate_number(fields[2], names),
            "composition": composition,
            "label": model_label(name, isotope),
        }
    return diffusivity, solubility


def parse_density():
    """
    Read the PbLi density correlation rho = a - b T (kg/m^3) from the rho_from_p_T function of
    MOOSE's LeadLithiumFluidProperties. Returns (a, b) in kg/m^3 and kg/m^3/K.
    """
    text = DENSITY_SOURCE.read_text()
    start = text.index(
        "LeadLithiumFluidProperties::rho_from_p_T(Real /*p*/, Real T) const"
    )
    match = re.search(r"return\s+([0-9.]+)\s*-\s*([0-9.]+)\s*\*\s*T\s*;", text[start:])
    if match is None:
        raise ValueError(f"Could not find the density correlation in {DENSITY_SOURCE}")
    return float(match.group(1)), float(match.group(2))


R = parse_constant(CONSTANTS_HEADER, "ideal_gas_constant")  # J/mol/K
AVOGADRO = parse_constant(CONSTANTS_HEADER, "avogadro_number")  # 1/mol
LITHIUM_MOLAR_MASS = parse_constant(HELPER_HEADER, "lithium_molar_mass")  # g/mol
LEAD_MOLAR_MASS = parse_constant(HELPER_HEADER, "lead_molar_mass")  # g/mol
G_PER_KG = parse_constant(HELPER_HEADER, "g_per_kg")  # g/kg
DENSITY_INTERCEPT, DENSITY_SLOPE = parse_density()  # kg/m^3, kg/m^3/K
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
    """Number density N(T) = rho(T) N_A / M of metal atoms (atoms/m^3), as atomDensity."""
    density = (DENSITY_INTERCEPT - DENSITY_SLOPE * temperature_k) * G_PER_KG  # g/m^3
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
        low, high = model["composition"]
        fraction = low if low == high else LITHIUM_FRACTION
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
        loc="upper left",
        bbox_to_anchor=(1.02, 1.0),
        borderaxespad=0.0,
        ncol=1,
        fontsize=9,
    )
    fig.tight_layout()
    fig.savefig(FIG_DIR / file_name, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_models(
    models, value_function, y_label, file_name, top_ticks, figsize, raw_data=None
):
    """
    Plot one curve per model. raw_data optionally maps a model name to a dictionary with the
    published 'temperature_k' and 'values' of that model, drawn as markers of the color of the curve.
    """
    raw_data = raw_data or {}
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(gridspec.GridSpec(1, 1)[0])
    line_info = []
    colors = plt.get_cmap("tab10").colors
    line_styles = ["-", "--", "-.", ":"]
    for index, (name, model) in enumerate(models.items()):
        t_min, t_max = model["temp_range_k"]
        temperature = np.linspace(t_min, t_max, 250)
        values = value_function(name, model, temperature)
        color = colors[index % len(colors)]
        (line,) = ax.plot(
            inverse_temperature_axis(temperature),
            values,
            linewidth=2.0,
            color=color,
            linestyle=line_styles[(index // len(colors)) % len(line_styles)],
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
        if name in raw_data:
            data = raw_data[name]
            marker = ax.scatter(
                inverse_temperature_axis(data["temperature_k"]),
                data["values"],
                s=60,
                marker="o",
                facecolors="none",
                edgecolors=color,
                linewidths=2.0,
                zorder=3,
                label=f"{model['label']}, published values",
            )
            line_info.append(
                {
                    "handle": marker,
                    "label": f"{model['label']}, published values",
                    "temperature_k": temperature,
                    "y_values": values,
                }
            )
    finish_figure(fig, ax, line_info, top_ticks, y_label, file_name)


def main():
    apply_validation_style()
    plot_models(
        DIFFUSIVITY_MODELS,
        lambda name, model, t: np.broadcast_to(
            arrhenius(model["prefactor"], model["activation_j_mol"], t), t.shape
        ),
        r"$D$ (m$^2$/s)",
        "pbli_diffusivity_models.png",
        [500.0, 600.0, 700.0, 800.0, 900.0, 1000.0],
        [10.0, 6.0],
        raw_data={
            "Shibuya1987": {
                "temperature_k": SHIBUYA1987_DATA["temperature_k"],
                "values": SHIBUYA1987_DATA["diffusivity_m2_s"],
            }
        },
    )
    plot_models(
        SOLUBILITY_MODELS,
        lambda name, model, t: np.broadcast_to(
            solubility_atoms_m3_pa0_5(name, model, t), t.shape
        ),
        r"$K_s$ (atoms m$^{-3}$ Pa$^{-1/2}$)",
        "pbli_solubility_models.png",
        [500.0, 600.0, 700.0, 800.0, 900.0, 1000.0],
        [10.0, 6.0],
    )


if __name__ == "__main__":
    main()
