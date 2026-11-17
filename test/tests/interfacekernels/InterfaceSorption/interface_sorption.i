# This test is to verify the implementation of InterfaceSorption and its AD counterpart.
# It contains two 1D blocks separated by a continuous interface.
# InterfaceSorption is used to enforce the sorption law and preserve flux between the blocks.
# Checks are performed to verify concentration conservation, sorption behavior, and flux preservation.
# This input file uses BreakMeshByBlockGenerator, which is currently only supported for replicated
# meshes, so this file should not be run with the `parallel_type = DISTRIBUTED` flag

# In this input file, we apply the Sievert law with n_sorption=1/2.

# Physical Constants
R = 8.31446261815324 # J/mol/K, based on number used in TMAP8PhysicalConstants.h

solubility = 1.e-2
n_sorption = 0.5

unit_scale = 1
unit_scale_neighbor = 1


[GlobalParams]
  order = FIRST
  family = LAGRANGE
[]

[Mesh]
  [gen]
    type = GeneratedMeshGenerator
    nx = 10
    dim = 1
  []
  [block1]
    type = SubdomainBoundingBoxGenerator
    input = gen
    block_id = 1
    bottom_left = '0 0 0'
    top_right = '0.5 1 0'
  []
  [block2]
    type = SubdomainBoundingBoxGenerator
    input = block1
    block_id = 2
    bottom_left = '0.5 0 0'
    top_right = '1 1 0'
  []
  [interface]
    type = SideSetsBetweenSubdomainsGenerator
    input = block2
    primary_block = 1
    paired_block = 2
    new_boundary = interface
  []
  [interface2]
    type = SideSetsBetweenSubdomainsGenerator
    input = interface
    primary_block = 2
    paired_block = 1
    new_boundary = interface2
  []
[]

[Variables]
  [u1]
    block = 1
  []
  [u2]
    block = 2
  []
  [temperature]
  []
[]

[Kernels]
  [u1]
    type = MatDiffusion
    variable = u1
    diffusivity = diffusivity
    block = 1
  []
  [u2]
    type = MatDiffusion
    variable = u2
    diffusivity = diffusivity
    block = 2
  []
  [temperature]
    type = HeatConduction
    variable = temperature
  []
[]

[BCs]
  [left_u1]
    type = DirichletBC
    value = 1
    variable = u1
    boundary = left
  []
  [right_u2]
    type = DirichletBC
    value = 1
    variable = u2
    boundary = right
  []
  [left_temperature]
    type = DirichletBC
    value = 1100
    variable = temperature
    boundary = left
  []
  [right_temperature]
    type = DirichletBC
    value = 0
    variable = temperature
    boundary = right
  []
  [block1_2_temperature]
    type = DirichletBC
    value = 1000
    variable = temperature
    boundary = interface
  []
  [block2_1_temperature]
    type = DirichletBC
    value = 900
    variable = temperature
    boundary = interface2
  []
[]

[InterfaceKernels]
  [interface]
    type = InterfaceSorption
    K0 = ${solubility}
    Ea = 0
    n_sorption = ${n_sorption}
    diffusivity = diffusivity
    unit_scale = ${unit_scale}
    unit_scale_neighbor = ${unit_scale_neighbor}
    temperature = temperature
    variable = u2
    neighbor_var = u1
    sorption_penalty = 1e1
    boundary = interface2
  []
[]

[Materials]
  [properties_1]
    type = GenericConstantMaterial
    prop_names = 'thermal_conductivity diffusivity'
    prop_values = '1 1'
    block = 1
  []
  [properties_2]
    type = GenericConstantMaterial
    prop_names = 'thermal_conductivity diffusivity solubility'
    prop_values = '2 2 ${solubility}'
    block = 2
  []
[]

[Functions]
  [u_mid_diff]
    type = ParsedFunction
    symbol_names = 'u_mid_inner u_mid_outer'
    symbol_values = 'u_mid_inner u_mid_outer'
    expression = '(abs(u_mid_outer) - abs(u_mid_inner)) / abs(u_mid_inner)'
  []
  [residual_concentration]
    type = ParsedFunction
    symbol_names = 'u_mid_inner u_mid_outer T'
    symbol_values = 'u_mid_inner u_mid_outer temperature_mid_inner'
    expression = 'u_mid_outer*${unit_scale} - ${solubility}*(u_mid_inner*${unit_scale_neighbor}*${R}*T)^${n_sorption}'
  []
  [flux_error]
    type = ParsedFunction
    symbol_names = 'flux_inner flux_outer'
    symbol_values = 'flux_inner flux_outer'
    expression = '(abs(flux_outer) - abs(flux_inner)) / abs(flux_inner)'
  []
[]

[Preconditioning]
  [smp]
    type = SMP
    full = true
  []
[]

[Executioner]
  type = Steady
  solve_type = NEWTON

  petsc_options_iname = '-pc_type -pc_factor_mat_solver_package'
  petsc_options_value = 'lu superlu_dist'
  line_search = none

  nl_rel_tol = 1e-15
  nl_abs_tol = 1e-9
  l_tol = 1e-3
[]

[Postprocessors]
  [u_mid_inner]
    type = PointValue
    variable = u1
    point = '0.49999 0 0'
    outputs = 'csv console'
  []
  [u_mid_outer]
    type = PointValue
    variable = u2
    point = '0.50001 0 0'
    outputs = 'csv console'
  []
  [u_mid_diff]
    type = FunctionValuePostprocessor
    function = u_mid_diff
    outputs = 'csv console'
  []
  [temperature_mid_inner]
    type = PointValue
    variable = temperature
    point = '0.49999 0 0'
    outputs = csv
  []
  [temperature_mid_outer]
    type = PointValue
    variable = temperature
    point = '0.50001 0 0'
    outputs = csv
  []
  [residual_concentration]
    type = FunctionValuePostprocessor
    function = residual_concentration
    outputs = 'csv console'
  []

  [flux_inner] # verify flux preservation
    type = SideDiffusiveFluxIntegral
    variable = u1
    boundary = interface
    diffusivity = diffusivity
    outputs = 'csv console'
  []
  [flux_outer]
    type = SideDiffusiveFluxIntegral
    variable = u2
    boundary = interface2
    diffusivity = diffusivity
    outputs = 'csv console'
  []
  [flux_error]
    type = FunctionValuePostprocessor
    function = flux_error
    outputs = 'csv console'
  []
[]

[Outputs]
  exodus = true
  csv = true
[]

[Debug]
  show_var_residual_norms = true
[]
