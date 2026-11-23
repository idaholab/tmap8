!include val-2h_parameters.params

# Materials properties
## diffusivity of tritium in FLiBe
D_FLiBe_prefactor = '${units 9.3e-7 m^2/s}'
D_FLiBe_energy = '${units 42e3 J/mol}'
D_FLiBe = '${units ${fparse D_FLiBe_prefactor * exp(- D_FLiBe_energy / (R*temperature_exp))} m^2/s}'
## Henry's law solubility for tritium in FLiBe
K_s_FLiBe_prefactor = '${units 7.9e-2 mol/m^3/Pa}'
K_s_FLiBe_energy = '${units 35e3 J/mol}'

# Initial conditions
initial_pressure = '${units 1210 Pa}' # input pressure
initial_concentration_FLiBe = '${units 1e-12 mol/m^3}'

# Geometry and mesh
length_Ni = '${units 2 mm -> m}' # Ni membrane thickness
num_nodes_Ni = 10
length_FLiBe = '${units 8.1 mm -> m}' # FLiBe membrane thickness
num_nodes_FLiBe = 100
thickness = '${units 1 m}'
width_inner = '${units 25 mm -> m}'

[Mesh]
  [cmg]
    type = CartesianMeshGenerator
    dim = 1
    dx = '${length_Ni} ${length_FLiBe}'
    ix = '${num_nodes_Ni} ${num_nodes_FLiBe}'
    subdomain_id = '1 2'
  []
  [interface_Ni_FLiBe]
    type = SideSetsBetweenSubdomainsGenerator
    input = cmg
    primary_block = '1'
    paired_block = '2'
    new_boundary = 'interface_Ni_FLiBe'
  []
  [interface_Ni_FLiBe_other_direction]
    type = SideSetsBetweenSubdomainsGenerator
    input = interface_Ni_FLiBe
    primary_block = '2'
    paired_block = '1'
    new_boundary = 'interface_Ni_FLiBe_other_direction'
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
    family = SCALAR
    initial_condition = ${initial_pressure}
  []
[]

[Kernels]
  # Diffusion in Ni membrane
  [diffusion_Ni]
    type = ADMatDiffusion
    variable = 'tritium_concentration_Ni_membrane'
    diffusivity = ${D_Ni}
    block = 1
  []
  [time_diff_Ni]
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
  [right_concentration]
    type = ADDirichletBC
    boundary = 'right'
    variable = 'tritium_concentration_FLiBe'
    value = 0.0
  []
[]

[InterfaceKernels]
  [interface_sorption_Ni_FLiBe]
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
    boundary = 'interface_Ni_FLiBe_other_direction'
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
  # left and right flux
  [left_flux_membrane] # mol/m^2/s
    type = SideDiffusiveFluxAverage
    boundary = 'left'
    variable = 'tritium_concentration_Ni_membrane'
    diffusivity = ${D_Ni}
    # outputs = none
  []
  [right_flux_membrane] # mol/m^2/s
    type = SideDiffusiveFluxAverage
    boundary = 'right'
    variable = 'tritium_concentration_FLiBe'
    diffusivity = ${D_FLiBe}
    # outputs = none
  []

  # Mass conservation
  ## left boundary
  [left_inventory] # mol/s
    type = ParsedPostprocessor
    expression = 'left_flux_membrane*${thickness}*${width_inner}'
    pp_names = 'left_flux_membrane'
    # outputs = none
  []
  ## right boundary
  [right_inventory] # mol/s
    type = ParsedPostprocessor
    expression = 'right_flux_membrane*${thickness}*${width_inner}'
    pp_names = 'right_flux_membrane'
    # outputs = none
  []
  ## in cell
  # []
  [Ni_membrane_inventory1] # mol/m^3
    type = ElementAverageValue
    variable = 'tritium_concentration_Ni_membrane'
    block = 1
    outputs = none
  []
  [Ni_membrane_inventory] # mol
    type = ParsedPostprocessor
    expression = 'Ni_membrane_inventory1*${thickness}*${length_Ni}*${width_inner}'
    pp_names = 'Ni_membrane_inventory1'
    outputs = none
  []
  [FLiBe_inventory1] # mol/m^3
    type = ElementAverageValue
    variable = 'tritium_concentration_FLiBe'
    block = 2
    outputs = none
  []
  [FLiBe_inventory] # mol
    type = ParsedPostprocessor
    expression = 'FLiBe_inventory1*${thickness}*${length_FLiBe}*${width_inner}'
    pp_names = 'FLiBe_inventory1'
    outputs = none
  []
  [tritium_inventory] # mol
    type = ParsedPostprocessor
    expression = 'Ni_membrane_inventory+FLiBe_inventory'
    pp_names = 'Ni_membrane_inventory FLiBe_inventory'
    # outputs = none
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
  solve_type = 'PJFNK'
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'
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
  file_base = 'val-2h_1D_823K_1210Pa'
  [csv]
    type = CSV
  []
  [exodus]
    type = Exodus
    time_step_interval = 200
  []
[]
