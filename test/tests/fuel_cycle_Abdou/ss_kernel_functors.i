# Unit system: SI (s, unitless tritium inventory)
# This input extends ss_kernel.i to verify that FuelCycleSystemScalarKernel accepts
# different kinds of functors. Each object below evaluates to the same constant as
# the 'device_T_consumption' postprocessor, so selecting any of them through
# 'ScalarKernels/I1/other_sinks' must reproduce the ss_kernel.i solution:
#   sink_function                - Function
#   sink_scalar                  - scalar variable
#   sink_field                   - finite element field variable
#   sink_fv_field                - finite volume field variable
#   sink_material                - functor material property (constant)
#   sink_parsed_material         - functor material property built from postprocessors

!include ss_kernel.i

device_T_consumption = ${fparse 5.3125e-6 / 0.0036 / 0.25}

[Functions]
  [sink_function]
    type = ParsedFunction
    expression = '${device_T_consumption}'
  []
[]

[AuxVariables]
  [sink_scalar]
    family = SCALAR
    initial_condition = ${device_T_consumption}
  []
  [sink_field]
    initial_condition = ${device_T_consumption}
  []
  [sink_fv_field]
    type = MooseVariableFVReal
    initial_condition = ${device_T_consumption}
  []
[]

[FunctorMaterials]
  [sink_functor_material]
    type = GenericFunctorMaterial
    prop_names = 'sink_material'
    prop_values = '${device_T_consumption}'
  []
  [sink_parsed_functor_material]
    type = ParsedFunctorMaterial
    property_name = 'sink_parsed_material'
    functor_names = 'tritium_burn_rate tritium_burn_fraction tritium_fueling_efficiency'
    functor_symbols = 'burn_rate burn_fraction fueling_efficiency'
    expression = 'burn_rate / burn_fraction / fueling_efficiency'
  []
[]

[Outputs]
  hide = 'sink_scalar'
[]
