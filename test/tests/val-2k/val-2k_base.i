# Validation Problem val-2k
# Shared base input for a validation case based on experimental data from
# Kremer et al. (2022):
# https://doi.org/10.1016/j.nme.2022.101137
# Unit system:
# - length: micrometers
# - time: seconds
# - concentration: atoms / micrometer^3
# - flux: atoms / micrometer^2 / second
# This file assembles the common val-2k mesh, variables, postprocessors,
# executioner settings, and output controls, then includes the shared layer,
# trap, and surface model blocks.
!include val-2k_layer.i
!include val-2k_traps.i
!include val-2k_surface.i

[Mesh]
  active = mesh_fine
  [mesh_fine]
    type = CartesianMeshGenerator
    dim = 1
    dx = '${oxide_thickness_hat} ${left_refined_tungsten_depth_hat} ${damage_remainder_depth_hat} ${oxide_buffer_fine_depth_hat} ${oxide_buffer_coarse_depth_hat} ${oxide_bulk_depth_hat}'
    ix = '${ix_oxide_fine} ${ix_left_refined_tungsten_fine} ${ix_damage_remainder_fine} ${ix_buffer_fine} ${ix_buffer_coarse_fine} ${ix_bulk_fine}'
    subdomain_id = '0 0 0 0 0 0'
  []
  [mesh_coarse]
    type = CartesianMeshGenerator
    dim = 1
    dx = '${oxide_thickness_hat} ${left_refined_tungsten_depth_hat} ${damage_remainder_depth_hat} ${oxide_buffer_fine_depth_hat} ${oxide_buffer_coarse_depth_hat} ${oxide_bulk_depth_hat}'
    ix = '${ix_oxide_coarse} ${ix_left_refined_tungsten_coarse} ${ix_damage_remainder_coarse} ${ix_buffer_coarse} ${ix_buffer_coarse_coarse} ${ix_bulk_coarse}'
    subdomain_id = '0 0 0 0 0 0'
  []
[]

[Variables]
  [deuterium_mobile]
    order = FIRST
    family = LAGRANGE
    initial_condition = ${initial_mobile_concentration_hat}
  []
  [oxygen]
    order = FIRST
    family = LAGRANGE
  []
[]

[ICs]
  [oxygen_initial_condition]
    type = FunctionIC
    variable = oxygen
    function = oxygen_initial_distribution_function
  []
[]

[AuxVariables]
  active = 'bounds_dummy temperature oxygen_physical deuterium_mobile_physical deuterium_trapped_intrinsic_physical
  deuterium_trapped_1_physical deuterium_trapped_2_physical deuterium_trapped_3_physical
  deuterium_trapped_4_physical deuterium_trapped_5_physical deuterium_total_physical'
  [bounds_dummy]
    order = FIRST
    family = LAGRANGE
  []
  [temperature]
    initial_condition = ${temperature_initial}
  []
  [oxygen_physical]
  []
  [deuterium_mobile_physical]
  []
  [deuterium_trapped_intrinsic_physical]
    initial_condition = 0
  []
  [deuterium_trapped_1_physical]
    initial_condition = 0
  []
  [deuterium_trapped_2_physical]
    initial_condition = 0
  []
  [deuterium_trapped_3_physical]
    initial_condition = 0
  []
  [deuterium_trapped_4_physical]
    initial_condition = 0
  []
  [deuterium_trapped_5_physical]
    initial_condition = 0
  []
  [deuterium_total_physical]
  []
[]

[Bounds]
  [deuterium_mobile_lower_bound]
    type = ConstantBounds
    variable = bounds_dummy
    bounded_variable = deuterium_mobile
    bound_type = lower
    bound_value = 0
  []
  [oxygen_lower_bound]
    type = ConstantBounds
    variable = bounds_dummy
    bounded_variable = oxygen
    bound_type = lower
    bound_value = 0
  []
  [oxygen_upper_bound]
    type = ConstantBounds
    variable = bounds_dummy
    bounded_variable = oxygen
    bound_type = upper
    bound_value = 1
  []
[]

[Kernels]
  [mobile_time]
    type = TimeDerivative
    variable = deuterium_mobile
  []
  [mobile_diffusion]
    type = ADMatDiffusion
    variable = deuterium_mobile
    diffusivity = diffusivity_tungsten
  []
  [oxygen_time]
    type = TimeDerivative
    variable = oxygen
  []
  [oxygen_diffusion]
    type = ADMatDiffusion
    variable = oxygen
    diffusivity = diffusivity_oxygen
  []
[]

[AuxKernels]
  [temperature_aux]
    type = FunctionAux
    variable = temperature
    function = temperature_history
    execute_on = 'INITIAL LINEAR'
  []
  [oxygen_physical_aux]
    type = NormalizationAux
    variable = oxygen_physical
    normal_factor = ${oxygen_concentration_reference_m3}
    source_variable = oxygen
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [deuterium_mobile_physical_aux]
    type = NormalizationAux
    variable = deuterium_mobile_physical
    normal_factor = ${mobile_concentration_reference_m3}
    source_variable = deuterium_mobile
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [deuterium_trapped_intrinsic_physical_aux]
    type = NormalizationAux
    variable = deuterium_trapped_intrinsic_physical
    normal_factor = ${trap_concentration_reference_intrinsic_m3}
    source_variable = deuterium_trapped_intrinsic
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [deuterium_trapped_1_physical_aux]
    type = NormalizationAux
    variable = deuterium_trapped_1_physical
    normal_factor = ${trap_concentration_reference_1_m3}
    source_variable = deuterium_trapped_1
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [deuterium_trapped_2_physical_aux]
    type = NormalizationAux
    variable = deuterium_trapped_2_physical
    normal_factor = ${trap_concentration_reference_2_m3}
    source_variable = deuterium_trapped_2
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [deuterium_trapped_3_physical_aux]
    type = NormalizationAux
    variable = deuterium_trapped_3_physical
    normal_factor = ${trap_concentration_reference_3_m3}
    source_variable = deuterium_trapped_3
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [deuterium_trapped_4_physical_aux]
    type = NormalizationAux
    variable = deuterium_trapped_4_physical
    normal_factor = ${trap_concentration_reference_4_m3}
    source_variable = deuterium_trapped_4
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [deuterium_trapped_5_physical_aux]
    type = NormalizationAux
    variable = deuterium_trapped_5_physical
    normal_factor = ${trap_concentration_reference_5_m3}
    source_variable = deuterium_trapped_5
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [deuterium_total_physical_aux]
    type = ParsedAux
    variable = deuterium_total_physical
    coupled_variables = 'deuterium_mobile_physical deuterium_trapped_intrinsic_physical
    deuterium_trapped_1_physical deuterium_trapped_2_physical deuterium_trapped_3_physical
    deuterium_trapped_4_physical deuterium_trapped_5_physical'
    expression = 'deuterium_mobile_physical + deuterium_trapped_intrinsic_physical +
    deuterium_trapped_1_physical + deuterium_trapped_2_physical + deuterium_trapped_3_physical +
    deuterium_trapped_4_physical + deuterium_trapped_5_physical'
    execute_on = 'INITIAL TIMESTEP_END'
  []
[]

[Functions]
  [temperature_history]
    type = PiecewiseLinear
    data_file = gold/Experimental_desorption_temperature.csv
    format = columns
    x_title = 'time (s)'
    y_title = 'temperature (K)'
  []
[]

[Postprocessors]
  [temperature_pps]
    type = ElementAverageValue
    variable = temperature
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [integral_mobile]
    type = ElementIntegralVariablePostprocessor
    variable = deuterium_mobile
    outputs = none
  []
  [scaled_mobile]
    type = ScalePostprocessor
    scaling_factor = '${fparse mobile_concentration_reference * length_reference * ${units 1 m^2 -> mum^2}}'
    value = integral_mobile
  []
  [mobile_inventory_physical]
    type = ScalePostprocessor
    scaling_factor = 1
    value = scaled_mobile
  []
  [flux_surface_left_d2]
    type = ADSideAverageMaterialProperty
    boundary = left
    property = flux_recombination_surface_d2
    outputs = none
  []
  [scaled_flux_surface_left_d2]
    type = ScalePostprocessor
    scaling_factor = '${fparse -1 * mobile_concentration_reference * length_reference * ${units 1 m^2 -> mum^2} / time_reference}'
    value = flux_surface_left_d2
    execute_on = 'INITIAL LINEAR NONLINEAR TIMESTEP_END'
  []
  [flux_surface_left_d2_physical]
    type = ScalePostprocessor
    scaling_factor = 1
    value = scaled_flux_surface_left_d2
  []
  [flux_surface_left_d2o]
    type = ADSideAverageMaterialProperty
    boundary = left
    property = flux_recombination_surface_d2o
    outputs = none
  []
  [scaled_flux_surface_left_d2o]
    type = ScalePostprocessor
    scaling_factor = '${fparse -1 * mobile_concentration_reference * length_reference * ${units 1 m^2 -> mum^2} / time_reference}'
    value = flux_surface_left_d2o
    execute_on = 'INITIAL LINEAR NONLINEAR TIMESTEP_END'
  []
  [flux_surface_left_d2o_physical]
    type = ScalePostprocessor
    scaling_factor = 1
    value = scaled_flux_surface_left_d2o
  []
  [flux_surface_left_oxygen]
    type = ADSideAverageMaterialProperty
    boundary = left
    property = flux_recombination_surface_oxygen
    outputs = none
  []
  [scaled_flux_surface_left_oxygen]
    type = ScalePostprocessor
    scaling_factor = '${fparse -1 * oxygen_concentration_reference * length_reference * ${units 1 m^2 -> mum^2} / time_reference}'
    value = flux_surface_left_oxygen
    execute_on = 'INITIAL LINEAR NONLINEAR TIMESTEP_END'
  []
  [flux_surface_left_oxygen_physical]
    type = ScalePostprocessor
    scaling_factor = 1
    value = scaled_flux_surface_left_oxygen
  []
  [scaled_flux_surface_left]
    type = SumPostprocessor
    values = 'scaled_flux_surface_left_d2 scaled_flux_surface_left_d2o'
    execute_on = 'INITIAL LINEAR NONLINEAR TIMESTEP_END'
  []
  [flux_surface_left_physical]
    type = ScalePostprocessor
    scaling_factor = 1
    value = scaled_flux_surface_left
  []
  [flux_surface_right_d2]
    type = ADSideAverageMaterialProperty
    boundary = right
    property = flux_recombination_surface_d2
    outputs = none
  []
  [scaled_flux_surface_right_d2]
    type = ScalePostprocessor
    scaling_factor = '${fparse -1 * mobile_concentration_reference * length_reference * ${units 1 m^2 -> mum^2} / time_reference}'
    value = flux_surface_right_d2
    execute_on = 'INITIAL LINEAR NONLINEAR TIMESTEP_END'
  []
  [flux_surface_right_d2_physical]
    type = ScalePostprocessor
    scaling_factor = 1
    value = scaled_flux_surface_right_d2
  []
  [flux_surface_right_d2o]
    type = ADSideAverageMaterialProperty
    boundary = right
    property = flux_recombination_surface_d2o
    outputs = none
  []
  [scaled_flux_surface_right_d2o]
    type = ScalePostprocessor
    scaling_factor = '${fparse -1 * mobile_concentration_reference * length_reference * ${units 1 m^2 -> mum^2} / time_reference}'
    value = flux_surface_right_d2o
    execute_on = 'INITIAL LINEAR NONLINEAR TIMESTEP_END'
  []
  [flux_surface_right_d2o_physical]
    type = ScalePostprocessor
    scaling_factor = 1
    value = scaled_flux_surface_right_d2o
  []
  [flux_surface_right_oxygen]
    type = ADSideAverageMaterialProperty
    boundary = right
    property = flux_recombination_surface_oxygen
    outputs = none
  []
  [scaled_flux_surface_right_oxygen]
    type = ScalePostprocessor
    scaling_factor = '${fparse -1 * oxygen_concentration_reference * length_reference * ${units 1 m^2 -> mum^2} / time_reference}'
    value = flux_surface_right_oxygen
    execute_on = 'INITIAL LINEAR NONLINEAR TIMESTEP_END'
  []
  [flux_surface_right_oxygen_physical]
    type = ScalePostprocessor
    scaling_factor = 1
    value = scaled_flux_surface_right_oxygen
  []
  [scaled_flux_surface_right]
    type = SumPostprocessor
    values = 'scaled_flux_surface_right_d2 scaled_flux_surface_right_d2o'
    execute_on = 'INITIAL LINEAR NONLINEAR TIMESTEP_END'
  []
  [flux_surface_right_physical]
    type = ScalePostprocessor
    scaling_factor = 1
    value = scaled_flux_surface_right
  []
  [deuterium_inventory_in_sample]
    type = ElementIntegralVariablePostprocessor
    variable = deuterium_total_physical
    execute_on = 'INITIAL TIMESTEP_END'
    outputs = none
  []
  [deuterium_inventory_in_sample_physical]
    type = ScalePostprocessor
    scaling_factor = '${units 1 mum -> m}'
    value = deuterium_inventory_in_sample
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [oxygen_initial_inventory_in_sample]
    type = FunctionElementIntegral
    function = oxygen_initial_distribution_function
    execute_on = 'INITIAL TIMESTEP_END'
    outputs = none
  []
  [oxygen_initial_inventory_in_sample_physical]
    type = ScalePostprocessor
    scaling_factor = '${fparse oxygen_concentration_reference * length_reference * ${units 1 m^2 -> mum^2}}'
    value = oxygen_initial_inventory_in_sample
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [oxygen_inventory_in_sample]
    type = ElementIntegralVariablePostprocessor
    variable = oxygen
    execute_on = 'INITIAL TIMESTEP_END'
    outputs = none
  []
  [oxygen_inventory_in_sample_physical]
    type = ScalePostprocessor
    scaling_factor = '${fparse oxygen_concentration_reference * length_reference * ${units 1 m^2 -> mum^2}}'
    value = oxygen_inventory_in_sample
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [deuterium_release_flux_total]
    type = SumPostprocessor
    values = 'scaled_flux_surface_left scaled_flux_surface_right'
    execute_on = 'INITIAL TIMESTEP_END'
    outputs = none
  []
  [oxygen_release_flux_total]
    type = SumPostprocessor
    values = 'scaled_flux_surface_left_oxygen scaled_flux_surface_right_oxygen'
    execute_on = 'INITIAL TIMESTEP_END'
    outputs = none
  []
  [deuterium_released_physical]
    type = TimeIntegratedPostprocessor
    value = deuterium_release_flux_total
    time_integration_scheme = trapezoidal-rule
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [oxygen_released_physical]
    type = TimeIntegratedPostprocessor
    value = oxygen_release_flux_total
    time_integration_scheme = trapezoidal-rule
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [deuterium_inventory_change]
    type = ChangeOverTimePostprocessor
    postprocessor = deuterium_inventory_in_sample_physical
    change_with_respect_to_initial = true
    execute_on = 'INITIAL TIMESTEP_END'
    outputs = none
  []
  [oxygen_inventory_change]
    type = ChangeOverTimePostprocessor
    postprocessor = oxygen_inventory_in_sample_physical
    change_with_respect_to_initial = true
    execute_on = 'INITIAL TIMESTEP_END'
    outputs = none
  []
  [deuterium_mass_conservation_residual]
    type = ParsedPostprocessor
    pp_names = 'deuterium_inventory_change deuterium_released_physical'
    expression = 'deuterium_inventory_change + deuterium_released_physical'
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [oxygen_mass_conservation_residual]
    type = ParsedPostprocessor
    pp_names = 'oxygen_inventory_change oxygen_released_physical'
    expression = 'oxygen_inventory_change + oxygen_released_physical'
    execute_on = 'INITIAL TIMESTEP_END'
  []
[]

[VectorPostprocessors]
  [line_profile]
    type = LineValueSampler
    start_point = '0 0 0'
    end_point = '${profile_depth_hat} 0 0'
    num_points = ${profile_num_points}
    sort_by = x
    variable = 'oxygen_physical deuterium_total_physical deuterium_mobile_physical deuterium_trapped_intrinsic_physical
    deuterium_trapped_1_physical deuterium_trapped_2_physical deuterium_trapped_3_physical
    deuterium_trapped_4_physical deuterium_trapped_5_physical'
    execute_on = INITIAL
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
  end_time = ${end_time_hat}
  solve_type = Newton
  scheme = bdf2
  petsc_options_iname = '-pc_type -pc_factor_mat_solver_type -snes_type'
  petsc_options_value = 'lu       mumps                      vinewtonrsls'
  line_search = none
  automatic_scaling = true
  nl_rel_tol = 1e-7
  nl_abs_tol = 1e-10
  nl_max_its = 30
  l_tol = 1e-8
  dtmax = 20
  abort_on_solve_fail = true
  [TimeStepper]
    type = IterationAdaptiveDT
    dt = '${fparse 1 / time_reference}'
    optimal_iterations = 8
    growth_factor = 1.2
    cutback_factor = 0.8
  []
  [Predictor]
    type = SimplePredictor
    scale = 1.0
  []
[]

[Outputs]
  file_base = ${output_file_base}
  [exodus]
    type = Exodus
    # legacy value
    max_output_name_length = 32
    time_step_interval = 10
  []
  [csv]
    type = CSV
  []
  [profile_out]
    type = CSV
    sync_only = true
    sync_times = '0'
    execute_vector_postprocessors_on = 'INITIAL'
    execute_postprocessors_on = NONE
    file_base = ${profile_output_file_base}
  []
[]
