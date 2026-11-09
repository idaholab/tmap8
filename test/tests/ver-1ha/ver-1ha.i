# Verification Problem #1ha from TMAP4/TMAP7 V&V document
# A Convective Gas Outflow Problem with Three Enclosures

# Modeling parameters
simulation_time = '${units 40 s}'
P1 = '${units 1 Pa}'
R = '${units 8.31446261815324 J/K/mol}' # from TMAP8PhysicalConstants.h
T = '${units 303 K}'
N_a = '${units 6.02214076e23 at/mol}' # from TMAP8PhysicalConstants.h
Q = '${units 0.1 m^3/s }'
V2 = '${units 1 m^3}'
V3 = '${units 1 m^3}'
Q_by_V2 = '${fparse Q / V2}'
Q_by_V3 = '${fparse Q / V3}'

[Mesh]
    type = GeneratedMesh
    dim = 1
[]

[Variables]
    [P2]
    []
    [P3]
    []
[]
[AuxVariables]
    [P1]
        initial_condition = ${P1}
    []
[]

[Kernels]
    # Equation for enclosure P2
    [timeDerivative_P2]
        type = ADTimeDerivative
        variable = P2
    []
    [MatReaction_P2_P1_influx]
        type = ADMatReaction
        variable = P2
        v = 'P1'
        reaction_rate = ${Q_by_V2}
    []
    [MatReaction_P2_P3_outflux]
        type = ADMatReaction
        variable = P2
        reaction_rate = -${Q_by_V2}
    []

    # Equation for enclosure P3
    [timeDerivative_P3]
        type = ADTimeDerivative
        variable = P3
    []
    [MatReaction_P3_P2_influx]
        type = ADMatReaction
        variable = P3
        v = 'P2'
        reaction_rate = ${Q_by_V3}
    []
    [MatReaction_P3_P3_outflux]
        type = ADMatReaction
        variable = P3
        reaction_rate = -${Q_by_V3}
    []
[]

[Materials]
    [C2]
        type = ParsedMaterial
        coupled_variables = 'P2'
        property_name = 'C2'
        expression = 'P2*${N_a}/(${R}*${T})'
    []
    [C3]
        type = ParsedMaterial
        coupled_variables = 'P3'
        property_name = 'C3'
        expression = 'P3*${N_a}/(${R}*${T})'
    []
[]

[Postprocessors]
    [P2_value]
        type = ElementAverageValue
        variable = P2
        execute_on = 'INITIAL TIMESTEP_END'
    []
    [P3_value]
        type = ElementAverageValue
        variable = P3
        execute_on = 'INITIAL TIMESTEP_END'
    []
    [C2_value]
        type = ElementAverageMaterialProperty
        mat_prop = C2
        execute_on = 'INITIAL TIMESTEP_END'
    []
    [C3_value]
        type = ElementAverageMaterialProperty
        mat_prop = C3
        execute_on = 'INITIAL TIMESTEP_END'
    []
[]

[Executioner]
    type = Transient
    scheme = bdf2
    solve_type = 'NEWTON'
    petsc_options_iname = '-pc_type'
    petsc_options_value = 'lu'
    automatic_scaling = true
    end_time = '${simulation_time}'
    dt = 0.1
[]

[Outputs]
    csv = true
[]
