# Mini-Canister Hydrogen Transport

TMAP8 is used to model hydrogen transport and permeation through an aluminum-clad used nuclear fuel (AUNF) mini-canister storage device from Savannah River National Laboratory (SRNL) [!citep](d'entremont2024aunfminicanister). The mini-canisters house irradiated AUNF assemblies where gamma and neutron radiation from the fuel drives radiolytic decomposition of water, generating H$_2$ gas. Over time, this hydrogen will dissociate and diffuse through the surrounding 304 stainless steel wall, raising concern for potential accumulation. This example demonstrates how TMAP8 can model these processes through two distinct input files with varying degrees of fidelity:

1. [steel_only.i] — isolates hydrogen diffusion through the steel wall with an assumed boundary partial pressure. This simpler model permits verification against an analytical solution, assuming time-independent Dirichlet boundary conditions.
2. [gas_steel.i] — simulates the full system: radiolytic H$_2$ generation, gas-phase transport inside the canister, and simultaneous permeation through the steel wall. This model is validated against SRNL experimental measurements [!citep](d'entremont2024aunfminicanister).

Both models share the same 1D axisymmetric geometry and material parameters for the steel wall. The progression from [steel_only.i] to [gas_steel.i] illustrates the flexibility of TMAP8 in building complexity incrementally.

## Canister Geometry and Mesh

!style halign=left
Both models represent the canister as a 1D axisymmetric domain in cylindrical coordinates ($r$, $z$), using `coord_type = RZ` with `rz_coord_axis = Y` so that the $x$-axis is the radial direction. The canister dimensions [!citep](d'entremont2024aunfminicanister) are listed in [tab:geometry].

!table id=tab:geometry caption=Canister geometry.
| Parameter | Value | Units |
| --- | --- | --- |
| Inner radius, $\mathbf{r_i}$ | $\mathbf{35.94}$ | mm |
| Steel wall thickness, $\mathbf{\delta}$ | $\mathbf{2.16}$ | mm |
| Canister height, $\mathbf{h}$ | $\mathbf{179.3}$ | mm |

In [steel_only.i], the 1D mesh spans only the steel wall, from $r_i$ to $r_i+\delta$, using a single [GeneratedMeshGenerator.md] with 1,500 elements (subdomain 1). In [gas_steel.i], a [CartesianMeshGenerator.md] produces two adjacent blocks: the gas block (subdomain 0) from $r = 0$ to $r = r_i$ with 250 elements, and the steel block (subdomain 1) from $r = r_i$ to $r = r_i + \delta$ with 1,500 elements. Two [SideSetsBetweenSubdomainsGenerator.md] steps then create the named interface sidesets `interface_gas_to_steel` and `interface_steel_to_gas` that are required for the [InterfaceSorption.md] kernel.

In [steel_only.i], the mesh is defined as:

!listing test/tests/mini_canister/steel_only.i link=false block=Mesh

In [gas_steel.i], the mesh is defined as:

!listing test/tests/mini_canister/gas_steel.i link=false block=Mesh

## Nomenclature

!style halign=left
[tab:variables] lists the variables and physical parameters used in this example with their units.

!table id=tab:variables caption=Nomenclature of variables and physical parameters.
| Symbol | Description | Units |
| --- | --- | --- |
| $\mathbf{C_s}$ | Mobile H atom concentration in steel | $\mathrm{\mu}$mol mm$^{-3}$ |
| $\mathbf{C_g}$ | Mobile H$_2$ molecule concentration in gas | $\mathrm{\mu}$mol mm$^{-3}$ |
| $\mathbf{D_s}$ | Diffusivity of H in 304 stainless steel | mm$^2$ day$^{-1}$ |
| $\mathbf{D_g}$ | Diffusivity of H$_2$ in He | mm$^2$ day$^{-1}$ |
| $\mathbf{K_s}$ | Solubility of H in steel (Sieverts' constant) | $\mathrm{\mu}$mol mm$^{-3}$ Pa$^{-1/2}$ |
| $\mathbf{P}$ | Partial pressure of H$_2$ | Pa |
| $\mathbf{T}$ | Temperature (constant) | K |
| $\mathbf{R}$ | Ideal gas constant | J K$^{-1}$ mol$^{-1}$ |
| $\mathbf{S}$ | Volumetric H$_2$ generation rate in gas | $\mathrm{\mu}$mol mm$^{-3}$ day$^{-1}$ |
| $\mathbf{M(t)}$ | Cumulative H$_2$ yield in gas | $\mathrm{\mu}$mol |
| $\mathbf{t}$ | Time | day |

## Steel-Only Model

### Governing Equations

!style halign=left
In the steel-only model, only hydrogen transport within the steel wall is simulated. The governing equation is a 1D diffusion model:

\begin{equation} \label{eq:steel_diffusion}
\frac{\partial C_s}{\partial t} = \frac{\partial}{\partial x}\left(D_s\frac{\partial C_s}{\partial x} \right),
\end{equation}

where the diffusivity follows an Arrhenius temperature dependence [!citep](san_marchi2012hydrogensteel):

\begin{equation} \label{eq:diffusivity}
D_s(T) = D_{s,0} \exp\!\left( - \frac{E_{D}}{RT} \right).
\end{equation}

Because `coord_type = RZ` is set, MOOSE automatically applies the axisymmetric cylindrical weighting to the diffusion kernel.

### Boundary Conditions

!style halign=left
At the inner steel surface ($r = r_i$), the hydrogen concentration is fixed by Sieverts' law using the [EquilibriumBC.md] boundary condition. An auxiliary variable `H_partial_pressure_gas` is first set by a [FunctionAux.md] at the inner boundary, and [EquilibriumBC.md] then enforces:

\begin{equation} \label{eq:sieverts_bc}
C_s(r_i, t) = 2 K_s(T) \sqrt{P},
\end{equation}

where the factor of 2 converts from molecular H$_2$ equilibrium to atomic H concentration, and the solubility follows an Arrhenius dependence:

\begin{equation} \label{eq:solubility}
K_s(T) = K_{s,0} \exp\!\left( - \frac{E_{K}}{RT} \right).
\end{equation}

!style halign=left
The H$_2$ partial pressure $P$ is provided by a function selected via the `pressure_function` input parameter. A nonexhaustive set of implementations include: (1) a power-law fit to experimental SRNL pressure data (`SRNL_pressure`) calculated using a power-law least-squares fit, used as the default for validation (see [fig:partial_pressure] and [fig:gas_yield]) and for the conservation-of-mass check (see [fig:steel_conservation]):

\begin{equation} \label{eq:srnl_pressure}
P = P_{\text{SRNL}}\left(t\right) \coloneqq 376.7588 \, t^{0.6177} \quad \text{Pa},
\end{equation}

or (2) a constant value (`constant_pressure`) that can be selected to enable the diffusion-front verification against a closed-form analytical solution (see [fig:diffusion_length]):

\begin{equation} \label{eq:assumed_pressure}
P = P_c \coloneqq 0.10 \times 24 \text{ psi} \approx 16{,}547 \text{ Pa},
\end{equation}

which assumes 10% of the 24 psi He-backfilled canister pressure is attributable to H$_2$ [!citep](d'entremont2024aunfminicanister,hlushko2024aunf).

At the outer steel surface ($r = r_i + \delta$), hydrogen is released to the ambient environment, and the concentration is set to zero by a [DirichletBC.md] (defined in [mini_canister_base.i]):

\begin{equation} \label{eq:outer_bc}
C_s(r_i + \delta, t) = 0.
\end{equation}

### Solver

!style halign=left
Because the steel-only problem is linear (constant diffusivity, linear Sieverts' BC), [steel_only.i] uses `solve_type = LINEAR` for a direct LU factorization at each timestep.

### Model Parameters and Simulation Conditions

!table id=tab:steel_only_params caption=Steel-only model parameters and simulation conditions.
| Parameter | Description | Value | Units | Reference |
| --- | --- | --- | --- | --- |
| $\mathbf{D_{s,0}}$ | Diffusivity pre-exponential factor | $\mathbf{0.20 \times 10^{-6}}$ | m$^2$ s$^{-1}$ | [!cite](san_marchi2012hydrogensteel) |
| $\mathbf{E_{D}}$ | Diffusivity activation energy | $\mathbf{49.3}$ | kJ mol$^{-1}$ | [!cite](san_marchi2012hydrogensteel) |
| $\mathbf{K_{s,0}}$ | Solubility pre-exponential factor | $\mathbf{266 \times 10^{-6}}$ | $\mathrm{\mu}$mol mm$^{-3}$ Pa$^{-1/2}$ | [!cite](san_marchi2012hydrogensteel) |
| $\mathbf{E_{K}}$ | Solubility activation energy | $\mathbf{6.86}$ | kJ mol$^{-1}$ | [!cite](san_marchi2012hydrogensteel) |
| $\mathbf{T}$ | Temperature | $\mathbf{313.15}$ | K | [!cite](d'entremont2024aunfminicanister) |

### Results

#### Conservation of Mass

!style halign=left
As an internal consistency check, the total hydrogen mass integrated over the steel domain (`annular_cylinder_total_mass_steel`) is compared against the time-integrated net diffusive flux across the inner and outer boundaries (`annular_cylinder_time_integrated_flux`). Both integrals are weighted for the axisymmetric cylindrical geometry and then scaled by the canister height $h$ to represent 3D mass in $\mathrm{\mu}$mol H. [fig:steel_conservation] shows the percent difference between the two quantities as a single-curve conservation metric, defined as $\left|\,\mathrm{flux}/\mathrm{mass} - 1\,\right| \times 100\,\%$. The metric is highly sensitive to the postprocessors' small values within the first few timesteps, but quickly converges to a small value, and can be further reduced by refining the mesh and timestep.

!media comparison_mini_canister.py
  image_name=steel_only_conservation_of_mass.png
  style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
  id=fig:steel_conservation
  caption=Conservation of mass check for the steel-only model: percent difference $\left|\,\mathrm{flux}/\mathrm{mass} - 1\,\right| \times 100\,\%$ between the accumulated boundary flux and the total H mass in the steel domain for $t>1$ day.

#### Diffusion Front Verification

!style halign=left
For a semi-infinite slab with a constant-concentration boundary condition, the diffusion front advances as $\ell(t) = \sqrt{\pi D_s t}$, providing a straightforward check that the numerical diffusion is correctly implemented. The simulated diffusion front is computed via the `simulated_diffusion_length` postprocessor as the $x$-intercept of the tangent line using the interface concentration and gradient. [fig:diffusion_length] shows the simulated diffusion front length, using the constant pressure $P_c$, compared to the analytical expression, which it matches.

!media comparison_mini_canister.py
  image_name=diffusion_length.png
  style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
  id=fig:diffusion_length
  caption=Comparison of the simulated and analytical ($\sqrt{\pi D_s t}$) diffusion front length in the steel wall over 0.25 years.

!listing test/tests/mini_canister/steel_only.i link=false block=Postprocessors/exact_diffusion_length

!listing test/tests/mini_canister/steel_only.i link=false block=Postprocessors/simulated_diffusion_length

## Gas-Steel Model

### Governing Equations

!style halign=left
The gas-steel model resolves both the gas phase and steel simultaneously. In the gas phase ($0 \leq r \leq r_i$), H$_2$ is generated by radiolysis and transported by diffusion:

\begin{equation} \label{eq:gas_diffusion}
\frac{\partial C_g}{\partial t} = \frac{\partial}{\partial x}\left(D_g \frac{\partial C_g}{\partial x} \right) + S(t),
\end{equation}

where $D_g$ is the diffusivity of H$_2$ in the He backfill gas [!citep](middha2002hydrogenhelium). In the steel wall ($r_i \leq r \leq r_i + \delta$), [eq:steel_diffusion] applies as before. The axisymmetric weighting is again applied automatically by MOOSE. At the symmetry axis ($r = 0$), no explicit boundary condition is required: MOOSE's natural boundary condition enforces zero diffusive flux.

### Hydrogen Generation Source Term

!style halign=left
The cumulative radiolytic H$_2$ yield is modeled using a power-law fit to the SRNL experimental data [!citep](d'entremont2024aunfminicanister), again calculated using a power-law least-squares fit:

\begin{equation} \label{eq:H2_yield}
M(t) = 69.7055 \, t^{0.6808} \quad [\mathrm{\mu}\text{mol}],
\end{equation}

where $t$ is time in days, calibrated assuming a Co-60 irradiator dose rate of approximately 124 Gy/min [!citep](d'entremont2024aunfminicanister). The volumetric source term in [eq:gas_diffusion] is obtained by differentiating [eq:H2_yield] with respect to time and normalizing by the gas volume:

\begin{equation} \label{eq:source_term}
S(t) = \frac{1}{V_g} \frac{dM}{dt} = \frac{69.7055 \times 0.6808}{V_g} \, t^{0.6808 - 1} \quad [\mathrm{\mu}\text{mol mm}^{-3}\text{ day}^{-1}].
\end{equation}

### Interface Condition

!style halign=left
At the gas-steel interface ($r = r_i$), hydrogen equilibrium between the gas and solid phases is enforced by the [InterfaceSorption.md] interface kernel. Using the ideal gas law to convert gas-phase concentration to partial pressure ($P = C_g R T$), the equilibrium atomic hydrogen concentration in the steel is:

\begin{equation} \label{eq:interface_sieverts}
C_s(r_i, t) = 2 K_s(T) \sqrt{C_g(r_i, t) \, R \, T}.
\end{equation}

The `unit_scale_neighbor` parameter is set to $10^3$ to correct for the unit mismatch between $C_g$ in $\mathrm{\mu}$mol mm$^{-3}$ and the ideal gas constant used internally by [InterfaceSorption.md], which draws $R$ in J K$^{-1}$ mol$^{-1}$ from the MOOSE [TMAP8PhysicalConstants.md] namespace. Converting $C_g$ from $\mathrm{\mu}$mol mm$^{-3}$ to mol m$^{-3}$ introduces a combined factor of $10^{-6}$ (mol/$\mathrm{\mu}$mol) $\times$ $10^{9}$ (mm$^3$/m$^3$) $= 10^3$, which is supplied via `unit_scale_neighbor`. The extra factor of $2$ converts the solubility to represent atomic $H$.

### Solver

!style halign=left
Because the interface is nonlinear, [gas_steel.i] uses `solve_type = Newton`. Both models simulate 0.25 years (≈ 91.3 days) using a [BDF2.md] time integration scheme. This model is equipped with an [IterationAdaptiveDT.md] adaptive timestep that targets 5 Newton iterations per step.

### Model Parameters

[tab:gas_steel_params] lists the parameters used in the gas-steel model.

!table id=tab:gas_steel_params caption=Additional gas-steel model parameters (steel parameters as in [tab:steel_only_params]).
| Parameter | Description | Value | Units | Reference |
| --- | --- | --- | --- | --- |
| $\mathbf{D_g}$ | H$_2$ diffusivity in He | $\mathbf{2.7}$ | cm$^2$ s$^{-1}$ | [!cite](middha2002hydrogenhelium) |
| $\mathbf{V_g} = \pi\mathbf{r_i}^2\mathbf{h}$ | Internal gas volume | $\approx\mathbf{727,400}$ | mm$^3$ | Computed |

### Results

#### Conservation of Mass

!style halign=left
[fig:gas_steel_conservation] verifies conservation of mass in the gas-steel model by comparing the total hydrogen mass in the domain (`cylinder_total_mass`, the sum of gas and steel masses) against the sum of the time-integrated boundary flux (`cylinder_time_integrated_flux`) and the cumulative source term (`cylinder_total_generation`). Throughout, all quantities are tracked in $\mathrm{\mu}$mol H atoms. The figure plots the percent difference between the two quantities, defined similarly to before as $\left|\,(\mathrm{flux}+\mathrm{source})/\mathrm{mass} - 1\,\right| \times 100\,\%$. The metric remains small, confirming that mass contributions from the coupled gas-generation, gas-phase transport, interface transfer, and steel diffusion are all consistently accounted for.

!media comparison_mini_canister.py
  image_name=gas_steel_conservation_of_mass.png
  style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
  id=fig:gas_steel_conservation
  caption=Conservation of mass check for the gas-steel model: percent difference $\left|\,(\mathrm{flux}+\mathrm{source})/\mathrm{mass} - 1\,\right| \times 100\,\%$ between the accumulated boundary flux plus source term and the total H mass in the domain for $t>1$ day.

#### Gas-Phase Hydrogen Yield Validation

!style halign=left
[fig:gas_yield] compares the total atomic hydrogen mass in the gas phase (`inner_cylinder_total_mass_gas`) against the cumulative H$_2$ yield measured by SRNL [!citep](d'entremont2024aunfminicanister). Agreement between the simulation and experiment reflects the accuracy of the power-law source model ([eq:H2_yield]). It is important to note that we are comparing against data that is also fed into the model. Future work will include a more complex generation model independent of this data.

!media comparison_mini_canister.py
  image_name=gas_phase_validation.png
  style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
  id=fig:gas_yield
  caption=Comparison of TMAP8 total gas-phase hydrogen mass against SRNL experimental cumulative H$_2$ yield data.

#### Partial Pressure Validation

!style halign=left
[fig:partial_pressure] compares the simulated H$_2$ partial pressure at the gas-steel interface against pressure measurements from the SRNL irradiation experiment [!citep](d'entremont2024aunfminicanister). The partial pressure is computed from the gas-phase concentration at the interface using the ideal gas law via the `H_partial_pressure_interface` postprocessor.

!media comparison_mini_canister.py
  image_name=partial_pressure_comparison.png
  style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
  id=fig:partial_pressure
  caption=Comparison of TMAP8 simulated H$_2$ partial pressure at the gas-steel interface against SRNL experimental measurements.

## Comparison of Steel Hydrogen Uptake Between the Two Models

!style halign=left
[fig:model_comparison] compares the total atomic hydrogen mass accumulated in the steel wall between the steel-only and gas-steel models. The left axis shows the absolute H mass in $\mathrm{\mu}$mol; the right axis shows the steel mass as a percentage of the total H inventory. By default the steel-only model uses the time-dependent SRNL partial-pressure fit (`pressure_function = SRNL_pressure`), giving decent agreement with the gas-steel model, which evolves the interface pressure self-consistently.

!media comparison_mini_canister.py
  image_name=hydrogen_yield_in_steel.png
  style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
  id=fig:model_comparison
  caption=Comparison of total H mass in the steel wall (left axis) and fraction of total H inventory in the steel (right axis, dashed) between the steel-only (SRNL pressure fit) and gas-steel simulations.


## Input File Structure

!style halign=left
Both models are structured around two shared files that are incorporated via the `!include` capability:

- [mini_canister.params] — defines all shared model parameters (geometry, material properties, numerics).
- [mini_canister_base.i] — defines the MOOSE objects shared by both models: the steel variable and kernels, temperature auxiliary variable, outer Dirichlet boundary condition, steel-domain postprocessors, and the executioner.

Each top-level input file adds only the objects that are specific to its model. This structure keeps the shared physics in one place and avoids duplication.

## Input Files

!style halign=left
The input files for this example are [/steel_only.i] and [/gas_steel.i], together with the shared [/mini_canister_base.i] and [/mini_canister.params]. All files are also used as tests in TMAP8 at [/mini_canister/tests].

!listing test/tests/mini_canister/mini_canister_base.i link=false

!listing test/tests/mini_canister/steel_only.i link=false

!listing test/tests/mini_canister/gas_steel.i link=false

!bibtex bibliography
