# ver-1ie

# Species Equilibration Problem in Lawdep Conditions with Equal Starting Pressures

!alert tip title=TMAP8 supports different surface reaction models
The current case uses what TMAP7 called the `lawdep` model.
The [theory_manual.md] page describes the `lawdep` model and other surface models.

## General Case Description

This verification problem is taken from [!cite](ambrosek2008verification) and builds on [ver-1ia](ver-1ia.md). The configuration and modeling parameters are similar to [ver-1ia](ver-1ia.md), except that, in the current case, the reaction is in lawdep conditions. The case is simulated in [!file](/ver-1ie.i).

The problem considers the reaction between two isotopic species, A$_2$ and B$_2$, on a surface in lawdep conditions. The reaction between AB, A$_2$, and B$_2$ is the same as in [ver-1ia](ver-1ia.md). Therefore, the partial pressure of AB in equilibrium depends on the initial partial pressures of A$_2$ and B$_2$:

\begin{equation}
\label{eq:lawdep:p_AB_equilibrium}
P_{AB}^{eq} = \frac{2 P_{A_2}^0 P_{B_2}^0}{P_{A_2}^0 + P_{B_2}^0}.
\end{equation}

Just as in [ver-1ia](ver-1ia.md), we solve the net current of AB molecules from the surface to the enclosure with

\begin{equation}
\label{eq:lawdep:equation_p_ab}
\frac{d P_{AB}}{dt} = \frac{S k_B T}{V} (2 K_r C_A C_B - K_d P_{AB}),
\end{equation}

where $t$ is the time, $S$ is the surface area, $k_B$ is the Boltzmann constant, $T$ is the temperature, $V$ is the volume in the enclosure, $K_r$ and $K_d$ are the recombination and dissociation coefficients, and $C_A$ and $C_B$ are the concentration of atoms from A$_2$ and B$_2$ on the reactive surface, respectively. In lawdep diffusion boundary conditions, the concentrations of A$_2$ and B$_2$ are always fixed relative to the partial pressures in the gas over the surface. When heteronuclear species formation is involved, TMAP8 uses logic similar to that used in the ratedep and surfdep condition for the arrival rate of gas atoms to the surface. However, there are no barriers to adsorption or release, and conversion is assumed to take place instantaneously. Any gas that does not diffuse away is immediately released from the surface. Therefore, the concentrations of A$_2$ and B$_2$ from Sieverts' law are given by

\begin{equation}
\label{eq:lawdep:p_ca_relation}
C_A = K_s \sqrt{P_{A_2}},
\end{equation}

and

\begin{equation}
\label{eq:lawdep:p_cb_relation}
C_B = K_s \sqrt{P_{B_2}},
\end{equation}

where $K_s$ is Sieverts’ solubility. Because A$_2$ and B$_2$ are isotopic variants, $K_s$ is the same for each homonuclear species. The relationship between $K_s$, $K_r$, and $K_d$ is given by

\begin{equation}
\label{eq:lawdep:k_relation}
K_d = {K_s}^2 K_r.
\end{equation}

This case uses equal starting pressures of $1 \times 10^{4}$ Pa of A$_2$ and B$_2$ and no AB. $K_d$ is specified to be $1.858 \times 10^{24}/\sqrt{T}$ atom/m$^2$/s/Pa. $K_s$ is specified to be $1 \times 10^{24}$ atom/m$^3$/Pa$^{0.5}$, the temperature is 1000 K, the surface area for reaction is 0.05 m $\times$ 0.05 m square, and the enclosure volume is 1 m$^3$.


## Analytical solution

After combining [eq:lawdep:p_ca_relation] and [eq:lawdep:p_cb_relation], [eq:lawdep:equation_p_ab] becomes

\begin{equation}
\label{eq:lawdep:equation_p_ab_final}
\frac{d P_{AB}}{dt} = \frac{S k_B T K_d}{V} \left(2 \sqrt{P^0_{A_2} - \frac{P_{AB}}{2}} \sqrt{P^0_{B_2} - \frac{P_{AB}}{2}} - P_{AB} \right).
\end{equation}

This is a nonlinear function, but it has a special solution when $P^0_{A_2} = P^0_{B_2}$, which is true in the current case. Thus, the analytical solution for the partial pressure of AB is given by

\begin{equation}
\label{eq:lawdep:analytical_solution}
P_{AB}  = P_{A_2}^0 \left(1 - \exp \left( -\frac{ 2 S K_d k_B T}{V} t \right)\right).
\end{equation}

## Results

A comparison of the AB concentration as a function of time is plotted in [ver-1ie_comparison_pressure]. The TMAP8 calculations are found to be in good agreement with the analytical solution, with a root mean square percentage error (RMSPE) of RMSPE =  0.36%. The concentrations of A$_2$ and B$_2$ as a function of time are also plotted in [ver-1ie_comparison_pressure].

!media comparison_ver-1ie.py
       image_name=ver-1ie_comparison_pressure.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1ie_comparison_pressure
       caption=Comparison of AB concentration as a function of time calculated through TMAP8 and analytically for the solution in lawdep conditions when A$_2$ and B$_2$ have equal pressures [!citep](ambrosek2008verification). As expected, the partial pressures for $A_2$ and $B_2$ overlap.

## Input files

!style halign=left
The input file for this case can be found at [!file](/ver-1ie.i), which is also used as tests in TMAP8 at [!file](/ver-1ie/tests).

!bibtex bibliography
