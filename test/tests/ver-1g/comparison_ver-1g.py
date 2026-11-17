import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
import pandas as pd
from scipy import special
import os

# Changes working directory to script directory (for consistent MooseDocs usage)
script_folder = os.path.dirname(__file__)
os.chdir(script_folder)

fig = plt.figure(figsize=[6.5, 5.5])
gs = gridspec.GridSpec(1, 1)
ax = fig.add_subplot(gs[0])

# ==============================================================================

# TMAP4 case
if "/tmap8/doc/" in script_folder.lower():  # if in documentation folder
    csv_folder = "../../../../test/tests/ver-1g/gold/diff_conc_TMAP4_out.csv"
else:  # if in test folder
    csv_folder = "./gold/diff_conc_TMAP4_out.csv"
tmap_sol = pd.read_csv(csv_folder)
tmap_time = tmap_sol["time"]
tmap_concAB_TMAP4 = tmap_sol["conc_ab"]
ax.plot(
    tmap_time,
    tmap_concAB_TMAP4,
    linewidth=2,
    label=r"TMAP8 (TMAP4 case)",
    c="tab:brown",
)

# TMAP7 case
if "/tmap8/doc/" in script_folder.lower():  # if in documentation folder
    csv_folder = "../../../../test/tests/ver-1g/gold/diff_conc_TMAP7_out.csv"
else:  # if in test folder
    csv_folder = "./gold/diff_conc_TMAP7_out.csv"
tmap_sol = pd.read_csv(csv_folder)
tmap_time = tmap_sol["time"]
tmap_concAB_TMAP7 = tmap_sol["conc_ab"]
ax.plot(
    tmap_time, tmap_concAB_TMAP7, linewidth=2, label=r"TMAP8 (TMAP7 case)", c="tab:gray"
)


def get_conc_from_pressure(P):
    R = 8.31446261815324  # Gas constant (from TMAP8PhysicalConstants.h)
    T = 25 + 273.15  # Temperature (25 C -> K)
    Na = 6.02214076e23  # Avogadro's constant (from TMAP8PhysicalConstants.h)
    m3_to_microns3 = 1e18  # Convert m^3 to microns^3
    # Using ideal gas law
    return P * Na / (R * T * m3_to_microns3)


def get_concAB_diff(analytical_time, P_A0, P_B0):
    concA_o = get_conc_from_pressure(P_A0)  # atoms / microns^3
    concB_o = get_conc_from_pressure(P_B0)  # atoms / microns^3
    K = 4.14e3  # molecule.m^3/atom^2/s
    exponential_term = np.exp(K * analytical_time * (concB_o - concA_o))
    analytical_concAB = (
        concB_o * (1 - exponential_term) / (1 - (concB_o / concA_o) * exponential_term)
    )
    return analytical_concAB


analytical_time = tmap_time

# TMAP4
P_A0 = 1e-6  # Pressure (Pa)
P_B0 = 1e-7  # Pressure (Pa)
analytical_concAB_diff_TMAP4 = get_concAB_diff(analytical_time, P_A0, P_B0)

ax.plot(
    analytical_time,
    analytical_concAB_diff_TMAP4,
    "--",
    c="tab:cyan",
    dashes=(5, 5),
    label=r"Analytical TMAP4",
)

# TMAP7
P_A0 = 1e-6  # Pressure (Pa)
P_B0 = 5e-7  # Pressure (Pa)
analytical_concAB_diff_TMAP7 = get_concAB_diff(analytical_time, P_A0, P_B0)

ax.plot(
    analytical_time,
    analytical_concAB_diff_TMAP7,
    "k--",
    dashes=(5, 5),
    label=r"Analytical TMAP7",
)

ax.set_xlabel("Time (seconds)")
ax.set_ylabel("Concentration of AB (atoms / $\mu$m$^3$)")
ax.legend(loc="best")
ax.set_xlim(left=0)
ax.set_ylim(bottom=0)
plt.grid(visible=True, which="major", color="0.65", linestyle="--", alpha=0.3)
RMSE = np.sqrt(
    np.mean((tmap_concAB_TMAP4 - analytical_concAB_diff_TMAP4) ** 2)
)  # TMAP4
RMSPE = RMSE * 100 / np.mean(analytical_concAB_diff_TMAP4)
ax.text(10, 1.8e-5, "RMSPE = %.2f " % RMSPE + "%", fontweight="bold", c="k")
RMSE = np.sqrt(
    np.mean((tmap_concAB_TMAP7 - analytical_concAB_diff_TMAP7) ** 2)
)  # TMAP7
RMSPE = RMSE * 100 / np.mean(analytical_concAB_diff_TMAP7)
ax.text(10, 11.5e-5, "RMSPE = %.2f " % RMSPE + "%", fontweight="bold", c="k")
ax.minorticks_on()
plt.savefig("ver-1g_comparison_diff_conc.png", bbox_inches="tight", dpi=300)

plt.close(fig)

# ==============================================================================
fig = plt.figure(figsize=[6.5, 5.5])
gs = gridspec.GridSpec(1, 1)
ax = fig.add_subplot(gs[0])

if "/tmap8/doc/" in script_folder.lower():  # if in documentation folder
    csv_folder = "../../../../test/tests/ver-1g/gold/equal_conc_out.csv"
else:  # if in test folder
    csv_folder = "./gold/equal_conc_out.csv"
tmap_sol = pd.read_csv(csv_folder)
tmap_time = tmap_sol["time"]
tmap_concAB = tmap_sol["conc_ab"]
ax.plot(tmap_time, tmap_concAB, label=r"TMAP8", c="tab:gray")


def get_concAB_equal(analytical_time, P_A0):
    concA_o = get_conc_from_pressure(P_A0)  # atoms / microns^3
    K = 4.14e3  # molecule.m^3/atom^2/s
    analytical_concAB = concA_o - 1 / (1 / concA_o + K * analytical_time)
    return analytical_concAB


analytical_time = tmap_time
P_A0 = 1e-6  # Pressure (Pa) (which is equal to P_B0)
analytical_concAB_diff = get_concAB_equal(analytical_time, P_A0)

ax.plot(
    analytical_time, analytical_concAB_diff, "k--", dashes=(5, 5), label=r"Analytical"
)

ax.set_xlabel("Time (seconds)")
ax.set_ylabel("Concentration of AB (atoms / $\mu$m$^3$)")
ax.legend(loc="best")
ax.set_xlim(left=0)
ax.set_ylim(bottom=0)
plt.grid(visible=True, which="major", color="0.65", linestyle="--", alpha=0.3)
RMSE = np.sqrt(np.mean((tmap_concAB - analytical_concAB_diff) ** 2))
RMSPE = RMSE * 100 / np.mean(analytical_concAB_diff)
ax.text(10, 21e-5, "RMSPE = %.2f " % RMSPE + "%", fontweight="bold", c="k")
ax.minorticks_on()
plt.savefig("ver-1g_comparison_equal_conc.png", bbox_inches="tight", dpi=300)

plt.close(fig)
