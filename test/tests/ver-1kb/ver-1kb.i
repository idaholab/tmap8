# Verification Problem #1kb from TMAP7 V&V document
# A diffusion on two connected enclosures by a membrane without a volumetric source using Henry’s Law

# Physical Constants
R = '${units 8.31446261815324 J/mol/K}' # ideal gas constant from TMAP8PhysicalConstants.h

# Modeling parameters
nb_segments_TMAP7 = 20
node_size_TMAP7 = '${units 1.25e-5 m}'
long_total = '${fparse nb_segments_TMAP7 * node_size_TMAP7}' # m
nb_segments_TMAP8 = 100
simulation_time = '${units 10 s}'
temperature = '${units 500 K}'
initial_pressure_1 = '${units 1e5 Pa}'
initial_pressure_2 = '${units 1e-10 Pa}'
initial_concentration_1 = '${units ${fparse initial_pressure_1 / (R*temperature)} mol/m^3}'
initial_concentration_2 = '${units ${fparse initial_pressure_2 / (R*temperature)} mol/m^3}'
solubility = '${units ${fparse 1/(R*temperature)} mol/m^3/Pa}' # Henry's law solubility
diffusivity = '${units ${fparse 4.31e-6 * exp(-2818/temperature)} m^2/s}'
n_sorption = 1 # Henry's Law
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
  # Two surfaces from interface
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
  [concentration_enclosure_1]
    block = 1
    order = FIRST
    family = LAGRANGE
    initial_condition = '${initial_concentration_1}'
  []
  [concentration_enclosure_2]
    block = 2
    order = FIRST
    family = LAGRANGE
    initial_condition = '${initial_concentration_2}'
  []
[]

[AuxVariables]
  [pressure_enclosure_1]
    order = CONSTANT
    family = MONOMIAL
    block = 1
    initial_condition = '${initial_pressure_1}'
  []
  [pressure_enclosure_2]
    order = CONSTANT
    family = MONOMIAL
    block = 2
    initial_condition = '${initial_pressure_2}'
  []
[]

[Kernels]
  # Kernel for enclosure 1
  [diffusion_enclosure_1]
    type = MatDiffusion
    variable = concentration_enclosure_1
    diffusivity = ${diffusivity}
    block = '1'
  []
  [time_enclosure_1]
    type = TimeDerivative
    variable = concentration_enclosure_1
    block = '1'
  []
  # Kernel for enclosure 2
  [diffusion_enclosure_2]
    type = MatDiffusion
    variable = concentration_enclosure_2
    diffusivity = ${diffusivity}
    block = '2'
  []
  [time_enclosure_2]
    type = TimeDerivative
    variable = concentration_enclosure_2
    block = '2'
  []
[]

[AuxKernels]
  [pressure_enclosure_1]
    type = ParsedAux
    variable = pressure_enclosure_1
    coupled_variables = 'concentration_enclosure_1'
    expression = '${fparse R*temperature}*concentration_enclosure_1'
    block = 1
    execute_on = 'initial timestep_end'
  []
  [pressure_enclosure_2]
    type = ParsedAux
    variable = pressure_enclosure_2
    coupled_variables = 'concentration_enclosure_2'
    expression = '${fparse R*temperature}*concentration_enclosure_2'
    block = 2
    execute_on = 'initial timestep_end'
  []
[]

[InterfaceKernels]
  [interface_sorption]
    type = InterfaceSorption
    K0 = ${solubility}
    Ea = 0
    n_sorption = ${n_sorption}
    diffusivity = ${diffusivity}
    unit_scale = ${unit_scale}
    unit_scale_neighbor = ${unit_scale_neighbor}
    temperature = ${temperature}
    variable = concentration_enclosure_1
    neighbor_var = concentration_enclosure_2
    sorption_penalty = 1e1
    boundary = interface
  []
[]

[Postprocessors]
  [pressure_enclosure_1]
    type = ElementAverageValue
    variable = pressure_enclosure_1
    block = 1
    execute_on = 'initial timestep_end'
  []
  [pressure_enclosure_2]
    type = ElementAverageValue
    variable = pressure_enclosure_2
    block = 2
    execute_on = 'initial timestep_end'
  []
  [concentration_enclosure_1_at_interface]
    type = SideAverageValue
    boundary = interface
    variable = concentration_enclosure_1
    outputs = 'csv console'
    execute_on = 'initial timestep_end'
  []
  [concentration_enclosure_2_at_interface]
    type = SideAverageValue
    boundary = interface2
    variable = concentration_enclosure_2
    outputs = 'csv console'
    execute_on = 'initial timestep_end'
  []
  [concentration_ratio]
    type = ParsedPostprocessor
    expression = 'concentration_enclosure_1_at_interface / concentration_enclosure_2_at_interface'
    pp_names = 'concentration_enclosure_1_at_interface concentration_enclosure_2_at_interface'
    execute_on = 'initial timestep_end'
    outputs = 'csv console'
  []
  [solubility]
    type = ParsedPostprocessor
    expression = 'concentration_enclosure_1_at_interface / pressure_enclosure_2_at_interface'
    pp_names = 'concentration_enclosure_1_at_interface pressure_enclosure_2_at_interface'
    execute_on = 'initial timestep_end'
    outputs = 'csv console'
  []
  [pressure_enclosure_1_at_interface]
    type = SideAverageValue
    boundary = interface
    variable = pressure_enclosure_1
    outputs = 'csv console'
    execute_on = 'initial timestep_end'
  []
  [pressure_enclosure_2_at_interface]
    type = SideAverageValue
    boundary = interface2
    variable = pressure_enclosure_2
    outputs = 'csv console'
    execute_on = 'initial timestep_end'
  []
  [concentration_encl_1_inventory]
    type = ElementIntegralVariablePostprocessor
    variable = concentration_enclosure_1
    block = 1
    execute_on = 'initial timestep_end'
  []
  [concentration_encl_2_inventory]
    type = ElementIntegralVariablePostprocessor
    variable = concentration_enclosure_2
    block = 2
    execute_on = 'initial timestep_end'
  []
  [mass_conservation_sum_encl1_encl2]
    type = LinearCombinationPostprocessor
    pp_names = 'concentration_encl_1_inventory concentration_encl_2_inventory'
    pp_coefs = '1            1'
    execute_on = 'initial timestep_end'
  []
[]

[Executioner]
  type = Transient
  end_time = ${simulation_time}
  dtmax = 10
  nl_abs_tol = 1e-12
  nl_rel_tol = 1e-8
  scheme = 'bdf2'
  solve_type = NEWTON
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'
  nl_max_its = 6
  [TimeStepper]
    type = IterationAdaptiveDT
    dt = 0.01
    optimal_iterations = 5
    iteration_window = 3
    growth_factor = 1.05
    cutback_factor_at_failure = 0.8
  []
[]

[Outputs]
  file_base = 'ver-1kb_out_k1'
  csv = true
  [exodus]
    type = Exodus
    # legacy value
    max_output_name_length = 32
  []
  execute_on = 'initial timestep_end'
[]
