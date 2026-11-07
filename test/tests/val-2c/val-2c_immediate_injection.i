# This input file utilizes val_2c_base and adds specific parameter values and capabilities to inject T2 immediately

# Physical Constants (from TMAP8PhysicalConstants.h)
kb = '${units 1.380649e-23 J/K}' # Boltzmann constant based on number used in TMAP8PhysicalConstants.h
NA = '${units 6.02214076e23 at/mol}' # Avogadro's number based on number used in TMAP8PhysicalConstants.h

## Geometry
paint_thickness = '${units 0.16 mm -> mum}'
mesh_num_nodes_paint = 12 # impose by manual mesh
mesh_node_size_paint = '${fparse paint_thickness/mesh_num_nodes_paint}'
length_domain = '${fparse paint_thickness + 2*mesh_node_size_paint}'
volume_enclosure = '${units 0.96 m^3 -> mum^3}'

## Conditions
temperature = '${units 303 K}'

## Conversion
Curie = '${units 3.7e10 1/s}' # disintegrations/s - activity of one Curie
decay_rate_tritium = '${units 1.782785958230312e-09 1/s/at}' # disintegrations/s/atoms
conversion_Ci_atom = '${units ${fparse decay_rate_tritium / Curie} 1/at}' # 1 tritium at = ~4.82e-20 Ci
concentration_to_pressure_conversion_factor = '${units ${fparse kb * temperature} Pa*m^3 -> Pa*mum^3}' # J = Pa*m^3

## Material properties
diffusivity_elemental_tritium = '${units 4.0e-12 m^2/s -> mum^2/s}'
diffusivity_tritiated_water = '${units 1.0e-14 m^2/s -> mum^2/s}'
diffusivity_artificial_enclosure = '${fparse diffusivity_elemental_tritium*1e3}'
reaction_rate = '${units ${fparse 1.5 * 2.0e-10*conversion_Ci_atom} m^3/at/s -> mum^3/at/s}' # ~ 1.5* 9.62e-30 m^3/at/s, close to the 1.0e-29 m3/atoms/s in TMAP4
solubility_elemental_tritium = '${units ${fparse 5e-2 * 4.0e19} 1/m^3/Pa -> 1/mum^3/Pa}' # molecules/microns^3/Pa = molecules*s^2/m^2/kg
solubility_tritiated_water = '${units ${fparse 3.5e-4 * 6.0e24} 1/m^3/Pa -> 1/mum^3/Pa}' # molecules/microns^3/Pa = molecules*s^2/m^2/kg

## Initial conditions
# The units below are actually in molecules, not atoms
initial_T2_inventory = '${units ${fparse 10 / 2 / conversion_Ci_atom} at}' # (equivalent to 10 Ci) - the 1/2 is to account for 2 tritium atoms per molecules, both contributing to activity
initial_T2_concentration = '${units ${fparse initial_T2_inventory / volume_enclosure} at/mum^3}'
initial_H2O_pressure = '${units 714 Pa}' # Found in TMAP4 input file, which corresponds to ambient air with 20% relative humidity.
initial_H2O_concentration = '${units ${fparse initial_H2O_pressure / concentration_to_pressure_conversion_factor} at/mum^3}'

## Numerical parameters
time_step = '${units 1 s}'
time_end = '${units 180000 s}'
dtmax = '${units 1e3 s}'
dtmin = '${units 1 s}'

## Inflow and outflow
inflow = '${units 0.54 m^3/h -> mum^3/s}' # inflow of normally moist (20% relative humidity) air at the same temperature as the enclosure
inflow_concentration = '${fparse initial_H2O_concentration * inflow / volume_enclosure}'
outflow = '${units 0.54 m^3/h -> mum^3/s}' # outflow of enclosure air # even if only 0.06 m^3/h is used to do measurements, all that air is purged out.

!include val-2c_base.i

[Variables]
  # T2 concentration in the enclosure in molecules/microns^3
  [t2_enclosure_concentration]
    initial_condition = ${initial_T2_concentration}
  []
[]
