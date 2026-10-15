# FuelCycleSystemScalarKernel

!syntax description /ScalarKernels/FuelCycleSystemScalarKernel

## Overview

This object implements the time-dependent mass-transport equations for a
single variable given an arbitrary number of coupled inputs/outputs (coupled [ScalarVariables](/syntax/Variables))
and/or sources and sinks. 
This kernel tracks tritium decay. 
All parameters are defined as functors,
which should allow versatility in accepting a variety of input arguments. An example of using this
kernel for a system is available, following the [Abdou fuel cycle](/examples/fuel_cycle_Abdou) model.

Some consideration should be given to the [!param](/ScalarKernels/FuelCycleSystemScalarKernel/is_implicit) parameter. This term allows the user to select whether the solve
should be done with the current or the last accepted value for the system as the beginning parameter. This may allow the system to evolve more slowly which may avoid some issues with respect to divergence of particularly unstable systems.

Rather than using [`ParsedODEKernel`](scalarkernels/ParsedODEKernel.md) and [`ODETimeDerivative`](scalarkernels/ODETimeDerivative.md) kernels, the scalar kernels block can be simplified.

!listing test/tests/fuel_cycle_Abdou/fuel_cycle_abdou_generic.i link=false block=ScalarKernels

If parameters are to be made available to external control objects, there is still a need to define appropriate [`Postprocessors`](/syntax/Postprocessors) to inform the scalar kernels, as these cannot be assumed for the general case. Otherwise (for constant properties) it is fine to set values directly in the scalar kernel definition.

!listing test/tests/fuel_cycle_Abdou/fuel_cycle_abdou_generic.i link=false block=Postprocessors

## Supported functor types

Because the system is zero-dimensional, all functor parameters are evaluated at a single spatial location set by [!param](/ScalarKernels/FuelCycleSystemScalarKernel/evaluation_point), which defaults to the origin. The functors may be any of the following:

- [Postprocessors](/syntax/Postprocessors) and constant values,
- [Functions](/syntax/Functions), which are evaluated at [!param](/ScalarKernels/FuelCycleSystemScalarKernel/evaluation_point) and at the time matching the selected solution state,
- scalar variables,
- field variables (finite element or finite volume) and [FunctorMaterials](/syntax/FunctorMaterials). These require [!param](/ScalarKernels/FuelCycleSystemScalarKernel/evaluation_point) to lie inside the mesh, in a subdomain where the functor is defined.

The kernel checks these requirements at initial setup. If [!param](/ScalarKernels/FuelCycleSystemScalarKernel/evaluation_point) lies outside the mesh, or in a subdomain outside the block restriction of an element-dependent functor, the simulation stops with an error that names the functor and the parameter it was supplied to.

The following input shows each of these functor types defined so that it reproduces the same sink term. Each one is selected in turn through `other_sinks` in the test suite.

!listing test/tests/fuel_cycle_Abdou/ss_kernel_functors.i link=false

As a reminder, the system of variables should be defined with the [!param](/Variables/family) attribute set to `SCALAR` for each variable.

!listing test/tests/fuel_cycle_Abdou/fuel_cycle_abdou_generic.i link=false block=Variables/T_01_BZ

!syntax parameters /ScalarKernels/FuelCycleSystemScalarKernel

!syntax inputs /ScalarKernels/FuelCycleSystemScalarKernel

!syntax children /ScalarKernels/FuelCycleSystemScalarKernel
