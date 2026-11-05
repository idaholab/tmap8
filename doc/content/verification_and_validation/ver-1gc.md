# ver-1gc

# Series Chemical Reactions


## Problem set up

This verification problem is taken from [!cite](ambrosek2008verification) and builds on the capabilities verified in [ver-1g](ver-1g.md) for simple chemical reactions.
This case is simulated in [!file](/ver-1gc.i). This TMAP8 case is published in [!cite](Simon2027).

This problem models a set of chemical reactions in series with three species: $A$, $B$, and $C$.
The system was configured so that the enclosure initially contained only species $A$.
At time $t \geq 0$ s, the reactions were allowed to proceed.
The reactions that were modeled are

\begin{equation} \label{eq:chemical_reaction}
A \xrightarrow{\mathit{k_1}} B \xrightarrow{\mathit{k_2}} C,
\end{equation}
with $k_1$ and $k_2$ as the reaction rates. The series of reactions is illustrated in [ver-1gc_schematic].

!media figures/ver-1gc_schematic.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=ver-1gc_schematic
    caption=Schematic of the ver-1gc case: species A converts to B, which converts to C, in a well-mixed enclosure initially containing only A.

The concentration of each species is therefore described as
\begin{equation} \label{eq:chemical_reaction_reaction_A}
\frac{dc_A}{dt} = - k_1 c_A,
\end{equation}
\begin{equation} \label{eq:chemical_reaction_reaction_B}
\frac{dc_B}{dt} = k_1 c_A - k_2 c_B,
\end{equation}
\begin{equation} \label{eq:chemical_reaction_reaction_C}
\frac{dc_C}{dt} = k_2 c_B,
\end{equation}
with $c_i$ as the concentration of species $i$.


## Analytical solution

[!cite](Fogler1999) provides the analytical equations for the time evolution of the concentrations of $A$ and $B$ as
\begin{equation} \label{eq:chemical_reaction_solution_A}
c_A(t) = c_{A0} \exp\left( -k_1 t\right),
\end{equation}
and
\begin{equation} \label{eq:chemical_reaction_solution_B}
c_B(t) = k_1 c_{A0} \frac{\exp\left( -k_1 t\right) - \exp\left( -k_2 t\right)}{k_2-k_1},
\end{equation}
where $t$ is the time in s, $c_{A0} = 2.415 \times 10^{14}$ atoms/m$^3$ is the initial concentration of species $A$, $k_1 = 0.0125$ s$^{-1}$, and $k_2 = 0.0025$ s$^{-1}$.


The concentration of $C$ was found by applying a mass balance over the system in [!cite](ambrosek2008verification). From the
stoichiometry of this reaction,
\begin{equation} \label{eq:chemical_reaction_solution_C}
c_C(t) = c_{A0} - c_A(t) - c_B(t).
\end{equation}
The time evolution of the species concentrations from the analytical solution is provided in [ver-1gc_comparison_diff_conc].

## Results and comparison against analytical solution

The comparison of TMAP8 results against the analytical solution is shown in [ver-1gc_comparison_diff_conc]. The match between TMAP8's predictions and the analytical solution is satisfactory, with root mean square percentage errors (RMSPE) of RMSPE = 4.78 % for species $A$, RMSPE = 3.20 % for species $B$, and RMSPE = 0.38 % for species $C$. The larger values of RMSPE for species $A$ and $B$ are due to the small average values of these concentrations over time, and do not reflect on the accuracy of the TMAP8 solve itself.

!media comparison_ver-1gc.py
       image_name=ver-1gc_comparison_diff_conc.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1gc_comparison_diff_conc
       caption=Comparison of partial pressures of species in a series reaction predicted by TMAP8 and provided by the analytical solution. The RMSPE is the root mean square percent error between the analytical solution and TMAP8 predictions.

## Input files

!style halign=left
The input file for this case can be found at [!file](/ver-1gc.i), which is also used as test in TMAP8 at [!file](/ver-1gc/tests).

!bibtex bibliography
