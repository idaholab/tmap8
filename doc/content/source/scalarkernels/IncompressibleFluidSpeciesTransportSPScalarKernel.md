# IncompressibleFluidSpeciesTransportSPScalarKernel

!syntax description /ScalarKernels/IncompressibleFluidSpeciesTransportSPScalarKernel

## Overview

This object implements the time-dependent, globally compressible, locally incompressible, single-phase, scalar-transport solve along a single 1D segment for a single variable dilute primary species concentration. It requires a coupled variable mass flow rate, a coupled variable upstream fluid temperature, a coupled variable downstream fluid temperature, a coupled variable fluid temperature, a coupled variable upstream primary species concentration, a coupled variable downstream primary species concentration, and coupled variables for dissociated atomic concentrations composing the primary species present in the wall, all given as (coupled [ScalarVariables](syntax/Variables/index.md)). Optionally, radioactive precursor concentrations may be supplied as coupled variables as well.

!equation
\frac{\partial u}{\partial t} + \frac{\dot{m}}{2 L} \left(1 - \frac{|\dot{m}|}{\dot{m}}\right) c_d - \frac{\dot{m}}{2 L} \left(1 + \frac{|\dot{m}|}{\dot{m}}\right) c_u + \frac{|\dot{m}|}{L A \rho} u = S_c + \frac{J_c P_w}{A} + \sum_p c_p \lambda_p e^{-\lambda_p \Delta t} - u \lambda_u e^{\lambda_u \Delta t} \,

This kernel takes a fluid properties object based on the [SinglePhaseFluidProperties.md] base class.
It also takes functor inputs for flow area, perimeter, length, precursor half lives, primary species half life, diffusivity, solubility, dissociation, recombination, and equilibrium.
Most parameters are defined as functors,
which should allow versatility in accepting a variety of input arguments.

The fluid type must be defined using the [!param](/ScalarKernels/IncompressibleFluidSpeciesTransportSPScalarKernel/fluid_type) parameter. Accepted values are "gas", "solvent", and "metal". This affects the formulation used in computing the wall flux.



Some consideration should be given to the [!param](/ScalarKernels/IncompressibleEnergySPScalarKernel/is_implicit) parameter. This term allows the user to select whether the solve
should be done with the current or the previous state values of functor properties. This may allow the system to evolve more slowly which may avoid some issues with respect to divergence of particularly unstable systems.

Rather than using [ParsedODEKernel.md] and [ODETimeDerivative.md] kernels, the scalar kernels block can be simplified.

If parameters are to be made available to external control objects, there is still a need to define appropriate [Postprocessors](syntax/Postprocessors/index.md) to inform the scalar kernels, as these cannot be assumed for the general case. Otherwise (for constant properties) it is fine to set values directly in the scalar kernel definition.

As a reminder, the system of variables should be defined with the [!param](/Variables/family) attribute set to `SCALAR` for each variable.

!syntax parameters /ScalarKernels/IncompressibleFluidSpeciesTransportSPScalarKernel

!syntax inputs /ScalarKernels/IncompressibleFluidSpeciesTransportSPScalarKernel

!syntax children /ScalarKernels/IncompressibleFluidSpeciesTransportSPScalarKernel
