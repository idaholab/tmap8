# ver-1fb

# Thermal Transient in a Slab

## General Case Description

This heat transfer verification problem is taken from [!cite](longhurst1992verification) and [!cite](ambrosek2008verification) and builds on the capabilities verified in [ver-1fa](ver-1fa.md). It has been updated and extended in [!cite](Simon2025). The configuration is the same as in [ver-1fa](ver-1fa.md), except that, in the current case, there is no heat source in the slab and both ends with fixed temperature. This case is simulated in [!file](/ver-1fb.i). The geometry and boundary conditions of this case are shown in [ver-1fb_schematic].

!media figures/ver-1fb_schematic.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=ver-1fb_schematic
    caption=Schematic of the ver-1fb case: a slab without heat source and with fixed temperatures at both ends.

The heat conduction in the one-dimensional model is described as:

\begin{equation} \label{eq:thermal_equation}
\rho C_P \frac{d T}{d t} = \nabla \cdot k \nabla T,
\end{equation}

where $T$ is the temperature, $\rho$ is the density, $C_P$ is the specific heat, and $k$ is the thermal conductivity.

The ends of a slab are kept fixed at different temperatures. The temperature distribution in the slab evolves from an initial state to steady-state.

In this case, the thickness of slab, $L$, is 4.0 m, the thermal conductivity is $k =10$ W/m/K, the material density is assumed to be $\rho = 1$ kg/m$^3$, and the specific heat is assumed to be $C_P = 10$ J/kg/K. The fixed surface temperature, $T_0$ and $T_1$, on both ends are defined as 400 K and 300 K, respectively.

## Analytical solution

[!cite](Incropera2002) provides the analytical solution for the temperature of this case as:

\begin{equation} \label{eq:thermal_analytical}
T(x,t) = T_0 \;+\; (T_1-T_0)\left\{1-\frac{x}{L}-\frac{2}{L}\sum_{m=1}^{\infty} \left(\frac{1}{\lambda_m}  \sin(\lambda_m x) \exp(-\alpha \lambda_m^2 t)  \right)\right\},
\end{equation}

where $x$ is the distance across the slab, $t$ is the time, $\lambda_m$ is a coefficient of $\frac{m\pi}{L}$, and $\alpha$ is the thermal diffusivity, which is defined as:

\begin{equation} \label{eq:thermal_diffusivity}
\alpha = \frac{k}{\rho C_p}.
\end{equation}

!alert! warning title=Typo in analytical solution from [!cite](longhurst1992verification)
Both TMAP4 [!citep](longhurst1992verification) and TMAP7 [!citep](ambrosek2008verification) provide analytical solutions, but they use different equations.
At the initial time and steady state, the solution from TMAP7 matches the real thermal distribution, whereas the solution from TMAP4 does not. Thus, TMAP8 selects the solution from TMAP7 as the analytical solution.
!alert-end!

## Results

A comparison of the temperature distribution in the slab, computed through TMAP8 and calculated analytically, is shown in [ver-1fb_comparison_temperature]. The TMAP8 code predictions match very well with the analytical solution with the root mean square percentage errors of RMSPE = 0.09 % at $t = 0.1$ s, RMSPE = 0.03 % at $t = 0.5$ s, RMSPE = 0.02 % at $t = 1$ s, and RMSPE = 0.00 % at $t = 5$ s, respectively.

!media comparison_ver-1fb.py
       image_name=ver-1fb_comparison_temperature.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1fb_comparison_temperature
       caption=Comparison of temperature distribution in the slab calculated
        through TMAP8 and analytically

## Input files

!style halign=left
The input file for this case can be found at [!file](/ver-1fb.i), which is also used as test in TMAP8 at [!file](/ver-1fb/tests).

!bibtex bibliography
