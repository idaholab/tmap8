#!/usr/bin/env python3
"""Unit tests for scripts/create_fuel_cycle_diagram.py's compact-mode edge
routing and label placement.

Run directly with `python3 test_diagram_label_and_routing.py`.
"""

import importlib.util
import math
import os
import sys
import unittest
from pathlib import Path

script_folder = os.path.dirname(__file__)
os.chdir(script_folder)

spec = importlib.util.spec_from_file_location(
    "create_fuel_cycle_diagram", "../../../scripts/create_fuel_cycle_diagram.py"
)
cfd = importlib.util.module_from_spec(spec)
sys.modules["create_fuel_cycle_diagram"] = cfd
spec.loader.exec_module(cfd)


def _load_fixture(filename):
    source_lines = cfd.expand_includes(Path(filename))
    text = "\n".join(source_lines)
    root = cfd.parse_moose_file(text)
    families = list(cfd.BUILTIN_KERNEL_FAMILIES.values())
    nodes = cfd.build_kernel_nodes(root, source_lines, families)
    edges, external_inputs = cfd.build_edges(nodes)
    return nodes, edges, external_inputs


class TestRectHitsPath(unittest.TestCase):
    """Checks whether a rect overlaps any segment of a polyline path."""

    def test_detects_crossing_segment(self):
        rect = (10.0, 10.0, 20.0, 10.0)  # x in [10,30], y in [10,20]
        crossing_path = [(0.0, 15.0), (50.0, 15.0)]
        self.assertTrue(cfd._rect_hits_path(rect, crossing_path, pad=0.0))

    def test_ignores_distant_segment(self):
        rect = (10.0, 10.0, 20.0, 10.0)
        distant_path = [(0.0, 100.0), (50.0, 100.0)]
        self.assertFalse(cfd._rect_hits_path(rect, distant_path, pad=0.0))


class TestPlaceLabel(unittest.TestCase):
    """place_label avoids other labels, obstacle boxes, and other edges'
    lines, and only forces a crowded placement when require_space=False."""

    def test_slides_away_from_obstacle_box(self):
        path = [(0.0, 0.0), (200.0, 0.0)]
        obstacle = cfd._label_rect_at(100.0, 0.0, "T_VAR")  # sits on the midpoint
        placement = cfd.place_label(path, "T_VAR", [], obstacle_rects=[obstacle])
        self.assertIsNotNone(placement)
        lx, ly, _, _ = placement
        label_rect = cfd._label_rect_at(lx, ly, "T_VAR")
        self.assertFalse(cfd._rects_overlap(label_rect, obstacle, pad=2.0))

    def test_slides_away_from_crossing_edge(self):
        path = [(0.0, 0.0), (200.0, 0.0)]
        crossing = [(100.0, -50.0), (100.0, 50.0)]  # vertical line through midpoint
        placement = cfd.place_label(path, "T_VAR", [], other_paths=[crossing])
        self.assertIsNotNone(placement)
        lx, ly, _, _ = placement
        label_rect = cfd._label_rect_at(lx, ly, "T_VAR")
        self.assertFalse(cfd._rect_hits_path(label_rect, crossing, pad=3.0))

    def test_returns_none_when_fully_crowded_and_space_required(self):
        path = [(0.0, 0.0), (40.0, 0.0)]
        obstacle = (-100.0, -20.0, 300.0, 40.0)  # covers every candidate slide position
        placement = cfd.place_label(
            path, "T_VAR", [], obstacle_rects=[obstacle], require_space=True
        )
        self.assertIsNone(placement)

    def test_forces_placement_when_space_not_required(self):
        path = [(0.0, 0.0), (40.0, 0.0)]
        obstacle = (-100.0, -20.0, 300.0, 40.0)
        placement = cfd.place_label(
            path, "T_VAR", [], obstacle_rects=[obstacle], require_space=False
        )
        self.assertIsNotNone(placement)


def _path_length(path):
    return sum(
        math.hypot(path[i + 1][0] - path[i][0], path[i + 1][1] - path[i][1])
        for i in range(len(path) - 1)
    )


def _path_self_overlaps(path, pad=1.0):
    """True if two non-adjacent segments of this path overlap each other
    (the path folds back over itself, e.g. a fishhook or loop)."""
    segs = [cfd._segment_box(*path[i], *path[i + 1]) for i in range(len(path) - 1)]
    for i in range(len(segs)):
        for j in range(i + 2, len(segs)):
            if cfd._rects_overlap(segs[i], segs[j], pad=pad):
                return True
    return False


class TestCompactRoutingHasNoFishhooks(unittest.TestCase):
    """Checks that no routed edge self-overlaps or detours far beyond the
    direct distance between its endpoints, in compact mode."""

    # Fixed layouts peak at ~1.7x; a bad detour can reach ~3.6x.
    MAX_LENGTH_RATIO = 2.2

    def _assert_clean_routing(self, filename):
        nodes, edges, external_inputs = _load_fixture(filename)
        layout = cfd.compute_diagram_layout(
            nodes, edges, external_inputs, verify=True, compact=True
        )
        self.assertEqual(
            layout["verification_warnings"],
            [],
            f"compact-mode routing for {filename} left residual box overlaps",
        )
        for src, dst, varname, path, _is_back in layout["routed_edges"]:
            self.assertFalse(
                _path_self_overlaps(path),
                f"{filename}: edge {src}->{dst} ({varname}) self-overlaps "
                "in compact mode -- a fishhook/loop in the routed path",
            )
            manhattan = abs(path[0][0] - path[-1][0]) + abs(path[0][1] - path[-1][1])
            if manhattan > 1:
                ratio = _path_length(path) / manhattan
                self.assertLessEqual(
                    ratio,
                    self.MAX_LENGTH_RATIO,
                    f"{filename}: edge {src}->{dst} ({varname}) is {ratio:.2f}x "
                    "the direct distance in compact mode -- an excessive detour",
                )

    def test_fuel_cycle(self):
        self._assert_clean_routing("fuel_cycle.i")

    def test_fuel_cycle_abdou_generic(self):
        self._assert_clean_routing("fuel_cycle_abdou_generic.i")

    def test_fuel_cycle_abdou_generic_AD(self):
        self._assert_clean_routing("fuel_cycle_abdou_generic_AD.i")


class TestCompactLabelsAppearWhenThereIsSpace(unittest.TestCase):
    """Checks that compact mode still renders edge labels where space
    allows, without introducing verification warnings."""

    def test_svg_contains_at_least_one_edge_label(self):
        nodes, edges, external_inputs = _load_fixture("fuel_cycle_abdou_generic.i")
        svg_text, warnings = cfd.render_svg(
            nodes, edges, external_inputs, compact=True, verify=True
        )
        self.assertEqual(warnings, [])
        varnames = {e[2] for e in edges}
        self.assertTrue(
            any(v in svg_text for v in varnames),
            "no edge-variable label text found anywhere in the compact SVG output",
        )


if __name__ == "__main__":
    unittest.main()
