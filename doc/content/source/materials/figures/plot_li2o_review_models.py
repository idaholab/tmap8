#!/usr/bin/env python3

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import gridspec

R = 8.31446261815324  # J/mol/K

SCRIPT_DIR = Path(__file__).resolve().parent
FIG_DIR = SCRIPT_DIR


DIFFUSIVITY_MODELS = {
    "Ohira1989": {
        "prefactor_m2_s": 1.2e-11,
        "activation_j_mol": 45.1e3,
        "temp_range_k": (600.0, 711.0),
        "label": "Ohira1989, unirradiated single crystal",
    },
    "Tanifuji1987": {
        "prefactor_m2_s": 1.16e-5,
        "activation_j_mol": 101.0e3,
        "temp_range_k": (573.0, 950.0),
        "label": "Tanifuji1987, neutron-irradiated single crystal",
    },
    "Kurasawa1991": {
        "prefactor_m2_s": 2.0e-7,
        "activation_j_mol": 81.7e3,
        "temp_range_k": (450.0 + 273.15, 820.0 + 273.15),
        "label": "Kurasawa1991, in-situ single crystal",
    },
    "Terai1988Grain": {
        "prefactor_m2_s": 1.27e-9,
        "activation_j_mol": 54.9e3,
        "temp_range_k": (360.0 + 273.15, 600.0 + 273.15),
        "label": "Terai1988Grain, neutron-irradiated polycrystal grain",
    },
    "Terai1988GrainBoundary": {
        "prefactor_m2_s": 1.61e-2,
        "activation_j_mol": 95.1e3,
        "temp_range_k": (360.0 + 273.15, 600.0 + 273.15),
        "label": "Terai1988GrainBoundary, neutron-irradiated polycrystal grain boundary",
    },
}


SOLUBILITY_MODELS = {
    "Ohira1989Tritium": {
        "a": 1290.0,
        "b": 1.14,
        "temp_range_k": (300.0 + 273.15, 1000.0),
        "label": "Ohira1989Tritium, tritium in unirradiated single crystal",
    },
    "Ohira1989Hydrogen": {
        "a": 1271.0,
        "b": 2.33,
        "temp_range_k": (200.0 + 273.15, 1000.0),
        "label": "Ohira1989Hydrogen, Hydrogen in unirradiated single crystal",
    },
}


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


def diffusivity_m2_s(
    prefactor_m2_s: float, activation_j_mol: float, temperature_k: np.ndarray
):
    return prefactor_m2_s * np.exp(-activation_j_mol / (R * temperature_k))


def solubility_atm_0_5(a: float, b: float, temperature_k: np.ndarray):
    return 10.0 ** (a / temperature_k + b)


def inverse_temperature_axis(temperature_k: np.ndarray):
    return 1000.0 / temperature_k


def temperature_from_inverse_axis(inverse_temperature):
    inverse_temperature = np.asarray(inverse_temperature)
    result = np.full_like(inverse_temperature, np.nan, dtype=float)
    mask = inverse_temperature != 0.0
    result[mask] = 1000.0 / inverse_temperature[mask]
    return result


def inverse_axis_from_temperature(temperature_k):
    temperature_k = np.asarray(temperature_k)
    result = np.full_like(temperature_k, np.nan, dtype=float)
    mask = temperature_k != 0.0
    result[mask] = 1000.0 / temperature_k[mask]
    return result


def add_temperature_top_axis(ax, temperature_ticks_k):
    secax = ax.secondary_xaxis(
        "top", functions=(temperature_from_inverse_axis, inverse_axis_from_temperature)
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
    ordered = sorted(
        line_info,
        key=lambda item: np.interp(
            reference_temperature_k, item["temperature_k"], item["y_values"]
        ),
        reverse=True,
    )
    handles = [item["handle"] for item in ordered]
    labels = [item["label"] for item in ordered]
    return handles, labels


def plot_diffusivity():
    fig = plt.figure(figsize=[6.5, 7.0])
    gs = gridspec.GridSpec(1, 1)
    ax = fig.add_subplot(gs[0])
    line_info = []

    for model in DIFFUSIVITY_MODELS.values():
        t_min, t_max = model["temp_range_k"]
        temperature = np.linspace(t_min, t_max, 250)
        inverse_temperature = inverse_temperature_axis(temperature)
        diffusivity = diffusivity_m2_s(
            model["prefactor_m2_s"], model["activation_j_mol"], temperature
        )
        (line,) = ax.plot(
            inverse_temperature, diffusivity, linewidth=2.0, label=model["label"]
        )
        line_info.append(
            {
                "handle": line,
                "label": model["label"],
                "temperature_k": temperature,
                "y_values": diffusivity,
            }
        )

    ax.set_yscale("log")
    apply_axes_style(
        ax,
        r"1000 / Temperature (K$^{-1}$)",
        r"$D$ (m$^2$/s)",
    )
    add_temperature_top_axis(ax, [600.0, 700.0, 800.0, 900.0, 1000.0])
    handles, labels = order_legend_by_reference_y(line_info, 700.0)
    ax.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        borderaxespad=0.0,
        ncol=1,
    )
    fig.tight_layout()
    fig.savefig(FIG_DIR / "li2o_diffusivity_models.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_solubility():
    fig = plt.figure(figsize=[6.5, 5.5])
    gs = gridspec.GridSpec(1, 1)
    ax = fig.add_subplot(gs[0])
    line_info = []

    for model in SOLUBILITY_MODELS.values():
            t_min, t_max = model["temp_range_k"]
            temperature = np.linspace(t_min, t_max, 250)
            inverse_temperature = inverse_temperature_axis(temperature)
            solubility = solubility_atm_0_5(model["a"], model["b"], temperature)
            (line,) = ax.plot(
                inverse_temperature, solubility, linewidth=2.0, label=model["label"]
            )
            line_info.append(
                {
                    "handle": line,
                    "label": model["label"],
                    "temperature_k": temperature,
                    "y_values": solubility,
                }
            )

    ax.set_yscale("log")
    apply_axes_style(
        ax,
        r"1000 / Temperature (K$^{-1}$)",
        r"$K_s$ (atm$^{1/2}$)",
    )
    add_temperature_top_axis(ax, [400.0, 500.0, 600.0, 700.0, 800.0, 900.0, 1000.0, 1100.0])
    handles, labels = order_legend_by_reference_y(line_info, 700.0)
    ax.legend(
        handles,
        labels,
        loc="upper center",
        bbox_to_anchor=(0.5, -0.15),
        borderaxespad=0.0,
        ncol=1,
    )
    fig.tight_layout()
    fig.savefig(FIG_DIR / "li2o_solubility_models.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main():
    apply_validation_style()
    plot_diffusivity()
    plot_solubility()


if __name__ == "__main__":
    main()
