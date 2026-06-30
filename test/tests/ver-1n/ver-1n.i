# Verification Problem #1n for voltage-assisted transport
# Diffusion verification under an applied voltage with constant source boundary condition

# Physical constants
R = '${units 8.31446261815324 J/mol/K}' # ideal gas constant based on number used in include/utils/PhysicalConstants.h
eV_to_J = '${units 1.602176634e-19 eV/J}'
N_a = '${units 6.02214076e23 at/mol}'
q = '${units 1.602176634e-19 C}'
F = '${fparse N_a * q}'

# Pressure conditions
pressure_high = '${units 100 Pa}'
pressure_low = '${units 1e-6 Pa}'

# Temperature conditions
temperature = '${units 773 K}' # 500 C

# PCC Materials properties
diffusion_pre_PCC = '${units ${fparse sqrt(3) * 1.41e-6} m^2/s -> mum^2/s}' # Deuterium
diffusion_energy_PCC = '${units ${fparse 0.74 * eV_to_J * N_a} J/mol}'
solubility_pre_PCC = '${units ${fparse 1.06 * N_a / 1e18} at/mum^3/Pa^0.5}' # at/m^3/Pa^0.5 -> at/mum^3/Pa^0.5
solubility_energy_PCC = '${units 7726.21 J/mol}'
solubility_order = .5 # Here, we use Sievert's law
charge_number = 1
V_current = '${units 20 V}'

# Important times
end_time = '${units 500 s}'
dt_max = '${units 10 s}'
dt_start = '${units 1 s}'

# Geometry and mesh
length = '${units 10 mm -> mum}'
num_nodes = 1000

[Mesh]
  [cmg]
    type = CartesianMeshGenerator
    dim = 1
    dx = '${fparse length}'
    ix = '${fparse num_nodes}'
  []
[]

[Variables]
  [deuterium_concentration_PCC] # (atoms/microns^3)
  []
[]

[AuxVariables]
  [voltage_phi]
  []
[]

[AuxKernels]
  [phi_auxkernel]
    type = FunctionAux
    variable = voltage_phi
    function = '${V_current} * (${length} - x) / ${length}'
    execute_on = 'INITIAL TIMESTEP_END'
  []
[]

[Problem]
  type = ReferenceResidualProblem
  extra_tag_vectors = 'ref'
  reference_vector = 'ref'
[]

[Kernels]
  [time_PCC]
    type = TimeDerivative
    variable = deuterium_concentration_PCC
    extra_vector_tags = ref
  []
  [diffusion_PCC]
    type = ADMatDiffusion
    variable = deuterium_concentration_PCC
    diffusivity = diffusivity_PCC
    extra_vector_tags = ref
  []
  [diffusion_phi_PCC]
    type = ADMatDiffusion
    variable = deuterium_concentration_PCC
    v = voltage_phi
    diffusivity = conductivity
    extra_vector_tags = ref
  []
[]

[BCs]
  [left_flux]
    type = EquilibriumBC
    Ko = '${solubility_pre_PCC}'
    activation_energy = '${solubility_energy_PCC}'
    boundary = left
    enclosure_var = '${pressure_high}'
    temperature = '${temperature}'
    variable = deuterium_concentration_PCC
    p = ${solubility_order}
  []
  [right_flux]
    type = EquilibriumBC
    Ko = '${solubility_pre_PCC}'
    activation_energy = '${solubility_energy_PCC}'
    boundary = right
    enclosure_var = '${pressure_low}'
    temperature = '${temperature}'
    variable = deuterium_concentration_PCC
    p = ${solubility_order}
  []
[]

[Functions]
  [diffusivity_PCC_func]
    type = ParsedFunction
    expression = '${diffusion_pre_PCC} * exp(-${diffusion_energy_PCC} / ${R} / ${temperature})'
  []
  [solubility_PCC_func]
    type = ParsedFunction
    expression = '${solubility_pre_PCC} * exp(-${solubility_energy_PCC} / ${R} / ${temperature})'
  []
[]

[Materials]
  [diffusion_solubility]
    type = ADGenericFunctionMaterial
    prop_names = 'diffusivity_PCC solubility_PCC'
    prop_values = 'diffusivity_PCC_func solubility_PCC_func'
    outputs = all
  []
  [conductivity]
    type = ADParsedMaterial
    property_name = 'conductivity'
    coupled_variables = 'deuterium_concentration_PCC'
    functor_names = 'diffusivity_PCC_func'
    functor_symbols = 'diffusivity'
    expression = 'diffusivity * ${charge_number} * ${F} * deuterium_concentration_PCC / ${R} / ${temperature}'
    outputs = all
  []
[]

[Postprocessors]
  [concentration_point1]
    type = PointValue
    variable = deuterium_concentration_PCC
    point = '100 0 0'
    outputs = 'csv'
  []
  [concentration_point2]
    type = PointValue
    variable = deuterium_concentration_PCC
    point = '500 0 0'
    outputs = 'csv'
  []
[]

[VectorPostprocessors]
  [line]
    type = LineValueSampler
    start_point = '0 0 0'
    end_point = '1000 0 0'
    num_points = 1001
    sort_by = 'x'
    variable = deuterium_concentration_PCC
    outputs = 'vector_postproc_30s vector_postproc_500s'
  []
[]

[Preconditioning]
  [SMP]
    type = SMP
    full = true
  []
[]

[Executioner]
  type = Transient
  scheme = bdf2
  solve_type = NEWTON
  petsc_options_iname = '-pc_type'
  petsc_options_value = 'lu'
  nl_rel_tol = 1e-8
  nl_abs_tol = 1e-8
  end_time = ${end_time}
  automatic_scaling = true
  compute_scaling_once = true
  # nl_max_its = 7
  dtmax = ${dt_max}
  [TimeStepper]
    type = IterationAdaptiveDT
    dt = ${dt_start}
    optimal_iterations = 5
    growth_factor = 1.1
    cutback_factor = 0.9
    cutback_factor_at_failure = 0.9
  []
[]

[Debug]
  show_var_residual_norms = true
[]

[Outputs]
  csv = true
  [exodus]
    type = Exodus
    output_material_properties = true
    time_step_interval = 5
  []
  [vector_postproc_30s]
    type = CSV
    sync_times = '30'
    sync_only = true
  []
  [vector_postproc_500s]
    type = CSV
    sync_times = '500'
    sync_only = true
  []
[]
