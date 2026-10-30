# This input file models the transient natural circulation startup of a
# lead-lithium eutectic (PbLi) loop based on an experiment conducted at Oak
# Ridge National Laboratory (ORNL), with a code-to-code comparison against a
# RELAP5 model developed at the University of Tennessee-Knoxville (UTK). It
# is identical to PbLi_Loop_steady.i except that time derivatives are enabled
# on all scalar variables and the loop is run from a uniform initial
# temperature to a 21600 s end time, allowing the flow and temperature
# distribution to develop from rest as the imposed wall heat fluxes drive
# buoyant circulation. Loop geometry, boundary heat fluxes, and comparison
# postprocessors against the RELAP5 model and the ORNL experimental
# measurements are the same as in the steady-state case.
# Unit system: SI (length in meters, temperature in Kelvin, pressure in Pascals)

Lx = 0.495
Ly = 0.71
m_horiz = 0.25
inner_diameter = 0.0267
wall_thickness = 0.0031
reference_pressure = 101325
initial_temperature = 745
flow_area = '${fparse pi / 4 * inner_diameter^2}'
wetted_perimeter = '${fparse pi * inner_diameter}'
midthickness_diameter = '${fparse inner_diameter + wall_thickness}'
outer_diameter = '${fparse inner_diameter + 2 * wall_thickness}'
inner_wall_area = '${fparse pi / 4 * midthickness_diameter^2 - pi / 4 * inner_diameter^2}'
outer_wall_area = '${fparse pi / 4 * outer_diameter^2 - pi / 4 * midthickness_diameter^2}'
midthickness_perimeter = '${fparse pi * midthickness_diameter}'
outer_perimeter = '${fparse pi * outer_diameter}'
Q_horiz = 148.3
Q_vert = 638.7
chains_loss = 62.5

[Functions]
    [kw]
        type = PiecewiseLinear
        x = '323.15 873.15 1073.15 1273.15 1473.15'
        y = '11 21 23 27 29'
    []
    [cpw]
        type = PiecewiseLinear
        x = '293.15 473.15 673.15 873.15 1073.15 1273.15 1473.15'
        y = '480.0 560.0 640.0 710.0 670.0 690.0 700.0'
    []
    [rhof]
        type = ParsedFunction
        expression = '10520.35 - 1.19051 * t'
    []
[]

[FluidProperties]
  [PbLi]
    type = LeadLithiumFluidProperties
  []
[]

[SolidProperties]
  [APMT]
    type = ThermalFunctionSolidProperties
    k = kw
    cp = cpw
    rho = 7250
  []
[]

[Problem]
  allow_invalid_solution = true
[]

[Mesh]
  type = GeneratedMesh
  dim = 1
  xmin = 0
  xmax = 1
  nx = 1
[]

[Variables]
  [m1]
    family = SCALAR
    initial_condition = 0.1
  []
  [dPc]
    family = SCALAR
    initial_condition = 0.0
  []
  [T01]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T02]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T03]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T04]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T05]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T06]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T07]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T08]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T09]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T10]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T11]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T12]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T13]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T14]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T15]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T16]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T17]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T18]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T19]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T20]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T21]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T22]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T23]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T24]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T25]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T26]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T27]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T28]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T29]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T30]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T31]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T32]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T33]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T34]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T35]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T36]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T37]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T38]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T39]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [T40]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi01]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi02]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi03]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi04]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi05]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi06]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi07]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi08]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi09]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi10]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi11]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi12]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi13]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi14]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi15]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi16]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi17]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi18]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi19]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi20]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi21]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi22]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi23]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi24]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi25]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi26]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi27]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi28]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi29]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi30]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi31]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi32]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi33]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi34]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi35]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi36]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi37]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi38]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi39]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Twi40]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two01]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two02]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two03]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two04]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two05]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two06]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two07]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two08]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two09]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two10]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two11]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two12]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two13]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two14]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two15]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two16]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two17]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two18]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two19]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two20]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two21]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two22]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two23]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two24]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two25]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two26]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two27]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two28]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two29]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two30]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two31]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two32]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two33]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two34]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two35]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two36]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two37]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two38]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two39]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
  [Two40]
    family = SCALAR
    initial_condition = ${initial_temperature}
  []
[]

[ScalarKernels]
  [cold_leg]
    type = ADIncompressibleMomentumSPScalarKernel
    variable = 'm1'
    reference_pressure_drop = 'dPc'
    temperatures = ' T01  T02  T03  T04  T05  T06  T07  T08  T09 T10 
                    T11 T12 T13 T14 T15 T16 T17 T18 T19 T20'
    reference_pressure = ${reference_pressure}
    fp = 'PbLi'
    areas = '${flow_area} ${flow_area} ${flow_area} ${flow_area} ${flow_area} 
             ${flow_area} ${flow_area} ${flow_area} ${flow_area} ${flow_area} 
             ${flow_area} ${flow_area} ${flow_area} ${flow_area} ${flow_area} 
             ${flow_area} ${flow_area} ${flow_area} ${flow_area} ${flow_area}'
    perimeters = '${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter} 
                  ${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter} 
                  ${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter} 
                  ${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter}'
    lengths = '${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10} ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10} 
               ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10} ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10} 
               ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10} ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10} 
               ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10} ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10} 
               ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10} ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10} 
               ${fparse Ly/10} ${fparse Ly/10} ${fparse Ly/10} ${fparse Ly/10} ${fparse Ly/10} 
               ${fparse Ly/10} ${fparse Ly/10} ${fparse Ly/10} ${fparse Ly/10} ${fparse Ly/10}'
    alphas = '${fparse -atan(m_horiz)} ${fparse -atan(m_horiz)} 
              ${fparse -atan(m_horiz)} ${fparse -atan(m_horiz)} 
              ${fparse -atan(m_horiz)} ${fparse -atan(m_horiz)} 
              ${fparse -atan(m_horiz)} ${fparse -atan(m_horiz)} 
              ${fparse -atan(m_horiz)} ${fparse -atan(m_horiz)} 
              ${fparse -pi/2} ${fparse -pi/2} ${fparse -pi/2} ${fparse -pi/2} ${fparse -pi/2} 
              ${fparse -pi/2} ${fparse -pi/2} ${fparse -pi/2} ${fparse -pi/2} ${fparse -pi/2}'
    forms_losses = '0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 
                    ${chains_loss} ${chains_loss} 
                    ${chains_loss} ${chains_loss} 
                    ${chains_loss} ${chains_loss} 
                    ${chains_loss} ${chains_loss} 
                    ${chains_loss} ${chains_loss}'
    pump_pressures = '0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 
                      0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0'
    roughnesses = '0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 
                   0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0'
  []
  [cold_leg_DT]
    type = ADScalarTimeDerivative
    variable = 'm1'
  []
  [hot_leg]
    type = ADCoupledPressureIncompressibleMomentumSPScalarKernel
    variable = 'dPc'
    coupled_mass_flow_rate = 'm1'
    temperatures = 'T21 T22 T23 T24 T25 T26 T27 T28 T29 T30 
                    T31 T32 T33 T34 T35 T36 T37 T38 T39 T40'
    reference_pressure = ${reference_pressure}
    fp = 'PbLi'
    areas = '${flow_area} ${flow_area} ${flow_area} ${flow_area} ${flow_area} 
             ${flow_area} ${flow_area} ${flow_area} ${flow_area} ${flow_area} 
             ${flow_area} ${flow_area} ${flow_area} ${flow_area} ${flow_area} 
             ${flow_area} ${flow_area} ${flow_area} ${flow_area} ${flow_area}'
    perimeters = '${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter} 
                  ${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter} 
                  ${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter} 
                  ${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter} ${wetted_perimeter}'
    lengths = '${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10} ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10} 
               ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10} ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10} 
               ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10} ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10} 
               ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10} ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10} 
               ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10} ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10} 
               ${fparse Ly/10} ${fparse Ly/10} ${fparse Ly/10} ${fparse Ly/10} ${fparse Ly/10} 
               ${fparse Ly/10} ${fparse Ly/10} ${fparse Ly/10} ${fparse Ly/10} ${fparse Ly/10}'
    alphas = '${fparse atan(m_horiz)} ${fparse atan(m_horiz)} 
              ${fparse atan(m_horiz)} ${fparse atan(m_horiz)} 
              ${fparse atan(m_horiz)} ${fparse atan(m_horiz)} 
              ${fparse atan(m_horiz)} ${fparse atan(m_horiz)} 
              ${fparse atan(m_horiz)} ${fparse atan(m_horiz)} 
              ${fparse pi/2} ${fparse pi/2} ${fparse pi/2} ${fparse pi/2} ${fparse pi/2} 
              ${fparse pi/2} ${fparse pi/2} ${fparse pi/2} ${fparse pi/2} ${fparse pi/2}'
    forms_losses = '0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 
                    ${chains_loss} ${chains_loss} 
                    ${chains_loss} ${chains_loss} 
                    ${chains_loss} ${chains_loss} 
                    ${chains_loss} ${chains_loss} 
                    ${chains_loss} ${chains_loss}'
    pump_pressures = '0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 
                      0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0'
    roughnesses = '0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 
                   0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0'
  []
  [hot_leg_DT]
    type = CoupledODETimeDerivative
    variable = 'dPc'
    v = 'm1'
  []
  [temp1]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T40'
    outlet_temperature = 'T02'
    wall_temperature = 'Twi01'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T01
  []
  [temp1_DT]
    type = ADScalarTimeDerivative
    variable = 'T01'
  []
  [temp2]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T01'
    outlet_temperature = 'T03'
    wall_temperature = 'Twi02'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T02
  []
  [temp2_DT]
    type = ADScalarTimeDerivative
    variable = 'T02'
  []
  [temp3]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T02'
    outlet_temperature = 'T04'
    wall_temperature = 'Twi03'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T03
  []
  [temp3_DT]
    type = ADScalarTimeDerivative
    variable = 'T03'
  []
  [temp4]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T03'
    outlet_temperature = 'T05'
    wall_temperature = 'Twi04'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T04
  []
  [temp4_DT]
    type = ADScalarTimeDerivative
    variable = 'T04'
  []
  [temp5]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T04'
    outlet_temperature = 'T06'
    wall_temperature = 'Twi05'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T05
  []
  [temp5_DT]
    type = ADScalarTimeDerivative
    variable = 'T05'
  []
  [temp6]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T05'
    outlet_temperature = 'T07'
    wall_temperature = 'Twi06'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T06
  []
  [temp6_DT]
    type = ADScalarTimeDerivative
    variable = 'T06'
  []
  [temp7]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T06'
    outlet_temperature = 'T08'
    wall_temperature = 'Twi07'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T07
  []
  [temp7_DT]
    type = ADScalarTimeDerivative
    variable = 'T07'
  []
  [temp8]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T07'
    outlet_temperature = 'T09'
    wall_temperature = 'Twi08'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T08
  []
  [temp8_DT]
    type = ADScalarTimeDerivative
    variable = 'T08'
  []
  [temp9]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T08'
    outlet_temperature = 'T10'
    wall_temperature = 'Twi09'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T09
  []
  [temp9_DT]
    type = ADScalarTimeDerivative
    variable = 'T09'
  []
  [temp10]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T09'
    outlet_temperature = 'T11'
    wall_temperature = 'Twi10'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T10
  []
  [temp10_DT]
    type = ADScalarTimeDerivative
    variable = 'T10'
  []
  [temp11]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T10'
    outlet_temperature = 'T12'
    wall_temperature = 'Twi11'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse Ly/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T11
  []
  [temp11_DT]
    type = ADScalarTimeDerivative
    variable = 'T11'
  []
  [temp12]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T11'
    outlet_temperature = 'T13'
    wall_temperature = 'Twi12'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse Ly/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T12
  []
  [temp12_DT]
    type = ADScalarTimeDerivative
    variable = 'T12'
  []
  [temp13]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T12'
    outlet_temperature = 'T14'
    wall_temperature = 'Twi13'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse Ly/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T13
  []
  [temp13_DT]
    type = ADScalarTimeDerivative
    variable = 'T13'
  []
  [temp14]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T13'
    outlet_temperature = 'T15'
    wall_temperature = 'Twi14'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse Ly/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T14
  []
  [temp14_DT]
    type = ADScalarTimeDerivative
    variable = 'T14'
  []
  [temp15]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T14'
    outlet_temperature = 'T16'
    wall_temperature = 'Twi15'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse Ly/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T15
  []
  [temp15_DT]
    type = ADScalarTimeDerivative
    variable = 'T15'
  []
  [temp16]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T15'
    outlet_temperature = 'T17'
    wall_temperature = 'Twi16'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse Ly/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T16
  []
  [temp16_DT]
    type = ADScalarTimeDerivative
    variable = 'T16'
  []
  [temp17]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T16'
    outlet_temperature = 'T18'
    wall_temperature = 'Twi17'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse Ly/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T17
  []
  [temp17_DT]
    type = ADScalarTimeDerivative
    variable = 'T17'
  []
  [temp18]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T17'
    outlet_temperature = 'T19'
    wall_temperature = 'Twi18'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse Ly/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T18
  []
  [temp18_DT]
    type = ADScalarTimeDerivative
    variable = 'T18'
  []
  [temp19]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T18'
    outlet_temperature = 'T20'
    wall_temperature = 'Twi19'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse Ly/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T19
  []
  [temp19_DT]
    type = ADScalarTimeDerivative
    variable = 'T19'
  []
  [temp20]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T19'
    outlet_temperature = 'T21'
    wall_temperature = 'Twi20'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse Ly/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T20
  []
  [temp20_DT]
    type = ADScalarTimeDerivative
    variable = 'T20'
  []
  [temp21]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T20'
    outlet_temperature = 'T22'
    wall_temperature = 'Twi21'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T21
  []
  [temp21_DT]
    type = ADScalarTimeDerivative
    variable = 'T21'
  []
  [temp22]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T21'
    outlet_temperature = 'T23'
    wall_temperature = 'Twi22'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T22
  []
  [temp22_DT]
    type = ADScalarTimeDerivative
    variable = 'T22'
  []
  [temp23]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T22'
    outlet_temperature = 'T24'
    wall_temperature = 'Twi23'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T23
  []
  [temp23_DT]
    type = ADScalarTimeDerivative
    variable = 'T23'
  []
  [temp24]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T23'
    outlet_temperature = 'T25'
    wall_temperature = 'Twi24'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T24
  []
  [temp24_DT]
    type = ADScalarTimeDerivative
    variable = 'T24'
  []
  [temp25]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T24'
    outlet_temperature = 'T26'
    wall_temperature = 'Twi25'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T25
  []
  [temp25_DT]
    type = ADScalarTimeDerivative
    variable = 'T25'
  []
  [temp26]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T25'
    outlet_temperature = 'T27'
    wall_temperature = 'Twi26'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T26
  []
  [temp26_DT]
    type = ADScalarTimeDerivative
    variable = 'T26'
  []
  [temp27]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T26'
    outlet_temperature = 'T28'
    wall_temperature = 'Twi27'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T27
  []
  [temp27_DT]
    type = ADScalarTimeDerivative
    variable = 'T27'
  []
  [temp28]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T27'
    outlet_temperature = 'T29'
    wall_temperature = 'Twi28'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T28
  []
  [temp28_DT]
    type = ADScalarTimeDerivative
    variable = 'T28'
  []
  [temp29]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T28'
    outlet_temperature = 'T30'
    wall_temperature = 'Twi29'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T29
  []
  [temp29_DT]
    type = ADScalarTimeDerivative
    variable = 'T29'
  []
  [temp30]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T29'
    outlet_temperature = 'T31'
    wall_temperature = 'Twi30'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T30
  []
  [temp30_DT]
    type = ADScalarTimeDerivative
    variable = 'T30'
  []
  [temp31]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T30'
    outlet_temperature = 'T32'
    wall_temperature = 'Twi31'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse Ly/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T31
  []
  [temp31_DT]
    type = ADScalarTimeDerivative
    variable = 'T31'
  []
  [temp32]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T31'
    outlet_temperature = 'T33'
    wall_temperature = 'Twi32'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse Ly/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T32
  []
  [temp32_DT]
    type = ADScalarTimeDerivative
    variable = 'T32'
  []
  [temp33]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T32'
    outlet_temperature = 'T34'
    wall_temperature = 'Twi33'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse Ly/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T33
  []
  [temp33_DT]
    type = ADScalarTimeDerivative
    variable = 'T33'
  []
  [temp34]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T33'
    outlet_temperature = 'T35'
    wall_temperature = 'Twi34'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse Ly/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T34
  []
  [temp34_DT]
    type = ADScalarTimeDerivative
    variable = 'T34'
  []
  [temp35]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T34'
    outlet_temperature = 'T36'
    wall_temperature = 'Twi35'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse Ly/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T35
  []
  [temp35_DT]
    type = ADScalarTimeDerivative
    variable = 'T35'
  []
  [temp36]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T35'
    outlet_temperature = 'T37'
    wall_temperature = 'Twi36'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse Ly/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T36
  []
  [temp36_DT]
    type = ADScalarTimeDerivative
    variable = 'T36'
  []
  [temp37]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T36'
    outlet_temperature = 'T38'
    wall_temperature = 'Twi37'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse Ly/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T37
  []
  [temp37_DT]
    type = ADScalarTimeDerivative
    variable = 'T37'
  []
  [temp38]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T37'
    outlet_temperature = 'T39'
    wall_temperature = 'Twi38'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse Ly/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T38
  []
  [temp38_DT]
    type = ADScalarTimeDerivative
    variable = 'T38'
  []
  [temp39]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T38'
    outlet_temperature = 'T40'
    wall_temperature = 'Twi39'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse Ly/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T39
  []
  [temp39_DT]
    type = ADScalarTimeDerivative
    variable = 'T39'
  []
  [temp40]
    type = ADIncompressibleEnergySPScalarKernel
    mass_flow_rate = 'm1'
    inlet_temperature = 'T39'
    outlet_temperature = 'T01'
    wall_temperature = 'Twi40'
    area = ${flow_area} 
    fp = PbLi
    length = ${fparse Ly/10}
    perimeter = '${wetted_perimeter}'
    reference_pressure = ${reference_pressure}
    variable = T40
  []
  [temp40_DT]
    type = ADScalarTimeDerivative
    variable = 'T40'
  []
  [innerwalltemp1]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi01
    mass_flow_rate = m1
    outer_wall_temperature = Two01
    upstream_wall_temperature = Twi40
    downstream_wall_temperature = Twi02
    fluid_temperature = T01
    upstream_fluid_temperature = T40
    downstream_fluid_temperature = T02
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h1
  []
  [innerwalltemp1_dt]
    type = ADScalarTimeDerivative
    variable = Twi01
  []
  [innerwalltemp2]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi02
    mass_flow_rate = m1
    outer_wall_temperature = Two02
    upstream_wall_temperature = Twi01
    downstream_wall_temperature = Twi03
    fluid_temperature = T02
    upstream_fluid_temperature = T01
    downstream_fluid_temperature = T03
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h2
  []
  [innerwalltemp2_dt]
    type = ADScalarTimeDerivative
    variable = Twi02
  []
  [innerwalltemp3]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi03
    mass_flow_rate = m1
    outer_wall_temperature = Two03
    upstream_wall_temperature = Twi02
    downstream_wall_temperature = Twi04
    fluid_temperature = T03
    upstream_fluid_temperature = T02
    downstream_fluid_temperature = T04
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h3
  []
  [innerwalltemp3_dt]
    type = ADScalarTimeDerivative
    variable = Twi03
  []
  [innerwalltemp4]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi04
    mass_flow_rate = m1
    outer_wall_temperature = Two04
    upstream_wall_temperature = Twi03
    downstream_wall_temperature = Twi05
    fluid_temperature = T04
    upstream_fluid_temperature = T03
    downstream_fluid_temperature = T05
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h4
  []
  [innerwalltemp4_dt]
    type = ADScalarTimeDerivative
    variable = Twi04
  []
  [innerwalltemp5]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi05
    mass_flow_rate = m1
    outer_wall_temperature = Two05
    upstream_wall_temperature = Twi04
    downstream_wall_temperature = Twi06
    fluid_temperature = T05
    upstream_fluid_temperature = T04
    downstream_fluid_temperature = T06
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h5
  []
  [innerwalltemp5_dt]
    type = ADScalarTimeDerivative
    variable = Twi05
  []
  [innerwalltemp6]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi06
    mass_flow_rate = m1
    outer_wall_temperature = Two06
    upstream_wall_temperature = Twi05
    downstream_wall_temperature = Twi07
    fluid_temperature = T06
    upstream_fluid_temperature = T05
    downstream_fluid_temperature = T07
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h6
  []
  [innerwalltemp6_dt]
    type = ADScalarTimeDerivative
    variable = Twi06
  []
  [innerwalltemp7]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi07
    mass_flow_rate = m1
    outer_wall_temperature = Two07
    upstream_wall_temperature = Twi06
    downstream_wall_temperature = Twi08
    fluid_temperature = T07
    upstream_fluid_temperature = T06
    downstream_fluid_temperature = T08
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h7
  []
  [innerwalltemp7_dt]
    type = ADScalarTimeDerivative
    variable = Twi07
  []
  [innerwalltemp8]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi08
    mass_flow_rate = m1
    outer_wall_temperature = Two08
    upstream_wall_temperature = Twi07
    downstream_wall_temperature = Twi09
    fluid_temperature = T08
    upstream_fluid_temperature = T07
    downstream_fluid_temperature = T09
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h8
  []
  [innerwalltemp8_dt]
    type = ADScalarTimeDerivative
    variable = Twi08
  []
  [innerwalltemp9]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi09
    mass_flow_rate = m1
    outer_wall_temperature = Two09
    upstream_wall_temperature = Twi08
    downstream_wall_temperature = Twi10
    fluid_temperature = T09
    upstream_fluid_temperature = T08
    downstream_fluid_temperature = T10
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h9
  []
  [innerwalltemp9_dt]
    type = ADScalarTimeDerivative
    variable = Twi09
  []
  [innerwalltemp10]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi10
    mass_flow_rate = m1
    outer_wall_temperature = Two10
    upstream_wall_temperature = Twi09
    downstream_wall_temperature = Twi11
    fluid_temperature = T10
    upstream_fluid_temperature = T09
    downstream_fluid_temperature = T11
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h10
  []
  [innerwalltemp10_dt]
    type = ADScalarTimeDerivative
    variable = Twi10
  []
  [innerwalltemp11]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi11
    mass_flow_rate = m1
    outer_wall_temperature = Two11
    upstream_wall_temperature = Twi10
    downstream_wall_temperature = Twi12
    fluid_temperature = T11
    upstream_fluid_temperature = T10
    downstream_fluid_temperature = T12
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h11
  []
  [innerwalltemp11_dt]
    type = ADScalarTimeDerivative
    variable = Twi11
  []
  [innerwalltemp12]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi12
    mass_flow_rate = m1
    outer_wall_temperature = Two12
    upstream_wall_temperature = Twi11
    downstream_wall_temperature = Twi13
    fluid_temperature = T12
    upstream_fluid_temperature = T11
    downstream_fluid_temperature = T13
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h12
  []
  [innerwalltemp12_dt]
    type = ADScalarTimeDerivative
    variable = Twi12
  []
  [innerwalltemp13]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi13
    mass_flow_rate = m1
    outer_wall_temperature = Two13
    upstream_wall_temperature = Twi12
    downstream_wall_temperature = Twi14
    fluid_temperature = T13
    upstream_fluid_temperature = T12
    downstream_fluid_temperature = T14
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h13
  []
  [innerwalltemp13_dt]
    type = ADScalarTimeDerivative
    variable = Twi13
  []
  [innerwalltemp14]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi14
    mass_flow_rate = m1
    outer_wall_temperature = Two14
    upstream_wall_temperature = Twi13
    downstream_wall_temperature = Twi15
    fluid_temperature = T14
    upstream_fluid_temperature = T13
    downstream_fluid_temperature = T15
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h14
  []
  [innerwalltemp14_dt]
    type = ADScalarTimeDerivative
    variable = Twi14
  []
  [innerwalltemp15]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi15
    mass_flow_rate = m1
    outer_wall_temperature = Two15
    upstream_wall_temperature = Twi14
    downstream_wall_temperature = Twi16
    fluid_temperature = T15
    upstream_fluid_temperature = T14
    downstream_fluid_temperature = T16
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h15
  []
  [innerwalltemp15_dt]
    type = ADScalarTimeDerivative
    variable = Twi15
  []
  [innerwalltemp16]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi16
    mass_flow_rate = m1
    outer_wall_temperature = Two16
    upstream_wall_temperature = Twi15
    downstream_wall_temperature = Twi17
    fluid_temperature = T16
    upstream_fluid_temperature = T15
    downstream_fluid_temperature = T17
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h16
  []
  [innerwalltemp16_dt]
    type = ADScalarTimeDerivative
    variable = Twi16
  []
  [innerwalltemp17]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi17
    mass_flow_rate = m1
    outer_wall_temperature = Two17
    upstream_wall_temperature = Twi16
    downstream_wall_temperature = Twi18
    fluid_temperature = T17
    upstream_fluid_temperature = T16
    downstream_fluid_temperature = T18
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h17
  []
  [innerwalltemp17_dt]
    type = ADScalarTimeDerivative
    variable = Twi17
  []
  [innerwalltemp18]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi18
    mass_flow_rate = m1
    outer_wall_temperature = Two18
    upstream_wall_temperature = Twi17
    downstream_wall_temperature = Twi19
    fluid_temperature = T18
    upstream_fluid_temperature = T17
    downstream_fluid_temperature = T19
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h18
  []
  [innerwalltemp18_dt]
    type = ADScalarTimeDerivative
    variable = Twi18
  []
  [innerwalltemp19]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi19
    mass_flow_rate = m1
    outer_wall_temperature = Two19
    upstream_wall_temperature = Twi18
    downstream_wall_temperature = Twi20
    fluid_temperature = T19
    upstream_fluid_temperature = T18
    downstream_fluid_temperature = T20
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h19
  []
  [innerwalltemp19_dt]
    type = ADScalarTimeDerivative
    variable = Twi19
  []
  [innerwalltemp20]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi20
    mass_flow_rate = m1
    outer_wall_temperature = Two20
    upstream_wall_temperature = Twi19
    downstream_wall_temperature = Twi21
    fluid_temperature = T20
    upstream_fluid_temperature = T19
    downstream_fluid_temperature = T21
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h20
  []
  [innerwalltemp20_dt]
    type = ADScalarTimeDerivative
    variable = Twi20
  []
  [innerwalltemp21]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi21
    mass_flow_rate = m1
    outer_wall_temperature = Two21
    upstream_wall_temperature = Twi20
    downstream_wall_temperature = Twi22
    fluid_temperature = T21
    upstream_fluid_temperature = T20
    downstream_fluid_temperature = T22
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h21
  []
  [innerwalltemp21_dt]
    type = ADScalarTimeDerivative
    variable = Twi21
  []
  [innerwalltemp22]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi22
    mass_flow_rate = m1
    outer_wall_temperature = Two22
    upstream_wall_temperature = Twi21
    downstream_wall_temperature = Twi23
    fluid_temperature = T22
    upstream_fluid_temperature = T21
    downstream_fluid_temperature = T23
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h22
  []
  [innerwalltemp22_dt]
    type = ADScalarTimeDerivative
    variable = Twi22
  []
  [innerwalltemp23]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi23
    mass_flow_rate = m1
    outer_wall_temperature = Two23
    upstream_wall_temperature = Twi22
    downstream_wall_temperature = Twi24
    fluid_temperature = T23
    upstream_fluid_temperature = T22
    downstream_fluid_temperature = T24
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h23
  []
  [innerwalltemp23_dt]
    type = ADScalarTimeDerivative
    variable = Twi23
  []
  [innerwalltemp24]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi24
    mass_flow_rate = m1
    outer_wall_temperature = Two24
    upstream_wall_temperature = Twi23
    downstream_wall_temperature = Twi25
    fluid_temperature = T24
    upstream_fluid_temperature = T23
    downstream_fluid_temperature = T25
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h24
  []
  [innerwalltemp24_dt]
    type = ADScalarTimeDerivative
    variable = Twi24
  []
  [innerwalltemp25]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi25
    mass_flow_rate = m1
    outer_wall_temperature = Two25
    upstream_wall_temperature = Twi24
    downstream_wall_temperature = Twi26
    fluid_temperature = T25
    upstream_fluid_temperature = T24
    downstream_fluid_temperature = T26
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h25
  []
  [innerwalltemp25_dt]
    type = ADScalarTimeDerivative
    variable = Twi25
  []
  [innerwalltemp26]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi26
    mass_flow_rate = m1
    outer_wall_temperature = Two26
    upstream_wall_temperature = Twi25
    downstream_wall_temperature = Twi27
    fluid_temperature = T26
    upstream_fluid_temperature = T25
    downstream_fluid_temperature = T27
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h26
  []
  [innerwalltemp26_dt]
    type = ADScalarTimeDerivative
    variable = Twi26
  []
  [innerwalltemp27]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi27
    mass_flow_rate = m1
    outer_wall_temperature = Two27
    upstream_wall_temperature = Twi26
    downstream_wall_temperature = Twi28
    fluid_temperature = T27
    upstream_fluid_temperature = T26
    downstream_fluid_temperature = T28
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h27
  []
  [innerwalltemp27_dt]
    type = ADScalarTimeDerivative
    variable = Twi27
  []
  [innerwalltemp28]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi28
    mass_flow_rate = m1
    outer_wall_temperature = Two28
    upstream_wall_temperature = Twi27
    downstream_wall_temperature = Twi29
    fluid_temperature = T28
    upstream_fluid_temperature = T27
    downstream_fluid_temperature = T29
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h28
  []
  [innerwalltemp28_dt]
    type = ADScalarTimeDerivative
    variable = Twi28
  []
  [innerwalltemp29]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi29
    mass_flow_rate = m1
    outer_wall_temperature = Two29
    upstream_wall_temperature = Twi28
    downstream_wall_temperature = Twi30
    fluid_temperature = T29
    upstream_fluid_temperature = T28
    downstream_fluid_temperature = T30
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h29
  []
  [innerwalltemp29_dt]
    type = ADScalarTimeDerivative
    variable = Twi29
  []
  [innerwalltemp30]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi30
    mass_flow_rate = m1
    outer_wall_temperature = Two30
    upstream_wall_temperature = Twi29
    downstream_wall_temperature = Twi31
    fluid_temperature = T30
    upstream_fluid_temperature = T29
    downstream_fluid_temperature = T31
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h30
  []
  [innerwalltemp30_dt]
    type = ADScalarTimeDerivative
    variable = Twi30
  []
  [innerwalltemp31]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi31
    mass_flow_rate = m1
    outer_wall_temperature = Two31
    upstream_wall_temperature = Twi30
    downstream_wall_temperature = Twi32
    fluid_temperature = T31
    upstream_fluid_temperature = T30
    downstream_fluid_temperature = T32
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h31
  []
  [innerwalltemp31_dt]
    type = ADScalarTimeDerivative
    variable = Twi31
  []
  [innerwalltemp32]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi32
    mass_flow_rate = m1
    outer_wall_temperature = Two32
    upstream_wall_temperature = Twi31
    downstream_wall_temperature = Twi33
    fluid_temperature = T32
    upstream_fluid_temperature = T31
    downstream_fluid_temperature = T33
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h32
  []
  [innerwalltemp32_dt]
    type = ADScalarTimeDerivative
    variable = Twi32
  []
  [innerwalltemp33]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi33
    mass_flow_rate = m1
    outer_wall_temperature = Two33
    upstream_wall_temperature = Twi32
    downstream_wall_temperature = Twi34
    fluid_temperature = T33
    upstream_fluid_temperature = T32
    downstream_fluid_temperature = T34
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h33
  []
  [innerwalltemp33_dt]
    type = ADScalarTimeDerivative
    variable = Twi33
  []
  [innerwalltemp34]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi34
    mass_flow_rate = m1
    outer_wall_temperature = Two34
    upstream_wall_temperature = Twi33
    downstream_wall_temperature = Twi35
    fluid_temperature = T34
    upstream_fluid_temperature = T33
    downstream_fluid_temperature = T35
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h34
  []
  [innerwalltemp34_dt]
    type = ADScalarTimeDerivative
    variable = Twi34
  []
  [innerwalltemp35]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi35
    mass_flow_rate = m1
    outer_wall_temperature = Two35
    upstream_wall_temperature = Twi34
    downstream_wall_temperature = Twi36
    fluid_temperature = T35
    upstream_fluid_temperature = T34
    downstream_fluid_temperature = T36
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h35
  []
  [innerwalltemp35_dt]
    type = ADScalarTimeDerivative
    variable = Twi35
  []
  [innerwalltemp36]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi36
    mass_flow_rate = m1
    outer_wall_temperature = Two36
    upstream_wall_temperature = Twi35
    downstream_wall_temperature = Twi37
    fluid_temperature = T36
    upstream_fluid_temperature = T35
    downstream_fluid_temperature = T37
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h36
  []
  [innerwalltemp36_dt]
    type = ADScalarTimeDerivative
    variable = Twi36
  []
  [innerwalltemp37]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi37
    mass_flow_rate = m1
    outer_wall_temperature = Two37
    upstream_wall_temperature = Twi36
    downstream_wall_temperature = Twi38
    fluid_temperature = T37
    upstream_fluid_temperature = T36
    downstream_fluid_temperature = T38
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h37
  []
  [innerwalltemp37_dt]
    type = ADScalarTimeDerivative
    variable = Twi37
  []
  [innerwalltemp38]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi38
    mass_flow_rate = m1
    outer_wall_temperature = Two38
    upstream_wall_temperature = Twi37
    downstream_wall_temperature = Twi39
    fluid_temperature = T38
    upstream_fluid_temperature = T37
    downstream_fluid_temperature = T39
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h38
  []
  [innerwalltemp38_dt]
    type = ADScalarTimeDerivative
    variable = Twi38
  []
  [innerwalltemp39]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi39
    mass_flow_rate = m1
    outer_wall_temperature = Two39
    upstream_wall_temperature = Twi38
    downstream_wall_temperature = Twi40
    fluid_temperature = T39
    upstream_fluid_temperature = T38
    downstream_fluid_temperature = T40
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h39
  []
  [innerwalltemp39_dt]
    type = ADScalarTimeDerivative
    variable = Twi39
  []
  [innerwalltemp40]
    type = ADPipeInnerWallTemperatureScalarKernel
    variable = Twi40
    mass_flow_rate = m1
    outer_wall_temperature = Two40
    upstream_wall_temperature = Twi39
    downstream_wall_temperature = Twi01
    fluid_temperature = T40
    upstream_fluid_temperature = T39
    downstream_fluid_temperature = T01
    solid_properties = APMT
    wetted_perimeter = ${wetted_perimeter}
    area = ${inner_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${inner_wall_area}
    downstream_area = ${inner_wall_area}
    heat_transfer_coefficient = h40
  []
  [innerwalltemp40_dt]
    type = ADScalarTimeDerivative
    variable = Twi40
  []
  [outerwalltemp1]
    type = ADPipeOuterWallAmbientTemperatureScalarKernel
    variable = Two01
    inner_wall_temperature = Twi01
    upstream_wall_temperature = Two40
    downstream_wall_temperature = Two02
    solid_properties = APMT
    T_ambient = 293.15
    htc_ambient = 13.5
    ambient_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp1_dt]
    type = ADScalarTimeDerivative
    variable = Two01
  []
  [outerwalltemp2]
    type = ADPipeOuterWallAmbientTemperatureScalarKernel
    variable = Two02
    inner_wall_temperature = Twi02
    upstream_wall_temperature = Two01
    downstream_wall_temperature = Two03
    solid_properties = APMT
    T_ambient = 293.15
    htc_ambient = 13.5
    ambient_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp2_dt]
    type = ADScalarTimeDerivative
    variable = Two02
  []
  [outerwalltemp3]
    type = ADPipeOuterWallAmbientTemperatureScalarKernel
    variable = Two03
    inner_wall_temperature = Twi03
    upstream_wall_temperature = Two02
    downstream_wall_temperature = Two04
    solid_properties = APMT
    T_ambient = 293.15
    htc_ambient = 13.5
    ambient_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp3_dt]
    type = ADScalarTimeDerivative
    variable = Two03
  []
  [outerwalltemp4]
    type = ADPipeOuterWallAmbientTemperatureScalarKernel
    variable = Two04
    inner_wall_temperature = Twi04
    upstream_wall_temperature = Two03
    downstream_wall_temperature = Two05
    solid_properties = APMT
    T_ambient = 293.15
    htc_ambient = 13.5
    ambient_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp4_dt]
    type = ADScalarTimeDerivative
    variable = Two04
  []
  [outerwalltemp5]
    type = ADPipeOuterWallAmbientTemperatureScalarKernel
    variable = Two05
    inner_wall_temperature = Twi05
    upstream_wall_temperature = Two04
    downstream_wall_temperature = Two06
    solid_properties = APMT
    T_ambient = 293.15
    htc_ambient = 13.5
    ambient_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp5_dt]
    type = ADScalarTimeDerivative
    variable = Two05
  []
  [outerwalltemp6]
    type = ADPipeOuterWallAmbientTemperatureScalarKernel
    variable = Two06
    inner_wall_temperature = Twi06
    upstream_wall_temperature = Two05
    downstream_wall_temperature = Two07
    solid_properties = APMT
    T_ambient = 293.15
    htc_ambient = 13.5
    ambient_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp6_dt]
    type = ADScalarTimeDerivative
    variable = Two06
  []
  [outerwalltemp7]
    type = ADPipeOuterWallAmbientTemperatureScalarKernel
    variable = Two07
    inner_wall_temperature = Twi07
    upstream_wall_temperature = Two06
    downstream_wall_temperature = Two08
    solid_properties = APMT
    T_ambient = 293.15
    htc_ambient = 13.5
    ambient_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp7_dt]
    type = ADScalarTimeDerivative
    variable = Two07
  []
  [outerwalltemp8]
    type = ADPipeOuterWallAmbientTemperatureScalarKernel
    variable = Two08
    inner_wall_temperature = Twi08
    upstream_wall_temperature = Two07
    downstream_wall_temperature = Two09
    solid_properties = APMT
    T_ambient = 293.15
    htc_ambient = 13.5
    ambient_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp8_dt]
    type = ADScalarTimeDerivative
    variable = Two08
  []
  [outerwalltemp9]
    type = ADPipeOuterWallAmbientTemperatureScalarKernel
    variable = Two09
    inner_wall_temperature = Twi09
    upstream_wall_temperature = Two08
    downstream_wall_temperature = Two10
    solid_properties = APMT
    T_ambient = 293.15
    htc_ambient = 13.5
    ambient_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp9_dt]
    type = ADScalarTimeDerivative
    variable = Two09
  []
  [outerwalltemp10]
    type = ADPipeOuterWallAmbientTemperatureScalarKernel
    variable = Two10
    inner_wall_temperature = Twi10
    upstream_wall_temperature = Two09
    downstream_wall_temperature = Two11
    solid_properties = APMT
    T_ambient = 293.15
    htc_ambient = 13.5
    ambient_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp10_dt]
    type = ADScalarTimeDerivative
    variable = Two10
  []
  [outerwalltemp11]
    type = ADPipeOuterWallAmbientTemperatureScalarKernel
    variable = Two11
    inner_wall_temperature = Twi11
    upstream_wall_temperature = Two10
    downstream_wall_temperature = Two12
    solid_properties = APMT
    T_ambient = 293.15
    htc_ambient = 13.5
    ambient_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp11_dt]
    type = ADScalarTimeDerivative
    variable = Two11
  []
  [outerwalltemp12]
    type = ADPipeOuterWallAmbientTemperatureScalarKernel
    variable = Two12
    inner_wall_temperature = Twi12
    upstream_wall_temperature = Two11
    downstream_wall_temperature = Two13
    solid_properties = APMT
    T_ambient = 293.15
    htc_ambient = 13.5
    ambient_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp12_dt]
    type = ADScalarTimeDerivative
    variable = Two12
  []
  [outerwalltemp13]
    type = ADPipeOuterWallAmbientTemperatureScalarKernel
    variable = Two13
    inner_wall_temperature = Twi13
    upstream_wall_temperature = Two12
    downstream_wall_temperature = Two14
    solid_properties = APMT
    T_ambient = 293.15
    htc_ambient = 13.5
    ambient_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp13_dt]
    type = ADScalarTimeDerivative
    variable = Two13
  []
  [outerwalltemp14]
    type = ADPipeOuterWallAmbientTemperatureScalarKernel
    variable = Two14
    inner_wall_temperature = Twi14
    upstream_wall_temperature = Two13
    downstream_wall_temperature = Two15
    solid_properties = APMT
    T_ambient = 293.15
    htc_ambient = 13.5
    ambient_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp14_dt]
    type = ADScalarTimeDerivative
    variable = Two14
  []
  [outerwalltemp15]
    type = ADPipeOuterWallAmbientTemperatureScalarKernel
    variable = Two15
    inner_wall_temperature = Twi15
    upstream_wall_temperature = Two14
    downstream_wall_temperature = Two16
    solid_properties = APMT
    T_ambient = 293.15
    htc_ambient = 13.5
    ambient_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp15_dt]
    type = ADScalarTimeDerivative
    variable = Two15
  []
  [outerwalltemp16]
    type = ADPipeOuterWallAmbientTemperatureScalarKernel
    variable = Two16
    inner_wall_temperature = Twi16
    upstream_wall_temperature = Two15
    downstream_wall_temperature = Two17
    solid_properties = APMT
    T_ambient = 293.15
    htc_ambient = 13.5
    ambient_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp16_dt]
    type = ADScalarTimeDerivative
    variable = Two16
  []
  [outerwalltemp17]
    type = ADPipeOuterWallAmbientTemperatureScalarKernel
    variable = Two17
    inner_wall_temperature = Twi17
    upstream_wall_temperature = Two16
    downstream_wall_temperature = Two18
    solid_properties = APMT
    T_ambient = 293.15
    htc_ambient = 13.5
    ambient_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp17_dt]
    type = ADScalarTimeDerivative
    variable = Two17
  []
  [outerwalltemp18]
    type = ADPipeOuterWallAmbientTemperatureScalarKernel
    variable = Two18
    inner_wall_temperature = Twi18
    upstream_wall_temperature = Two17
    downstream_wall_temperature = Two19
    solid_properties = APMT
    T_ambient = 293.15
    htc_ambient = 13.5
    ambient_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp18_dt]
    type = ADScalarTimeDerivative
    variable = Two18
  []
  [outerwalltemp19]
    type = ADPipeOuterWallAmbientTemperatureScalarKernel
    variable = Two19
    inner_wall_temperature = Twi19
    upstream_wall_temperature = Two18
    downstream_wall_temperature = Two20
    solid_properties = APMT
    T_ambient = 293.15
    htc_ambient = 13.5
    ambient_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp19_dt]
    type = ADScalarTimeDerivative
    variable = Two19
  []
  [outerwalltemp20]
    type = ADPipeOuterWallAmbientTemperatureScalarKernel
    variable = Two20
    inner_wall_temperature = Twi20
    upstream_wall_temperature = Two19
    downstream_wall_temperature = Two21
    solid_properties = APMT
    T_ambient = 293.15
    htc_ambient = 13.5
    ambient_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp20_dt]
    type = ADScalarTimeDerivative
    variable = Two20
  []
  [outerwalltemp21]
    type = ADPipeOuterWallHeatFluxScalarKernel
    variable = Two21
    inner_wall_temperature = Twi21
    upstream_wall_temperature = Two20
    downstream_wall_temperature = Two22
    solid_properties = APMT
    heat_flux = ${fparse Q_horiz/sqrt(Lx^2+(m_horiz*Lx)^2)/outer_perimeter}
    heated_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp21_dt]
    type = ADScalarTimeDerivative
    variable = Two21
  []
  [outerwalltemp22]
    type = ADPipeOuterWallHeatFluxScalarKernel
    variable = Two22
    inner_wall_temperature = Twi22
    upstream_wall_temperature = Two21
    downstream_wall_temperature = Two23
    solid_properties = APMT
    heat_flux = ${fparse Q_horiz/sqrt(Lx^2+(m_horiz*Lx)^2)/outer_perimeter}
    heated_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp22_dt]
    type = ADScalarTimeDerivative
    variable = Two22
  []
  [outerwalltemp23]
    type = ADPipeOuterWallHeatFluxScalarKernel
    variable = Two23
    inner_wall_temperature = Twi23
    upstream_wall_temperature = Two22
    downstream_wall_temperature = Two24
    solid_properties = APMT
    heat_flux = ${fparse Q_horiz/sqrt(Lx^2+(m_horiz*Lx)^2)/outer_perimeter}
    heated_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp23_dt]
    type = ADScalarTimeDerivative
    variable = Two23
  []
  [outerwalltemp24]
    type = ADPipeOuterWallHeatFluxScalarKernel
    variable = Two24
    inner_wall_temperature = Twi24
    upstream_wall_temperature = Two23
    downstream_wall_temperature = Two25
    solid_properties = APMT
    heat_flux = ${fparse Q_horiz/sqrt(Lx^2+(m_horiz*Lx)^2)/outer_perimeter}
    heated_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp24_dt]
    type = ADScalarTimeDerivative
    variable = Two24
  []
  [outerwalltemp25]
    type = ADPipeOuterWallHeatFluxScalarKernel
    variable = Two25
    inner_wall_temperature = Twi25
    upstream_wall_temperature = Two24
    downstream_wall_temperature = Two26
    solid_properties = APMT
    heat_flux = ${fparse Q_horiz/sqrt(Lx^2+(m_horiz*Lx)^2)/outer_perimeter}
    heated_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp25_dt]
    type = ADScalarTimeDerivative
    variable = Two25
  []
  [outerwalltemp26]
    type = ADPipeOuterWallHeatFluxScalarKernel
    variable = Two26
    inner_wall_temperature = Twi26
    upstream_wall_temperature = Two25
    downstream_wall_temperature = Two27
    solid_properties = APMT
    heat_flux = ${fparse Q_horiz/sqrt(Lx^2+(m_horiz*Lx)^2)/outer_perimeter}
    heated_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp26_dt]
    type = ADScalarTimeDerivative
    variable = Two26
  []
  [outerwalltemp27]
    type = ADPipeOuterWallHeatFluxScalarKernel
    variable = Two27
    inner_wall_temperature = Twi27
    upstream_wall_temperature = Two26
    downstream_wall_temperature = Two28
    solid_properties = APMT
    heat_flux = ${fparse Q_horiz/sqrt(Lx^2+(m_horiz*Lx)^2)/outer_perimeter}
    heated_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp27_dt]
    type = ADScalarTimeDerivative
    variable = Two27
  []
  [outerwalltemp28]
    type = ADPipeOuterWallHeatFluxScalarKernel
    variable = Two28
    inner_wall_temperature = Twi28
    upstream_wall_temperature = Two27
    downstream_wall_temperature = Two29
    solid_properties = APMT
    heat_flux = ${fparse Q_horiz/sqrt(Lx^2+(m_horiz*Lx)^2)/outer_perimeter}
    heated_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp28_dt]
    type = ADScalarTimeDerivative
    variable = Two28
  []
  [outerwalltemp29]
    type = ADPipeOuterWallHeatFluxScalarKernel
    variable = Two29
    inner_wall_temperature = Twi29
    upstream_wall_temperature = Two28
    downstream_wall_temperature = Two30
    solid_properties = APMT
    heat_flux = ${fparse Q_horiz/sqrt(Lx^2+(m_horiz*Lx)^2)/outer_perimeter}
    heated_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp29_dt]
    type = ADScalarTimeDerivative
    variable = Two29
  []
  [outerwalltemp30]
    type = ADPipeOuterWallHeatFluxScalarKernel
    variable = Two30
    inner_wall_temperature = Twi30
    upstream_wall_temperature = Two29
    downstream_wall_temperature = Two31
    solid_properties = APMT
    heat_flux = ${fparse Q_horiz/sqrt(Lx^2+(m_horiz*Lx)^2)/outer_perimeter}
    heated_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp30_dt]
    type = ADScalarTimeDerivative
    variable = Two30
  []
  [outerwalltemp31]
    type = ADPipeOuterWallHeatFluxScalarKernel
    variable = Two31
    inner_wall_temperature = Twi31
    upstream_wall_temperature = Two30
    downstream_wall_temperature = Two32
    solid_properties = APMT
    heat_flux = ${fparse Q_vert/Ly/outer_perimeter}
    heated_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp31_dt]
    type = ADScalarTimeDerivative
    variable = Two31
  []
  [outerwalltemp32]
    type = ADPipeOuterWallHeatFluxScalarKernel
    variable = Two32
    inner_wall_temperature = Twi32
    upstream_wall_temperature = Two31
    downstream_wall_temperature = Two33
    solid_properties = APMT
    heat_flux = ${fparse Q_vert/Ly/outer_perimeter}
    heated_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp32_dt]
    type = ADScalarTimeDerivative
    variable = Two32
  []
  [outerwalltemp33]
    type = ADPipeOuterWallHeatFluxScalarKernel
    variable = Two33
    inner_wall_temperature = Twi33
    upstream_wall_temperature = Two32
    downstream_wall_temperature = Two34
    solid_properties = APMT
    heat_flux = ${fparse Q_vert/Ly/outer_perimeter}
    heated_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp33_dt]
    type = ADScalarTimeDerivative
    variable = Two33
  []
  [outerwalltemp34]
    type = ADPipeOuterWallHeatFluxScalarKernel
    variable = Two34
    inner_wall_temperature = Twi34
    upstream_wall_temperature = Two33
    downstream_wall_temperature = Two35
    solid_properties = APMT
    heat_flux = ${fparse Q_vert/Ly/outer_perimeter}
    heated_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp34_dt]
    type = ADScalarTimeDerivative
    variable = Two34
  []
  [outerwalltemp35]
    type = ADPipeOuterWallHeatFluxScalarKernel
    variable = Two35
    inner_wall_temperature = Twi35
    upstream_wall_temperature = Two34
    downstream_wall_temperature = Two36
    solid_properties = APMT
    heat_flux = ${fparse Q_vert/Ly/outer_perimeter}
    heated_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp35_dt]
    type = ADScalarTimeDerivative
    variable = Two35
  []
  [outerwalltemp36]
    type = ADPipeOuterWallHeatFluxScalarKernel
    variable = Two36
    inner_wall_temperature = Twi36
    upstream_wall_temperature = Two35
    downstream_wall_temperature = Two37
    solid_properties = APMT
    heat_flux = ${fparse Q_vert/Ly/outer_perimeter}
    heated_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp36_dt]
    type = ADScalarTimeDerivative
    variable = Two36
  []
  [outerwalltemp37]
    type = ADPipeOuterWallHeatFluxScalarKernel
    variable = Two37
    inner_wall_temperature = Twi37
    upstream_wall_temperature = Two36
    downstream_wall_temperature = Two38
    solid_properties = APMT
    heat_flux = ${fparse Q_vert/Ly/outer_perimeter}
    heated_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp37_dt]
    type = ADScalarTimeDerivative
    variable = Two37
  []
  [outerwalltemp38]
    type = ADPipeOuterWallHeatFluxScalarKernel
    variable = Two38
    inner_wall_temperature = Twi38
    upstream_wall_temperature = Two37
    downstream_wall_temperature = Two39
    solid_properties = APMT
    heat_flux = ${fparse Q_vert/Ly/outer_perimeter}
    heated_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp38_dt]
    type = ADScalarTimeDerivative
    variable = Two38
  []
  [outerwalltemp39]
    type = ADPipeOuterWallHeatFluxScalarKernel
    variable = Two39
    inner_wall_temperature = Twi39
    upstream_wall_temperature = Two38
    downstream_wall_temperature = Two40
    solid_properties = APMT
    heat_flux = ${fparse Q_vert/Ly/outer_perimeter}
    heated_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse Ly/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp39_dt]
    type = ADScalarTimeDerivative
    variable = Two39
  []
  [outerwalltemp40]
    type = ADPipeOuterWallHeatFluxScalarKernel
    variable = Two40
    inner_wall_temperature = Twi40
    upstream_wall_temperature = Two39
    downstream_wall_temperature = Two01
    solid_properties = APMT
    heat_flux = ${fparse Q_vert/Ly/outer_perimeter}
    heated_perimeter = ${outer_perimeter}
    area = ${outer_wall_area}
    interface_perimeter = ${midthickness_perimeter}
    wall_thickness = ${wall_thickness}
    length = ${fparse Ly/10}
    upstream_spacing = ${fparse Ly/10}
    downstream_spacing = ${fparse sqrt(Lx^2+(m_horiz*Lx)^2)/10}
    upstream_area = ${outer_wall_area}
    downstream_area = ${outer_wall_area}
  []
  [outerwalltemp40_dt]
    type = ADScalarTimeDerivative
    variable = Two40
  []
[]

[FunctorMaterials]
  [h1]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T01
    T_fluid_inlet = T40
    T_fluid_outlet = T02
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h2]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T02
    T_fluid_inlet = T01
    T_fluid_outlet = T03
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h3]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T03
    T_fluid_inlet = T02
    T_fluid_outlet = T04
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h4]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T04
    T_fluid_inlet = T03
    T_fluid_outlet = T05
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h5]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T05
    T_fluid_inlet = T04
    T_fluid_outlet = T06
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h6]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T06
    T_fluid_inlet = T05
    T_fluid_outlet = T07
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h7]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T07
    T_fluid_inlet = T06
    T_fluid_outlet = T08
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h8]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T08
    T_fluid_inlet = T07
    T_fluid_outlet = T09
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h9]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T09
    T_fluid_inlet = T08
    T_fluid_outlet = T10
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h10]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T10
    T_fluid_inlet = T09
    T_fluid_outlet = T11
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h11]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T11
    T_fluid_inlet = T10
    T_fluid_outlet = T12
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h12]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T12
    T_fluid_inlet = T11
    T_fluid_outlet = T13
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h13]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T13
    T_fluid_inlet = T12
    T_fluid_outlet = T14
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h14]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T14
    T_fluid_inlet = T13
    T_fluid_outlet = T15
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h15]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T15
    T_fluid_inlet = T14
    T_fluid_outlet = T16
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h16]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T16
    T_fluid_inlet = T15
    T_fluid_outlet = T17
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h17]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T17
    T_fluid_inlet = T16
    T_fluid_outlet = T18
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h18]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T18
    T_fluid_inlet = T17
    T_fluid_outlet = T19
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h19]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T19
    T_fluid_inlet = T18
    T_fluid_outlet = T20
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h20]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T20
    T_fluid_inlet = T19
    T_fluid_outlet = T21
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h21]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T21
    T_fluid_inlet = T20
    T_fluid_outlet = T22
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h22]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T22
    T_fluid_inlet = T21
    T_fluid_outlet = T23
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h23]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T23
    T_fluid_inlet = T22
    T_fluid_outlet = T24
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h24]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T24
    T_fluid_inlet = T23
    T_fluid_outlet = T25
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h25]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T25
    T_fluid_inlet = T24
    T_fluid_outlet = T26
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h26]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T26
    T_fluid_inlet = T25
    T_fluid_outlet = T27
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h27]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T27
    T_fluid_inlet = T26
    T_fluid_outlet = T28
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h28]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T28
    T_fluid_inlet = T27
    T_fluid_outlet = T29
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h29]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T29
    T_fluid_inlet = T28
    T_fluid_outlet = T30
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h30]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T30
    T_fluid_inlet = T29
    T_fluid_outlet = T31
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h31]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T31
    T_fluid_inlet = T30
    T_fluid_outlet = T32
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h32]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T32
    T_fluid_inlet = T31
    T_fluid_outlet = T33
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h33]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T33
    T_fluid_inlet = T32
    T_fluid_outlet = T34
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h34]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T34
    T_fluid_inlet = T33
    T_fluid_outlet = T35
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h35]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T35
    T_fluid_inlet = T34
    T_fluid_outlet = T36
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h36]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T36
    T_fluid_inlet = T35
    T_fluid_outlet = T37
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h37]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T37
    T_fluid_inlet = T36
    T_fluid_outlet = T38
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h38]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T38
    T_fluid_inlet = T37
    T_fluid_outlet = T39
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h39]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T39
    T_fluid_inlet = T38
    T_fluid_outlet = T40
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
  [h40]
    type = ADDittusBoelterHTCFunctorMaterial
    mass_flow_rate = m1
    fluid_properties = PbLi
    T_fluid = T40
    T_fluid_inlet = T39
    T_fluid_outlet = T01
    reference_pressure = ${reference_pressure}
    flow_area = ${flow_area}
    wetted_perimeter = ${wetted_perimeter}
  []
[]

[Postprocessors]
  [mdot]
    type = ScalarVariable
    variable = m1
    execute_on = 'INITIAL TIMESTEP_END FINAL'
  []
  [Temp20]
    type = ScalarVariable
    variable = T20
    execute_on = 'INITIAL TIMESTEP_END FINAL'
  []
  [Temp40]
    type = ScalarVariable
    variable = T40
    execute_on = 'INITIAL LINEAR TIMESTEP_END FINAL'
  []
  [AveTemp]
    type = ParsedPostprocessor
    expression = '(Temp20 + Temp40)/2'
    pp_names = 'Temp20 Temp40'
    execute_on = 'INITIAL TIMESTEP_END FINAL'
  []
  [rhoave]
    type = FunctionValuePostprocessor
    function = rhof
    time = AveTemp
    execute_on = 'INITIAL TIMESTEP_END FINAL'
  []
  [flow_velocity]
    type = ParsedPostprocessor
    expression = 'abs(mdot)/rhoave/${flow_area}'
    pp_names = 'mdot rhoave'
    execute_on = 'INITIAL TIMESTEP_END FINAL'
  []
  [RELAP_comp_Tlow]
    type = ParsedPostprocessor
    expression = '(Temp20 - 708.1)/708.1'
    pp_names = 'Temp20'
    execute_on = 'INITIAL TIMESTEP_END FINAL'
  []
  [RELAP_comp_Thigh]
    type = ParsedPostprocessor
    expression = '(Temp40 - 827.7)/827.7'
    pp_names = 'Temp40'
    execute_on = 'INITIAL TIMESTEP_END FINAL'
  []
  [RELAP_comp_velocity]
    type = ParsedPostprocessor
    expression = '(flow_velocity - 0.0065)/0.0065'
    pp_names = 'flow_velocity'
    execute_on = 'INITIAL TIMESTEP_END FINAL'
  []
  [experiment_comp_Tlow]
    type = ParsedPostprocessor
    expression = '(Temp20 - 707.5)/707.5'
    pp_names = 'Temp20'
    execute_on = 'INITIAL TIMESTEP_END FINAL'
  []
  [experiment_comp_Thigh]
    type = ParsedPostprocessor
    expression = '(Temp40 - 823.2)/823.2'
    pp_names = 'Temp40'
    execute_on = 'INITIAL TIMESTEP_END FINAL'
  []
  [experiment_comp_velocity]
    type = ParsedPostprocessor
    expression = '(flow_velocity - 0.0067)/0.0067'
    pp_names = 'flow_velocity'
    execute_on = 'INITIAL TIMESTEP_END FINAL'
  []
[]

[Executioner]
  type = Transient
  solve_type = 'PJFNK'
  petsc_options_iname = '-pc_type'
  petsc_options_value = ' lu     '
  nl_rel_tol = 1e-10
  nl_abs_tol = 1e-10
  nl_max_its = 25
  start_time = 0
  end_time = 21600
  dtmax = 300
  [TimeSteppers]
    [adaptive]
      type = IterationAdaptiveDT
      dt = 1
      growth_factor = 1.2
      cutback_factor = 0.8
    []
  []
[]

[Outputs]
  perf_graph = true
  [out]
    type = CSV
    execute_on = 'TIMESTEP_END'
  []
[]