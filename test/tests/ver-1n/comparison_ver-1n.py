import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec
import pandas as pd
from scipy import special
import os

# Use larger fonts everywhere (~2x matplotlib default of 10) per reviewer request
plt.rcParams.update({'font.size': 15})

# Changes working directory to script directory (for consistent MooseDocs usage)
script_folder = os.path.dirname(__file__)
os.chdir(script_folder)

# ========================== TMAP8 result - location ========================= #

if "/tmap8/doc/" in script_folder.lower():     # if in documentation folder
    csv_folder = "../../../../test/tests/ver-1n/gold/ver-1n_vector_postproc_30s_line_0015.csv"
else:                                  # if in test folder
    csv_folder = "./gold/ver-1n_vector_postproc_30s_line_0015.csv"
tmap_sol = pd.read_csv(csv_folder)
tmap_distance = tmap_sol['x'] / 1e6 # m
tmap_concentration_on_distance_case1 = tmap_sol['deuterium_concentration_PCC'] * 1e18 # atom/m^3

if "/tmap8/doc/" in script_folder.lower():     # if in documentation folder
    csv_folder = "../../../../test/tests/ver-1n/gold/ver-1n_vector_postproc_500s_line_0066.csv"
else:                                  # if in test folder
    csv_folder = "./gold/ver-1n_vector_postproc_500s_line_0066.csv"
tmap_sol = pd.read_csv(csv_folder)
tmap_concentration_on_distance_case2 = tmap_sol['deuterium_concentration_PCC'] * 1e18 # atom/m^3

# ============================ TMAP8 result - time =========================== #

if "/tmap8/doc/" in script_folder.lower():     # if in documentation folder
    csv_folder = "../../../../test/tests/ver-1b/gold/ver-1n_out.csv"
else:                                  # if in test folder
    csv_folder = "./gold/ver-1n_out.csv"
tmap_sol = pd.read_csv(csv_folder)
tmap_time = tmap_sol['time']
tmap_concentration_on_time_case3 = tmap_sol['concentration_point1'] * 1e18 # atom/m^3
tmap_concentration_on_time_case4 = tmap_sol['concentration_point2'] * 1e18 # atom/m^3


# ============================ Analytical solution =========================== #
# reference from:
# Luping, Tang, and Lars-Olof Nilsson.
# "Rapid determination of the chloride diffusivity in concrete by applying an electric field."
# Materials Journal 89.1 (1993): 49-53.
def concentration_analytical_solution_semi_infinity(x, t, concentration_high, constant_a, diffusivity):
    return concentration_high / 2 * (
                np.exp(constant_a * x) * special.erfc((x + constant_a * diffusivity * t) / 2 / np.sqrt(diffusivity * t)) +
                special.erfc((x - constant_a * diffusivity * t) / 2 / np.sqrt(diffusivity * t)))

# physical constants
R = 8.31446261815324 # J/mol/K
eV_to_J = 1.602176634e-19 # eV/J
N_a = 6.02214076e23 # at/mol
q = 1.602176634e-19 # C quantity of charge
F = N_a * q
# model parameters
Temperature = 773 # K
Pressure_high = 100 # Pa
V = 20 # V
L = 10e-3 # m
diffusivity = np.sqrt(3) * 1.41e-6 * np.exp( - 0.74 * eV_to_J * N_a / R / Temperature) # m^2/s
solubility =  1.06 * N_a * np.exp( - 7726.21 / R / Temperature) # atom/m^3/Pa^0.5
z = 1
# derivative parameters
E = V / L
constant_a = z * F / R / Temperature * E
concentration_high = solubility * np.sqrt(Pressure_high)

t_case1 = 30 # s
t_case2 = 500 # s
x_case3 = 100/1e6 # m
x_case4 = 500/1e6 # m
concentration_case1 = concentration_analytical_solution_semi_infinity(
                            tmap_distance, t_case1, concentration_high, constant_a, diffusivity)
concentration_case2 = concentration_analytical_solution_semi_infinity(
                            tmap_distance, t_case2, concentration_high, constant_a, diffusivity)
concentration_case3 = concentration_analytical_solution_semi_infinity(
                            x_case3, tmap_time, concentration_high, constant_a, diffusivity)
concentration_case4 = concentration_analytical_solution_semi_infinity(
                            x_case4, tmap_time, concentration_high, constant_a, diffusivity)


# ============================================================================ #
# Plot figure for verification on location
fig = plt.figure(figsize=[6.5, 5.5])
gs = gridspec.GridSpec(1, 1)
ax = fig.add_subplot(gs[0])

ax.plot(tmap_distance, tmap_concentration_on_distance_case1, label=r"TMAP8 - 30s", c='C0', alpha=0.3) # numerical solution
ax.plot(tmap_distance, concentration_case1, c=f'C0', linestyle='--', label = f"Analytical results - 30s")
ax.plot(tmap_distance, tmap_concentration_on_distance_case2, label=r"TMAP8 - 500s", c='C1', alpha=0.3) # numerical solution
ax.plot(tmap_distance, concentration_case2, c=f'C1', linestyle='--', label = f"Analytical results - 500s")

ax.set_xlabel(u'Location (m)')
ax.set_ylabel(u"Concentration (atom/m$^3$)")
ax.legend(loc=[0.35,0.68])
ax.set_xlim(left=0, right=0.00126)
ax.set_ylim(bottom=0, top=2.2e24)
plt.grid(visible=True, which='major', color='0.65', linestyle='--', alpha=0.3)
RMSPE_case1 = np.sqrt(np.mean((tmap_concentration_on_distance_case1-concentration_case1)**2)) / np.mean(concentration_case1) * 100
ax.text(1.5e-4,0.5e24, 'RMSPE = %.2f '%RMSPE_case1+'%',fontweight='bold', c='C0')
RMSPE_case2 = np.sqrt(np.mean((tmap_concentration_on_distance_case2-concentration_case2)**2)) / np.mean(concentration_case2) * 100
ax.text(7.0e-4,0.75e24, 'RMSPE = %.2f '%RMSPE_case2+'%',fontweight='bold', c='C1')
ax.minorticks_on()
plt.savefig('ver-1n_comparison_location.png', bbox_inches='tight', dpi=300)
plt.close(fig)

# ============================================================================ #
# Plot figure for verification on time
fig = plt.figure(figsize=[6.5, 5.5])
gs = gridspec.GridSpec(1, 1)
ax = fig.add_subplot(gs[0])

ax.plot(tmap_time, tmap_concentration_on_time_case3, label=r"TMAP8 - point1", c='C0', alpha=0.3) # numerical solution
ax.plot(tmap_time, concentration_case3, c=f'C0', linestyle='--', label = f"Analytical results - point1")
ax.plot(tmap_time, tmap_concentration_on_time_case4, label=r"TMAP8 - point2", c='C1', alpha=0.3) # numerical solution
ax.plot(tmap_time, concentration_case4, c=f'C1', linestyle='--', label = f"Analytical results - point2")

ax.set_xlabel(u'Time (s)')
ax.set_ylabel(u"Concentration (atom/m$^3$)")
ax.legend(loc=[0.05,0.68])
ax.set_xlim(left=0, right=510)
ax.set_ylim(bottom=0, top=2.8e24)
plt.grid(visible=True, which='major', color='0.65', linestyle='--', alpha=0.3)
RMSPE_case3 = np.sqrt(np.mean((tmap_concentration_on_time_case3-concentration_case3)**2)) / np.mean(concentration_case3) * 100
ax.text(60,0.5e24, 'RMSPE = %.2f '%RMSPE_case3+'%',fontweight='bold', c='C0')
RMSPE_case4 = np.sqrt(np.mean((tmap_concentration_on_time_case4-concentration_case4)**2)) / np.mean(concentration_case4) * 100
ax.text(300,0.1e24, 'RMSPE = %.2f '%RMSPE_case4+'%',fontweight='bold', c='C1')
ax.minorticks_on()
plt.savefig('ver-1n_comparison_time.png', bbox_inches='tight', dpi=300)
plt.close(fig)
