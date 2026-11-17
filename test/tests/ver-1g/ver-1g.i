# Verification Problem #1g from TMAP4/TMAP7 V&V document
# A Simple Forward Chemical Reaction

## Run this file with one of three input files to simulate various verification cases
## a. equal_conc.i        -> TMAP4 and TMAP7 equal concentration case
## b. diff_conc_TMAP4.i  -> TMAP4 different concentration case
## c. diff_conc_TMAP7.i  -> TMAP7 different concentration case
## Example: ~/projects/TMAP8/tmap8-opt -i ver-1g.i equal_conc.i

# Physical Constants
R = 8.31446261815324 # Gas constant (from TMAP8PhysicalConstants.h)
T = '${units 25 degC -> K}' # Temperature
Na = 6.02214076E23 # Avogadro's constant (from TMAP8PhysicalConstants.h)

[Mesh]
  type = GeneratedMesh
  dim = 2
[]

[Variables]
  [c_a]
  []
  [c_b]
  []
  [c_ab]
    initial_condition = 0
  []
[]

[Kernels]
  [timeDerivative_c_a]
    type = ADTimeDerivative
    variable = c_a
  []
  [timeDerivative_c_b]
    type = TimeDerivative
    variable = c_b
  []
  [timeDerivative_c_ab]
    type = TimeDerivative
    variable = c_ab
  []
  [MatReaction_b]
    type = ADMatReactionFlexible
    variable = c_b
    vs = 'c_a c_b'
    coeff = -1
    reaction_rate_name = K
  []
  [MatReaction_a]
    type = ADMatReactionFlexible
    variable = c_a
    vs = 'c_b c_a'
    coeff = -1
    reaction_rate_name = K
  []
  [MatReaction_ab]
    type = ADMatReactionFlexible
    variable = c_ab
    vs = 'c_b c_a'
    coeff = 1
    reaction_rate_name = K
  []
[]

[Materials]
  [K]
    type = ADParsedMaterial
    property_name = 'K'
    expression = '4.14e3' # units: molecule.micrometer^3/atom/second
  []
[]

[BCs]
  [c_a_neumann] # No flux on the sides
    type = NeumannBC
    variable = c_a
    boundary = 'left right bottom top'
    value = 0
  []
  [c_b_neumann] # No flux on the sides
    type = NeumannBC
    variable = c_b
    boundary = 'left right bottom top'
    value = 0
  []
  [c_ab_neumann] # No flux on the sides
    type = NeumannBC
    variable = c_ab
    boundary = 'left right bottom top'
    value = 0
  []
[]

[Postprocessors]
  [conc_a]
    type = ElementAverageValue
    variable = c_a
  []
  [conc_b]
    type = ElementAverageValue
    variable = c_b
  []
  [conc_ab]
    type = ElementAverageValue
    variable = c_ab
  []
[]

[Executioner]
  type = Transient
  scheme = bdf2
  nl_rel_tol = 1e-10
  nl_abs_tol = 1e-15

  solve_type = 'NEWTON'

  petsc_options = '-snes_ksp_ew'
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'

  start_time = 0.0
  end_time = 40
  num_steps = 60000
  dt = .2
  n_startup_steps = 0
[]

[Outputs]
  exodus = true
  csv = true
[]
