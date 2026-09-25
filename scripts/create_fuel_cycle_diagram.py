#!/usr/bin/env python3
"""
tmap8_fuelcycle_diagram.py

Reads a TMAP8 (MOOSE) input file, finds every [ScalarKernels] sub-block whose
`type` names a FuelCycleSystemScalarKernel variant -- e.g. the plain
`FuelCycleSystemScalarKernel` or the automatic-differentiation
`ADFuelCycleSystemScalarKernel` (MOOSE's standard "AD" prefix convention for
AD-enabled kernel variants), or any other prefixed variant sharing that base
name -- and draws a block diagram showing how those blocks are wired
together via their `variable` (output) and `inputs` (inputs) parameters.

Portable by design: pure standard library, single self-contained SVG output,
optional Graphviz DOT export.

Layout and routing
-------------------
  - Nodes are placed in left-to-right layers by longest-path from sources.
  - Each node's external-input/other_sources "stub" boxes reserve their own
    horizontal column, baked directly into the layer x-offset calculation.
  - Edges are rendered as orthogonal polyline segments with small FIXED-
    RADIUS rounded corners (max 14px), not length-scaled bezier smoothing.
  - FORWARD edges (dst layer > src layer):
      - Adjacent layers (one gap): a single-elbow router picks a bend x
        that clears every obstacle along both horizontal runs. If no bend
        x works, it falls back to a guaranteed-clear route that leaves the
        node grid entirely via a short perpendicular exit/entry stub and a
        dedicated overflow lane above every box.
      - Multiple layers (several gaps): one waypoint is placed at each
        intervening layer boundary, each choosing its own y to clear
        whatever obstacle spans that specific x -- a single elbow cannot
        clear multiple obstacles at different x's along a long span. If
        the assembled path still clips something, it falls back to the
        same overflow-lane escape used by the single-gap case.
  - BACK edges (feedback/cycle, dst layer <= src layer) are routed as a
    simple orthogonal "staple": straight up from the source's top-face
    port, one flat run in a lane dedicated to that edge (so back edges
    never collide with each other), straight down into the destination's
    top-face port. Both port-facing segments stay perfectly vertical so
    arrowheads always point down into the box, never sideways. If the
    vertical run clips a sibling box that shares the port's own x column,
    the run is nudged sideways via small orthogonal elbows (never a
    diagonal jump).
  - Every port-facing segment (forward or back, normal or fallback) is
    guaranteed perpendicular to the box face it touches.
  - Labels default to sitting directly on their own edge's longest
    straight segment. If that spot is taken by another label, the label
    slides along the SAME line (never toward a different edge) before
    trying the next-longest segment of the same path. A faint leader line
    ties a slid label back to its anchor so ownership is never ambiguous.
  - `--verify` re-checks every edge's final rendered path against every
    node/stub box and reports any residual overlap explicitly.

Usage
-----
    python tmap8_fuelcycle_diagram.py path/to/model.i
    python tmap8_fuelcycle_diagram.py path/to/model.i -o diagram.svg
    python tmap8_fuelcycle_diagram.py path/to/model.i --dot diagram.dot
    python tmap8_fuelcycle_diagram.py path/to/model.i --json blocks.json
    python tmap8_fuelcycle_diagram.py path/to/model.i --list-kernel-types
    python tmap8_fuelcycle_diagram.py path/to/model.i --verify
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# --------------------------------------------------------------------------
# 1. MOOSE input-file tokenizer / block parser
# --------------------------------------------------------------------------

@dataclass
class MooseBlock:
    name: str
    path: Tuple[str, ...]
    params: Dict[str, str] = field(default_factory=dict)
    children: List["MooseBlock"] = field(default_factory=list)
    parent: Optional["MooseBlock"] = None
    line_no: int = 0


def _strip_comment(line: str) -> str:
    in_squote = in_dquote = False
    for i, ch in enumerate(line):
        if ch == "'" and not in_dquote:
            in_squote = not in_squote
        elif ch == '"' and not in_squote:
            in_dquote = not in_dquote
        elif ch == "#" and not in_squote and not in_dquote:
            return line[:i]
    return line


_INCLUDE_RE = re.compile(r"^!include\s+(.+?)\s*$")


def expand_includes(path: Path, _seen: Optional[Tuple[Path, ...]] = None) -> List[str]:
    """Read `path` and recursively expand any `!include <file>` directives,
    returning one flat list of lines with each include replaced in place
    by the (recursively expanded) lines of the referenced file.

    Per MOOSE convention, a relative path in `!include` is resolved
    relative to the directory of the file THAT CONTAINS the directive --
    not the top-level input file and not the current working directory.
    This matters once includes are nested: an included file's own
    `!include` lines must resolve relative to where that included file
    itself lives, so each recursive call re-anchors to `path.parent`.

    `_seen` tracks the chain of files currently being expanded (by
    resolved absolute path) so a cyclic include (A includes B includes A)
    raises a clear error instead of recursing forever.
    """
    resolved = path.resolve()
    _seen = _seen or ()
    if resolved in _seen:
        chain = " -> ".join(str(p) for p in _seen + (resolved,))
        raise ValueError(f"circular !include detected: {chain}")

    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        chain = " -> ".join(str(p) for p in _seen)
        context = f" (included from: {chain})" if _seen else ""
        raise FileNotFoundError(f"!include target not found: {path}{context}")

    out_lines: List[str] = []
    for raw_line in text.splitlines():
        stripped_for_match = _strip_comment(raw_line).strip()
        m = _INCLUDE_RE.match(stripped_for_match)
        if m:
            include_arg = _strip_quotes(m.group(1).strip())
            include_path = path.parent / include_arg
            out_lines.extend(expand_includes(include_path, _seen + (resolved,)))
        else:
            out_lines.append(raw_line)

    return out_lines


def parse_moose_file(text: str) -> MooseBlock:
    root = MooseBlock(name="__root__", path=())
    stack: List[MooseBlock] = [root]

    open_re = re.compile(r"^\[([^\[\]/]+)\]\s*$")
    close_re = re.compile(r"^\[\]\s*$")
    open_dot_re = re.compile(r"^\[\./([^\[\]]+)\]\s*$")
    close_dot_re = re.compile(r"^\[\.\./\]\s*$")

    kv_re = re.compile(r"^([A-Za-z0-9_:]+)\s*=\s*(.+)$")

    for line_no, raw_line in enumerate(text.splitlines(), start=1):
        line = _strip_comment(raw_line).strip()
        if not line:
            continue

        m = open_re.match(line) or open_dot_re.match(line)
        if m:
            name = m.group(1)
            parent = stack[-1]
            block = MooseBlock(
                name=name, path=parent.path + (name,), parent=parent, line_no=line_no
            )
            parent.children.append(block)
            stack.append(block)
            continue

        if close_re.match(line) or close_dot_re.match(line):
            if len(stack) > 1:
                stack.pop()
            continue

        m = kv_re.match(line)
        if m:
            key, value = m.group(1), m.group(2).strip()
            value = _strip_quotes(value)
            stack[-1].params[key] = value
            continue

    return root


def _strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
        return value[1:-1].strip()
    return value


FUEL_CYCLE_KERNEL_BASE_NAME = "FuelCycleSystemScalarKernel"
FUEL_CYCLE_KERNEL_TYPE_PATTERN = re.compile(
    r"^(?:[A-Za-z0-9]*)" + re.escape(FUEL_CYCLE_KERNEL_BASE_NAME) + r"$"
)


def is_fuel_cycle_kernel_type(type_name: Optional[str]) -> bool:
    if not type_name:
        return False
    return bool(FUEL_CYCLE_KERNEL_TYPE_PATTERN.match(type_name))


def find_blocks_by_type(root: MooseBlock, type_name: str) -> List[MooseBlock]:
    found: List[MooseBlock] = []

    def _walk(block: MooseBlock):
        if block.params.get("type") == type_name:
            found.append(block)
        for child in block.children:
            _walk(child)

    _walk(root)
    return found


def find_fuel_cycle_kernel_blocks(root: MooseBlock) -> List[MooseBlock]:
    found: List[MooseBlock] = []

    def _walk(block: MooseBlock):
        if is_fuel_cycle_kernel_type(block.params.get("type")):
            found.append(block)
        for child in block.children:
            _walk(child)

    _walk(root)
    return found


# --------------------------------------------------------------------------
# 2. Build a graph model from the FuelCycleSystemScalarKernel blocks
# --------------------------------------------------------------------------


def split_vector(value: str) -> List[str]:
    if not value:
        return []
    return [tok for tok in re.split(r"[\s,]+", value.strip()) if tok]


@dataclass
class FuelCycleNode:
    block_name: str
    kernel_type: str = ""
    comment: str = ""
    variable: Optional[str] = None
    inputs: List[str] = field(default_factory=list)
    other_sources: List[str] = field(default_factory=list)
    extra_params: Dict[str, str] = field(default_factory=dict)


IGNORED_PARAM_KEYS = {"type", "variable", "inputs", "other_sources", "block"}


def build_fuelcycle_nodes(
    root: MooseBlock, source_lines: List[str]
) -> List[FuelCycleNode]:
    blocks = find_fuel_cycle_kernel_blocks(root)
    nodes: List[FuelCycleNode] = []

    for b in blocks:
        node = FuelCycleNode(block_name=b.name)
        node.kernel_type = b.params.get("type", "")
        node.variable = b.params.get("variable")
        node.inputs = split_vector(b.params.get("inputs", ""))
        node.other_sources = split_vector(b.params.get("other_sources", ""))
        node.extra_params = {
            k: v for k, v in b.params.items() if k not in IGNORED_PARAM_KEYS
        }
        if 0 < b.line_no <= len(source_lines):
            raw = source_lines[b.line_no - 1]
            if "#" in raw:
                node.comment = raw.split("#", 1)[1].strip()
        nodes.append(node)

    return nodes


def build_edges(nodes: List[FuelCycleNode]):
    var_to_block = {n.variable: n.block_name for n in nodes if n.variable}

    edges: List[Tuple[str, str, str]] = []
    external_inputs: Dict[str, List[str]] = {n.block_name: [] for n in nodes}

    for n in nodes:
        for inp in n.inputs:
            src_block = var_to_block.get(inp)
            if src_block and src_block != n.block_name:
                edges.append((src_block, n.block_name, inp))
            else:
                external_inputs[n.block_name].append(inp)
        for src in n.other_sources:
            external_inputs[n.block_name].append(f"{src} (source)")

    return edges, external_inputs


# --------------------------------------------------------------------------
# 3. Layered layout
# --------------------------------------------------------------------------


def compute_layers(
    nodes: List[FuelCycleNode], edges: List[Tuple[str, str, str]]
) -> Dict[str, int]:
    names = [n.block_name for n in nodes]
    preds: Dict[str, List[str]] = {name: [] for name in names}
    for src, dst, _ in edges:
        preds[dst].append(src)

    layer: Dict[str, int] = {}
    in_progress: set = set()

    def _layer_of(name: str, depth: int = 0) -> int:
        if name in layer:
            return layer[name]
        if name in in_progress or depth > len(names) + 2:
            return 0
        in_progress.add(name)
        p = preds.get(name, [])
        result = 0 if not p else 1 + max(_layer_of(pred, depth + 1) for pred in p)
        in_progress.discard(name)
        layer[name] = result
        return result

    for name in names:
        _layer_of(name)

    return layer


def wrap_text(text: str, width: int) -> List[str]:
    if not text:
        return []
    return textwrap.wrap(text, width=width) or [text]


def escape_xml(s: str) -> str:
    return (
        s.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


# --------------------------------------------------------------------------
# 4. Geometry / collision helpers
# --------------------------------------------------------------------------

Rect = Tuple[float, float, float, float]  # (x, y, w, h)


def _rects_overlap(a: Rect, b: Rect, pad: float = 0.0) -> bool:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    ax -= pad
    ay -= pad
    aw += 2 * pad
    ah += 2 * pad
    return not (ax + aw <= bx or bx + bw <= ax or ay + ah <= by or by + bh <= ay)


def _segment_box(x1: float, y1: float, x2: float, y2: float) -> Rect:
    x0, x1_ = min(x1, x2), max(x1, x2)
    y0, y1_ = min(y1, y2), max(y1, y2)
    return (x0, y0, max(x1_ - x0, 1e-6), max(y1_ - y0, 1e-6))


def _path_collides(
    points: List[Tuple[float, float]],
    rects: List[Rect],
    skip: List[Rect],
    pad: float = 5.0,
) -> bool:
    for i in range(len(points) - 1):
        seg = _segment_box(*points[i], *points[i + 1])
        for rect in rects:
            if any(rect is s for s in skip):
                continue
            if _rects_overlap(seg, rect, pad=pad):
                return True
    return False


def _simplify_path(
    points: List[Tuple[float, float]], min_gap: float = 1.5
) -> List[Tuple[float, float]]:
    out: List[Tuple[float, float]] = []
    for p in points:
        if (
            out
            and ((out[-1][0] - p[0]) ** 2 + (out[-1][1] - p[1]) ** 2) ** 0.5 < min_gap
        ):
            continue
        out.append(p)
    return out


def _distribute_points(center: float, n: int, spacing: float) -> List[float]:
    if n <= 1:
        return [center]
    span = spacing * (n - 1)
    start = center - span / 2
    return [start + i * spacing for i in range(n)]


# --------------------------------------------------------------------------
# 5. Bounded-radius rounded-corner path rendering
# --------------------------------------------------------------------------

CORNER_RADIUS = 14.0
DEBUG_ROUTING = False


def waypoints_to_rounded_path(
    points: List[Tuple[float, float]], radius: float = CORNER_RADIUS
) -> str:
    pts = points
    n = len(pts)
    if n < 2:
        return ""
    if n == 2:
        (x0, y0), (x1, y1) = pts
        return f"M {x0:.1f},{y0:.1f} L {x1:.1f},{y1:.1f}"

    MIN_SEG_FOR_ROUNDING = 2.0

    def dist(a, b):
        return ((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2) ** 0.5

    def unit(a, b):
        dd = dist(a, b) or 1.0
        return ((b[0] - a[0]) / dd, (b[1] - a[1]) / dd)

    d = [f"M {pts[0][0]:.1f},{pts[0][1]:.1f}"]
    for i in range(1, n - 1):
        prev_pt = pts[i - 1]
        corner = pts[i]
        next_pt = pts[i + 1]

        seg_in_len = dist(prev_pt, corner)
        seg_out_len = dist(corner, next_pt)
        r = min(radius, seg_in_len / 2.0, seg_out_len / 2.0)

        if (
            seg_in_len < MIN_SEG_FOR_ROUNDING
            or seg_out_len < MIN_SEG_FOR_ROUNDING
            or r < 0.5
        ):
            d.append(f"L {corner[0]:.1f},{corner[1]:.1f}")
            continue

        u_in = unit(prev_pt, corner)
        u_out = unit(corner, next_pt)

        pre_corner = (corner[0] - u_in[0] * r, corner[1] - u_in[1] * r)
        post_corner = (corner[0] + u_out[0] * r, corner[1] + u_out[1] * r)

        d.append(f"L {pre_corner[0]:.1f},{pre_corner[1]:.1f}")
        d.append(
            f"Q {corner[0]:.1f},{corner[1]:.1f} {post_corner[0]:.1f},{post_corner[1]:.1f}"
        )

    last = pts[-1]
    d.append(f"L {last[0]:.1f},{last[1]:.1f}")
    return " ".join(d)


def verify_path_clear(
    points: List[Tuple[float, float]],
    all_rects: List[Rect],
    skip: List[Rect],
    pad: float = 2.0,
) -> List[Rect]:
    hits: List[Rect] = []
    for i in range(len(points) - 1):
        seg = _segment_box(*points[i], *points[i + 1])
        for rect in all_rects:
            if any(rect is s for s in skip):
                continue
            if _rects_overlap(seg, rect, pad=pad) and rect not in hits:
                hits.append(rect)
    return hits


# --------------------------------------------------------------------------
# 6. Edge routing
# --------------------------------------------------------------------------


def _route_single_elbow(
    start: Tuple[float, float],
    end: Tuple[float, float],
    all_rects: List[Rect],
    skip: List[Rect],
    reserved_x: List[float],
    lane_clearance: float,
    claimed_overflow_lanes: Optional[List[float]] = None,
    preferred_x: Optional[float] = None,
) -> Tuple[List[Tuple[float, float]], Optional[float]]:
    """Single-elbow router for FORWARD edges between ADJACENT layers only
    (one gap). Both port-facing segments stay horizontal (perpendicular to
    the box's left/right face).

    If `preferred_x` is given (a deterministic bend x pre-assigned by the
    caller based on this edge's port index at its source/destination box,
    guaranteeing distinctness from sibling edges without relying on
    search), it is tried FIRST, before the general sampling search below.
    This is what actually guarantees separation for edges sharing a
    source or destination port column -- a search that merely *prefers*
    an unclaimed x can still, for certain port-count/gap-width
    combinations, have every edge's search converge on the same nearest
    valid candidate. A pre-assigned distinct value sidesteps that.

    Otherwise, tries a range of bend x's, at each trying height variants
    for both horizontal runs, to clear every obstacle, preferring a bend x
    that is at least `lane_clearance` away from every x already listed in
    `reserved_x`. If nothing clears, falls back to a guaranteed-clear
    overflow-lane route that leaves the grid via a short perpendicular
    exit/entry stub, claiming a distinct lane so it doesn't stack on other
    overflow-routed edges.
    """
    sx, sy = start
    ex, ey = end

    def obstacles_on_horizontal_run(y: float, x0: float, x1: float) -> List[Rect]:
        lo, hi = min(x0, x1), max(x0, x1)
        hits = []
        for rect in all_rects:
            if any(rect is s for s in skip):
                continue
            rx, ry, rw, rh = rect
            if (
                ry - CORNER_RADIUS <= y <= ry + rh + CORNER_RADIUS
                and rx < hi
                and rx + rw > lo
            ):
                hits.append(rect)
        return hits

    def try_bend_x(mid_x: float) -> Optional[List[Tuple[float, float]]]:
        start_run_hits = obstacles_on_horizontal_run(sy, sx, mid_x)
        end_run_hits = obstacles_on_horizontal_run(ey, mid_x, ex)

        y_start_variants = [sy]
        for rect in start_run_hits:
            rx, ry, rw, rh = rect
            y_start_variants.append(ry - CORNER_RADIUS - 4)
            y_start_variants.append(ry + rh + CORNER_RADIUS + 4)
        y_end_variants = [ey]
        for rect in end_run_hits:
            rx, ry, rw, rh = rect
            y_end_variants.append(ry - CORNER_RADIUS - 4)
            y_end_variants.append(ry + rh + CORNER_RADIUS + 4)

        for y_s in y_start_variants:
            for y_e in y_end_variants:
                if y_s == sy and y_e == ey:
                    wp = _simplify_path([start, (mid_x, sy), (mid_x, ey), end])
                else:
                    wp = _simplify_path(
                        [
                            start,
                            (mid_x, sy),
                            (mid_x, y_s),
                            (mid_x, y_e),
                            (mid_x, ey),
                            end,
                        ]
                    )
                if len(wp) <= 2:
                    continue
                if _path_collides(wp, all_rects, skip, pad=CORNER_RADIUS):
                    continue
                return wp
        return None

    if preferred_x is not None:
        wp = try_bend_x(preferred_x)
        if wp is not None:
            return wp, preferred_x

    if abs(sy - ey) < 1e-6 and not any(
        abs(sx + (ex - sx) / 2 - rx) < lane_clearance for rx in reserved_x
    ):
        wp = [start, end]
        if not _path_collides(wp, all_rects, skip, pad=CORNER_RADIUS):
            return wp, None

    gap_left, gap_right = sx, ex
    if gap_right <= gap_left:
        gap_right = gap_left + 40
    mid_x_natural = (gap_left + gap_right) / 2

    # Sample MANY more candidate bend x's than before (was 11 fixed steps)
    # so that even in a tightly packed layer gap there's a good chance of
    # finding a bend x that's both box-clear AND far from every reserved
    # x. More samples cost little (routing runs once per edge at build
    # time) and meaningfully reduce how often two edges are forced onto
    # the same bend column.
    steps = 41
    xs = [mid_x_natural] + [
        gap_left + (i / (steps + 1)) * (gap_right - gap_left)
        for i in range(1, steps + 1)
    ]

    # Also probe a bit OUTSIDE the [gap_left, gap_right] span itself, since
    # two edges sharing the same source box edge (same gap_left) or the
    # same destination box edge (same gap_right) can have natural elbow
    # regions that coincide almost entirely -- there may be no interior
    # x that's both box-clear and far enough from a reservation, but a
    # bend slightly beyond the gap's own span can still work.
    span = max(gap_right - gap_left, 1.0)
    xs += [gap_left - span * f for f in (0.15, 0.3, 0.45)]
    xs += [gap_right + span * f for f in (0.15, 0.3, 0.45)]

    lane_clear_hits: List[Tuple[float, List[Tuple[float, float]], float]] = []
    any_clear_hits: List[Tuple[float, List[Tuple[float, float]], float]] = []
    seen = set()

    for mid_x in xs:
        key = round(mid_x, 3)
        if key in seen:
            continue
        seen.add(key)

        found_for_this_x = try_bend_x(mid_x)
        if not found_for_this_x:
            continue

        dist = abs(mid_x - mid_x_natural)
        any_clear_hits.append((dist, found_for_this_x, mid_x))
        if not any(abs(mid_x - rx) < lane_clearance for rx in reserved_x):
            lane_clear_hits.append((dist, found_for_this_x, mid_x))

    if lane_clear_hits:
        lane_clear_hits.sort(key=lambda t: t[0])
        _, wp, mid_x = lane_clear_hits[0]
        return wp, mid_x

    # No candidate was BOTH box-clear AND far from every reservation. Do
    # NOT silently fall back to "any box-clear x" here -- that was the bug
    # that let two edges sharing a source/destination box both collapse
    # onto the same natural bend x (the reservation was computed but then
    # ignored the moment it couldn't be perfectly satisfied). Instead,
    # relax the REQUIRED clearance in stages, still preferring the least
    # crowded available x over simply taking whatever is closest to
    # natural, so two edges are still pushed apart even if not by the
    # full lane_clearance.
    if any_clear_hits:

        def min_dist_to_reserved(mid_x: float) -> float:
            if not reserved_x:
                return float("inf")
            return min(abs(mid_x - rx) for rx in reserved_x)

        any_clear_hits.sort(key=lambda t: (-min_dist_to_reserved(t[2]), t[0]))
        _, wp, mid_x = any_clear_hits[0]
        return wp, mid_x

    # No bend x cleared everything. Leave the grid: a short perpendicular
    # stub away from each box, then an overflow lane above every box,
    # claiming a distinct lane height from other overflow-routed edges.
    wp, lane_y_used = _overflow_lane_route(
        start, end, all_rects, skip, claimed_overflow_lanes
    )
    if claimed_overflow_lanes is not None:
        claimed_overflow_lanes.append(lane_y_used)
    return wp, None


def _overflow_lane_route(
    start: Tuple[float, float],
    end: Tuple[float, float],
    all_rects: List[Rect],
    skip: List[Rect],
    claimed_overflow_lanes: Optional[List[float]] = None,
) -> Tuple[List[Tuple[float, float]], float]:
    """Guaranteed-clear fallback for a horizontally-facing edge: exit the
    source box horizontally (perpendicular to its right face), travel in
    a lane above every box in the diagram, then enter the destination box
    horizontally (perpendicular to its left face).

    `claimed_overflow_lanes` holds the y-values every PRIOR overflow-routed
    edge already used. Without tracking this, every edge that falls back
    to this route independently starts its search from the same
    `top_of_grid` height and -- since that first candidate is usually
    already clear of every BOX (the only thing `_path_collides` checks) --
    multiple unrelated edges all land on the identical y and run stacked
    on top of each other for their entire horizontal span, even though no
    box overlap is ever reported. This function now also skips any y
    within one lane-height of an already-claimed lane, so each overflow
    edge gets its own horizontal band. Returns (waypoints, lane_y_used) so
    the caller can add it to `claimed_overflow_lanes`.
    """
    sx, sy = start
    ex, ey = end
    stub_len = 24.0
    exit_x = sx + stub_len
    entry_x = ex - stub_len
    top_of_grid = min((r[1] for r in all_rects), default=min(sy, ey)) - 30
    step = 16.0
    claimed = claimed_overflow_lanes or []

    def build(ly: float) -> List[Tuple[float, float]]:
        return _simplify_path(
            [start, (exit_x, sy), (exit_x, ly), (entry_x, ly), (entry_x, ey), end]
        )

    def far_enough_from_claimed(ly: float) -> bool:
        return all(abs(ly - c) >= step - 1e-6 for c in claimed)

    # First pass: require both box-clearance AND distance from every
    # already-claimed overflow lane.
    lane_y = top_of_grid
    for _ in range(200):
        if far_enough_from_claimed(lane_y):
            wp = build(lane_y)
            if not _path_collides(wp, all_rects, skip, pad=CORNER_RADIUS):
                return wp, lane_y
        lane_y -= step

    # Relaxed pass: box-clearance only (matches old behavior), in case the
    # diagram is dense enough that no fully-unclaimed lane exists within
    # a reasonable search range.
    lane_y = top_of_grid
    for _ in range(80):
        wp = build(lane_y)
        if not _path_collides(wp, all_rects, skip, pad=CORNER_RADIUS):
            return wp, lane_y
        lane_y -= step
    return build(lane_y), lane_y


def route_forward_waypoints(
    start: Tuple[float, float],
    end: Tuple[float, float],
    all_rects: List[Rect],
    skip: List[Rect],
    reserved_by_boundary: Optional[Dict[int, List[float]]] = None,
    layer_gap_xs: Optional[List[float]] = None,
    claimed_overflow_lanes: Optional[List[float]] = None,
    global_reserved_x: Optional[List[float]] = None,
    exit_stub_x: Optional[float] = None,
    entry_stub_x: Optional[float] = None,
) -> Tuple[List[Tuple[float, float]], List[Tuple[int, float]]]:
    """Route a FORWARD edge (dst layer > src layer). Single-gap edges
    delegate to `_route_single_elbow`. Multi-gap edges get one waypoint
    per intervening layer boundary (each boundary choosing its own y to
    clear whatever obstacle spans that x), falling back to the same
    overflow-lane escape as the single-gap case if the assembled path
    still clips something.

    `exit_stub_x` / `entry_stub_x`, when provided, are DETERMINISTIC bend
    x's assigned by the caller ahead of time (based on this edge's port
    index among all edges sharing the same source/destination box), used
    as the very first / last bend point instead of deriving one from
    `sx`/`ex` via search. This guarantees distinctness for edges sharing a
    source or destination port column without relying on a collision
    search to happen to discover different values -- the search-based
    approach was found to still let multiple edges from the same source
    converge on the same x in some port-count/layer-span combinations.

    `global_reserved_x` is still consulted for the INTERIOR layer-boundary
    waypoints of multi-gap edges (which aren't pre-assigned), and by
    `_route_single_elbow`'s own bend-x search for single-gap edges.
    `claimed_overflow_lanes` is shared across all edges in the diagram so
    several unrelated edges falling back to the overflow lane land on
    distinct horizontal bands instead of stacking.

    Returns (waypoints, claims) where claims is a list of
    (boundary_index, y) pairs this edge occupies at each boundary it
    crosses, used by the caller only for bookkeeping/debugging.
    """
    reserved_by_boundary = reserved_by_boundary or {}
    layer_gap_xs = layer_gap_xs or []
    global_reserved_x = global_reserved_x if global_reserved_x is not None else []
    LANE_CLEARANCE = 16.0

    sx, sy = start
    ex, ey = end

    def boundary_index_for_x(x: float) -> Optional[int]:
        if not layer_gap_xs:
            return None
        best_i, best_d = None, None
        for i, bx in enumerate(layer_gap_xs):
            dd = abs(bx - x)
            if best_d is None or dd < best_d:
                best_i, best_d = i, dd
        return best_i

    boundary_idxs_crossed = [i for i, x in enumerate(layer_gap_xs) if sx < x < ex]

    if not boundary_idxs_crossed:
        bidx = boundary_index_for_x((sx + ex) / 2.0)
        reserved_here = list(reserved_by_boundary.get(bidx, [])) + list(
            global_reserved_x
        )
        if exit_stub_x is not None:
            reserved_here = [rx for rx in reserved_here if abs(rx - exit_stub_x) > 1e-6]
        wp, claimed_x = _route_single_elbow(
            start,
            end,
            all_rects,
            skip,
            reserved_here,
            LANE_CLEARANCE,
            claimed_overflow_lanes=claimed_overflow_lanes,
            preferred_x=exit_stub_x,
        )
        if claimed_x is not None:
            global_reserved_x.append(claimed_x)
        claims = (
            [(bidx, claimed_x)] if (bidx is not None and claimed_x is not None) else []
        )
        return wp, claims

    def rects_spanning_x(x: float) -> List[Rect]:
        hits = []
        for rect in all_rects:
            if any(rect is s for s in skip):
                continue
            rx, ry, rw, rh = rect
            if rx - 2 <= x <= rx + rw + 2:
                hits.append(rect)
        return hits

    claims: List[Tuple[int, float]] = []
    all_ys: List[float] = [sy]
    for bidx in boundary_idxs_crossed:
        bx = layer_gap_xs[bidx]
        frac = (bx - sx) / (ex - sx) if ex != sx else 0.5
        natural_y = sy + (ey - sy) * frac
        blockers = rects_spanning_x(bx)

        if not blockers:
            all_ys.append(natural_y)
            claims.append((bidx, natural_y))
            continue

        candidates = [natural_y]
        for rect in blockers:
            rx, ry, rw, rh = rect
            candidates.append(ry - CORNER_RADIUS - 4)
            candidates.append(ry + rh + CORNER_RADIUS + 4)

        def clears_obstacles(c: float) -> bool:
            return all(
                not (r[1] - CORNER_RADIUS <= c <= r[1] + r[3] + CORNER_RADIUS)
                for r in blockers
            )

        chosen = natural_y
        for c in sorted(candidates, key=lambda v: abs(v - natural_y)):
            if clears_obstacles(c):
                chosen = c
                break

        all_ys.append(chosen)
        claims.append((bidx, chosen))
    all_ys.append(ey)

    all_xs = [sx] + [layer_gap_xs[i] for i in boundary_idxs_crossed] + [ex]

    # Exit/entry stub x's are now assigned DETERMINISTICALLY by the caller
    # (one distinct value per port index at the source/destination box),
    # passed in as `exit_stub_x`/`entry_stub_x`. Fall back to a search-
    # based pick only if the caller didn't provide one (e.g. direct calls
    # from tests or the stub-edge renderer).
    if exit_stub_x is None:
        exit_stub_x = sx + 24.0
        if any(abs(exit_stub_x - rx) < LANE_CLEARANCE for rx in global_reserved_x):
            for k in range(1, 40):
                cand = exit_stub_x + LANE_CLEARANCE * k
                if not any(abs(cand - rx) < LANE_CLEARANCE for rx in global_reserved_x):
                    exit_stub_x = cand
                    break
    if entry_stub_x is None:
        entry_stub_x = ex - 24.0
        if any(abs(entry_stub_x - rx) < LANE_CLEARANCE for rx in global_reserved_x):
            for k in range(1, 40):
                cand = entry_stub_x - LANE_CLEARANCE * k
                if not any(abs(cand - rx) < LANE_CLEARANCE for rx in global_reserved_x):
                    entry_stub_x = cand
                    break

    # Nudge each intervening boundary's x slightly if it's within
    # LANE_CLEARANCE of an x already claimed by a prior edge's vertical
    # leg, so two multi-gap edges (or a multi-gap and a single-gap edge)
    # sharing a boundary don't run their vertical segments on top of each
    # other. Only the INTERIOR boundary x's are adjustable -- the first
    # and last entries are the edge's own fixed port x's.
    adjusted_xs = list(all_xs)
    for i in range(1, len(adjusted_xs) - 1):
        base_x = adjusted_xs[i]
        if not any(abs(base_x - rx) < LANE_CLEARANCE for rx in global_reserved_x):
            continue
        for k in range(1, 20):
            for sign in (1, -1):
                cand = base_x + sign * LANE_CLEARANCE * k
                if not any(abs(cand - rx) < LANE_CLEARANCE for rx in global_reserved_x):
                    adjusted_xs[i] = cand
                    break
            else:
                continue
            break

    # Build the path with explicit exit/entry stubs as the first and last
    # bend points -- a short horizontal run from the port to the stub x
    # (perpendicular exit, matching every other router in this file),
    # THEN the vertical run at the (now-distinct) stub x, THEN the
    # regular boundary-to-boundary stair-steps, THEN the mirrored entry.
    waypoints: List[Tuple[float, float]] = [start, (exit_stub_x, sy)]
    for i in range(1, len(adjusted_xs) - 1):
        waypoints.append((adjusted_xs[i], all_ys[i]))
    waypoints.append((entry_stub_x, ey))
    waypoints.append(end)

    stair: List[Tuple[float, float]] = [waypoints[0]]
    for i in range(1, len(waypoints)):
        px, py = stair[-1]
        nx, ny = waypoints[i]
        if abs(py - ny) > 1e-6:
            stair.append((px, ny))
        stair.append((nx, ny))
    wp = _simplify_path(stair)

    if not _path_collides(wp, all_rects, skip, pad=CORNER_RADIUS):
        global_reserved_x.append(exit_stub_x)
        global_reserved_x.append(entry_stub_x)
        for i in range(1, len(adjusted_xs) - 1):
            global_reserved_x.append(adjusted_xs[i])
        return wp, claims

    # The per-boundary local placement can't see obstacles that sit
    # strictly between two boundaries, nor obstacles that only one other
    # boundary's y choice needed to dodge. Rather than iterate blindly,
    # fall back to the overflow-lane route, which is geometrically
    # guaranteed clear regardless of how many boxes sit along the span,
    # and claims its own distinct lane so it doesn't stack on other
    # overflow-routed edges.
    wp2, lane_y_used = _overflow_lane_route(
        start, end, all_rects, skip, claimed_overflow_lanes
    )
    if claimed_overflow_lanes is not None:
        claimed_overflow_lanes.append(lane_y_used)
    bidx0 = boundary_idxs_crossed[0]
    claims2 = [(bidx0, None)]
    return wp2, claims2


def route_back_waypoints(
    src_rect: Rect,
    dst_rect: Rect,
    src_port_x: float,
    dst_port_x: float,
    lane_y: float,
    all_rects: List[Rect],
    skip: List[Rect],
    global_reserved_x: Optional[List[float]] = None,
) -> List[Tuple[float, float]]:
    """Route a back/feedback edge as an orthogonal "staple": straight up
    from the source's top-face port, one flat run in this edge's own
    dedicated lane (the caller assigns each back edge a distinct lane, so
    back edges never collide with EACH OTHER vertically-adjacent-wise),
    straight down into the destination's top-face port. Both port-facing
    segments stay perfectly vertical so the arrowhead always points down
    into the box.

    Two different back edges can still end up with vertical legs at (or
    very near) the same x even though their lanes differ, since each
    edge's own port x is independent of every other edge's. `global_reserved_x`
    -- shared with the forward-edge router -- lets this function also
    avoid landing a vertical leg on top of an x some other edge (forward
    OR back) already used, in addition to the existing box-collision
    nudge.
    """
    sx, sy, sw, sh = src_rect
    dx, dy, dw, dh = dst_rect

    start = (src_port_x, sy)
    end = (dst_port_x, dy)
    global_reserved_x = global_reserved_x if global_reserved_x is not None else []
    LANE_CLEARANCE = 16.0

    def build(src_x: float, dst_x: float) -> List[Tuple[float, float]]:
        pts = [start]
        if abs(src_x - src_port_x) > 1e-6:
            elbow_y = sy - 10
            pts.append((src_port_x, elbow_y))
            pts.append((src_x, elbow_y))
        pts.append((src_x, lane_y))
        pts.append((dst_x, lane_y))
        if abs(dst_x - dst_port_x) > 1e-6:
            elbow_y2 = dy - 10
            pts.append((dst_x, elbow_y2))
            pts.append((dst_port_x, elbow_y2))
        pts.append(end)
        return _simplify_path(pts)

    def clear_of_reserved(src_x: float, dst_x: float) -> bool:
        return not any(
            abs(src_x - rx) < LANE_CLEARANCE for rx in global_reserved_x
        ) and not any(abs(dst_x - rx) < LANE_CLEARANCE for rx in global_reserved_x)

    step = 16.0
    max_k = 24

    def offsets():
        yield 0.0
        for k in range(1, max_k):
            yield step * k
            yield -step * k

    # First pass: require both box-clearance AND distance from every
    # x already used by another edge's vertical leg (forward or back).
    for src_off in offsets():
        for dst_off in offsets():
            src_x, dst_x = src_port_x + src_off, dst_port_x + dst_off
            if not clear_of_reserved(src_x, dst_x):
                continue
            cand = build(src_x, dst_x)
            if not _path_collides(cand, all_rects, skip, pad=CORNER_RADIUS):
                global_reserved_x.append(src_x)
                global_reserved_x.append(dst_x)
                return cand

    # Relaxed pass: box-clearance only, same as before, in case no fully
    # unclaimed x exists within a reasonable search range.
    wp = build(src_port_x, dst_port_x)
    if not _path_collides(wp, all_rects, skip, pad=CORNER_RADIUS):
        global_reserved_x.append(src_port_x)
        global_reserved_x.append(dst_port_x)
        return wp

    for off in offsets():
        cand = build(src_port_x + off, dst_port_x)
        if not _path_collides(cand, all_rects, skip, pad=CORNER_RADIUS):
            global_reserved_x.append(src_port_x + off)
            global_reserved_x.append(dst_port_x)
            return cand
    for off in offsets():
        cand = build(src_port_x, dst_port_x + off)
        if not _path_collides(cand, all_rects, skip, pad=CORNER_RADIUS):
            global_reserved_x.append(src_port_x)
            global_reserved_x.append(dst_port_x + off)
            return cand
    for off1 in offsets():
        for off2 in offsets():
            cand = build(src_port_x + off1, dst_port_x + off2)
            if not _path_collides(cand, all_rects, skip, pad=CORNER_RADIUS):
                global_reserved_x.append(src_port_x + off1)
                global_reserved_x.append(dst_port_x + off2)
                return cand

    return wp


# --------------------------------------------------------------------------
# 7. Label placement
# --------------------------------------------------------------------------


def _segment_lengths(
    path: List[Tuple[float, float]],
) -> List[Tuple[float, Tuple[float, float], Tuple[float, float]]]:
    """Every segment of `path`, longest-first, as (length, midpoint, unit_dir)."""
    out = []
    for i in range(len(path) - 1):
        x1, y1 = path[i]
        x2, y2 = path[i + 1]
        L = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        if L < 1e-6:
            continue
        mid = ((x1 + x2) / 2.0, (y1 + y2) / 2.0)
        unit = ((x2 - x1) / L, (y2 - y1) / L)
        out.append((L, mid, unit))
    out.sort(key=lambda t: t[0], reverse=True)
    return out


def _label_rect_at(cx: float, cy: float, text: str) -> Rect:
    w = len(text) * 6.6 + 8
    h = 16
    return (cx - w / 2, cy - h / 2, w, h)


def place_label(
    path: List[Tuple[float, float]],
    text: str,
    placed_label_rects: List[Rect],
) -> Tuple[float, float, float, float]:
    """Pick a label position for `text` along `path`. Defaults to the
    midpoint of the longest straight segment. If that spot is already
    occupied by another label, slides ALONG the same segment (never
    perpendicular, never toward a different edge). If the whole segment
    is exhausted, tries the next-longest segment of the SAME path.
    Returns (label_x, label_y, anchor_x, anchor_y) -- the anchor is the
    segment midpoint before sliding, used to draw a leader line back to
    it if the final position moved away from it.
    """
    segs = _segment_lengths(path)
    if not segs:
        p = path[0] if path else (0.0, 0.0)
        return p[0], p[1], p[0], p[1]

    for seg_len, (mx, my), (ux, uy) in segs:
        max_slide = max(seg_len / 2 - 8, 0)
        for k in range(0, 10):
            slide = min(k * 14.0, max_slide)
            for sign in (1, -1) if k > 0 else (1,):
                cx = mx + ux * slide * sign
                cy = my + uy * slide * sign
                cand_rect = _label_rect_at(cx, cy, text)
                if not any(
                    _rects_overlap(cand_rect, r, pad=2.0) for r in placed_label_rects
                ):
                    return cx, cy, mx, my

    # Every segment crowded: place at the longest segment's midpoint anyway.
    _, (mx, my), _ = segs[0]
    return mx, my, mx, my


# --------------------------------------------------------------------------
# 8. SVG rendering
# --------------------------------------------------------------------------


def render_svg(
    nodes: List[FuelCycleNode],
    edges: List[Tuple[str, str, str]],
    external_inputs: Dict[str, List[str]],
    title: str = "TMAP8 FuelCycleSystemScalarKernel Diagram",
    verify: bool = False,
) -> Tuple[str, List[str]]:
    if not nodes:
        return _empty_svg(title), []

    layers = compute_layers(nodes, edges)
    by_layer: Dict[int, List[FuelCycleNode]] = {}
    for n in nodes:
        by_layer.setdefault(layers[n.block_name], []).append(n)

    BOX_W = 260
    BOX_MIN_H = 90
    LINE_H = 15
    LAYER_GAP_X_BASE = 170
    NODE_GAP_Y = 50
    MARGIN = 60
    STUB_W = 150
    STUB_H = 30
    STUB_GUTTER = 50
    PORT_SPACING = 16
    BACK_LANE_HEIGHT = 22
    BACK_LANE_TOP_GAP = 40

    def node_lines(n: FuelCycleNode) -> List[str]:
        lines = []
        if n.comment:
            lines.append(f"\u201c{n.comment}\u201d")
        if n.kernel_type and n.kernel_type != FUEL_CYCLE_KERNEL_BASE_NAME:
            lines.append(f"type: {n.kernel_type}")
        if n.variable:
            lines.append(f"variable: {n.variable}")
        if n.extra_params:
            for k, v in list(n.extra_params.items())[:4]:
                lines.append(f"{k} = {v}")
            if len(n.extra_params) > 4:
                lines.append(f"... +{len(n.extra_params) - 4} more param(s)")
        return lines

    node_content: Dict[str, List[str]] = {}
    node_height: Dict[str, int] = {}
    for n in nodes:
        lines: List[str] = []
        for raw in node_lines(n):
            lines.extend(wrap_text(raw, 34))
        node_content[n.block_name] = lines
        node_height[n.block_name] = max(BOX_MIN_H, 34 + LINE_H * len(lines))

    max_layer = max(layers.values()) if layers else 0
    layer_stub_width: Dict[int, float] = {L: 0.0 for L in range(max_layer + 1)}
    for n in nodes:
        stubs = external_inputs.get(n.block_name, [])
        if stubs:
            L = layers[n.block_name]
            layer_stub_width[L] = max(layer_stub_width[L], STUB_W + STUB_GUTTER)

    layer_x: Dict[int, float] = {}
    cursor = MARGIN + layer_stub_width.get(0, 0.0)
    layer_x[0] = cursor
    for L in range(1, max_layer + 1):
        cursor += BOX_W + LAYER_GAP_X_BASE + layer_stub_width.get(L, 0.0)
        layer_x[L] = cursor

    def is_back_edge(src: str, dst: str) -> bool:
        return layers[dst] <= layers[src]

    back_edge_list = [
        (src, dst, var) for src, dst, var in edges if is_back_edge(src, dst)
    ]
    n_back_edges = len(back_edge_list)
    back_lanes_height = (
        (BACK_LANE_TOP_GAP + n_back_edges * BACK_LANE_HEIGHT) if n_back_edges else 0.0
    )
    TOP_MARGIN = MARGIN + back_lanes_height

    positions: Dict[str, Tuple[float, float]] = {}
    for L, layer_nodes in by_layer.items():
        y = TOP_MARGIN
        for n in layer_nodes:
            positions[n.block_name] = (layer_x[L], y)
            y += node_height[n.block_name] + NODE_GAP_Y

    stub_positions: Dict[Tuple[str, int], Tuple[float, float]] = {}
    for n in nodes:
        stubs = external_inputs.get(n.block_name, [])
        if not stubs:
            continue
        bx, by_ = positions[n.block_name]
        stub_x = bx - STUB_GUTTER - STUB_W
        node_h = node_height[n.block_name]
        total_stub_h = len(stubs) * STUB_H + (len(stubs) - 1) * 12
        start_y = by_ + node_h / 2 - total_stub_h / 2
        for i, _ in enumerate(stubs):
            stub_positions[(n.block_name, i)] = (stub_x, start_y + i * (STUB_H + 12))

    total_width = max(layer_x.values()) + BOX_W + MARGIN if layer_x else 400
    tallest_layer_height = 0
    for L, layer_nodes in by_layer.items():
        h = sum(node_height[n.block_name] + NODE_GAP_Y for n in layer_nodes)
        tallest_layer_height = max(tallest_layer_height, h)

    total_height = TOP_MARGIN + tallest_layer_height + MARGIN

    node_rects: Dict[str, Rect] = {}
    for n in nodes:
        x, y = positions[n.block_name]
        node_rects[n.block_name] = (x, y, BOX_W, node_height[n.block_name])

    stub_rects: Dict[Tuple[str, int], Rect] = {}
    for key, (sx, sy) in stub_positions.items():
        stub_rects[key] = (sx, sy, STUB_W, STUB_H)

    all_rects: List[Rect] = list(node_rects.values()) + list(stub_rects.values())

    lowest_y = max((r[1] + r[3] for r in all_rects), default=total_height)
    total_height = max(total_height, lowest_y + 80)

    layer_gap_xs: List[float] = []
    for L in range(max_layer):
        right_edge_of_L = layer_x[L] + BOX_W
        left_edge_of_next = layer_x[L + 1]
        layer_gap_xs.append((right_edge_of_L + left_edge_of_next) / 2)

    forward_edges = [
        (i, e) for i, e in enumerate(edges) if not is_back_edge(e[0], e[1])
    ]
    back_edges = [(i, e) for i, e in enumerate(edges) if is_back_edge(e[0], e[1])]

    fwd_outgoing: Dict[str, List[int]] = {}
    fwd_incoming: Dict[str, List[int]] = {}
    back_outgoing: Dict[str, List[int]] = {}
    back_incoming: Dict[str, List[int]] = {}
    for idx, (src, dst, _var) in forward_edges:
        fwd_outgoing.setdefault(src, []).append(idx)
        fwd_incoming.setdefault(dst, []).append(idx)
    for idx, (src, dst, _var) in back_edges:
        back_outgoing.setdefault(src, []).append(idx)
        back_incoming.setdefault(dst, []).append(idx)

    out_port_y: Dict[int, float] = {}
    in_port_y: Dict[int, float] = {}
    for block_name, idxs in fwd_outgoing.items():
        rect = node_rects[block_name]
        center = rect[1] + rect[3] / 2
        for idx, y in zip(
            sorted(idxs), _distribute_points(center, len(idxs), PORT_SPACING)
        ):
            out_port_y[idx] = y
    for block_name, idxs in fwd_incoming.items():
        rect = node_rects[block_name]
        center = rect[1] + rect[3] / 2
        for idx, y in zip(
            sorted(idxs), _distribute_points(center, len(idxs), PORT_SPACING)
        ):
            in_port_y[idx] = y

    out_port_x: Dict[int, float] = {}
    in_port_x: Dict[int, float] = {}
    for block_name, idxs in back_outgoing.items():
        rect = node_rects[block_name]
        center = rect[0] + rect[2] / 2
        for idx, x in zip(
            sorted(idxs), _distribute_points(center, len(idxs), PORT_SPACING)
        ):
            out_port_x[idx] = x
    for block_name, idxs in back_incoming.items():
        rect = node_rects[block_name]
        center = rect[0] + rect[2] / 2
        for idx, x in zip(
            sorted(idxs), _distribute_points(center, len(idxs), PORT_SPACING)
        ):
            in_port_x[idx] = x

    out_port_x_stub: Dict[int, float] = {}
    in_port_x_stub: Dict[int, float] = {}
    STUB_FAN = 20.0

    # Group by the SOURCE COLUMN (rect right-edge x), not just by source
    # node. Multiple different nodes sitting in the same layer (e.g. I2,
    # I6, I8 all in layer 1) share an identical right-edge x, so edges
    # leaving DIFFERENT nodes can still need staggering against each
    # other, not just edges leaving the SAME node.
    out_by_column: Dict[float, List[int]] = {}
    for block_name, idxs in fwd_outgoing.items():
        rect = node_rects[block_name]
        col_x = round(rect[0] + rect[2], 1)
        bucket = out_by_column.setdefault(col_x, [])
        for i in idxs:
            if i not in bucket:
                bucket.append(i)
    for col_x, idxs in out_by_column.items():
        base_x = col_x + 24.0
        for k, idx in enumerate(sorted(idxs)):
            out_port_x_stub[idx] = base_x + k * STUB_FAN

    in_by_column: Dict[float, List[int]] = {}
    for block_name, idxs in fwd_incoming.items():
        rect = node_rects[block_name]
        col_x = round(rect[0], 1)
        bucket = in_by_column.setdefault(col_x, [])
        for i in idxs:
            if i not in bucket:
                bucket.append(i)
    for col_x, idxs in in_by_column.items():
        base_x = col_x - 24.0
        for k, idx in enumerate(sorted(idxs)):
            in_port_x_stub[idx] = base_x - k * STUB_FAN

    if DEBUG_ROUTING:
        print(
            f"[stub-assign] out_by_column keys={list(out_by_column.keys())}",
            file=sys.stderr,
        )
        for col_x, idxs in out_by_column.items():
            print(
                f"  out col_x={col_x}: idxs={sorted(idxs)} -> x's={[out_port_x_stub[i] for i in sorted(idxs)]}",
                file=sys.stderr,
            )
        print(
            f"[stub-assign] in_by_column keys={list(in_by_column.keys())}",
            file=sys.stderr,
        )
        for col_x, idxs in in_by_column.items():
            print(
                f"  in col_x={col_x}: idxs={sorted(idxs)} -> x's={[in_port_x_stub[i] for i in sorted(idxs)]}",
                file=sys.stderr,
            )

    reserved_by_boundary: Dict[int, List[float]] = {}
    global_elbow_xs: List[float] = []
    claimed_overflow_lanes: List[float] = []
    routed_edges: List[Tuple[str, str, str, List[Tuple[float, float]], bool]] = []

    def _span(item):
        idx, (src, dst, _var) = item
        return layers[dst] - layers[src]

    for idx, (src, dst, var) in sorted(forward_edges, key=_span, reverse=True):
        src_rect = node_rects[src]
        dst_rect = node_rects[dst]
        start = (src_rect[0] + src_rect[2], out_port_y[idx])
        end = (dst_rect[0], in_port_y[idx])
        path, claims = route_forward_waypoints(
            start,
            end,
            all_rects,
            skip=[src_rect, dst_rect],
            reserved_by_boundary=reserved_by_boundary,
            layer_gap_xs=layer_gap_xs,
            claimed_overflow_lanes=claimed_overflow_lanes,
            global_reserved_x=global_elbow_xs,
            exit_stub_x=out_port_x_stub.get(idx),
            entry_stub_x=in_port_x_stub.get(idx),
        )
        # POST-PROCESS SAFETY NET: force the path's actual first segment
        # (leaving the source port) and last segment (entering the
        # destination port) to sit at the pre-assigned, guaranteed-
        # distinct stub x for this edge's port index -- regardless of
        # what the router internally produced. Earlier attempts threaded
        # a "preferred/assigned" x through several layers of routing
        # logic (single-elbow search, multi-gap stair-step, their
        # fallbacks) and it was not reliably honored by every branch.
        # Rewriting the first/last segment here, after routing, is a
        # single guaranteed choke point: whatever the router internally
        # decided, THIS is what actually gets drawn.
        assigned_exit_x = out_port_x_stub.get(idx)
        assigned_entry_x = in_port_x_stub.get(idx)

        def try_rewrite_exit(target_x: float) -> bool:
            nonlocal path
            if len(path) <= 2:
                return False
            shifted = [path[0], (target_x, path[0][1])] + path[2:]
            if not _path_collides(
                shifted, all_rects, skip=[src_rect, dst_rect], pad=CORNER_RADIUS
            ):
                path = shifted
                return True
            return False

        def try_rewrite_entry(target_x: float) -> bool:
            nonlocal path
            if len(path) <= 2:
                return False
            shifted = path[:-2] + [(target_x, path[-1][1]), path[-1]]
            if not _path_collides(
                shifted, all_rects, skip=[src_rect, dst_rect], pad=CORNER_RADIUS
            ):
                path = shifted
                return True
            return False

        if assigned_exit_x is not None and len(path) >= 2:
            old_exit_x = path[1][0]
            if abs(old_exit_x - assigned_exit_x) > 0.5:
                if not try_rewrite_exit(assigned_exit_x):
                    # First choice collides (e.g. clips a box sitting
                    # near that x). Rather than silently reverting to the
                    # OLD x -- which is what caused two sibling edges to
                    # end up sharing a column in the first place, since
                    # the old x is exactly the value some other edge in
                    # this same column also naturally lands on -- search
                    # outward in both directions in STUB_FAN steps for
                    # any nearby x that both clears boxes AND isn't the
                    # old (shared) value.
                    found = False
                    for k in range(1, 15):
                        for sign in (1, -1):
                            cand = assigned_exit_x + sign * STUB_FAN * k
                            if abs(cand - old_exit_x) < 1.0:
                                continue
                            if try_rewrite_exit(cand):
                                global_elbow_xs.append(cand)
                                found = True
                                break
                        if found:
                            break
                    if not found and DEBUG_ROUTING:
                        print(
                            f"[rewrite-rejected exit] idx={idx} {src}->{dst} wanted {assigned_exit_x}, kept {old_exit_x} (no nearby alt clear)",
                            file=sys.stderr,
                        )

        if assigned_entry_x is not None and len(path) >= 2:
            old_entry_x = path[-2][0]
            if abs(old_entry_x - assigned_entry_x) > 0.5:
                if not try_rewrite_entry(assigned_entry_x):
                    found = False
                    for k in range(1, 15):
                        for sign in (1, -1):
                            cand = assigned_entry_x + sign * STUB_FAN * k
                            if abs(cand - old_entry_x) < 1.0:
                                continue
                            if try_rewrite_entry(cand):
                                global_elbow_xs.append(cand)
                                found = True
                                break
                        if found:
                            break
                    if not found and DEBUG_ROUTING:
                        print(
                            f"[rewrite-rejected entry] idx={idx} {src}->{dst} wanted {assigned_entry_x}, kept {old_entry_x} (no nearby alt clear)",
                            file=sys.stderr,
                        )

        if DEBUG_ROUTING:
            print(
                f"[final] idx={idx} {src}->{dst} ({var}) assigned_exit={assigned_exit_x} assigned_entry={assigned_entry_x} final_first_x={path[1][0] if len(path)>1 else None} final_last_bend_x={path[-2][0] if len(path)>1 else None}",
                file=sys.stderr,
            )
        for bidx, cy in claims:
            if bidx is not None and cy is not None:
                reserved_by_boundary.setdefault(bidx, []).append(cy)
        routed_edges.append((src, dst, var, path, False))

    order_key = {(s, d, v): i for i, (s, d, v) in enumerate(edges)}
    routed_edges.sort(key=lambda t: order_key.get((t[0], t[1], t[2]), 0))

    for lane_i, (idx, (src, dst, var)) in enumerate(back_edges):
        src_rect = node_rects[src]
        dst_rect = node_rects[dst]
        lane_y = TOP_MARGIN - BACK_LANE_TOP_GAP - lane_i * BACK_LANE_HEIGHT
        path = route_back_waypoints(
            src_rect,
            dst_rect,
            src_port_x=out_port_x[idx],
            dst_port_x=in_port_x[idx],
            lane_y=lane_y,
            all_rects=all_rects,
            skip=[src_rect, dst_rect],
            global_reserved_x=global_elbow_xs,
        )
        routed_edges.append((src, dst, var, path, True))

    stub_edge_paths: List[Tuple[str, int, str, List[Tuple[float, float]]]] = []
    for n in nodes:
        stubs = external_inputs.get(n.block_name, [])
        target_rect = node_rects[n.block_name]
        n_stubs = len(stubs)
        target_ys = _distribute_points(
            target_rect[1] + target_rect[3] / 2, n_stubs, PORT_SPACING
        )
        for i, label in enumerate(stubs):
            key = (n.block_name, i)
            stub_rect = stub_rects[key]
            start = (stub_rect[0] + stub_rect[2], stub_rect[1] + stub_rect[3] / 2)
            end = (target_rect[0], target_ys[i])
            path, _claims = route_forward_waypoints(
                start,
                end,
                all_rects,
                skip=[stub_rect, target_rect],
                claimed_overflow_lanes=claimed_overflow_lanes,
                global_reserved_x=global_elbow_xs,
            )
            stub_edge_paths.append((n.block_name, i, label, path))

    min_y_seen = min(
        [p[1] for _, _, _, path, _ in routed_edges for p in path]
        + [p[1] for _, _, _, path in stub_edge_paths for p in path]
        + [0.0],
        default=0.0,
    )
    if min_y_seen < 10:
        shift = 10 - min_y_seen
        positions = {k: (x, y + shift) for k, (x, y) in positions.items()}
        stub_positions = {k: (x, y + shift) for k, (x, y) in stub_positions.items()}
        node_rects = {
            k: (r[0], r[1] + shift, r[2], r[3]) for k, r in node_rects.items()
        }
        stub_rects = {
            k: (r[0], r[1] + shift, r[2], r[3]) for k, r in stub_rects.items()
        }
        all_rects = list(node_rects.values()) + list(stub_rects.values())
        routed_edges = [
            (s, d, v, [(x, y + shift) for (x, y) in path], b)
            for (s, d, v, path, b) in routed_edges
        ]
        stub_edge_paths = [
            (bn, i, lbl, [(x, y + shift) for (x, y) in path])
            for (bn, i, lbl, path) in stub_edge_paths
        ]
        total_height += shift

    max_y_seen = max(
        [r[1] + r[3] for r in all_rects]
        + [p[1] for _, _, _, path, _ in routed_edges for p in path]
        + [p[1] for _, _, _, path in stub_edge_paths for p in path],
        default=total_height,
    )
    total_height = max(total_height, max_y_seen + 70)

    svg_parts: List[str] = []
    svg_parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_width:.0f} {total_height:.0f}" '
        f'font-family="Helvetica, Arial, sans-serif">'
    )
    svg_parts.append(
        f'<rect x="0" y="0" width="{total_width:.0f}" height="{total_height:.0f}" fill="#fafafa"/>'
    )
    svg_parts.append(
        f'<text x="{MARGIN}" y="30" font-size="18" font-weight="bold" fill="#1a1a1a">{escape_xml(title)}</text>'
    )
    svg_parts.append(
        "<defs>"
        '<marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M0,0 L10,5 L0,10 z" fill="#4a5568"/>'
        "</marker>"
        '<marker id="arrow-stub" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        '<path d="M0,0 L10,5 L0,10 z" fill="#a0aec0"/>'
        "</marker>"
        '<marker id="arrow-back" viewBox="0 0 10 10" refX="9" refY="5" '
        'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
        '<path d="M0,0 L10,5 L0,10 z" fill="#b7791f"/>'
        "</marker>"
        "</defs>"
    )

    # --- Boxes drawn FIRST so edges/labels always render on top ---------

    for n in nodes:
        stubs = external_inputs.get(n.block_name, [])
        for i, label in enumerate(stubs):
            key = (n.block_name, i)
            sx, sy, sw, sh = stub_rects[key]
            svg_parts.append(
                f'<rect x="{sx:.0f}" y="{sy:.0f}" width="{sw:.0f}" height="{sh:.0f}" '
                f'rx="6" fill="#edf2f7" stroke="#a0aec0" stroke-width="1.5"/>'
            )
            wrapped = wrap_text(label, 22)[:2]
            for li, wline in enumerate(wrapped):
                svg_parts.append(
                    f'<text x="{sx + sw/2:.0f}" y="{sy + 13 + li * 13:.0f}" '
                    f'font-size="10.5" fill="#4a5568" text-anchor="middle">{escape_xml(wline)}</text>'
                )

    for n in nodes:
        rx, ry, rw, rh = node_rects[n.block_name]
        svg_parts.append(
            f'<rect x="{rx:.0f}" y="{ry:.0f}" width="{BOX_W}" height="{rh}" rx="10" '
            f'fill="#ebf8ff" stroke="#2b6cb0" stroke-width="2"/>'
        )
        svg_parts.append(
            f'<rect x="{rx:.0f}" y="{ry:.0f}" width="{BOX_W}" height="24" rx="10" fill="#2b6cb0"/>'
        )
        svg_parts.append(
            f'<rect x="{rx:.0f}" y="{ry + 12:.0f}" width="{BOX_W}" height="12" fill="#2b6cb0"/>'
        )
        svg_parts.append(
            f'<text x="{rx + BOX_W/2:.0f}" y="{ry + 17:.0f}" font-size="13" font-weight="bold" '
            f'fill="white" text-anchor="middle">[{escape_xml(n.block_name)}]</text>'
        )
        content_lines = node_content[n.block_name]
        for li, line in enumerate(content_lines):
            svg_parts.append(
                f'<text x="{rx + 12:.0f}" y="{ry + 42 + li * LINE_H:.0f}" font-size="11.5" '
                f'fill="#1a202c">{escape_xml(line)}</text>'
            )
        if not content_lines:
            svg_parts.append(
                f'<text x="{rx + 12:.0f}" y="{ry + 42:.0f}" font-size="11.5" '
                f'fill="#718096" font-style="italic">FuelCycleSystemScalarKernel</text>'
            )

    # --- Stub edges on top of boxes --------------------------------------

    for block_name, stub_idx, label, path in stub_edge_paths:
        d = waypoints_to_rounded_path(path)
        svg_parts.append(
            f'<path d="{d}" fill="none" stroke="#a0aec0" stroke-width="1.5" '
            f'stroke-dasharray="4,3" stroke-linecap="round" marker-end="url(#arrow-stub)"/>'
        )

    # --- Main edges + labels, on top of everything -----------------------

    placed_label_rects: List[Rect] = []

    for src, dst, varname, path, is_back in routed_edges:
        d = waypoints_to_rounded_path(path)
        stroke = "#b7791f" if is_back else "#4a5568"
        marker = "url(#arrow-back)" if is_back else "url(#arrow)"
        dash = ' stroke-dasharray="6,3"' if is_back else ""
        svg_parts.append(
            f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="2"{dash} '
            f'stroke-linecap="round" marker-end="{marker}"/>'
        )

        label_x, label_y, anchor_x, anchor_y = place_label(
            path, varname, placed_label_rects
        )
        lr = _label_rect_at(label_x, label_y, varname)
        placed_label_rects.append(lr)

        if (label_x - anchor_x) ** 2 + (label_y - anchor_y) ** 2 > 4.0:
            svg_parts.append(
                f'<line x1="{anchor_x:.0f}" y1="{anchor_y:.0f}" x2="{label_x:.0f}" y2="{label_y:.0f}" '
                f'stroke="{stroke}" stroke-width="1" opacity="0.5"/>'
            )

        svg_parts.append(
            f'<rect x="{lr[0]:.0f}" y="{lr[1]:.0f}" width="{lr[2]:.0f}" height="{lr[3]:.0f}" '
            f'fill="#fafafa" stroke="{stroke}" stroke-width="0.75" opacity="0.97"/>'
        )
        svg_parts.append(
            f'<text x="{label_x:.0f}" y="{label_y + 4:.0f}" font-size="11" fill="{stroke}" '
            f'text-anchor="middle">{escape_xml(varname)}</text>'
        )

    legend_y = total_height - 46
    svg_parts.append(
        f'<line x1="{MARGIN}" y1="{legend_y}" x2="{MARGIN+40}" y2="{legend_y}" '
        f'stroke="#4a5568" stroke-width="2" marker-end="url(#arrow)"/>'
    )
    svg_parts.append(
        f'<text x="{MARGIN+50}" y="{legend_y+4}" font-size="12" fill="#2d3748">'
        f"variable flowing between blocks</text>"
    )
    svg_parts.append(
        f'<line x1="{MARGIN}" y1="{legend_y+20}" x2="{MARGIN+40}" y2="{legend_y+20}" '
        f'stroke="#b7791f" stroke-width="2" stroke-dasharray="6,3" marker-end="url(#arrow-back)"/>'
    )
    svg_parts.append(
        f'<text x="{MARGIN+50}" y="{legend_y+24}" font-size="12" fill="#2d3748">'
        f"feedback / cycle edge</text>"
    )
    svg_parts.append(
        f'<line x1="{MARGIN}" y1="{legend_y+40}" x2="{MARGIN+40}" y2="{legend_y+40}" '
        f'stroke="#a0aec0" stroke-width="1.5" stroke-dasharray="4,3" marker-end="url(#arrow-stub)"/>'
    )
    svg_parts.append(
        f'<text x="{MARGIN+50}" y="{legend_y+44}" font-size="12" fill="#4a5568">'
        f"external input / other_sources</text>"
    )

    svg_parts.append("</svg>")

    verification_warnings: List[str] = []
    if verify:
        rect_names: Dict[int, str] = {}
        for name, r in node_rects.items():
            rect_names[id(r)] = f"node [{name}]"
        for (block_name, stub_idx), r in stub_rects.items():
            rect_names[id(r)] = f"stub #{stub_idx} of [{block_name}]"

        for src, dst, varname, path, is_back in routed_edges:
            skip = [node_rects[src], node_rects[dst]]
            hits = verify_path_clear(path, all_rects, skip)
            for rect in hits:
                label = rect_names.get(id(rect), "unknown rect")
                verification_warnings.append(
                    f"edge {src} -> {dst} ({varname}): rendered path still overlaps {label}"
                )
        for block_name, stub_idx, label_text, path in stub_edge_paths:
            skip = [stub_rects[(block_name, stub_idx)], node_rects[block_name]]
            hits = verify_path_clear(path, all_rects, skip)
            for rect in hits:
                label = rect_names.get(id(rect), "unknown rect")
                verification_warnings.append(
                    f"stub edge -> {block_name} ({label_text}): rendered path still overlaps {label}"
                )

    return "\n".join(svg_parts), verification_warnings


def _empty_svg(title: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 120" '
        'font-family="Helvetica, Arial, sans-serif">'
        '<rect width="600" height="120" fill="#fafafa"/>'
        f'<text x="20" y="30" font-size="16" font-weight="bold">{escape_xml(title)}</text>'
        '<text x="20" y="60" font-size="13" fill="#718096">'
        "No FuelCycleSystemScalarKernel blocks were found in this input file.</text>"
        "</svg>"
    )


# --------------------------------------------------------------------------
# 9. Optional Graphviz DOT export
# --------------------------------------------------------------------------


def render_dot(
    nodes: List[FuelCycleNode],
    edges: List[Tuple[str, str, str]],
    external_inputs: Dict[str, List[str]],
) -> str:
    lines = [
        "digraph FuelCycle {",
        "  rankdir=LR;",
        "  splines=ortho;",
        '  node [shape=box, style="rounded,filled", fillcolor="#ebf8ff", color="#2b6cb0"];',
    ]
    for n in nodes:
        label_lines = [f"[{n.block_name}]"]
        if n.comment:
            label_lines.append(n.comment)
        if n.kernel_type and n.kernel_type != FUEL_CYCLE_KERNEL_BASE_NAME:
            label_lines.append(f"type: {n.kernel_type}")
        if n.variable:
            label_lines.append(f"variable: {n.variable}")
        for k, v in n.extra_params.items():
            label_lines.append(f"{k} = {v}")
        label = "\\n".join(l.replace('"', "'") for l in label_lines)
        lines.append(f'  "{n.block_name}" [label="{label}"];')

    stub_counter = 0
    for n in nodes:
        for s in external_inputs.get(n.block_name, []):
            stub_counter += 1
            stub_id = f"ext_{stub_counter}"
            slabel = s.replace('"', "'")
            lines.append(
                f'  "{stub_id}" [label="{slabel}", shape=ellipse, style=dashed, fillcolor="#edf2f7", color="#a0aec0"];'
            )
            lines.append(
                f'  "{stub_id}" -> "{n.block_name}" [style=dashed, color="#a0aec0"];'
            )

    for src, dst, var in edges:
        vlabel = var.replace('"', "'")
        lines.append(f'  "{src}" -> "{dst}" [label="{vlabel}"];')

    lines.append("}")
    return "\n".join(lines)


# --------------------------------------------------------------------------
# 10. CLI
# --------------------------------------------------------------------------


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Diagram FuelCycleSystemScalarKernel blocks in a TMAP8 input file."
    )
    parser.add_argument(
        "input_file",
        type=Path,
        help="Path to the TMAP8 .i input file",
        default=input_folder + "fuel_cycle_abdou_generic_AD.i",
        nargs="?",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Output SVG path (default: <input_stem>_fuelcycle.svg next to the input file)",
    )
    parser.add_argument(
        "--dot",
        type=Path,
        default=None,
        help="Also write a Graphviz DOT file to this path",
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=None,
        help="Also write the parsed block/edge data as JSON to this path",
    )
    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help="Custom title for the diagram",
    )
    parser.add_argument(
        "--list-kernel-types",
        action="store_true",
        help="Print the distinct `type = ...` values matched and exit",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="After rendering, check every edge's final path against every node/stub box and "
        "print a warning for any residual overlap",
    )
    parser.add_argument(
        "--debug-routing",
        action="store_true",
        help="Print, for every edge, which router handled it (single-elbow / "
        "multi-gap / overflow-lane / back-staple) and the exact x of its "
        "first vertical segment after leaving the source port -- use this "
        "to see which edges are landing on the same bend column and why.",
    )
    args = parser.parse_args(argv)

    if args.debug_routing:
        global DEBUG_ROUTING
        DEBUG_ROUTING = True

    if not args.input_file.exists():
        print(f"error: input file not found: {args.input_file}", file=sys.stderr)
        return 1

    try:
        source_lines = expand_includes(args.input_file)
    except (FileNotFoundError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    text = "\n".join(source_lines)

    root = parse_moose_file(text)
    nodes = build_fuelcycle_nodes(root, source_lines)

    if args.list_kernel_types:
        types = sorted({n.kernel_type for n in nodes if n.kernel_type})
        if types:
            print("Matched FuelCycleSystemScalarKernel variant type(s):")
            for t in types:
                print(f"  - {t}")
        else:
            print("No FuelCycleSystemScalarKernel variant blocks found.")
        return 0

    if not nodes:
        print(
            f"warning: no FuelCycleSystemScalarKernel-variant blocks found in {args.input_file}",
            file=sys.stderr,
        )

    edges, external_inputs = build_edges(nodes)

    title = (
        args.title or f"FuelCycleSystemScalarKernel diagram — {args.input_file.name}"
    )
    svg_text, verification_warnings = render_svg(
        nodes, edges, external_inputs, title=title, verify=args.verify
    )

    if args.verify:
        if verification_warnings:
            print(
                f"--verify found {len(verification_warnings)} residual overlap(s):",
                file=sys.stderr,
            )
            for w in verification_warnings:
                print(f"  - {w}", file=sys.stderr)
        else:
            print("--verify: no residual overlaps found", file=sys.stderr)

    out_path = args.output or args.input_file.with_name(
        args.input_file.stem + "_fuelcycle.svg"
    )
    out_path.write_text(svg_text, encoding="utf-8")
    print(f"wrote {out_path}")

    if args.dot:
        dot_text = render_dot(nodes, edges, external_inputs)
        args.dot.write_text(dot_text, encoding="utf-8")
        print(f"wrote {args.dot}")

    if args.json:
        data = {
            "blocks": [
                {
                    "name": n.block_name,
                    "kernel_type": n.kernel_type,
                    "comment": n.comment,
                    "variable": n.variable,
                    "inputs": n.inputs,
                    "other_sources": n.other_sources,
                    "extra_params": n.extra_params,
                }
                for n in nodes
            ],
            "edges": [{"from": s, "to": d, "variable": v} for s, d, v in edges],
            "external_inputs": external_inputs,
        }
        args.json.write_text(json.dumps(data, indent=2), encoding="utf-8")
        print(f"wrote {args.json}")

    print(
        f"found {len(nodes)} FuelCycleSystemScalarKernel-variant block(s), {len(edges)} inter-block edge(s)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
