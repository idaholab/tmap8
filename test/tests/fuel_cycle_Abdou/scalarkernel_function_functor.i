!include fuel_cycle_abdou_generic.i

[Functions]
  [temp]
    type = ParsedFunction
    expression = 'p'
    symbol_names = 'p'
    symbol_values = 'plasma_FW_flux'
  []
[]

ScalarKernels/I3/other_sources:='temp'
