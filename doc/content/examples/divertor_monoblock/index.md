# Divertor Monoblock During Pulsed Operation

TMAP8 is used to model tritium transport in a divertor monoblock to elucidate the effects of pulsed operation (up to fifty 1600-second plasma discharge and cool-down cycles) on the tritium in-vessel inventory source term and ex-vessel release term (i.e., tritium retention and permeation) for safety analysis. This example reproduces the results presented in [!cite](Shimada2024114438).

This case is also available on the [Virtual Test Bed (VTB)](https://mooseframework.inl.gov/virtual_test_bed/) [!citep](Charlot2025VTB).

## General description of the simulation case and corresponding input file

### Introduction

!style halign=left
In a magnetic confinement fusion system, the divertor components will be subjected to intense particle and heat fluxes from plasma,
as well as 14-MeV neutrons stemming from deuterium-tritium (D-T) reactions,
thus creating extremely high temperature and hydrogen concentration gradients across tens of millimeters.
Furthermore, the thermomechanical properties of the divertor materials will evolve over time in response to displacement damage and gas/solid transmutations.
Thus, predictive modeling of tritium transport in the divertor poses enormous challenges, as it requires simulation capabilities capable of
(1) multi-material configurations, (2) high thermal cycles, (3) complex 2D and 3D geometries, (4) and microstructural evolution
resulting from displacement damage and gas/solid transmutations.
For example, the ITER divertor, which consists of tungsten (W) monoblocks bonded to cooling tubes made of copper-chromium-zirconium (CuCrZr) alloy,
is designed to withstand high heat fluxes (∼10 MW $m^{−2}$) during steady-state plasma operation from intense D-T plasma flux (∼1024 $m^{−2}s^{−1}$).
In this example, we simulate tritium retention and permeation as well as thermal transport in an ITER-like 2D W-Cu-CuCrZr monoblock and demonstrate
the first three (out of four) aforementioned required simulation capabilities for tritium transport in the divertor using TMAP8, as presented in [!cite](Shimada2024114438).
This simulation was also based on the cases published in [!cite](Hodille2021126003).

The sections below describe the simulation details and explain how they translate into the example TMAP8 input file.
Not every part of the input file is explained here.
If the interested reader has more questions about this example case and how to modify this input file to adapt it to a different case,
feel free to reach out to the TMAP8 development team on the [TMAP8 GitHub discussion page](https://github.com/idaholab/TMAP8/discussions).


### Divertor monoblock geometry and mesh generation

!style halign=left
[fig:mesh] shows the geometry, mesh, and temperature distribution of the 2D monoblock employed in [!cite](Shimada2024114438) and in the present example.
The 2D monoblock consisted of three materials:

1. W monoblock ($r$ (mm) > 8.5),
2. Cu interlayer (7.5 < $r$ (mm) < 8.5),
3. CuCrZr tube (6.0 < $r$ (mm) < 7.5), and
4. H$_2$O cooling ($r$ (mm) < 6.0),

where $r=\sqrt{x^2+y^2}$  in a Cartesian coordinate system, and the center point ($x$, $y$) = (0, 0) is defined at the center of the CuCrZr tube.

!media examples/figures/divertor_monoblock_mesh.png
  id=fig:mesh
  caption=2D monoblock: (left) geometry and mesh; (right) temperature distribution. This corresponds to Fig. 1 in Ref. [!cite](Shimada2024114438).
  style=display:block;margin-left:auto;margin-right:auto;width:50%

[MOOSE] is equipped with a set of user-friendly, built-in mesh generators for creating meshes based on simple geometries (e.g., a monoblock).
The built-in mesh generator [ConcentricCircleMeshGenerator.md] is used to create meshes for the 2D monoblock geometry.
Only the left-hand (−14.0 < $x$ (mm) < 0 & −14.0 < $y$ (mm) < 14.0) portion of the monoblock is used,
such that the mesh size is halved by assuming symmetry at the $x = 0$ plane.
This example uses a total of 9,418 nodes, creating 28,402 degrees of freedom in the non-linear system.
The finer mesh size and time step are required to compute the trapping-limited diffusion regime, as described in TMAP8 verification case [ver-1d](ver-1d.md).
However, a set of relatively low detrapping energies (< 0.85 eV) is used here to reduce the computing time via the relatively coarse mesh size.

In the input file, the mesh is defined as:

!listing test/tests/divertor_monoblock/divertor_monoblock.i link=false block=Mesh

### Nomenclature of variables and physical parameters

!style halign=left
[tab:variables] lists the variables and physical parameters used in this example with their units.

!table id=tab:variables caption=Nomenclature of variables and physical parameters used in this example.
| Symbol | Variable or Physical Property | Unit |
| --- | --- | --- |
| $C_s$ | Concentration of solute (mobile) species | m$^{−3}$ |
| $C_t$ | Concentration of trapped species | m$^{−3}$ |
| $T$ | Temperature | K |
| $D$ | Diffusivity of solute (mobile) species | m$^{2}$ s$^{-1}$ |
| $K_s$ | Solubility of solute (mobile) species | m$^{−3}$ Pa$^{-1/2}$ |
| $C_{total}$ | Total concentration of species $C_{total}=C_s + C_t$ | m$^{−3}$ |
| $C_t^e$ | Concentration of empty trapping sites | m$^{−3}$ |
| $C_t^0$ | Concentration of trapping sites $C_t^e=C_t^0-C_t$ | m$^{−3}$ |
| $\alpha_t$ | Trapping rate coefficient, $2.75 \times 10^{11}$ | s$^{−1}$ |
| $\alpha_r$ | Release rate coefficient $\alpha_r=\alpha_{r0} \exp⁡((-E_{dt})/(k_b T))$ | s$^{−1}$ |
| $\alpha_{r0}$ | Pre-exponential factor, $8.40 \times 10^{12}$ | s$^{−1}$ |
| $E_{dt}$ | Detrapping energy | eV |
| $N$ | Atomic number density | m$^{−3}$ |
| $\rho$ | Density | kg m$^{-3}$ |
| $c_p$ | Specific heat | J kg$^{-1}$ K$^{-1}$ |
| $k_T$ | Thermal conductivity | W m$^{-1}$ K$^{-1}$ |

!alert warning title=Typo in [!cite](Shimada2024114438)
The equivalent table in [!cite](ambrosek2008verification) has a typographical error: It lists the density in g m$^{-3}$ when the correct unit, used in [tab:variables], is kg m$^{-3}$. This does not, however, change the results since the value used for the density was correct and used the proper unit.


### Variables and governing equations

!style halign=left
To simulate tritium and thermal transport, we define two sets of [!ac](PDEs).
First, the strong form of the mass conservation equation for solute (mobile) T atoms, $C_s$, is written as:

\begin{equation} \label{eq:concentration}
\frac{\partial C_s}{\partial t} + \nabla \cdot (-D \nabla C_s) + \alpha_t \frac{C_t^e}{N} C_s - \alpha_r C_t = 0.
\end{equation}

We use three sets of mass conservation equations to calculate the behaviors of solute T atoms in three different materials (i.e., W, Cu, CuCrZr).
Second, the strong form of the conservation of energy equation is written as:

\begin{equation} \label{eq:temperature}
\rho c_p \frac{\partial T}{\partial t} - \nabla \cdot (k_T \nabla T) = 0.
\end{equation}

[tab:variables] lists all the symbols and definitions used in [eq:concentration] and [eq:temperature].

The next step is to convert these two strong-form PDEs into their weak forms by multiplying with a test function, $\psi$, and integrating over a domain, $\Omega$ with surface $\delta \Omega$ and outward-facing normal vector $\hat{n}$. Using the divergence theorem, one can obtain the weak form of the mass conservation equation ([eq:concentration]) as follows:

\begin{equation} \label{eq:concentration_weak}
\int_{\Omega}\psi \frac{\partial C_s}{\partial t}
-\int_{\delta \Omega} \psi D \nabla C_s \cdot \hat{n}
+\int_{\Omega} \nabla \psi \cdot D \nabla C_s
+\int_{\Omega} \psi \alpha_t \frac{C_t^e}{N} C_s
-\int_{\Omega} \psi \alpha_r C_t = 0.
\end{equation}

Similarly, the weak form of the conservation of energy equation can be written by multiplying [eq:temperature] with a test function, $\psi$, and integrating over a domain, $\Omega$ with surface $\delta \Omega$ and outward-facing normal vector $\hat{n}$. Using the divergence theorem, one can obtain the weak form of the conservation of energy equation as follows:

\begin{equation} \label{eq:temperature_weak}
\int_{\Omega}\psi c_p \frac{\partial T}{\partial t}
-\int_{\delta \Omega} \psi k_T \nabla T \cdot \hat{n}
+\int_{\Omega} \nabla \psi \cdot k_T \nabla T = 0.
\end{equation}

Then, to solve for the [!ac](PDEs) and physical phenomena, we can select appropriate kernels and boundary conditions (BCs) from MOOSE’s extensive library. The following three subsections describe each kernel, BC, and numerical method utilized in the present work.

In the input file, the variables are defined as:

!listing test/tests/divertor_monoblock/divertor_monoblock.i link=false block=Variables

Note the usage of `initial_condition` and `block` parameters in order to set initial conditions and material block applicability for each variable.


### Kernels

!style halign=left
For the mass conservation equation, we use [ADTimeDerivative.md] and [MatDiffusion.md] to represent the 1$^{\text{st}}$ and 3$^{\text{rd}}$ terms of [eq:concentration_weak].
The TMAP8 kernels [TrappingNodalKernel.md] and [ReleasingNodalKernel.md] represent the 4$^{\text{th}}$ and 5$^{\text{th}}$ terms of [eq:concentration_weak],
respectively, and simulate the trapping/release behavior of hydrogen isotopes in/from trap sites.
For the conservation of energy equation, [SpecificHeatConductionTimeDerivative.md] and [HeatConduction.md] solve the 1$^{\text{st}}$ and 3$^{\text{rd}}$ terms of [eq:temperature_weak].
`ADTimeDerivative` and `ADMatDiffusion` are kernels from the core MOOSE framework, and `SpecificHeatConductionTimeDerivative` and `HeatConduction` are kernels from the [MOOSE Heat Transfer Module](modules/heat_transfer/index.md). These pre-made kernels are commonly
re-used to represent time derivative, diffusion, and heat conduction terms in a given material within a variety of MOOSE-based simulations.

!listing test/tests/divertor_monoblock/divertor_monoblock.i link=false block=Kernels

[NodalKernels](syntax/NodalKernels/index.md) are used for non-diffusive variables (trapped species).

!listing test/tests/divertor_monoblock/divertor_monoblock.i link=false block=NodalKernels


### AuxVariables and AuxKernels

!style halign=left
[AuxVariables](AuxVariable.md) are used to track quantities that are not solved for by the [!ac](PDEs),
but are needed to compute materials properties,
or are desirable to obtain as outputs, such as the total concentration of tritium or flux values.
[AuxKernels](AuxKernel.md) provide the expressions that define the `AuxVariables`.

!listing test/tests/divertor_monoblock/divertor_monoblock.i link=false block=AuxVariables

!listing test/tests/divertor_monoblock/divertor_monoblock.i link=false block=AuxKernels


### Boundary conditions and history

!style halign=left
For the mass conservation equation, we use [FunctionNeumannBC.md] and [DirichletBC.md] to solve the 2$^{\text{nd}}$ term of [eq:concentration_weak].
`FunctionNeumannBC` is used to treat the time-dependent plasma exposure at the top (plasma-exposed) surface,
and `DirichletBC` is used to set the BC of the solute T atom concentration to zero at the inner CuCrZr tube (at $r = 6$ mm).
For the energy conservation equation, we use `FunctionNeumannBC` and `DirichletBC` to solve the 2$^{\text{nd}}$ term of [eq:temperature_weak].
`FunctionNeumannBC` is used to treat the time-dependent heat flux at the top (plasma-exposed) surface,
and [FunctionDirichletBC.md] is used to treat the temperature increase in the cooling tube.
`FunctionNeumannBC`, `FunctionDirichletBC`, `DirichletBC`, and `FunctionDirichletBC` are MOOSE objects commonly used to represent the BCs of the variables to be solved.

We simulate a 20,000-second plasma discharge, with each 1,600-second cycle consisting of a 100-second plasma ramp-up,
a 400-second steady-state plasma discharge, a 100-second plasma ramp-down, and a 1,000-second waiting phase.
Up to 50 cycles are simulated to achieve the total discharge.
[fig:tritium_temperature_history] shows the integrated (solute, total and trapped) tritium concentration profiles in the monoblock.
It shows that implantation fluxes and temperatures vary linearly up to (from) their steady-state values from (up to) their initial values during ramp-up (ramp-down).

!media examples/figures/divertor_monoblock_history.png
  id=fig:tritium_temperature_history
  caption=Temperature profiles (orange) and integrated tritium concentration profiles (blue) during two 1,600-second-cycle plasma discharges. This corresponds to Fig. 2 in [!cite](Shimada2024114438).
  style=display:block;margin-left:auto;margin-right:auto;width:60%

During the steady-state plasma discharge, we set a heat flux of 10 MW$\cdot$m$^{-2}$ at the top of the 2D monoblock (at $y = 14.0$ mm)
and a cooling temperature of 552 K at the inner CuCrZr tube (at $r = 6.0$ mm).
We assume a 100% T plasma with a 5.0 $\times$ 10$^{23}$ m$^{-2}$$\cdot$s$^{-1}$ plasma particle flux
(which is half of the full 1.0 $\times$ 10$^{24}$ m$^{-2}$$\cdot$s$^{-1}$ DT plasma particle flux),
and only 0.1% of the incident plasma particle flux is treated as a retained tritium surface flux at
the exposed surface ($y = 14.0$ mm), corresponding to 5.0 $\times$ 10$^{20}$ m$^{-2}$$\cdot$s$^{-1}$.
For the normalized atomic-fraction variable used in the input file, this boundary condition is written as a
Neumann flux of 7.89 $\times$ 10$^{-9}$ m$\cdot$s$^{-1}$.
The solute T atom concentration is set to zero at the inner CuCrZr tube (at $r = 6.0$ mm).

We treated this plasma exposure by setting the flux BC of the
solute T atom concentration at the exposed surface ($y = 14.0$ mm)
as a simplification of the complex plasma implantation and recombination phenomena,
which would otherwise require a more detailed near-surface implantation model and increase computational costs.

!alert warning title=Updated tritium retained surface flux value from [!cite](Shimada2024114438)
Since publication, the input file has been updated to fix a typo in [!cite](Shimada2024114438), where the retained tritium surface flux was multiplied by the thickness of the first mesh layer ($dx = 1 \times 10^{-4}$ m), leading to a flux of 7.89 $\times$ 10$^{-13}$ s$^{-1}$ instead of 7.89 $\times$ 10$^{-9}$ m$\cdot$s$^{-1}$. The updated input files now use the corrected value of 7.89 $\times$ 10$^{-9}$ m$\cdot$s$^{-1}$.

!alert warning title=Small typo fixed for the heat flux from [!cite](Shimada2024114438)
Since publication, the input file has been updated to fix a small typo that has a minor, almost insignificant effect on the results. The typo set the heat flux to be equal to 300 W/m$^2$ while the pulse was off, as opposed to being equal to 0 W/m$^2$. This was likely due to a mistake in using the off-pulse temperature of the cooling channel (300 K) rather than the zero flux. The change from 300 W/m$^2$ to 0 W/m$^2$ was observed to be negligible, which is attributed to the fact that 300 W/m$^2$ is a small value in this scenario. For context, the maximum heat flux value is 1 $\times 10^{7}$ W/m$^2$. The current version of the input file uses 0 W/m$^2$.

!listing test/tests/divertor_monoblock/divertor_monoblock.i link=false block=BCs


### Functions

!style halign=left

In this example, [Functions](Functions/index.md) are used to define the time-dependent tritium
and heat flux at the exposed surface, as well as the coolant temperature.
Functions can also be spatially-dependent.
The functions are then provided to BCs, as described above.

!listing test/tests/divertor_monoblock/divertor_monoblock.i link=false block=Functions


### Material properties

!style halign=left
We use the tritium mass transport properties listed in [tab:material_properties_tritium]
to solve the mass conservation equation ([eq:concentration_weak]) for two variables:
$C_s$ and $C_t$ (i.e., solute and trapped T atom concentrations) in three materials
and the thermal properties (i.e., density, temperature-dependent specific heat, and thermal conductivity) listed in [tab:material_properties_thermal]
to solve the energy conservation equation ([eq:temperature_weak]) for one variable: the temperature $T$.
The diffusivity is defined as $D=D_0 \exp⁡(-E_D/k_B/T)$ and the solubility is defined as $K_s=K_{s,0} \exp⁡(-E_s/k_B/T)$.

!table id=tab:material_properties_tritium
  caption=Tritium mass transport and trapping properties used in the W, Cu, and CuCrZr layers. $^{**}$NOTE: Two-component solubility in W kept the maximum solubility ratio between W and Cu to 104 at low temperature. The references are provided in [!cite](Shimada2024114438).
| Material | $D_0$ (m$^2$/s) | $E_D$ (eV) | $K_{s,0}$ (Pa$^{1/2}$) | $E_s$ (eV) | Detrapping energy: $E_{dt}$ (eV) | Trap density: $n_{trap}$ (at.fr.) |
| --- | --- | --- | --- | --- | --- | --- |
| W | 2.4$\times$10$^{-7}$ | 0.39 | 1.87$\times$10$^{24}$ | 1.04 | 0.85 | 1.0$\times$10$^{-4}$ |
| W |   |   |  3.14$\times$10$^{20}$$^{**}$ | 0.57$^{**}$ |   |   |
| Cu | 6.6$\times$10$^{-7}$ | 0.39 | 3.14$\times$10$^{24}$ | 0.57 | 0.50 | 5.0$\times$10$^{-5}$ |
| CuCrZr | 3.9$\times$10$^{-7}$ | 0.42 | 4.28$\times$10$^{23}$ | 0.39 | 0.83 | 5.0$\times$10$^{-5}$ |

!table id=tab:material_properties_thermal
  caption=Thermal properties used in the W, Cu, and CuCrZr layers. The references are provided in [!cite](Shimada2024114438).
| Material | Density: $\rho$ (g m$^{-3}$) | Specific heat: $c_p$ (J kg$^{-1}$ K$^{-1}$) | Thermal conductivity: $k_T$ (W m$^{-1}$ K$^{-1}$) |
| --- | --- | --- | --- |
| W | 19,300 | 1.16$\times$10$^{2}$ +7.11$\times$10$^{-2}$ T –6.58$\times$10$^{-5}$ T$^{2}$ +3.24$\times$10$^{-8}$ T$^{3}$ –5.45$\times$10$^{-12}$ T$^{4}$ (293 < T (K) < 2500) | 2.41$\times$10$^{2}$ –2.90$\times$10$^{-1}$ T + 2.54$\times$10$^{-4}$ T$^{2}$ –1.03$\times$10$^{-7}$ T$^{3}$ +1.52$\times$10$^{-11}$ T$^{4}$ (293 < T (K) < 2500) |
| Cu | 8,960 | 4.21$\times$10$^{2}$ –6.85$\times$10$^{-2}$ T (293 < T (K) < 873) | 3.16$\times$10$^{2}$ +3.18$\times$10$^{-1}$ T –3.49$\times$10$^{-4}$ T$^{2}$ +1.66$\times$10$^{-7}$ T$^{3}$ (293 < T (K) < 873) |
| CuCrZr | 8,900 | 390 | 3.87$\times$10$^{2}$ –1.28$\times$10$^{-1}$ T (293 < T (K) < 927) |

!listing test/tests/divertor_monoblock/divertor_monoblock.i link=false block=Materials


### Interface Kernels

!style halign=left
TMAP8 assumes equilibrium between the chemical potentials of the diffusing species similar to how
TMAP4 and TMAP7 treated the diffusing species across two different materials with different chemical potentials.
[SolubilityRatioMaterial.md] is used to treat solute concentration differences stemming from a difference in T solubilities across the interface.
The solubility ratio jump is calculated via the following:
\begin{equation} \label{eq:solubility}
J = \frac{C_{s,1}}{K_{s,1}} - \frac{C_{s,2}}{K_{s,2}}.
\end{equation}

[ADPenaltyInterfaceDiffusion](PenaltyInterfaceDiffusion.md) is used to conserve the particle flux at this interface between two different solubilities.
The extremely low tritium solubility in W at low temperature leads to an extremely low solute concentration in W,
creating a large solute concentration difference between W and Cu.
Two-component solubility in W is used to keep the maximum solubility ratio between W and Cu to 104 at low temperature
to avoid the convergence issue associated with calculating two significantly different solute concentration in W and Cu.

!listing test/tests/divertor_monoblock/divertor_monoblock.i link=false block=InterfaceKernels

### Postprocessors

!style halign=left
Relevant postprocessors have been added to characterize temperatures, fluxes and concentrations of tritium at various points in the model.

First, we add a postprocessor to track the flux across the CuCrZr boundary, and scale it to obtain a total flux

!listing test/tests/divertor_monoblock/divertor_monoblock.i block=Postprocessors/Tritium_SideFluxIntegral link=false

!listing test/tests/divertor_monoblock/divertor_monoblock.i block=Postprocessors/Scaled_Tritium_Flux link=false

We also track the heat flux and maximum temperature in each material

!listing test/tests/divertor_monoblock/divertor_monoblock.i block=Postprocessors/coolant_heat_flux link=false

!listing test/tests/divertor_monoblock/divertor_monoblock.i block=Postprocessors/max_temperature_W link=false

!listing test/tests/divertor_monoblock/divertor_monoblock.i block=Postprocessors/max_temperature_Cu link=false

!listing test/tests/divertor_monoblock/divertor_monoblock.i block=Postprocessors/max_temperature_CuCrZr link=false

Additionally the average temperature in each material

!listing test/tests/divertor_monoblock/divertor_monoblock.i block=Postprocessors/avg_temperature_W link=false

!listing test/tests/divertor_monoblock/divertor_monoblock.i block=Postprocessors/avg_temperature_Cu link=false

!listing test/tests/divertor_monoblock/divertor_monoblock.i block=Postprocessors/avg_temperature_CuCrZr link=false

We also look at the maximum concentration of tritium in each material

!listing test/tests/divertor_monoblock/divertor_monoblock.i block=Postprocessors/max_concentration_W link=false

!listing test/tests/divertor_monoblock/divertor_monoblock.i block=Postprocessors/max_concentration_Cu link=false

!listing test/tests/divertor_monoblock/divertor_monoblock.i block=Postprocessors/max_concentration_CuCrZr link=false

And the total area (2D volume) each material occupies

!listing test/tests/divertor_monoblock/divertor_monoblock.i block=Postprocessors/area_W link=false

!listing test/tests/divertor_monoblock/divertor_monoblock.i block=Postprocessors/area_Cu link=false

!listing test/tests/divertor_monoblock/divertor_monoblock.i block=Postprocessors/area_CuCrZr link=false

!listing test/tests/divertor_monoblock/divertor_monoblock.i block=Postprocessors/total_retention link=false

### Numerical method

!style halign=left
We use a standard preconditioner: the [“single matrix preconditioner”](SingleMatrixPreconditioner.md).
The Newton method is used to model the [transient](Transient.md) tritium and thermal transport in a 2D monoblock.
It is important to note that MOOSE is equipped with the built-in Message Passing Interface (MPI) protocol,
as tritium and thermal transport analysis of fifty 1,600-second cycle plasma discharges in the 2D monoblock is
performed in under 2 hours using a single device/computer (3.5 GHz Apple M2 Pro, 10-Core CPU/16-Core GPU) with this MPI feature.

!listing test/tests/divertor_monoblock/divertor_monoblock.i link=false block=Executioner


## Results

!style halign=left
The simulation results from this example are shown in [fig:results2D_a] and [fig:results2D_b].
For more results, information, and discussion about the results for this example case and
their significance, the reader is referred to [!cite](Shimada2024114438).

!media examples/figures/divertor_monoblock_results_2D_a.png
  id=fig:results2D_a
  caption=Tritium concentration profile in W (left), Cu (center), and CuCrZr (right) after ten 1,600-second cycles ($t = 14912$ s). This corresponds to Fig. 4A in [!cite](Shimada2024114438). The input files have been updated since publication and will provide different results (see warning below).
  style=display:block;margin-left:auto;margin-right:auto;width:40%

!media examples/figures/divertor_monoblock_results_2D_b.png
  id=fig:results2D_b
  caption=Tritium concentration profile in W (left), Cu (center), and CuCrZr (right) after fifty 1,600-second cycles ($t = 78912$ s). This corresponds to Fig. 4B in [!cite](Shimada2024114438). The input files have been updated since publication and will provide different results (see warning below).
  style=display:block;margin-left:auto;margin-right:auto;width:40%

!alert warning title=Updated results since publication of [!cite](Shimada2024114438).
As detailed in the `Boundary conditions and history` section above, the BCs for tritium influx and heat flux have been updated since publication of [!cite](Shimada2024114438) to fix typos. While the heat flux correction only has very minor effects, the new tritium flux is 4 orders of magnitude larger than in [!cite](Shimada2024114438), leading to higher tritium concentrations, overall retention, and losses to the coolant side.

!alert warning title=The exodus file in `gold` is a smaller version of the output
The input file [/divertor_monoblock.i] returns the outputs updated from [!cite](Shimada2024114438). However, a slightly modified version of this input is run in [/divertor_monoblock/tests] as part of TMAP8's [Software Quality Assurance](sqa/index.md exact=True) process: It simulates only one pulse cycle, has a coarser mesh, and outputs the results less regularly to limit the file size. As a result, the exodus file in the test `gold` directory is a smaller version of the output generated when running the full input file.

Note that the current model has been utilized in a follow up study to perform a sensitivity study on material properties and operation conditions, for which the documentation is available [here](examples/divertor_monoblock/sensitivity.md exact=True).

## Complete input file

This case is reproduced three times:

- Once with the usual TMAP8 syntax for input files, which is done in [/divertor_monoblock.i],
- Another time using the [Physics Syntax](syntax/Physics/index.md) to reproduce the same exact case, but with a simpler input file, which is shown in [/divertor_monoblock_physics.i], and
- Last with a simpler model utilizing only two variables (mobile and trapped) for tritium concentration across the different materials instead of having different variables in each block. The input file also uses the [Physics Syntax](syntax/Physics/index.md) and is shown in [/divertor_monoblock_physics-single-variable.i].

Note that since these input files have a lot of sections in common, we utilize the `!include` feature available in MOOSE/TMAP8 to template common parts of the input files. In this case:

- [/divertor_monoblock_common_base.i] contains all the parts of the input files common to all three cases.
- [/divertor_monoblock_mesh_base.i] contains parts related to the geometry and mesh for all three cases.
- [/divertor_monoblock_multi_variable_base.i] contains the parts shared by both the [/divertor_monoblock.i] and [/divertor_monoblock_physics.i] cases.
- [/divertor_monoblock_physics-single-variable.i] contains the parts equivalent to the ones in [/divertor_monoblock_multi_variable_base.i], but for the case in [/divertor_monoblock_physics-single-variable.i].

Below are the input files which [/divertor_monoblock.i] uses to model the scenario described above.
This case can be run reliably with approximately 4 processor cores.
Note that this input file has been optimized for showcasing capability rather than computational cost.

!listing test/tests/divertor_monoblock/divertor_monoblock.i

!listing test/tests/divertor_monoblock/divertor_monoblock_explicit_base.i

!listing test/tests/divertor_monoblock/divertor_monoblock_mesh_base.i

!listing test/tests/divertor_monoblock/divertor_monoblock_common_base.i

!listing test/tests/divertor_monoblock/divertor_monoblock_multi_variable_base.i

!listing test/tests/divertor_monoblock/divertor_monoblock_output_base.i

!bibtex bibliography
