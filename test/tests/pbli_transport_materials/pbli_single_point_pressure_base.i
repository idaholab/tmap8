# PbLi single-point material property regression base with a pressure field
# Unit system: temperature in K; property units depend on the selected material type
# and pressure in Pa
# (diffusivity in m^2/s, solubility in atoms m^-3 Pa^-1/2), density from
# LeadLithiumFluidProperties in kg/m^3

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
  [pressure]
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
  [set_pressure]
    type = ConstantAux
    variable = pressure
    value = 5000
    execute_on = INITIAL
  []
[]

[FluidProperties]
  [pbli_fp]
    type = LeadLithiumFluidProperties
  []
[]

[Materials]
  [pbli_property]
    type = TritiumDiffusivityPbLi
    temperature = temperature
    pressure = pressure
    model = Terai1992
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
