# Jacobian check of TrappingNodalKernel and ReleasingNodalKernel, including the temperature
# off-diagonal terms. Temperature is a solved variable and both activation energies are non-zero,
# so the dR/dT contributions are exercised. The PetscJacobianTester compares the hand-coded
# Jacobian against a finite-difference Jacobian.
# Units: arbitrary, self-consistent (concentrations in at.fr., time in s, temperature in K).
[Mesh]
  type = GeneratedMesh
  dim = 1
  nx = 4
[]

[Variables]
  [C_mobile]
  []
  [C_trapped]
    initial_condition = 0.1
  []
  [T]
  []
[]

[ICs]
  [T_initial]
    type = FunctionIC
    variable = T
    function = '500 + 200*x'
  []
  [C_mobile_initial]
    type = FunctionIC
    variable = C_mobile
    function = '0.2 + 0.3*x'
  []
[]

[Kernels]
  [dC_mobile]
    type = TimeDerivative
    variable = C_mobile
  []
  [diffC_mobile]
    type = Diffusion
    variable = C_mobile
  []
  [coupling]
    type = ScaledCoupledTimeDerivative
    variable = C_mobile
    v = C_trapped
  []
  [dT]
    type = TimeDerivative
    variable = T
  []
  [diffT]
    type = Diffusion
    variable = T
  []
[]

[NodalKernels]
  [dC_trapped]
    type = TimeDerivativeNodalKernel
    variable = C_trapped
  []
  [trap]
    type = TrappingNodalKernel
    variable = C_trapped
    temperature = T
    alpha_t = 2.0
    N = 1
    Ct0 = 0.5
    trapping_energy = 800
    mobile_concentration = C_mobile
  []
  [rel]
    type = ReleasingNodalKernel
    variable = C_trapped
    temperature = T
    alpha_r = 3.0
    detrapping_energy = 1500
  []
[]

[BCs]
  [l]
    type = DirichletBC
    variable = T
    boundary = left
    value = 500
  []
  [r]
    type = DirichletBC
    variable = T
    boundary = right
    value = 700
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
  num_steps = 1
  dt = 0.01
  solve_type = NEWTON
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'
[]

[Outputs]
[]
