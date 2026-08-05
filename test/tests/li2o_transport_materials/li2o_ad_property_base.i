# Li2O AD Jacobian regression base
# Unit system: temperature in K; property units depend on the selected material type

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
  [li2o_property]
    type = TritiumDiffusivityLi2O
    temperature = temperature
    model = Ohira1989
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
