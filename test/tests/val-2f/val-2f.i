# Validation Problem #2f
# Self-damaged Tungsten Effects on Deuterium Transport extended from an original model from
# Dark, J., Delaporte-Mathurin, R., Schwarz-Selinger, T., Hodille, E. A., Mougenot, J.,
# Charles, Y., & Grisolia, C. (2024). Modelling neutron damage effects on tritium transport
# in tungsten. Nuclear Fusion, 64(8), 086026.

!include parameters_val-2f.params
!include val-2f_trapping_intrinsic.i
!include val-2f_trapping_5.i
!include val-2f_trapping_4.i
!include val-2f_trapping_3.i
!include val-2f_trapping_2.i
!include val-2f_trapping_1.i

[Mesh]
  [cartesian_mesh]
    type = CartesianMeshGenerator
    dim = 1
    dx = '${dx1_hat} ${dx2_hat} ${dx3_hat} ${dx4_hat} ${dx5_hat}'
    ix = '${ix1} ${ix2} ${ix3} ${ix4} ${ix5}'
    subdomain_id = '0 0 0 0 0'
  []
[]

[Variables]
  [deuterium_concentration_W]
  []
[]

[AuxVariables]
  active = 'bounds_dummy temperature'
  [bounds_dummy]
    order = FIRST
    family = LAGRANGE
  []
  [temperature]
    initial_condition = ${temperature_initial}
  []
[]

[Bounds]
  [deuterium_concentration_lower_bound]
    type = ConstantBounds
    variable = bounds_dummy
    bounded_variable = deuterium_concentration_W
    bound_type = lower
    bound_value = 0
  []
[]

[Kernels]
  [time_W]
    type = TimeDerivative
    variable = deuterium_concentration_W
  []
  [diffusion_W]
    type = ADMatDiffusion
    variable = deuterium_concentration_W
    diffusivity = diffusivity_W
  []
  [source_deuterium]
    type = BodyForce
    variable = deuterium_concentration_W
    function = source_deuterium
  []
[]

[AuxKernels]
  [temperature_aux]
    type = FunctionAux
    variable = temperature
    function = temperature_bc_func
    execute_on = 'INITIAL LINEAR'
  []
[]

[BCs]
  active = 'left_recombination_flux right_recombination_flux'
  # Kinetic boundary conditions
  [left_recombination_flux]
    type = ADMatNeumannBC
    variable = deuterium_concentration_W
    boundary = left
    value = 1
    boundary_material = flux_recombination_surface
  []
  [right_recombination_flux]
    type = ADMatNeumannBC
    variable = deuterium_concentration_W
    boundary = right
    value = 1
    boundary_material = flux_recombination_surface
  []
  # Sieverts' boundary conditions
  [left_concentration_sieverts]
    type = ADDirichletBC
    value = '${sieverts_boundary_hat}'
    boundary = left
    variable = deuterium_concentration_W
  []
  [right_concentration_sieverts]
    type = ADDirichletBC
    value = '${sieverts_boundary_hat}'
    boundary = right
    variable = deuterium_concentration_W
  []
[]

[Functions]
  [temperature_bc_func]
    type = ParsedFunction
    expression = 'if(t<${charge_time_hat}, ${temperature_initial},
                  if(t<${fparse charge_time_hat + cooldown_duration_hat}, ${temperature_cooldown},
                  ${temperature_desorption_min}+${desorption_heating_rate_hat}*(t-${fparse charge_time_hat + cooldown_duration_hat})))'
  []
  [source_distribution]
    type = ParsedFunction
    expression = '1 / (${sigma_hat} * sqrt(2 * pi)) * exp(-0.5 * ((x - ${R_p_hat}) / ${sigma_hat}) ^ 2)'
  []
  [surface_flux_func]
    type = ParsedFunction
    expression = 'if(t<${charge_time_hat}, ${surface_flux_hat}, 0)'
  []
  [source_deuterium]
    type = ParsedFunction
    symbol_names = 'source_distribution surface_flux_func'
    symbol_values = 'source_distribution surface_flux_func'
    expression = 'source_distribution * surface_flux_func'
  []
  [max_dt_size_function]
    type = ParsedFunction
    expression = 'if(t<${fparse 5 / time_reference}, ${fparse 1e-2 / time_reference},
                  if(t<${fparse 8 / time_reference}, ${fparse 1e2 / time_reference},
                  if(t<${fparse 12 / time_reference}, ${fparse 1e-2 / time_reference},
                  if(t<${fparse 20 / time_reference}, ${fparse 1e2 / time_reference},
                  if(t<${fparse 35 / time_reference}, ${fparse 1e-2 / time_reference},
                  if(t<${fparse 450 / time_reference}, ${fparse 1e2 / time_reference},
                  if(t<${fparse 5000 / time_reference}, ${fparse 1e1 / time_reference},
                  if(t<${fparse 11000 / time_reference}, ${fparse 1e2 / time_reference},
                  if(t<${fparse 13000 / time_reference}, ${fparse 1e1 / time_reference},
                  if(t<${fparse (charge_time + cooldown_duration + 4500) / time_reference}, ${fparse 1e2 / time_reference},
                  if(t<${fparse 313000 / time_reference}, ${fparse 1e2 / time_reference},
                  if(t<${fparse 315000 / time_reference}, ${fparse 1e1 / time_reference}, ${fparse 1e3 / time_reference}))))))))))))'
  []
  [max_dt_size_function_inf]
    type = ParsedFunction
    expression = 'if(t<${fparse 5 / time_reference}, ${fparse 1e-2 / time_reference},
                  if(t<${fparse 8 / time_reference}, ${fparse 1e2 / time_reference},
                  if(t<${fparse 12 / time_reference}, ${fparse 1e-2 / time_reference},
                  if(t<${fparse 20 / time_reference}, ${fparse 1e2 / time_reference},
                  if(t<${fparse 35 / time_reference}, ${fparse 1e-2 / time_reference},
                  if(t<${fparse 450 / time_reference}, ${fparse 1e2 / time_reference},
                  if(t<${fparse 5000 / time_reference}, ${fparse 1e1 / time_reference},
                  if(t<${fparse 11000 / time_reference}, ${fparse 1e2 / time_reference},
                  if(t<${fparse 13000 / time_reference}, ${fparse 1e1 / time_reference},
                  if(t<${fparse (charge_time + cooldown_duration + 4500) / time_reference}, ${fparse 1e2 / time_reference},
                  if(t<${fparse 315000 / time_reference}, ${fparse 1e1 / time_reference}, ${fparse 1e3 / time_reference})))))))))))'
  []
  [max_dt_size_function_coarse]
    type = ParsedFunction
    expression = 'if(t<${fparse 1e-1 / time_reference}, ${fparse 1e4 / time_reference}, ${fparse 1e5 / time_reference})'
  []
[]

[Materials]
  active = 'diffusivity_W_func diffusivity_nonAD recombination_rate_surface flux_recombination_surface'
  [diffusivity_W_func]
    type = ADDerivativeParsedMaterial
    property_name = 'diffusivity_W'
    functor_names = 'temperature_bc_func'
    functor_symbols = 'temperature'
    expression = '${diffusion_W_preexponential_hat} * exp(- ${diffusion_W_energy} / ${kb_eV} / temperature)'
  []
  [diffusivity_nonAD]
    type = MaterialADConverter
    ad_props_in = 'diffusivity_W'
    reg_props_out = 'diffusivity_W_nonAD'
  []
  [recombination_rate_surface]
    type = ADDerivativeParsedMaterial
    property_name = 'Kr'
    functor_names = 'temperature_bc_func'
    functor_symbols = 'temperature'
    expression = '${recombination_coefficient_hat} * exp(- ${recombination_energy} / ${kb_eV} / temperature)'
  []
  [flux_recombination_surface]
    type = ADDerivativeParsedMaterial
    coupled_variables = 'deuterium_concentration_W'
    property_name = 'flux_recombination_surface'
    material_property_names = 'Kr'
    expression = '- 2 * Kr * deuterium_concentration_W ^ 2'
  []
[]

[Postprocessors]
  active = 'integral_source_deuterium scaled_implanted_deuterium integral_deuterium_concentration
  scaled_mobile_deuterium flux_surface_left scaled_flux_surface_left
  flux_surface_right scaled_flux_surface_right temperature_pps diffusion_W_hat diffusion_W
  max_time_step_size max_time_step_size_coarse integral_trapped_concentration_1 scaled_trapped_deuterium_1
  integral_trapped_concentration_2 scaled_trapped_deuterium_2 integral_trapped_concentration_3 scaled_trapped_deuterium_3
  integral_trapped_concentration_4 scaled_trapped_deuterium_4 integral_trapped_concentration_5 scaled_trapped_deuterium_5
  integral_trapped_concentration_intrinsic scaled_trapped_deuterium_intrinsic
  spatial_max_mobile_d2 spatial_max_trapped_1 spatial_max_trapped_2 spatial_max_trapped_3 spatial_max_trapped_4 spatial_max_trapped_5 spatial_max_trapped_intrinsic
  max_mobile_d2 max_trapped_1 max_trapped_2 max_trapped_3 max_trapped_4 max_trapped_5 max_trapped_intrinsic max_scaled_flux_surface_left max_scaled_flux_surface_right
  max_scaled_mobile_deuterium max_scaled_trapped_deuterium_intrinsic'
  [integral_source_deuterium]
    type = FunctionElementIntegral
    function = source_deuterium
    outputs = none
  []
  [scaled_implanted_deuterium]
    type = ScalePostprocessor
    scaling_factor = '${fparse mobile_concentration_reference * length_reference * ${units 1 m^2 -> mum^2} / time_reference}'
    value = integral_source_deuterium
  []
  [integral_deuterium_concentration]
    type = ElementIntegralVariablePostprocessor
    variable = deuterium_concentration_W
    outputs = none
  []
  [scaled_mobile_deuterium]
    type = ScalePostprocessor
    scaling_factor = '${fparse mobile_concentration_reference * length_reference * ${units 1 m^2 -> mum^2}}'
    value = integral_deuterium_concentration
  []
  [max_scaled_mobile_deuterium]
    type = TimeExtremeValue
    postprocessor = scaled_mobile_deuterium
    value_type = max
    outputs = 'console'
  []
  [flux_surface_left]
    type = ADSideAverageMaterialProperty
    boundary = 'left'
    property = flux_recombination_surface
    outputs = none
  []
  [scaled_flux_surface_left]
    type = ScalePostprocessor
    scaling_factor = '${fparse -1 * mobile_concentration_reference * length_reference * ${units 1 m^2 -> mum^2} / time_reference}'
    value = flux_surface_left
    execute_on = 'initial nonlinear linear timestep_end'
  []
  [max_scaled_flux_surface_left]
    type = TimeExtremeValue
    postprocessor = scaled_flux_surface_left
    execute_on = 'initial timestep_end'
    outputs = 'console'
  []
  [flux_surface_left_sieverts]
    type = SideDiffusiveFluxAverage
    variable = deuterium_concentration_W
    boundary = 'left'
    diffusivity = 'diffusivity_W_nonAD'
    outputs = none
  []
  [scaled_flux_surface_left_sieverts]
    type = ScalePostprocessor
    scaling_factor = '${fparse mobile_concentration_reference * length_reference * ${units 1 m^2 -> mum^2} / time_reference}'
    value = flux_surface_left_sieverts
    execute_on = 'initial nonlinear linear timestep_end'
  []
  [max_scaled_flux_surface_left_sieverts]
    type = TimeExtremeValue
    postprocessor = scaled_flux_surface_left_sieverts
    value_type = max
  []
  [flux_surface_right]
    type = ADSideAverageMaterialProperty
    boundary = 'right'
    property = flux_recombination_surface
    outputs = none
  []
  [scaled_flux_surface_right]
    type = ScalePostprocessor
    scaling_factor = '${fparse -1 * mobile_concentration_reference * length_reference * ${units 1 m^2 -> mum^2} / time_reference}'
    value = flux_surface_right
    execute_on = 'initial nonlinear linear timestep_end'
  []
  [max_scaled_flux_surface_right]
    type = TimeExtremeValue
    postprocessor = scaled_flux_surface_right
    execute_on = 'initial timestep_end'
    outputs = 'console'
  []
  [flux_surface_right_sieverts]
    type = SideDiffusiveFluxAverage
    variable = deuterium_concentration_W
    boundary = 'right'
    diffusivity = 'diffusivity_W_nonAD'
    outputs = none
  []
  [scaled_flux_surface_right_sieverts]
    type = ScalePostprocessor
    scaling_factor = '${fparse -1 * mobile_concentration_reference * length_reference * ${units 1 m^2 -> mum^2} / time_reference}'
    value = flux_surface_right_sieverts
    execute_on = 'initial nonlinear linear timestep_end'
  []
  [max_scaled_flux_surface_right_sieverts]
    type = TimeExtremeValue
    postprocessor = scaled_flux_surface_right_sieverts
    value_type = max
  []
  [temperature_pps]
    type = ElementAverageValue
    variable = temperature
    execute_on = 'initial timestep_end'
  []
  [diffusion_W_hat]
    type = ElementAverageMaterialProperty
    mat_prop = diffusivity_W_nonAD
    outputs = none
  []
  [diffusion_W]
    type = ScalePostprocessor
    scaling_factor = '${fparse length_reference ^ 2 / time_reference}'
    value = diffusion_W_hat
    outputs = none
  []
  [max_time_step_size]
    type = FunctionValuePostprocessor
    function = max_dt_size_function
    execute_on = 'initial nonlinear linear timestep_end'
    outputs = none
  []
  [max_time_step_size_coarse]
    type = FunctionValuePostprocessor
    function = max_dt_size_function_coarse
    execute_on = 'initial nonlinear linear timestep_end'
    outputs = none
  []

  [spatial_max_mobile_d2]
    type = NodalExtremeValue
    value_type = 'max'
    variable = deuterium_concentration_W
    execute_on = 'initial timestep_end'
    outputs = 'console'
  []
  [spatial_max_trapped_1]
    type = NodalExtremeValue
    value_type = 'max'
    variable = trapped_1
    execute_on = 'initial timestep_end'
    outputs = 'console'
  []
  [spatial_max_trapped_2]
    type = NodalExtremeValue
    value_type = 'max'
    variable = trapped_2
    execute_on = 'initial timestep_end'
    outputs = 'console'
  []
  [spatial_max_trapped_3]
    type = NodalExtremeValue
    value_type = 'max'
    variable = trapped_3
    execute_on = 'initial timestep_end'
    outputs = 'console'
  []
  [spatial_max_trapped_4]
    type = NodalExtremeValue
    value_type = 'max'
    variable = trapped_4
    execute_on = 'initial timestep_end'
    outputs = 'console'
  []
  [spatial_max_trapped_5]
    type = NodalExtremeValue
    value_type = 'max'
    variable = trapped_5
    execute_on = 'initial timestep_end'
    outputs = 'console'
  []
  [spatial_max_trapped_intrinsic]
    type = NodalExtremeValue
    value_type = 'max'
    variable = trapped_intrinsic
    execute_on = 'initial timestep_end'
    outputs = 'console'
  []
  [max_mobile_d2]
    type = TimeExtremeValue
    value_type = 'max'
    postprocessor = spatial_max_mobile_d2
    execute_on = 'initial timestep_end'
    outputs = 'console'
  []
  [max_trapped_1]
    type = TimeExtremeValue
    value_type = 'max'
    postprocessor = spatial_max_trapped_1
    execute_on = 'initial timestep_end'
    outputs = 'console'
  []
  [max_trapped_2]
    type = TimeExtremeValue
    value_type = 'max'
    postprocessor = spatial_max_trapped_2
    execute_on = 'initial timestep_end'
    outputs = 'console'
  []
  [max_trapped_3]
    type = TimeExtremeValue
    value_type = 'max'
    postprocessor = spatial_max_trapped_3
    execute_on = 'initial timestep_end'
    outputs = 'console'
  []
  [max_trapped_4]
    type = TimeExtremeValue
    value_type = 'max'
    postprocessor = spatial_max_trapped_4
    execute_on = 'initial timestep_end'
    outputs = 'console'
  []
  [max_trapped_5]
    type = TimeExtremeValue
    value_type = 'max'
    postprocessor = spatial_max_trapped_5
    execute_on = 'initial timestep_end'
    outputs = 'console'
  []
  [max_trapped_intrinsic]
    type = TimeExtremeValue
    value_type = 'max'
    postprocessor = spatial_max_trapped_intrinsic
    execute_on = 'initial timestep_end'
    outputs = 'console'
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
  scheme = bdf2
  solve_type = 'Newton'
  petsc_options_iname = '-pc_type -pc_factor_mat_solver_type -snes_type'
  petsc_options_value = 'lu       mumps                      vinewtonrsls'
  end_time = ${endtime_hat}
  line_search = 'none'
  nl_rel_tol = 1e-8
  nl_abs_tol = 4e-5
  nl_max_its = 34
  [TimeStepper]
    type = IterationAdaptiveDT
    dt = '${fparse dt_init / time_reference}'
    growth_factor = 1.1
    timestep_limiting_postprocessor = max_time_step_size
  []
  [Predictor]
    type = SimplePredictor
    scale = 1.0
  []
[]

[Debug]
  show_var_residual_norms = true
[]

[Outputs]
  [csv]
    type = CSV
    file_base = 'val-2f_out'
  []
  [csv_temperature_history]
    type = CSV
    show = 'temperature_pps'
    file_base = 'val-2f_temperature_out'
  []
  [exodus]
    type = Exodus
    output_material_properties = true
    time_step_interval = 200
    file_base = 'val-2f_out'
  []
[]
