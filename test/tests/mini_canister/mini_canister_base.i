### This is the base input file for the mini-canister example case, which is
### incorporated into steel_only.i and gas_steel.i using the `!include` feature
### This file is not designed to be run on its own

[Variables]
  [H_mobile_steel] # Mobile H atoms within steel
    block = '1'
  []
[]

[Kernels]
  [steel_mobile_time]
    type = ADTimeDerivative
    variable = H_mobile_steel
    block = 1
  []
  [steel_mobile_diff]
    type = ADMatDiffusion
    variable = H_mobile_steel
    diffusivity = '${diffusivity_H_in_steel}'
    block = 1
  []
[]

[AuxVariables]
    [T] # Temperature
    initial_condition = ${temperature}
  []
[]

[AuxKernels]
  [constant_temperature]
    type = ConstantAux
    variable = T
    value = '${temperature}'
  []
[]

[BCs]
  [steel_air_boundary] # Boundary of steel and outside environment
    type = DirichletBC
    boundary = '1'
    value = 0
    variable = H_mobile_steel
  []
[]

[Postprocessors]

  [annulus_concentration_steel] # Axisymmetric: 2D integral of annulus
    type = ElementIntegralVariablePostprocessor
    variable = H_mobile_steel
    block = '1'
    outputs = none
  []

  [annular_cylinder_total_mass_steel]
    type = ScalePostprocessor
    value = annulus_concentration_steel
    scaling_factor = '${height}'
    outputs = csv
  []

  [outer_edge_outflux]
    type = ADSideDiffusiveFluxIntegral
    boundary = '1'
    variable = H_mobile_steel
    diffusivity = ${diffusivity_H_in_steel}
    outputs = none
  []
[]

[Executioner]
  type = Transient
  scheme = bdf2
  dtmax = '${dt_max}'
  dtmin = '${dt_min}'
  dt = '${dt_start}'
  automatic_scaling = true
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'
  end_time = ${endtime}
  [TimeStepper]
    type = IterationAdaptiveDT
    dt = ${dt_start}
    optimal_iterations = 5
    growth_factor = 1.1
    cutback_factor_at_failure = .9
  []
[]

[Outputs]
  csv = true
[]
