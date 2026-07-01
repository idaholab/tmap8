import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import os
import glob
import re

# Define font size
plt.rcParams.update({"font.size": 15})

# Changes working directory to script directory (for consistent MooseDocs usage)
script_folder = os.path.dirname(__file__)
os.chdir(script_folder)


def get_repo_relative_path(test_path):
    if "/tmap8/doc/" in script_folder.lower():
        return os.path.join("../../../../test/tests/ver-1o", test_path)
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


def get_raw_parameter_value(parameter_name, source_file="ver-1o.i"):
    parameters_file = get_repo_relative_path(source_file)
    result = search_parameter(parameters_file, set(), parameter_name)
    if result is None:
        raise KeyError(
            f"Could not find parameter {parameter_name} in {parameters_file}"
        )
    return result


def get_raw_block_parameter(block_name, parameter_name, source_file="ver-1o.i"):
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


def parse_numeric_value(value, source_file="ver-1o.i", output_unit=None):
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
                ("mm", "m"): 1e-3,
                ("m", "mum"): 1e6,
                ("mum", "m"): 1e-6,
                ("g/mol", "kg/mol"): 1e-3,
                ("g/cm^3", "kg/m^3"): 1e3,
                ("g/m^3", "kg/m^3"): 1e-3,
                ("A/V/m", "S/m"): 1.0,
                ("A/V/m", "A/V/mum"): 1e-6,
                ("A/V/mum", "S/m"): 1e6,
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


def get_numeric_parameter(parameter_name, source_file="ver-1o.i", output_unit=None):
    raw_value = get_raw_parameter_value(parameter_name, source_file)
    return parse_numeric_value(raw_value, source_file, output_unit)


# ===============================================================================
# Physical constants and material properties

FULL_LENGTH = get_numeric_parameter("full_length", output_unit="m")
HALF_LENGTH = FULL_LENGTH / 2.0
SURFACE_TEMPERATURE = get_numeric_parameter("temperature_surface")
THERMAL_CONDUCTIVITY = get_numeric_parameter("thermal_conductivity_SI")
SIGMA_REF = get_numeric_parameter("sigma_ref", output_unit="S/m")
VOLTAGE_TOTAL = get_numeric_parameter("V_full")
DENSITY = get_numeric_parameter("density_BCY20", output_unit="kg/m^3")
SPECIFIC_HEAT_MOLAR = get_numeric_parameter("specific_heat_molar")
MOLAR_MASS_BCY20 = get_numeric_parameter("molar_mass_BCY20", output_unit="kg/mol")
NUM_SERIES_TERMS = 2000  # number of Fourier series terms for convergence
PROFILE_TIMES = (
    float(get_raw_block_parameter("vector_postproc_1000s", "sync_times")),
    float(get_raw_block_parameter("vector_postproc_20000s", "sync_times")),
)

SPECIFIC_HEAT = SPECIFIC_HEAT_MOLAR / MOLAR_MASS_BCY20  # J/kg/K
THERMAL_DIFFUSIVITY = THERMAL_CONDUCTIVITY / (DENSITY * SPECIFIC_HEAT)  # m^2/s
HEAT_SOURCE = (
    SIGMA_REF * (VOLTAGE_TOTAL / FULL_LENGTH) ** 2
)  # W/m^3, uniform Joule source
LAMBDA_N = (
    np.arange(NUM_SERIES_TERMS, dtype=float) + 0.5
) * np.pi  # eigenvalues: (n+1/2)*pi

# ===============================================================================
# Analytical solution functions


def get_analytical_solution(x_m, time_s):
    """Return the transient half-slab temperature profile in kelvin.

    x_m is measured from the prescribed-temperature surface at x = 0.
    """
    x_array = np.atleast_1d(np.asarray(x_m, dtype=float))
    if np.isscalar(time_s) and time_s <= 0.0:
        return np.full_like(x_array, SURFACE_TEMPERATURE)

    y = x_array / HALF_LENGTH
    fourier_number = THERMAL_DIFFUSIVITY * float(time_s) / HALF_LENGTH**2
    sine_term = np.sin(np.outer(LAMBDA_N, y))
    decay_term = np.exp(-(LAMBDA_N**2) * fourier_number)
    transient_sum = np.sum(
        sine_term * decay_term[:, np.newaxis] / (LAMBDA_N[:, np.newaxis] ** 3),
        axis=0,
    )
    temperature_rise = (
        HEAT_SOURCE
        * HALF_LENGTH**2
        / THERMAL_CONDUCTIVITY
        * (y - 0.5 * y**2 - 2.0 * transient_sum)
    )
    return SURFACE_TEMPERATURE + temperature_rise


def get_analytical_delta_t_history(time_s):
    """Return the maximum temperature rise history at the insulated face x = L."""
    times = np.asarray(time_s, dtype=float)
    delta_t = np.zeros_like(times)
    positive_mask = times > 0.0
    if not np.any(positive_mask):
        return delta_t

    fourier_numbers = THERMAL_DIFFUSIVITY * times[positive_mask] / HALF_LENGTH**2
    sine_at_right = np.sin(LAMBDA_N)
    decay_term = np.exp(-np.outer(LAMBDA_N**2, fourier_numbers))
    transient_sum = np.sum(
        sine_at_right[:, np.newaxis] * decay_term / (LAMBDA_N[:, np.newaxis] ** 3),
        axis=0,
    )
    delta_t[positive_mask] = (
        HEAT_SOURCE
        * HALF_LENGTH**2
        / THERMAL_CONDUCTIVITY
        * (0.5 - 2.0 * transient_sum)
    )
    return delta_t


# ===============================================================================
# Extract TMAP8 results

results_folder = get_repo_relative_path("gold")

# one CSV per profile time, named by sync time and timestep index
profile_csvs = {
    t: glob.glob(
        os.path.join(results_folder, f"ver-1o_vector_postproc_{int(t)}s_line_*.csv")
    )[0]
    for t in PROFILE_TIMES
}

# time-history postprocessor output
time_data = pd.read_csv(os.path.join(results_folder, "ver-1o_out.csv"))
time_history = time_data["time"].to_numpy(dtype=float)
tmap_delta_t_history = (
    time_data["delta_T"].to_numpy(dtype=float)
    if "delta_T" in time_data
    else time_data["temperature_max"].to_numpy(dtype=float) - SURFACE_TEMPERATURE
)

# ===============================================================================
# Compute RMSPE for temperature-rise history

analytical_delta_t_history = get_analytical_delta_t_history(time_history)
history_mask = time_history > 0.0
history_rmse = np.sqrt(
    np.mean(
        (tmap_delta_t_history[history_mask] - analytical_delta_t_history[history_mask])
        ** 2
    )
)
history_rmspe = history_rmse * 100.0 / np.mean(analytical_delta_t_history[history_mask])

# ===============================================================================
# Plot temperature-rise history

fig, ax_history = plt.subplots(figsize=(6.5, 5.5))
ax_history.plot(
    time_history[history_mask],
    tmap_delta_t_history[history_mask],
    label="TMAP8",
    c="tab:gray",
    linewidth=2,
)
ax_history.plot(
    time_history[history_mask],
    analytical_delta_t_history[history_mask],
    linestyle="--",
    label="Analytical",
    c="k",
    linewidth=2,
)
ax_history.set_xscale("log")
ax_history.set_xlabel("Time (s)", fontsize=15)
ax_history.set_ylabel(r"$\Delta T_{\max}$ (K)", fontsize=15)
ax_history.set_ylim(bottom=0)
ax_history.set_xlim(left=1)
ax_history.legend(loc="lower right", fontsize=15)
ax_history.grid(visible=True, which="major", color="0.65", linestyle="--", alpha=0.3)
ax_history.text(
    0.03,
    0.93,
    f"RMSPE = {history_rmspe:.2f} %",
    transform=ax_history.transAxes,
    fontweight="bold",
    fontsize=15,
    va="top",
)
ax_history.minorticks_on()
plt.tight_layout()
plt.savefig("ver-1o_comparison_temperature_history.png", bbox_inches="tight", dpi=300)
plt.close(fig)

# ===============================================================================
# Plot spatial temperature profiles at selected times

fig, ax_profiles = plt.subplots(figsize=(6.5, 5.5))
profile_colors = {PROFILE_TIMES[0]: "C0", PROFILE_TIMES[1]: "C1"}
for time_s in PROFILE_TIMES:
    line_csv = profile_csvs[time_s]
    line_data = pd.read_csv(line_csv)
    x_m = line_data["x"].to_numpy(dtype=float) * 1e-6
    tmap_temperature = line_data["temperature"].to_numpy(dtype=float)
    analytical_temperature = get_analytical_solution(x_m, time_s)
    rmse = np.sqrt(np.mean((tmap_temperature - analytical_temperature) ** 2))
    rmspe = rmse * 100.0 / np.mean(analytical_temperature)
    x_mm = x_m * 1e3
    color = profile_colors[time_s]
    ax_profiles.plot(
        x_mm,
        tmap_temperature,
        label=f"TMAP8 {time_s:.0f} s",
        c=color,
        linewidth=2,
        alpha=0.5,
    )
    ax_profiles.plot(
        x_mm,
        analytical_temperature,
        label=f"Analytical {time_s:.0f} s",
        c=color,
        linestyle="--",
        linewidth=2,
    )
    # place RMSPE label near the right end of the curve, colored to match
    ax_profiles.text(
        x_mm[-1] * 0.85,
        (tmap_temperature[-1] + analytical_temperature[-1]) / 2 + 0.1,
        f"RMSPE = {rmspe:.2f} %",
        color=color,
        fontsize=15,
        fontweight="bold",
        ha="right",
        va="center",
    )

ax_profiles.set_xlabel("Location (mm)", fontsize=15)
ax_profiles.set_ylabel("Temperature (K)", fontsize=15)
ax_profiles.set_xlim(left=0.0, right=HALF_LENGTH * 1e3)
ax_profiles.set_ylim(bottom=771.7, top=777)
ax_profiles.grid(visible=True, which="major", color="0.65", linestyle="--", alpha=0.3)
ax_profiles.legend(loc=[0.3, 0.01], fontsize=15, ncol=1)
ax_profiles.minorticks_on()
plt.tight_layout()
plt.savefig("ver-1o_comparison_temperature_profiles.png", bbox_inches="tight", dpi=300)
plt.close(fig)
