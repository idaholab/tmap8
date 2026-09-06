"""
This script animates mobile and trapped deuterium concentration profiles over the TDS ramp.

Current Layout (2 x 2):
  [0,0] Mobile  – whole domain (0–200 µm)
  [0,1] Mobile  – near surface (0–1 µm)
  [1,0] Trapped – bulk & near surface (0–7 µm)
  [1,1] Trapped – near surface (0–1 µm)

A temperature-ramp axes sits above the panels; a marker tracks the current frame.
This script is modular, so add and remove panels as traps are changed and added.
"""

import os
import glob
import argparse
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# ── Trap information from val-2l.i ───────────────────────────────────────────────────── #
trap_per_free = pd.read_csv("val-2l_out.csv")["trap_per_free"].iloc[0]
TRAP_BOUNDARY = pd.read_csv("val-2l_out.csv")["trap_depth"].iloc[0]
FRAME_STRIDE = 25  # Add frame to animation every "FRAME_STRIDE"th timestep


# ── File paths ────────────────────────────────────────────────────────────── #
MOBILE_DIR = "deuterium_mobile_concentration_profile"
TRAPPED_DIR = "deuterium_trapped_concentration_profile"
MOBILE_COL = "mobile"
TRAPPED_COL = "trapped_1"
MAIN_CSV = "val-2l_out.csv"
OUTPUT_FILE = "val-2l_profile_animation.gif"

# ── Panel definitions ─────────────────────────────────────────────────────── #
# Each entry: (row, col, species, label, x_min, x_max)
PANELS = [
    (0, 0, "mobile", "Mobile – whole domain", 0.0, 200.0),
    (0, 1, "mobile", "Mobile – near surface", 0.0, 1.0),
    (1, 0, "trapped", "Trapped – bulk & near surface", 0.0, 7.0),
    (1, 1, "trapped", "Trapped – near surface", 0.0, 1.0),
]

COLOR_MOBILE = "steelblue"
COLOR_TRAPPED = "darkorange"
COLOR_TRAP_BOUNDARY = "dimgray"


# ── Helpers ───────────────────────────────────────────────────────────────── #


def detect_value_column(df, hint):
    cols = list(df.columns)
    if hint in cols:
        return hint
    matches = [c for c in cols if hint in c]
    if matches:
        return matches[0]
    candidates = [c for c in cols if c not in ("x", "id")]
    if candidates:
        print(f"  Warning: '{hint}' not found; using '{candidates[0]}'.")
        return candidates[0]
    raise KeyError(f"Cannot find value column in {cols}; expected '{hint}'.")


def load_profile_series(directory, col_hint, scale=1.0):
    pattern = os.path.join(directory, "val-2l_out_*.csv")
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(
            f"No profile CSVs found in '{directory}'.\n"
            "Check that the VectorPostprocessor output block is active in val-2l.i."
        )
    xs, cs = [], []
    col_name = None
    for f in files:
        df = pd.read_csv(f, skipinitialspace=True).sort_values("x")
        if col_name is None:
            col_name = detect_value_column(df, col_hint)
        xs.append(df["x"].values)
        cs.append(df[col_name].values * scale)
    return xs, cs


def global_ylim(c_series, x_series, x_min, x_max, pad=0.08):
    masked = [c[(x >= x_min) & (x <= x_max)] for c, x in zip(c_series, x_series)]
    g_max = max((v.max() for v in masked if v.size), default=0.0)
    return 0.0, max(g_max * (1.0 + pad), 1e-30)


def region_mask(x, x_min, x_max):
    return (x >= x_min) & (x <= x_max)


# ── Main ──────────────────────────────────────────────────────────────────── #


def build_animation(show=False):
    # ── Scalar CSV for time / temperature ────────────────────────────────── #
    main_df = pd.read_csv(MAIN_CSV)
    all_times = main_df["time"].values
    all_temps = main_df["temperature"].values

    time_offset = 1 if all_times[0] == 0.0 else 0

    def frame_metadata(i):
        row = min(i + time_offset, len(all_times) - 1)
        return all_times[row], all_temps[row]

    # ── Load profile series ───────────────────────────────────────────────── #
    mob_xs, mob_cs = load_profile_series(MOBILE_DIR, MOBILE_COL, scale=1.0)
    trp_xs, trp_cs = load_profile_series(TRAPPED_DIR, TRAPPED_COL, scale=trap_per_free)
    n_frames = min(len(mob_xs), len(trp_xs))
    frame_indices = range(0, n_frames, FRAME_STRIDE)

    series = {
        "mobile": (mob_xs, mob_cs, COLOR_MOBILE),
        "trapped": (trp_xs, trp_cs, COLOR_TRAPPED),
    }

    # ── Figure: temperature ramp on top, 2x2 panels below ────────────────── #
    fig = plt.figure(figsize=(12, 9))
    # Reserve top 15% for temperature axes, bottom 85% for the 2x2 grid
    temp_ax = fig.add_axes([0.10, 0.88, 0.82, 0.09])
    gs = fig.add_gridspec(
        2, 2, left=0.10, right=0.92, top=0.82, bottom=0.07, hspace=0.45, wspace=0.35
    )
    axes = gs.subplots()

    # ── Temperature ramp axes ─────────────────────────────────────────────── #
    temp_ax.plot(all_times, all_temps, color="firebrick", linewidth=1.5)
    (temp_marker,) = temp_ax.plot(
        all_times[0], all_temps[0], "o", color="firebrick", markersize=6, zorder=5
    )
    temp_ax.set_xlim(0, all_times[-1])
    temp_ax.set_ylim(all_temps.min() * 0.95, all_temps.max() * 1.05)
    temp_ax.set_xlabel("Time (s)", fontsize=8)
    temp_ax.set_ylabel("T (K)", fontsize=8)
    temp_ax.tick_params(labelsize=7)
    temp_ax.grid(True, linestyle="--", alpha=0.35)

    # ── Concentration panels ──────────────────────────────────────────────── #
    lines = {}

    for row, col, species, label, xlo, xhi in PANELS:
        xs, cs, color = series[species]
        ax = axes[row, col]

        ylim = global_ylim(cs, xs, xlo, xhi)
        mask = region_mask(xs[0], xlo, xhi)
        (ln,) = ax.plot(xs[0][mask], cs[0][mask], color=color, linewidth=1.6)
        lines[(row, col)] = ln

        ax.set_xlim(xlo, xhi)
        ax.set_ylim(*ylim)
        ax.set_title(label, fontsize=9, pad=4)
        ax.set_xlabel("Position (µm)", fontsize=8)
        ax.set_ylabel("Concentration (at·µm⁻³)", fontsize=8)
        ax.grid(True, linestyle="--", alpha=0.35)
        ax.ticklabel_format(axis="y", style="sci", scilimits=(0, 0))

        if xlo <= TRAP_BOUNDARY <= xhi:
            ax.axvline(
                TRAP_BOUNDARY,
                color=COLOR_TRAP_BOUNDARY,
                linestyle=":",
                linewidth=1.1,
                label=f"Trap edge ({TRAP_BOUNDARY} µm)",
            )
            ax.legend(fontsize=7, loc="upper right")

    # ── Animation update ──────────────────────────────────────────────────── #
    def update(frame):
        t, T = frame_metadata(frame)
        temp_marker.set_data([t], [T])

        for row, col, species, _, xlo, xhi in PANELS:
            xs, cs, _ = series[species]
            mask = region_mask(xs[frame], xlo, xhi)
            lines[(row, col)].set_data(xs[frame][mask], cs[frame][mask])

        return list(lines.values()) + [temp_marker]

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=frame_indices,
        interval=50,
        blit=True,
    )

    if show:
        plt.show()
    else:
        print(f"Saving animation to {OUTPUT_FILE} …")
        ani.save(OUTPUT_FILE, writer="pillow", fps=20, dpi=140)
        print("Done.")

    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Animate mobile and trapped D profiles from val-2l TMAP8 output."
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Preview interactively instead of saving to file.",
    )
    args = parser.parse_args()
    build_animation(show=args.show)
