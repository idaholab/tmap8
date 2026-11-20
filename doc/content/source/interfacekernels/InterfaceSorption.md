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

### Inverted formulation for $n < 1$

By default, the sorption law is enforced as $C_s - K \left(C_g R T\right)^n = 0$, which raises the gas concentration $C_g$ to the power $n$.
For $n < 1$, such as Sieverts' law, the slope of this function with respect to $C_g$ is infinite at $C_g = 0$.
To avoid non-numerical values, the gas concentration is limited to a small positive value ($10^{-20}$) in the residual.
This causes convergence problems when the concentration of the gas, or of the species on the neighbor side of the interface, is orders of magnitude below the other concentrations.
Below the limit, the interface condition does not depend on $C_g$ and holds $C_s$ at the value that corresponds to the limit.
Above the limit, the slope is very large.
The solver can then fail to converge once the concentration crosses the limit, and the time step is cut back until it becomes impractically small.
Typical signs are negative concentrations at the interface before the failure, and a solid concentration at the interface that stays at $K \left(10^{-20} R T\right)^n$.
Changing the value of the limit does not remove the problem, because it only shifts which side of the limit is affected.
Bounding the variables, adjusting the initial conditions, and using the unit conversion factors do not solve it either.

Setting [!param](/InterfaceKernels/InterfaceSorption/use_inverted_sorption) to `true` enforces the same law in its inverted form:

\begin{equation}
C_g = \frac{1}{R T} \left(\frac{C_s}{K}\right)^{1/n}.
\end{equation}

For $n \leq 1$, the exponent $1/n$ is at least one, so this function is smooth at $C_s = 0$ and the gas concentration needs no lower limit.
The solid concentration is limited to non-negative values.
The two forms describe the same constraint, so the converged solutions agree.
In the tests, the differences are on the order of $10^{-6}$ in relative terms, which is consistent with the solver tolerance.

To make [!param](/InterfaceKernels/InterfaceSorption/sorption_penalty) have the same meaning as in the default formulation, the residual of the inverted form is multiplied by the slope of the original law, $s = n K \left(R T\right)^n C_\mathrm{eff}^{n-1}$:

\begin{equation}
s \left[\frac{1}{R T} \left(\frac{C_s}{K}\right)^{1/n} - C_g\right] \approx C_s - K \left(C_g R T\right)^n,
\end{equation}

where the approximation becomes an equality at the solution.
The slope is evaluated at $C_\mathrm{eff} = \left[C_g + \left(C_s / K\right)^{1/n} / (R T)\right] / 2$, which is the mean of the gas concentration and the gas concentration implied by the solid concentration.
Because the slope decreases when its argument increases, this value remains bounded whether the solid concentration starts far above or far below its equilibrium value.
Evaluating the slope at only one of the two values diverges in one of these two regimes.
The weighting changes only the relative importance of the residual, not the location of its zero.

!alert warning title=Restrictions of the inverted formulation
The inverted formulation requires $n \leq 1$, and an error is reported otherwise.
It does not change the flux balance, so it is compatible with both the default and penalty-enforced flux balance methods, and with the unit conversion factors.
For $n = 1$ (Henry's law), the scaling factor is constant and both formulations are equivalent, so there is no benefit in using the inverted formulation.
The inverted formulation is not the default, so existing inputs are not affected.

The results of the two formulations are compared in the tests of this object (for example with unit conversion factors and a penalty-enforced flux balance) and in the verification case [ver-1kd](ver-1kd.md), which has a species with an initial concentration many orders of magnitude lower on one side of the interface.
An additional test based on a solid-liquid interface with a very small concentration in the liquid, which does not converge with the default formulation, verifies that the inverted formulation conserves mass and satisfies the sorption law.

## Input File Usage Example

!listing test/tests/interfacekernels/InterfaceSorption/interface_sorption.i block=InterfaceKernels

!syntax parameters /InterfaceKernels/InterfaceSorption

!syntax inputs /InterfaceKernels/InterfaceSorption

!syntax children /InterfaceKernels/InterfaceSorption

