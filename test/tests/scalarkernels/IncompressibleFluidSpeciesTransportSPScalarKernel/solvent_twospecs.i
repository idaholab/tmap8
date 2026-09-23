

length = 1.0
R = 0.025
min = 1.0
Pin = 101300
dP = -10130
Tin = 293.15
Tout = 323.15
Cin = 0.0
Cout = 0.02
Prein = 0.0
rho = 998.2
mu = 0.001002
alpha = 0.0
epsilon = 0.0001
forms = 0.0
pump = 0.0
gravity = 0.0
area = '${fparse 3.14159* ${R}^2}'
diffus = 1.0e-08
PHL = 1000000000000000
HL = 1000000000000000
fsol = '${fparse 8.0e-04*3.34e+22*100^3/101325/6.022e+23}'
wsols = 2.25e-02 #sieverts
wsolh = '${fparse 32.0e-04*3.34e+22*100^3/101325/6.022e+23}' #henrys
wsol = ${wsolh}
dissoc = 1.0e-11
recomb = 1.0e-33
ftype = "solvent"
equib = 0.5

[Mesh]
  type = GeneratedMesh
  dim = 1
  xmin = 0
  xmax = ${length}
  nx = 1
[]

[Variables]
  [m1]
    family = SCALAR
    initial_condition = ${min}
  []
  [dPc]
    family = SCALAR
    initial_condition = ${dP}
  []
  [T0]
    family = SCALAR
    initial_condition = ${Tin}
  []
  [T1]
    family = SCALAR
    initial_condition = ${Tin}
  []
  [Tw]
    family = SCALAR
    initial_condition = ${Tout}
  []
  [T2]
    family = SCALAR
    initial_condition = ${Tout}
  []
  [C0]
    family = SCALAR
    initial_condition = ${Cin}
  []
  [C1]
    family = SCALAR
    initial_condition = ${Cin}
  []
  [Cw1]
    family = SCALAR
    initial_condition = '${fparse ${Cout}}'
  []
  [Cw2]
    family = SCALAR
    initial_condition = '${fparse ${Cout}}'
  []
  [C2]
    family = SCALAR
    initial_condition = ${Cout}
  []
  [P1]
    family = SCALAR
    initial_condition = ${Prein}
  []
[]

[FluidProperties]
  [water]
    type = Water97FluidProperties
  []
[]

[ScalarKernels]
  [pipe1_mom]
    type = IncompressibleMomentumSPScalarKernel
    variable = 'm1'
    reference_pressure_drop = 'dPc'
    temperatures = 'T1'
    reference_pressure = ${Pin}
    fp = 'water'
    areas = '${area}'
    perimeters = '${fparse 2*3.14159* ${R}}'
    lengths = '${length}'
    alphas = '${alpha}'
    forms_losses = '${forms}'
    pump_pressures = '${pump}'
    roughnesses = '${epsilon}'
    g = ${gravity}
    is_implicit = True
  []
  [temp0]
    type = ParsedODEKernel
    expression = 'T0 - ${Tin}'
    variable = T0
  []
  [temp1]
    type = IncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T0'
    outlet_temperature = 'T2'
    wall_temperature = 'Tw'
    area = ${area}
    fp = water
    length = ${length}
    perimeter = '${fparse 2*3.14159* ${R}}'
    reference_pressure = ${Pin}
    variable = T1
    is_implicit = True
  []
  [temp2]
    type = ParsedODEKernel
    expression = 'T2 - ${Tout}'
    variable = T2
  []
  [walltemp]
    type = ParsedODEKernel
    expression = 'Tw - ${Tout}'
    variable = Tw
  []
  [conc0]
    type = ParsedODEKernel
    expression = 'C0 - ${Cin}'
    variable = C0
  []
  [conc1]
    type = IncompressibleFluidSpeciesTransportSPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T0'
    outlet_temperature = 'T2'
    wall_temperature = 'Tw'
    area = ${area}
    fp = water
    length = ${length}
    perimeter = '${fparse 2*3.14159* ${R}}'
    reference_pressure = ${Pin}
    variable = C1
    is_implicit = True
    temperature = 'T1'
    upstream_concentration = 'C0'
    downstream_concentration = 'C2'
    precursors = 'P1'
    precursor_half_lives = '${PHL}'
    wall_dissociated_atoms = 'Cw1 Cw2'
    half_life = '${HL}'
    fluid_type = ${ftype}
    species_diffusivity = ${diffus}
    fluid_solubility = '${fsol}'
    dissociation_coeff = '${dissoc}'
    recombination_coeff = '${recomb}'
    is_homonuclear = false
    equilibrium_constant = '${equib}'
    wall_solubility = '${fparse ${wsol}} ${wsol}'
  []
  [conc2]
    type = ParsedODEKernel
    expression = 'C2 - ${Cout}'
    variable = C2
  []
  [wallconc1]
    type = ParsedODEKernel
    expression = 'Cw1 - ${Cout}'
    variable = Cw1
  []
  [wallconc2]
    type = ParsedODEKernel
    expression = 'Cw2 - ${Cout}'
    variable = Cw2
  []
  [pre1]
    type = ParsedODEKernel
    expression = 'P1 - ${Prein}'
    variable = P1
  []
  [dPk]
    type = ParsedODEKernel
    expression = 'dPc - ${dP}'
    variable = dPc
  []
[]

[Postprocessors]
  [dummyPP]
    type = ConstantPostprocessor
    value = ${wsols}
  []
  [C]
    type = ScalarVariable
    variable = C1
    execute_on = 'TIMESTEP_END'
  []
  [M]
    type = ScalarVariable
    variable = m1
    execute_on = 'TIMESTEP_END'
  []
  [T]
    type = ScalarVariable
    variable = T1
    execute_on = 'TIMESTEP_END'
  []
  [Re]
    type = ParsedPostprocessor
    expression = 'abs(M) / ${area} * 2 * ${R} / ${mu}'
    pp_names = 'M'
    execute_on = 'TIMESTEP_END'
  []
  [Sc]
    type = ParsedPostprocessor
    expression = '${mu} / ${diffus} / ${rho}'
    execute_on = 'TIMESTEP_END'
  []
  [Kt]
    type = ParsedPostprocessor
    expression = '0.023 * Re^0.8 * Sc^0.3333 * ${diffus} / ${R} / 2'
    pp_names = 'Re Sc'
    execute_on = 'TIMESTEP_END'
  []
  [in]
    type = ParsedPostprocessor
    expression = '1 / 2 * (1 - abs(M)/M) * ${Cout}
                  + 1 / 2 * (1 + abs(M)/M) * ${Cin}'
    pp_names = 'M'
    execute_on = 'TIMESTEP_END'
  []
  [Jgas]
    type = ParsedPostprocessor
    expression = '2 * ${recomb} * (${Cout})^2 - ${dissoc} * C / ${fsol}'
    pp_names = 'C'
    execute_on = 'TIMESTEP_END'
  []
  [Jmetal]
    type = ParsedPostprocessor
    expression = 'Kt * (${wsol} / ${fsol} * 2*${Cout} - C)'
    pp_names = 'Kt C'
    execute_on = 'TIMESTEP_END'
  []
  [Jsolvent]
    type = ParsedPostprocessor
    expression = 'Kt / 1.380649E-23 / 6.022E+23 / T * ((${Cout})^2 / (${wsol})^2 * sqrt(${equib}) - C)'
    pp_names = 'Kt C T'
    execute_on = 'TIMESTEP_END'
  []
  [analytical_Csolvent]
    type = ParsedPostprocessor
    expression = '-(log(2)/${HL} + abs(M)/${length}/${area}/${rho})^(-1)
                  *((1/${length}/${area}/${rho})*(M/2*(1-abs(M)/M)*${Cout}
                  -M/2*(1+abs(M)/M)*${Cin}) - ${Prein}*log(2)/${PHL}
                  - Jsolvent*2*3.14159*${R}/${area})'
    pp_names = 'Jsolvent M'
  []
  [analytical_Cmetal]
    type = ParsedPostprocessor
    expression = '-(log(2)/${HL} + abs(M)/${length}/${area}/${rho})^(-1)
                  *((1/${length}/${area}/${rho})*(M/2*(1-abs(M)/M)*${Cout}
                  -M/2*(1+abs(M)/M)*${Cin}) - ${Prein}*log(2)/${PHL}
                  - Jmetal*2*3.14159*${R}/${area})'
    pp_names = 'Jmetal M'
  []
  [analytical_Cgas]
    type = ParsedPostprocessor
    expression = '-(log(2)/${HL} + abs(M)/${length}/${area}/${rho})^(-1)
                  *((1/${length}/${area}/${rho})*(M/2*(1-abs(M)/M)*${Cout}
                  -M/2*(1+abs(M)/M)*${Cin}) - ${Prein}*log(2)/${PHL}
                  - Jgas*2*3.14159*${R}/${area})'
    pp_names = 'Jgas M'
  []
  [relative_error_solvent]
    type = ParsedPostprocessor
    expression = 'abs((analytical_Csolvent - C)/analytical_Csolvent)'
    pp_names = 'analytical_Csolvent C'
    execute_on = 'TIMESTEP_END'
  []
  [relative_error_metal]
    type = ParsedPostprocessor
    expression = 'abs((analytical_Cmetal - C)/analytical_Cmetal)'
    pp_names = 'analytical_Cmetal C'
    execute_on = 'TIMESTEP_END'
  []
  [relative_error_gas]
    type = ParsedPostprocessor
    expression = 'abs((analytical_Cgas - C)/analytical_Cgas)'
    pp_names = 'analytical_Cgas C'
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
