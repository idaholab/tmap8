# Unit system: SI (s, unitless tritium inventory)
# Minimal input verifying that FuelCycleSystemScalarKernel rejects functors that are not
# defined on the subdomain containing 'evaluation_point'. The mesh has two subdomains and
# 'sink_field' and 'sink_material' are restricted to subdomain 0, so evaluating them at a
# point in subdomain 1 must raise an error.

[Mesh]
  [gen]
    type = GeneratedMeshGenerator
    dim = 1
    nx = 2
  []
  [right]
    type = SubdomainBoundingBoxGenerator
    input = gen
    bottom_left = '0.5 -1 -1'
    top_right = '1 1 1'
    block_id = 1
  []
[]

[Variables]
  [T_01_BZ]
    family = SCALAR
    initial_condition = 1
  []
[]

[AuxVariables]
  [sink_field]
    block = 0
    initial_condition = 1
  []
[]

[FunctorMaterials]
  [sink_functor_material]
    type = GenericFunctorMaterial
    block = 0
    prop_names = 'sink_material'
    prop_values = '1'
  []
[]

[ScalarKernels]
  [I1]
    type = FuelCycleSystemScalarKernel
    variable = 'T_01_BZ'
    other_sinks = 'sink_field'
    evaluation_point = '0.75 0 0'
  []
[]

[Problem]
  material_coverage_check = false
[]

[Executioner]
  type = Transient
  num_steps = 1
[]
