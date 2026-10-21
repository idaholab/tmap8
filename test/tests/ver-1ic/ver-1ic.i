# Verification Problem #1ic/1id from TMAP7 V&V document
# A Species Equilibration Problem in Surfdep Conditions with Low/High Barrier Energy

# Physical Constants
k = '${units 1.380649e-23 J/K}' # Boltzmann constant (from PhysicalConstants.h - https://physics.nist.gov/cgi-bin/cuu/Value?r)
amu = '${units 1.6605390666e-27 kg}' # Atomic mass unit

# Modeling parameters
end_time = '${units 10 s}'
time_interval = '${units 0.1 s}'
temperature = '${units 1000 K}' # Temperature
V = '${units 1 m^3}' # Volume
S = '${units 25 cm^2 -> m^2}' # Area
p0_A2 = '${units 1e4 Pa}' # Initial pressure for A2
p0_B2 = '${units 1e4 Pa}' # Initial pressure for B2
peq_AB = '${fparse 2 * p0_A2 * p0_B2 / ( p0_A2 + p0_B2 )}' # pressure in equilibration for AB

# Surface reaction parameters
E_x = '${units 0.05 eV -> J}'
E_c = '${units -0.01 eV -> J}'
E_b = '${units 0.00 eV -> J}'
nu = '${units 8.4e12 1/s}' # Debye frequency
M = '${fparse 2 * amu}'
K_d = '${units ${fparse 1 / sqrt(2 * pi * M * k * temperature) * exp( - E_x / ( k * temperature ) )} s/kg/m}' # deposition rate
K_r = '${fparse nu * exp((E_c - E_x) / k / temperature)}' # release rate
K_b = '${fparse nu * exp(- E_b / k / temperature)}' # dissociation rate
D_s_lamda = '${units ${fparse 5.3167e-7 * exp( -4529 / temperature )} m^4/at/s}'


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
  [c_A_dot_c_B]
  []
  [c_AB]
  []
  [p_A2]
    initial_condition = ${p0_A2}
  []
  [p_B2]
    initial_condition = ${p0_B2}
  []
[]

[AuxKernels]
  [c_A_dot_c_B_kernel]
    type = ParsedAux
    variable = c_A_dot_c_B
    # coupled_variables = 'p_AB c_A c_B'
    expression = ' ${peq_AB} * ${K_d} * ${K_b} / ${K_r} / 2 / ${D_s_lamda} '
  []
  [c_AB_kernel]
    type = ParsedAux
    variable = c_AB
    coupled_variables = 'p_AB c_A_dot_c_B'
    expression = ' (p_AB * ${K_d} + c_A_dot_c_B * 2 * ${D_s_lamda}) / ( ${K_r} + ${K_b} ) '
  []
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
[]

[Kernels]
  [timeDerivative_p_AB]
    type = ADTimeDerivative
    variable = p_AB
  []
  [MatReaction_p_AB_recombination]
    type = ADMatReactionFlexible
    variable = p_AB
    vs = 'c_A_dot_c_B'
    coeff = '${fparse 2 * S * k * temperature / V}'
    reaction_rate_name = '${D_s_lamda}'
  []
  [MatReaction_p_AB_dissociation]
    type = ADMatReactionFlexible
    variable = p_AB
    vs = 'c_AB'
    coeff = '${fparse - S * k * temperature / V}'
    reaction_rate_name = '${K_b}'
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
  nl_abs_tol = 1e-15

  solve_type = 'NEWTON'
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'

  end_time = ${end_time}
  dt = ${time_interval}
  automatic_scaling = true
[]

[Outputs]
  csv = true
[]
