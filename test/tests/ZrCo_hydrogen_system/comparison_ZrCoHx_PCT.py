# Import Required Libraries
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.lines import Line2D

# ------------------------------------------------------------------------------
# Setup
# ------------------------------------------------------------------------------
script_folder = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_folder)

TEMPERATURES_K = [423, 524, 544, 564, 584, 604, 624]  # K
ATOM_RATIO_LOW = 0.7
ATOM_RATIO_HIGH = 1.1
FIG_DPI = 300
N_SMOOTH = 1000  # number of points for smoother analytical curves

COL_PRESSURE_PA = "Partial Pressure"
COL_ATOM_RATIO = "Atom Ratio"
COL_TMAP_T = "temperature"
COL_TMAP_P = "pressure_H2_enclosure_1_at_interface"
COL_TMAP_AF = "atomic_fraction_H_enclosure_2_at_interface"

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
if "/tmap8/doc/" in script_folder.lower():
    root = "../../../../../test/tests/ZrCo_hydrogen_system/"
else:
    root = ""

folderPath = root
exp_data_dir = os.path.join(folderPath, "PCT_data")
gold_dir = os.path.join(folderPath, "gold")


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------
def p0_lim_func(T):
    return np.exp(-9.41 + 3.32e-2 * T - 3.30e-06 * T * T)


def atom_ratio_eq_lower_func(T, P):
    p0 = p0_lim_func(T)
    arg = np.maximum(p0 - P, 1e-10)
    return 0.7 - (
        5.0e-03
        + np.exp(-4.37 + 1.34e-02 * T + (-8.22e-02 - 3.97e-04 * T) * np.log(arg))
    ) ** (-1)


def rmse(y_true, y_pred):
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


def atom_ratio_eq_upper_func(T, P):
    p0 = p0_lim_func(T)
    arg = np.maximum(P - p0, 1e-10)
    return 2.7 - 1.45 * (
        1.0 + np.exp(6.57 - 2.21e-02 * T + (6.52e-01 - 1.17e-05 * T) * np.log(arg))
    ) ** (-1)


# ---------------------------------------------------------------------------
# Load experimental data
# ---------------------------------------------------------------------------
data_by_temp = {}
for Tk in TEMPERATURES_K:
    df = pd.read_csv(os.path.join(exp_data_dir, f"{Tk}.csv"))
    df = df[[COL_PRESSURE_PA, COL_ATOM_RATIO]].dropna().sort_values(COL_PRESSURE_PA)
    data_by_temp[Tk] = df.reset_index(drop=True)

# ---------------------------------------------------------------------------
# Raw plot [unchanged, separate file]
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(10, 6))
for T in TEMPERATURES_K:
    df = data_by_temp.get(T)
    plt.scatter(df[COL_ATOM_RATIO], df[COL_PRESSURE_PA], s=28, label=f"{T}.15 K")
    plt.plot(df[COL_ATOM_RATIO], df[COL_PRESSURE_PA])
plt.yscale("log")
plt.xlabel("Atom Ratio (-)")
plt.ylabel("Partial Pressure (Pa)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("ZrCoHx_PCT_Data.png", dpi=FIG_DPI)
plt.close(fig)

# ---------------------------------------------------------------------------
# Plateau fit [unchanged, separate file]
# ---------------------------------------------------------------------------
p0_vals = p0_lim_func(np.array(TEMPERATURES_K))
sel_T, sel_P = [], []
for T in TEMPERATURES_K:
    df = data_by_temp[T]
    AR = df[COL_ATOM_RATIO].values
    P = df[COL_PRESSURE_PA].values
    idx = np.where(AR > ATOM_RATIO_LOW)[0]
    if idx.size:
        sel_T.append(T)
        sel_P.append(P[idx[0]])

fig = plt.figure(figsize=(5, 5))
plt.plot(TEMPERATURES_K, p0_vals, "--", label="Fit")
if sel_T:
    plt.scatter(sel_T, sel_P, color="red", label="Plateau Pressures")
plt.yscale("log")
plt.xlabel("Temperature (K)")
plt.ylabel("Pressure (Pa)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("ZrCoHx_PCT_plateau_pressure_fit.png", dpi=FIG_DPI)
plt.close(fig)

# ---------------------------------------------------------------------------
# Load TMAP8 predictions (single-point, for the analytical-fit portion)
# ---------------------------------------------------------------------------
low_files = {"ZrCoHx_PCT_T524_5E2P_out.csv", "ZrCoHx_PCT_T604_5E2P_out.csv"}
high_files = {
    "ZrCoHx_PCT_T423_1E4P_out.csv",
    "ZrCoHx_PCT_T524_3E4P_out.csv",
    "ZrCoHx_PCT_T604_5E4P_out.csv",
}

tmap_low = {}
for f in low_files:
    path = os.path.join(gold_dir, f)
    if os.path.exists(path):
        tmap_low[f] = pd.read_csv(path)

tmap_high = {}
for f in high_files:
    path = os.path.join(gold_dir, f)
    if os.path.exists(path):
        tmap_high[f] = pd.read_csv(path)


def overlay_tmap(dfp, ax):
    T_pred = dfp[COL_TMAP_T].iat[-1]
    P_pred = dfp[COL_TMAP_P].iat[-1]
    AF_pred = dfp[COL_TMAP_AF].iat[-1]

    p0 = p0_lim_func(T_pred)
    if P_pred < p0:
        AF_model = atom_ratio_eq_lower_func(T_pred, np.array([P_pred]))[0]
        marker = "*"
    else:
        AF_model = atom_ratio_eq_upper_func(T_pred, np.array([P_pred]))[0]
        marker = "x"

    err = abs(AF_pred - AF_model) / AF_model * 100 if AF_model != 0 else np.nan

    ax.scatter(
        AF_pred,
        P_pred,
        marker=marker,
        color="k",
        s=90,
        label=f"TMAP8 {int(T_pred)}.15 K, {P_pred:.2e} Pa (err {err:.2f}%)",
    )


# ---------------------------------------------------------------------------
# MAPE helper (for the TMAP8 low-to-high sweep portion)
# ---------------------------------------------------------------------------
def compute_mape(ar_t, p_t, ar_e, p_e):
    # Sort the TMAP8 curve
    ar_t = ar_t[np.argsort(ar_t)]
    p_t = p_t[np.argsort(ar_t)]
    # Sort the Experimental curve
    ar_e = ar_e[np.argsort(ar_e)]
    p_e = p_e[np.argsort(p_e)]

    # Determine the overlapping x-range between the two curves
    lo = max(ar_e.min(), ar_t.min())
    hi = min(ar_e.max(), ar_t.max())

    # Keep only experimental points that fall within the overlapping range
    mask = (ar_e >= lo) & (ar_e <= hi)
    ar_e2 = ar_e[mask]
    p_e2 = p_e[mask]

    # Interpolate experimental curve values at the x-locations of TMAP8 curves
    p_interp = np.interp(ar_e2, ar_t, p_t)
    return np.mean(np.abs((p_interp - p_e2) / p_e2)) * 100


# ----------------------------------------------------------------------------
# - Plots exp scatter vs TMAP8 dashed
# - Calculates MAPE on overlapping atomic-ratio range
# ----------------------------------------------------------------------------

base = Path(__file__).resolve().parent
exp_dir = base / "PCT_data"

fig, ax = plt.subplots(figsize=(12, 10))

fallback_cmap = plt.get_cmap("tab10")
fallback_colors = {}
fb_idx = 0


def get_color_for_temp(Tk):
    global fb_idx
    Tk = int(Tk)
    fallback_colors[Tk] = fallback_cmap(fb_idx % 10)
    fb_idx += 1
    return fallback_colors[Tk]


for Tk in TEMPERATURES_K:
    df = data_by_temp[Tk]
    P = df[COL_PRESSURE_PA].values
    AR = df[COL_ATOM_RATIO].values
    color_T = get_color_for_temp(Tk)

    # --- Plot ALL experimental points for this temperature ONCE, so there's
    #     a single "Data" legend entry per temperature instead of one for the
    #     low-pressure branch and another for the high-pressure branch.
    ax.scatter(AR, P, color=color_T, label=f"{Tk}.15 K Data")

    idx_low = AR < ATOM_RATIO_LOW
    if np.any(idx_low):
        P_lo = P[idx_low]
        AR_lo = AR[idx_low]
        fit_lo = atom_ratio_eq_lower_func(Tk, P_lo)

        Pmin = float(np.nanmax([np.min(P_lo), 1e-12]))
        Pmax = float(np.max(P_lo))
        Ps = np.geomspace(Pmin, Pmax, N_SMOOTH)
        fits = atom_ratio_eq_lower_func(Tk, Ps)
        ax.plot(
            fits,
            Ps,
            linestyle="-",
            marker="^",
            markevery=0.05,
            markersize=7,
            lw=1.2,
            markeredgecolor="black",
            markerfacecolor='none',
            color=color_T,
            # Tag as the Low-P (lower plateau) fit
            label=f"{Tk}.15 K Low P Fit RMSE {rmse(AR_lo, fit_lo):.3f}",
        )

    idx_mid = (AR >= ATOM_RATIO_LOW) & (AR < 1.4)
    # mid-range points already covered by the single scatter call above;
    # nothing else to plot/label here.

    idx_hi = AR >= 1.4
    if np.any(idx_hi):
        P_hi = P[idx_hi]
        AR_hi = AR[idx_hi]
        fit_hi = atom_ratio_eq_upper_func(Tk, P_hi)
        mask = np.isfinite(fit_hi)
        P_hi = P_hi[mask]
        AR_hi = AR_hi[mask]
        fit_hi = fit_hi[mask]

        if Tk == 524:
            Pmin = float(np.nanmax([np.min(P_hi) + 355, 1e-12]))
        else:
            Pmin = float(np.nanmax([np.min(P_hi), 1e-12]))
        Pmax = float(np.max(P_hi))
        Ps = np.geomspace(Pmin, Pmax, N_SMOOTH)
        fits = atom_ratio_eq_upper_func(Tk, Ps)
        ax.plot(
            fits,
            Ps,
            linestyle="-",
            marker="o",
            markevery=0.08,
            markersize=7,
            markeredgecolor="black",
            markerfacecolor='none',
            lw=1.2,
            color=color_T,
            # Tag as the High-P (upper plateau) fit
            label=f"{Tk}.15 K High P Fit RMSE {rmse(AR_hi, fit_hi):.3f}",
        )

for dfp in tmap_low.values():
    overlay_tmap(dfp, ax)
for dfp in tmap_high.values():
    overlay_tmap(dfp, ax)


for Tk in TEMPERATURES_K:
    df = data_by_temp.get(Tk)
    ar_exp = df[COL_ATOM_RATIO].values
    p_exp = df[COL_PRESSURE_PA].values

    tmap_name = f"ZrCoHx_PCT_Low_to_High_{int(Tk)}K.csv"
    tmap_path = os.path.join(gold_dir, tmap_name)
    df_tmap = pd.read_csv(tmap_path)

    ar_tmap = (
        df_tmap["atomic_fraction_H_enclosure_2_at_interface"].astype(float).to_numpy()
    )
    p_tmap = df_tmap["pressure_H2_enclosure_1_at_interface"].astype(float).to_numpy()

    mape = compute_mape(ar_tmap, p_tmap, ar_exp, p_exp)

    order = np.argsort(ar_tmap)
    ax.plot(
        ar_tmap[order],
        p_tmap[order],
        linestyle=":",
        lw=2,
        label=f"TMAP8 {int(Tk)}.15 K (err={mape:.2f}%)",
    )

ax.set_yscale("log")
ax.set_xlabel("Atom Ratio (-)")
ax.set_ylabel("Partial Pressure (Pa)")
ax.grid(True, which="both", ls="--", alpha=0.6)

# ---- Group into Data / Fit / TMAP8 single-point / TMAP8 sweep ----
handles, labels = ax.get_legend_handles_labels()

data_h, data_l = [], []
fit_h, fit_l = [], []
tmap_single_h, tmap_single_l = [], []
tmap_sweep_h, tmap_sweep_l = [], []

for h, l in zip(handles, labels):
    if "Data" in l:
        data_h.append(h)
        data_l.append(l)
    elif "Fit RMSE" in l:
        fit_h.append(h)
        fit_l.append(l)
    elif l.startswith("TMAP8") and "Pa (err" in l:  # single-point *,x markers
        tmap_single_h.append(h)
        tmap_single_l.append(l)
    else:  # TMAP8 sweep curves
        tmap_sweep_h.append(h)
        tmap_sweep_l.append(l)

# ---- Pad shorter columns with invisible entries so columns align ----
n_rows = max(len(data_h), len(fit_h), len(tmap_single_h), len(tmap_sweep_h))


def pad(hs, ls, n):
    blank = Line2D([], [], color="none")
    hs = hs + [blank] * (n - len(hs))
    ls = ls + [""] * (n - len(ls))
    return hs, ls


data_h, data_l = pad(data_h, data_l, n_rows)
fit_h, fit_l = pad(fit_h, fit_l, n_rows)
tmap_single_h, tmap_single_l = pad(tmap_single_h, tmap_single_l, n_rows)
tmap_sweep_h, tmap_sweep_l = pad(tmap_sweep_h, tmap_sweep_l, n_rows)

# Column-major concatenation: col1=Data, col2=Fit, col3=TMAP8 single-point, col4=TMAP8 sweep
handles = data_h + fit_h + tmap_single_h + tmap_sweep_h
labels = data_l + fit_l + tmap_single_l + tmap_sweep_l

ax.legend(
    handles,
    labels,
    loc="upper center",
    bbox_to_anchor=(0.5, -0.01),
    ncol=4,
    fontsize=8,
    handletextpad=0.6,
    columnspacing=1.2,
    handlelength=3.5,
)

fig.tight_layout()
plt.savefig("ZrCoHx_PCT_combined.png", dpi=FIG_DPI, bbox_inches="tight")
plt.close(fig)
