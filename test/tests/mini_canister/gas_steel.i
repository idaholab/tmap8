### This input file models the transport of H2 through both the gas chamber and
### steel wall of the mini_canister, using InterfaceSorption to model the
### interface between the gas chamber and steel

# Model parameters
!include mini_canister.params
# Volume of gas chamber in canister
gas_volume = '${units ${fparse pi*inner_radius^2*height} mm^3}'
# H2 diffusivity in He backfill
diffusivity_H2_in_He = '${units 2.7 cm^2/s -> mm^2/day}'
# Numerics
num_elements_gas = 250

# Shared objects between two models
!include mini_canister_base.i

[Mesh]
  coord_type = 'RZ' # Axisymmetric coordinates
  rz_coord_axis = Y # Specifies X axis is radial direction and Y axis is axis of symmetry
  [cannister_radius]
    type = CartesianMeshGenerator
    dim = 1
    dx = '${inner_radius} ${steel_thickness}'
    ix = '${num_elements_gas} ${num_elements_steel}'
    subdomain_id = '0 1'
  []
  [interface_left]
    type = SideSetsBetweenSubdomainsGenerator
    input = cannister_radius
    primary_block = '0' # gas chamber
    paired_block = '1' # steel wall
    new_boundary = 'interface_gas_to_steel'
  []
  [interface_right]
    type = SideSetsBetweenSubdomainsGenerator
    input = interface_left
    primary_block = '1' # steel wall
    paired_block = '0' # gas chamber
    new_boundary = 'interface_steel_to_gas'
  []
[]

[Variables]
  [H_mobile_gas] # Mobile H_2 gas inside canister
    block = '0'
  []
[]

[Kernels]
  [gas_mobile_time]
    type = ADTimeDerivative
    variable = H_mobile_gas
    block = 0
  []
  [gas_mobile_diff]
    type = ADMatDiffusion
    variable = H_mobile_gas
    diffusivity = '${diffusivity_H2_in_He}'
    block = 0
  []
  [gas_source]
    type = ADBodyForce
    variable = H_mobile_gas
    block = 0
    function = gas_generation_rhs_function
  []
[]

[InterfaceKernels]
  [Equilibrium_gas_to_steel]
    type = ADInterfaceSorption
    K0 = '${fparse 2 * solubility_preexponential_factor_in_steel}' # Convert solubility to represent H atoms
    boundary = interface_steel_to_gas
    Ea = '${solubility_activation_energy_in_steel}'
    neighbor_var = H_mobile_gas
    variable = H_mobile_steel
    temperature = T
    n_sorption = 0.5 # Sieverts' Law
    diffusivity = '${diffusivity_H_in_steel}'
    unit_scale_neighbor = 1e3 # Unit corrections for C_s = K*\sqrt{unit_scale_neighbor*C_g*R*T}
  []
[]

[Functions]
  [gas_generation_function] # Power model linear least sqaures fit to mumol vs days (assuming 124.7 Gy/min dosage rate from SRNL report)
    type = ParsedFunction
    expression = '69.7055*t^0.6808'
  []

  [gas_generation_rhs_function] # Take time derivative of gas_generation_function and divide by volume to get appropriate units for source term in concentration per unit time (mumol/mm^3/day)
    type = ParsedFunction
    expression = '69.7055*0.6808*t^(0.6808-1)/${gas_volume}'
  []
[]

[Postprocessors]

  # Conservation of mass: Total mass in domain

  [inner_circle_concentration_gas_molecular] # Axisymmetric: 2D Integral of inner circle Cross section
    type = ElementIntegralVariablePostprocessor
    variable = H_mobile_gas
    block = '0'
    outputs = none
  []

  [inner_circle_concentration_gas]
    type = ScalePostprocessor
    value = inner_circle_concentration_gas_molecular
    scaling_factor = 2 # Count H atoms
    outputs = none
  []

  [circle_concentration]
    type = SumPostprocessor
    values = 'inner_circle_concentration_gas annulus_concentration_steel'
    outputs = none
  []

  [inner_cylinder_total_mass_gas]
    type = ScalePostprocessor
    value = inner_circle_concentration_gas
    scaling_factor = '${height}'
    outputs = csv
  []

  [cylinder_total_mass]
    type = SumPostprocessor
    values = 'inner_cylinder_total_mass_gas annular_cylinder_total_mass_steel'
    outputs = csv
  []

  # Conservation of mass: Accumulated flux

  [center_influx] # Influx at the center of canister (Natural BC enforces 0)
    type = ADSideDiffusiveFluxIntegral
    boundary = '0'
    variable = H_mobile_gas
    diffusivity = ${diffusivity_H2_in_He}
    outputs = none
  []

  [circle_flux_difference]
    type = ParsedPostprocessor
    expression = '-2*center_influx-outer_edge_outflux' # Account for sign of outward normal vector
    pp_names = 'center_influx outer_edge_outflux'
    outputs = none
  []

  [circle_time_integrated_flux]
    type = TimeIntegratedPostprocessor
    value = circle_flux_difference
    time_integration_scheme = IMPLICIT-EULER
    outputs = none
  []

  [cylinder_time_integrated_flux]
    type = ScalePostprocessor
    value = circle_time_integrated_flux
    scaling_factor = ${height}
    outputs = csv
  []

  # Conservation of mass: H generation source term

  [cylinder_total_generation]
    type = FunctionValuePostprocessor
    function = gas_generation_function
    scale_factor = 2 # Count H atoms
    outputs = csv
  []

  # Pressure calculation

  [Mobile_gas_interface] # C_g at the gas-steel interface
    type = SideAverageValue
    boundary = 'interface_gas_to_steel'
    variable = H_mobile_gas
    outputs = none
  []

  [H_partial_pressure_interface] # Use ideal gas law to approximate pressure
    type = ScalePostprocessor
    value = Mobile_gas_interface
    scaling_factor = '${fparse ideal_gas_constant * temperature*1e9}' # J/mm^3 = 1e9 J/m^3 = 1e9 Pa
    outputs = csv
  []
[]

[Executioner]
  solve_type = Newton
  line_search = NONE
  nl_rel_tol = 1e-07
[]

[Outputs]
  file_base = 'gas_steel_out'
[]
