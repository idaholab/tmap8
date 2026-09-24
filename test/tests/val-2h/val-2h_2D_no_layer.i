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
num_nodes_Ni = 5 # 10
length_FLiBe = '${units 8.1 mm -> m}' # FLiBe membrane thickness
num_nodes_FLiBe = 20 # 30
width_inner = '${units 25 mm -> m}'
num_nodes_inner = 25 # 50
thickness = '${units 1 m}'

[Mesh]
  [cmg]
    type = CartesianMeshGenerator
    dim = 2
    dx = '${fparse length_Ni} ${fparse length_FLiBe}'
    dy = '${fparse width_inner}'
    ix = '${num_nodes_Ni} ${num_nodes_FLiBe}'
    iy = '${num_nodes_inner}'
    subdomain_id = '1 2'
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
  [restrict_bottom_Ni]
    type = ParsedGenerateSideset
    combinatorial_geometry = '1'
    input = 'interface_Ni_membrane_FLiBe_other_direction'
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
  [restrict_top_Ni]
    type = ParsedGenerateSideset
    combinatorial_geometry = '1'
    input = 'restrict_bottom_FLiBe'
    new_sideset_name = 'top_Ni'
    included_boundaries = 'top'
    included_subdomains = '1'
  []
  [restrict_top_FLiBe]
    type = ParsedGenerateSideset
    combinatorial_geometry = '1'
    input = 'restrict_top_Ni'
    new_sideset_name = 'top_FLiBe'
    included_boundaries = 'top'
    included_subdomains = '2'
  []
[]

[Variables]
  [tritium_concentration_Ni_membrane]
    initial_condition = ${initial_concentration_Ni} # mol/m^3
    block = 1
  []
  [tritium_concentration_FLiBe]
    initial_condition = ${initial_concentration_FLiBe} # mol/m^3
    block = 2
  []
[]

[AuxVariables]
  [enclosure_pressure]
    initial_condition = ${initial_pressure}
  []
  [tritium_concentration_Ni_membrane_squared]
    block = 1
  []
  [bounds_dummy_Ni_membrane]
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
    bound_value = '${fparse -1e-20}'
  []
  [tritium_concentration_FLiBe_lower_bound]
    type = ConstantBounds
    variable = bounds_dummy_FLiBe
    bounded_variable = tritium_concentration_FLiBe
    bound_type = lower
    bound_value = '${fparse -1e-20}'
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
  [tritium_concentration_Ni_membrane_squared]
    type = ParsedAux
    variable = 'tritium_concentration_Ni_membrane_squared'
    coupled_variables = 'tritium_concentration_Ni_membrane'
    expression = 'tritium_concentration_Ni_membrane^2'
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
    variable = 'tritium_concentration_Ni_membrane'
    p = ${n_Sieverts}
  []
  [right_concentration_FLiBe]
    type = ADDirichletBC
    boundary = 'right'
    variable = 'tritium_concentration_FLiBe'
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
  [top_flux_Ni]
    type = ADNeumannBC
    boundary = 'top_Ni'
    variable = 'tritium_concentration_Ni_membrane'
    value = 0.0
  []
  [top_flux_FLiBe]
    type = ADNeumannBC
    boundary = 'top_FLiBe'
    variable = 'tritium_concentration_FLiBe'
    value = 0.0
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
    sorption_penalty = 1e2
    boundary = 'interface_Ni_membrane_FLiBe_other_direction'
  []
[]

[Postprocessors]
  [left_flux_density_membrane] # mol/m^2/s
    type = SideDiffusiveFluxAverage
    boundary = 'left'
    variable = 'tritium_concentration_Ni_membrane'
    diffusivity = ${D_Ni}
    # outputs = none
  []
  [right_flux_density_membrane] # mol/m^2/s
    type = SideDiffusiveFluxAverage
    boundary = 'right'
    variable = 'tritium_concentration_FLiBe'
    diffusivity = ${D_FLiBe}
    # outputs = none
  []

  # Mass conservation

  ## left boundary
  [left_flux] # mol/s
    type = ParsedPostprocessor
    expression = 'left_flux_density_membrane*${thickness}*${width_inner}'
    pp_names = 'left_flux_density_membrane'
    # outputs = none
  []
  # right boundary
  [right_flux] # mol/s
    type = ParsedPostprocessor
    expression = 'right_flux_density_membrane*${thickness}*${width_inner}'
    pp_names = 'right_flux_density_membrane'
    # outputs = none
  []

  ## in cell
  # []
  [Ni_membrane_concentration] # mol/m^3
    type = ElementAverageValue
    variable = 'tritium_concentration_Ni_membrane'
    block = 1
    outputs = none
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
    outputs = none
  []
  [FLiBe_amount] # mol
    type = ParsedPostprocessor
    expression = 'FLiBe_concentration*${thickness}*${length_FLiBe}*${width_inner}'
    pp_names = 'FLiBe_concentration'
    outputs = none
  []
  [tritium_amount] # mol
    type = ParsedPostprocessor
    expression = 'Ni_membrane_amount+FLiBe_amount'
    pp_names = 'Ni_membrane_amount FLiBe_amount'
    # outputs = none
  []

  # top boundary
  [top_flux_density_Ni_membrane] # mol/m^2/s
    type = SideDiffusiveFluxAverage
    boundary = 'top_Ni'
    variable = 'tritium_concentration_Ni_membrane'
    diffusivity = ${D_Ni}
    outputs = none
  []
  [top_flux_Ni_membrane] # mol/s
    type = ParsedPostprocessor
    expression = 'top_flux_density_Ni_membrane*${thickness}*${length_Ni}'
    pp_names = 'top_flux_density_Ni_membrane'
    outputs = none
  []
  [top_flux_density_FLiBe] # mol/m^2/s
    type = SideDiffusiveFluxAverage
    boundary = 'top_FLiBe'
    variable = 'tritium_concentration_FLiBe'
    diffusivity = ${D_FLiBe}
    outputs = none
  []
  [top_flux_FLiBe] # mol/s
    type = ParsedPostprocessor
    expression = 'top_flux_density_FLiBe*${thickness}*${length_FLiBe}'
    pp_names = 'top_flux_density_FLiBe'
    outputs = none
  []
  [top_flux] # mol/s
    type = ParsedPostprocessor
    expression = 'top_flux_Ni_membrane + top_flux_FLiBe'
    pp_names = 'top_flux_Ni_membrane top_flux_FLiBe'
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

[Debug]
  show_var_residual_norms = true
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

