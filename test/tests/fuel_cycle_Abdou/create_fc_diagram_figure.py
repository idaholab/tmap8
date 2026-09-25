#!/usr/bin/env python3
import os
import importlib
import importlib.util
import sys
from pathlib import Path
script_folder = os.path.dirname(__file__)
os.chdir(script_folder)

if "/tmap8/doc" in script_folder.lower():
    input_folder = "../../../../test/tests/fuel_cycle_Abdou/"
    scripts_folder = "../../../../scripts/"
else:
    input_folder = "./"
    scripts_folder = "../../../scripts/"


spec = importlib.util.spec_from_file_location("create_fuel_cycle_diagram",scripts_folder+'create_fuel_cycle_diagram.py')
create_fuel_cycle_diagram = importlib.util.module_from_spec(spec)
sys.modules['create_fuel_cycle_diagram'] = create_fuel_cycle_diagram
spec.loader.exec_module(create_fuel_cycle_diagram)
source_lines = create_fuel_cycle_diagram.expand_includes(Path(input_folder+'fuel_cycle_abdou_generic_AD.i'))
text = "\n".join(source_lines)
root = create_fuel_cycle_diagram.parse_moose_file(text)
nodes = create_fuel_cycle_diagram.build_fuelcycle_nodes(root,source_lines)
edges, external_inputs = create_fuel_cycle_diagram.build_edges(nodes)

title = (
    f"Abdou Fuel Cycle Diagram"
)
svg_text, verification_warnings = create_fuel_cycle_diagram.render_svg(
    nodes, edges, external_inputs, title=title, verify=False
)

out_path = Path('fuel_cycle_abdou_generic_AD_fuelcycle.svg')
out_path.write_text(svg_text, encoding="utf-8")

