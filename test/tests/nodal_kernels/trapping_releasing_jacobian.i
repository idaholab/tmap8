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
  [Cm]
  []
  [Ct]
    initial_condition = 0.1
  []
  [T]
  []
[]
[ICs]
  [Tic]
    type = FunctionIC
    variable = T
    function = '500 + 200*x'
  []
  [Cmic]
    type = FunctionIC
    variable = Cm
    function = '0.2 + 0.3*x'
  []
[]
[Kernels]
  [dCm]
    type = TimeDerivative
    variable = Cm
  []
  [diffCm]
    type = Diffusion
    variable = Cm
  []
  [coup]
    type = ScaledCoupledTimeDerivative
    variable = Cm
    v = Ct
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
  [dCt]
    type = TimeDerivativeNodalKernel
    variable = Ct
  []
  [trap]
    type = TrappingNodalKernel
    variable = Ct
    temperature = T
    alpha_t = 2.0
    N = 1
    Ct0 = 0.5
    trapping_energy = 800
    mobile_concentration = Cm
  []
  [rel]
    type = ReleasingNodalKernel
    variable = Ct
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
