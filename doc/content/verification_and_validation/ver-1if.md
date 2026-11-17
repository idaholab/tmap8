# ver-1if

# Species Equilibration Problem in Lawdep Conditions with Unequal Starting Pressures

!alert tip title=TMAP8 supports different surface reaction models
The current case uses what TMAP7 called the `lawdep` model.
The [theory_manual.md] page describes the `lawdep` model and other surface models.

## General Case Description

This challenge problem is taken from [!cite](ambrosek2008verification) and builds on [ver-1ie](ver-1ie.md). This TMAP8 case is published in [!cite](Simon2027). The configuration and modeling parameters are the same as in [ver-1ie](ver-1ie.md), except that, in the current case, the starting pressures for A$_2$ and B$_2$ are not equal. The case is simulated in [!file](/ver-1ie.i), but the starting pressures of A$_2$ and B$_2$ are $1 \times 10^4$ Pa and $1 \times 10^5$ Pa, respectively, and there is no AB initially present. The surface reaction considered is illustrated in [ver-1if_schematic].

!media figures/ver-1i_schematic.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=ver-1if_schematic
    caption=Schematic of the ver-1if case (the same configuration is used for ver-1ia to ver-1if): gas species A$_2$ and B$_2$ in a gas enclosure react on a reactive surface to form AB.

## Analytical solution

Similar to [ver-1ie](ver-1ie.md), the governing equation becomes

\begin{equation}
\label{eq:lawdep:equation_p_ab_final}
\frac{d P_{AB}}{dt} = \frac{S k_B T K_d}{V} \left(2 \sqrt{P^0_{A_2} - \frac{P_{AB}}{2}} \sqrt{P^0_{B_2} - \frac{P_{AB}}{2}} - P_{AB}\right).
\end{equation}

This is a nonlinear function and the analytical solution is hard to calculate. [!cite](ambrosek2008verification) uses the solution from [ver-1ia](ver-1ia.md) with a different saturation time constant to compare with the numerical solution. The equation is defined by

\begin{equation}
\label{eq:lawdep:analytical_solution}
P_{AB}  = \frac{2 P_{A_2}^0 P_{B_2}^0}{P_{A_2}^0 + P_{B_2}^0} \left(1 - \exp \left(- \frac{t}{\tau}\right)\right),
\end{equation}
where $\tau$ is the saturation time constant. $\tau$ is selected as 0.123 to match the numerical solution in [eq:lawdep:analytical_solution].

!alert note title= No exact analytical solution
Because [eq:lawdep:equation_p_ab_final] is a complex nonlinear function, we have no exact analytical solution to compare against. Although presented as a verification case in [!cite](ambrosek2008verification) this is, therefore, not a true verification case, as no analytical solution is currently available for direct comparison. Instead, we compare the numerical solution provided by TMAP8 against an adapted analytical solution from [ver-1ia](ver-1ia.md), and we benchmark the TMAP8 predictions against the TMAP7 results from [!cite](ambrosek2008verification). This is, in essence, a code-to-code benchmarking case.


## Results

A comparison of the AB concentration as a function of time is plotted in [ver-1if_comparison_pressure]. The TMAP8 calculations are found to be in reasonable agreement with the solution from TMAP7, with a root mean square percentage error (RMSPE) of RMSPE =  13.56%. It makes sense for us because the solution from TMAP7 is not the real analytical solution. Also, the results from TMAP8 represent an improvement from those from TMAP7, which showed some numerical instability around $t=2.5$ s. The concentrations of A$_2$ and B$_2$ as a function of time are also plotted in [ver-1if_comparison_pressure].

!media comparison_ver-1if.py
       image_name=ver-1if_comparison_pressure.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1if_comparison_pressure
       caption=Comparison of AB concentration as a function of time calculated through TMAP8 and analytically for the solution in lawdep conditions when A$_2$ and B$_2$ have unequal pressures [!citep](ambrosek2008verification).

## Input files

!style halign=left
The input file for this case can be obtained by updating the initial pressure for B$_2$ in [!file](/ver-1ie.i), which is the approach used to create tests in TMAP8 at [!file](/ver-1if/tests).

!bibtex bibliography
