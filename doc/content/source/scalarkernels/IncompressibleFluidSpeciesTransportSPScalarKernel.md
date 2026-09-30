# IncompressibleFluidSpeciesTransportSPScalarKernel

## Overview

This class implements the steady-state residual of the species transport equation for the [Path-integrated incompressible flow model](modules/thermal_hydraulics/theory_manual/path_integrated_incompressible_model/index.md). It requires a coupled variable mass flow rate, a coupled variable fluid temperature, a coupled variable upstream fluid temperature, a coupled variable downstream fluid temperature, a coupled variable upstream concentration, a coupled variable downstream concentration, and coupled variable wall species concentrations that compose the primary species, all given as coupled [ScalarVariables](syntax/Variables/index.md). It operates on the segment primary species concentration, $C$:

!equation
0 = \frac{\dot{m}}{2 L A \rho} \left(1 - \frac{|\dot{m}|}{\dot{m}}\right) C_d - \frac{\dot{m}}{2 L A \rho} \left(1 + \frac{|\dot{m}|}{\dot{m}}\right) C_u + \frac{|\dot{m}|}{L A \rho} C - \sum_{i=1}^{N_p} C_{p,i} \lambda_{p,i} + C \lambda - \frac{J P_w}{A} \,

Note, use of this kernel with transient problems also necessitates the use of a [ODETimeDerivative.md], which includes the time derivative term, $\frac{du}{dt}$, with $u$ being the segment primary species concentration, which adds the time derivative of the segment concentration to the residual.

The wall flux, $J$, is computed differently depending on the [!param](/ScalarKernels/IncompressibleFluidSpeciesTransportSPScalarKernel/fluid_type) parameter. If the [!param](/ScalarKernels/IncompressibleFluidSpeciesTransportSPScalarKernel/fluid_type) is "solvent" then the flux is computed assuming quasi-steady Sievert's law, assuming the wall transports dissociated atoms and the fluid transports molecules. If the [!param](/ScalarKernels/IncompressibleFluidSpeciesTransportSPScalarKernel/fluid_type) is "metal" then the flux is computed assuming quasi-steady Henry's law, assuming both the wall and the fluid transport dissociated atoms. If the [!param](/ScalarKernels/IncompressibleFluidSpeciesTransportSPScalarKernel/fluid_type) is "gas" then the flux is computed from a rate balance of atom dissociation and recombination at the interface.

This kernel takes a fluid properties object based on the [SinglePhaseFluidProperties.md] base class.
It also takes functor inputs for flow area, perimeter, and length.
All parameters are defined as functors,
which should allow versatility in accepting a variety of input arguments. Furthermore, being functors, it is possible for them to be controlled via [Controls](syntax/Controls/index.md) as supplied [Postprocessors](syntax/Postprocessors/index.md), for example.

Some consideration should be given to the [!param](/ScalarKernels/IncompressibleEnergySPScalarKernel/is_implicit) parameter. This term allows the user to select whether the solve
should be done with the current or the previous state values of functor properties. This may allow the system to evolve more slowly which may avoid some issues with respect to divergence of particularly unstable systems.

As a reminder, the system of variables should be defined with the [!param](/Variables/family) attribute set to `SCALAR` for each variable.

!syntax parameters /ScalarKernels/IncompressibleEnergySPScalarKernel

!syntax inputs /ScalarKernels/IncompressibleEnergySPScalarKernel

!syntax children /ScalarKernels/IncompressibleEnergySPScalarKernel
