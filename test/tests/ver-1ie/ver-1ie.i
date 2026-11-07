# Verification Problem #1ie/1if from TMAP7 V&V document
# A Species Equilibration Problem in Lawdep Condition with Equal/Unequal Starting Pressures

# Physical Constants
k = '${units 1.380649e-23 J/K}' # Boltzmann constant (from PhysicalConstants.h - https://physics.nist.gov/cgi-bin/cuu/Value?k)

# Modeling parameters
simulation_time = '${units 3 s}'
time_interval = '${units 0.01 s}'
T = '${units 1000 K}' # Temperature
V = '${units 1 m^3}' # Volume
S = '${units 25 cm^2 -> m^2}' # Area
p0_A2 = '${units 1e4 Pa}' # Initial pressure for A2
p0_B2 = '${units 1e4 Pa}' # Initial pressure for B2

# Surface reaction parameters
K_s = '${units 1.0e24 at/m^3/Pa^0.5}' # atom/m^3/pa^0.5 recombination rate for A2 or B2
K_d = '${units ${fparse 1.858e24 / sqrt( ${T} )} at/m^2/s/Pa}' # dissociation rate for AB
K_r = '${units ${fparse K_d / K_s / K_s} m^4/at/s}'

[Mesh]
  type = GeneratedMesh
  dim = 2
[]

[Variables]
  [p_AB]
    initial_condition = 0
  []
[]

[AuxVariables]
  [p_A2]
    initial_condition = ${p0_A2}
  []
  [p_B2]
    initial_condition = ${p0_B2}
  []
  [c_A]
  []
  [c_B]
  []
[]

[AuxKernels]
  [p_A2_kernel]
    type = ParsedAux
    variable = p_A2
    coupled_variables = 'p_AB'
    expression = '${p0_A2} - p_AB / 2'
  []
  [p_B2_kernel]
    type = ParsedAux
    variable = p_B2
    coupled_variables = 'p_AB'
    expression = '${p0_B2} - p_AB / 2'
  []
  [c_A_kernel]
    type = ParsedAux
    variable = c_A
    coupled_variables = 'p_A2'
    expression = '${K_s} * sqrt(p_A2)'
  []
  [c_B_kernel]
    type = ParsedAux
    variable = c_B
    coupled_variables = 'p_B2'
    expression = '${K_s} * sqrt(p_B2)'
  []
[]

[Kernels]
  [timeDerivative_p_AB]
    type = ADTimeDerivative
    variable = p_AB
  []
  [MatReaction_p_AB_recombination]
    type = ADMatReactionFlexible
    variable = p_AB
    vs = 'c_A c_B'
    coeff = '${fparse 2 * ${k} * ${T} * ${S} / ${V}}'
    reaction_rate_name = '${K_r}'
  []
  [MatReaction_p_AB_dissociation]
    type = ADMatReactionFlexible
    variable = p_AB
    vs = 'p_AB'
    coeff = '${fparse -1 * ${k} * ${T} * ${S} / ${V}}'
    reaction_rate_name = '${K_d}'
  []
[]

[BCs]
  [p_AB_neumann] # No flux on the sides
    type = NeumannBC
    variable = p_AB
    boundary = 'left right bottom top'
    value = 0
  []
[]

[Postprocessors]
  [pressure_A2]
    type = ElementAverageValue
    variable = p_A2
    execute_on = 'initial timestep_end'
  []
  [pressure_B2]
    type = ElementAverageValue
    variable = p_B2
    execute_on = 'initial timestep_end'
  []
  [pressure_AB]
    type = ElementAverageValue
    variable = p_AB
    execute_on = 'initial timestep_end'
  []
[]

[Executioner]
  type = Transient
  scheme = bdf2
  nl_rel_tol = 1e-10
  nl_abs_tol = 1e-10

  solve_type = 'NEWTON'
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'

  end_time = ${simulation_time}
  dt = ${time_interval}
  automatic_scaling = true
[]

[Outputs]
  csv = true
[]
