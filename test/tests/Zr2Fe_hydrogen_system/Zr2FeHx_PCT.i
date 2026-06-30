###########################################
# Testing PCT Zr2FeHx modelling capability and performance
# This input file works in two independent ways:
# (A) : Evaluate the equilibrium of hydrogen and Zr2Fe at a set Pressure boundary and Temperature
# (B) : Evaluate the equilibrium of hydrogen and Zr2Fe at an increasing Pressure boundary and set Temperature
###########################################

# Physical constants
R = '${units 8.31446261815324 J/mol/K}' # ideal gas constant from PhysicalConstants.h
N_a = '${units 6.02214076e23 1/mol}' # Avogadro's number from PhysicalConstants.h
boltzmann_constant = '${units 1.380649e-23 J/K}' # Boltzmann constant from PhysicalConstants.h

# Simulation conditions and material properties
temperature = '${units 598.15 K}'
density_Zr2Fe = '${units 29375.60 mol/m^3}'


initial_pressure_H2_enclosure_1 = '${units 7 Pa}'
initial_concentration_H_enclosure_1 = '${units ${fparse 2*initial_pressure_H2_enclosure_1 / (R*temperature)} mol/m^3}'
initial_atomic_fraction= '${fparse 5.0 - 8.320e-03  / ( 1e-03 + exp(-2.4851 - 7.6091e-03 * temperature + (5.6264e-02 + 1.7197e-04 * temperature) * log(max(initial_pressure_H2_enclosure_1 - 5, 1e-10))))}'
initial_concentration_H_enclosure_2 = '${units ${fparse initial_atomic_fraction*density_Zr2Fe} mol/m^3}'

# diffusivity from:
#Zr:Yu, Feifei, et al. “Hydrogen Diffusion in Zirconium Hydrides from On-the-Fly Machine Learning Molecular Dynamics.” International Journal of Hydrogen Energy, vol. 56, Feb. 2024, pp. 1057–66. DOI.org (Crossref), https://doi.org/10.1016/j.ijhydene.2023.12.241

diffusivity_Do = '${units 1.53e-07 m^2/s}'
diffusivity_Ea = '${units 0.61 eV -> J}'

diffusivity_ratio_gas_Zr2FeHx = '${fparse initial_concentration_H_enclosure_2 / initial_concentration_H_enclosure_1 * 10}' # this ratio is large and helps InterfaceDiffusion due to the ratio of concentrations
# Surface reaction rate from:
#Yang, Zhiyi, et al. “A Potential Hydrogen Isotope Storage Material Zr2Fe: Deep Exploration on Phase Transition Behaviors and Disproportionation Mechanism.” Energy Materials, vol. 5, no. 1, Jan. 2025. DOI.org (Crossref), https://doi.org/10.20517/energymater.2024.83.
reaction_rate_0 = '${units 4.28e02 1/s}'
reaction_rate_Ea = '${units 0.9108 eV -> J}'

# Domain size and mesh parameters
domain_length = '${units 1 m}'
num_nodes = 50

# time
simulation_time = '${units 1e9 s}'
dt_max = '${fparse simulation_time/100}'
dt_init = '${units 1e-3 s}'

# convergence parameters
lower_value_threshold_concentration_enclosure_1 = -1e-20
lower_value_threshold_concentration_enclosure_2 = -1e-20

# file base
output_file_base ='Zr2FeHx_PCT_out'


[Mesh]
  [generated]
    type = GeneratedMeshGenerator
    dim = 1
    nx = ${num_nodes}
    xmax = ${domain_length}
  []
  [enclosure_1]
    type = SubdomainBoundingBoxGenerator
    input = generated
    block_id = 1
    bottom_left = '0 0 0'
    top_right = '${fparse 1/2 * domain_length} 0 0'
  []
  [enclosure_2]
    type = SubdomainBoundingBoxGenerator
    input = enclosure_1
    block_id = 2
    bottom_left = '${fparse 1/2 * domain_length} 0 0'
    top_right = '${fparse domain_length} 0 0'
  []
  [interface]
    type = SideSetsBetweenSubdomainsGenerator
    input = enclosure_2
    primary_block = 1
    paired_block = 2
    new_boundary = interface
  []
  [interface_2]
    type = SideSetsBetweenSubdomainsGenerator
    input = interface
    primary_block = 2
    paired_block = 1
    new_boundary = interface_2
  []
[]

[Variables]
  [concentration_H_enclosure_1]
    block = 1
    initial_condition = '${initial_concentration_H_enclosure_1}'
  []
  [concentration_H_enclosure_2]
    block = 2
    initial_condition = '${initial_concentration_H_enclosure_2}'
  []
[]

[Bounds]
  # To prevent negative concentrations
  [concentration_H_enclosure_1_lower_bound]
    type = ConstantBounds
    variable = bounds_dummy_concentration_H_enclosure_1
    bounded_variable = concentration_H_enclosure_1
    bound_type = lower
    bound_value = ${lower_value_threshold_concentration_enclosure_1}
  []
  [concentration_H_enclosure_2_lower_bound]
    type = ConstantBounds
    variable = bounds_dummy_concentration_H_enclosure_2
    bounded_variable = concentration_H_enclosure_2
    bound_type = lower
    bound_value = ${lower_value_threshold_concentration_enclosure_2}
  []
[]

[BCs]
  [concentration_H_enclosure_1_fixed]
    type = FunctionDirichletBC
    variable = concentration_H_enclosure_1
    boundary = left
    function = 'function_BC_concentration_H_enclosure_1'
  []
[]

[Functions]
  [function_BC_concentration_H_enclosure_1]
    type = ParsedFunction
    expression = 'exp(-${dt_init}*2e-2/t)* ${initial_concentration_H_enclosure_1}'
  []
[]

[Kernels]
  # Diffusion equation for H in enclosure 1
  [H_time_derivative_enclosure_1]
    type = TimeDerivative
    variable = concentration_H_enclosure_1
    block = '1'
  []
  [H_diffusion_enclosure_1]
    type = MatDiffusion
    variable = concentration_H_enclosure_1
    diffusivity = diffusivity_gas
    block = '1'
  []
  # Diffusion equation for H in enclosure 2
  [H_time_derivative_enclosure_2]
    type = TimeDerivative
    variable = concentration_H_enclosure_2
    block = '2'
  []
  [H_diffusion_enclosure_2]
    type = MatDiffusion
    variable = concentration_H_enclosure_2
    diffusivity = diffusivity_Zr2FeHx
    block = '2'
  []
[]

[AuxVariables]
  [temperature]
    initial_condition = '${temperature}'
  []
  [pressure_H2_enclosure_1]
    initial_condition = '${initial_pressure_H2_enclosure_1}'
  []
  [bounds_dummy_concentration_H_enclosure_1]
    order = FIRST
    family = LAGRANGE
  []
  [bounds_dummy_concentration_H_enclosure_2]
    order = FIRST
    family = LAGRANGE
  []
[]

[AuxKernels]
  [pressure_H2_enclosure_1]
    type = ParsedAux
    variable = pressure_H2_enclosure_1
    coupled_variables = 'concentration_H_enclosure_1 temperature'
    expression = '${R} * temperature * concentration_H_enclosure_1/2'
    block = 1
    execute_on = 'initial timestep_end'
  []
[]

[Materials]
  [diffusivity_Zr2FeHx]
    type = DerivativeParsedMaterial
    property_name = diffusivity_Zr2FeHx
    coupled_variables = 'temperature'
    expression = '${diffusivity_Do} * exp(-${fparse diffusivity_Ea*N_a/R}/temperature)'
    outputs = exodus
  []
  [diffusivity_gas]
    type = DerivativeParsedMaterial
    property_name = diffusivity_gas
    material_property_names = diffusivity_Zr2FeHx
    expression = '${diffusivity_ratio_gas_Zr2FeHx}*diffusivity_Zr2FeHx'
    outputs = exodus
  []
  [reaction_rate_surface_Zr2FeHx_1]
    type = ADDerivativeParsedMaterial
    property_name = reaction_rate_surface_Zr2FeHx
    coupled_variables = 'temperature'
    expression = '${reaction_rate_0} * exp(-${fparse reaction_rate_Ea/boltzmann_constant}/temperature)' # 1/s
    block = '1'
  []
  [reaction_rate_surface_Zr2FeHx_2]
    type = ADDerivativeParsedMaterial
    property_name = reaction_rate_surface_Zr2FeHx
    coupled_variables = 'temperature'
    expression = '${reaction_rate_0} * exp(-${fparse reaction_rate_Ea/boltzmann_constant}/temperature)' # 1/s
    block = '2'
  []
[]

[InterfaceKernels]
  [interface_diffusion]
    type = InterfaceDiffusion
    variable = concentration_H_enclosure_2
    neighbor_var = concentration_H_enclosure_1
    boundary = interface_2
    D = diffusivity_Zr2FeHx
    D_neighbor = diffusivity_gas
  []
  [interface_reaction_Zr2FeHx_PCT]
    type = ADMatInterfaceReactionZr2FeHxPCT
    variable = concentration_H_enclosure_2
    neighbor_var = concentration_H_enclosure_1
    neighbor_temperature = temperature
    density = ${density_Zr2Fe}
    boundary = interface_2
    forward_rate = 'reaction_rate_surface_Zr2FeHx'
    backward_rate = 'reaction_rate_surface_Zr2FeHx'
  []
[]

[Postprocessors]
  [temperature]
    type = ElementAverageValue
    variable = temperature
    block = 1
    execute_on = 'initial timestep_end'
  []
  [pressure_H2_enclosure_1]
    type = ElementAverageValue
    variable = pressure_H2_enclosure_1
    block = 1
    execute_on = 'initial timestep_end'
  []
  [concentration_H_enclosure_1_at_interface]
    type = SideAverageValue
    boundary = interface
    variable = concentration_H_enclosure_1
    outputs = 'csv console'
    execute_on = 'initial timestep_end'
  []
  [concentration_H_enclosure_2_at_interface]
    type = SideAverageValue
    boundary = interface_2
    variable = concentration_H_enclosure_2
    outputs = 'csv console'
    execute_on = 'initial timestep_end'
  []
  [atomic_fraction_H_enclosure_2_at_interface]
    type = ParsedPostprocessor
    pp_names = 'concentration_H_enclosure_2_at_interface'
    expression = 'concentration_H_enclosure_2_at_interface / ${density_Zr2Fe}'
    outputs = 'csv console'
    execute_on = 'initial timestep_end'
  []
  [concentration_ratio_H2]
    type = ParsedPostprocessor
    expression = 'concentration_H_enclosure_1_at_interface / sqrt(concentration_H_enclosure_2_at_interface)'
    pp_names = 'concentration_H_enclosure_1_at_interface concentration_H_enclosure_2_at_interface'
    execute_on = 'initial timestep_end'
    outputs = 'csv console'
  []
  [pressure_H2_enclosure_1_at_interface]
    type = SideAverageValue
    boundary = interface
    variable = pressure_H2_enclosure_1
    outputs = 'csv console'
    execute_on = 'initial timestep_end'
  []
  [concentration_H_encl_1_inventory]
    type = ElementIntegralVariablePostprocessor
    variable = concentration_H_enclosure_1
    block = 1
    execute_on = 'initial timestep_end'
  []
  [concentration_H_encl_2_inventory]
    type = ElementIntegralVariablePostprocessor
    variable = concentration_H_enclosure_2
    block = 2
    execute_on = 'initial timestep_end'
  []

  # postprocessors for mass conservation
  [mass_conservation_sum_encl1_encl2]
    type = LinearCombinationPostprocessor
    pp_names = 'concentration_H_encl_1_inventory concentration_H_encl_2_inventory'
    pp_coefs = '1                                1'
    execute_on = 'initial timestep_end'
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
  end_time = ${simulation_time}
  dtmax = ${dt_max}
  nl_max_its = 16
  l_max_its = 30
  nl_rel_tol = 1e-2
  nl_abs_tol = 4e-15
  scheme = 'bdf2'
  solve_type = 'Newton'
  petsc_options_iname = '-pc_type -pc_factor_mat_solver_type -snes_type'
  petsc_options_value = 'lu       mumps                      vinewtonrsls' # This petsc option helps prevent negative concentrations with bounds'
  line_search = 'none'
  automatic_scaling = true
  compute_scaling_once = true
  [TimeStepper]
    type = IterationAdaptiveDT
    dt = ${dt_init}
    optimal_iterations = 13
    iteration_window = 1
    growth_factor = 1.2
    cutback_factor = 0.9
    cutback_factor_at_failure = 0.9
  []
[]

[Outputs]
  file_base = ${output_file_base}
  csv = true
  [exodus]
    type = Exodus
    execute_on = 'timestep_end'
  []
[]
