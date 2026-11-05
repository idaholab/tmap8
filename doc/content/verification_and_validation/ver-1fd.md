# ver-1fd

# Convective Heating

## General Case Description

The fourth heat transfer problem taken from [!cite](ambrosek2008verification) builds on the capabilities verified in [ver-1fa](ver-1fa.md), [ver-1fb](ver-1fb.md), and [ver-1fc](ver-1fc.md). The configuration is the same as in [ver-1fb](ver-1fb.md), except that, the current case has a convection boundary. This case is simulated in [!file](/ver-1fd.i). This TMAP8 case is published in [!cite](Simon2027).

The case focuses on the heating of a semi-infinite slab by convection at the boundary. The slab is initially configured with a constant temperature of 100 K throughout the slab. A convection boundary is activated at the surface from time $t = 0$ s. The convection temperature in the enclosure is $T_{\infty} = 500$ K. In the slab, the conduction coefficient is $h = 200$ W/m$^2$/K, the thermal conductivity is $k = 401$ W/m/K, and the thermal diffusivity is $\alpha = 1.17 \times 10^{-4}$ m$^2$/s. The geometry and boundary conditions of this case are shown in [ver-1fd_schematic].

!media figures/ver-1fd_schematic.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=ver-1fd_schematic
    caption=Schematic of the ver-1fd case: a slab heated by convection on its left boundary, with a zero-flux condition on the right boundary to truncate the domain.

## Analytical solution

The analytical solution is provided by [!cite](Incropera2002):

\begin{equation} \label{eq:analytical_solution}
T(x,t) = T_i + (T_{\infty}-T_i) \left[ \text{erfc}\left( \frac{x}{2 \sqrt{t \alpha}} \right)-\exp\left( \frac{hx}{k} + \frac{h^2t \alpha} {k^2}\right) \text{erfc}\left( \frac{x}{2 \sqrt{t \alpha}} + \frac{h \sqrt{t \alpha}}{k} \right)\right],
\end{equation}
where $T_i = 100$ K is the initial temperature, $T_{\infty} = 500$ K is the temperature of the enclosure, $h = 200$ W/m$^2$/K is the conduction coefficient, $k = 401$ W/m/K is the thermal conductivity, $\text{erfc}$ is the complimentary error function, $x$ is the position in the slab in m, and
\begin{equation} \label{eq:analytical_solution_alpha}
\alpha = \frac{k}{\rho C_p}
\end{equation}
is the thermal diffusivity. The volumetric specific heat is defined as $\rho C_p = 3.439 \times 10^6$ J/m$^3$/K, which gives us $\alpha \approx 1.17 \times 10^{-4}$ m$^2$/s.

Note that the simulated length of the semi-infinite slab is not explicitly specified in [!cite](ambrosek2008verification). In TMAP8, a length of $l=100$ cm with a zero-flux boundary condition at the end was sufficient to match the analytical solution (i.e., the temperature at the desired position $x = 5$ cm is not affected by the boundary condition at position $l$), as shown in [ver-1fd_comparison_convective_heating].

!alert warning title=Typo in [!cite](ambrosek2008verification)
In [!cite](ambrosek2008verification), the value of $k = 801$ W/m/K is provided, whereas the input file lists $k = 401$ W/m/K. In TMAP8, we have decided to use $k = 401$ W/m/K since it provides the same results as those shown in Figure 9 in [!cite](ambrosek2008verification), and provides the appropriate value for $\alpha$. Moreover, [!cite](ambrosek2008verification) lists $\alpha = 1.17 \times 10^{-4}$ m$^2$/s in the documentation, but the input file lists $\rho C_p = 3.439 \times 10^6$ instead of $\alpha$. TMAP8 assumes a density and specific heat value to match $\rho C_p = 3.439 \times 10^6$ to reproduce TMAP7's input file rather than its documentation.

## Results

The comparison between TMAP8 predictions and the analytical solution is performed at depth $x = 5$ cm.
These results are shown in [ver-1fd_comparison_convective_heating].
They show great agreement between TMAP8 and the analytical solution with a root mean square percentage error of RMSPE = 0.29 %.

!media comparison_ver-1fd.py
       image_name=ver-1fd_comparison_convective_heating.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1fd_comparison_convective_heating
       caption=Comparison of temperature profiles for convective heating in a semi-infinite slab from the analytical solution and TMAP8 at depth $x = 5$ cm. The RMSPE is the root mean square percentage error between the analytical solution and TMAP8 predictions.

## Input files

!style halign=left
The input file for this case can be found at [!file](/ver-1fd.i), which is also used as test in TMAP8 at [!file](/ver-1fd/tests).

!bibtex bibliography
