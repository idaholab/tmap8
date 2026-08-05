# Li2O single-point material property regression base
# Unit system: temperature in K; property units depend on the selected material type

[Mesh]
  type = GeneratedMesh
  dim = 1
  nx = 1
[]

[AuxVariables]
  [temperature]
    family = MONOMIAL
    order = CONSTANT
  []
[]

[AuxKernels]
  [set_temperature]
    type = ConstantAux
    variable = temperature
    value = 650
    execute_on = INITIAL
  []
[]

[Materials]
  [li2o_property]
    type = TritiumDiffusivityLi2O
    temperature = temperature
    model = Ohira1989
    validity_action = ignore
    property_name = property
    ad_property_name = ad_property
  []
[]

[Postprocessors]
  [value]
    type = ElementAverageMaterialProperty
    mat_prop = property
    execute_on = INITIAL
  []
  [ad_value]
    type = ADElementAverageMaterialProperty
    mat_prop = ad_property
    execute_on = INITIAL
  []
[]

[Problem]
  solve = false
[]

[Executioner]
  type = Steady
[]

[Outputs]
  csv = true
  execute_on = INITIAL
[]
