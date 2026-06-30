# This input file re-creates the hydrogen redistribution model
# described by Huang et al (2000).
# "Estimation of Hydrogen Redistribution in Zirconium Hydride under Temperature
#   Gradient." J Huang, B Tsuchiya, K Konashi & M Yamawaki J. Nucl. Sci.
#   Technol. 37 (2000) 887–892 https://doi.org/10.1080/18811248.2000.9714969

# Physical constants
boltzmann_constant = '${units 1.380649e-23 J/K -> eV/K}' # Boltzmann constant from PhysicalConstants.h

# Geometry
pin_radius = '${units 0.005 m}'
gap_thickness = '${units 0.0001 m}'
cladding_thickness = '${units 0.001 m}'

# Simulation conditions and material properties
linear_heating_rate = '${units ${LHR} W/cm -> W/m}'
volumetric_heating_rate = '${units ${fparse linear_heating_rate/(pi*pin_radius^2)} W/m^3}'
heat_of_transport = '${units 5.3 kJ/mol -> J/mol}'
fuel_thermal_conductivity = '${units 17.6 W/m/K}'
cladding_thermal_conductivity = '${units 16.5 W/m/K}'
fuel_density = '${units  8.26e3 kg/m^3}'
cladding_density = '${units 8.0 g/cm^3 -> kg/m^3}'
initial_atomic_fraction = 1.6 # ratio H/Zr
coolant_water_temperature = '${units 563.15 K}'
water_convective_htc = '${units 18000 W/m^2/K}'
gap_conductance = '${units 7.381e3 W/m^2/K}'
gap_thermal_conductivity = '${units ${fparse gap_conductance*gap_thickness} W/m^2/K}'

# limiting diffusivity from  G Majer et al 1994 J. Phys.: Condens. Matter 6 2935
diffusivity_D0 = '${units 1.53e-7 m^2/s}'
diffusivity_Ea = '${units 0 eV}' # this value does not impact the steady state solution, so the limiting diffusivity is assumed in all cases.

reference_temperature = '${units ${fparse coolant_water_temperature  + (linear_heating_rate/(2*pi*fuel_thermal_conductivity))} K}'

# time
end_time = '${fparse ${hours}*3600}'
dt_max = ${units 10000 s}
dt_init = ${units 0.01 s}

# file base
output_file_base = 'ver-1m_out_${LHR}'

[Mesh]
  [fuel_pin]
    type = ConcentricCircleMeshGenerator
    num_sectors = 16
    has_outer_square = 'on'
    pitch = 2.0
    radii = '${pin_radius} ${fparse pin_radius+gap_thickness} ${fparse pin_radius+gap_thickness+cladding_thickness}'
    rings = '10 1 1 1'
    preserve_volumes = 'on'
  []
  [add_sideset_fuel_outer]
    type = SideSetsBetweenSubdomainsGenerator
    input = 'fuel_pin'
    primary_block = '1'
    paired_block = '2'
    new_boundary = 'fuel_outer'
  []
  [add_sideset_gap_outer]
    type = SideSetsBetweenSubdomainsGenerator
    input = 'add_sideset_fuel_outer'
    primary_block = '3'
    paired_block = '2'
    new_boundary = 'gap_outer'
  []
  [add_sideset_clad_outer]
    type = SideSetsBetweenSubdomainsGenerator
    input = 'add_sideset_gap_outer'
    primary_block = '3'
    paired_block = '4'
    new_boundary = 'clad_outer'
  []
  [remove_blocks] # remove gap and outer square
    type = BlockDeletionGenerator
    input = 'add_sideset_clad_outer'
    block = '4'
  []
[]

[Variables]
  [temperature]
    initial_condition = '${reference_temperature}'
  []
  [hydrogen_concentration]
    initial_condition = '${initial_atomic_fraction}'
    block = '1'
  []
[]

[Kernels]
  # Heat conduction
  [heat_time_derivative_fuel]
    type = HeatConductionTimeDerivative
    variable = temperature
  []
  [heat_conduction_fuel]
    type = HeatConduction
    variable = temperature
  []
  [heat_source_fuel]
    type = HeatSource
    variable = temperature
    block = '1'
    value = '${volumetric_heating_rate}'
  []
  #  Hydrogen redistribution
  [hydrogen_concentration_time_derivative]
    type = TimeDerivative
    variable = hydrogen_concentration
    block = '1'
  []
  [hydrogen_concentration_dxdx]
    type = MatDiffusion
    variable = 'hydrogen_concentration'
    diffusivity = 'D'
    block = '1'
  []
  [soretDiff]
    type = ThermoDiffusion
    variable = 'hydrogen_concentration'
    temp = 'temperature '
    heat_of_transport = 'Q'
    mass_diffusivity = 'D'
    block = '1'
  []
[]

[BCs]
  [t_out]
    type = ConvectiveHeatFluxBC
    variable = temperature
    boundary = 'clad_outer'
    heat_transfer_coefficient = '${water_convective_htc}' # Convective heat transfer coefficient in W/m^2/K (adjust as needed)
    T_infinity = '${coolant_water_temperature}' # Temperature of the bulk fluid in K
  []
[]

[Materials]
  #### CLADDING #####
  [cladding_density]
    type = GenericConstantMaterial
    block = '3'
    prop_names = 'density'
    prop_values = '${cladding_density}'
  []
  [cladding_kappa]
    type = HeatConductionMaterial
    block = '3'
    thermal_conductivity = '${cladding_thermal_conductivity}'
  []
  [gap_density]
    type = GenericConstantMaterial
    block = '2'
    prop_names = 'density'
    prop_values = '0.1785'
  []
  [gap_kappa]
    type = HeatConductionMaterial
    block = '2'
    thermal_conductivity = '${gap_thermal_conductivity}'
  []
  #### FUEL ####
  [fuel_kappa]
    type = HeatConductionMaterial
    block = '1'
    thermal_conductivity = '${fuel_thermal_conductivity}'
  []
  [fuel_density]
    type = GenericConstantMaterial
    block = '1'
    prop_names = 'density'
    prop_values = '${fuel_density}'
  []
  # Material properties for migration
  [h_diffusivity]
    type = ParsedMaterial
    block = '1'
    coupled_variables = 'temperature'
    property_name = 'D'
    expression = 'D0*exp(-Ea/(k*temperature))'
    constant_names = 'D0 Ea k'
    constant_expressions = '${diffusivity_D0} ${diffusivity_Ea} ${boltzmann_constant}'
  []
  [h_heat_of_transport]
    type = GenericConstantMaterial
    block = '1'
    prop_names = 'Q'
    prop_values = '${heat_of_transport}'
  []
[]

[Executioner]
  type = Transient
  petsc_options_iname = '-pc_type -pc_hypre_type -ksp_gmres_restart'
  petsc_options_value = 'hypre boomeramg 300'
  line_search = 'none'
  automatic_scaling = true
  compute_scaling_once = 'false'

  l_tol = 1e-02
  nl_abs_tol = 1e-7
  nl_rel_tol = 1e-8

  l_max_its = 50
  nl_max_its = 25

  start_time = 0
  steady_state_detection = 'true'
  steady_state_start_time = '${end_time}'

  [TimeStepper]
    type = IterationAdaptiveDT
    growth_factor = 1.5
    dt = '${dt_init}'
  []
  dtmax = '${dt_max}'
  dtmin = 1e-3
[]

[Postprocessors]
  [surface_hydrogen_concentration]
    type = SideAverageValue
    variable = hydrogen_concentration
    boundary = 'fuel_outer'
    execute_on = 'INITIAL TIMESTEP_END'
  []
[]

[VectorPostprocessors]
  [hydrogen_profile]
    type = LineValueSampler
    start_point = '0 0 0'
    end_point = '${pin_radius} 0 0'
    num_points = 101
    sort_by = 'x'
    variable = 'hydrogen_concentration'
    execute_on = 'FINAL'
    contains_complete_history = true
  []
  [temperature_profile]
    type = LineValueSampler
    start_point = '0 0 0'
    end_point = '${pin_radius} 0 0'
    num_points = 101
    sort_by = 'x'
    variable = 'temperature'
    execute_on = 'FINAL'
    contains_complete_history = true
  []
[]

[Outputs]
  file_base = '${output_file_base}'

  [postprocessors]
    type = CSV
    execute_vector_postprocessors_on = 'NONE'
    execute_postprocessors_on = 'INITIAL TIMESTEP_END'
    file_base = '${output_file_base}'
  []

  [hydrogen_profile]
    type = CSV
    execute_vector_postprocessors_on = 'FINAL'
    execute_postprocessors_on = 'NONE'
    file_base = '${output_file_base}_end'
  []
[]
