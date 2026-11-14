# Verification Problem #1gc from TMAP7 V&V document
# A Series Chemical Reaction

# Modeling parameters
concentration_A_0 = '${units 2.415e14 at/m^3 -> at/mum^3}' # atoms/microns^3 initial concentration of species A
k_1 = '${units 0.0125 1/s}' # 1/s reaction rate for first reaction
k_2 = '${units 0.0025 1/s}' # 1/s reaction rate for second reaction
end_time = '${units 1500 s}' # s

[Mesh]
  type = GeneratedMesh
  dim = 1
[]

[Variables]
  [c_A]
    initial_condition = ${concentration_A_0}
    scaling = 1e4
  []
  [c_B]
    scaling = 1e4
  []
  [c_C]
    scaling = 1e4
  []
[]

[Kernels]
  # Equation for species A
  [timeDerivative_c_A]
    type = ADTimeDerivative
    variable = c_A
  []
  [MatReaction_A]
    type = ADMatReactionFlexible
    variable = c_A
    vs = 'c_A'
    coeff = -1
    reaction_rate_name = K1
  []
  # Equation for species B
  [timeDerivative_c_B]
    type = TimeDerivative
    variable = c_B
  []
  [MatReaction_B_1]
    type = ADMatReactionFlexible
    variable = c_B
    vs = 'c_A'
    coeff = 1
    reaction_rate_name = K1
  []
  [MatReaction_B_2]
    type = ADMatReactionFlexible
    variable = c_B
    vs = 'c_B'
    coeff = -1
    reaction_rate_name = K2
  []
  # Equation for species C
  [timeDerivative_c_C]
    type = TimeDerivative
    variable = c_C
  []
  [MatReaction_C]
    type = ADMatReactionFlexible
    variable = c_C
    vs = 'c_B'
    coeff = 1
    reaction_rate_name = K2
  []
[]

[Materials]
  [K1]
    type = ADParsedMaterial
    property_name = 'K1'
    expression = ${k_1}
  []
  [K2]
    type = ADParsedMaterial
    property_name = 'K2'
    expression = ${k_2}
  []
[]

[BCs]
  [c_A_neumann]
    # No flux on the sides
    type = NeumannBC
    variable = c_A
    boundary = 'left right'
    value = 0
  []
  [c_B_neumann]
    # No flux on the sides
    type = NeumannBC
    variable = c_B
    boundary = 'left right'
    value = 0
  []
  [c_C_neumann]
    # No flux on the sides
    type = NeumannBC
    variable = c_C
    boundary = 'left right'
    value = 0
  []
[]

[Postprocessors]
  [concentration_A]
    type = ElementAverageValue
    variable = c_A
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [concentration_B]
    type = ElementAverageValue
    variable = c_B
    execute_on = 'INITIAL TIMESTEP_END'
  []
  [concentration_C]
    type = ElementAverageValue
    variable = c_C
    execute_on = 'INITIAL TIMESTEP_END'
  []
[]

[Executioner]
  type = Transient
  scheme = bdf2
  nl_rel_tol = 1e-9
  nl_abs_tol = 1e-8
  solve_type = 'NEWTON'
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'
  end_time = ${end_time}
  dtmax = 50
  [TimeStepper]
    type = IterationAdaptiveDT
    dt = 1.0
    # Newton converges in about 1 iteration per step, so the step size growth is set by growth_factor
    # (the iteration-count criterion is not reached). The RMSPE depends on this time step history.
    optimal_iterations = 4
    growth_factor = 1.05
    cutback_factor = 0.8
  []
[]

[Outputs]
  exodus = true
  csv = true
[]
