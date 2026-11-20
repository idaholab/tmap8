# Jacobian test for ADMatReactionFlexible.
# The reaction terms depend on the kernel's own variable ('vs = c_a c_a' and 'vs = c_a c_b')
# and on a second nonlinear variable, which exercises both the diagonal and the off-diagonal
# Jacobian blocks. Units are arbitrary (the test only compares Jacobians).

[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 3
  ny = 3
[]

[Variables]
  [c_a]
    [InitialCondition]
      type = FunctionIC
      function = 'a_ic'
    []
  []
  [c_b]
    [InitialCondition]
      type = FunctionIC
      function = 'b_ic'
    []
  []
[]

[Functions]
  # Non-constant, non-linear initial conditions so that no derivative term vanishes by accident
  [a_ic]
    type = ParsedFunction
    expression = '1 + 0.5 * x * x + 0.3 * sin(3 * y)'
  []
  [b_ic]
    type = ParsedFunction
    expression = '2 - 0.4 * y * y + 0.2 * cos(2 * x)'
  []
[]

[Kernels]
  [time_a]
    type = ADTimeDerivative
    variable = c_a
  []
  [time_b]
    type = ADTimeDerivative
    variable = c_b
  []
  [self_reaction_a]
    # depends on the kernel's own variable twice
    type = ADMatReactionFlexible
    variable = c_a
    vs = 'c_a c_a'
    coeff = -2
    reaction_rate_name = K
  []
  [cross_reaction_a]
    # depends on the own variable and on another nonlinear variable
    type = ADMatReactionFlexible
    variable = c_a
    vs = 'c_a c_b'
    coeff = 1
    reaction_rate_name = K
  []
  [cross_reaction_b]
    # off-diagonal block: c_b residual depends on c_a and c_b
    type = ADMatReactionFlexible
    variable = c_b
    vs = 'c_a c_b'
    coeff = 1
    reaction_rate_name = K
  []
[]

[Materials]
  [K]
    type = ADGenericConstantMaterial
    prop_names = 'K'
    prop_values = '3'
  []
[]

[Preconditioning]
  [smp]
    type = SMP
    full = true
  []
[]

[Executioner]
  type = Transient
  solve_type = NEWTON
  num_steps = 1
  dt = 0.1
[]

[Outputs]
  exodus = false
[]
