# val-2g

# Permeation experiment with FLiBe

## Case Description

In this experiment from [!cite](calderoni2008measurement), tritium permeation through molten FLiBe (2LiF–BeF$_2$) is measured using a stainless steel permeation cell composed of two internal volumes separated by a 2 mm thick nickel membrane. The bottom side of the membrane is exposed to a T$_2$/argon gas mixture at controlled partial pressures ranging from 1 to 1250 Pa, while the top side is in contact with molten FLiBe. Temperatures are varied between 500°C and 700°C (773–973 K). As tritium permeated through the membrane and dissolved in the FLiBe, it is carried away from the liquid surface by an argon sweep gas containing 5$\%$ H$_2$.

## Model Description

To model this case and understand the physics step by step in order to match the experimental data, we propose two approaches:

- A 1D case with a Ni membrane in contact with FLiBe,
- A 2D case with both a Ni membrane and FLiBe, including an additional Ni layer to investigate tritium losses at the sides.

### 1D case: Nickel Membrane with FLiBe

We model this experimental study in TMAP8 using a 1D simulation that includes three interfaces: enclosure-nickel membrane, nickel membrane-FLiBe, and FLiBe-air. The full domain spans 2 mm of membrane length and 8.1 mm of FLiBe length. The governing equations and modeling assumptions are detailed below.

The diffusion for tritium in the nickel membrane and FLiBe can be expressed by

\begin{equation}
\frac{\partial C_{T_2, \, \text{Ni}}}{\partial t} = \nabla D_{\text{Ni}} \nabla C_{T_2, \, \text{Ni}},
\end{equation}
and
\begin{equation}
\frac{\partial C_{T_2, \, \text{FLiBe}}}{\partial t} = \nabla D_{\text{FLiBe}} \nabla C_{T_2, \, \text{FLiBe}},
\end{equation}

where $C_{T_2, \, \text{Ni}}$ and $C_{T_2, \, \text{FLiBe}}$ represent the concentration fields in the nickel membrane and FLiBe, respectively, $t$ is the time, and $D_{\text{Ni}}$ and $D_{\text{FLiBe}}$ denotes the diffusivity coefficients.

The concentration in FLiBe is related to the concentration in the nickel membrane via the interface sorption law:

\begin{equation}
C_{T_2, \, \text{FLiBe}} = \frac{K_{s, \, \text{FLiBe}}}{K_{s, \, \text{Ni}}^2} C_{T_2, \, \text{Ni}}^2,
\end{equation}

where $K_{s, \, \text{FLiBe}}$ and $K_{s, \, \text{Ni}}$ are the solubilities for tritium in FLiBe and nickel respectively.

At the top of the experimental setup, a Dirichlet boundary condition with a tritium concentration set to zero is imposed, reflecting the assumption that tritium is continuously swept away from the surface:

\begin{equation}
C_{T_2, \, \text{FLiBe}} = 0.
\end{equation}

On the left boundary, which interfaces with the tritium gas, a Dirichlet condition is imposed based on Sieverts’ law:

\begin{equation}
C_{\text{Ni}} = K_{s,\,\text{Ni}}(T) \cdot \sqrt{P_0}
\end{equation}

where $K_{s,\,\text{Ni}}(T)$ is the temperature-dependent solubility of tritium in Ni, and $P_0$ is the applied tritium partial pressure.

These sorption law interfaces assume that the kinetics of the surface reactions are much faster than the other kinetics of the problem.

### 2D Simulation: Nickel Membrane without FLiBe

This simulation models a 2D domain composed solely of a nickel membrane, without any adjacent FLiBe region. The geometry is rectangular, with a length of 2 mm and a width of 25 mm. Tritium transport in the Ni membrane is governed by Fick’s law, given by:

\begin{equation}
\frac{\partial C_{T_2, \, \text{Ni}}}{\partial t} = \nabla D_{\text{Ni}} \nabla C_{T_2, \, \text{Ni}},
\end{equation}

where $C_{\text{Ni}}$ is the tritium concentration in the nickel membrane, and $D_{\text{Ni}}$ is the diffusivity of tritium in Ni.

On the left boundary, which interfaces with the tritium gas, a Dirichlet condition is imposed based on Sieverts’ law:

\begin{equation}
C_{\text{Ni}} = K_{s,\,\text{Ni}}(T) \cdot \sqrt{P_0}
\end{equation}

where $K_{s,\,\text{Ni}}(T)$ is the temperature-dependent solubility of tritium in Ni, and $P_0$ is the applied tritium partial pressure.

On the top and bottom boundaries, Neumann conditions are applied to enforce zero flux:

\begin{equation}
\frac{\partial C_{\text{Ni}}}{\partial y} = 0.
\end{equation}

On the right boundary, which is exposed to the surrounding air, a Dirichlet condition sets the tritium concentration to zero:

\begin{equation}
C_{\text{Ni}} = 0.
\end{equation}

### 2D Simulation: Ni Membrane with FLiBe and Side Ni Layer

This case models a 2D domain composed of three regions: a Ni membrane, a Ni layer at the top, and a block of FLiBe on the right. The geometry enables investigation of tritium side losses through the additional Ni layer. The full domain spans 2 mm of membrane length, 8.1 mm of FLiBe length, and 25 mm in width, with a side layer of width 2 mm.

Tritium diffusion in both the Ni regions and the FLiBe block is governed by Fick's law. The time evolution of the tritium concentration $C_{T_2, \, \text{Ni}}$ in the Ni membrane is given by:

\begin{equation}
\frac{\partial C_{T_2, \, \text{Ni}}}{\partial t} = \nabla D_{\text{Ni}} \nabla C_{T_2, \, \text{Ni}},
\end{equation}

while in the FLiBe region, the concentration $C_{T_2, \, \text{FLiBe}}$ evolves according to:

\begin{equation}
\frac{\partial C_{T_2, \, \text{FLiBe}}}{\partial t} = \nabla D_{\text{FLiBe}} \nabla C_{T_2, \, \text{FLiBe}}.
\end{equation}

At the left boundary of the Ni membrane, a Dirichlet boundary condition is imposed based on Sieverts' law with a spatially varying pressure profile:

\begin{equation}
C_{\text{Ni}}(y) = K_{s,\,\text{Ni}}(T) \cdot \sqrt{P(y)},
\end{equation}

where $K_{s,\,\text{Ni}}(T)$ is the temperature-dependent solubility of tritium in Ni, and $P(y)$ is the applied pressure defined as:

\begin{equation}
P(y) =
\begin{cases}
P_0, & y < 25\, \text{mm} \\
P_0 \cdot \left[ 1 - 3 \left( \frac{y - 25\text{e-3}}{1\text{e-3}} \right)^2 + 2 \left( \frac{y - 25\text{e-3}}{1\text{e-3}} \right)^3 \right], & 25\, \text{mm} \leq y \leq 27\, \text{mm}
\end{cases}
\end{equation}

This pressure profile ensures a smooth transition toward zero tritium concentration near the top of the system, reflecting sweep-out conditions.

Neumann boundary conditions are applied at the bottom of the Ni membrane and the FLiBe region, and at the top of the Ni layer to enforce zero normal flux:

\begin{equation}
\frac{\partial C}{\partial n} = 0.
\end{equation}

A the rightmost boundaries of both the Ni and FLiBe regions, Dirichlet conditions set the tritium concentration to zero:

\begin{equation}
C_{\text{FLiBe}} = 0,
\end{equation}

\begin{equation}
C_{\text{Ni}} = 0,
\end{equation}

indicating that tritium is assumed to be continuously and perfectly removed by a sweep gas.

At the interface between the Ni membrane and the top Ni side layer, continuity conditions are applied to ensure smooth transport of tritium across the materials. Both the concentration and the flux are required to match:

\begin{equation}
C_{\text{Ni, membrane}} = C_{\text{Ni, layer}},
\end{equation}

\begin{equation}
\frac{\partial C_{\text{Ni, membrane}}}{\partial n} = \frac{\partial C_{\text{Ni, layer}}}{\partial n}.
\end{equation}

Finally, at the interface between the Ni membrane and FLiBe, the concentration in FLiBe is related to the concentration in the nickel membrane via the interface sorption law:

\begin{equation}
C_{\text{FLiBe}} = \frac{K_{s,\,\text{FLiBe}}}{K_{s,\,\text{Ni}}^2} C_{\text{Ni}}^2,
\end{equation}

where $K_{s,\,\text{FLiBe}}$ is the solubility of tritium in FLiBe.

## Model Parameters

[val-2g_set_up_values] summarizes the physical parameters used in the simulation, including material properties, boundary conditions, and geometric dimensions derived from experimental data:

!table id=val-2g_set_up_values caption=Physical parameters and geometry used in the simulation.
| Parameter | Description | Value | Units  | Reference |
|---------- |------------ |------ |------- |---------- |
| $D_{\text{FLiBe}}$ | FLiBe diffusion | $9.3 \times 10^{-7} \cdot \exp(-42 \times 10^3 / RT)$ | m²/s | [!cite](calderoni2008measurement) |
| $K_{s,\,\text{FLiBe}}$ | FLiBe solubility | $7.9 \times 10^{-2} \cdot \exp(-35 \times 10^3 / RT)$ | mol/m³/Pa | [!cite](calderoni2008measurement) |
| $D_{\text{Ni}}$ | Ni diffusion | $7 \times 10^{-7} \cdot \exp(-39.5 \times 10^3 / RT)$ | m²/s | [!cite](hattab2024openfoam) / [!cite](causey2012tritium) |
| $K_{s,\,\text{Ni}}$ | Ni solubility | $564 \times 10^{-3} \cdot \exp(-15.8 \times 10^3 / RT)$ | mol/m³/Pa$^{0.5}$ | [!cite](hattab2024openfoam) / [!cite](causey2012tritium) |
| $P_0$ | Initial pressure | $170$, $316$, $538$, $1210$ | Pa | [!cite](calderoni2008measurement) |
| $C_0$ | Initial concentrations in Ni and FLiBe | $10^{-12}$ | mol/m³ | - |
| $L$ | Lengths of Ni and FLiBe regions | Ni membrane: $2$, FLiBe: $8.1$ | mm | [!cite](calderoni2008measurement) |
| $W$ | Widths of the domain | Ni membrane $25$, Ni layer: $2$ | mm | [!cite](calderoni2008measurement) |

## Results and discussion

We first analyze the TMAP8 simulation results using the 1D case without any additional layer, in order to compare them with experimental data. As shown in [val-2g_tritium_flux_1D], the simulation captures the correct order of magnitude for the tritium flux as a function of the T$_2$ partial pressure. At low pressures, the TMAP8 results show good agreement with the experimental measurements. However, at higher pressures, the model deviates significantly, and the fit deteriorates. Specifically, we observe a linear relationship between the tritium flux and pressure, whereas the expected behavior should follow a square-root dependence.

!media comparison_val-2g.py
       image_name=val-2g_tritium_flux_1D.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=val-2g_tritium_flux_1D
       caption= Steady state permeation flux for the 1D case, through Ni and FLiBe at different temperatures and input pressures. The TMAP8 results are compared against experimental results from [!cite](calderoni2008measurement).

We now aim to test the hypothesis that tritium transport through the Ni membrane is the limiting factor. To do so, we removed the FLiBe region and focused solely on simulating tritium diffusion within the nickel membrane. As shown in [val-2g_tritium_flux_2D_no_FLiBe], the resulting tritium flux is significantly overestimated compared to the experimental data, as expected from the removal of additional transport resistance. This result confirms that the presence of FLiBe plays a critical role and must be included in subsequent simulations to more accurately capture the physical behavior of the system at the interface.

!media comparison_val-2g.py
       image_name=val-2g_tritium_flux_2D_no_FLiBe.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=val-2g_tritium_flux_2D_no_FLiBe
       caption= Steady state permeation flux for the 2D case without FLiBe, through Ni and FLiBe at different temperatures and input pressures. The TMAP8 results are compared against experimental results from [!cite](calderoni2008measurement).

To better match the experimental data, we next tested the hypothesis that permeation losses through the side walls could potentially lead to the expected square-root dependence at high pressure. This motivated the implementation of the 2D case with an additional Ni layer.

As shown in [mass_conservation_2D_with_layer], we first verified that mass conservation is respected in the simulation, with a root mean square percentage error (RMSPE) of 4.57 % for the case at 1210 Pa and 823 K. Then, in [val-2g_tritium_flux_2D], we observe that while the tritium flux is reduced compared to the 1D case without a side layer, the flux decreases uniformly across all pressures. Importantly, the relationship between flux and pressure remains linear, rather than exhibiting the expected square root behavior.

!media comparison_val-2g.py
       image_name=val-2g_mass_conservation_2D_with_layer.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=mass_conservation_2D_with_layer
       caption= Mass conservation verification for the 1210 Pa, 823K case: time evolution of $dn/dt$ compared to the net flux.

!media comparison_val-2g.py
       image_name=val-2g_tritium_flux_2D.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=val-2g_tritium_flux_2D
       caption= Steady state permeation flux for the 2D case, through Ni and FLiBe at different temperatures and input pressures. The TMAP8 results are compared against experimental results from [!cite](calderoni2008measurement). For comparison, the 1D results are shown with shading.

This analysis suggests that the additional Ni layer alone does not explain the deviation from experimental data. Other possible mechanisms that may need to be considered to improve agreement with the experimental data include:

- Temperature heterogeneity within the system
- Convective transport within the FLiBe
- Effects related to corrosion, impurities, or surface chemistry
- The presence of hydrogen affecting tritium transport
- Limitations or assumptions in the experimental setup (e.g., the current model tracks the flux exiting the FLiBe)

## Input files

!style halign=left
All the input files for this case can be found at:

- [/val-2g_1D.i]: This file contains the 1D simulation of the nickel membrane and FLiBe
- [/val-2g_2D_no_FLiBe.i]: This file contains the 2D simulation of the nickel membrane without FLiBe
- [/val-2g.i]: This file contains the 2D simulation of the nickel membrane and FLiBe, including an additional Ni layer

[/val-2g/tests] uses `cli_args` to modify [/val-2g.i] and impose the desired temperatures and initial pressures to reproduce the experimental conditions.

To limit the computational costs of the test case, the test runs a version of the file with a smaller simulation time. More information about the changes can be found in the test specification file for this case, namely [/val-2g/tests].
