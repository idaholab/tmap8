import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

from yhx_pct_metrics import (
    atom_ratio_eq_upper_func,
    compute_prediction_rmspe,
    load_prediction_points,
    p0_lim_func,
)

# Changes working directory to script directory (for consistent MooseDocs usage)
script_folder = os.path.dirname(__file__)
os.chdir(script_folder)

TEMPERATURES_C = [900, 950, 1000, 1050, 1100, 1150, 1200, 1250, 1300]
TEMPERATURES_K = [int(t + 273.15) for t in TEMPERATURES_C]

ATOM_RATIO_LOW = 0.65
ATOM_RATIO_HIGH = 1.0
FIG_DPI = 300
N_SMOOTH = 400

MMHG_TO_PA = 133.322

COL_PRESSURE_EXP_LOG = "Partial Pressure"
COL_PRESSURE_PA = "Partial Pressure (Pa)"
COL_PRESSURE_MMHG = "Partial Pressure (mm Hg)"
COL_ATOM_RATIO = "Atom Ratio"
COL_TMAP_T = "temperature"
COL_TMAP_P = "pressure_H2_enclosure_1_at_interface"
COL_TMAP_AF = "atomic_fraction_H_enclosure_2_at_interface"

if "/tmap8/doc/" in script_folder.lower():
    root = "../../../../../test/tests/yttrium_hydrogen_system/"
else:
    root = ""

exp_data_dir = os.path.join(root, "PCT_data")
gold_dir = os.path.join(root, "gold")

# ------------------------------------------------------------------------------
# Models
# ------------------------------------------------------------------------------


def p0_lim_func(T):
    return np.exp(-26.1 + 3.88e-2 * T - 9.7e-6 * T**2)


def atom_ratio_eq_lower_func(T, P):
    p0 = p0_lim_func(T)
    arg = np.maximum(p0 - P, 1e-12)
    with np.errstate(divide="ignore", invalid="ignore"):
        return 0.5 - (
            0.001 + np.exp(-8.97e01 + 9.75e-2 * T + (1.20 - 4.41e-3 * T) * np.log(arg))
        ) ** (-1)


def atom_ratio_eq_upper_func(T, P):
    p0 = p0_lim_func(T)
    arg = np.maximum(P - p0, 1e-12)
    with np.errstate(divide="ignore", invalid="ignore"):
        return 2.0 - (
            1.0 + np.exp(21.6 - 0.0225 * T + (-0.0445 + 7.18e-4 * T) * np.log(arg))
        ) ** (-1)


def rmse(y_true, y_pred):
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


# ------------------------------------------------------------------------------
# Load experimental data
# ------------------------------------------------------------------------------

data_by_temp = {}

for T in TEMPERATURES_K:
    path_k = os.path.join(exp_data_dir, f"{int(T)}.csv")
    path_c = os.path.join(exp_data_dir, f"{int(round(T - 273.15))}.csv")
    f = path_k if os.path.exists(path_k) else path_c

    if not os.path.exists(f):
        print(
            f"WARNING: missing experimental CSV for {T} K -> tried {path_k} and {path_c}"
        )
        continue

    df = pd.read_csv(f)

    # Pressure columns accepted: log10(Pa), Pa, or mmHg
    if COL_PRESSURE_EXP_LOG in df.columns:
        df[COL_PRESSURE_PA] = 10 ** df[COL_PRESSURE_EXP_LOG]
    elif COL_PRESSURE_PA in df.columns:
        df[COL_PRESSURE_PA] = df[COL_PRESSURE_PA].astype(float)
    elif COL_PRESSURE_MMHG in df.columns:
        df[COL_PRESSURE_PA] = df[COL_PRESSURE_MMHG].astype(float) * MMHG_TO_PA
    else:
        raise ValueError(f"CSV {f} missing pressure columns")

    # Atom ratio harmonization
    if COL_ATOM_RATIO not in df.columns:
        if "Atom Ratio (-)" in df.columns:
            df[COL_ATOM_RATIO] = df["Atom Ratio (-)"]
        else:
            raise ValueError(f"CSV {f} missing atom ratio column")

    df = df[[COL_PRESSURE_PA, COL_ATOM_RATIO]].dropna().sort_values(COL_PRESSURE_PA)
    data_by_temp[T] = df.reset_index(drop=True)

# ------------------------------------------------------------------------------
# Raw plot
# ------------------------------------------------------------------------------

fig = plt.figure(figsize=(10, 6))
for T in TEMPERATURES_K:
    df = data_by_temp.get(T)
    if df is None:
        continue
    plt.scatter(df[COL_ATOM_RATIO], df[COL_PRESSURE_PA], s=16, label=f"{T}.15 K")
    plt.plot(df[COL_ATOM_RATIO], df[COL_PRESSURE_PA])

p0_lim = p0_lim_func(temperature_list)

for T in TEMPERATURES_K:
    df = data_by_temp.get(T)
    if df is None:
        continue
    AR = df[COL_ATOM_RATIO].values
    P = df[COL_PRESSURE_PA].values
    idx = np.where(AR > ATOM_RATIO_LOW)[0]
    if idx.size:
        sel_T.append(T)
        sel_P.append(P[idx[0]])

fig = plt.figure(figsize=(5, 5))
plt.plot(TEMPERATURES_K, p0_vals, "--", label="Fit")
if sel_T:
    plt.scatter(sel_T, sel_P, color="red", s=24, label="Plateau Pressures")
plt.yscale("log")
plt.xlabel("Temperature (K)")
plt.ylabel("Pressure (Pa)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("YHx_PCT_plateau_pressure_fit.png", dpi=FIG_DPI)
plt.close(fig)

# ------------------------------------------------------------------------------
# TMAP8 Data
# ------------------------------------------------------------------------------

# ============================================================================ #
# Create a meshgrid for the fit surface
pressure_range = np.linspace(
    (min(list_expData[0].iloc[:, 1])), (max(list_expData[0].iloc[:, 1])), 100
)
temperature_range = np.linspace(min(temperature_list), max(temperature_list), 100)
pressure_mesh, temperature_mesh = np.meshgrid(pressure_range, temperature_range)

for f in low_files:
    path = os.path.join(gold_dir, f)
    if os.path.exists(path):
        try:
            tmap_low[f] = pd.read_csv(path)
        except Exception as e:
            print(f"WARNING: could not read {path}: {e}")

for f in high_files:
    path = os.path.join(gold_dir, f)
    if os.path.exists(path):
        try:
            tmap_high[f] = pd.read_csv(path)
        except Exception as e:
            print(f"WARNING: could not read {path}: {e}")

<<<<<<< HEAD
prediction_points = load_prediction_points(csv_folder)
prediction_rmspe = compute_prediction_rmspe(csv_folder)

=======
# ------------------------------------------------------------------------------
# Colors (consistent palette by temperature)
# ------------------------------------------------------------------------------
TEMP_COLOR_MAP = {
    1173: "#1f77b4",
    1273: "#ff7f0e",
    1373: "#2ca02c",
    1473: "#d62728",
    1573: "#9467bd",
}


def color_for_T(T, idx):
    if int(T) in TEMP_COLOR_MAP:
        return TEMP_COLOR_MAP[int(T)]
    palette = plt.cm.tab20
    return palette(idx % 20)


# ------------------------------------------------------------------------------
# Combined 2D Fit Figure
# ------------------------------------------------------------------------------
>>>>>>> 6de057a7 (Appling patches to python and C files)

# ============================================================================ #
# Plot the experimental data, the fit, and the TMAP8 results
fig = plt.figure(figsize=(12, 8))
ax = plt.gca()

# Collect handles/labels
high_data_handles, high_data_labels = [], []
high_fit_handles, high_fit_labels = [], []

low_fit_handles, low_fit_labels = [], []  # no low_data collected for legend

tmap_high_handles, tmap_high_labels = [], []
tmap_low_handles, tmap_low_labels = [], []

for i, T in enumerate(TEMPERATURES_K):
    df = data_by_temp.get(T)
    if df is None:
        continue

    P = df[COL_PRESSURE_PA].values.astype(float)
    AR = df[COL_ATOM_RATIO].values.astype(float)
    color_T = color_for_T(T, i)

    # ---- Low branch ----
    idx_low = AR < 0.5
    if np.any(idx_low):
        P_lo, AR_lo = P[idx_low], AR[idx_low]
        fit_lo = atom_ratio_eq_lower_func(T, P_lo)

        # Plot low data (unlabeled to avoid legend duplication)
        plt.scatter(P_lo, AR_lo, color=color_T, s=16)

        # Fit line with RMSE label
        Pmin = max(np.min(P_lo), 1e-12)
        Pmax = np.max(P_lo)
        if Pmax > Pmin:
            Ps = np.geomspace(Pmin, Pmax, N_SMOOTH)
            (ln_lo,) = plt.plot(
                Ps, atom_ratio_eq_lower_func(T, Ps), "--", color=color_T
            )
        else:
            (ln_lo,) = plt.plot(P_lo, fit_lo, "--", color=color_T)
        low_fit_handles.append(ln_lo)
        low_fit_labels.append(f"{T} K Low P Fit RMSE {rmse(AR_lo, fit_lo):.3f}")

    # ---- High branch ----
    idx_hi = AR > ATOM_RATIO_HIGH
    if np.any(idx_hi):
        P_hi, AR_hi = P[idx_hi], AR[idx_hi]
        fit_hi = atom_ratio_eq_upper_func(T, P_hi)
        valid = np.isfinite(fit_hi)
        P_hi, AR_hi, fit_hi = P_hi[valid], AR_hi[valid], fit_hi[valid]

        if len(fit_hi):
            # High data (collect for legend)
            sc_hi = plt.scatter(P_hi, AR_hi, color=color_T, s=16)
            high_data_handles.append(sc_hi)
            high_data_labels.append(f"{T} K Data")

            # High fit with RMSE
            Pmin = max(np.min(P_hi), 1e-12)
            Pmax = np.max(P_hi)
            if Pmax > Pmin:
                Ps = np.geomspace(Pmin, Pmax, N_SMOOTH)
                (ln_hi,) = plt.plot(
                    Ps, atom_ratio_eq_upper_func(T, Ps), "-", color=color_T
                )
            else:
                (ln_hi,) = plt.plot(P_hi, fit_hi, "-", color=color_T)
            high_fit_handles.append(ln_hi)
            high_fit_labels.append(f"{T} K High P Fit RMSE {rmse(AR_hi, fit_hi):.3f}")


# ---- TMAP8 overlays: split into High vs Low ----
def overlay_tmap_split(df):
    T_pred = float(df[COL_TMAP_T].iat[-1])
    P_pred = float(df[COL_TMAP_P].iat[-1])
    AF_pred = float(df[COL_TMAP_AF].iat[-1])
    p0 = float(p0_lim_func(T_pred))

    if P_pred < p0:
        AF_model = float(atom_ratio_eq_lower_func(T_pred, np.array([P_pred]))[0])
        marker = "*"
        err_pct = abs(AF_pred - AF_model) / AF_model * 100 if AF_model != 0 else np.nan
        h = plt.scatter(P_pred, AF_pred, s=70, marker=marker, color="k")
        tmap_low_handles.append(h)
        tmap_low_labels.append(f"{int(T_pred)} K, {P_pred:.2e} Pa (err {err_pct:.2f}%)")
    else:
        AF_model = float(atom_ratio_eq_upper_func(T_pred, np.array([P_pred]))[0])
        marker = "x"
        err_pct = abs(AF_pred - AF_model) / AF_model * 100 if AF_model != 0 else np.nan
        h = plt.scatter(P_pred, AF_pred, s=70, marker=marker, color="k")
        tmap_high_handles.append(h)
        tmap_high_labels.append(
            f"{int(T_pred)} K, {P_pred:.2e} Pa (err {err_pct:.2f}%)"
        )


        # Plot the data points
        plt.scatter(pressures_upper, atom_ratios_upper, label=f"{temperature} K Data")

        # Plot the fit function
        plt.plot(
            pressures_upper,
            fit_values_upper,
            label=f"{temperature} K Fit (RMSE: {RMSE:.2f})",
        )

# plot the TMAP8 predictions
for point in prediction_points:
    error = abs(point["prediction"] - point["reference"]) / point["reference"] * 100
    plt.scatter(
        point["pressure"],
        point["prediction"],
        label=(
            f'{point["temperature"]} K and {point["pressure"]:.2f} Pa prediction '
            f"(error: {error:.2f} %)"
        ),
        marker="x",
        color="k",
        s=90,
    )

plt.xscale("log")
plt.xlabel("Partial Pressure (Pa)")
plt.ylabel("Atom Ratio (-)")
plt.xscale("log")
plt.text(
    0.02,
    0.98,
    f"TMAP8 prediction RMSPE = {prediction_rmspe:.3f} %",
    transform=plt.gca().transAxes,
    va="top",
    bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "none"},
)
plt.legend(bbox_to_anchor=(1.1, 1.05))
plt.grid(True)

# -------------------- Legend assembly (single column, ordered groups) --------------------
combined_handles = []
combined_labels = []

# 1) High Pressure: Data, then Fit
for h, l in zip(high_data_handles, high_data_labels):
    combined_handles.append(h)
    combined_labels.append(l)
for h, l in zip(high_fit_handles, high_fit_labels):
    combined_handles.append(h)
    combined_labels.append(l)

# 2) TMAP8 High
for h, l in zip(tmap_high_handles, tmap_high_labels):
    combined_handles.append(h)
    combined_labels.append(l)

# 3) Low Pressure: Fit only (no Low Data legend)
for h, l in zip(low_fit_handles, low_fit_labels):
    combined_handles.append(h)
    combined_labels.append(l)

# 4) TMAP8 Low
for h, l in zip(tmap_low_handles, tmap_low_labels):
    combined_handles.append(h)
    combined_labels.append(l)

# Reserve a bit of margin on the right side for the outside legend
plt.subplots_adjust(right=0.78)

legend = plt.legend(
    combined_handles,
    combined_labels,
    ncols=1,
    loc="center left",  # anchor the center-left of the legend...
    bbox_to_anchor=(1.02, 0.5),  # ...just outside the axes at 102% x, 50% y
    fontsize=8,
    frameon=True,
    borderaxespad=0.0,  # reduce extra padding between axes and legend
)

# Optional: tidy the internal layout of the legend entries
try:
    legend._legend_box.align = "left"
except Exception:
    pass

plt.savefig("YHx_PCT_fit_2D.png", dpi=FIG_DPI, bbox_inches="tight")
plt.close(fig)

# print the RMSE values for each temperature
print("temperatures (K) and RMSE values: ", RMSE_values)

# print the average RMSE value
average_rmse = np.mean(list(RMSE_values.values()))
print(f"Average RMSE: {average_rmse:.2f}")
print(f"TMAP8 prediction RMSPE: {prediction_rmspe:.6f} %")
