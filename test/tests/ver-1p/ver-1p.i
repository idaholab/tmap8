# Reference:
#   T. F. Fuerst, M. D. Eklund, J. A. Leland, A. A. Riet, C. N. Taylor,
#   "Parametric Study of the Vacuum Permeator for the Tritium Extraction
#   eXperiment," Fusion Science and Technology 79 (2023) 1224-1234.
#   DOI: 10.1080/15361055.2023.2196237
#
# Radial transport:
#   bulk PbLi -> PbLi/V partition -> cylindrical V diffusion
#   -> recombination -> vacuum
#
# Assumptions:
#   - steady state and isothermal operation
#   - zero pressure on the vacuum side
# Nominal geometry / hydraulics at 673.15 K and Reynolds number = 1e5:
#   Tube length = 5.00 m, inner radius = 4.75 mm,
#   outer radius = 5.00 mm, and PbLi velocity = 1.78 m/s.
# ============================================================================

# -----------------------------------------------------------------------------
# Inputs
# -----------------------------------------------------------------------------
temperature = '${units 673.15 K}'                        # 400 C
gas_constant = '${units 8.31446261815324 J/mol/K}'
concentration_inlet = '${units 1.0 mol/m^3}'             # dissolved H-isotope concentration
reynolds_number = 1e5
tube_length = '${units 5.00 m}'                          # active permeator length
radius_inner_wall = '${units 0.00475 m}'
radius_outer_wall = '${units 0.00500 m}'
number_axial_segments = 20

# -----------------------------------------------------------------------------
# Nominal properties
# -----------------------------------------------------------------------------

diffusivity_PbLi = '${units ${fparse 8.30e-9*exp(-7.37e3/(gas_constant*temperature))} m^2/s}'
density_PbLi = '${units ${fparse 10520.35 - 1.19051*temperature} kg/m^3}'
molar_mass_PbLi_atom = '${units 0.1731558 kg/mol}'
atomic_concentration_PbLi = '${units ${fparse density_PbLi/molar_mass_PbLi_atom} mol/m^3}'
solubility_factor_PbLi = '${units 4.32e-7 1/Pa^0.5}'  # Table II in the paper
solubility_PbLi = '${units ${fparse solubility_factor_PbLi*atomic_concentration_PbLi} mol/m^3/Pa^(1/2)}'
diffusivity_vanadium = '${units ${fparse 2.90e-8*exp(-4.2e3/(gas_constant*temperature))} m^2/s}'
solubility_vanadium = '${units ${fparse 0.138*exp(29.0e3/(gas_constant*temperature))} mol/m^3/Pa^(1/2)}'
recombination_coefficient = '${units 3.1582e-9 m^4/mol/s}'
outer_to_inner_area_ratio = ${fparse radius_outer_wall/radius_inner_wall}
recombination_coefficient_inner_area = '${units ${fparse outer_to_inner_area_ratio*recombination_coefficient} m^4/mol/s}'


# -----------------------------------------------------------------------------
# Properties from inputs
# -----------------------------------------------------------------------------
velocity_PbLi = '${units 1.78 m/s}'
hydraulic_diameter = '${units ${fparse 2.0*radius_inner_wall} m}'
flow_area = '${units ${fparse pi*radius_inner_wall^2} m^2}'
volumetric_flow_rate_PbLi = '${units ${fparse velocity_PbLi*flow_area} m^3/s}'
kinematic_viscosity_PbLi = '${units ${fparse velocity_PbLi*hydraulic_diameter/reynolds_number} m^2/s}'
schmidt_number = ${fparse kinematic_viscosity_PbLi/diffusivity_PbLi}

# -----------------------------------------------------------------------------
# PbLi mass transfer from Sherwood correlations
# -----------------------------------------------------------------------------
#   sherwood_number  = 0.023 reynolds_number^0.83 schmidt_number^(1/3)
#   mass_transfer_coefficient_PbLi = sherwood_number diffusivity_PbLi / (2 radius_inner_wall)
sherwood_number = ${fparse 0.023*reynolds_number^0.83*schmidt_number^(1.0/3.0)}
mass_transfer_coefficient_PbLi = '${units ${fparse sherwood_number*diffusivity_PbLi/hydraulic_diameter} m/s}'

# -----------------------------------------------------------------------------
# Radial equations
# -----------------------------------------------------------------------------
#
# Liquid flux on the inner area:
#   J_i = mass_transfer_coefficient_PbLi * (C_bulk - C_L2)
#
# Interface partition:
#   C_S1 = partition_ratio * C_L2
#
# Cylindrical diffusion expressed on the inner area:
#   J_i = diffusivity_vanadium * (C_S1 - C_S2)
#         / (radius_inner_wall * ln(radius_outer_wall/radius_inner_wall))
#
# Recombination occurs on the outer vacuum surface:
#   J_o = recombination_coefficient * C_S2^2
#
# Conservation of permeation rate requires
#   2*pi*radius_inner_wall*J_i = 2*pi*radius_outer_wall*J_o,
#
# so the equivalent recombination flux on the inner area is
#   J_i = recombination_coefficient_inner_area * C_S2^2.
#
# Define
#   partition_ratio = solubility_vanadium / solubility_PbLi
#   membrane_resistance = radius_inner_wall
#                         * ln(radius_outer_wall/radius_inner_wall)
#                         / diffusivity_vanadium
#   radial_transport_coefficient =
#       partition_ratio / mass_transfer_coefficient_PbLi
#       + membrane_resistance
#
# Then the physical positive root is
#   C_S2(C) = 2*partition_ratio*C
#             / [1 + sqrt(1 + 4*radial_transport_coefficient
#             * recombination_coefficient_inner_area
#             * partition_ratio*C)].

partition_ratio = ${fparse solubility_vanadium/solubility_PbLi}
membrane_resistance = '${units ${fparse radius_inner_wall*log(radius_outer_wall/radius_inner_wall)/diffusivity_vanadium} s/m}'
radial_transport_coefficient = '${units ${fparse partition_ratio/mass_transfer_coefficient_PbLi+membrane_resistance} s/m}'

# -----------------------------------------------------------------------------
# Control volumes (axial direction)
# -----------------------------------------------------------------------------

axial_segment_length = '${units ${fparse tube_length/number_axial_segments} m}'
segment_permeation_area = '${units ${fparse 2.0*pi*radius_inner_wall*axial_segment_length} m^2}'
total_permeation_area = '${units ${fparse 2.0*pi*radius_inner_wall*tube_length} m^2}'
segment_area_to_flow_ratio = '${units ${fparse segment_permeation_area/volumetric_flow_rate_PbLi} s/m}'

# -----------------------------------------------------------------------------
# Pressure drop
# -----------------------------------------------------------------------------

darcy_friction_factor = ${fparse 0.3164/(reynolds_number^0.25)}
pressure_drop_straight = '${units ${fparse darcy_friction_factor*(tube_length/hydraulic_diameter)*density_PbLi*velocity_PbLi^2/2.0} Pa}'

# -----------------------------------------------------------------------------
# Mesh (Needed just to run the model)
# -----------------------------------------------------------------------------

[Mesh]
  type = GeneratedMesh
  dim = 1
  nx = 1
[]

# -----------------------------------------------------------------------------
# Unknowns (concentrations at the axial direction)
# -----------------------------------------------------------------------------

# concentration_segment_01 is the concentration at z = 0.25 m, ...,
# concentration_segment_20 is the concentration at z = 5.00 m.
[Variables]
  [concentration_segment_01]
    family = SCALAR
    initial_condition = ${concentration_inlet}
  []

  [concentration_segment_02]
    family = SCALAR
    initial_condition = ${concentration_inlet}
  []

  [concentration_segment_03]
    family = SCALAR
    initial_condition = ${concentration_inlet}
  []

  [concentration_segment_04]
    family = SCALAR
    initial_condition = ${concentration_inlet}
  []

  [concentration_segment_05]
    family = SCALAR
    initial_condition = ${concentration_inlet}
  []

  [concentration_segment_06]
    family = SCALAR
    initial_condition = ${concentration_inlet}
  []

  [concentration_segment_07]
    family = SCALAR
    initial_condition = ${concentration_inlet}
  []

  [concentration_segment_08]
    family = SCALAR
    initial_condition = ${concentration_inlet}
  []

  [concentration_segment_09]
    family = SCALAR
    initial_condition = ${concentration_inlet}
  []

  [concentration_segment_10]
    family = SCALAR
    initial_condition = ${concentration_inlet}
  []

  [concentration_segment_11]
    family = SCALAR
    initial_condition = ${concentration_inlet}
  []

  [concentration_segment_12]
    family = SCALAR
    initial_condition = ${concentration_inlet}
  []

  [concentration_segment_13]
    family = SCALAR
    initial_condition = ${concentration_inlet}
  []

  [concentration_segment_14]
    family = SCALAR
    initial_condition = ${concentration_inlet}
  []

  [concentration_segment_15]
    family = SCALAR
    initial_condition = ${concentration_inlet}
  []

  [concentration_segment_16]
    family = SCALAR
    initial_condition = ${concentration_inlet}
  []

  [concentration_segment_17]
    family = SCALAR
    initial_condition = ${concentration_inlet}
  []

  [concentration_segment_18]
    family = SCALAR
    initial_condition = ${concentration_inlet}
  []

  [concentration_segment_19]
    family = SCALAR
    initial_condition = ${concentration_inlet}
  []

  [concentration_segment_20]
    family = SCALAR
    initial_condition = ${concentration_inlet}
  []
[]

# -----------------------------------------------------------------------------
# Steady state mass balance
# -----------------------------------------------------------------------------

# For each segment i:
#   volumetric_flow_rate_PbLi*C_up = volumetric_flow_rate_PbLi*C_down
#                                   + J(C_up)*segment_permeation_area
# or
#   C_down - C_up + segment_area_to_flow_ratio*J(C_up) = 0
#
# The radial flux J(C_up) is evaluated using the local upstream concentration.
[ScalarKernels]
  [segment_01]
    type = ParsedODEKernel
    variable = concentration_segment_01
    expression = 'concentration_segment_01 - concentration_upstream + segment_area_to_flow_ratio*recombination_coefficient_inner_area*(2.0*partition_ratio_local*concentration_upstream/(1.0+sqrt(1.0+4.0*radial_transport_coefficient_local*recombination_coefficient_inner_area*partition_ratio_local*concentration_upstream)))^2'
    constant_names = 'concentration_upstream segment_area_to_flow_ratio recombination_coefficient_inner_area partition_ratio_local radial_transport_coefficient_local'
    constant_expressions = '${concentration_inlet} ${segment_area_to_flow_ratio} ${recombination_coefficient_inner_area} ${partition_ratio} ${radial_transport_coefficient}'
    evalerror_behavior = error
  []

  [segment_02]
    type = ParsedODEKernel
    variable = concentration_segment_02
    coupled_variables = 'concentration_segment_01'
    expression = 'concentration_segment_02 - concentration_segment_01 + segment_area_to_flow_ratio*recombination_coefficient_inner_area*(2.0*partition_ratio_local*concentration_segment_01/(1.0+sqrt(1.0+4.0*radial_transport_coefficient_local*recombination_coefficient_inner_area*partition_ratio_local*concentration_segment_01)))^2'
    constant_names = 'segment_area_to_flow_ratio recombination_coefficient_inner_area partition_ratio_local radial_transport_coefficient_local'
    constant_expressions = '${segment_area_to_flow_ratio} ${recombination_coefficient_inner_area} ${partition_ratio} ${radial_transport_coefficient}'
    evalerror_behavior = error
  []

  [segment_03]
    type = ParsedODEKernel
    variable = concentration_segment_03
    coupled_variables = 'concentration_segment_02'
    expression = 'concentration_segment_03 - concentration_segment_02 + segment_area_to_flow_ratio*recombination_coefficient_inner_area*(2.0*partition_ratio_local*concentration_segment_02/(1.0+sqrt(1.0+4.0*radial_transport_coefficient_local*recombination_coefficient_inner_area*partition_ratio_local*concentration_segment_02)))^2'
    constant_names = 'segment_area_to_flow_ratio recombination_coefficient_inner_area partition_ratio_local radial_transport_coefficient_local'
    constant_expressions = '${segment_area_to_flow_ratio} ${recombination_coefficient_inner_area} ${partition_ratio} ${radial_transport_coefficient}'
    evalerror_behavior = error
  []

  [segment_04]
    type = ParsedODEKernel
    variable = concentration_segment_04
    coupled_variables = 'concentration_segment_03'
    expression = 'concentration_segment_04 - concentration_segment_03 + segment_area_to_flow_ratio*recombination_coefficient_inner_area*(2.0*partition_ratio_local*concentration_segment_03/(1.0+sqrt(1.0+4.0*radial_transport_coefficient_local*recombination_coefficient_inner_area*partition_ratio_local*concentration_segment_03)))^2'
    constant_names = 'segment_area_to_flow_ratio recombination_coefficient_inner_area partition_ratio_local radial_transport_coefficient_local'
    constant_expressions = '${segment_area_to_flow_ratio} ${recombination_coefficient_inner_area} ${partition_ratio} ${radial_transport_coefficient}'
    evalerror_behavior = error
  []

  [segment_05]
    type = ParsedODEKernel
    variable = concentration_segment_05
    coupled_variables = 'concentration_segment_04'
    expression = 'concentration_segment_05 - concentration_segment_04 + segment_area_to_flow_ratio*recombination_coefficient_inner_area*(2.0*partition_ratio_local*concentration_segment_04/(1.0+sqrt(1.0+4.0*radial_transport_coefficient_local*recombination_coefficient_inner_area*partition_ratio_local*concentration_segment_04)))^2'
    constant_names = 'segment_area_to_flow_ratio recombination_coefficient_inner_area partition_ratio_local radial_transport_coefficient_local'
    constant_expressions = '${segment_area_to_flow_ratio} ${recombination_coefficient_inner_area} ${partition_ratio} ${radial_transport_coefficient}'
    evalerror_behavior = error
  []

  [segment_06]
    type = ParsedODEKernel
    variable = concentration_segment_06
    coupled_variables = 'concentration_segment_05'
    expression = 'concentration_segment_06 - concentration_segment_05 + segment_area_to_flow_ratio*recombination_coefficient_inner_area*(2.0*partition_ratio_local*concentration_segment_05/(1.0+sqrt(1.0+4.0*radial_transport_coefficient_local*recombination_coefficient_inner_area*partition_ratio_local*concentration_segment_05)))^2'
    constant_names = 'segment_area_to_flow_ratio recombination_coefficient_inner_area partition_ratio_local radial_transport_coefficient_local'
    constant_expressions = '${segment_area_to_flow_ratio} ${recombination_coefficient_inner_area} ${partition_ratio} ${radial_transport_coefficient}'
    evalerror_behavior = error
  []

  [segment_07]
    type = ParsedODEKernel
    variable = concentration_segment_07
    coupled_variables = 'concentration_segment_06'
    expression = 'concentration_segment_07 - concentration_segment_06 + segment_area_to_flow_ratio*recombination_coefficient_inner_area*(2.0*partition_ratio_local*concentration_segment_06/(1.0+sqrt(1.0+4.0*radial_transport_coefficient_local*recombination_coefficient_inner_area*partition_ratio_local*concentration_segment_06)))^2'
    constant_names = 'segment_area_to_flow_ratio recombination_coefficient_inner_area partition_ratio_local radial_transport_coefficient_local'
    constant_expressions = '${segment_area_to_flow_ratio} ${recombination_coefficient_inner_area} ${partition_ratio} ${radial_transport_coefficient}'
    evalerror_behavior = error
  []

  [segment_08]
    type = ParsedODEKernel
    variable = concentration_segment_08
    coupled_variables = 'concentration_segment_07'
    expression = 'concentration_segment_08 - concentration_segment_07 + segment_area_to_flow_ratio*recombination_coefficient_inner_area*(2.0*partition_ratio_local*concentration_segment_07/(1.0+sqrt(1.0+4.0*radial_transport_coefficient_local*recombination_coefficient_inner_area*partition_ratio_local*concentration_segment_07)))^2'
    constant_names = 'segment_area_to_flow_ratio recombination_coefficient_inner_area partition_ratio_local radial_transport_coefficient_local'
    constant_expressions = '${segment_area_to_flow_ratio} ${recombination_coefficient_inner_area} ${partition_ratio} ${radial_transport_coefficient}'
    evalerror_behavior = error
  []

  [segment_09]
    type = ParsedODEKernel
    variable = concentration_segment_09
    coupled_variables = 'concentration_segment_08'
    expression = 'concentration_segment_09 - concentration_segment_08 + segment_area_to_flow_ratio*recombination_coefficient_inner_area*(2.0*partition_ratio_local*concentration_segment_08/(1.0+sqrt(1.0+4.0*radial_transport_coefficient_local*recombination_coefficient_inner_area*partition_ratio_local*concentration_segment_08)))^2'
    constant_names = 'segment_area_to_flow_ratio recombination_coefficient_inner_area partition_ratio_local radial_transport_coefficient_local'
    constant_expressions = '${segment_area_to_flow_ratio} ${recombination_coefficient_inner_area} ${partition_ratio} ${radial_transport_coefficient}'
    evalerror_behavior = error
  []

  [segment_10]
    type = ParsedODEKernel
    variable = concentration_segment_10
    coupled_variables = 'concentration_segment_09'
    expression = 'concentration_segment_10 - concentration_segment_09 + segment_area_to_flow_ratio*recombination_coefficient_inner_area*(2.0*partition_ratio_local*concentration_segment_09/(1.0+sqrt(1.0+4.0*radial_transport_coefficient_local*recombination_coefficient_inner_area*partition_ratio_local*concentration_segment_09)))^2'
    constant_names = 'segment_area_to_flow_ratio recombination_coefficient_inner_area partition_ratio_local radial_transport_coefficient_local'
    constant_expressions = '${segment_area_to_flow_ratio} ${recombination_coefficient_inner_area} ${partition_ratio} ${radial_transport_coefficient}'
    evalerror_behavior = error
  []

  [segment_11]
    type = ParsedODEKernel
    variable = concentration_segment_11
    coupled_variables = 'concentration_segment_10'
    expression = 'concentration_segment_11 - concentration_segment_10 + segment_area_to_flow_ratio*recombination_coefficient_inner_area*(2.0*partition_ratio_local*concentration_segment_10/(1.0+sqrt(1.0+4.0*radial_transport_coefficient_local*recombination_coefficient_inner_area*partition_ratio_local*concentration_segment_10)))^2'
    constant_names = 'segment_area_to_flow_ratio recombination_coefficient_inner_area partition_ratio_local radial_transport_coefficient_local'
    constant_expressions = '${segment_area_to_flow_ratio} ${recombination_coefficient_inner_area} ${partition_ratio} ${radial_transport_coefficient}'
    evalerror_behavior = error
  []

  [segment_12]
    type = ParsedODEKernel
    variable = concentration_segment_12
    coupled_variables = 'concentration_segment_11'
    expression = 'concentration_segment_12 - concentration_segment_11 + segment_area_to_flow_ratio*recombination_coefficient_inner_area*(2.0*partition_ratio_local*concentration_segment_11/(1.0+sqrt(1.0+4.0*radial_transport_coefficient_local*recombination_coefficient_inner_area*partition_ratio_local*concentration_segment_11)))^2'
    constant_names = 'segment_area_to_flow_ratio recombination_coefficient_inner_area partition_ratio_local radial_transport_coefficient_local'
    constant_expressions = '${segment_area_to_flow_ratio} ${recombination_coefficient_inner_area} ${partition_ratio} ${radial_transport_coefficient}'
    evalerror_behavior = error
  []

  [segment_13]
    type = ParsedODEKernel
    variable = concentration_segment_13
    coupled_variables = 'concentration_segment_12'
    expression = 'concentration_segment_13 - concentration_segment_12 + segment_area_to_flow_ratio*recombination_coefficient_inner_area*(2.0*partition_ratio_local*concentration_segment_12/(1.0+sqrt(1.0+4.0*radial_transport_coefficient_local*recombination_coefficient_inner_area*partition_ratio_local*concentration_segment_12)))^2'
    constant_names = 'segment_area_to_flow_ratio recombination_coefficient_inner_area partition_ratio_local radial_transport_coefficient_local'
    constant_expressions = '${segment_area_to_flow_ratio} ${recombination_coefficient_inner_area} ${partition_ratio} ${radial_transport_coefficient}'
    evalerror_behavior = error
  []

  [segment_14]
    type = ParsedODEKernel
    variable = concentration_segment_14
    coupled_variables = 'concentration_segment_13'
    expression = 'concentration_segment_14 - concentration_segment_13 + segment_area_to_flow_ratio*recombination_coefficient_inner_area*(2.0*partition_ratio_local*concentration_segment_13/(1.0+sqrt(1.0+4.0*radial_transport_coefficient_local*recombination_coefficient_inner_area*partition_ratio_local*concentration_segment_13)))^2'
    constant_names = 'segment_area_to_flow_ratio recombination_coefficient_inner_area partition_ratio_local radial_transport_coefficient_local'
    constant_expressions = '${segment_area_to_flow_ratio} ${recombination_coefficient_inner_area} ${partition_ratio} ${radial_transport_coefficient}'
    evalerror_behavior = error
  []

  [segment_15]
    type = ParsedODEKernel
    variable = concentration_segment_15
    coupled_variables = 'concentration_segment_14'
    expression = 'concentration_segment_15 - concentration_segment_14 + segment_area_to_flow_ratio*recombination_coefficient_inner_area*(2.0*partition_ratio_local*concentration_segment_14/(1.0+sqrt(1.0+4.0*radial_transport_coefficient_local*recombination_coefficient_inner_area*partition_ratio_local*concentration_segment_14)))^2'
    constant_names = 'segment_area_to_flow_ratio recombination_coefficient_inner_area partition_ratio_local radial_transport_coefficient_local'
    constant_expressions = '${segment_area_to_flow_ratio} ${recombination_coefficient_inner_area} ${partition_ratio} ${radial_transport_coefficient}'
    evalerror_behavior = error
  []

  [segment_16]
    type = ParsedODEKernel
    variable = concentration_segment_16
    coupled_variables = 'concentration_segment_15'
    expression = 'concentration_segment_16 - concentration_segment_15 + segment_area_to_flow_ratio*recombination_coefficient_inner_area*(2.0*partition_ratio_local*concentration_segment_15/(1.0+sqrt(1.0+4.0*radial_transport_coefficient_local*recombination_coefficient_inner_area*partition_ratio_local*concentration_segment_15)))^2'
    constant_names = 'segment_area_to_flow_ratio recombination_coefficient_inner_area partition_ratio_local radial_transport_coefficient_local'
    constant_expressions = '${segment_area_to_flow_ratio} ${recombination_coefficient_inner_area} ${partition_ratio} ${radial_transport_coefficient}'
    evalerror_behavior = error
  []

  [segment_17]
    type = ParsedODEKernel
    variable = concentration_segment_17
    coupled_variables = 'concentration_segment_16'
    expression = 'concentration_segment_17 - concentration_segment_16 + segment_area_to_flow_ratio*recombination_coefficient_inner_area*(2.0*partition_ratio_local*concentration_segment_16/(1.0+sqrt(1.0+4.0*radial_transport_coefficient_local*recombination_coefficient_inner_area*partition_ratio_local*concentration_segment_16)))^2'
    constant_names = 'segment_area_to_flow_ratio recombination_coefficient_inner_area partition_ratio_local radial_transport_coefficient_local'
    constant_expressions = '${segment_area_to_flow_ratio} ${recombination_coefficient_inner_area} ${partition_ratio} ${radial_transport_coefficient}'
    evalerror_behavior = error
  []

  [segment_18]
    type = ParsedODEKernel
    variable = concentration_segment_18
    coupled_variables = 'concentration_segment_17'
    expression = 'concentration_segment_18 - concentration_segment_17 + segment_area_to_flow_ratio*recombination_coefficient_inner_area*(2.0*partition_ratio_local*concentration_segment_17/(1.0+sqrt(1.0+4.0*radial_transport_coefficient_local*recombination_coefficient_inner_area*partition_ratio_local*concentration_segment_17)))^2'
    constant_names = 'segment_area_to_flow_ratio recombination_coefficient_inner_area partition_ratio_local radial_transport_coefficient_local'
    constant_expressions = '${segment_area_to_flow_ratio} ${recombination_coefficient_inner_area} ${partition_ratio} ${radial_transport_coefficient}'
    evalerror_behavior = error
  []

  [segment_19]
    type = ParsedODEKernel
    variable = concentration_segment_19
    coupled_variables = 'concentration_segment_18'
    expression = 'concentration_segment_19 - concentration_segment_18 + segment_area_to_flow_ratio*recombination_coefficient_inner_area*(2.0*partition_ratio_local*concentration_segment_18/(1.0+sqrt(1.0+4.0*radial_transport_coefficient_local*recombination_coefficient_inner_area*partition_ratio_local*concentration_segment_18)))^2'
    constant_names = 'segment_area_to_flow_ratio recombination_coefficient_inner_area partition_ratio_local radial_transport_coefficient_local'
    constant_expressions = '${segment_area_to_flow_ratio} ${recombination_coefficient_inner_area} ${partition_ratio} ${radial_transport_coefficient}'
    evalerror_behavior = error
  []

  [segment_20]
    type = ParsedODEKernel
    variable = concentration_segment_20
    coupled_variables = 'concentration_segment_19'
    expression = 'concentration_segment_20 - concentration_segment_19 + segment_area_to_flow_ratio*recombination_coefficient_inner_area*(2.0*partition_ratio_local*concentration_segment_19/(1.0+sqrt(1.0+4.0*radial_transport_coefficient_local*recombination_coefficient_inner_area*partition_ratio_local*concentration_segment_19)))^2'
    constant_names = 'segment_area_to_flow_ratio recombination_coefficient_inner_area partition_ratio_local radial_transport_coefficient_local'
    constant_expressions = '${segment_area_to_flow_ratio} ${recombination_coefficient_inner_area} ${partition_ratio} ${radial_transport_coefficient}'
    evalerror_behavior = error
  []
[]

# -----------------------------------------------------------------------------
# Postprocessor
# -----------------------------------------------------------------------------

[Postprocessors]
  [concentration_inlet_pp]
    type = ConstantPostprocessor
    value = ${concentration_inlet}
    execute_on = 'initial timestep_end'
  []

  [concentration_segment_01_pp]
    type = ScalarVariable
    variable = concentration_segment_01
    execute_on = 'initial timestep_end'
  []

  [concentration_segment_02_pp]
    type = ScalarVariable
    variable = concentration_segment_02
    execute_on = 'initial timestep_end'
  []

  [concentration_segment_03_pp]
    type = ScalarVariable
    variable = concentration_segment_03
    execute_on = 'initial timestep_end'
  []

  [concentration_segment_04_pp]
    type = ScalarVariable
    variable = concentration_segment_04
    execute_on = 'initial timestep_end'
  []

  [concentration_segment_05_pp]
    type = ScalarVariable
    variable = concentration_segment_05
    execute_on = 'initial timestep_end'
  []

  [concentration_segment_06_pp]
    type = ScalarVariable
    variable = concentration_segment_06
    execute_on = 'initial timestep_end'
  []

  [concentration_segment_07_pp]
    type = ScalarVariable
    variable = concentration_segment_07
    execute_on = 'initial timestep_end'
  []

  [concentration_segment_08_pp]
    type = ScalarVariable
    variable = concentration_segment_08
    execute_on = 'initial timestep_end'
  []

  [concentration_segment_09_pp]
    type = ScalarVariable
    variable = concentration_segment_09
    execute_on = 'initial timestep_end'
  []

  [concentration_segment_10_pp]
    type = ScalarVariable
    variable = concentration_segment_10
    execute_on = 'initial timestep_end'
  []

  [concentration_segment_11_pp]
    type = ScalarVariable
    variable = concentration_segment_11
    execute_on = 'initial timestep_end'
  []

  [concentration_segment_12_pp]
    type = ScalarVariable
    variable = concentration_segment_12
    execute_on = 'initial timestep_end'
  []

  [concentration_segment_13_pp]
    type = ScalarVariable
    variable = concentration_segment_13
    execute_on = 'initial timestep_end'
  []

  [concentration_segment_14_pp]
    type = ScalarVariable
    variable = concentration_segment_14
    execute_on = 'initial timestep_end'
  []

  [concentration_segment_15_pp]
    type = ScalarVariable
    variable = concentration_segment_15
    execute_on = 'initial timestep_end'
  []

  [concentration_segment_16_pp]
    type = ScalarVariable
    variable = concentration_segment_16
    execute_on = 'initial timestep_end'
  []

  [concentration_segment_17_pp]
    type = ScalarVariable
    variable = concentration_segment_17
    execute_on = 'initial timestep_end'
  []

  [concentration_segment_18_pp]
    type = ScalarVariable
    variable = concentration_segment_18
    execute_on = 'initial timestep_end'
  []

  [concentration_segment_19_pp]
    type = ScalarVariable
    variable = concentration_segment_19
    execute_on = 'initial timestep_end'
  []

  [concentration_segment_20_pp]
    type = ScalarVariable
    variable = concentration_segment_20
    execute_on = 'initial timestep_end'
  []

  [pressure_drop_straight_Pa]
    type = ConstantPostprocessor
    value = ${pressure_drop_straight}
    execute_on = 'initial timestep_end'
  []

  [extraction_efficiency]
    type = ParsedPostprocessor
    expression = '1.0-concentration_outlet/concentration_inlet_local'
    pp_names = 'concentration_segment_20_pp'
    pp_symbols = 'concentration_outlet'
    constant_names = 'concentration_inlet_local'
    constant_expressions = '${concentration_inlet}'
    execute_on = 'timestep_end'
  []

  [average_permeation_flux_mol_m2_s]
    type = ParsedPostprocessor
    expression = 'volumetric_flow_rate*(concentration_inlet_local-concentration_outlet)/permeation_area'
    pp_names = 'concentration_segment_20_pp'
    pp_symbols = 'concentration_outlet'
    constant_names = 'volumetric_flow_rate concentration_inlet_local permeation_area'
    constant_expressions = '${volumetric_flow_rate_PbLi} ${concentration_inlet} ${total_permeation_area}'
    execute_on = 'timestep_end'
  []
[]

[Executioner]
  type = Steady
  solve_type = NEWTON
  nl_abs_tol = 1e-25
  nl_rel_tol = 1e-8
  nl_max_its = 100
[]

[Outputs]
  console = true

  [csv]
    type = CSV
    file_base = ver-1p_out
    precision = 16
    scientific_notation = true
  []
[]
