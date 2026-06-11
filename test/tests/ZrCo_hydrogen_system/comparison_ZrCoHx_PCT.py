# Import Required Libraries
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ------------------------------------------------------------------------------
# Setup
# ------------------------------------------------------------------------------
script_folder = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_folder)

TEMPERATURES_K = [423, 524, 544, 564, 584, 604, 624]
ATOM_RATIO_LOW = 0.7
ATOM_RATIO_HIGH = 1.0
FIG_DPI = 300
N_SMOOTH = 1000

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
    return np.exp(-9.4114 + 3.3226e-02 * T - 3.2909e-06 * T * T)


def atom_ratio_eq_lower_func(T, P):
    p0 = p0_lim_func(T)
    arg = np.maximum(p0 - P, 1e-10)
    return 0.7 - (
        5e-03
        + np.exp(-4.37 + 1.3408e-02 * T + (-8.217e-02 - 3.9745e-04 * T) * np.log(arg))
    ) ** (-1)


def rmse(y_true, y_pred):
    return np.sqrt(np.mean((y_true - y_pred) ** 2))


def atom_ratio_eq_upper_func(T, P):
    p0 = p0_lim_func(T)
    arg = np.maximum(P - p0, 1e-10)
    return 2.7 - 1.4529 * (
        1.0
        + np.exp(6.5726 - 2.2087e-02 * T + (6.5206e-01 - 1.1738e-05 * T) * np.log(arg))
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
# Raw plot
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(10, 6))
for T in TEMPERATURES_K:
    df = data_by_temp.get(T)
    plt.scatter(df[COL_ATOM_RATIO], df[COL_PRESSURE_PA], s=28, label=f"{T}.15 K")
    plt.plot(df[COL_ATOM_RATIO], df[COL_PRESSURE_PA])
plt.yscale("log")
plt.xlabel("Atom Ratio (-)")
plt.ylabel("Pressure (Pa)")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("ZrCoHx_PCT_Data.png", dpi=FIG_DPI)
plt.close(fig)

# ---------------------------------------------------------------------------
# Plateau fit
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
# Load TMAP8 predictions
# ---------------------------------------------------------------------------
low_files = {"ZrCoHx_PCT_T524_5E2P_out.csv", "ZrCoHx_PCT_T604_5E2P_out.csv"}
high_files = {
    "ZrCoHx_PCT_T423_1E4P_out.csv",
    "ZrCoHx_PCT_T524_3E4P_out.csv",
    "ZrCoHx_PCT_T604_5E4P_out.csv",
}

tmap_low = {}
for f in low_files:
    p = os.path.join(gold_dir, f)
    if os.path.exists(p):
        tmap_low[f] = pd.read_csv(p)

tmap_high = {}
for f in high_files:
    p = os.path.join(gold_dir, f)
    if os.path.exists(p):
        tmap_high[f] = pd.read_csv(p)

# ---------------------------------------------------------------------------
# Combined figure: low + high + TMAP8 overlay
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(12, 8))

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

    idx_low = AR < ATOM_RATIO_LOW
    if np.any(idx_low):
        P_lo = P[idx_low]
        AR_lo = AR[idx_low]
        fit_lo = atom_ratio_eq_lower_func(Tk, P_lo)
        plt.scatter(AR_lo, P_lo, color=color_T, label=f"{Tk}.15 K Data")

        Pmin = float(np.nanmax([np.min(P_lo), 1e-12]))
        Pmax = float(np.max(P_lo))
        Ps = np.geomspace(Pmin, Pmax, N_SMOOTH)
        fits = atom_ratio_eq_lower_func(Tk, Ps)
        plt.plot(
            fits,
            Ps,
            "--",
            color=color_T,
            label=f"{Tk}.15 K Fit RMSE {rmse(AR_lo, fit_lo):.3f}",
        )

    idx_hi = AR >= ATOM_RATIO_HIGH
    if np.any(idx_hi):
        P_hi = P[idx_hi]
        AR_hi = AR[idx_hi]
        fit_hi = atom_ratio_eq_upper_func(Tk, P_hi)
        mask = np.isfinite(fit_hi)
        P_hi = P_hi[mask]
        AR_hi = AR_hi[mask]
        fit_hi = fit_hi[mask]

        plt.scatter(AR_hi, P_hi, color=color_T, label=f"{Tk}.15 K Data")

        Pmin = float(np.nanmax([np.min(P_hi), 1e-12]))
        Pmax = float(np.max(P_hi))
        Ps = np.geomspace(Pmin, Pmax, N_SMOOTH)
        fits = atom_ratio_eq_upper_func(Tk, Ps)
        plt.plot(
            fits,
            Ps,
            "-",
            color=color_T,
            label=f"{Tk}.15 K Fit RMSE {rmse(AR_hi, fit_hi):.3f}",
        )


def overlay_tmap(dfp):
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

    plt.scatter(
        AF_pred,
        P_pred,
        marker=marker,
        color="k",
        s=90,
        label=f"{int(T_pred)}.15 K, {P_pred:.2e} Pa (err {err:.2f}%)",
    )


for df in tmap_low.values():
    overlay_tmap(df)
for df in tmap_high.values():
    overlay_tmap(df)

plt.yscale("log")
plt.ylabel("Pressure (Pa)")
plt.xlabel("Atom Ratio (-)")
plt.grid(True)
plt.legend(bbox_to_anchor=(1.18, 1.02))
plt.tight_layout()
plt.savefig("ZrCoHx_PCT_fit_2D.png", dpi=FIG_DPI)
plt.close(fig)
"""
• Plots exp scatter vs TMAP8 dashed
• Calculates MAPE on overlapping atomic‑ratio range
"""

from pathlib import Path


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


fig, ax = plt.subplots(figsize=(12, 8))


for Tk in TEMPERATURES_K:
    df = data_by_temp.get(Tk)
    ar_exp = df[COL_ATOM_RATIO].values
    p_exp = df[COL_PRESSURE_PA].values

    # ---------------------------
    # Load TMAP8
    # ---------------------------
    tmap_name = f"ZrCoHx_PCT_Low_to_High_{int(Tk)}K.csv"
    tmap_path = os.path.join(gold_dir, tmap_name)
    df_tmap = pd.read_csv(tmap_path)

    ar_tmap = (
        df_tmap["atomic_fraction_H_enclosure_2_at_interface"].astype(float).to_numpy()
    )
    p_tmap = df_tmap["pressure_H2_enclosure_1_at_interface"].astype(float).to_numpy()

    mask = np.isfinite(ar_tmap) & np.isfinite(p_tmap) & (p_tmap > 1e-12)
    ar_tmap = ar_tmap[mask]
    p_tmap = p_tmap[mask]

    # ---------------------------
    # MAPE
    # ---------------------------
    mape = compute_mape(ar_tmap, p_tmap, ar_exp, p_exp)

    # ---------------------------
    # Plot
    # ---------------------------
    ax.scatter(ar_exp, p_exp, s=30, label=f"Exp {int(Tk)}.15 K")
    order = np.argsort(ar_tmap)
    ax.plot(
        ar_tmap[order],
        p_tmap[order],
        "--",
        lw=2,
        label=f"TMAP {int(Tk)}.15 K ( err {mape:.2f}%)",
    )

# ---------------------------
# --- Finalize figure ---
ax.set_yscale("log")
ax.set_xlabel("Atom Ratio (–)")
ax.set_ylabel("Pressure (Pa)")
ax.grid(True, which="both", ls="--", alpha=0.6)
ax.legend(fontsize=9, loc="best", ncol=2)
fig.tight_layout()
fig.savefig("PCT_all_temperatures_experimental_vs_TMAP8_ZrCo.png", dpi=300)
plt.close(fig)
