# ver-1kc-1

# Sieverts’ Law Boundaries with No Volumetric Source

## General Case Description

Two enclosures are separated by a membrane that allows diffusion according to Sieverts' law, with no volumetric source present. Enclosure 2 has twice the volume of Enclosure 1. The system of two enclosures is illustrated in [ver-1kc-1_schematic].

!media figures/ver-1k_schematic.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=ver-1kc-1_schematic
    caption=Schematic of the ver-1kc-1 case (the same configuration is used for ver-1ka to ver-1kd): two enclosures separated by a membrane, with T$_2$, H$_2$, and HT in each enclosure.

## Case Set Up

This verification problem is taken from [!cite](ambrosek2008verification). This TMAP8 case is published in [!cite](Simon2027).

This setup describes a diffusion system in which tritium T$_2$ is modeled across a one-dimensional domain split into two enclosures. The total system length is $2.5 \times 10^{-4}$ m, divided into 100 segments. The system operates at a constant temperature of 500 Kelvin. Initial tritium pressures are specified as $10^{5}$ Pa for Enclosure 1 and $10^{-10}$ Pa for Enclosure 2.

The diffusion process in each of the two enclosures can be described by

\begin{equation}
\frac{\partial C_1}{\partial t} = \nabla \cdot D \nabla C_1,
\end{equation}
and
\begin{equation}
\frac{\partial C_2}{\partial t} = \nabla \cdot D \nabla C_2,
\end{equation}

where $C_1$ and $C_2$ represent the concentration fields in Enclosures 1 and 2 respectively, $t$ is the time, and $D$ denotes the diffusivity.

This case is similar to the [ver-1kb](ver-1kb.md) case, with the key difference being that sorption here follows Sieverts' law instead of Henry's law.
The concentration in Enclosure 1 is related to the partial pressure and concentration in Enclosure 2 via the interface sorption law:

\begin{equation}
C_1 = K P_2^n = K \left( C_2 RT \right)^n
\end{equation}

where $R$ is the ideal gas constant in J/mol/K, $T$ is the temperature in K, $K$ is the solubility, and $n$ is the exponent of the sorption law. For Sieverts' law, $n=0.5$.

## Results

We assume that $K = \frac{10}{\sqrt{RT}}$, which is expected to lead to $C_1 = 10 \sqrt{C_2}$ at equilibrium.
As illustrated in [ver-1kc-1_comparison_time_k10], the pressure jump maintains a ratio of $\frac{C_1}{\sqrt{C_2}} \approx 10$, which is consistent with the relationship $C_1 = K (RT C_2)^n$ for $K = \frac{10}{\sqrt{RT}}$ and $n=0.5$. The concentration ratio between Enclosures 1 and 2 in [ver-1kc-1_concentration_ratio_k10] shows that the results obtained with TMAP8 are consistent with the analytical results derived from the sorption law for $K \sqrt{RT}=10$. As shown in [ver-1kc-1_mass_conservation_k10], mass is conserved between the two enclosures over time, with a variation in mass of only $0.4$ %. This variation in mass can be further minimized by refining the mesh (i.e., increasing the number of segments in the domain).

!media comparison_ver-1kc-1.py
       image_name=ver-1kc-1_comparison_time_k10.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1kc-1_comparison_time_k10
       caption=Evolution of species concentration over time governed by Sieverts' law with $K = \frac{10}{\sqrt{RT}}$.

!media comparison_ver-1kc-1.py
       image_name=ver-1kc-1_concentration_ratio_k10.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1kc-1_concentration_ratio_k10
       caption=Concentrations ratio between Enclosures 1 and 2 at the interface for $K = \frac{10}{\sqrt{RT}}$. This verifies TMAP8's ability to apply Sieverts' law across the interface.

!media comparison_ver-1kc-1.py
       image_name=ver-1kc-1_mass_conservation_k10.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1kc-1_mass_conservation_k10
       caption=Total mass conservation across both enclosures over time for $K = \frac{10}{\sqrt{RT}}$.

## Input files

!style halign=left
The input file for this case can be found at [!file](/ver-1kc-1.i). To limit the computational costs of the test cases, the tests run a version of the file with a coarser mesh and less number of time steps. More information about the changes can be found in the test specification file for this case [!file](/ver-1kc-1/tests).

!bibtex bibliography
