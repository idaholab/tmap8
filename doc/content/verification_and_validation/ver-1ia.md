# ver-1ia

# Species Equilibration Problem in Ratedep Conditions with Equal Starting Pressures

!alert tip title=TMAP8 supports different surface reaction models
The current case uses what TMAP7 called the `ratedep` model.
The [theory_manual.md] page describes the `ratedep` model and other surface models.

## General Case Description

This verification problem is taken from [!cite](ambrosek2008verification). This TMAP8 case is published in [!cite](Simon2027).
When two species react on a surface to form a third, it is possible to predict the rate at which equilibration between the species will occur.
For example, the reaction between two isotopic species, A$_2$ and B$_2$, is described as

\begin{equation}
\label{eq:ratedep:reaction}
\frac{1}{2} A_2 + \frac{1}{2} B_2 \rightleftharpoons AB,
\end{equation}

and the partial pressure of A$_2$, B$_2$, and AB in equilibrium of the reaction is defined by

\begin{equation}
\label{eq:ratedep:reaction_equilibrium_pressure}
\frac{P_{AB}}{\sqrt{P_{A_2}} \sqrt{P_{B_2}}} = K_{eq},
\end{equation}

where $P_i$ is the partial pressure of corresponding gas $i$ and $K_{eq}$ is the equilibrium constant. The surface reaction considered is illustrated in [ver-1ia_schematic].

!media figures/ver-1i_schematic.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=ver-1ia_schematic
    caption=Schematic of the ver-1ia case (the same configuration is used for ver-1ia to ver-1if): gas species A$_2$ and B$_2$ in a gas enclosure react on a reactive surface to form AB.

Assuming that the molecular species have the same mass and chemical properties such that there is no enthalpy change associated with this reaction and only configurational entropy $s_f$ is driving the reaction, then

\begin{equation}
\label{eq:ratedep:reaction_rate}
K_{eq} = \exp\left( - \frac{\Delta G_f}{RT} \right) = \exp\left( - \frac{-T \Delta s_f}{RT} \right) = \exp\left( - \frac{-RT \ln(2)}{RT} \right) = 2,
\end{equation}

where $G_f$ is the Gibbs free energy, $R$ is the ideal gas constant, and $T$ is the temperature.

Therefore, the partial pressure of AB in equilibrium depends on initial partial pressure of A$_2$ and B$_2$:

\begin{equation}
\label{eq:ratedep:p_AB_equilibrium}
P_{AB}^{eq} = \frac{2 P_{A_2}^0 P_{B_2}^0}{P_{A_2}^0 + P_{B_2}^0}.
\end{equation}

At equilibrium, the surface concentrations of A$_2$ (i.e., $C_A$) and B$_2$ (i.e., $C_B$) from Sieverts' law are given by

\begin{equation}
\label{eq:ratedep:p_ca_relation}
C_A = K_s \sqrt{P_{A_2}},
\end{equation}

and

\begin{equation}
\label{eq:ratedep:p_cb_relation}
C_B = K_s \sqrt{P_{B_2}},
\end{equation}

where $K_s$ is Sieverts’ solubility. Because we are considering isotopic variants, $K_s$ will be the same for each homonuclear species. Under equilibrium conditions, we also expect

\begin{equation}
\label{eq:ratedep:equation_p_a2}
K_d P_{A_2} = K_r C_A^2,
\end{equation}

where $K_d$ is the dissociation coefficient and $K_r$ is the recombination coefficient. That leads to

\begin{equation}
\label{eq:ratedep:Kd_Kr_Ks}
K_d = K_s^2 K_r,
\end{equation}

Under `ratedep` conditions, equilibrium is not assumed, but the relationships between the coefficients are maintained. In particular, the recombination and dissociation coefficients are assumed to be independent of the surface species concentrations and gas partial pressures, respectively. If the species molecular masses and solubilities are assumed equal, the dissociation
coefficients for AB, A$_2$, and B$_2$ molecules should be identical. Because two different microscopic processes can produce AB (A jumping to find B and B jumping to find A) and only one (A finding A) can form A$_2$, and similarly for B$_2$, the recombination coefficient for AB should be twice the coefficient for homonuclear molecules. We solve the net current of AB molecules from the surface to the enclosure by

\begin{equation}
\label{eq:ratedep:equation_p_ab}
\frac{d P_{AB}}{dt} = \frac{S k_B T}{V} (2 K_r C_A C_B - K_d P_{AB}),
\end{equation}

where $t$ is the time, $S$ is the surface area, $k_B$ is the Boltzmann’s constant, $T$ is the temperature, and $V$ is the volume in the enclosure. If diffusion is small, the almost constant numbers of A and B atoms in the gas imply that $C_A$ and $C_B$ should have an almost constant value regardless of the isotopic species composition. The production of A$_2$ and B$_2$ in equilibration conditions is given by

\begin{equation}
\label{eq:ratedep:equal_c_a_c_b}
C_A C_B = \frac{K_d}{2 K_r} P_{AB}^{eq}.
\end{equation}

This case uses equal starting pressures of $1 \times 10^{4}$ Pa of A$_2$ and B$_2$ and no AB. $K_d$ is specified to be $1.858 \times 10^{24}/\sqrt{T}$ atom/m$^2$/s/Pa, $K_r$ is specified to be $5.88 \times 10^{-26}$ m$^4$/atom/s, the temperature is 1000 K, the surface area for reaction is 0.05 m $\times$ 0.05 m square, and the enclosure volume is 1 m$^3$.


## Analytical solution

[!cite](ambrosek2008verification) provides the analytical equation for the partial pressure of AB when the conversion rate at the surface is high as

\begin{equation}
\label{eq:ratedep:analytical_solution}
P_{AB}  = \frac{2 P_{A_2}^0 P_{B_2}^0}{P_{A_2}^0 + P_{B_2}^0} \left(1 - \exp \left( -\frac{S K_d k_B T}{V} t \right)\right).
\end{equation}

## Results

A comparison of the concentration of AB as a function of time is plotted in [ver-1ia_comparison_pressure]. The TMAP8 calculations are found to be in good agreement with the analytical solution, with a root mean square percentage error (RMSPE) of RMSPE = 0.13 %. The concentrations of A$_2$ and B$_2$ as a function of time are also plotted in [ver-1ia_comparison_pressure].

!media comparison_ver-1ia.py
       image_name=ver-1ia_comparison_pressure.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1ia_comparison_pressure
       caption=Comparison of concentration of AB as a function of time calculated through TMAP8 and analytically for the solution in the `ratedep` condition when A and B have equal pressures [!citep](ambrosek2008verification). As expected, the partial pressures for $A_2$ and $B_2$ overlap.

## Input files

!style halign=left
The input file for this case can be found at [!file](/ver-1ia.i), which is also used as tests in TMAP8 at [!file](/ver-1ia/tests).

!bibtex bibliography
