# This test is to verify the implementation of InterfaceSorption and its AD counterpart in transient conditions.
# It contains two 1D blocks separated by a continuous interface.
# InterfaceSorption is used to enforce the sorption law and preserve flux between the blocks.
# Checks are performed to verify concentration conservation, sorption behavior, and flux preservation.
# This input file uses BreakMeshByBlockGenerator, which is currently only supported for replicated
# meshes, so this file should not be run with the `parallel_type = DISTRIBUTED` flag

# In this input file, we apply the Sievert law with n_sorption=1/2.

# Physical Constants
R = 8.31446261815324 # J/mol/K, based on number used in MOOSE PhysicalConstants.h (also see TMAP8PhysicalConstants.h)

temperature = 1000 # K
initial_concentration = 1
n_sorption = 0.5
solubility = ${fparse 2/R^n_sorption/temperature^n_sorption}

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
    initial_condition = ${initial_concentration}
  []
  [u2]
    block = 2
    initial_condition = ${initial_concentration}
  []
  [temperature]
    initial_condition = ${temperature}
  []
[]

[Kernels]
  [u1_time_derivative]
    type = TimeDerivative
    variable = u1
    block = 1
  []
  [u1_diffusion]
    type = MatDiffusion
    variable = u1
    diffusivity = diffusivity
    block = 1
  []
  [u2_time_derivative]
    type = TimeDerivative
    variable = u2
    block = 2
  []
  [u2_diffusion]
    type = MatDiffusion
    variable = u2
    diffusivity = diffusivity
    block = 2
  []
  [temperature]
    type = TimeDerivative
    variable = temperature
  []
[]

[BCs]
  [left_u1]
    type = NeumannBC
    value = 0
    variable = u1
    boundary = left
  []
  [right_u2]
    type = NeumannBC
    value = 0
    variable = u2
    boundary = right
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
    prop_names = 'diffusivity thermal_conductivity '
    prop_values = '0.2 1'
    block = '1'
  []
  [properties_2]
    type = GenericConstantMaterial
    prop_names = 'diffusivity solubility thermal_conductivity'
    prop_values = '0.2 ${solubility} 1'
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
    symbol_names = 'u_mid_inner u_mid_outer'
    symbol_values = 'u_mid_inner u_mid_outer '
    expression = 'u_mid_outer*${unit_scale} - ${solubility}*(u_mid_inner*${unit_scale_neighbor}*${R}*${temperature})^${n_sorption}'
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
  type = Transient
  solve_type = NEWTON

  petsc_options_iname = '-pc_type -pc_factor_mat_solver_package'
  petsc_options_value = 'lu superlu_dist'
  dt = 0.1
  end_time = 5
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
  [u1_inventory]
    type = ElementIntegralVariablePostprocessor
    variable = u1
    block = 1
  []
  [u2_inventory]
    type = ElementIntegralVariablePostprocessor
    variable = u2
    block = 2
  []
  [mass_conservation_sum_u1_u2]
    type = LinearCombinationPostprocessor
    pp_names = 'u1_inventory u2_inventory'
    pp_coefs = '1            1'
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
