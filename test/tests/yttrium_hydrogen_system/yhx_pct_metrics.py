# The python script compares the TMAP8 predictions against the
# analytical expression of the PCT curve

import os

import numpy as np
import pandas as pd

HIGH_PREDICTION_FILES = (
    "YHx_PCT_T1273_P3e3_out.csv",
    "YHx_PCT_T1173_P1e3_out.csv",
    "YHx_PCT_T1173_P1e4_out.csv",
    "YHx_PCT_T1173_P5e4_out.csv",
)

# Low-pressure steady-state prediction files.
LOW_PREDICTION_FILES = (
    "YHx_PCT_T1573_P5e3_out.csv",
    "YHx_PCT_T1473_P3e3_out.csv",
    "YHx_PCT_T1273_P3e2_out.csv",
    "YHx_PCT_T1573_P6e2_out.csv",
)

# Branch-switching tolerance: P / p0(T) threshold used to decide whether a
# point sits in the low-pressure, plateau, or high-pressure regime.
TOLERANCE = 1.148


def p0_lim_func(temperature):
    return np.exp(
        -26.1
        + 3.88 * 10 ** (-2) * np.array(temperature)
        - 9.7 * 10 ** (-6) * np.square(temperature)
    )


def ar_max_low_p(temperature):
    """
    Temperature-dependent maximum atom ratio for the low-pressure branch:
    Ar_Max_Low_P(T) = 1.01e-6 * T^2 - 2.55e-3 * T + 2.156
    """
    temperature = np.asarray(temperature, dtype=float)
    return 1.01e-6 * (temperature**2) - 2.55e-3 * temperature + 2.16


def ar_min_high_p(temperature):
    """
    Temperature-dependent minimum atom ratio for the high-pressure branch:
    Ar_Min_High_P(T) = -1.01e-6 * T^2 + 2.55e-3 * T - 0.56
    """
    temperature = np.asarray(temperature, dtype=float)
    return -1.01e-6 * (temperature**2) + 2.55e-3 * temperature - 0.56


def atom_ratio_eq_upper_func(temperature, pressure):
    """High-pressure branch fit (corrected/updated model)."""
    AR_min = ar_min_high_p(temperature)
    with np.errstate(divide="ignore", invalid="ignore"):
        return 2 - 1.0015 * (
            AR_min
            + np.exp(
                24.89
                - 2.53e-02 * temperature
                + (-3.98e-01 + 0.001 * temperature)
                * (np.log(pressure - p0_lim_func(temperature)))
            )
        ) ** (-1)


def atom_ratio_eq_lower_func(temperature, pressure):
    """Low-pressure branch fit."""
    p0 = p0_lim_func(temperature)
    arg = np.maximum(p0 - pressure, 1e-12)
    with np.errstate(divide="ignore", invalid="ignore"):
        return (
            1.01e-6 * np.square(temperature) - 2.56e-3 * temperature + 2.16
        ) - 10 * (
            0.001
            + np.exp(
                -50.0
                + 5.73e-2 * temperature
                + (0.83 - 2.69e-3 * temperature) * np.log(arg)
            )
        ) ** (
            -1
        )


def atom_ratio_plateau_region_fit(temperature, pressure, tolerance=TOLERANCE):
    """
    Plateau-region log-linear fit:
    AR(P, T) = (1.33 - 2.18e-04*T) + (3.50 - 1.44e-03*T)*ln(P / (tolerance*p0(T)))
    """
    temperature = float(temperature)
    p0 = float(p0_lim_func(temperature))
    denom = max(tolerance * p0, 1e-20)
    arg = np.maximum(np.asarray(pressure, dtype=float) / denom, 1e-12)
    return (1.33 - 2.18e-04 * temperature) + (3.50 - 1.44e-03 * temperature) * np.log(
        arg
    )


def select_branch(temperature, pressure, tolerance=TOLERANCE):
    """
    Classify a single (temperature, pressure) point into "low", "plateau",
    or "high" using the same domain- and AR-threshold rules used for fitting.
    """
    temperature = float(temperature)
    pressure = float(pressure)
    p0_T = float(p0_lim_func(temperature))

    AR_low = atom_ratio_eq_lower_func(temperature, np.array([pressure]))
    AR_high = atom_ratio_eq_upper_func(temperature, np.array([pressure]))
    AR_plateau = atom_ratio_plateau_region_fit(
        temperature, np.array([pressure]), tolerance
    )

    AR_low = AR_low[0] if np.size(AR_low) else np.nan
    AR_high = AR_high[0] if np.size(AR_high) else np.nan
    AR_plateau = AR_plateau[0] if np.size(AR_plateau) else np.nan

    AR_low_max = ar_max_low_p(temperature)
    AR_high_min = ar_min_high_p(temperature)

    is_low_dom = (pressure / p0_T) < tolerance
    is_high_dom = (pressure / p0_T) > tolerance

    use_low = np.isfinite(AR_low) and is_low_dom and (AR_low <= AR_low_max)
    use_high = np.isfinite(AR_high) and is_high_dom and (AR_high >= AR_high_min)

    if use_low:
        return "low"
    if use_high:
        return "high"
    return "plateau"


def compute_mape(ar_tmap, p_tmap, ar_exp, p_exp):
    """
    Mean absolute percentage error between a TMAP8 curve and an experimental
    curve, computed on their overlapping atom-ratio range by interpolating
    the experimental pressure onto the TMAP8 atom-ratio grid.
    """
    ar_tmap = ar_tmap[np.argsort(ar_tmap)]
    p_tmap = p_tmap[np.argsort(ar_tmap)]
    ar_exp = ar_exp[np.argsort(ar_exp)]
    p_exp = p_exp[np.argsort(p_exp)]

    lo = max(ar_exp.min(), ar_tmap.min())
    hi = min(ar_exp.max(), ar_tmap.max())

    mask = (ar_exp >= lo) & (ar_exp <= hi)
    ar_exp2 = ar_exp[mask]
    p_exp2 = p_exp[mask]

    p_interp = np.interp(ar_exp2, ar_tmap, p_tmap)
    return np.mean(np.abs((p_interp - p_exp2) / p_exp2)) * 100


def load_high_prediction_points(csv_folder):
    points = []
    for filename in HIGH_PREDICTION_FILES:
        dataframe = pd.read_csv(os.path.join(csv_folder, filename))
        temperature = dataframe["temperature"].iat[-1]
        pressure = dataframe["pressure_H2_enclosure_1_at_interface"].iat[-1]
        prediction = dataframe["atomic_fraction_H_enclosure_2_at_interface"].iat[-1]
        reference = atom_ratio_eq_upper_func(temperature, pressure)
        points.append(
            {
                "filename": filename,
                "temperature": temperature,
                "pressure": pressure,
                "prediction": prediction,
                "reference": reference,
            }
        )

    return points


"""
def load_low_prediction_points(csv_folder):
    points = []
    for filename in LOW_PREDICTION_FILES:
        dataframe = pd.read_csv(os.path.join(csv_folder, filename))
        T = dataframe["temperature"].iat[-1]
        P = dataframe["pressure_H2_enclosure_1_at_interface"].iat[-1]
        xH = dataframe["atomic_fraction_H_enclosure_2_at_interface"].iat[-1]
        prediction = dataframe["atomic_fraction_H_enclosure_2_at_interface"].iat[-1]
        reference = atom_ratio_eq_lower_func(temperature, pressure)
        xH_model_low = atom_ratio_eq_lower_func(T, P)
        points.append(
            {
                "file": filename,
                "T": T,
                "P": P,
                "xH": xH,
                "xH_model": xH_model_low,
                "error_pct": abs(xH - xH_model_low) / xH_model_low * 100,
            }
        )

    return points
"""


def load_low_prediction_points(csv_folder):
    points = []
    for filename in LOW_PREDICTION_FILES:
        dataframe = pd.read_csv(os.path.join(csv_folder, filename))
        temperature = dataframe["temperature"].iat[-1]
        pressure = dataframe["pressure_H2_enclosure_1_at_interface"].iat[-1]
        prediction = dataframe["atomic_fraction_H_enclosure_2_at_interface"].iat[-1]
        reference = atom_ratio_eq_lower_func(temperature, pressure)
        points.append(
            {
                "filename": filename,
                "temperature": temperature,
                "pressure": pressure,
                "prediction": prediction,
                "reference": reference,
            }
        )

    return points


def high_compute_prediction_rmspe(csv_folder):
    points = load_high_prediction_points(csv_folder)
    predictions = np.array([point["prediction"] for point in points])
    references = np.array([point["reference"] for point in points])
    rmse = np.sqrt(np.mean((predictions - references) ** 2))
    return rmse * 100.0 / np.mean(references)


def low_compute_prediction_rmspe(csv_folder):
    points = load_low_prediction_points(csv_folder)
    predictions = np.array([point["prediction"] for point in points])
    references = np.array([point["reference"] for point in points])
    rmse = np.sqrt(np.mean((predictions - references) ** 2))
    return rmse * 100.0 / np.mean(references)


def compute_fit_rmse(
    temperature, pressures, atom_ratios, tolerance=TOLERANCE, ar_high_min=1.0
):
    """
    RMSE between the analytical low/high branch fits and experimental data at
    a given temperature, each restricted to that branch's valid domain (same
    masks used when deciding which fit-line segments are plotted).
    Returns (rmse_low, rmse_high); either is np.nan if no points qualify.
    """
    temperature = float(temperature)
    pressures = np.asarray(pressures, dtype=float)
    atom_ratios = np.asarray(atom_ratios, dtype=float)

    p0_T = float(p0_lim_func(temperature))
    ar_low_max = ar_max_low_p(temperature)

    pred_low = atom_ratio_eq_lower_func(temperature, pressures)
    pred_high = atom_ratio_eq_upper_func(temperature, pressures)

    mask_low = (
        np.isfinite(pred_low)
        & ((pressures / p0_T) < tolerance)
        & (pred_low <= ar_low_max)
    )
    mask_high = (
        np.isfinite(pred_high)
        & ((pressures / p0_T) > tolerance)
        & (pred_high >= ar_high_min)
    )

    rmse_low = (
        float(np.sqrt(np.mean((atom_ratios[mask_low] - pred_low[mask_low]) ** 2)))
        if np.any(mask_low)
        else np.nan
    )
    rmse_high = (
        float(np.sqrt(np.mean((atom_ratios[mask_high] - pred_high[mask_high]) ** 2)))
        if np.any(mask_high)
        else np.nan
    )

    return rmse_low, rmse_high


def compute_all_fit_rmse(list_expData, temperature_list):
    """
    Compute per-temperature fit RMSE (low & high branch) across all
    experimental datasets. Returns (RMSE_values_low, RMSE_values_high) dicts
    keyed by temperature, containing only temperatures with valid points.
    """
    RMSE_values_low = {}
    RMSE_values_high = {}
    for expData, temperature in zip(list_expData, temperature_list):
        pressures = expData["Partial Pressure (Pa)"].to_numpy(dtype=float)
        atom_ratios = expData["Atom Ratio (-)"].to_numpy(dtype=float)
        rmse_low, rmse_high = compute_fit_rmse(temperature, pressures, atom_ratios)
        if np.isfinite(rmse_low):
            RMSE_values_low[temperature] = rmse_low
        if np.isfinite(rmse_high):
            RMSE_values_high[temperature] = rmse_high
    return RMSE_values_low, RMSE_values_high
