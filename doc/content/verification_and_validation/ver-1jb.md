# ver-1jb

Two verification problems, [ver-1ja](ver-1ja.md) and ver-1jb, demonstrate tritium decay, though any other isotope could have been chosen.
The first ([ver-1ja](ver-1ja.md)) models the simple decay of mobile species in a slab.
The second (ver-1jb) models the decay of trapped atoms in a similar slab but with a distributed trap concentration.
This page presents ver-1jb, based on the case published in the TMAP7 verification and validation suite [!citep](ambrosek2008verification).

# Radioactive Decay of Tritium in a Distributed Trap

## General Case Description

This verification case is an extension of[ver-1ja](ver-1ja.md), which tests radioactive decay capabilities of TMAP8 on their own.
In ver-1jb, tritium decay is coupled with trapping, which itself was verified in several TMAP8 verification cases including [ver-1d](ver-1d.md). This TMAP8 case is published in [!cite](Simon2027).
Similarly to [ver-1ja](ver-1ja.md), the model assumes pre-charging of an $l=1.5$-m-long slab (with an assumed width and thickness of 1 m) with tritium. Further complexity is added to the problem by introducing mobile tritium and trapping sites whose locations follow a normal distribution centered at the mid-plane of the slab with a standard deviation of $l/4$.
The peak atomic fraction of traps is $C_{trap} = 0.001$, and the trap energy is $E=4.2$ eV. The material density used to calculate the number of traps is based on tungsten and is defined as 6.34 $\times 10^{28}$ atoms/m$^3$. The traps are initially filled with trapped tritium to 50% of trap concentration. The case is illustrated in [ver-1jb_schematic].

!media figures/ver-1jb_schematic.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=ver-1jb_schematic
    caption=Schematic of the ver-1jb case: mobile and trapped tritium decay to helium in a slab with zero-flux boundaries.

The evolution of the mobile tritium, trapped tritium, and helium concentrations, i.e.,
$C_M$, $C_T$, and $C_{He}$, respectively, is governed by

\begin{equation}
    \label{eqn:diffusion_mobile}
    \frac{dC_M}{dt} = \nabla \cdot D_T \nabla C_M - f_{T/M} \left(\frac{dC_T}{dt} + k C_T \right) - k C_M,
\end{equation}
\begin{equation}
    \label{eqn:trapped_rate}
    \frac{dC_T}{dt} = \alpha_t  \frac {C_T^{empty} C_M } {(N f_{T/M})} - \alpha_r C_T - k C_T,
\end{equation}
and
\begin{equation}
    C_T^{empty} = C_{T0} N - f_{T/M} C_T,
\end{equation}
\begin{equation}
    \frac{d C_{He}}{dt} = k (C_M + C_T),
\end{equation}
where $t$ is the time in s, concentrations are in atoms/m$^3$,
$D_T$ is the tritium diffusivity in m$^2$/s,
$f_{T/M}$ is a user-defined numerical factor converting the magnitude of $C_T$ to be closer to $C_M$ for better numerical convergence,
$k= 0.693/t_{1/2}$ is the decay rate constant in 1/s, $t_{1/2} = 12.3232$ years is the half life of tritium decay to $^3$He,
$C_T^{empty}$ is the concentration of empty trapping sites,
$N$ is the host density,
$\alpha_t$ and $\alpha_r$ are the trapping and release rate coefficients, respectively,
and $C_{T0}$ is the fraction of host sites that can contribute to trapping.

The tritium diffusivity is defined as
\begin{equation}
    D_T = 1.58 \times 10^{-4} \exp \left(- \frac{308 \times 10^{3}}{RT}\right),
\end{equation}
where $R$ is the ideal gas constant in J/K/mol from [Physical Constants](utils/TMAP8PhysicalConstants.md) and $T=300$ K is the temperature of the domain.
The trapping frequency is defined as
\begin{equation}
    \alpha_t = 2.096 \times 10^{15} \exp \left(- \frac{308 \times 10^{3}}{RT}\right),
\end{equation}
and the release frequency is equal to
\begin{equation}
    \alpha_r = 1 \times 10^{13} \exp \left(- \frac{4.2}{k_bT}\right),
\end{equation}
where $k_b$ is the Boltzmann constant in eV/K from [Physical Constants](utils/TMAP8PhysicalConstants.md).

!alert warning title=TMAP8 uses different model parameters than TMAP7
$k$ is defined as $k= 0.693/t_{1/2}=1.78199 \times 10^{-9}$ 1/s instead of $1.78241 \times 10^{-9}$ 1/s to be fully consistent with the half-life value (assuming 365.25 days in a year).
Note also that TMAP7 uses a temperature of $T = 273$ K instead of $T = 300$ K.


We define two different initial conditions for the mobile tritium concentration $C_M^0$:

- $C_M^0 = 1$ atoms/m$^3$, which is much lower than the initial trapped tritium concentration. This case corresponds to the TMAP7 case in [!citep](ambrosek2008verification).
- $C_M^0 = 1 \times 10^{25}$ atoms/m$^3$, which makes it equivalent to the initial trapped tritium concentration. This new case demonstrates TMAP8's improved ability (over TMAP7) to model the decay, trapping, detrapping, and diffusion of tritium when the concentration of mobile tritium is non-negligible.

To limit the computational challenges related to the orders-of-magnitude difference in trapped and mobile tritium in the first case, we make the concentrations dimensionless by dividing them by $1 \times 10^{25}$ atoms/m$^3$ and setting $f_{T/M} = 1 \times 10^{25}$ (-). In the second case, when the concentrations are equivalent, $f_{T/M} = 1$ (-).

## Analytical Solution

In [!cite](ambrosek2008verification), the total inventory of T in atoms, $I_{tot} = I_M + I_T$ where $I_M$ and $I_T$ are the mobile and trapped tritium inventories, respectively, is given at any given time by

\begin{equation}
    I_{tot} = I_{tot}^0 \exp(-kt),
\end{equation}

where $I_{tot}^0 = I_M^0 + I_T^0$ atoms/m is the initial total inventory of tritium
($I_M^0$ and $I_T^0$ are the initial mobile and trapped tritium inventories, respectively).
Applying a mass balance over the system, the inventory of helium in atoms, $I_{He}$, is given by
\begin{equation}
    I_{He} = I_{tot}^0 \left[1- \exp(-kt) \right].
\end{equation}

### Results

#### With a small concentration of mobile tritium compared to trapped tritium

[ver-1jb_results_comparison_analytical_time_evolution_1] shows the TMAP8 predictions and how they compare to the analytical solution
for the tritium decay and associated growth of $^3$He in a distributed trap.
TMAP8 matches the analytical solution, with a root mean square percentage error
(RMSPE) of 0.82% and 0.20% for the $I_{tot}$ and $I_{He}$ concentration curves, respectively,
and can also provide the trapped and mobile tritium concentrations.

!media comparison_ver-1jb.py
       image_name=ver-1jb_comparison_analytical_time_evolution.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1jb_results_comparison_analytical_time_evolution_1
       caption=Comparison of TMAP8 predictions against the analytical solution for the tritium decay and associated growth of $^3$He in a distributed trap with a small concentration of mobile tritium compared to trapped tritium.

[ver-1jb_results_profile_1] shows the depth profile of the initial trapped atoms of tritium, the concentration of trapped atoms of
tritium after 45 years, and the distribution of $^3$He at the end of that time period across the distributed trapping sites as predicted by TMAP8. The concentration of mobile tritium remains very low.

Note that because $^3$He is given a null diffusivity in this verification problem, the shape of the $^3$He concentration does not broaden.
This could be easily implemented with existing TMAP8 diffusive capabilities, as was shown in many other TMAP8 cases,
including [ver-1d](ver-1d.md).

!media comparison_ver-1jb.py
       image_name=ver-1jb_profile.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1jb_results_profile_1
       caption=Concentration profiles of initially trapped tritium that decayed to $^3$He over 45 years with a small concentration of mobile tritium compared to trapped tritium.

#### With equivalent mobile and trapped tritium initial concentrations

[ver-1jb_results_comparison_analytical_time_evolution_2] and [ver-1jb_results_profile_2] show the results of the simulations when the initial concentrations of mobile and trapped tritium are equivalent.
[ver-1jb_results_comparison_analytical_time_evolution_2] shows TMAP8's time predictions of the inventories and how they compare to the analytical solution. The RMSPE values are as low as in the previous case.

!media comparison_ver-1jb.py
       image_name=ver-1jb_equivalent_concentrations_comparison_analytical_time_evolution.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1jb_results_comparison_analytical_time_evolution_2
       caption=Comparison of TMAP8 predictions against the analytical solution for the tritium decay and associated growth of $^3$He in a distributed trap with equivalent initial concentrations of mobile and trapped tritium.

[ver-1jb_results_profile_2] shows the depth profile of the initial trapped atoms of tritium, the concentration of mobile and trapped atoms of
tritium after 45 years, and the distribution of $^3$He at the end of that time period across the distributed trapping sites as predicted by TMAP8.

!media comparison_ver-1jb.py
       image_name=ver-1jb_equivalent_concentrations_profile.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1jb_results_profile_2
       caption=Concentration profiles of initially trapped tritium that decayed to $^3$He over 45 years with equivalent initial concentrations of mobile and trapped tritium.

### Input file

The input file for this case can be found at [!file](/ver-1jb.i), which is also used as test in TMAP8 at [!file](/ver-1jb/tests). The case with equivalent mobile and trapped tritium initial concentrations was based on [!file](/ver-1jb.i) with slight modifications made in [!file](/ver-1jb/tests) to adjust the initial mobile tritium concentration.

!bibtex bibliography

