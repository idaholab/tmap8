# ver-1ib

# Species Equilibration Problem in Ratedep Conditions with Unequal Starting Pressures

!alert tip title=TMAP8 supports different surface reaction models
The current case uses what TMAP7 called the `ratedep` model.
The [theory_manual.md] page describes the `ratedep` model and other surface models.

## General Case Description

This verification problem is taken from [!cite](ambrosek2008verification) and builds on [ver-1ia](ver-1ia.md). This TMAP8 case is published in [!cite](Simon2027). The configuration and modeling parameters are the same as in [ver-1ia](ver-1ia.md), except that, in the current case, the starting pressures for A$_2$ and B$_2$ are not equal. The case is simulated in [!file](/ver-1ia.i), but the starting pressures of A$_2$ and B$_2$ are $1 \times 10^4$ Pa and $1 \times 10^5$ Pa, respectively, and there is no AB initially present. The surface reaction considered is illustrated in [ver-1ib_schematic].

!media figures/ver-1i_schematic.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=ver-1ib_schematic
    caption=Schematic of the ver-1ib case (the same configuration is used for ver-1ia to ver-1if): gas species A$_2$ and B$_2$ in a gas enclosure react on a reactive surface to form AB.

## Analytical solution

[!cite](ambrosek2008verification) provides the analytical equation for the partial pressure of AB when the conversion rate at the surface is high as

\begin{equation}
\label{eq:ratedep:analytical_solution}
P_{AB}  = \frac{2 P_{A_2}^0 P_{B_2}^0}{P_{A_2}^0 + P_{B_2}^0} \left(1 - \exp \left( -\frac{S K_d k_B T}{V} t \right)\right).
\end{equation}

## Results

A comparison of the concentration of AB as a function of time is plotted in [ver-1ib_comparison_pressure]. The TMAP8 calculations are found to be in good agreement with the analytical solution, with a root mean square percentage error (RMSPE) of RMSPE =  1.32%. The concentrations of A$_2$ and B$_2$ as a function of time are also plotted in [ver-1ib_comparison_pressure].

!media comparison_ver-1ib.py
       image_name=ver-1ib_comparison_pressure.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1ib_comparison_pressure
       caption=Comparison of concentration of AB as a function of time calculated through TMAP8 and analytically for the solution in ratedep conditions when A$_2$ and B$_2$ have unequal pressures [!citep](ambrosek2008verification).

## Input files

!style halign=left
The input file for this case can be obtained by updating the initial pressure for B$_2$ in [!file](/ver-1ia.i), which is the approach used to create tests in TMAP8 at [!file](/ver-1ib/tests).

!bibtex bibliography
