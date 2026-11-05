# ver-1id

# Species Equilibration Model in Surfdep Conditions with High Barrier Energy

!alert tip title=TMAP8 supports different surface reaction models
The current case uses what TMAP7 called the `surfdep` model.
The [theory_manual.md] page describes the `surfdep` model and other surface models.

## General Case Description

This verification problem is taken from [!cite](ambrosek2008verification) and builds on [ver-1ic](ver-1ic.md). This TMAP8 case is published in [!cite](Simon2027). The configuration and modeling parameters are the same as in [ver-1ic](ver-1ic.md), except that, in the current case, the reaction has a high barrier energy. The case is simulated in [!file](/ver-1ic.i), but $E_x$ is set to 0.20 eV instead of 0.05 eV. The surface reaction considered is illustrated in [ver-1id_schematic].

!media figures/ver-1i_schematic.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=ver-1id_schematic
    caption=Schematic of the ver-1id case (the same configuration is used for ver-1ia to ver-1if): gas species A$_2$ and B$_2$ in a gas enclosure react on a reactive surface to form AB.

## Analytical solution

[!cite](ambrosek2008verification) provides the analytical equation for the partial pressure of AB as

\begin{equation}
\label{eq:surfdep:analytical_solution}
P_{AB}  = \frac{2 P_{A_2}^0 P_{B_2}^0}{P_{A_2}^0 + P_{B_2}^0} \left(1 - \exp \left(- \frac{t}{\tau}\right)\right),
\end{equation}

where $\tau$ is defined as

\begin{equation}
\label{eq:surfdep:tau}
\tau = \frac{V (\hat{K_r} + \hat{K_b})}{S k_B T \hat{K_d} \hat{K_b}}.
\end{equation}

## Results

A comparison of the AB concentration as a function of time is plotted in [ver-1id_comparison_pressure]. The TMAP8 calculations are found to be in good agreement with the analytical solution, with a root mean square percentage error (RMSPE) of RMSPE =  0.19%. The concentrations of A$_2$ and B$_2$ as a function of time are also plotted in [ver-1id_comparison_pressure].

!media comparison_ver-1id.py
       image_name=ver-1id_comparison_pressure.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1id_comparison_pressure
       caption=Comparison of AB concentration as a function of time calculated through TMAP8 and analytically for the solution in surfdep conditions with high barrier energy [!citep](ambrosek2008verification). As expected, the partial pressures for $A_2$ and $B_2$ overlap.

## Input files

!style halign=left
The input file for this case can be obtained by updating the adsorption barrier energy $E_x$ in [!file](/ver-1ic.i), which is the approach used to create tests in TMAP8 at [!file](/ver-1id/tests).

!bibtex bibliography
