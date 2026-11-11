# Li2O three-point material property regression base
# Unit system: temperature in K; property units depend on the selected material type

[Mesh]
  [base_mesh]
    type = GeneratedMeshGenerator
    dim = 1
    nx = 3
    xmin = 0
    xmax = 3
  []
  [subdomains]
    type = SubdomainPerElementGenerator
    input = base_mesh
    subdomain_ids = '0 1 2'
  []
[]

[AuxVariables]
  [temperature]
    family = MONOMIAL
    order = CONSTANT
  []
[]

[AuxKernels]
  [temperature_1]
    type = ConstantAux
    variable = temperature
    block = 0
    value = 573
    execute_on = INITIAL
  []
  [temperature_2]
    type = ConstantAux
    variable = temperature
    block = 1
    value = 750
    execute_on = INITIAL
  []
  [temperature_3]
    type = ConstantAux
    variable = temperature
    block = 2
    value = 950
    execute_on = INITIAL
  []
[]

[Materials]
  [li2o_property]
    type = TritiumDiffusivityLi2O
    block = '0 1 2'
    temperature = temperature
    model = Tanifuji1987
    property_name = property
    ad_property_name = ad_property
  []
[]

[Postprocessors]
  [value_1]
    type = ElementAverageMaterialProperty
    block = 0
    mat_prop = property
    execute_on = INITIAL
  []
  [ad_value_1]
    type = ADElementAverageMaterialProperty
    block = 0
    mat_prop = ad_property
    execute_on = INITIAL
  []
  [value_2]
    type = ElementAverageMaterialProperty
    block = 1
    mat_prop = property
    execute_on = INITIAL
  []
  [ad_value_2]
    type = ADElementAverageMaterialProperty
    block = 1
    mat_prop = ad_property
    execute_on = INITIAL
  []
  [value_3]
    type = ElementAverageMaterialProperty
    block = 2
    mat_prop = property
    execute_on = INITIAL
  []
  [ad_value_3]
    type = ADElementAverageMaterialProperty
    block = 2
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
