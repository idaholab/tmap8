# ver-1fa

# Heat Conduction with Heat Generation

## General Case Description

This heat transfer verification problem is taken from [!cite](longhurst1992verification) and [!cite](ambrosek2008verification), and it has been updated and extended in [!cite](Simon2025). The geometry and boundary conditions of this case are shown in [ver-1fa_schematic].

!media figures/ver-1fa_schematic.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=ver-1fa_schematic
    caption=Schematic of the ver-1fa case: a slab with volumetric heating $Q$, an adiabatic left boundary, and a fixed temperature on the right boundary.

This case models a heat conduction problem through a slab with a heat source. The heat conduction in the one-dimensional model is described as:

\begin{equation} \label{eq:thermal_equation}
\rho C_P \frac{d T}{d t} = \nabla \cdot k \nabla T + Q,
\end{equation}

where $T$ is the temperature, $\rho$ is the density, $C_P$ is the specific heat, $k$ is the thermal conductivity, and $Q$ is the internal volumetric heat generation rate.

One end of the slab is kept at a constant temperature of 300 K while the other end acts as an adiabatic surface.

This case uses internal volumetric heat generation rate of $Q = 1 \times 10^{4}$ W/m$^3$ in the slab. The thickness of slab, $L$, is 1.6 m, and the thermal conductivity is $k = 10$ W/m/K. The surface temperature, $T_s$, on the end with a constant temperature, is 300 K. The material density and specific heat are assumed to be $\rho = 1$ kg/m$^3$ and $C_P = 1$ J/kg/K, respectively.

## Analytical solution

[!cite](Incropera2002) provides the analytical solution for the steady state temperature of this case as:

\begin{equation}  \label{eq:thermal_analytical}
T = T_s \;+\; \frac{QL^2}{2k} \left(1-\frac{x^2}{L^2}\right),
\end{equation}

where $L$ is the thickness of the slab, and $T_s$ is the imposed surface temperature.

## Results

A comparison of the temperature calculated through TMAP8 and calculated analytically is shown in [ver-1fa_comparison_temperature]. The TMAP8 calculations are found to be in good agreement with the analytical solution, with a root mean square percentage error (RMSPE) of RMSPE = 0.05 %.

!media comparison_ver-1fa.py
       image_name=ver-1fa_comparison_temperature.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1fa_comparison_temperature
       caption=Comparison of temperature along the slab calculated
       through TMAP8 and analytically

## Input files

!style halign=left
The input file for this case can be found at [!file](/ver-1fa.i), which is also used as test in TMAP8 at [!file](/ver-1fa/tests).

!bibtex bibliography
