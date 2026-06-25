# Verification Problem #1o for Joule heating effect
# Joule heating verification under an applied voltage for proton-conducting ceramics
#
# This case isolates Joule heating in the half-slab symmetry reduction of a
# 10 mm PCC membrane under a 20 V applied potential.

# Geometry and electrical loading
full_length = '${units 10 mm -> mum}'
length = '${fparse full_length / 2}'
num_nodes = 100
V_full = '${units 20 V}'
left_voltage = '${units 20 V}'

# Initial and boundary temperature
temperature_surface = '${units 773 K}'

# Important times
end_time = '${units 200000 s}'
dt_max = '${units 5000 s}'
dt_start = '${units 1 s}'

# Thermal properties
# kappa chosen for verification (Delta_T_max ~ 20 K)
thermal_conductivity_SI = '${units 0.014 W/m/K}'
thermal_conductivity = '${fparse thermal_conductivity_SI * 1e-6}' # W/(mum*K)

# Ref: Yamanaka et al. 2003, J. Alloys and Compounds, Vol. 359, 109-113
molar_mass_BCY20 = '${units 283.42 g/mol}'
specific_heat_molar = '${units 120 J/mol/K}'
specific_heat = '${fparse specific_heat_molar / molar_mass_BCY20}' # J/(g*K)
density_BCY20 = '${units ${fparse 6.154} g/cm^3 -> g/m^3}'
density_thermal = '${fparse density_BCY20 * 1e-18}' # g/mum^3

# Electrical conductivity
# This verification parameter matches the previous coupled case's reference
# conductivity, converted from A/V/m to A/V/mum.
sigma_ref = '${units 1e-03 A/V/m -> A/V/mum}'

[Mesh]
  [cmg]
    type = CartesianMeshGenerator
    dim = 1
    dx = '${fparse length}'
    ix = '${fparse num_nodes}'
  []
[]

[Variables]
  [temperature]
    initial_condition = ${temperature_surface}
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
    function = '${left_voltage} - (${V_full} / ${full_length}) * x'
    execute_on = 'INITIAL TIMESTEP_END'
  []
[]

[Kernels]
  [heat_time]
    type = ADHeatConductionTimeDerivative
    variable = temperature
    specific_heat = specific_heat_BCY20
    density_name = density_BCY20_thermal
  []
  [heat_conduction]
    type = ADHeatConduction
    variable = temperature
    thermal_conductivity = thermal_conductivity_BCY20
  []
  [joule_heating_source]
    type = ADJouleHeatingSource
    variable = temperature
    heating_term = joule_heating_Q
  []
[]

[BCs]
  [left_temperature]
    type = ADDirichletBC
    variable = temperature
    boundary = left
    value = ${temperature_surface}
  []
  [right_insulated]
    type = ADNeumannBC
    variable = temperature
    boundary = right
    value = 0
  []
[]

[Materials]
  [thermal_conductivity_mat]
    type = ADGenericConstantMaterial
    prop_names = 'thermal_conductivity_BCY20'
    prop_values = '${thermal_conductivity}'
  []
  [specific_heat_mat]
    type = ADGenericConstantMaterial
    prop_names = 'specific_heat_BCY20'
    prop_values = '${specific_heat}'
  []
  [density_thermal_mat]
    type = ADGenericConstantMaterial
    prop_names = 'density_BCY20_thermal'
    prop_values = '${density_thermal}'
  []

  [electrical_conductivity_mat]
    type = ADGenericConstantMaterial
    prop_names = 'electrical_conductivity'
    prop_values = '${sigma_ref}'
  []
  [electromagnetic_heating]
    type = ADParsedMaterial
    property_name = 'joule_heating_Q'
    material_property_names = 'electrical_conductivity'
    expression = 'electrical_conductivity * (${V_full} / ${full_length})^2'
  []
[]

[Postprocessors]
  [temperature_max]
    type = ElementExtremeValue
    variable = temperature
    value_type = max
    execute_on = 'INITIAL TIMESTEP_END'
    outputs = 'csv'
  []
  [temperature_min]
    type = ElementExtremeValue
    variable = temperature
    value_type = min
    execute_on = 'INITIAL TIMESTEP_END'
    outputs = 'csv'
  []
  [delta_T]
    type = ParsedPostprocessor
    pp_names = 'temperature_max temperature_min'
    expression = 'temperature_max - temperature_min'
    execute_on = 'TIMESTEP_END'
    outputs = 'csv'
  []
[]

[VectorPostprocessors]
  [line]
    type = LineValueSampler
    start_point = '0 0 0'
    end_point = '${fparse length} 0 0'
    num_points = 101
    sort_by = 'x'
    variable = 'temperature'
    outputs = 'vector_postproc_1000s vector_postproc_20000s'
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
  compute_scaling_once = false
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

[Outputs]
  csv = true
  [exodus]
    type = Exodus
  []
  [vector_postproc_1000s]
    type = CSV
    sync_times = '1000'
    sync_only = true
  []
  [vector_postproc_20000s]
    type = CSV
    sync_times = '20000'
    sync_only = true
  []
[]
