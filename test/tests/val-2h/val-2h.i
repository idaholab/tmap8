!include val-2h_parameters.params

# Materials properties
## diffusivity of tritium in FLiBe
D_FLiBe_prefactor = '${units 9.3e-7 m^2/s}'
D_FLiBe_energy = '${units 42e3 J/mol}'
D_FLiBe = '${units ${fparse D_FLiBe_prefactor * exp(- D_FLiBe_energy / (R*temperature_exp))} m^2/s}'
## Henry's law solubility for tritium in FLiBe
K_s_FLiBe_prefactor = '${units 7.9e-2 mol/m^3/Pa}'
K_s_FLiBe_energy = '${units 35e3 J/mol}'
# K_s_FLiBe = '${fparse K_s_FLiBe_prefactor * exp(- K_s_FLiBe_energy / (R*temperature_exp))}'

# Initial conditions
initial_pressure = '${units 1210 Pa}' # input pressure
initial_concentration_FLiBe = '${units 1e-12 mol/m^3}'

# Geometry and mesh
length_Ni = '${units 2 mm -> m}' # Ni membrane thickness
num_nodes_Ni = 5
length_FLiBe = '${units 8.1 mm -> m}' # FLiBe membrane thickness
num_nodes_FLiBe = 20
width_inner = '${units 25 mm -> m}'
num_nodes_inner = 50
width_wall = '${units 2 mm -> m}'
num_nodes_wall = 10
thickness = '${units 1 m}'

[Mesh]
  [cmg]
    type = CartesianMeshGenerator
    dim = 2
    dx = '0.00032 ${fparse length_Ni-0.0004-0.00032} 0.0004 0.000405 ${fparse length_FLiBe-0.000405-0.000405} 0.000405'
    dy = '${fparse width_inner-0.0005} 0.0005 0.0002 ${fparse width_wall-0.0002-0.00018} 0.00018'
    ix = '10 ${num_nodes_Ni} 15 15 ${num_nodes_FLiBe} 20'
    iy = '${num_nodes_inner} 15 15 ${fparse num_nodes_wall} 10'
    subdomain_id = '1 1 1 2 2 2
                    1 1 1 2 2 2
                    3 3 3 3 3 3
                    3 3 3 3 3 3
                    3 3 3 3 3 3'
  []
  [interface_Ni_FLiBe]
    type = SideSetsBetweenSubdomainsGenerator
    input = cmg
    primary_block = '1'
    paired_block = '2'
    new_boundary = 'interface_Ni_FLiBe'
  []
  [interface_Ni_membrane_FLiBe_other_direction]
    type = SideSetsBetweenSubdomainsGenerator
    input = 'interface_Ni_FLiBe'
    primary_block = '2'
    paired_block = '1'
    new_boundary = 'interface_Ni_membrane_FLiBe_other_direction'
  []
  [interface_Ni_wall_FLiBe]
    type = SideSetsBetweenSubdomainsGenerator
    input = 'interface_Ni_membrane_FLiBe_other_direction'
    primary_block = '3'
    paired_block = '2'
    new_boundary = 'interface_Ni_FLiBe'
  []
  [interface_Ni_wall_FLiBe_other_direction]
    type = SideSetsBetweenSubdomainsGenerator
    input = 'interface_Ni_wall_FLiBe'
    primary_block = '2'
    paired_block = '3'
    new_boundary = 'interface_Ni_wall_FLiBe_other_direction'
  []
  [restrict_bottom_Ni]
    type = ParsedGenerateSideset
    combinatorial_geometry = '1'
    input = 'interface_Ni_wall_FLiBe_other_direction'
    new_sideset_name = 'bottom_Ni'
    included_boundaries = 'bottom'
    included_subdomains = '1'
  []
  [restrict_bottom_FLiBe]
    type = ParsedGenerateSideset
    combinatorial_geometry = '1'
    input = 'restrict_bottom_Ni'
    new_sideset_name = 'bottom_FLiBe'
    included_boundaries = 'bottom'
    included_subdomains = '2'
  []
  [restrict_right_FLiBe]
    type = ParsedGenerateSideset
    combinatorial_geometry = '1'
    input = 'restrict_bottom_FLiBe'
    new_sideset_name = 'right_FLiBe'
    included_boundaries = 'right'
    included_subdomains = '2'
  []
  [restrict_right_Ni]
    type = ParsedGenerateSideset
    combinatorial_geometry = '1'
    input = 'restrict_right_FLiBe'
    new_sideset_name = 'right_Ni'
    included_boundaries = 'right'
    included_subdomains = '3'
  []
  [left_null_pressure]
    type = ParsedGenerateSideset
    combinatorial_geometry = 'y > 25e-3'
    included_boundaries = 'left'
    new_sideset_name = 'left_null_pressure'
    input = 'restrict_right_Ni'
  []
  [left_normal_pressure]
    type = ParsedGenerateSideset
    combinatorial_geometry = 'y < 25e-3'
    included_boundaries = 'left'
    new_sideset_name = 'left_normal_pressure'
    input = 'left_null_pressure'
  []
  [interface_Ni_wall_Ni_membrane]
    type = SideSetsBetweenSubdomainsGenerator
    input = 'left_normal_pressure'
    primary_block = '1'
    paired_block = '3'
    new_boundary = 'interface_Ni_wall_Ni_membrane'
  []
  [interface_Ni_wall_Ni_membrane_FLiBe_other_direction]
    type = SideSetsBetweenSubdomainsGenerator
    input = 'interface_Ni_wall_Ni_membrane'
    primary_block = '3'
    paired_block = '1'
    new_boundary = 'interface_Ni_wall_Ni_membrane_FLiBe_other_direction'
  []
  [restrict_left]
    type = ParsedGenerateSideset
    combinatorial_geometry = 'y < 10e-3'
    input = 'interface_Ni_wall_Ni_membrane_FLiBe_other_direction'
    new_sideset_name = 'restrict_left'
    included_boundaries = 'left'
    included_subdomains = '1'
  []
[]

[Variables]
  [tritium_concentration_Ni_membrane]
    initial_condition = ${initial_concentration_Ni} # mol/m^3
    block = 1
  []
  [tritium_concentration_Ni_wall]
    initial_condition = ${initial_concentration_Ni} # mol/m^3
    block = 3
  []
  [tritium_concentration_FLiBe]
    initial_condition = ${initial_concentration_FLiBe} # mol/m^3
    block = 2
  []
[]

[AuxVariables]
  [enclosure_pressure]
  []
  [enclosure_pressure_null]
  []
  [tritium_concentration_Ni_membrane_squared]
    block = 1
  []
  [tritium_concentration_Ni_wall_squared]
    block = 3
  []
  [bounds_dummy_Ni_membrane]
    order = FIRST
    family = LAGRANGE
  []
  [bounds_dummy_Ni_wall]
    order = FIRST
    family = LAGRANGE
  []
  [bounds_dummy_FLiBe]
    order = FIRST
    family = LAGRANGE
  []
[]

[Bounds]
  [tritium_concentration_Ni_membrane_lower_bound]
    type = ConstantBounds
    variable = bounds_dummy_Ni_membrane
    bounded_variable = tritium_concentration_Ni_membrane
    bound_type = lower
    bound_value = '${fparse -1e-30}'
  []
  [tritium_concentration_Ni_wall_lower_bound]
    type = ConstantBounds
    variable = bounds_dummy_Ni_wall
    bounded_variable = tritium_concentration_Ni_wall
    bound_type = lower
    bound_value = '${fparse -1e-30}'
  []
  [tritium_concentration_FLiBe_lower_bound]
    type = ConstantBounds
    variable = bounds_dummy_FLiBe
    bounded_variable = tritium_concentration_FLiBe
    bound_type = lower
    bound_value = '${fparse -1e-30}'
  []
[]

[Kernels]
  # Diffusion in Ni membrane
  [diffusion_Ni_membrane]
    type = ADMatDiffusion
    variable = 'tritium_concentration_Ni_membrane'
    diffusivity = ${D_Ni}
    block = 1
  []
  [time_diff_Ni_membrane]
    type = TimeDerivative
    variable = 'tritium_concentration_Ni_membrane'
    block = 1
  []
  # Diffusion in Ni wall
  [diffusion_Ni_wall]
    type = ADMatDiffusion
    variable = 'tritium_concentration_Ni_wall'
    diffusivity = ${D_Ni}
    block = 3
  []
  [time_diff_Ni_wall]
    type = TimeDerivative
    variable = 'tritium_concentration_Ni_wall'
    block = 3
  []
  # Diffusion in FLiBe
  [diffusion_FLiBe]
    type = ADMatDiffusion
    variable = 'tritium_concentration_FLiBe'
    diffusivity = ${D_FLiBe}
    block = 2
  []
  [time_diff_FLiBe]
    type = TimeDerivative
    variable = 'tritium_concentration_FLiBe'
    block = 2
  []
[]

[AuxKernels]
  [enclosure_pressure_null]
    type = FunctionAux
    function = 'pressure_value'
    variable = 'enclosure_pressure_null'
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [enclosure_pressure]
    type = FunctionAux
    function = 'pressure_value'
    variable = 'enclosure_pressure'
    execute_on = 'INITIAL TIMESTEP_END'
  []
[]

[BCs]
  [left_concentration]
    type = EquilibriumBC
    Ko = ${K_s_Ni_prefactor}
    activation_energy = ${K_s_Ni_energy}
    boundary = 'left_normal_pressure'
    enclosure_var = 'enclosure_pressure'
    temperature = ${temperature_exp}
    variable = 'tritium_concentration_Ni_membrane'
    p = ${n_Sieverts}
  []
  [left_concentration_null]
    type = EquilibriumBC
    Ko = ${K_s_Ni_prefactor}
    activation_energy = ${K_s_Ni_energy}
    boundary = 'left_null_pressure'
    enclosure_var = 'enclosure_pressure_null'
    temperature = ${temperature_exp}
    variable = 'tritium_concentration_Ni_wall'
    p = ${n_Sieverts}
  []
  [right_concentration_FLiBe]
    type = ADDirichletBC
    boundary = 'right_FLiBe'
    variable = 'tritium_concentration_FLiBe'
    value = 0.0
  []
  [right_concentration_Ni]
    type = ADDirichletBC
    boundary = 'right_Ni'
    variable = 'tritium_concentration_Ni_wall'
    value = 0.0
  []
  [bottom_flux_Ni]
    type = ADNeumannBC
    boundary = 'bottom_Ni'
    variable = 'tritium_concentration_Ni_membrane'
    value = 0.0
  []
  [bottom_flux_FLiBe]
    type = ADNeumannBC
    boundary = 'bottom_FLiBe'
    variable = 'tritium_concentration_FLiBe'
    value = 0.0
  []
  [top_concentration]
    type = ADDirichletBC
    boundary = 'top'
    variable = 'tritium_concentration_Ni_wall'
    value = 0.0
  []
  [equates_concentration_Ni_wall_Ni_membrane]
    type = MatchedValueBC
    variable = 'tritium_concentration_Ni_membrane'
    boundary = 'interface_Ni_wall_Ni_membrane'
    v = 'tritium_concentration_Ni_wall'
  []
[]

[InterfaceKernels]
  [interface_sorption_Ni_membrane_FLiBe]
    type = InterfaceSorption
    K0 = '${fparse K_s_FLiBe_prefactor / (K_s_Ni_prefactor^2) / (R*temperature_exp)^2}'
    Ea = '${fparse K_s_FLiBe_energy - (2*K_s_Ni_energy)}'
    n_sorption = 2
    diffusivity = ${D_Ni}
    unit_scale = ${unit_scale}
    unit_scale_neighbor = ${unit_scale_neighbor}
    temperature = ${temperature_exp}
    variable = 'tritium_concentration_FLiBe'
    neighbor_var = 'tritium_concentration_Ni_membrane'
    sorption_penalty = 1e1
    boundary = 'interface_Ni_membrane_FLiBe_other_direction'
  []
  [interface_sorption_Ni_wall_FLiBe]
    type = InterfaceSorption
    K0 = '${fparse K_s_FLiBe_prefactor / (K_s_Ni_prefactor^2) / (R*temperature_exp)^2}'
    Ea = '${fparse K_s_FLiBe_energy - (2*K_s_Ni_energy)}'
    n_sorption = 2
    diffusivity = ${D_Ni}
    unit_scale = ${unit_scale}
    unit_scale_neighbor = ${unit_scale_neighbor}
    temperature = ${temperature_exp}
    variable = 'tritium_concentration_FLiBe'
    neighbor_var = 'tritium_concentration_Ni_wall'
    sorption_penalty = 1e1
    boundary = 'interface_Ni_wall_FLiBe_other_direction'
  []
  [interface_Ni_wall_Ni_membrane]
    type = InterfaceDiffusion
    variable = 'tritium_concentration_Ni_wall'
    neighbor_var = 'tritium_concentration_Ni_membrane'
    boundary = 'interface_Ni_wall_Ni_membrane_FLiBe_other_direction'
    D = '${D_Ni}'
    D_neighbor = '${D_Ni}'
  []
[]

[Functions]
  [pressure_value]
    type = ParsedFunction
    expression = 'if(y<25e-3, ${initial_pressure}, ${initial_pressure}*(1-3*((y-25e-3)/2e-3)^2+2*((y-25e-3)/2e-3)^3))'
  []
[]

[Postprocessors]
  [left_flux_density_membrane] # mol/m^2/s
    type = SideDiffusiveFluxAverage
    boundary = 'left_normal_pressure'
    variable = 'tritium_concentration_Ni_membrane'
    diffusivity = ${D_Ni}
    # outputs = none
  []
  [left_flux_density_wall] # mol/m^2/s
    type = SideDiffusiveFluxAverage
    boundary = 'left_null_pressure'
    variable = 'tritium_concentration_Ni_wall'
    diffusivity = ${D_Ni}
    # outputs = none
  []
  [right_flux_density_membrane] # mol/m^2/s
    type = SideDiffusiveFluxAverage
    boundary = 'right_FLiBe'
    variable = 'tritium_concentration_FLiBe'
    diffusivity = ${D_FLiBe}
    # outputs = none
  []
  [right_flux_density_wall] # mol/m^2/s
    type = SideDiffusiveFluxAverage
    boundary = 'right_Ni'
    variable = 'tritium_concentration_Ni_wall'
    diffusivity = ${D_Ni}
    # outputs = none
  []

  # Mass conservation

  ## left boundary
  [left_flux_membrane] # mol/s
    type = ParsedPostprocessor
    expression = 'left_flux_density_membrane*${thickness}*${width_inner}'
    pp_names = 'left_flux_density_membrane'
    # outputs = none
  []
  [left_flux_wall] # mol/s
    type = ParsedPostprocessor
    expression = 'left_flux_density_wall*${thickness}*${width_wall}'
    pp_names = 'left_flux_density_wall'
    # outputs = none
  []
  [left_flux] # mol/s
    type = ParsedPostprocessor
    expression = 'left_flux_membrane+left_flux_wall'
    pp_names = 'left_flux_membrane left_flux_wall'
    # outputs = none
  []
  # right boundary
  [right_flux_membrane] # mol/s
    type = ParsedPostprocessor
    expression = 'right_flux_density_membrane*${thickness}*${width_inner}'
    pp_names = 'right_flux_density_membrane'
    # outputs = none
  []
  [right_flux_wall] # mol/s
    type = ParsedPostprocessor
    expression = 'right_flux_density_wall*${thickness}*${width_wall}'
    pp_names = 'right_flux_density_wall'
    # outputs = none
  []
  [right_flux] # mol/s
    type = ParsedPostprocessor
    expression = 'right_flux_membrane+right_flux_wall'
    pp_names = 'right_flux_membrane right_flux_wall'
    # outputs = none
  []

  ## in cell
  # []
  [Ni_membrane_concentration] # mol/m^3
    type = ElementAverageValue
    variable = 'tritium_concentration_Ni_membrane'
    block = 1
    # outputs = none
  []
  [Ni_membrane_amount] # mol
    type = ParsedPostprocessor
    expression = 'Ni_membrane_concentration*${thickness}*${length_Ni}*${width_inner}'
    pp_names = 'Ni_membrane_concentration'
    outputs = none
  []
  [FLiBe_concentration] # mol/m^3
    type = ElementAverageValue
    variable = 'tritium_concentration_FLiBe'
    block = 2
    #outputs = none
  []
  [FLiBe_amount] # mol
    type = ParsedPostprocessor
    expression = 'FLiBe_concentration*${thickness}*${length_FLiBe}*${width_inner}'
    pp_names = 'FLiBe_concentration'
    outputs = none
  []
  [Ni_wall_concentration] # mol/m^3
    type = ElementAverageValue
    variable = 'tritium_concentration_Ni_wall'
    block = 3
    #outputs = none
  []
  [Ni_wall_amount] # mol
    type = ParsedPostprocessor
    expression = 'Ni_wall_concentration*${thickness}*${fparse length_Ni+length_FLiBe}*${width_wall}'
    pp_names = 'Ni_wall_concentration'
    outputs = none
  []
  [tritium_amount] # mol
    type = ParsedPostprocessor
    expression = 'Ni_membrane_amount+FLiBe_amount+Ni_wall_amount'
    pp_names = 'Ni_membrane_amount FLiBe_amount Ni_wall_amount'
    # outputs = none
  []

  # top boundary
  [top_flux_density] # mol/m^2/s
    type = SideDiffusiveFluxAverage
    boundary = 'top'
    variable = 'tritium_concentration_Ni_wall'
    diffusivity = ${D_Ni}
    outputs = none
  []
  [top_flux] # mol/s
    type = ParsedPostprocessor
    expression = 'top_flux_density*${thickness}*${fparse length_Ni+length_FLiBe}'
    pp_names = 'top_flux_density'
    # outputs = none
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
  []
[]

[Outputs]
  file_base = 'val-2h_823K_1210Pa_out'
  [csv]
    type = CSV
  []
  [exodus]
    type = Exodus
    time_step_interval = 20
  []
[]
