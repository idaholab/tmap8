import pandas as pd
import scipy.constants as scc
import numpy as np
import matplotlib.pyplot as plt
import os

# Changes working directory to script directory (for consistent MooseDocs usage)
script_folder = os.path.dirname(__file__)
os.chdir(script_folder)


# ================================= Functions ================================ #


def read_csv_from_TMAP8(file_name, parameter_names, delimiter=","):
    # Read simulation data
    if "/tmap8/doc/" in script_folder.lower():  # if in documentation folder
        csv_folder = f"../../../../test/tests/PbLi_Natural_Circulation/{file_name}"
    else:  # if in test folder
        csv_folder = f"./{file_name}"
    simulation_data = pd.read_csv(csv_folder, delimiter=delimiter)
    simulation_results = []
    for i in range(len(parameter_names)):
        simulation_results.append(simulation_data[parameter_names[i]])
    simulation_results = np.array(simulation_results)
    return simulation_results


# =========================== TMAP8 data extraction ========================== #

# Read the output in gold file
file_name = "PbLi_Loop_transient_out.csv"
x_keys = ["time", "T01", "T20", "T21", "T40"]
dfgold = read_csv_from_TMAP8(file_name, x_keys)  # read csv file
dfgold[x_keys.index("time")] /= scc.minute  # update time unit

# dfnew = read_csv_from_TMAP8(
#     "PbLi_Loop_out.csv", ["time", "T20", "T40"], ","
# )  # read csv file

# =================================== Plot =================================== #
fig, ax = plt.subplots()
ax.set_xscale("linear")
ax.set_xscale("linear")

for i, x_key in enumerate(x_keys[1:]):
    ax.plot(
        dfgold[x_keys.index("time")],
        dfgold[x_keys.index(x_key)],
        label=x_key,
    )

# Match the original figure bounds
ax.set_xlabel("Time (Minutes)")
# Make lighter shaded lines to reflect the original figure lines. Keep the color,
# but make them transparent
# ax.plot(dfnew[0], dfnew[1], alpha=0.5)
ax.legend()
ax.set_ylabel("Temperature [K]")
fig.savefig("PbLi_Loop.png", dpi=300)
