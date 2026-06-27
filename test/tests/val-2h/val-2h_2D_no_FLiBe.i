!include val-2h_parameters.params

# Materials properties
## diffusivity of tritium in air
D_air = '${units 1e-5 m^2/s}'

# Initial conditions
initial_pressure = '${units 1210 Pa}' # input pressure
initial_concentration_air = '${units 1e-12 mol/m^3}'

# Geometry and mesh
length_Ni = '${units 2 mm -> m}' # Ni membrane thickness
num_nodes_Ni = 10
length_air = '${units 8.1 mm -> m}' # air membrane thickness
num_nodes_air = 50

[Mesh]
  [cmg]
    type = CartesianMeshGenerator
    dim = 1
    dx = '${length_Ni} ${length_air}'
    ix = '${num_nodes_Ni} ${num_nodes_air}'
    subdomain_id = '1 2'
  []
  [interface_Ni_air]
    type = SideSetsBetweenSubdomainsGenerator
    input = cmg
    primary_block = '1'
    paired_block = '2'
    new_boundary = 'interface_Ni_air'
  []
  [interface_Ni_air_other_direction]
    type = SideSetsBetweenSubdomainsGenerator
    input = interface_Ni_air
    primary_block = '2'
    paired_block = '1'
    new_boundary = 'interface_Ni_air_other_direction'
  []
[]

[Variables]
  [tritium_concentration_Ni]
    initial_condition = ${initial_concentration_Ni} # mol/m^3
    block = 1
  []
  [tritium_concentration_air]
    initial_condition = ${initial_concentration_air} # mol/m^3
    block = 2
  []
[]

[AuxVariables]
  [enclosure_pressure]
    family = SCALAR
    initial_condition = ${initial_pressure}
  []
  [bounds_dummy_Ni]
    order = FIRST
    family = LAGRANGE
  []
  [bounds_dummy_air]
    order = FIRST
    family = LAGRANGE
  []
[]

[Bounds]
  [tritium_concentration_Ni_membrane_lower_bound]
    type = ConstantBounds
    variable = bounds_dummy_Ni
    bounded_variable = tritium_concentration_Ni
    bound_type = lower
    bound_value = '${fparse -1e-30}'
  []
  [tritium_concentration_Ni_wall_lower_bound]
    type = ConstantBounds
    variable = bounds_dummy_air
    bounded_variable = tritium_concentration_air
    bound_type = lower
    bound_value = '${fparse -1e-30}'
  []
[]

[Kernels]
  # Diffusion in Ni membrane
  [diffusion_Ni]
    type = ADMatDiffusion
    variable = 'tritium_concentration_Ni'
    diffusivity = ${D_Ni}
    block = 1
  []
  [time_diff_Ni]
    type = TimeDerivative
    variable = 'tritium_concentration_Ni'
    block = 1
  []
  # Diffusion in air
  [diffusion_air]
    type = ADMatDiffusion
    variable = 'tritium_concentration_air'
    diffusivity = ${D_air}
    block = 2
  []
  [time_diff_air]
    type = TimeDerivative
    variable = 'tritium_concentration_air'
    block = 2
  []
[]

[BCs]
  [left_concentration]
    type = EquilibriumBC
    Ko = ${K_s_Ni_prefactor}
    activation_energy = ${K_s_Ni_energy}
    boundary = 'left'
    enclosure_var = 'enclosure_pressure'
    temperature = ${temperature_exp}
    variable = 'tritium_concentration_Ni'
    p = ${n_Sieverts}
  []
  [right_concentration]
    type = ADDirichletBC
    boundary = 'right'
    variable = 'tritium_concentration_air'
    value = 0.0
  []
[]

[InterfaceKernels]
  [interface_sorption_Ni_air]
    type = InterfaceSorption
    K0 = ${K_s_Ni_prefactor}
    Ea = ${K_s_Ni_energy}
    n_sorption = ${n_Sieverts}
    diffusivity = ${D_Ni}
    unit_scale = ${unit_scale}
    unit_scale_neighbor = ${unit_scale_neighbor}
    temperature = ${temperature_exp}
    variable = 'tritium_concentration_Ni'
    neighbor_var = 'tritium_concentration_air'
    sorption_penalty = 1e1
    boundary = 'interface_Ni_air'
  []
[]

[Functions]
  [max_dt_size_function]
    type = ParsedFunction
    expression = 'if(t<${fparse 8500}, ${fparse 1e2},
                  if(t<${fparse 37000}, ${fparse 1e1},
                  if(t<${fparse 38500}, ${fparse 1e0}, ${fparse 1e1})))'
  []
[]

[Postprocessors]
  [average_flux_left] # mol/m^2/s
    type = SideDiffusiveFluxAverage
    variable = 'tritium_concentration_Ni'
    boundary = 'left'
    diffusivity = ${D_Ni}
  []
  [average_flux_Ni_air_interface] # mol/m^2/s
    type = SideDiffusiveFluxAverage
    variable = 'tritium_concentration_Ni'
    boundary = 'interface_Ni_air'
    diffusivity = ${D_Ni}
  []
  [average_flux_right] # mol/m^2/s
    type = SideDiffusiveFluxAverage
    variable = 'tritium_concentration_air'
    boundary = 'right'
    diffusivity = ${D_air}
  []
  [max_time_step_size]
    type = FunctionValuePostprocessor
    function = 'max_dt_size_function'
    execute_on = 'initial nonlinear linear timestep_end'
    outputs = none
  []
[]

[Preconditioning]
  [SMP]
    type = SMP
    full = true
  []
[]

[Executioner]
  type = Transient
  end_time = ${simulation_time}
  nl_max_its = 9
  l_max_its = 30
  scheme = 'bdf2'
  solve_type = 'Newton'
  petsc_options_iname = '-pc_type -sub_pc_type -snes_type'
  petsc_options_value = 'asm lu vinewtonrsls' # This petsc option helps prevent negative concentrations with bounds'
  nl_abs_tol = 1e-11
  [TimeStepper]
    type = IterationAdaptiveDT
    dt = 1e-6
    optimal_iterations = 7
    iteration_window = 1
    growth_factor = 1.1
    cutback_factor = 0.9
    cutback_factor_at_failure = 0.9
    timestep_limiting_postprocessor = max_time_step_size
  []
[]

[Outputs]
  file_base = 'val-2h_823K_1210Pa_out'
  [csv]
    type = CSV
  []
  [exodus]
    type = Exodus
    time_step_interval = 200
  []
[]
