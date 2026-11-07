# Verification Problem #1l for Soret effect
# Tritium diffusion through semi-infinity layer under heat gradient

# Physical Constants
# This is to be consistent with TMAP8PhysicalConstants.h
# kb = '${units 1.380649e-23 J/K}' # Boltzmann constant
# R = '${units 8.31446261815324 J/mol/K}' # Gas constant

# Material properties
point_location = '${units 10 m}'
thickness = '${units 100 m}'
temperature_left = '${units 1 K}'
temperature_right = '${units 0 K}'
diffusivity = '${units 0.1 m^2/s}'
soret_coefficient = '${units 50 1/K}'
initial_concentration = '${units 0.1 mol/m^3}'
concentration_left = '${units 100 mol/m^3}'

simulation_time = '${units 100 s}'


[Mesh]
  type = GeneratedMesh
  dim = 1
  nx = 160
  xmax = '${thickness}'
[]

[AuxVariables]
  [temperature]
  []
[]

[AuxKernels]
  [temperature_kernel]
    type = ParsedAux
    use_xyzt = true
    variable = temperature
    expression = '(${temperature_right} - ${temperature_left}) / ${thickness} * x + ${temperature_left}'
    execute_on = 'initial timestep_end'
  []
[]

[Variables]
  # concentration in mol/m^3
  [concentration]
    initial_condition = '${initial_concentration}'
  []
[]

[Kernels]
  [time]
    type = ADTimeDerivative
    variable = concentration
  []
  [diffusion]
    type = ADMatDiffusion
    variable = concentration
    diffusivity = '${diffusivity}'
  []
  # Computes thermodiffusive flux: -D * S_T * C * grad(T)
  [thermodiffusion]
    type = ADThermoDiffusion
    variable = concentration
    temperature = 'temperature'
    soret_coefficient = 'thermodiffusion_prefactor'
  []
[]

[Materials]
  # Computes thermodiffusive prefactor: -D * S_T * C
  [thermodiffusion_prefactor]
    type = ADParsedMaterial
    property_name = 'thermodiffusion_prefactor'
    coupled_variables = 'concentration'
    expression = '${soret_coefficient} * ${diffusivity} * concentration'
  []
[]

[BCs]
  # The concentration of tritium on left is assumed constant
  [left]
    type = ADDirichletBC
    variable = concentration
    value = '${concentration_left}'
    boundary = 'left'
  []
  # The concentration of tritium on right is assumed impermeable
  [right]
    type = ADNeumannBC
    variable = concentration
    value = 0
    boundary = 'right'
  []
[]

[Postprocessors]
  # flux of tritium through the left surface
  [flux_surface_left]
    type = SideDiffusiveFluxIntegral
    variable = concentration
    diffusivity = '${diffusivity}'
    boundary = 'left'
    execute_on = 'initial timestep_end'
    outputs = 'console csv exodus'
  []
  # flux of tritium through the right surface
  [flux_surface_right]
    type = SideDiffusiveFluxIntegral
    variable = concentration
    diffusivity = '${diffusivity}'
    boundary = 'right'
    execute_on = 'initial timestep_end'
    outputs = 'console csv exodus'
  []
  # concentration at location
  [concentration_point]
    type = PointValue
    variable = concentration
    point = '${point_location} 0 0'
    outputs = 'csv'
  []
[]

[VectorPostprocessors]
  [line]
    type = LineValueSampler
    start_point = '0 0 0'
    end_point = '${thickness} 0 0'
    num_points = 101
    sort_by = 'x'
    variable = concentration
    outputs = 'vector_postproc'
  []
[]

[Executioner]
  type = Transient
  scheme = bdf2
  solve_type = NEWTON
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'

  nl_rel_tol = 1e-8
  nl_abs_tol = 1e-10
  end_time = '${simulation_time}'
  dtmax = 1
  automatic_scaling = true
  [TimeStepper]
    type = IterationAdaptiveDT
    optimal_iterations = 12
    iteration_window = 1
    growth_factor = 1.1
    dt = 1e-3
    cutback_factor = 0.9
    cutback_factor_at_failure = 0.9
  []
[]

[Outputs]
  exodus = true
  print_linear_residuals = false
  perf_graph = true
  [csv]
    type = CSV
    execute_on = 'initial timestep_end'
  []
  [console]
    type = Console
    time_step_interval = 10
  []
  [vector_postproc]
    type = CSV
    sync_times = '${simulation_time}'
    sync_only = true
  []
[]
