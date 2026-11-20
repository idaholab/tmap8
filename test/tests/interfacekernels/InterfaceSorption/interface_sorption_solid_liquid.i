# This test verifies the inverted formulation of InterfaceSorption (use_inverted_sorption = true)
# for a Sieverts' law (n = 1/2) interface between a solid and a liquid when the concentration of
# the dissolved species in the liquid is very small.
#
# A solid (x < 0.01 m) is in contact with a liquid (x > 0.01 m). The liquid is a source of
# molecular species Q2, which is absorbed in the solid as atoms Q. The solid is a strong sink
# (large solubility), so the concentration of Q2 at the interface is orders of magnitude below 1.
# With the default formulation, the square root of the interface concentration in the liquid
# makes the interface condition flat (because of the small floor applied to concentrations) when
# the concentration is negative or tiny, and singular otherwise. The solve then stalls with
# vanishing time steps once the liquid concentration at the interface becomes positive.
# This case is based on a discussion forum report (UKAEA, solid-liquid interface).
#
# Two checks are reported at the end of the simulation:
# - mass_balance_ratio: the atoms inventory over the atoms injected by the liquid source (= 1)
# - sorption_ratio: the interface concentration in the solid over the value from Sieverts' law
#   evaluated with the interface concentration in the liquid (= 1)
#
# Units: SI (m, s, K, mol). Concentrations are in mol/m^3 and pressures in Pa.

temperature = 773 # K
solubility = 10 # mol(Q) m^-3 Pa^-0.5
n_sorption = 0.5
source = 1e-11 # mol(Q2) m^-3 s^-1 in the liquid
liquid_length = 0.09 # m
R = 8.31446261815324 # J/mol/K, based on number used in include/utils/PhysicalConstants.h

[Mesh]
  # The mesh is refined toward the interface, where the concentration gradients are the largest
  [solid_mesh]
    type = GeneratedMeshGenerator
    dim = 1
    nx = 50
    xmin = 0
    xmax = 0.01
    bias_x = 0.8
  []
  [liquid_mesh_1]
    type = GeneratedMeshGenerator
    dim = 1
    nx = 50
    xmin = 0.01
    xmax = 0.02
    bias_x = 1.25
  []
  [liquid_mesh_2]
    type = GeneratedMeshGenerator
    dim = 1
    nx = 20
    xmin = 0.02
    xmax = 0.1
  []
  [stitched]
    type = StitchMeshGenerator
    inputs = 'solid_mesh liquid_mesh_1 liquid_mesh_2'
    stitch_boundaries_pairs = 'right left; right left'
    prevent_boundary_ids_overlap = false
  []
  [solid_block]
    type = SubdomainBoundingBoxGenerator
    input = stitched
    bottom_left = '0 0 0'
    top_right = '0.01 1 1'
    block_id = 1
    block_name = solid
  []
  [liquid_block]
    type = SubdomainBoundingBoxGenerator
    input = solid_block
    bottom_left = '0.01 0 0'
    top_right = '0.1 1 1'
    block_id = 2
    block_name = liquid
  []
  [interface]
    type = SideSetsBetweenSubdomainsGenerator
    input = liquid_block
    new_boundary = sl_interface
    primary_block = solid
    paired_block = liquid
  []
[]

[Variables]
  [C_Qsol] # atomic concentration in the solid
    block = solid
    initial_condition = 0
  []
  [C_Q2liq] # molecular concentration in the liquid
    block = liquid
    initial_condition = 0
  []
[]

[AuxVariables]
  [T_abs]
    initial_condition = ${temperature}
  []
[]

[Kernels]
  [C_Qsol_dt]
    type = ADTimeDerivative
    variable = C_Qsol
    block = solid
  []
  [C_Qsol_diffusion]
    type = ADMatDiffusion
    variable = C_Qsol
    block = solid
    diffusivity = diff
  []
  [C_Q2liq_dt]
    type = ADTimeDerivative
    variable = C_Q2liq
    block = liquid
  []
  [C_Q2liq_diffusion]
    type = ADMatDiffusion
    variable = C_Q2liq
    block = liquid
    diffusivity = diff
  []
  [C_Q2liq_source]
    type = ADBodyForce
    variable = C_Q2liq
    block = liquid
    value = ${source}
  []
[]

[InterfaceKernels]
  [sl_InterfaceSorption]
    type = ADInterfaceSorption
    variable = C_Qsol
    neighbor_var = C_Q2liq
    boundary = sl_interface
    K0 = ${solubility}
    Ea = 0
    n_sorption = ${n_sorption}
    temperature = T_abs
    diffusivity = diff
    use_flux_penalty = true
    flux_penalty = 1
    sorption_penalty = 1
    use_inverted_sorption = true
  []
[]

[Materials]
  [solid_diffusivity]
    type = ADConstantMaterial
    block = solid
    property_name = diff
    value = 1e-10 # m^2/s
  []
  [liquid_diffusivity]
    type = ADConstantMaterial
    block = liquid
    property_name = diff
    value = 1e-9 # m^2/s
  []
[]

[Preconditioning]
  [smp]
    type = SMP
    full = true
  []
[]

[Executioner]
  type = Transient
  solve_type = NEWTON
  petsc_options_iname = '-pc_type -pc_factor_mat_solver_package'
  petsc_options_value = 'lu superlu_dist'
  nl_abs_tol = 1e-12
  nl_rel_tol = 1e-8
  automatic_scaling = true
  compute_scaling_once = false
  line_search = none
  end_time = 3000 # s, the stall in the default formulation occurs at about 1200 s
  dtmax = 100
  [TimeStepper]
    type = IterationAdaptiveDT
    dt = 1
    optimal_iterations = 10
    iteration_window = 3
    linear_iteration_ratio = 10
    growth_factor = 1.25
    cutback_factor = 0.8
  []
[]

[Postprocessors]
  [inventory_solid]
    type = ElementIntegralVariablePostprocessor
    variable = C_Qsol
    block = solid
    execute_on = 'INITIAL TIMESTEP_END'
    outputs = none
  []
  [inventory_liquid]
    type = ElementIntegralVariablePostprocessor
    variable = C_Q2liq
    block = liquid
    execute_on = 'INITIAL TIMESTEP_END'
    outputs = none
  []
  [C_solid_interface]
    type = NodalExtremeValue
    variable = C_Qsol
    boundary = sl_interface
    value_type = max
    execute_on = 'INITIAL TIMESTEP_END'
    outputs = none
  []
  [C_liquid_interface]
    type = NodalExtremeValue
    variable = C_Q2liq
    boundary = sl_interface
    value_type = max
    execute_on = 'INITIAL TIMESTEP_END'
    outputs = none
  []
  [mass_balance_ratio]
    type = ParsedPostprocessor
    pp_names = 'inventory_solid inventory_liquid'
    expression = '(inventory_solid + 2 * inventory_liquid) / (2 * ${source} * ${liquid_length} * t)'
    use_t = true
    execute_on = FINAL
  []
  [sorption_ratio]
    type = ParsedPostprocessor
    pp_names = 'C_solid_interface C_liquid_interface'
    expression = 'C_solid_interface / (${solubility} * sqrt(${R} * ${temperature} * C_liquid_interface))'
    execute_on = FINAL
  []
[]

[Outputs]
  file_base = interface_sorption_solid_liquid_out
  [csv]
    type = CSV
    execute_on = FINAL
  []
[]
