# ADInterfaceSorption / InterfaceSorption

!syntax description /InterfaceKernels/InterfaceSorption

## Description

The surface concentrations $C_s$ in the solid are related to the partial pressure $P$ (and corresponding gas concentration $C_g$ assuming ideal gas behavior) of the neighboring gas by the interface sorption law:
\begin{equation}
C_s = K P^n = K \left(C_g R T \right)^n,
\end{equation}
where $R$ is the ideal gas constant in J/mol/K, $T$ is the temperature in K, $K$ is the solubility, and $n$ is the exponent of the sorption law. $K$ is described as an Arrhenius equation:
\begin{equation}
K = K_0 \exp \left(\frac{-E_a}{RT}\right),
\end{equation}
where $K_0$ is the pre-exponential constant, and $E_a$ is the activation energy in J/mol. The units of $K$ and $K_0$ depend on the units of $C_s$ and $P$, as well as the value of $n$.

The value of $n$ determines the sorption law. For example:

- $n = 1$ corresponds to Henry's law
- $n = 1/2$ corresponds to Sieverts' law.

A penalty is applied to enforce the sorption law at the interface. Note that solubilities in the literature may only be compatible with concentrations expressed in certain units, and those units may differ from those used elsewhere in the simulation, e.g., $mmol/kg$ versus $mol/m^3$. The model accepts concentration unit conversion factors ([!param](/InterfaceKernels/InterfaceSorption/unit_scale) and [!param](/InterfaceKernels/InterfaceSorption/unit_scale_neighbor)) to accommodate data from different sources. For example, unit conversion factors of $1000$ can be supplied to accommodate sets of solubilities for concentrations in $mmol/m^3$. Note that for multi-atomic molecules, it is important to specify if the moles correspond to the moles of gas molecules, or the moles of atoms. The model assumes that the units associated with the partial pressures are equal and that all constants are compatible with absolute temperature.

To balance the mass flux across the gap, a second interfacial condition is given as:

\begin{equation}
D_s \nabla C_s \cdot \mathbf{n_s} + D_g \nabla C_g \cdot \mathbf{n_g} = 0,
\label{eqn:flux}
\end{equation}
where $D_s$ and $D_g$ are the diffusivities in the solid and the gas, respectively, and $\mathbf{n_s}$ and $\mathbf{n_g}$ are the normals at the interface. Two methods are available to enforce flux conditions at the interface. By default, `InterfaceSorption` applies the flux at the primary side of the interface to the residual on the neighbor side of the interface. Using a kernel such as [MatDiffusion](/MatDiffusion.md) on the neighbor block adds the flux at the neighbor side of the interface to the residual, forming the full flux balance condition shown in the equation above.

!alert warning title=Enforcing flux conditions using the default, non-penalty method
When using the default, non-penalty method to enforce flux conditions at the interface, a kernel such as [MatDiffusion](/MatDiffusion.md) must be applied to the neighbor block to form the correct residual.

Optionally, a penalty can be applied within `InterfaceSorption` to directly enforce the full flux condition at the interface. The penalty method adds the correct residual to the neighbor side of the interface without requiring a second kernel, but it may over-constrain the problem under certain conditions.

Note that the unit conversion factors ([!param](/InterfaceKernels/InterfaceSorption/unit_scale) and [!param](/InterfaceKernels/InterfaceSorption/unit_scale_neighbor)) do not apply to the flux equation to ensure mass conservation.

## Input File Usage Example

!listing test/tests/interfacekernels/InterfaceSorption/interface_sorption.i block=InterfaceKernels

!syntax parameters /InterfaceKernels/InterfaceSorption

!syntax inputs /InterfaceKernels/InterfaceSorption

!syntax children /InterfaceKernels/InterfaceSorption

