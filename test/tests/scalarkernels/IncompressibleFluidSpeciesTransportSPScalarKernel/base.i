# Base input file for the incompressibleFluidSpeciesTransportSPScalarKernel tests.
# Sets up an incompressible single phase pipe model with momentum, energy, and mass transfer.
# These are simple verification tests, should not be taken as accurate example cases.

pipe_length = ${units 1.0 m}
pipe_radius = ${units 0.025 m}
mass_flow_rate = ${units 1.0 kg/s}
reference_pressure = ${ units 101300 Pa}
pressure_drop = ${units -10130 Pa}
temperature_inlet = ${units 293.15 K}
temperature_outlet = ${units 323.15 K}
concentration_inlet = ${units 0.0 mol/m^3}
concentration_outlet = ${units 0.02 mol/m^3}
precursor_concentration_inlet = ${units 0.0 mol/m^3}
density = ${units 998.2 kg/m^3}
viscosity = ${units 0.001002 Pa*s}
pipe_angle = 0.0
pipe_roughness = ${units 0.0001 m}
forms_loss_coefficients = 0.0
pump_pressure_gain = ${units 0.0 Pa}
gravity = ${units 0.0 m/s^2}
pipe_area = '${fparse 3.14159* ${pipe_radius}^2}'
diffusivity = ${units 1.0e-08 m^2/s}
precursor_half_life = ${units 1000000000000000 s}
primary_half_life = ${units 1000000000000000 s}
fluid_solubility = '${units ${fparse 8.0e-04*3.34e+22*100^3/101325/6.022e+23} mol/Pa/m^3}'
wall_sievert_solubility = ${units 2.25e-02 mol/Pa^0.5/m^3} #sieverts
wall_henry_solubility = '${units ${fparse 32.0e-04*3.34e+22*100^3/101325/6.022e+23} mol/Pa/m^3}' #henrys
primary_dissociation_coefficient = ${units 1.0e-11 mol/Pa/m^2/s}
primary_recombination_coefficient = ${units 1.0e-13 m^4/s}

[Mesh]
  type = GeneratedMesh
  dim = 1
  xmin = 0
  xmax = ${pipe_length}
  nx = 1
[]

[Variables]
  [mass_flow_rate_var]
    family = SCALAR
    initial_condition = ${mass_flow_rate}
  []
  [characteristic_pressure_drop_var]
    family = SCALAR
    initial_condition = ${pressure_drop}
  []
  [inlet_temperature_var]
    family = SCALAR
    initial_condition = ${temperature_inlet}
  []
  [temperature_var]
    family = SCALAR
    initial_condition = ${temperature_inlet}
  []
  [wall_temperature_var]
    family = SCALAR
    initial_condition = ${temperature_outlet}
  []
  [outlet_temperature_var]
    family = SCALAR
    initial_condition = ${temperature_outlet}
  []
  [inlet_concentration_var]
    family = SCALAR
    initial_condition = ${concentration_inlet}
  []
  [concentration_var]
    family = SCALAR
    initial_condition = ${concentration_inlet}
  []
  [outlet_concentration_var]
    family = SCALAR
    initial_condition = ${concentration_outlet}
  []
  [precursor_concentration_var]
    family = SCALAR
    initial_condition = ${precursor_concentration_inlet}
  []
[]

[FluidProperties]
  [water]
    type = Water97FluidProperties
  []
[]

[ScalarKernels]
  [momentum_RHS]
    type = IncompressibleMomentumSPScalarKernel
    variable = 'mass_flow_rate_var'
    reference_pressure_drop = 'characteristic_pressure_drop_var'
    temperatures = 'temperature_var'
    reference_pressure = ${reference_pressure}
    fp = 'water'
    areas = '${pipe_area}'
    perimeters = '${fparse 2*3.14159* ${pipe_radius}}'
    lengths = '${pipe_length}'
    alphas = '${pipe_angle}'
    forms_losses = '${forms_loss_coefficients}'
    pump_pressures = '${pump_pressure_gain}'
    roughnesses = '${pipe_roughness}'
    g = ${gravity}
    is_implicit = True
  []
  [momentum_LHS]
    type = ODETimeDerivative
    variable = 'mass_flow_rate_var'
  []
  [inlet_temperature_RHS]
    type = ParsedODEKernel
    expression = 'inlet_temperature_var - ${temperature_inlet}'
    variable = inlet_temperature_var
  []
  [temperature_RHS]
    type = IncompressibleEnergySPScalarKernel
    mass_flow_rate = 'mass_flow_rate_var'
    inlet_temperature = 'inlet_temperature_var'
    outlet_temperature = 'outlet_temperature_var'
    wall_temperature = 'wall_temperature_var'
    area = ${pipe_area}
    fp = water
    length = ${pipe_length}
    perimeter = '${fparse 2*3.14159* ${pipe_radius}}'
    reference_pressure = ${reference_pressure}
    variable = temperature_var
    is_implicit = True
  []
  [temperature_LHS]
    type = ODETimeDerivative
    variable = 'temperature_var'
  []
  [outlet_temperature_RHS]
    type = ParsedODEKernel
    expression = 'outlet_temperature_var - ${temperature_outlet}'
    variable = outlet_temperature_var
  []
  [wall_temperature_RHS]
    type = ParsedODEKernel
    expression = 'wall_temperature_var - ${temperature_outlet}'
    variable = wall_temperature_var
  []
  [inlet_concentration_RHS]
    type = ParsedODEKernel
    expression = 'inlet_concentration_var - ${concentration_inlet}'
    variable = inlet_concentration_var
  []
  [concentration_LHS]
    type = ODETimeDerivative
    variable = 'concentration_var'
  []
  [outlet_concentration_RHS]
    type = ParsedODEKernel
    expression = 'outlet_concentration_var - ${concentration_outlet}'
    variable = outlet_concentration_var
  []
  [precursor_concentration_RHS]
    type = ParsedODEKernel
    expression = 'precursor_concentration_var - ${precursor_concentration_inlet}'
    variable = precursor_concentration_var
  []
  [characteristic_pressure_drop_RHS]
    type = ParsedODEKernel
    expression = 'characteristic_pressure_drop_var - ${pressure_drop}'
    variable = characteristic_pressure_drop_var
  []
[]

[Postprocessors]
  [concentration_PP]
    type = ScalarVariable
    variable = concentration_var
    execute_on = 'TIMESTEP_END'
  []
  [mass_flow_rate_PP]
    type = ScalarVariable
    variable = mass_flow_rate_var
    execute_on = 'TIMESTEP_END'
  []
  [Reynolds_number]
    type = ParsedPostprocessor
    expression = 'abs(mass_flow_rate_PP) / ${pipe_area} * 2 * ${pipe_radius} / ${viscosity}'
    pp_names = 'mass_flow_rate_PP'
    execute_on = 'TIMESTEP_END'
  []
  [Schmidt_number]
    type = ParsedPostprocessor
    expression = '${viscosity} / ${diffusivity} / ${density}'
    execute_on = 'TIMESTEP_END'
  []
  [mass_transfer_coefficient]
    type = ParsedPostprocessor
    expression = '0.023 * Reynolds_number^0.8 * Schmidt_number^0.3333 * ${diffusivity} / ${pipe_radius} / 2'
    pp_names = 'Reynolds_number Schmidt_number'
    execute_on = 'TIMESTEP_END'
  []
  [concentration_inlet_PP]
    type = ParsedPostprocessor
    expression = '1 / 2 * (1 - abs(mass_flow_rate_PP)/mass_flow_rate_PP) * ${concentration_outlet}
                  + 1 / 2 * (1 + abs(mass_flow_rate_PP)/mass_flow_rate_PP) * ${concentration_inlet}'
    pp_names = 'mass_flow_rate_PP'
    execute_on = 'TIMESTEP_END'
  []
[]

[Executioner]
  type = Transient
  start_time = 0
  end_time = 100.0
  [TimeStepper]
    type = IterationAdaptiveDT
    growth_factor = 1.4
    dt = 5
  []
  solve_type = 'PJFNK'
  nl_abs_tol = 1e-08
  l_tol = 1e-07
[]

[Outputs]
  perf_graph = true
  [out]
    type = CSV
    execute_on = 'FINAL'
  []
[]