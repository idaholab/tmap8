"""
Animate mobile and trapped deuterium concentration profiles over the TDS ramp.

Current Layout (2 x 2):
  [0,0] Mobile  – whole domain (0–200 µm)
  [0,1] Mobile  – near surface (0–1 µm)
  [1,0] Trapped – bulk & near surface (0–7 µm)
  [1,1] Trapped – near surface (0–1 µm)

A temperature-ramp axes sits above the panels; a marker tracks the current frame.
This script is modular, so add and remove panels as traps are changed and added.
"""

import argparse
from pathlib import Path

import matplotlib.animation as animation
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# File paths
SCRIPT_DIR = Path(__file__).resolve().parent
GOLD_DIR = SCRIPT_DIR / "gold"
MOBILE_DIR = GOLD_DIR / "deuterium_mobile_concentration_profile"
TRAPPED_DIR = GOLD_DIR / "deuterium_trapped_concentration_profile"
MOBILE_COL = "mobile"
TRAPPED_COL = "trapped_1"
MAIN_CSV = GOLD_DIR / "val-2l_out.csv"
OUTPUT_FILE = SCRIPT_DIR / "val-2l_profile_animation.gif"

# Animation settings
FRAME_STRIDE = 10
FPS = 4
OUTPUT_DPI = 80
MAX_TIME = 3500.0
FIGURE_SIZE = (9, 6.75)

# Panel definitions
# Each entry: (row, col, species, label, x_min, x_max)
PANELS = [
    (0, 0, "mobile", "Mobile – whole domain", 0.0, 200.0),
    (0, 1, "mobile", "Mobile – near surface", 0.0, 1.0),
    (1, 0, "trapped", "Trapped – bulk & near surface", 0.0, 7.0),
    (1, 1, "trapped", "Trapped – near surface", 0.0, 1.0),
]

COLOR_MOBILE = "steelblue"
COLOR_TRAPPED = "darkorange"
COLOR_TRAP_BOUNDARY = "black"


# Helpers


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


def profile_number(path):
    """Return the output number at the end of a profile CSV filename."""
    return int(path.stem.rsplit("_", maxsplit=1)[-1])


def find_profile_files(directory):
    files = sorted(directory.glob("val-2l_out_*.csv"), key=profile_number)
    if not files:
        raise FileNotFoundError(
            f"No profile CSVs found in '{directory}'.\n"
            "Check that the VectorPostprocessor output block is active in val-2l.i."
        )
    return files


def load_profile_series(files, col_hint, scale=1.0):
    xs, cs = [], []
    col_name = None
    for f in files:
        df = pd.read_csv(f, skipinitialspace=True).sort_values("x")
        if col_name is None:
            col_name = detect_value_column(df, col_hint)
        xs.append(df["x"].values)
        cs.append(df[col_name].values * scale)
    return xs, cs


def select_profile_inputs(all_times, frame_stride, max_time):
    """Return completed-timestep profiles and matching scalar-output rows."""
    mobile_files = find_profile_files(MOBILE_DIR)
    trapped_files = find_profile_files(TRAPPED_DIR)

    mobile_numbers = [profile_number(path) for path in mobile_files]
    trapped_numbers = [profile_number(path) for path in trapped_files]
    if mobile_numbers != trapped_numbers:
        raise ValueError(
            "The mobile and trapped profile directories must contain matching "
            "output numbers."
        )

    invalid_numbers = [
        number for number in mobile_numbers if number < 0 or number >= len(all_times)
    ]
    if invalid_numbers:
        raise ValueError(
            "Profile output numbers do not map to rows in "
            f"'{MAIN_CSV}': {invalid_numbers}."
        )

    # Profile 0000 is the initial state. Completed timesteps begin at 0001,
    # which maps directly to row 1 of the scalar-output arrays.
    available = np.array([number for number in mobile_numbers if number > 0])
    if max_time is not None:
        available = available[all_times[available] <= max_time]
    if not available.size:
        raise ValueError("No profile frames satisfy the requested maximum time.")

    complete_series = np.array_equal(available, np.arange(1, available[-1] + 1))
    if complete_series:
        selected = available[::frame_stride]
        # Always include the last available state at or before max_time.
        if selected[-1] != available[-1]:
            selected = np.append(selected, available[-1])
    else:
        # A sparse gold directory already contains the selected animation frames.
        # Use each available profile instead of applying the stride a second time.
        selected = available

    mobile_by_number = dict(zip(mobile_numbers, mobile_files))
    trapped_by_number = dict(zip(trapped_numbers, trapped_files))
    return (
        [mobile_by_number[number] for number in selected],
        [trapped_by_number[number] for number in selected],
        selected,
        len(all_times) - 1,
    )


def relative_input_paths(mobile_files, trapped_files):
    """Return paths suitable for the TestHarness csvdiff parameter."""
    return [
        MAIN_CSV.name,
        *(str(path.relative_to(GOLD_DIR)) for path in mobile_files),
        *(str(path.relative_to(GOLD_DIR)) for path in trapped_files),
    ]


def global_ylim(c_series, x_series, x_min, x_max, pad=0.08):
    masked = [c[(x >= x_min) & (x <= x_max)] for c, x in zip(c_series, x_series)]
    g_max = max((v.max() for v in masked if v.size), default=0.0)
    return 0.0, max(g_max * (1.0 + pad), 1e-30)


def region_mask(x, x_min, x_max):
    return (x >= x_min) & (x <= x_max)


# Main


def build_animation(
    show=False,
    frame_stride=FRAME_STRIDE,
    fps=FPS,
    dpi=OUTPUT_DPI,
    max_time=MAX_TIME,
    output_file=OUTPUT_FILE,
    list_selected_files=False,
):
    if frame_stride < 1:
        raise ValueError("frame_stride must be at least 1.")
    if fps <= 0:
        raise ValueError("fps must be positive.")
    if dpi <= 0:
        raise ValueError("dpi must be positive.")
    if max_time is not None and max_time < 0:
        raise ValueError("max_time must be nonnegative.")

    # Scalar CSV for time and temperature
    main_df = pd.read_csv(MAIN_CSV)
    required_columns = {"time", "temperature", "trap_per_free", "trap_depth"}
    missing_columns = required_columns.difference(main_df.columns)
    if missing_columns:
        raise KeyError(
            f"Missing required columns in '{MAIN_CSV}': "
            f"{', '.join(sorted(missing_columns))}"
        )

    all_times = main_df["time"].values
    all_temps = main_df["temperature"].values
    trap_per_free = main_df["trap_per_free"].iloc[0]
    trap_boundary = main_df["trap_depth"].iloc[0]

    mobile_files, trapped_files, scalar_rows, total_profiles = select_profile_inputs(
        all_times, frame_stride, max_time
    )
    if list_selected_files:
        print(" ".join(relative_input_paths(mobile_files, trapped_files)))
        return

    # Read only the profiles that will become GIF frames.
    mob_xs, mob_cs = load_profile_series(mobile_files, MOBILE_COL, scale=1.0)
    trp_xs, trp_cs = load_profile_series(
        trapped_files, TRAPPED_COL, scale=trap_per_free
    )
    selected_times = all_times[scalar_rows]
    selected_temps = all_temps[scalar_rows]
    n_frames = len(mob_xs)
    time_limit = "none" if max_time is None else f"{max_time:g} s"
    print(
        f"Using {n_frames} of {total_profiles} completed-timestep profile frames "
        f"(stride={frame_stride}, max_time={time_limit})."
    )

    def frame_metadata(i):
        return selected_times[i], selected_temps[i]

    frame_indices = range(n_frames)

    series = {
        "mobile": (mob_xs, mob_cs, COLOR_MOBILE),
        "trapped": (trp_xs, trp_cs, COLOR_TRAPPED),
    }

    # Figure: temperature ramp on top, 2x2 panels below
    fig = plt.figure(figsize=FIGURE_SIZE)
    # Reserve top 15% for temperature axes, bottom 85% for the 2x2 grid
    temp_ax = fig.add_axes([0.10, 0.88, 0.82, 0.09])
    gs = fig.add_gridspec(
        2, 2, left=0.10, right=0.92, top=0.82, bottom=0.07, hspace=0.45, wspace=0.35
    )
    axes = gs.subplots()

    # Temperature ramp axes
    temperature_mask = np.ones(len(all_times), dtype=bool)
    if max_time is not None:
        temperature_mask = all_times <= max_time
    plotted_times = all_times[temperature_mask]
    plotted_temps = all_temps[temperature_mask]
    temp_ax.plot(plotted_times, plotted_temps, color="firebrick", linewidth=1.5)
    (temp_marker,) = temp_ax.plot(
        selected_times[0],
        selected_temps[0],
        "o",
        color="firebrick",
        markersize=6,
        zorder=5,
    )
    temp_ax.set_xlim(plotted_times[0], plotted_times[-1])
    temp_ax.set_ylim(plotted_temps.min() * 0.95, plotted_temps.max() * 1.05)
    temp_ax.set_xlabel("Time (s)", fontsize=8)
    temp_ax.set_ylabel("T (K)", fontsize=8)
    temp_ax.tick_params(labelsize=7)
    temp_ax.grid(True, linestyle="--", alpha=0.35)
    state_text = temp_ax.text(
        0.99,
        0.08,
        "",
        transform=temp_ax.transAxes,
        ha="right",
        va="bottom",
        fontsize=8,
    )

    # Concentration panels
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

        if xlo <= trap_boundary <= xhi:
            ax.axvline(
                trap_boundary,
                color=COLOR_TRAP_BOUNDARY,
                linestyle=":",
                linewidth=1.1,
                label=f"Trap edge ({trap_boundary} µm)",
            )
            legend_location = "upper left" if xhi == 1.0 else "upper right"
            ax.legend(fontsize=7, loc=legend_location)

    # Animation update
    def update(frame):
        time, temperature = frame_metadata(frame)
        temp_marker.set_data([time], [temperature])
        state_text.set_text(f"t = {time:.0f} s, T = {temperature:.1f} K")

        for row, col, species, _, xlo, xhi in PANELS:
            xs, cs, _ = series[species]
            mask = region_mask(xs[frame], xlo, xhi)
            lines[(row, col)].set_data(xs[frame][mask], cs[frame][mask])

        return list(lines.values()) + [temp_marker, state_text]

    ani = animation.FuncAnimation(
        fig,
        update,
        frames=frame_indices,
        interval=1000 / fps,
        blit=True,
    )

    if show:
        plt.show()
    else:
        output_path = Path(output_file)
        if not output_path.is_absolute():
            output_path = SCRIPT_DIR / output_path
        print(f"Saving animation to {output_path} …")
        ani.save(output_path, writer="pillow", fps=fps, dpi=dpi)
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
    parser.add_argument(
        "--frame-stride",
        type=int,
        default=FRAME_STRIDE,
        help="Include every Nth profile in the animation (default: %(default)s).",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=FPS,
        help="Set the saved or interactive playback rate (default: %(default)s).",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=OUTPUT_DPI,
        help="Set the saved GIF resolution in dots per inch (default: %(default)s).",
    )
    parser.add_argument(
        "--max-time",
        type=float,
        default=MAX_TIME,
        help="Ignore profiles after this time in seconds (default: %(default)s).",
    )
    parser.add_argument(
        "--list-selected-files",
        action="store_true",
        help="Print the files used by the animation and exit without creating a GIF.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=OUTPUT_FILE,
        help="Set the output GIF path (default: %(default)s).",
    )
    args = parser.parse_args()
    build_animation(
        show=args.show,
        frame_stride=args.frame_stride,
        fps=args.fps,
        dpi=args.dpi,
        max_time=args.max_time,
        output_file=args.output,
        list_selected_files=args.list_selected_files,
    )
