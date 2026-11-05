# ver-1ja

Two verification problems, ver-1ja and [ver-1jb](ver-1jb.md), demonstrate tritium decay, though any other isotope could have been chosen.
The first (ver-1ja) models the simple decay of mobile species in a slab.
The second ([ver-1jb](ver-1jb.md)) models the decay of trapped atoms in a similar slab but with a distributed trap concentration.
This page presents ver-1ja.

# Radioactive Decay of Mobile Tritium in a Slab

## General Case Description

!style halign=left
This verification case tests the first-order radioactive decay capabilities of TMAP8
and is based on the case published in the TMAP7 V&V suite [!citep](ambrosek2008verification). This TMAP8 case is published in [!cite](Simon2027).
The model assumes pre-charging of a slab with tritium.
The tritium (T) is uniformly distributed over the thickness of the slab with an initial concentration of $C_T^0 = 1.5 \times 10^{5}$ atoms/m$^3$.
The tritium decays to $^3\text{He}$ with a half-life of $t_{1/2} = 12.3232$ years.
The concentrations of the two species are calculated. The case is illustrated in [ver-1ja_schematic].

!media figures/ver-1ja_schematic.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=ver-1ja_schematic
    caption=Schematic of the ver-1ja case: tritium (T), uniformly distributed in a slab with zero-flux boundaries, decays to helium (He).

The evolution of the tritium and helium concentration, $C_T$ and $C_{He}$, respectively,
are governed by

\begin{equation}
    \frac{d C_T}{dt} = -k C_T,
\end{equation}
and
\begin{equation}
    \frac{d C_{He}}{dt} = k C_T,
\end{equation}
where $t$ is the time in seconds, concentrations are in atoms/m$^3$, and $k= 0.693/t_{1/2}$ is the decay rate constant in 1/s.

!alert warning title=TMAP8 uses different model parameters than TMAP7
The initial tritium concentration in TMAP7 was defined as $C_T^0 = 1.5$ atoms/m$^3$. To use more realistic values, TMAP8 uses $C_T^0 = 1.5 \times 10^{5}$ atoms/m$^3$.
Moreover, $k$ is defined as $k=0.693/t_{1/2} \approx 1.78199 \times 10^{-9}$ 1/s instead of $1.78241 \times 10^{-9}$ 1/s to be fully consistent with the half-life value (assuming 365.25 days in a year).

## Analytical Solution

!style halign=left
In [!cite](ambrosek2008verification), the concentration of T at any given time is given by

\begin{equation}
    C_T = C_T^0 \exp(-kt),
\end{equation}

where $t$ is the time in seconds and $C_T^0 = 1.5 \times 10^{5}$ atoms/m$^3$ is the initial tritium concentration.
Applying a mass balance over the system, the time evolution of helium concentration is given by
\begin{equation}
    C_{He} = C_T^0 \left[1- \exp(-kt) \right].
\end{equation}


### Results

!style halign=left
[ver-1ja_results] shows the TMAP8 predictions and how they compare to the analytical solution
for the tritium decay and associated growth of $^3\text{He}$ in a diffusion segment.
The TMAP8 predictions match the analytical solution, with root mean square percentage errors
(RMSPE) of 0.79% and 0.17% for the $C_T$ and $C_{He}$ concentration curves respectively.

!media comparison_ver-1ja.py
       image_name=ver-1ja_comparison_analytical.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1ja_results
       caption=Comparison of TMAP8 predictions against the analytical solution for the tritium decay and associated growth of $^3\text{He}$ in a diffusion segment. The RMSPE is very low for both species.

### Input file

!style halign=left
The input file for this case can be found at [!file](/ver-1ja.i), which is also used as test in TMAP8 at [!file](/ver-1ja/tests).

!bibtex bibliography
