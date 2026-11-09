# Light Case of Validation Problem #2g for TMAP8
# Deuterium Transport in Proton-Conducting Ceramics
# Diffusion, Surface Reaction under Wet Considered, No Trapping, Soret effects

# Physical constants
R = '${units 8.31446261815324 J/mol/K}' # ideal gas constant based on number used in TMAP8PhysicalConstants.h

# thermal parameters
temperature_low = '${units 1000 K}'
temperature_initial = '${units 873 K}'
temperature_high = '${units 1400 K}'
temperature_rate = '${units 10 K/s}'

# Geometry and mesh
length = '${units 0.5 mm -> mum}'
num_nodes = 30

# Initial concentrations
N = '${units 1.3043954487e28 at/m^3 -> at/mum^3}'
oxygen_vacancy_concentration_initial = '${units ${fparse 0.05 * N} at/mum^3}'
oxygen_concentration_initial = '${units ${fparse 2.95 * N} at/mum^3}'
electron_concentration_initial = '${units ${fparse 1e-5 * N} at/mum^3}'

# Wet Pressure conditions
pressure_T2O_high = '${units 2.8e3 Pa}'

# chemical_reaction
delta_H_T2O = '${units -79.5e3 J/mol}'
delta_S_T2O = '${units -88.9 J/mol/K}'
delta_H_T2 = '${units -79.5e3 J/mol}'
delta_S_T2 = '${units -124.53 J/mol/K}'
T2O_reaction_forward_value = '${units 2e-33 m^4/at/s -> mum^4/at/s}'
T2_reaction_forward_value = '${units 2e-41 m^4/at/s -> mum^4/at/s}'

# Materials diffusivities
diffusivity_OT_prefactor = '${units 2e-9 m^2/s -> mum^2/s}'
diffusivity_OT_energy = '${units 22191 J/mol}'
diffusivity_V_O_prefactor = '${units 1.021e-7 m^2/s -> mum^2/s}'
diffusivity_V_O_energy = '${units 89216.77 J/mol}'
diffusivity_e_prefactor = '${units 2.05e-2 m^2/s -> mum^2/s}'
diffusivity_e_energy = '${units 103818.22 J/mol}'

[Mesh]
  [cmg]
    type = CartesianMeshGenerator
    dim = 1
    dx = '${fparse length}'
    ix = '${fparse num_nodes}'
  []
[]

[Variables]
  #### Wet variable
  [OT_concentration_wet] # (atoms/microns^3)
    initial_condition = 0
  []
  [Oxygen_vacancy_concentration_wet]
    initial_condition = ${oxygen_vacancy_concentration_initial}
  []
  [electron_concentration_wet]
    initial_condition = ${electron_concentration_initial}
  []
[]

[AuxVariables]
  [temperature]
    initial_condition = ${temperature_initial}
  []
  #### Wet auxvariable
  [pressure_T2O_wet]
    initial_condition = ${pressure_T2O_high}
  []
  [Oxygen_concentration_wet]
    initial_condition = ${oxygen_concentration_initial}
  []
[]

[AuxKernels]
  [temperature_Aux]
    type = FunctionAux
    variable = temperature
    function = Temperature_function
  []
  #### Wet auxkernels
  [pressure_T2O_wet_Aux]
    type = FunctionAux
    variable = pressure_T2O_wet
    function = Pressure_T2O_wet_function
  []
  [Oxygen_concentration_wet_Aux] # at/mum^3
    type = ParsedAux
    variable = Oxygen_concentration_wet
    coupled_variables = 'Oxygen_vacancy_concentration_wet OT_concentration_wet'
    expression = '3  * ${N} - Oxygen_vacancy_concentration_wet - OT_concentration_wet'
  []
[]

[Problem]
  type = ReferenceResidualProblem
  extra_tag_vectors = 'ref'
  reference_vector = 'ref'
[]

[Kernels]
  #### Wet kernels
  [time_OT_wet]
    type = TimeDerivative
    variable = OT_concentration_wet
    extra_vector_tags = ref
  []
  [diffusion_OT_wet]
    type = MatDiffusion
    variable = OT_concentration_wet
    diffusivity = diffusivity_OT
    extra_vector_tags = ref
  []
  [time_V_O_wet]
    type = TimeDerivative
    variable = Oxygen_vacancy_concentration_wet
    extra_vector_tags = ref
  []
  [diffusion_V_O_wet]
    type = MatDiffusion
    variable = Oxygen_vacancy_concentration_wet
    diffusivity = diffusivity_V_O
    extra_vector_tags = ref
  []
  [time_e_wet]
    type = TimeDerivative
    variable = electron_concentration_wet
    extra_vector_tags = ref
  []
  [diffusion_e_wet]
    type = MatDiffusion
    variable = electron_concentration_wet
    diffusivity = diffusivity_e
    extra_vector_tags = ref
  []
[]

[BCs]
  #### Wet BCs
  [left_OT_wet]
    type = MatNeumannBC
    variable = OT_concentration_wet
    boundary = left
    value = 1
    boundary_material = flux_on_OT_wet
  []
  [right_OT_wet]
    type = MatNeumannBC
    variable = OT_concentration_wet
    boundary = right
    value = 1
    boundary_material = flux_on_OT_wet
  []
  [left_V_O_wet]
    type = MatNeumannBC
    variable = Oxygen_vacancy_concentration_wet
    boundary = left
    value = 1
    boundary_material = flux_on_V_O_wet
  []
  [right_V_O_wet]
    type = MatNeumannBC
    variable = Oxygen_vacancy_concentration_wet
    boundary = right
    value = 1
    boundary_material = flux_on_V_O_wet
  []
  [left_e_wet]
    type = MatNeumannBC
    variable = electron_concentration_wet
    boundary = left
    value = 1
    boundary_material = flux_on_e_wet
  []
  [right_e_wet]
    type = MatNeumannBC
    variable = electron_concentration_wet
    boundary = right
    value = 1
    boundary_material = flux_on_e_wet
  []
[]

[Functions]
  [Temperature_function]
    type = ParsedFunction
    expression = 'if(t<2, ${temperature_initial},
                  if(t<3, ${temperature_low} + ${temperature_rate} * (t - 2),
                          ${temperature_high}))'
  []
  [Pressure_T2O_wet_function]
    type = ParsedFunction
    expression = 'if(t<1, ${pressure_T2O_high},
                  if(t<2, 1e-5, 1e-5))'
  []
[]

[Materials]
  [diffusivity_OT]
    type = ParsedMaterial
    property_name = 'diffusivity_OT'
    coupled_variables = 'temperature'
    expression = '${diffusivity_OT_prefactor} * exp(-${diffusivity_OT_energy} / ${R} / temperature)'
    enable_jit = false
  []
  [diffusivity_V_O]
    type = ParsedMaterial
    property_name = 'diffusivity_V_O'
    coupled_variables = 'temperature'
    expression = '${diffusivity_V_O_prefactor} * exp(-${diffusivity_V_O_energy} / ${R} / temperature)'
    enable_jit = false
  []
  [diffusivity_e]
    type = ParsedMaterial
    property_name = 'diffusivity_e'
    coupled_variables = 'temperature'
    expression = '${diffusivity_e_prefactor} * exp(-${diffusivity_e_energy} / ${R} / temperature)'
    enable_jit = false
  []
  [reaction_equilibrium_constant_T2O]
    type = ParsedMaterial
    property_name = 'T2O_K_eq'
    coupled_variables = 'temperature'
    expression = 'exp( (temperature * ${delta_S_T2O} - ${delta_H_T2O}) / ${R} / temperature )'
    enable_jit = false
  []
  [reaction_forward_T2O]
    type = ParsedMaterial
    property_name = 'T2O_K_forward'
    expression = '${T2O_reaction_forward_value}'
    enable_jit = false
  []
  [reaction_reverse_T2O]
    type = ParsedMaterial
    property_name = 'T2O_K_reverse'
    material_property_names = 'T2O_K_forward T2O_K_eq'
    expression = 'T2O_K_forward / T2O_K_eq'
    enable_jit = false
  []
  [reaction_equilibrium_constant_T2]
    type = ParsedMaterial
    property_name = 'T2_K_eq'
    coupled_variables = 'temperature'
    expression = 'exp( (temperature * ${delta_S_T2} - ${delta_H_T2}) / ${R} / temperature )'
    enable_jit = false
  []
  [reaction_forward_T2]
    type = ParsedMaterial
    property_name = 'T2_K_forward'
    expression = '${T2_reaction_forward_value}'
    enable_jit = false
  []
  [reaction_reverse_T2]
    type = ParsedMaterial
    property_name = 'T2_K_reverse'
    material_property_names = 'T2_K_forward T2_K_eq'
    expression = 'T2_K_forward / T2_K_eq'
    enable_jit = false
  []
  #### Reaction for wet
  [flux_base_on_T2O_wet] # T2O + V_O + O -> 2 OT
    type = DerivativeParsedMaterial
    coupled_variables = 'OT_concentration_wet pressure_T2O_wet Oxygen_concentration_wet Oxygen_vacancy_concentration_wet'
    property_name = 'flux_base_on_T2O_wet'
    material_property_names = 'T2O_K_forward T2O_K_reverse'
    expression = '(T2O_K_forward * pressure_T2O_wet * Oxygen_concentration_wet * Oxygen_vacancy_concentration_wet - T2O_K_reverse * OT_concentration_wet^2)'
    enable_jit = false
  []
  [flux_base_on_T2_wet] # T2 + 2 O -> 2 OT + 2 e
    type = DerivativeParsedMaterial
    coupled_variables = 'OT_concentration_wet Oxygen_concentration_wet electron_concentration_wet'
    property_name = 'flux_base_on_T2_wet'
    material_property_names = 'T2_K_forward T2_K_reverse'
    expression = '(- T2_K_reverse * OT_concentration_wet^2 * electron_concentration_wet^2)'
    enable_jit = false
  []
  #### Flux for wet
  [flux_on_e_wet] # electron
    type = DerivativeParsedMaterial
    property_name = 'flux_on_e_wet'
    material_property_names = 'flux_base_on_T2_wet'
    expression = '2 * flux_base_on_T2_wet'
    enable_jit = false
  []
  [flux_on_OT_wet] # OT
    type = DerivativeParsedMaterial
    property_name = 'flux_on_OT_wet'
    material_property_names = 'flux_base_on_T2O_wet'
    expression = '2 * flux_base_on_T2O_wet'
    enable_jit = false
  []
  [flux_on_T2_wet] # T2
    type = DerivativeParsedMaterial
    property_name = 'flux_on_T2_wet'
    material_property_names = 'flux_base_on_T2_wet'
    expression = '-1 * flux_base_on_T2_wet'
    enable_jit = false
  []
  [flux_on_V_O_wet] # V_O
    type = DerivativeParsedMaterial
    property_name = 'flux_on_V_O_wet'
    material_property_names = 'flux_base_on_T2O_wet'
    expression = '-1 * flux_base_on_T2O_wet'
    enable_jit = false
  []
  [flux_on_T2O_wet] # T2O
    type = DerivativeParsedMaterial
    property_name = 'flux_on_T2O_wet'
    material_property_names = 'flux_base_on_T2O_wet'
    expression = '-1 * flux_base_on_T2O_wet'
    enable_jit = false
  []
[]

[Postprocessors]
  #### Postprocessors for flux under wet
  [recombination_flux_T2O_wet_left]
    type = SideAverageMaterialProperty
    boundary = left
    property = flux_on_T2O_wet
  []
  [recombination_flux_T2_wet_left]
    type = SideAverageMaterialProperty
    boundary = left
    property = flux_on_T2_wet
  []
[]

[Executioner]
  type = Transient
  scheme = bdf2
  solve_type = NEWTON
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'
  nl_rel_tol = 1e-7
  nl_abs_tol = 1e-8
  automatic_scaling = true
  compute_scaling_once = true
  line_search = none
  num_steps = 3
  nl_max_its = 10
  dt = 0.1
[]

[Outputs]
  csv = true
  exodus = true
[]
