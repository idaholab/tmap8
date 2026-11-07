# Verification Problem #1kd from TMAP7 V&V document
# A diffusion on two connected enclosures by a membrane with a volumetric source using Sieverts’ Law and chemical reactions

# Physical Constants
R = '${units 8.31446261815324 J/mol/K}' # ideal gas constant from TMAP8PhysicalConstants.h
N_a = '${units 6.02214076e23 1/mol}' # Avogadro's number from TMAP8PhysicalConstants.h

# Modeling parameters
nb_segments_TMAP7 = 20
node_size_TMAP7 = '${units 1.25e-5 m}'
long_total = '${units ${fparse nb_segments_TMAP7 * node_size_TMAP7} m}'
nb_segments_TMAP8 = 1e2
simulation_time = '${units 2 s}'
source = '${units ${fparse 1e23 / N_a} mol/m^3/s}' # Source term for T2 in enclosure 1
temperature = '${units 500 K}'
initial_pressure_1 = '${units 1e5 Pa}'
initial_pressure_2 = '${units 1e-10 Pa}'
initial_concentration_1 = '${units ${fparse initial_pressure_1 / (R*temperature)} mol/m^3}'
initial_concentration_2 = '${units ${fparse initial_pressure_2 / (R*temperature)} mol/m^3}'
solubility = '${units ${fparse 10/sqrt(R*temperature)} mol/m^3/Pa^(1/2)}' # Sieverts' law solubility
diffusivity = '${units ${fparse 4.31e-6 * exp(-2818/temperature)} m^2/s}'
n_sorption = 0.5 # Sieverts' Law
K1 = '${units 4000 mol/m^3/s}' # reaction rate for H2+T2->2HT
equilibrium_constant = 2.0
K2 = '${units ${fparse (2*K1) / (equilibrium_constant)^2} mol/m^3/s}' # reaction rate for 2HT->H2+T2
unit_scale = 1
unit_scale_neighbor = 1

[Mesh]
  [generated]
    type = GeneratedMeshGenerator
    dim = 1
    nx = ${nb_segments_TMAP8}
    xmax = ${long_total}
  []
  [enclosure_1]
    type = SubdomainBoundingBoxGenerator
    input = generated
    block_id = 1
    bottom_left = '0 0 0'
    top_right = '${fparse 1/3 * long_total} 0 0'
  []
  [enclosure_2]
    type = SubdomainBoundingBoxGenerator
    input = enclosure_1
    block_id = 2
    bottom_left = '${fparse 1/3 * long_total} 0 0'
    top_right = '${fparse long_total} 0 0'
  []
  [interface]
    type = SideSetsBetweenSubdomainsGenerator
    input = enclosure_2
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

  # Variables for H2, T2, and HT in enclosure 1
  [concentration_H2_enclosure_1]
    block = 1
    initial_condition = '${initial_concentration_1}'
  []
  [concentration_T2_enclosure_1]
    block = 1
    initial_condition = '${initial_concentration_1}'
  []
  [concentration_HT_enclosure_1]
    block = 1
    initial_condition = '${initial_concentration_2}'
  []

  # Variables for H2, T2, and HT in enclosure 2
  [concentration_H2_enclosure_2]
    block = 2
    initial_condition = '${initial_concentration_2}'
  []
  [concentration_T2_enclosure_2]
    block = 2
    initial_condition = '${initial_concentration_2}'
  []
  [concentration_HT_enclosure_2]
    block = 2
    initial_condition = '${initial_concentration_2}'
  []
[]

[AuxVariables]

  # Auxiliary variables for H2, T2, and HT in enclosure 1
  [pressure_H2_enclosure_1]
    order = CONSTANT
    family = MONOMIAL
    block = 1
    initial_condition = '${initial_pressure_1}'
  []
  [pressure_T2_enclosure_1]
    order = CONSTANT
    family = MONOMIAL
    block = 1
    initial_condition = '${initial_pressure_1}'
  []
  [pressure_HT_enclosure_1]
    order = CONSTANT
    family = MONOMIAL
    block = 1
    initial_condition = '${initial_pressure_2}'
  []

  # Auxiliary variables for H2, T2, and HT in enclosure 2
  [pressure_H2_enclosure_2]
    order = CONSTANT
    family = MONOMIAL
    block = 2
    initial_condition = '${initial_pressure_2}'
  []
  [pressure_T2_enclosure_2]
    order = CONSTANT
    family = MONOMIAL
    block = 2
    initial_condition = '${initial_pressure_2}'
  []
  [pressure_HT_enclosure_2]
    order = CONSTANT
    family = MONOMIAL
    block = 2
    initial_condition = '${initial_pressure_2}'
  []
[]

[Kernels]
  # Source term for T2 in enclosure 1
  [T2_source_term_enclosure_1]
    type = BodyForce
    variable = concentration_T2_enclosure_1
    block = '1'
    value = ${source}
  []

  # Diffusion equation for H2
  [H2_diffusion_enclosure_1]
    type = MatDiffusion
    variable = concentration_H2_enclosure_1
    diffusivity = ${diffusivity}
    block = '1'
  []
  [H2_time_derivative_enclosure_1]
    type = TimeDerivative
    variable = concentration_H2_enclosure_1
    block = '1'
  []
  [H2_diffusion_enclosure_2]
    type = MatDiffusion
    variable = concentration_H2_enclosure_2
    diffusivity = ${diffusivity}
    block = '2'
  []
  [H2_time_derivative_enclosure_2]
    type = TimeDerivative
    variable = concentration_H2_enclosure_2
    block = '2'
  []

  # Diffusion equation for T2
  [T2_diffusion_enclosure_1]
    type = MatDiffusion
    variable = concentration_T2_enclosure_1
    diffusivity = ${diffusivity}
    block = '1'
  []
  [T2_time_derivative_enclosure_1]
    type = TimeDerivative
    variable = concentration_T2_enclosure_1
    block = '1'
  []
  [T2_diffusion_enclosure_2]
    type = MatDiffusion
    variable = concentration_T2_enclosure_2
    diffusivity = ${diffusivity}
    block = '2'
  []
  [T2_time_derivative_enclosure_2]
    type = TimeDerivative
    variable = concentration_T2_enclosure_2
    block = '2'
  []

  # Diffusion equation for HT
  [HT_diffusion_enclosure_1]
    type = MatDiffusion
    variable = concentration_HT_enclosure_1
    diffusivity = ${diffusivity}
    block = '1'
  []
  [HT_time_derivative_enclosure_1]
    type = TimeDerivative
    variable = concentration_HT_enclosure_1
    block = '1'
  []
  [HT_diffusion_enclosure_2]
    type = MatDiffusion
    variable = concentration_HT_enclosure_2
    diffusivity = ${diffusivity}
    block = '2'
  []
  [HT_time_derivative_enclosure_2]
    type = TimeDerivative
    variable = concentration_HT_enclosure_2
    block = '2'
  []

  # Reaction H2+T2->2HT in enclosure 1
  [reaction_H2_encl_1_1]
    type = ADMatReactionFlexible
    variable = concentration_H2_enclosure_1
    vs = 'concentration_H2_enclosure_1 concentration_T2_enclosure_1'
    block = 1
    coeff = -1
    reaction_rate_name = ${K1}
  []
  [reaction_T2_encl_1_1]
    type = ADMatReactionFlexible
    variable = concentration_T2_enclosure_1
    vs = 'concentration_H2_enclosure_1 concentration_T2_enclosure_1'
    block = 1
    coeff = -1
    reaction_rate_name = ${K1}
  []
  [reaction_HT_encl_1_1]
    type = ADMatReactionFlexible
    variable = concentration_HT_enclosure_1
    vs = 'concentration_H2_enclosure_1 concentration_T2_enclosure_1'
    block = 1
    coeff = 2
    reaction_rate_name = ${K1}
  []

  # Reaction 2HT->H2+T2 in enclosure 1
  [reaction_H2_encl_1_2]
    type = ADMatReactionFlexible
    variable = concentration_H2_enclosure_1
    vs = 'concentration_HT_enclosure_1 concentration_HT_enclosure_1'
    block = 1
    coeff = 0.5
    reaction_rate_name = ${K2}
  []
  [reaction_T2_encl_1_2]
    type = ADMatReactionFlexible
    variable = concentration_T2_enclosure_1
    vs = 'concentration_HT_enclosure_1 concentration_HT_enclosure_1'
    block = 1
    coeff = 0.5
    reaction_rate_name = ${K2}
  []
  [reaction_HT_encl_1_2]
    type = ADMatReactionFlexible
    variable = concentration_HT_enclosure_1
    vs = 'concentration_HT_enclosure_1 concentration_HT_enclosure_1'
    block = 1
    coeff = -1
    reaction_rate_name = ${K2}
  []

  # Reaction H2+T2->2HT in enclosure 2
  [reaction_H2_encl_2_1]
    type = ADMatReactionFlexible
    variable = concentration_H2_enclosure_2
    vs = 'concentration_H2_enclosure_2 concentration_T2_enclosure_2'
    block = 2
    coeff = -1
    reaction_rate_name = ${K1}
  []
  [reaction_T2_encl_2_1]
    type = ADMatReactionFlexible
    variable = concentration_T2_enclosure_2
    vs = 'concentration_H2_enclosure_2 concentration_T2_enclosure_2'
    block = 2
    coeff = -1
    reaction_rate_name = ${K1}
  []
  [reaction_HT_encl_2_1]
    type = ADMatReactionFlexible
    variable = concentration_HT_enclosure_2
    vs = 'concentration_H2_enclosure_2 concentration_T2_enclosure_2'
    block = 2
    coeff = 2
    reaction_rate_name = ${K1}
  []

  # Reaction 2HT->H2+T2 in enclosure 2
  [reaction_H2_encl_2_2]
    type = ADMatReactionFlexible
    variable = concentration_H2_enclosure_2
    vs = 'concentration_HT_enclosure_2 concentration_HT_enclosure_2'
    block = 2
    coeff = 0.5
    reaction_rate_name = ${K2}
  []
  [reaction_T2_encl_2_2]
    type = ADMatReactionFlexible
    variable = concentration_T2_enclosure_2
    vs = 'concentration_HT_enclosure_2 concentration_HT_enclosure_2'
    block = 2
    coeff = 0.5
    reaction_rate_name = ${K2}
  []
  [reaction_HT_encl_2_2]
    type = ADMatReactionFlexible
    variable = concentration_HT_enclosure_2
    vs = 'concentration_HT_enclosure_2 concentration_HT_enclosure_2'
    block = 2
    coeff = -1
    reaction_rate_name = ${K2}
  []
[]

[AuxKernels]

  # Auxiliary kernels for H2, T2, and HT in enclosure 1
  [pressure_H2_enclosure_1]
    type = ParsedAux
    variable = pressure_H2_enclosure_1
    coupled_variables = 'concentration_H2_enclosure_1'
    expression = '${fparse R*temperature}*concentration_H2_enclosure_1'
    block = 1
    execute_on = 'initial timestep_end'
  []
  [pressure_T2_enclosure_1]
    type = ParsedAux
    variable = pressure_T2_enclosure_1
    coupled_variables = 'concentration_T2_enclosure_1'
    expression = '${fparse R*temperature}*concentration_T2_enclosure_1'
    block = 1
    execute_on = 'initial timestep_end'
  []
  [pressure_HT_enclosure_1]
    type = ParsedAux
    variable = pressure_HT_enclosure_1
    coupled_variables = 'concentration_HT_enclosure_1'
    expression = '${fparse R*temperature}*concentration_HT_enclosure_1'
    block = 1
    execute_on = 'initial timestep_end'
  []

  # Auxiliary kernels for H2, T2, and HT in enclosure 2
  [pressure_H2_enclosure_2]
    type = ParsedAux
    variable = pressure_H2_enclosure_2
    coupled_variables = 'concentration_H2_enclosure_2'
    expression = '${fparse R*temperature}*concentration_H2_enclosure_2'
    block = 2
    execute_on = 'initial timestep_end'
  []
  [pressure_T2_enclosure_2]
    type = ParsedAux
    variable = pressure_T2_enclosure_2
    coupled_variables = 'concentration_T2_enclosure_2'
    expression = '${fparse R*temperature}*concentration_T2_enclosure_2'
    block = 2
    execute_on = 'initial timestep_end'
  []
  [pressure_HT_enclosure_2]
    type = ParsedAux
    variable = pressure_HT_enclosure_2
    coupled_variables = 'concentration_HT_enclosure_2'
    expression = '${fparse R*temperature}*concentration_HT_enclosure_2'
    block = 2
    execute_on = 'initial timestep_end'
  []
[]

[InterfaceKernels]
  [interface_sorption_H2]
    type = InterfaceSorption
    K0 = ${solubility}
    Ea = 0
    n_sorption = ${n_sorption}
    diffusivity = ${diffusivity}
    unit_scale = ${unit_scale}
    unit_scale_neighbor = ${unit_scale_neighbor}
    temperature = ${temperature}
    variable = concentration_H2_enclosure_1
    neighbor_var = concentration_H2_enclosure_2
    sorption_penalty = 1e1
    boundary = interface
  []
  [interface_sorption_T2]
    type = InterfaceSorption
    K0 = ${solubility}
    Ea = 0
    n_sorption = ${n_sorption}
    diffusivity = ${diffusivity}
    unit_scale = ${unit_scale}
    unit_scale_neighbor = ${unit_scale_neighbor}
    temperature = ${temperature}
    variable = concentration_T2_enclosure_1
    neighbor_var = concentration_T2_enclosure_2
    sorption_penalty = 1e1
    boundary = interface
  []
  [interface_sorption_HT]
    type = InterfaceSorption
    K0 = ${solubility}
    Ea = 0
    n_sorption = ${n_sorption}
    diffusivity = ${diffusivity}
    unit_scale = ${unit_scale}
    unit_scale_neighbor = ${unit_scale_neighbor}
    temperature = ${temperature}
    variable = concentration_HT_enclosure_1
    neighbor_var = concentration_HT_enclosure_2
    sorption_penalty = 1e1
    boundary = interface
  []
[]

[Postprocessors]

  # postprocessors for H2
  [pressure_H2_enclosure_1]
    type = ElementAverageValue
    variable = pressure_H2_enclosure_1
    block = 1
    execute_on = 'initial timestep_end'
  []
  [pressure_H2_enclosure_2]
    type = ElementAverageValue
    variable = pressure_H2_enclosure_2
    block = 2
    execute_on = 'initial timestep_end'
  []
  [concentration_H2_enclosure_1_at_interface]
    type = SideAverageValue
    boundary = interface
    variable = concentration_H2_enclosure_1
    outputs = 'csv console'
    execute_on = 'initial timestep_end'
  []
  [concentration_H2_enclosure_2_at_interface]
    type = SideAverageValue
    boundary = interface2
    variable = concentration_H2_enclosure_2
    outputs = 'csv console'
    execute_on = 'initial timestep_end'
  []
  [concentration_ratio_H2]
    type = ParsedPostprocessor
    expression = 'concentration_H2_enclosure_1_at_interface / sqrt(concentration_H2_enclosure_2_at_interface)'
    pp_names = 'concentration_H2_enclosure_1_at_interface concentration_H2_enclosure_2_at_interface'
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
  [pressure_H2_enclosure_2_at_interface]
    type = SideAverageValue
    boundary = interface2
    variable = pressure_H2_enclosure_2
    outputs = 'csv console'
    execute_on = 'initial timestep_end'
  []
  [concentration_H2_encl_1_inventory]
    type = ElementIntegralVariablePostprocessor
    variable = concentration_H2_enclosure_1
    block = 1
    execute_on = 'initial timestep_end'
  []
  [concentration_H2_encl_2_inventory]
    type = ElementIntegralVariablePostprocessor
    variable = concentration_H2_enclosure_2
    block = 2
    execute_on = 'initial timestep_end'
  []

  # postprocessors for T2
  [pressure_T2_enclosure_1]
    type = ElementAverageValue
    variable = pressure_T2_enclosure_1
    block = 1
    execute_on = 'initial timestep_end'
  []
  [pressure_T2_enclosure_2]
    type = ElementAverageValue
    variable = pressure_T2_enclosure_2
    block = 2
    execute_on = 'initial timestep_end'
  []
  [concentration_T2_enclosure_1_at_interface]
    type = SideAverageValue
    boundary = interface
    variable = concentration_T2_enclosure_1
    outputs = 'csv console'
    execute_on = 'initial timestep_end'
  []
  [concentration_T2_enclosure_2_at_interface]
    type = SideAverageValue
    boundary = interface2
    variable = concentration_T2_enclosure_2
    outputs = 'csv console'
    execute_on = 'initial timestep_end'
  []
  [concentration_ratio_T2]
    type = ParsedPostprocessor
    expression = 'concentration_T2_enclosure_1_at_interface / sqrt(concentration_T2_enclosure_2_at_interface)'
    pp_names = 'concentration_T2_enclosure_1_at_interface concentration_T2_enclosure_2_at_interface'
    execute_on = 'initial timestep_end'
    outputs = 'csv console'
  []
  [concentration_T2_encl_1_inventory]
    type = ElementIntegralVariablePostprocessor
    variable = concentration_T2_enclosure_1
    block = 1
    execute_on = 'initial timestep_end'
  []
  [concentration_T2_encl_2_inventory]
    type = ElementIntegralVariablePostprocessor
    variable = concentration_T2_enclosure_2
    block = 2
    execute_on = 'initial timestep_end'
  []

  # postprocessors for HT
  [pressure_HT_enclosure_1]
    type = ElementAverageValue
    variable = pressure_HT_enclosure_1
    block = 1
    execute_on = 'initial timestep_end'
  []
  [pressure_HT_enclosure_2]
    type = ElementAverageValue
    variable = pressure_HT_enclosure_2
    block = 2
    execute_on = 'initial timestep_end'
  []
  [concentration_HT_enclosure_1_at_interface]
    type = SideAverageValue
    boundary = interface
    variable = concentration_HT_enclosure_1
    outputs = 'csv console'
    execute_on = 'initial timestep_end'
  []
  [concentration_HT_enclosure_2_at_interface]
    type = SideAverageValue
    boundary = interface2
    variable = concentration_HT_enclosure_2
    outputs = 'csv console'
    execute_on = 'initial timestep_end'
  []
  [concentration_ratio_HT]
    type = ParsedPostprocessor
    expression = 'concentration_HT_enclosure_1_at_interface / sqrt(concentration_HT_enclosure_2_at_interface)'
    pp_names = 'concentration_HT_enclosure_1_at_interface concentration_HT_enclosure_2_at_interface'
    execute_on = 'initial timestep_end'
    outputs = 'csv console'
  []
  [concentration_HT_encl_1_inventory]
    type = ElementIntegralVariablePostprocessor
    variable = concentration_HT_enclosure_1
    block = 1
    execute_on = 'initial timestep_end'
  []
  [concentration_HT_encl_2_inventory]
    type = ElementIntegralVariablePostprocessor
    variable = concentration_HT_enclosure_2
    block = 2
    execute_on = 'initial timestep_end'
  []

  # postprocessors for mass conservation
  [mass_conservation_sum_encl1_encl2]
    type = LinearCombinationPostprocessor
    pp_names = 'concentration_HT_encl_1_inventory concentration_HT_encl_2_inventory concentration_H2_encl_1_inventory concentration_H2_encl_2_inventory concentration_T2_encl_1_inventory concentration_T2_encl_2_inventory'
    pp_coefs = '1            1           1            1            1            1'
    execute_on = 'initial timestep_end'
  []

  # postprocessors for equilibrium constant
  [equilibrium_constant_encl_1]
    type = ParsedPostprocessor
    expression = 'pressure_HT_enclosure_1 / sqrt(pressure_H2_enclosure_1 * pressure_T2_enclosure_1)'
    pp_names = 'pressure_HT_enclosure_1 pressure_H2_enclosure_1 pressure_T2_enclosure_1'
    execute_on = 'initial timestep_end'
    outputs = 'csv console'
  []
  [equilibrium_constant_encl_2]
    type = ParsedPostprocessor
    expression = 'pressure_HT_enclosure_2 / sqrt(pressure_H2_enclosure_2 * pressure_T2_enclosure_2)'
    pp_names = 'pressure_HT_enclosure_2 pressure_H2_enclosure_2 pressure_T2_enclosure_2'
    execute_on = 'initial timestep_end'
    outputs = 'csv console'
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
  dtmax = 1e-2
  nl_max_its = 9
  l_max_its = 30
  scheme = 'bdf2'
  solve_type = 'PJFNK'
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'
  [TimeStepper]
    type = IterationAdaptiveDT
    dt = 1e-6
    optimal_iterations = 7
    iteration_window = 1
    growth_factor = 1.1
    cutback_factor = 0.9
    cutback_factor_at_failure = 0.9
  []
[]

[Outputs]
  file_base = 'ver-1kd_out_k10'
  csv = true
  exodus = true
  execute_on = 'initial timestep_end'
[]
