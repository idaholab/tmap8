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

if "TMAP8_DIR" in os.environ:
    scripts_folder = os.path.join(os.environ["TMAP8_DIR"], "scripts") + "/"
elif "/tmap8/doc" in script_folder.lower():
    scripts_folder = "../../../../scripts/"
else:
    scripts_folder = "../../../scripts/"


spec = importlib.util.spec_from_file_location(
    "create_fuel_cycle_diagram", scripts_folder + "create_fuel_cycle_diagram.py"
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


def _pp_block(name, **params):
    return cfd.MooseBlock(name=name, path=("Postprocessors", name), params=params)


class TestResolveConstantValue(unittest.TestCase):
    """resolve_constant_value resolves ConstantPostprocessors directly and
    ParsedPostprocessors through their pp_names/expression, but bails out
    (returns None) on anything outside that very-simple-expression scope."""

    def test_constant_postprocessor_resolves_directly(self):
        pps = {"c": _pp_block("c", type="ConstantPostprocessor", value="86400")}
        self.assertEqual(cfd.resolve_constant_value("c", pps), 86400.0)

    def test_parsed_postprocessor_resolves_through_constants(self):
        pps = {
            "eta": _pp_block("eta", type="ConstantPostprocessor", value="0.95"),
            "tau": _pp_block("tau", type="ConstantPostprocessor", value="86400"),
            "frac": _pp_block(
                "frac",
                type="ParsedPostprocessor",
                pp_names="eta tau",
                expression="(1 - eta) / tau",
            ),
        }
        self.assertAlmostEqual(cfd.resolve_constant_value("frac", pps), 0.05 / 86400)

    def test_unresolvable_reference_returns_none(self):
        pps = {
            "f": _pp_block("f", type="FunctionPostprocessor", function="sin(t)"),
            "frac": _pp_block(
                "frac", type="ParsedPostprocessor", pp_names="f", expression="f"
            ),
        }
        self.assertIsNone(cfd.resolve_constant_value("frac", pps))

    def test_cyclic_reference_returns_none(self):
        pps = {
            "a": _pp_block(
                "a", type="ParsedPostprocessor", pp_names="b", expression="b"
            ),
            "b": _pp_block(
                "b", type="ParsedPostprocessor", pp_names="a", expression="a"
            ),
        }
        self.assertIsNone(cfd.resolve_constant_value("a", pps))

    def test_disallowed_expression_construct_returns_none(self):
        pps = {
            "frac": _pp_block(
                "frac",
                type="ParsedPostprocessor",
                pp_names="",
                expression="abs(-1)",
            )
        }
        self.assertIsNone(cfd.resolve_constant_value("frac", pps))

    def test_unknown_name_returns_none(self):
        self.assertIsNone(cfd.resolve_constant_value("nope", {}))


class TestFlowFractionLabels(unittest.TestCase):
    """--show-flow-fractions resolves real input_fractions postprocessors
    from the Abdou fixtures into numeric edge-label suffixes, is a no-op
    by default, and is always suppressed in compact mode."""

    def test_default_output_has_no_fraction_suffixes(self):
        nodes, edges, external_inputs = _load_fixture("fuel_cycle_abdou_generic.i")
        svg_text, warnings = cfd.render_svg(nodes, edges, external_inputs, verify=True)
        self.assertEqual(warnings, [])
        # input_fractions=TES_frac still shows in the box's own param list
        # (unrelated to this feature); only the edge-label suffix is gated.
        self.assertNotIn("T_02_TES (TES_frac)", svg_text)
        self.assertNotIn("5.787e-07", svg_text)

    def test_show_flow_fractions_resolves_a_known_edge(self):
        nodes, edges, external_inputs = _load_fixture("fuel_cycle_abdou_generic.i")
        layout = cfd.compute_diagram_layout(
            nodes, edges, external_inputs, verify=True, show_flow_fractions=True
        )
        self.assertEqual(layout["verification_warnings"], [])
        svg_text, warnings = cfd.render_svg(
            nodes, edges, external_inputs, verify=True, layout=layout
        )
        self.assertEqual(warnings, [])
        self.assertIn("5.787e-07", svg_text)

    def test_compact_suppresses_fractions_even_when_requested(self):
        nodes, edges, external_inputs = _load_fixture("fuel_cycle_abdou_generic.i")
        layout = cfd.compute_diagram_layout(
            nodes,
            edges,
            external_inputs,
            verify=True,
            compact=True,
            show_flow_fractions=True,
        )
        self.assertEqual(layout["verification_warnings"], [])
        self.assertEqual(layout["edge_fraction_labels"], {})
        svg_text, warnings = cfd.render_svg(
            nodes, edges, external_inputs, verify=True, compact=True, layout=layout
        )
        self.assertEqual(warnings, [])
        self.assertNotIn("5.787e-07", svg_text)


class TestFractionWidthRatio(unittest.TestCase):
    """_fraction_width_ratio maps a resolved flow-fraction to an edge-width
    multiplier: unscaled when absent, clamped and log-scaled otherwise."""

    def test_none_is_unscaled(self):
        self.assertEqual(cfd._fraction_width_ratio(None), 1.0)

    def test_zero_is_thinnest(self):
        self.assertEqual(cfd._fraction_width_ratio(0), cfd._FRACTION_WIDTH_MIN_RATIO)

    def test_one_is_thickest(self):
        self.assertAlmostEqual(
            cfd._fraction_width_ratio(1), cfd._FRACTION_WIDTH_MAX_RATIO
        )

    def test_increases_monotonically_with_magnitude(self):
        self.assertLess(
            cfd._fraction_width_ratio(1e-6), cfd._fraction_width_ratio(1e-3)
        )
        self.assertLess(
            cfd._fraction_width_ratio(1e-3), cfd._fraction_width_ratio(1e-1)
        )


class TestFlowFractionLineWidth(unittest.TestCase):
    """--show-flow-fractions also scales each edge's stroke width by its
    resolved fraction (via layout["edge_fraction_values"]), gated the same
    way as the text labels: off by default, suppressed in compact mode."""

    def test_default_output_has_no_scaled_widths(self):
        nodes, edges, external_inputs = _load_fixture("fuel_cycle_abdou_generic.i")
        layout = cfd.compute_diagram_layout(nodes, edges, external_inputs, verify=True)
        self.assertEqual(layout["edge_fraction_values"], {})

    def test_show_flow_fractions_populates_known_edge_values(self):
        nodes, edges, external_inputs = _load_fixture("fuel_cycle_abdou_generic.i")
        layout = cfd.compute_diagram_layout(
            nodes, edges, external_inputs, verify=True, show_flow_fractions=True
        )
        values = layout["edge_fraction_values"]
        self.assertTrue(values)
        # same TES edge the label test resolves, and the FCU edge that
        # resolves to exactly 0 (an actual value, not "unresolved").
        self.assertTrue(
            any(abs(v - 5.787037037037042e-07) < 1e-12 for v in values.values())
        )
        self.assertTrue(any(v == 0.0 for v in values.values()))

    def test_compact_suppresses_width_values_too(self):
        nodes, edges, external_inputs = _load_fixture("fuel_cycle_abdou_generic.i")
        layout = cfd.compute_diagram_layout(
            nodes,
            edges,
            external_inputs,
            verify=True,
            compact=True,
            show_flow_fractions=True,
        )
        self.assertEqual(layout["edge_fraction_values"], {})


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
