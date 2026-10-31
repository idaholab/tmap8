# ver-1kb

# Henry’s Law Boundaries with No Volumetric Source

## General Case Description

Two enclosures are separated by a membrane that allows diffusion according to Henry’s law, with no volumetric source present. Enclosure 2 has twice the volume of Enclosure 1. The system of two enclosures is illustrated in [ver-1kb_schematic].

!media figures/ver-1k_schematic.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=ver-1kb_schematic
    caption=Schematic of the ver-1kb case (the same configuration is used for ver-1ka to ver-1kd): two enclosures separated by a membrane, with T$_2$, H$_2$, and HT in each enclosure.

## Case Set Up

This verification problem is taken from [!cite](ambrosek2008verification). This TMAP8 case is published in [!cite](Simon2027).

This setup describes a diffusion system in which tritium T$_2$ is modeled across a one-dimensional domain split into two enclosures. The total system length is $2.5 \times 10^{-4}$ m, divided into 100 segments. The system operates at a constant temperature of 500 K. Initial tritium pressures are specified as $10^{5}$ Pa for Enclosure 1 and $10^{-10}$ Pa for Enclosure 2.

Over time, the pressures of T$_2$, which diffuses across the membrane in accordance with Henry’s law, will gradually equilibrate between the two enclosures.

The diffusion process in each of the two enclosures can be described by

\begin{equation}
\frac{\partial C_1}{\partial t} = \nabla \cdot D \nabla C_1,
\end{equation}
and
\begin{equation}
\frac{\partial C_2}{\partial t} = \nabla \cdot D \nabla C_2,
\end{equation}

where $C_1$ and $C_2$ represent the concentration fields in Enclosures 1 and 2 respectively, $t$ is the time, and $D$ denotes the diffusivity.

The concentration in Enclosure 1 is related to the partial pressure and concentration in Enclosure 2 via the interface sorption law:

\begin{equation}
C_1 = K P_2^n = K \left( C_2 RT \right)^n
\end{equation}

where $R$ is the ideal gas constant in J/mol/K, $T$ is the temperature in K, $K$ is the solubility, and $n$ is the exponent of the sorption law. For Henry’s law, $n=1$.

## Results

Two subcases are considered. In the first subcase, we assume that $K=1/RT$ as is done in [!cite](ambrosek2008verification), which is expected to lead to $C_1 = C_2$ at equilibrium. In the second, $K=10/RT$, which is expected to lead to $C_1 = 10 C_2$. This second case is added to exercise TMAP8 in a case with a concentration jump.
In the first subcase, consistent with the results from TMAP7, the pressure evolution in both enclosures is shown in [ver-1kb_comparison_time] as a function of time. Both pressures find equilibrium and become equal, which is consistent with $C_1 = K (RT C_2)^n$ for $K=1/RT$ and $n=1$. The concentration ratio between Enclosures 1 and 2 in [ver-1kb_concentration_ratio] shows that the results obtained with TMAP8 are consistent with the analytical results derived from the sorption law for $K R T=1$. As shown in [ver-1kb_mass_conservation], mass is conserved between the two enclosures over time, with a variation in mass of only $1.0$ %. This variation in mass can be further minimized by refining the mesh (i.e., increasing the number of segments in the domain)

!media comparison_ver-1kb.py
       image_name=ver-1kb_comparison_time.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1kb_comparison_time
       caption=Equilibration of species pressures under Henry’s law for $K = 1/RT$.

!media comparison_ver-1kb.py
       image_name=ver-1kb_concentration_ratio.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1kb_concentration_ratio
       caption=Concentrations ratio between Enclosures 1 and 2 at the interface for $K = 1/RT$. This verifies TMAP8's ability to apply the sorption law across the interface without a concentration jump.

!media comparison_ver-1kb.py
       image_name=ver-1kb_mass_conservation.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1kb_mass_conservation
       caption=Total mass conservation across both enclosures over time for $K = 1/RT$.

In the second subcase, the sorption law with $K=10/RT$ does not lead to equal pressure in both enclosures. As illustrated in [ver-1kb_comparison_time_k10], the pressure jump maintains a ratio of $C_1/C_2 \approx 10$, which is consistent with the relationship $C_1 = K (RT C_2)^n$ for $K=10/RT$ and $n=1$. The concentration ratio between Enclosures 1 and 2 in [ver-1kb_concentration_ratio_k10] shows that the results obtained with TMAP8 are consistent with the analytical results derived from the sorption law for $K RT=10$. Additionally, [ver-1kb_mass_conservation_k10] verifies that mass is conserved between the two enclosures over time, with a variation in mass of only $0.25$ %. As in the previous case, this variation in mass can be further reduced by refining the mesh.

!media comparison_ver-1kb.py
       image_name=ver-1kb_comparison_time_k10.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1kb_comparison_time_k10
       caption=Pressure jump of species under Henry’s law for $K = 10/RT$.

!media comparison_ver-1kb.py
       image_name=ver-1kb_concentration_ratio_k10.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1kb_concentration_ratio_k10
       caption=Concentrations ratio between Enclosures 1 and 2 at the interface for $K = 10/RT$. This verifies TMAP8's ability to apply the sorption law across the interface with a concentration jump.

!media comparison_ver-1kb.py
       image_name=ver-1kb_mass_conservation_k10.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1kb_mass_conservation_k10
       caption=Total mass conservation across both enclosures over time for $K = 10/RT$.

!alert note title=A Comparison with TMAP7 Results: Impact of Diffusivity Variations on Kinetics
The kinetics observed in our results differ from those presented in TMAP7. We attribute this discrepancy to a variation in the diffusivity value used, which significantly affects the diffusion rate.

## Input files

!style halign=left
The input file for this case can be found at [!file](/ver-1kb.i), which is also used as tests in TMAP8 at [!file](/ver-1kb/tests).

!bibtex bibliography
