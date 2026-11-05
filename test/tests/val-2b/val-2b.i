# Validation Problem #2b from TMAP4/TMAP7 V&V document
# Thermal desorption of deuterium from BeO/Be with time-varying temperature and enclosure pressure
# No trapping terms

# Physical constants
R = ${units 8.31446261815324 J/mol/K} # ideal gas constant based on number used in include/utils/PhysicalConstants.h

# Pressure conditions
pressure_enclosure_init = ${units 13300 Pa}
pressure_enclosure_cooldown = ${units 1e-6 Pa} # vaccum
pressure_enclosure_desorption = ${units 1e-3 Pa} # vaccum, assumed

# Temperature conditions
temperature_initial = ${units 773 K}
temperature_desorption_min = ${units 300 K}
temperature_desorption_max = ${units 1073 K}
temperature_cooldown_min = ${temperature_desorption_min}
desorption_heating_rate = ${units ${fparse 3/60} K/s}

# Important times
charge_time = ${units 50 h -> s}
cooldown_time_constant = ${units ${fparse 45*60} s}
# TMAP4 and TMAP7 used 40 minutes for the cooldown duration,
# We use a 5 hour cooldown period to let the temperature decrease to around 300 K for the start of the desorption.
# R.G. Macaulay-Newcombe et al. (1991) is not very clear on how long samples cooled down.
cooldown_duration = ${units 5 h -> s}
desorption_duration = ${fparse (temperature_desorption_max-temperature_desorption_min)/desorption_heating_rate}
endtime = ${fparse charge_time + cooldown_duration + desorption_duration}

# Materials properties
concentration_scaling = 1e10 # (-)
diffusion_Be_preexponential = ${units 8.0e-9 m^2/s -> mum^2/s}
diffusion_Be_energy = ${units 4220 K}
diffusion_BeO_preexponential_charging = ${units 1.40e-4 m^2/s -> mum^2/s}
diffusion_BeO_energy_charging = ${units 24408 K}
diffusion_BeO_preexponential_desorption = ${units 7e-5 m^2/s -> mum^2/s}
diffusion_BeO_energy_desorption = ${units 27000 K}
solubility_order = .5 # order of the solubility law (Here, we use Sieverts' law)
solubility_constant_BeO = ${fparse 5.00e20 / 1e18 / concentration_scaling} # at/m^3/Pa^0.5 -> at/mum^3/Pa^0.5}
solubility_energy_BeO = ${units -9377.7 K}
solubility_constant_Be = ${fparse 7.156e27 / 1e18 / concentration_scaling} # at/m^3/Pa^0.5 -> at/mum^3/Pa^0.5}
solubility_energy_Be = ${units 11606 K}
jump_penalty = 1e0 # (-)

# Numerical parameters
dt_max_large = ${units 100 s}
dt_max_small = ${units 10 s}
dt_start_charging = ${units 1 s}
dt_start_cooldown = ${units 10 s}
dt_start_desorption = ${units 1 s}

# Geometry and mesh
length_BeO = ${units 18 nm -> mum}
num_nodes_BeO = 18
node_length_BeO = ${fparse length_BeO / num_nodes_BeO}
length_Be = ${units 0.4 mm -> mum}
length_Be_modeled = ${fparse length_Be/2}
num_nodes_Be = 40
node_length_Be = ${fparse length_Be_modeled / num_nodes_Be}

[Mesh]
  [cmg]
    type = CartesianMeshGenerator
    dim = 1

    #     0                  1                  2                  3                  4                  5                  6                  7                  8                  9                  10                 11                 12                 13                 14                 15                 16                 17
    dx = '${node_length_BeO} ${node_length_BeO} ${node_length_BeO} ${node_length_BeO} ${node_length_BeO} ${node_length_BeO} ${node_length_BeO} ${node_length_BeO} ${node_length_BeO} ${node_length_BeO} ${node_length_BeO} ${node_length_BeO} ${node_length_BeO} ${node_length_BeO} ${node_length_BeO} ${node_length_BeO} ${node_length_BeO} ${node_length_BeO}
          ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be}
          ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be} ${node_length_Be}'
    #     18                19                20                21                22                23                24                25                26                27                28                29                30                31                32                33                34                35                36                37

    #               0 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17
    subdomain_id = '0 0 0 0 0 0 0 0 0 0 0  0  0  0  0  0  0  0
                    1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1
                    1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1  1'
    #               18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37'

  []
  # two surfaces for interface
  [interface]
    type = SideSetsBetweenSubdomainsGenerator
    input = cmg
    primary_block = '0' #BeO
    paired_block = '1' # Be
    new_boundary = 'interface'
  []
  [interface_other_side]
    type = SideSetsBetweenSubdomainsGenerator
    input = interface
    primary_block = '1' #BeO
    paired_block = '0' # Be
    new_boundary = 'interface_other'
  []
[]

[Variables]
  # Mobile deuterium concentrations in BeO and Be domains
  [deuterium_concentration_Be] # (atoms/microns^3) / concentration_scaling
    block = 1
  []
  [deuterium_concentration_BeO] # (atoms/microns^3) / concentration_scaling
    block = 0
  []
[]

[AuxVariables]
  # Transient enclosure pressure and temperature used in source/BC functions
  [enclosure_pressure]
    family = SCALAR
    initial_condition = ${pressure_enclosure_init}
  []
  [temperature]
    initial_condition = ${temperature_initial}
  []
  # Flux diagnostic across both materials
  [flux_x]
    order = FIRST
    family = MONOMIAL
  []
[]

[Kernels]
  # Transient diffusion of deuterium in BeO
  [time_BeO]
    type = TimeDerivative
    variable = deuterium_concentration_BeO
    block = 0
  []
  [diffusion_BeO]
    type = ADMatDiffusion
    variable = deuterium_concentration_BeO
    diffusivity = diffusivity_BeO
    block = 0
  []
  # Transient diffusion of deuterium in Be
  [time_Be]
    type = TimeDerivative
    variable = deuterium_concentration_Be
    block = 1
  []
  [diffusion_Be]
    type = ADMatDiffusion
    variable = deuterium_concentration_Be
    diffusivity = diffusivity_Be
    block = 1
  []
[]

[InterfaceKernels]
  # Penalized continuity with solubility jump at BeO/Be interface
  [tied]
    type = ADPenaltyInterfaceDiffusion
    variable = deuterium_concentration_BeO
    neighbor_var = deuterium_concentration_Be
    penalty = ${jump_penalty}
    jump_prop_name = solubility_ratio
    boundary = 'interface'
  []
[]

[AuxScalarKernels]
  # Time-dependent enclosure pressure driving equilibrium BC
  [enclosure_pressure_aux]
    type = FunctionScalarAux
    variable = enclosure_pressure
    function = enclosure_pressure_func
  []
[]

[AuxKernels]
  # Temperature schedule applied as an auxiliary variable and used in functions
  [temperature_aux]
    type = FunctionAux
    variable = temperature
    function = temperature_bc_func
    execute_on = 'INITIAL LINEAR'
  []
  # Flux reconstruction for Be and BeO regions
  [flux_x_Be]
    type = DiffusionFluxAux
    diffusivity = diffusivity_Be
    variable = flux_x
    diffusion_variable = deuterium_concentration_Be
    component = x
    block = 1
  []
  [flux_x_BeO]
    type = DiffusionFluxAux
    diffusivity = diffusivity_BeO
    variable = flux_x
    diffusion_variable = deuterium_concentration_BeO
    component = x
    block = 0
  []
[]

[BCs]
  # Sieverts' law equilibrium on the left surface; symmetry on the right
  [left_flux]
    type = EquilibriumBC
    Ko = ${solubility_constant_BeO}
    activation_energy = '${fparse solubility_energy_BeO * R}'
    boundary = left
    enclosure_var = enclosure_pressure
    temperature = temperature
    variable = deuterium_concentration_BeO
    p = ${solubility_order}
  []
  [right_flux]
    type = ADNeumannBC
    boundary = right
    variable = deuterium_concentration_Be
    value = 0
  []
[]

[Functions]
  # Temperature, pressure, and property functions driving modeling
  [temperature_bc_func]
    type = ParsedFunction
    expression = 'if(t<${charge_time}, ${temperature_initial}, if(t<${fparse charge_time + cooldown_duration}, ${temperature_initial}-((1-exp(-(t-${charge_time})/${cooldown_time_constant}))*${fparse temperature_initial - temperature_cooldown_min}), ${temperature_desorption_min}+${desorption_heating_rate}*(t-${fparse charge_time + cooldown_duration})))'
  []
  [diffusivity_BeO_func]
    type = ParsedFunction
    symbol_names = 'T'
    symbol_values = 'temperature_bc_func'
    expression = 'if(t<${fparse charge_time + cooldown_duration}, ${diffusion_BeO_preexponential_charging}*exp(-${diffusion_BeO_energy_charging}/T), ${diffusion_BeO_preexponential_desorption}*exp(-${diffusion_BeO_energy_desorption}/T))'
  []
  [diffusivity_Be_func]
    type = ParsedFunction
    symbol_names = 'T'
    symbol_values = 'temperature_bc_func'
    expression = '${diffusion_Be_preexponential}*exp(-${diffusion_Be_energy}/T)'
  []
  [enclosure_pressure_func]
    type = ParsedFunction
    expression = 'if(t<${charge_time}, ${pressure_enclosure_init}, if(t<${fparse charge_time + cooldown_duration}, ${pressure_enclosure_cooldown}, ${pressure_enclosure_desorption}))'
  []
  [solubility_BeO_func]
    type = ParsedFunction
    symbol_names = 'T'
    symbol_values = 'temperature_bc_func'
    expression = '${solubility_constant_BeO} * exp(-${solubility_energy_BeO}/T)'
  []
  [solubility_Be_func]
    type = ParsedFunction
    symbol_names = 'T'
    symbol_values = 'temperature_bc_func'
    expression = '${solubility_constant_Be} * exp(-${solubility_energy_Be}/T)'
  []
  [max_time_step_size_func]
    type = ParsedFunction
    expression = 'if(t < ${fparse charge_time-dt_max_large}, ${dt_max_large}, ${dt_max_small})'
  []
[]

[Materials]
  # Temperature-dependent diffusivity and solubility materials plus interface jump ratio
  [diffusion_solubility]
    type = ADGenericFunctionMaterial
    prop_names = 'diffusivity_BeO diffusivity_Be solubility_Be solubility_BeO'
    prop_values = 'diffusivity_BeO_func diffusivity_Be_func solubility_Be_func solubility_BeO_func'
    outputs = 'exodus'
  []
  [converter_to_nonAD]
    type = MaterialADConverter
    ad_props_in = 'diffusivity_Be diffusivity_BeO'
    reg_props_out = 'diffusivity_Be_nonAD diffusivity_BeO_nonAD'
    outputs = 'exodus'
  []
  [interface_jump]
    type = SolubilityRatioMaterial
    solubility_primary = solubility_BeO
    solubility_secondary = solubility_Be
    boundary = interface
    concentration_primary = deuterium_concentration_BeO
    concentration_secondary = deuterium_concentration_Be
    outputs = 'exodus'
  []
[]

[Postprocessors]
  # Flux
  [avg_flux_left]
    type = SideDiffusiveFluxAverage
    variable = deuterium_concentration_BeO
    boundary = left
    diffusivity = diffusivity_BeO_nonAD
  []
  [avg_flux_total] # total flux coming out of the sample in atoms/microns^2/s
    type = ScalePostprocessor
    value = avg_flux_left
    scaling_factor = '${fparse 2 * concentration_scaling}'
    # Factor of 2 because symmetry is assumed and only one-half of the specimen is modeled.
    # Thus, the total flux coming out of the specimen (per unit area)
    # is twice the flux calculated at the left side of the domain.
    # The 'concentration_scaling' parameter is used to get a consistent concentration unit
  []
  # material properties
  [temperature]
    type = ElementAverageValue
    block = 0
    variable = temperature
    execute_on = 'initial timestep_end'
  []
  [diffusion_Be]
    type = ElementAverageValue
    block = 1
    variable = diffusivity_Be
    outputs = 'exodus csv'
  []
  [diffusion_BeO]
    type = ElementAverageValue
    block = 0
    variable = diffusivity_BeO
    outputs = 'exodus csv'
  []
  [solubility_Be]
    type = ElementAverageValue
    block = 1
    variable = solubility_Be
    outputs = 'exodus csv'
  []
  [solubility_BeO]
    type = ElementAverageValue
    block = 0
    variable = solubility_BeO
    outputs = 'exodus csv'
  []
  [gold_solubility_ratio]
    type = ParsedPostprocessor
    pp_names = 'solubility_BeO solubility_Be'
    expression = 'solubility_BeO / solubility_Be'
  []
  [BeO_interface]
    type = SideAverageValue
    boundary = interface
    variable = deuterium_concentration_BeO
  []
  [Be_interface]
    type = SideAverageValue
    boundary = interface_other
    variable = deuterium_concentration_Be
  []
  [variable_ratio]
    type = ParsedPostprocessor
    pp_names = 'BeO_interface Be_interface'
    expression = 'BeO_interface / Be_interface'
  []
  [dt]
    type = TimestepSize
  []
  [max_time_step_size_pp]
    type = FunctionValuePostprocessor
    function = max_time_step_size_func
    execute_on = 'INITIAL TIMESTEP_END'
    outputs = none
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
  nl_rel_tol = 1e-6
  nl_abs_tol = 5e-12
  end_time = ${endtime}
  automatic_scaling = true
  compute_scaling_once = false
  nl_max_its = 7
  [TimeStepper]
    type = IterationAdaptiveDT
    dt = ${dt_start_charging}
    optimal_iterations = 5
    growth_factor = 1.1
    cutback_factor_at_failure = .9
    timestep_limiting_postprocessor = max_time_step_size_pp
    time_t = ' 0                    ${charge_time}        ${fparse charge_time + cooldown_duration}'
    time_dt = '${dt_start_charging} ${dt_start_cooldown}  ${dt_start_desorption}'
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
  []
[]
