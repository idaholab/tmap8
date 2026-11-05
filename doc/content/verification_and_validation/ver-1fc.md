# ver-1fc

# Conduction in composite structure with constant surface temperatures

## General Case Description

This third heat transfer problem is taken from [!cite](ambrosek2008verification) and builds on the capabilities verified in [ver-1fa](ver-1fa.md) and [ver-1fb](ver-1fb.md).
The configuration is the same as in [ver-1fb](ver-1fb.md), except that the current case is in a composite structure with constant surface temperature. This case is simulated in [!file](/ver-1fc.i) with both transient and steady state solutions. This TMAP8 case is published in [!cite](Simon2027).

The composite is a 40-cm-thick layer of copper (Cu) followed by a 40 cm layer of iron (Fe) ([!cite](ambrosek2008verification)). The temperature of both layers is initially 0 K, but at time $t = 0$ s, the outside face of the Cu is held at 600 K while the outside face of the Fe is maintained at 0 K.
The thermal conductivities of Cu and Fe are set to 401 W/m/K and 80.2 W/m/K, respectively. The TMAP7 documentation does not specify the materials' density $\rho$ or the specific heat $C_p$, but the TMAP7 input file lists $\rho C_p = 3.4392 \times 10^6$ J$\cdot$m$^{-3}\cdot$K$^{-1}$ for Cu and $3.5179 \times 10^6$ J$\cdot$m$^{-3}\cdot$K$^{-1}$ for Fe ([!cite](ambrosek2008verification)). TMAP8 uses $\rho = 8960$ kg/m$^{3}$ and $C_p =  383.8$ J$\cdot$kg$^{-1}\cdot$K$^{-1}$ for Cu and $\rho = 7870$ kg/m$^{3}$ and $C_p = 447.0$ J$\cdot$kg$^{-1}\cdot$K$^{-1}$ for Fe. The densities are from [!cite](Haynes2015), and the specific heat capacities are calculated to match the $\rho C_p$ values from TMAP7 in [!cite](ambrosek2008verification), which closely match values from [!cite](Haynes2015) ($C_p =  385$ J$\cdot$kg$^{-1}\cdot$K$^{-1}$ for Cu and $C_p =  449$ J$\cdot$kg$^{-1}\cdot$K$^{-1}$ for Fe). The geometry and boundary conditions of this case are shown in [ver-1fc_schematic].

!media figures/ver-1fc_schematic.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=ver-1fc_schematic
    caption=Schematic of the ver-1fc case: a composite of copper (Cu) and iron (Fe) layers with fixed temperatures at the outer faces.

This case provides both a verification (comparison against an analytical solution) and a benchmarking (code-to-code comparison) exercise. The steady state solution (called ver-1fcs in [!cite](ambrosek2008verification)) is compared against an analytical solution, and the transient solution is compared against ABAQUS. ABAQUS is a finite element analysis (FEA) program that has been validated for both transient and steady state solutions in heat transfer modeling applications. The ABAQUS code was setup and run by R. G. Ambrosek and presented in [!cite](ambrosek2008verification).

!alert warning title=Typo in [!cite](ambrosek2008verification) - confusion between ABAQUS and TMAP7 results
In [!cite](ambrosek2008verification), Table 11 for TMAP7 and ABAQUS transient results and Table 13 for TMAP7 and ABAQUS steady-state results are identical, even though they should be different. Given the nature of the data, it corresponds to transient conditions and has been used as such for comparison below. As a result, no ABAQUS and TMAP7 data were used in the steady-state case, only TMAP8 predictions and the analytical solution.
Another issue is that the column labels for ABAQUS and TMAP7 are reversed in Table 11 and Table 13, casting doubt on which results correspond to ABAQUS and which to TMAP7. In this benchmarking exercise, we therefore refer to these results as `ABAQUS or TMAP7 (1)` and `ABAQUS or TMAP7 (2)`. Since they are close, we still consider the benchmarking exercise successful.

## Steady State solution and results

The steady-state solution for this problem was compared to the analytical solution in addition to the ABAQUS prediction from [!cite](ambrosek2008verification).
To solve for the steady state solution for this problem, the heat flux is given by

\begin{equation} \label{eq:solution_analytical_heat_flux}
q''=\frac{T_{SA} - T_{SB}}{\left(L_A / k_A \right) + \left(L_B / k_B \right)},
\end{equation}
where

- $T_{Si}$ is the temperature of surface $i$, left ($T_{SA}=600$ K) and right ($T_{SB}=0$ K),
- $L_i$ is the length of segment $i$ ($L_A=L_B=40$ cm),
- $k_i$ is the thermal conductivity of segment $i$ ($k_A = 401$ W/m/K, $k_B = 80.2$ W/m/K).

At steady state, the flux in and out of any section of the slab are equal. The temperature at the interface ($T_I$) can be found by setting the flux through A equal to the flux through B, which leads to:

\begin{equation} \label{eq:solution_analytical_steady_state}
\frac{T_{SA} - T_{I}}{\left(L_A / k_A \right)} = \frac{T_{I} - T_{SB}}{\left(L_B / k_B \right)}.
\end{equation}

The interface temperature at steady state is therefore equal to $T_I = 500$ K. The temperature profile for conduction in steady state, with constant physical properties, is linear,
so the temperature profile of A and B can therefore be found through linear interpolation.

With TMAP8, the steady state solution can be obtained in different ways: by using the [steady-state solve](source/executioners/Steady.md) or by running a [transient simulation](source/executioners/Transient.md) until a steady state is reached.
[!cite](ambrosek2008verification) indicates that the steady-state solution was obtained by running the transient solution until $t=10,000$ s, which is reproduced with TMAP8 here.
TMAP8 predictions were identical to the analytical solution with a root mean square percentage error (RMSPE) of 0.23 %, as shown in [ver-1fc_comparison_temperature_steady_state].

!media comparison_ver-1fc.py
       image_name=ver-1fc_comparison_temperature_steady_state.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1fc_comparison_temperature_steady_state
       caption=Comparison of temperature profiles from the analytical solution and TMAP8 in the composite structure at steady state ($t = 10,000$ s). RMSPE is the root mean square percentage error between the analytical and TMAP8 profiles.

## Transient solution and results

For the transient case, TMAP8 predictions are compared against ABAQUS predictions from [!cite](ambrosek2008verification).
This is therefore a benchmarking case (code-to-code comparison).

The transient solution was compared in two ways: where time, $t$, is held constant and where distance, $x$, through the structure is held constant.
The constant time comparison between ABAQUS and TMAP8 was made at time $t = 150$ s.
The constant time values are shown in [ver-1fc_comparison_temperature_transient_t150], and the comparison is satisfactory.

!media comparison_ver-1fc.py
       image_name=ver-1fc_comparison_temperature_transient_t150.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1fc_comparison_temperature_transient_t150
       caption=Comparison of temperature profiles from TMAP8, TMAP7, and ABAQUS in the composite structure at $t = 150$ s.

The constant distance values were compared at $x = 0.09$ m, at 5 second intervals from time
$t = 0$ s to $t = 150$ s. These results can be seen in [ver-1fc_comparison_temperature_transient_x0.09], and the comparison is satisfactory.

!media comparison_ver-1fc.py
       image_name=ver-1fc_comparison_temperature_transient_x0.09.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1fc_comparison_temperature_transient_x0.09
       caption=Comparison of temperature value over time from TMAP8, TMAP7, and ABAQUS in the composite structure at $x = 0.09$ m.

## Input files

!style halign=left
The input file for this case can be found at [!file](/ver-1fc.i), which is also used as test in TMAP8 at [!file](/ver-1fc/tests).

!bibtex bibliography
