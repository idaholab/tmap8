# Test gas type fluid (air, etc.), with precursor species radioactive decay

!include base.i

fluid_type = "gas"

[Variables]
  [wall_concentration]
    family = SCALAR
    initial_condition = '${fparse ${concentration_outlet}*2}'
  []
[]

[ScalarKernels]
  [concentration_RHS]
    type = IncompressibleFluidSpeciesTransportSPScalarKernel
    mass_flow_rate = 'mass_flow_rate_var'
    inlet_temperature = 'inlet_temperature_var'
    outlet_temperature = 'outlet_temperature_var'
    wall_temperature = 'wall_temperature_var'
    area = ${pipe_area}
    fp = water
    length = ${pipe_length}
    perimeter = '${fparse 2*3.14159* ${pipe_radius}}'
    reference_pressure = ${reference_pressure}
    variable = concentration_var
    is_implicit = True
    temperature = 'temperature_var'
    upstream_concentration = 'inlet_concentration_var'
    downstream_concentration = 'outlet_concentration_var'
    precursors = 'precursor_concentration_var'
    precursor_half_lives = '${precursor_half_life}'
    wall_dissociated_atoms = 'wall_concentration'
    half_life = '${primary_half_life}'
    fluid_type = ${fluid_type}
    species_diffusivity = ${diffusivity}
    fluid_solubility = '${fluid_solubility}'
    dissociation_coeff = '${primary_dissociation_coefficient}'
    recombination_coeff = '${primary_recombination_coefficient}'
    is_homonuclear = true
    equilibrium_constant = '${fluid_solubility}'
    wall_solubility = '${wall_henry_solubility}'
  []
  [wall_concentration_RHS]
    type = ParsedODEKernel
    expression = 'wall_concentration - ${concentration_outlet}*2'
    variable = wall_concentration
  []
[]

[Postprocessors]
  [dummyPP]
    type = ConstantPostprocessor
    value = ${wall_sievert_solubility}
  []
  [concentration_flux]
    type = ParsedPostprocessor
    expression = '2 * ${primary_recombination_coefficient} * (2*${concentration_outlet})^2 - ${primary_dissociation_coefficient} * concentration_PP / ${fluid_solubility}'
    pp_names = 'concentration_PP'
    execute_on = 'TIMESTEP_END'
  []
  [analytical_steady_state_concentration]
    type = ParsedPostprocessor
    expression = '-(log(2)/${primary_half_life} + abs(mass_flow_rate_PP)/${pipe_length}/${pipe_area}/${density})^(-1)
                  *((1/${pipe_length}/${pipe_area}/${density})*(mass_flow_rate_PP/2*(1-abs(mass_flow_rate_PP)/mass_flow_rate_PP)*${concentration_outlet}
                  -mass_flow_rate_PP/2*(1+abs(mass_flow_rate_PP)/mass_flow_rate_PP)*${concentration_inlet}) - ${precursor_concentration_inlet}*log(2)/${precursor_half_life}
                  - concentration_flux*2*3.14159*${pipe_radius}/${pipe_area})'
    pp_names = 'concentration_flux mass_flow_rate_PP'
  []
  [relative_error]
    type = ParsedPostprocessor
    expression = 'abs((analytical_steady_state_concentration - concentration_PP)/analytical_steady_state_concentration)'
    pp_names = 'analytical_steady_state_concentration concentration_PP'
    execute_on = 'TIMESTEP_END'
  []
  [one_percent_flag]
    type = ParsedPostprocessor
    expression = 'relative_error < 0.01'
    pp_names = 'relative_error'
    execute_on = 'TIMESTEP_END'
  []
[]
