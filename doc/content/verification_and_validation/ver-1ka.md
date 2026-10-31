# ver-1ka

# Simple Volumetric Source

## General Case Description

This problem involves two enclosures connected by a diffusive membrane that follows Sieverts' law for diffusion. Both enclosures contain hydrogen (H$_2$), tritium (T$_2$), and tritium gas (HT). In the first enclosure, there is an initial inventory of only hydrogen (H$_2$) along with a constant volumetric source rate of tritium (T$_2$). The second enclosure starts out empty. The system of two enclosures is illustrated in [ver-1ka_schematic].

!media figures/ver-1k_schematic.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=ver-1ka_schematic
    caption=Schematic of the ver-1ka case (the same configuration is used for ver-1ka to ver-1kd): two enclosures separated by a membrane, with T$_2$, H$_2$, and HT in each enclosure.

## Case Set Up

This verification problem is taken from [!cite](ambrosek2008verification). This TMAP8 case is published in [!cite](Simon2027).
The rise in pressure of T$_2$ molecules in the first enclosure can be monitored by not enabling T$_2$ molecules to traverse the membrane between the two enclosures (no tritium flux). Consequently, the rate of pressure increase in the first enclosure can be expressed as:

\begin{equation} \label{eq:source_term}
\frac{dP_{T_2}}{dt} = \frac{S}{V} kT,
\end{equation}

where $S$ represents the volumetric T$_2$ source rate, $V$ is the volume of the enclosure, $k$ is the Boltzmann constant, and $T$ is the temperature of the enclosure.
In this case, $S$ is set to 10$^{20}$ molecules/m$^{3}$/s, $V = 1$ m$^3$, and the temperature of the enclosure is constant at $T = 500$ K.

## Analytical Solution

In [!cite](ambrosek2008verification), the analytical solution for [eq:source_term] is simply

\begin{equation}
P_{T_2}(t) = \frac{S}{V} kT t.
\end{equation}

## Results

A comparison of the TMAP8 results and the analytical solution is shown in
[ver-1ka_comparison_time] as a function of time. The TMAP8 code predictions match very well with the analytical solution with a root mean squared percentage error of RMSPE $= 0.00$ %.

!media comparison_ver-1ka.py
       image_name=ver-1ka_comparison_time.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1ka_comparison_time
       caption=Comparison of T$_2$ partial pressure in an enclosure with no loss pathways as a function of time, calculated through TMAP8 and analytically. TMAP8 matches the analytical solution.

## Input files

!style halign=left
The input file for this case can be found at [!file](/ver-1ka.i), which is also used as tests in TMAP8 at [!file](/ver-1ka/tests).

!bibtex bibliography
