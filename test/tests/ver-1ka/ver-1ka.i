# Verification Problem #1ka from TMAP7 V&V document
# A diffusion on two connected enclosures by a membrane with a volumetric source using Sieverts' law

# Physical Constants
kb = ${units 1.380649e-23 J/K} # Boltzmann constant J/K - from TMAP8PhysicalConstants.h

# Modeling parameters
length = '${units 1 m}'
width = '${units 1 m}'
end_time = ${units 10000 s}
time_step = ${units 500 s}
initial_pressure = ${units 0 Pa} # initial internal pressure
T = ${units 500 K} # Temperature
S = ${units 1e20 1/m^3/s} # Source term
V = ${units 1 m^3} # Volume

[Mesh]
  type = GeneratedMesh
  dim = 2
  nx = 10
  ny = 10
  xmax = '${length}'
  ymax = '${width}'
[]

[Variables]
  [pressure]
    family = SCALAR
    order = FIRST
    initial_condition = '${fparse initial_pressure}'
  []
[]

[ScalarKernels]
  [time]
    type = ODETimeDerivative
    variable = pressure
  []
  [source]
    type = ParsedODEKernel
    variable = pressure
    expression = '${fparse - S/V * kb * T}'
  []
[]

[Executioner]
  type = Transient
  dt = ${time_step}
  end_time = ${end_time}
  scheme = 'bdf2'
[]

[Outputs]
  file_base = 'ver-1ka_out'
  csv = true
  exodus = true
[]
