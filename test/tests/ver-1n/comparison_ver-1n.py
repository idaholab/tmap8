import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
from matplotlib.ticker import ScalarFormatter
import pandas as pd
from scipy import special
import os
import re

# Define font size
plt.rcParams.update({"font.size": 15})

# Changes working directory to script directory (for consistent MooseDocs usage)
script_folder = os.path.dirname(__file__)
os.chdir(script_folder)


def get_repo_relative_path(test_path):
    if "/tmap8/doc/" in script_folder.lower():
        return os.path.join("../../../../test/tests/ver-1n", test_path)
    return os.path.join(".", test_path)


def strip_inline_comment(line):
    in_quote = None
    for index, character in enumerate(line):
        if character in ("'", '"'):
            if in_quote == character:
                in_quote = None
            elif in_quote is None:
                in_quote = character
        elif character == "#" and in_quote is None:
            return line[:index]
    return line


def search_parameter(path, visited, parameter_name):
    if path in visited:
        return None
    visited.add(path)
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            stripped = strip_inline_comment(line).strip()
            if stripped.startswith("!include "):
                include_name = stripped.split(maxsplit=1)[1]
                include_path = os.path.join(os.path.dirname(path), include_name)
                result = search_parameter(include_path, visited, parameter_name)
                if result is not None:
                    return result
            if stripped.startswith(f"{parameter_name} ="):
                return stripped.split("=", maxsplit=1)[1].strip().strip("'")
    return None


def get_raw_parameter_value(parameter_name, source_file="ver-1n.i"):
    parameters_file = get_repo_relative_path(source_file)
    result = search_parameter(parameters_file, set(), parameter_name)
    if result is None:
        raise KeyError(
            f"Could not find parameter {parameter_name} in {parameters_file}"
        )
    return result


def get_raw_block_parameter(block_name, parameter_name, source_file="ver-1n.i"):
    parameters_file = get_repo_relative_path(source_file)
    active = False
    depth = 0
    with open(parameters_file, encoding="utf-8") as handle:
        for line in handle:
            stripped = strip_inline_comment(line).strip()
            if not active and stripped == f"[{block_name}]":
                active = True
                depth = 1
                continue
            if not active:
                continue
            if stripped == "[]":
                depth -= 1
                if depth == 0:
                    break
                continue
            if stripped.startswith("[") and stripped.endswith("]"):
                depth += 1
                continue
            if stripped.startswith(f"{parameter_name} ="):
                return stripped.split("=", maxsplit=1)[1].strip().strip("'")
    raise KeyError(f"Could not find parameter {parameter_name} in block {block_name}")


def evaluate_fparse_expression(expression, source_file):
    safe_namespace = {
        "exp": np.exp,
        "sqrt": np.sqrt,
        "pi": np.pi,
    }
    names = set(re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", expression))
    for name in names:
        if name not in safe_namespace:
            safe_namespace[name] = get_numeric_parameter(name, source_file)
    return eval(expression, {"__builtins__": {}}, safe_namespace)


def resolve_fparse(value, source_file):
    pattern = re.compile(r"\$\{fparse ([^{}]+)\}")
    while True:
        match = pattern.search(value)
        if match is None:
            return value
        parsed_value = evaluate_fparse_expression(match.group(1), source_file)
        value = value[: match.start()] + str(parsed_value) + value[match.end() :]


def parse_numeric_value(value, source_file="ver-1n.i", output_unit=None):
    value = value.strip().strip("'")
    if value.startswith("${") and value.endswith("}"):
        inner_value = value[2:-1].strip()
        if inner_value.startswith("units "):
            units_expr = resolve_fparse(
                inner_value[len("units ") :].strip(), source_file
            )
            match = re.fullmatch(r"(.+?)\s+(\S+)(?:\s*->\s*(\S+))?", units_expr)
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
                ("mum", "m"): 1e-6,
                ("mm", "m"): 1e-3,
                ("m", "mum"): 1e6,
                ("mum^2/s", "m^2/s"): 1e-12,
                ("m^2/s", "mum^2/s"): 1e12,
                ("at/mum^3/Pa^0.5", "atom/m^3/Pa^0.5"): 1e18,
            }
            factor = supported_conversions.get((from_unit, target_unit))
            if factor is None:
                raise ValueError(f"Unsupported conversion in units expression: {value}")
            return numeric_value * factor
        if inner_value.startswith("fparse "):
            return evaluate_fparse_expression(
                inner_value[len("fparse ") :], source_file
            )
        return get_numeric_parameter(inner_value, source_file, output_unit)
    return float(value)


def get_numeric_parameter(parameter_name, source_file="ver-1n.i", output_unit=None):
    raw_value = get_raw_parameter_value(parameter_name, source_file)
    return parse_numeric_value(raw_value, source_file, output_unit)


def get_point_x_m(block_name, source_file="ver-1n.i"):
    raw_point = get_raw_block_parameter(block_name, "point", source_file).strip("'")
    return float(raw_point.split()[0]) * 1e-6


# ========================== TMAP8 result - location ========================= #

csv_folder = get_repo_relative_path("gold/ver-1n_vector_postproc_30s_line_0015.csv")
tmap_sol = pd.read_csv(csv_folder)
tmap_distance = tmap_sol["x"] / 1e6  # m
tmap_concentration_on_distance_case1 = (
    tmap_sol["deuterium_concentration_PCC"] * 1e18
)  # atom/m^3

csv_folder = get_repo_relative_path("gold/ver-1n_vector_postproc_500s_line_0066.csv")
tmap_sol = pd.read_csv(csv_folder)
tmap_concentration_on_distance_case2 = (
    tmap_sol["deuterium_concentration_PCC"] * 1e18
)  # atom/m^3

# ============================ TMAP8 result - time =========================== #

csv_folder = get_repo_relative_path("gold/ver-1n_out.csv")
tmap_sol = pd.read_csv(csv_folder)
tmap_time = tmap_sol["time"]
tmap_concentration_on_time_case3 = tmap_sol["concentration_point1"] * 1e18  # atom/m^3
tmap_concentration_on_time_case4 = tmap_sol["concentration_point2"] * 1e18  # atom/m^3


# ============================ Analytical solution =========================== #
# reference from:
# Luping, Tang, and Lars-Olof Nilsson.
# "Rapid determination of the chloride diffusivity in concrete by applying an electric field."
# Materials Journal 89.1 (1993): 49-53.
def concentration_analytical_solution_semi_infinity(
    x, t, concentration_high, constant_a, diffusivity
):
    return (
        concentration_high
        / 2
        * (
            np.exp(constant_a * x)
            * special.erfc(
                (x + constant_a * diffusivity * t) / 2 / np.sqrt(diffusivity * t)
            )
            + special.erfc(
                (x - constant_a * diffusivity * t) / 2 / np.sqrt(diffusivity * t)
            )
        )
    )


R = get_numeric_parameter("R")
Temperature = get_numeric_parameter("temperature")
Pressure_high = get_numeric_parameter("pressure_high")
V = get_numeric_parameter("V_current")
L = get_numeric_parameter("length", output_unit="m")
F = get_numeric_parameter("F")
diffusivity = get_numeric_parameter("diffusion_pre_PCC", output_unit="m^2/s") * np.exp(
    -get_numeric_parameter("diffusion_energy_PCC") / R / Temperature
)  # m^2/s
solubility = get_numeric_parameter(
    "solubility_pre_PCC", output_unit="atom/m^3/Pa^0.5"
) * np.exp(
    -get_numeric_parameter("solubility_energy_PCC") / R / Temperature
)  # atom/m^3/Pa^0.5
z = get_numeric_parameter("charge_number")
# derivative parameters
E = V / L
constant_a = z * F / R / Temperature * E
concentration_high = solubility * np.sqrt(Pressure_high)

t_case1 = float(get_raw_block_parameter("vector_postproc_30s", "sync_times"))
t_case2 = float(get_raw_block_parameter("vector_postproc_500s", "sync_times"))
x_case3 = get_point_x_m("concentration_point1")
x_case4 = get_point_x_m("concentration_point2")
concentration_case1 = concentration_analytical_solution_semi_infinity(
    tmap_distance, t_case1, concentration_high, constant_a, diffusivity
)
concentration_case2 = concentration_analytical_solution_semi_infinity(
    tmap_distance, t_case2, concentration_high, constant_a, diffusivity
)
concentration_case3 = concentration_analytical_solution_semi_infinity(
    x_case3, tmap_time, concentration_high, constant_a, diffusivity
)
concentration_case4 = concentration_analytical_solution_semi_infinity(
    x_case4, tmap_time, concentration_high, constant_a, diffusivity
)


# ============================================================================ #
# Plot figure for verification on location
fig = plt.figure(figsize=[6.5, 5.5])
gs = gridspec.GridSpec(1, 1)
ax = fig.add_subplot(gs[0])

ax.plot(
    tmap_distance,
    tmap_concentration_on_distance_case1,
    label=f"TMAP8 - {t_case1:.0f}s",
    c="C0",
    alpha=0.3,
)  # numerical solution
ax.plot(
    tmap_distance,
    concentration_case1,
    c=f"C0",
    linestyle="--",
    label=f"Analytical results - {t_case1:.0f}s",
)
ax.plot(
    tmap_distance,
    tmap_concentration_on_distance_case2,
    label=f"TMAP8 - {t_case2:.0f}s",
    c="C1",
    alpha=0.3,
)  # numerical solution
ax.plot(
    tmap_distance,
    concentration_case2,
    c=f"C1",
    linestyle="--",
    label=f"Analytical results - {t_case2:.0f}s",
)

ax.set_xlabel("Location (m)")
ax.set_ylabel("Concentration (atom/m$^3$)")
ax.legend(loc=[0.35, 0.68])
ax.set_xlim(left=0, right=0.00126)
ax.set_ylim(bottom=0, top=2.2e24)
x_formatter = ScalarFormatter(useMathText=True)
x_formatter.set_powerlimits((0, 0))
ax.xaxis.set_major_formatter(x_formatter)
plt.grid(visible=True, which="major", color="0.65", linestyle="--", alpha=0.3)
RMSPE_case1 = (
    np.sqrt(np.mean((tmap_concentration_on_distance_case1 - concentration_case1) ** 2))
    / np.mean(concentration_case1)
    * 100
)
ax.text(1.5e-4, 0.5e24, "RMSPE = %.2f " % RMSPE_case1 + "%", fontweight="bold", c="C0")
RMSPE_case2 = (
    np.sqrt(np.mean((tmap_concentration_on_distance_case2 - concentration_case2) ** 2))
    / np.mean(concentration_case2)
    * 100
)
ax.text(7.0e-4, 0.75e24, "RMSPE = %.2f " % RMSPE_case2 + "%", fontweight="bold", c="C1")
ax.minorticks_on()
plt.savefig("ver-1n_comparison_location.png", bbox_inches="tight", dpi=300)
plt.close(fig)

# ============================================================================ #
# Plot figure for verification on time
fig = plt.figure(figsize=[6.5, 5.5])
gs = gridspec.GridSpec(1, 1)
ax = fig.add_subplot(gs[0])

ax.plot(
    tmap_time,
    tmap_concentration_on_time_case3,
    label=r"TMAP8 - point1",
    c="C0",
    alpha=0.3,
)  # numerical solution
ax.plot(
    tmap_time,
    concentration_case3,
    c=f"C0",
    linestyle="--",
    label=f"Analytical results - point1",
)
ax.plot(
    tmap_time,
    tmap_concentration_on_time_case4,
    label=r"TMAP8 - point2",
    c="C1",
    alpha=0.3,
)  # numerical solution
ax.plot(
    tmap_time,
    concentration_case4,
    c=f"C1",
    linestyle="--",
    label=f"Analytical results - point2",
)

ax.set_xlabel("Time (s)")
ax.set_ylabel("Concentration (atom/m$^3$)")
ax.legend(loc=[0.05, 0.68])
ax.set_xlim(left=0, right=1.02 * get_numeric_parameter("end_time"))
ax.set_ylim(bottom=0, top=2.8e24)
plt.grid(visible=True, which="major", color="0.65", linestyle="--", alpha=0.3)
RMSPE_case3 = (
    np.sqrt(np.mean((tmap_concentration_on_time_case3 - concentration_case3) ** 2))
    / np.mean(concentration_case3)
    * 100
)
ax.text(60, 0.5e24, "RMSPE = %.2f " % RMSPE_case3 + "%", fontweight="bold", c="C0")
RMSPE_case4 = (
    np.sqrt(np.mean((tmap_concentration_on_time_case4 - concentration_case4) ** 2))
    / np.mean(concentration_case4)
    * 100
)
ax.text(300, 0.1e24, "RMSPE = %.2f " % RMSPE_case4 + "%", fontweight="bold", c="C1")
ax.minorticks_on()
plt.savefig("ver-1n_comparison_time.png", bbox_inches="tight", dpi=300)
plt.close(fig)
