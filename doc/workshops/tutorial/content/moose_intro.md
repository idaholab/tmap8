# Introduction to MOOSE

!---

# MOOSE Framework: Overview

!row!
!col! width=50%

!media large_media/tutorials/darcy_thermo_mech/moose_intro.png alt=MOOSE framework introduction diagram

!col-end!

!col! width=50%

- Developed by Idaho National Laboratory since 2008
- Used for studying and analyzing nuclear reactor problems
- Free and open source (LGPLv2 license)
- Large user community (5000+ unique visitors/month)
- Highly parallel and HPC capable
- Developed and supported by full time INL staff - long-term support
- https://www.mooseframework.inl.gov

!col-end!
!row-end!

!---

# MOOSE Framework: Key features

!row!
!col! width=50%

!media large_media/tutorials/darcy_thermo_mech/moose_systems.png alt=MOOSE framework systems diagram

!col-end!

!col! width=50%

- Massively parallel computation - successfully run on >100,000 processor cores
- Multiphysics solve capability - fully coupled and implicit solver
- Multiscale solve capability - multiple applications can perform computation for a problem simultaneously
- Provides high level interface to implement customized physics, geometries, boundary conditions, and material models
- Initially developed to support nuclear R&D but now widely used for non-nuclear R&D also

!col-end!
!row-end!

!---

# MOOSE Framework: Core Philosophy

- +Object-oriented design+ : Everything is an object with clear interfaces
- +Modular architecture+ : Mix and match components and/or physics to achieve simulation goals
- +Supporting Many Physics+ : Framework handles numerics, you focus on physics
- +Dimension-independent+ : Run in 1D, 2D, or 3D with minimal changes to the input file
- +Automatic differentiation+ : No need to compute Jacobians manually

!---

# MOOSE Framework: Applications

!media large_media/tutorials/darcy_thermo_mech/moose_herd_2022.png alt=MOOSE workshop group photo style=width:100%;margin-left:auto;margin-right:auto;display:block;

!---

# MOOSE Systems Architecture

!row!
!col! width=40%

+Core Systems:+

- Mesh
- Variables
- Kernels
- BCs
- Materials
- AuxKernels
- Functions

!col-end!

!col! width=60%

+Advanced Systems:+

- MultiApps (multi-scale coupling)
- Transfers (data exchange)
- Postprocessors (scalar values)
- VectorPostprocessors (vector values)
- UserObjects (custom algorithms)
- Controls (runtime parameter modification)
- Executioner (solve control)

!col-end!
!row-end!

- Each system has specific responsibilities
- Systems interact through well-defined interfaces
- Objects can be mixed and matched

!---

# MOOSE Systems Architecture \\ example for a TMAP8-relevant case

The upcoming slides will describe the main components of the MOOSE systems architecture. This slide illustrates in which context different systems are used in a TMAP8-relevant case.

Let's assume one wants to model hydrogen and tritium transport through the metallic walls of a pipe.
The model would include diffusion, decay, and reactions between diatomic molecules inside the pipe; surface reactions at the inner and outer walls; and diffusion, decay, and trapping for single atoms in the walls.
The figure below illustrates the case and specifies how MOOSE's systems would apply when constructing the case in a MOOSE input file:

!media figures/TMAP8_workshop_case_illustration.png alt=TMAP8 workshop case illustration style=display:block;margin-left:auto;margin-right:auto;width:80%;

!---

# The Finite Element Method in MOOSE

MOOSE solves PDEs using the Galerkin finite element method (the finite volume method is also available for fluid flow).

+Key steps:+

1. Write strong form of PDE
2. Convert to weak form (multiply by test function, integrate by parts)
3. Discretize with shape functions
4. Form residual vector and Jacobian matrix
5. Solve nonlinear system with Newton's method

+MOOSE handles:+

- Mesh management
- Shape functions
- Quadrature rules
- Assembly process
- Parallel decomposition

!---

# Example: Strong form, weak form, and implementation

!media large_media/tutorials/darcy_thermo_mech/moose_code.png alt=MOOSE code example diagram style=display:block;margin-left:auto;margin-right:auto;

!---

# Kernels System: Building PDEs

!row!
!col! width=60%

```cpp
class DiffusionKernel : public ADKernel
{
protected:
  virtual ADReal computeQpResidual() override
  {
    return _grad_test[_i][_qp] * _grad_u[_qp];
  }
};
```

!col-end!

!col! width=40%

- Kernels represent volume terms in PDEs
- Each kernel computes one term
- Automatic differentiation for Jacobians
- Mix kernels to build complex equations

!col-end!
!row-end!

+Available variables:+

- `_u`, `_grad_u`: Variable value and gradient
- `_test`, `_grad_test`: Test function value and gradient
- `_qp`: Quadrature point index
- `_q_point`: Physical coordinates

!---

# Special Note: NodalKernels System


+Purpose+: Compute residual contributions at nodes rather than quadrature points

!row!
!col! width=50%

+When to Use NodalKernels:+

- Non-diffusive species
- ODEs or time-derivative only terms
- Point sources or sinks
- Reaction terms without spatial derivatives
- Lumped parameter models

!col-end!

!col! width=5%
!! intentionally empty column to produce whitespace separation between listing snippet that goes out-of-box and the right-hand column
!col-end!

!col! width=50%

+Key Differences from Kernels:+

- Operates on nodes, not elements
- No spatial gradients available
- `_qp = 0` always (single evaluation point)
- No test function needed in residual
- More efficient for non-spatial terms

!col-end!
!row-end!

!row!
!col! width=50%

+Implementation:+

```cpp
  ADReal
  ReactionNodalKernel::computeQpResidual()
  {
    // Note: _qp = 0 for nodal kernels
    // (evaluated at only a single point)
    return _coef * _u[_qp];
  }
};
```

!col-end!

!col! width=5%
!! intentionally empty column to produce whitespace separation between listing snippet that goes out-of-box and the right-hand column
!col-end!

!col! width=50%

+Input File Example:+

```
[NodalKernels]
  ...
  [decay]
    type = ReactionNodalKernel
    variable = C_tritium
    coef = 1.0
  []
[]
```

!col-end!
!row-end!

!---

# NodalKernels in TMAP8

Nodal kernels are used to model non-diffusive species. In the case of TMAP8, nodal kernels are key to modeling trapped species. For example, these are used in the [Ver-1d verification case](ver-1d.md) and several validation cases.

+Application Examples:+

- Trap filling/release (Ver-1d)
- Surface reactions at nodes

!---

# Materials System: Property Management

!row!
!col! width=60%

+Producer/Consumer Pattern:+

- Materials produce properties than can be used in the rest of the simulation
- Other objects (including other materials), can consume properties
- Properties can vary in space and time
- Properties can be functions of variables or other properties

!col-end!

!col! width=2%
!! test
!col-end!

!col! width=38%

```cpp
// Material object, in the constructor
_permeability(declareADProperty<Real>("permeability"))
// In the compute method
_permeability = 2.0;

// Consumer object (Kernel, BCs, etc.) in the constructor
_permeability(getADMaterialProperty<Real>("permeability"))

// In the "computeQp..." method
ADReal
SomeObject::computeQpResidual() {
return _permeability[_qp] * _grad_u[_qp] * _grad_test[_qp];
}
```

!col-end!
!row-end!

+Key Methods:+

- `declareProperty<Type>()` - produce a standard material property in a material object
- `getMaterialProperty<Type>()` - consume a standard material property in a MOOSE object
- `declareADProperty<Type>()` - produce an AD material property in a material object
- `getADMaterialProperty<Type>()` - consume an AD material property in a MOOSE object

!---

# Boundary Condition System

+Purpose+: Apply constraints at domain boundaries

!row!
!col! width=45%

+Mathematical Forms:+

- +Dirichlet+: $u = g$ on $\Gamma$
- +Neumann+: $\nabla u \cdot n = h$ on $\Gamma$
- +Robin (Mixed)+: $\alpha u + \beta \nabla u \cdot n = \gamma$ on $\Gamma$

+Base Classes:+

- `NodalBC`: Applied at nodes (Dirichlet)
- `IntegratedBC`: Applied over sides (Neumann/Robin)
- AD versions for automatic differentiation

!col-end!

!col! width=50%

+Common BCs in MOOSE/TMAP8:+

- `DirichletBC`: Fixed value
- `NeumannBC`: Fixed flux
- `FunctionDirichletBC`: Time/space varying
- `VacuumBC`: Vacuum boundary condition for diffusive species
- `ConvectiveFluxBC`: Convective heat transfer
- `BinaryRecombinationBC`: Recombination of atoms into molecules
- `EquilibriumBC`: Sorption laws (Sieverts' or Henry's)

!col-end!
!row-end!

!---

# TMAP8 BC Example \\ Binary Recombination

This capability is located in the MOOSE Scalar Transport Module ([Link](https://github.com/idaholab/moose/blob/next/modules/scalar_transport/src/bcs/BinaryRecombinationBC.C)). More information about the surface models available in TMAP8 is available in the [theory manual](https://mooseframework.inl.gov/TMAP8/theory_manual.html).

Weak form:

!equation
\int_{\Omega} \psi_i K_r u v d\Omega

Input file:

!listing multiple-species.i block=BCs/ht_t_left

!---

# TMAP8 BC Example \\ Binary Recombination (continued)

Source:

!listing moose/modules/scalar_transport/src/bcs/BinaryRecombinationBC.C


!---

# InterfaceKernel System

+Purpose+: Couple physics across internal interfaces between subdomains

!row!
!col! width=47%

+Key Concepts:+

- Operates on internal subdomain boundaries
- Accesses both sides (primary/neighbor)
- Used to enforce flux continuity and jump conditions

!col-end!

!col! width=50%

+Applications:+

- Material interfaces (metal/ceramic)
- Phase boundaries
- Membrane transport
- Contact mechanics

!col-end!
!row-end!

+TMAP8 Usage:+

- Metal/coating permeation barriers
- Multi-layer diffusion
- Interface trapping/sorption (see [theory manual](https://mooseframework.inl.gov/TMAP8/theory_manual.html))

!---

# TMAP8 Example: InterfaceSorption

!row!
!col! width=48%

Computes a sorption law at the interface between solid and gas in isothermal conditions.

!equation
C_s = K P^n = K(C_g RT)^n

where:

- $R$ = ideal gas constant (J/mol/K)
- $T$ = temperature (K)
- $K$ = solubility (units depend on $C_s$ and $P$)

!equation
K = K_0 \exp \left(\frac{-E_a}{RT}\right)

- $K_0$ = pre-exponential constant
- $E_a$ = activation energy (J/mol)
- $n$ = sorption law exponent (1 = Henry's, 1/2 = Sieverts')


!col-end!

!col! width=2%
!! intentionally empty column to produce whitespace separation between listing snippet that goes out-of-box and the right-hand column
!col-end!

!col! width=50%

+InterfaceKernels block in Input File ([ver-1kb](https://mooseframework.inl.gov/TMAP8/verification_and_validation/ver-1kb.html)):+

!listing test/tests/ver-1kb/ver-1kb.i block=InterfaceKernels

!col-end!
!row-end!

!---

# Auxiliary System: Arbitrarily Calculated Variables

- +Purpose+: Variables that are not solved for as part of a PDE/ODE.
- +Use cases+: Postprocessing, visualization, coupling

!row!
!col! width=50%

+Auxiliary Variables:+

- Not solved for directly
- Can be computed from other variables
- Can be computed directly or imposed

  - Example: temperature/pressure with a set history

- Can be nodal or elemental

!col-end!

!col! width=50%

+Example: Flux Vector from Concentration+

!equation
\vec{J} = -D \nabla C

- Concentration ($C$) is a nonlinear variable, computed by the solver.
- Diffusive flux ($\vec{J}$) is an auxiliary variable.
- Expression is computed via AuxKernel ([DiffusionFluxAux](https://mooseframework.inl.gov/TMAP8/source/auxkernels/DiffusionFluxAux.html))

!col-end!
!row-end!

!---

# Another Aux Example: Temperature

This is sampled from the [val-2b validation case](val-2b.md). First, we need to declare the `temperature` variable, as we would any other variable. Except, we do it here under the `AuxVariables` block. Then, we set up an `AuxKernel` to calculate it using a time-dependent function.

!listing val-2b.i block=AuxVariables/temperature

!listing val-2b.i block=AuxKernels/temperature_aux

!---

# Example, cont.: Aux Temperature in a BC

Now, `temperature` can be used wherever a regular `MooseVariable` is used. For example, we use it in [val-2b](val-2b.md) in an [EquilibriumBC](EquilibriumBC.md) boundary condition on the `left` boundary.

!listing val-2b.i block=BCs/left_flux

!---

# Input File System: HIT Format

!row!
!col! width=45%

+Example: simple_diffusion.i:+

!listing tutorials/tutorial01_app_development/step01_moose_app/test/tests/kernels/simple_diffusion/simple_diffusion.i link=False

!col-end!

!col! width=5%
!! intentionally empty column to produce whitespace separation between listing snippet that goes out-of-box and the right-hand column
!col-end!

!col! width=50%

+Hierarchical Input Text (HIT):+

- Block-based structure
- Parameters in `key=value` format
- Strong typing
- Extensive error checking
- Documentation built-in

+Required blocks:+

- Mesh
- Variables
- Kernels
- BCs
- Executioner
- Outputs

!col-end!
!row-end!

!---

# Inline Unit Conversions in Input Files

+Built-in parser enables calculations and unit conversions directly in input files using the MOOSE `fparse` and `units` systems.+

```
${fparse num1 * num2}  # On-the-fly calculations

${units num1 unit1 -> unit2}  # Unit conversions

param = 5.0 * ${top_level_coef1} + ${top_level_coef2}  # Replacements
```

!row!
!col! width=50%

+Available Functions in `fparse`:+

- Basic: `+ - * / ^`
- Trig: `sin cos tan`
- Exp/Log: `exp log log10`
- Other: `sqrt abs min max`
- Constants: `pi` (3.14159...)

!col-end!

!col! width=50%

+Advantages:+

- Self-documenting calculations
- Avoid external calculators
- Useful when performing parametric studies
- Version control friendly

!col-end!
!row-end!

!---

# Fparse / Units Conversion Usage Example

+At the input file top level:+

!listing val-2d.i start=Diffusion parameters end=Traps parameters

+In an object:+

!listing val-2d.i block=Postprocessors/scaled_flux_surface_right

!---

# Solver System: PJFNK Method

+Preconditioned Jacobian-Free Newton-Krylov (PJFNK)+

!row!
!col! width=50%

+Newton's Method:+

- Solves nonlinear system: $R(u) = 0$
- Update: $u^{n+1} = u^n - J^{-1}R$
- Quadratic convergence

+Jacobian-Free:+

- Approximate $J(u) P^{-1} v$ operation via finite differences
- No explicit Jacobian formation
- Reduces memory requirements

!col-end!

!col! width=50%

+Krylov Solvers:+

- GMRES (default)
- Conjugate Gradient (CG), BiCGStab
- Build Krylov subspace

+Preconditioning:+

- Hypre/BoomerAMG
- Block Jacobi
- ILU/LU
- Essential for performance

!col-end!
!row-end!

+Note that a standard Newton solve (using the exact Jacobian) with preconditioning is also available!+

!---

# Automatic Differentiation in MOOSE

!row!
!col! width=45%

+Benefits:+

- No manual Jacobian calculations
- Reduces development time
- Eliminates Jacobian bugs
- Maintains accuracy

```cpp
// Traditional approach
Real computeQpResidual() {...}
Real computeQpJacobian() {...}
Real computeQpOffDiagJacobian() {...}

// AD approach - Jacobian automatic!
ADReal computeQpResidual() {...}
```

!col-end!

!col! width=5%
!! intentionally empty column to produce whitespace separation between listing snippet that goes out-of-box and the right-hand column
!col-end!

!col! width=40%

+How it works:+

- Based on the chain rule of partial derivatives
- Operator overloading (derivatives propagated with `+`,`-`,`*`, etc.)
- "Forward mode" AD
- Uses MetaPhysicL library (from the libMesh team)

+Best practice:+

- Use AD kernels/materials
- Let MOOSE handle derivatives
- +More overhead with this method, but *much* easier to develop!+

!col-end!
!row-end!

!---

# MultiApp and Transfer Systems

!style halign=center
+Solving Multiple Applications Together+

!row!
!col! width=50%

+MultiApp System:+

- Run multiple MOOSE apps / physics
- Different time scales
- Different spatial scales
- Master/sub-app hierarchy

+Use cases:+

- Multiscale modeling
- Multiphysics coupling (when adjustable levels of coupling are desired)
- Reduced-order models

!col-end!

!col! width=50%

+Transfer System:+

- Exchange data between apps
- Spatial interpolation
- Temporal interpolation
- Conservative transfers

+Types:+

- Field transfers
- Postprocessor transfers
- VectorPostprocessor transfers

!col-end!
!row-end!

!---

# Output System

+Flexible and Extensible Output+

!row!
!col! width=50%

+Supported Formats:+

- Exodus (recommended)
- VTK/VTU
- CSV (scalar data)
- Console
- Checkpoint (restart)
- Nemesis (parallel)

!col-end!

!col! width=50%

+Input file control:+

```
[Outputs]
  exodus = true
  csv = true
  [custom_out]
    type = Exodus
    interval = 10
    execute_on = 'timestep_end'
  []
[]
```

!col-end!
!row-end!

!row!
!col! width=50%

+Features:+

- Control output frequency
- Select variables to output
- Multiple outputs simultaneously

!col-end!

!col! width=50%

+Output control:+

- By time
- By timestep
- On events (initial, final, failed)

!col-end!
!row-end!

!---

# MOOSE/TMAP8 Development Process

+Nuclear Quality Assurance Level 1 (NQA-1)+

!row!
!col! width=50%

+Version Control:+

- Git/GitHub workflow
- Pull request reviews
- Continuous integration
- Extensive testing (30M+ tests/week)

!col-end!

!col! width=50%

+Development Tools:+

- [CIVET](https://github.com/idaholab/civet) (testing system)
- [VSCode integration](VSCode.md) with language server support
- Input file syntax highlighting

!col-end!
!row-end!

!row!
!col! width=50%

+Code Standards:+

- [Consistent style](sqa/tmap8_scs.md) (via clang-format)
- Documentation required
- Test coverage required

!col-end!

!col! width=50%

+Community:+

- 250+ contributors to MOOSE
- [MOOSE discussion forum](https://github.com/idaholab/moose/discussions)
- [TMAP8 discussion forum](https://github.com/idaholab/TMAP8/discussions)
- [MOOSE workshops and training](https://mooseframework.inl.gov/getting_started/examples_and_tutorials/index.html)
- Extensive documentation ([MOOSE](https://mooseframework.inl.gov), [TMAP8](https://mooseframework.inl.gov/TMAP8))

!col-end!
!row-end!

!---

# Testing Framework

[TMAP8 Software Quality Assurance Documentation](sqa/index.md exact=True)

!row!
!col! width=45%

+Test Types:+

- `Exodiff`: Compare Exodus files
- `CSVDiff`: Compare CSV output
- `RunException`: Test error conditions
- `PetscJacobianTester`: Verify Jacobians
- `RunApp`: Basic execution test

!col-end!

!col! width=5%
!! intentionally empty column to produce whitespace separation between listing snippet that goes out-of-box and the right-hand column
!col-end!

!col! width=50%

+Benefits:+

- Prevent regressions
- Document expected behavior
- Enable refactoring
- Build confidence

!col-end!
!row-end!

!row!
!col! width=45%

+Test Organization:+

```
test/
  tests/
    kernels/
      my_kernel/
        my_kernel_test.i
        tests
        gold/
          my_kernel_test_out.e
```

!col-end!

!col! width=5%
!! intentionally empty column to produce whitespace separation between listing snippet that goes out-of-box and the right-hand column
!col-end!

!col! width=50%

+Test spec (HIT format):+

```
[Tests]
  [my_kernel_test]
    type = Exodiff
    input = my_kernel_test.i
    cli_args = 'Kernels/my_kernel/active=true'
    exodiff = my_kernel_test_out.e
  []
[]
```

!col-end!
!row-end!

!---

# Getting Help

+Resources Available (all links):+

!row!
!col! width=50%

+Documentation (MOOSE):+

- [https://mooseframework.inl.gov](https://mooseframework.inl.gov)
- [Syntax documentation](https://mooseframework.inl.gov/syntax/index.html)
- [Module documentation](https://mooseframework.inl.gov/modules/index.html)
- [Example problems](https://mooseframework.inl.gov/getting_started/examples_and_tutorials/index.html)
- [Video tutorials](https://mooseframework.inl.gov/getting_started/examples_and_tutorials/index.html)

!col-end!

!col! width=50%

+Documentation (TMAP8):+

- [https://mooseframework.inl.gov/TMAP8](index.md exact=True)
- [Syntax documentation](syntax/index.md exact=True)
- [V&V problems](verification_and_validation/index.md)
- [Example cases](examples/index.md exact=True)

!col-end!
!row-end!

!row!
!col! width=50%

+Community:+

- [MOOSE discussions forum](https://github.com/idaholab/moose/discussions)
- [MOOSE GitHub issues (bugs/feature suggestions)](https://github.com/idaholab/moose/issues)
- [TMAP8 discussion forum](https://github.com/idaholab/TMAP8/discussions)
- [TMAP8 GitHub issues (bugs/feature suggestions)](https://github.com/idaholab/TMAP8/issues)
- [Workshops and in-person Training](https://mooseframework.inl.gov/training/index.html)

!col-end!

!col! width=50%

+Development:+

- [MOOSE Pull requests](https://github.com/idaholab/moose/pulls)
- [TMAP8 Pull requests](https://github.com/idaholab/TMAP8/pulls)
- [Code review process](https://mooseframework.inl.gov/framework/patch_to_code.html)
- [Contributing guidelines](https://mooseframework.inl.gov/framework/contributing.html)

!col-end!
!row-end!

!---

# Summary: Why MOOSE for TMAP8?

- +Proven framework+: Used in 500+ publications, tested extensively, production-ready
- +Parallel scalability+: Handles problems from workstation to supercomputer
- +Multiphysics capable+: Natural coupling of transport phenomena
- +Active development+: Continuous improvements and support
- +Extensible design+: Easy to add new physics for tritium transport
- +Quality assurance+: NQA-1 process ensures reliability
- +Community support+: Large user base and developer team across the world
- +Open source access+: Free and easily available, with contributions from many different fields

!style halign=center
+TMAP8 leverages all these capabilities for tritium transport modeling!+
