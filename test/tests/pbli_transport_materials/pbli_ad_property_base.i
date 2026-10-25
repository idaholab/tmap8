# PbLi AD Jacobian regression base
# Unit system: temperature in K; property units depend on the selected material type
# (density in kg/m^3, diffusivity in m^2/s, solubility in atoms m^-3 Pa^-1/2)

[Mesh]
  type = GeneratedMesh
  dim = 1
  nx = 1
[]

[Variables]
  [temperature]
    initial_condition = 650
  []
[]

[Materials]
  [pbli_property]
    type = TritiumDiffusivityPbLi
    temperature = temperature
    model = Terai1992
    property_name = property
    ad_property_name = ad_property
  []
[]

[Kernels]
  [ad_consumption]
    type = ADMatReactionFlexible
    variable = temperature
    reaction_rate_name = ad_property
  []
[]

[Executioner]
  type = Steady
  solve_type = NEWTON
[]
