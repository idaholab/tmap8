# ver-1kd

# Sieverts’ Law Boundaries with Chemical Reactions and Volumetric Source

## General Case Description

Two enclosures are separated by a membrane that allows diffusion according to Sieverts' law and chemical reactions, with a volumetric source in Enclosure 1. Enclosure 2 has twice the volume of Enclosure 1. The system of two enclosures is illustrated in [ver-1kd_schematic].

!media figures/ver-1k_schematic.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=ver-1kd_schematic
    caption=Schematic of the ver-1kd case (the same configuration is used for ver-1ka to ver-1kd): two enclosures separated by a membrane, with T$_2$, H$_2$, and HT in each enclosure.

## Case Set Up

This verification problem is taken from [!cite](ambrosek2008verification). This TMAP8 case is published in [!cite](Simon2027).

This setup describes a diffusion system in which tritium T$_2$, dihydrogen H$_2$ and HT are modeled across a one-dimensional domain split into two enclosures. Compared to the [ver-1kc-2](ver-1kc-2.md) case, we now incorporate a T$_2$ tritium volumetric source in Enclosure 1. The volumetric source rate is set to $S_{\text{T}_2} = 10^{23}/N_A$ mol/m$^3$/s with $N_A = 6.02214076 \times 10^{23}$ 1/mol.
The total system length is $2.5 \times 10^{-4}$ m, divided into 100 segments. The system operates at a constant temperature of 500 Kelvin. Initial tritium T$_2$ and dihydrogen H$_2$ pressures are specified as $10^{5}$ Pa for Enclosure 1 and $10^{-10}$ Pa for Enclosure 2. Initially, there is no HT in either enclosure.

The reaction between the species is described as

\begin{equation}
\text{H}_2 + \text{T}_2 \leftrightarrow 2\text{HT}
\end{equation}

The kinematic evolutions of the species are given by

\begin{equation}
\frac{d C_{\text{HT}}}{dt} = 2K_1 C_{\text{H}_2} C_{\text{T}_2} - K_2 C_{\text{HT}}^2
\end{equation}

\begin{equation}
\frac{d C_{\text{H}_2}}{dt} = -K_1 C_{\text{H}_2} C_{\text{T}_2} + \frac{1}{2} K_2 C_{\text{HT}}^2
\end{equation}

\begin{equation}
\frac{d C_{\text{T}_2}}{dt} = -K_1 c_{\text{H}_2} C_{\text{T}_2} + \frac{1}{2} K_2 C_{\text{HT}}^2
\end{equation}

where $K_1$ and $K_2$ represent the reaction rates for the forward and reverse reactions, respectively.

At equilibrium, the time derivatives are zero

\begin{equation}
2K_1 C_{\text{H}_2} C_{\text{T}_2} - K_2 C_{\text{HT}}^2 = 0
\end{equation}

From this, we can derive the same equilibrium condition as used in TMAP7:

\begin{equation}
P_{\text{HT}} = \eta \sqrt{P_{\text{H}_2} P_{\text{T}_2}}
\end{equation}

where the equilibrium constant $\eta$ is defined as

\begin{equation} \label{eq:eta}
\eta = \sqrt{\frac{2K_1}{K_2}}
\end{equation}

Similarly to TMAP7, the equilibrium constant $\eta$ has been set to a fixed value of $\eta = 2$.

The diffusion and generation processes for each species in the two enclosures can be expressed by

\begin{equation}
\frac{\partial C_1}{\partial t} = \nabla \cdot D \nabla C_1 + S_1,
\end{equation}
and
\begin{equation}
\frac{\partial C_2}{\partial t} = \nabla \cdot D \nabla C_2,
\end{equation}

where $C_1$ and $C_2$ represent the concentration fields in Enclosures 1 and 2, respectively, $t$ is the time, $D$ denotes the diffusivity, $S$ is the volumetric source rate, $V_1$ is the volume of Enclosure 1, $k$ is the Boltzmann constant, and $T$ is the temperature.
Note that the diffusivity may vary across different species and enclosures. However, in this case, it is assumed to be identical for all mobile species and enclosures.

The concentration in Enclosure 1 is related to the partial pressure and concentration in Enclosure 2 via the interface sorption law:

\begin{equation}
C_1 = K P_2^n = K \left( C_2 RT \right)^n
\end{equation}

where $R$ is the ideal gas constant in J/mol/K, $T$ is the temperature in K, $K$ is the solubility, and $n$ is the exponent of the sorption law. For Sieverts' law, $n=0.5$.

## Results

We assume that $K = 10/\sqrt{RT}$, which is expected to result in $C_1 = 10 \sqrt{C_2}$ at equilibrium.

As illustrated in [ver-1kd_comparison_time_k10], since the chemical reactions occur immediately, an initial quantity of HT is present in Enclosure 1, while T$_2$ and H$_2$ initially drop to half their original amounts.

The pressures of T$_2$ and H$_2$ in Enclosure 1 decrease due to diffusion into Enclosure 2. The constant flow rate of the T$_2$ source slows down the pressure drop of T$_2$ in Enclosure 2. Moreover, the volumetric source increases the amount of T$_2$ in Enclosure 1, thereby enhancing its chemical reactions with H$_2$. Consequently, in Enclosure 1, H$_2$ pressure gradually decreases over time, while HT pressure rises.

Similarly, in Enclosure 2, the pressures of T$_2$ and H$_2$ increase, with the rise being more pronounced for T$_2$ due to the continuous supply from the source. As a result, more H$_2$ reacts with T$_2$, further contributing to the increase in HT pressure.

For verification purposes, it is crucial to ensure that the chemical equilibrium between HT, T$_2$, and H$_2$ is achieved. This can be verified in both enclosures by examining the ratio between $P_{\text{HT}}$ and $\sqrt{P_{\text{H}_2} P_{\text{T}_2}}$, which must equal $\eta=2$.
As shown in [ver-1kd_equilibrium_constant_k10], this ratio approaches $\eta=2$ for both enclosures at equilibrium. To reach this equilibrium, the ratio of $K_1$ and $K_2$ must respect [eq:eta]. The values of $K_1$ and $K_2$ must also be large enough to ensure that the kinetics of chemical reactions are faster than diffusion or surface permeation to be closer to the equilibrium assumption imposed in TMAP7. Here, the equilibrium in Enclosure 1 is achieved rapidly. Increasing $K_1$ and $K_2$ would also enable a quicker attainment of equilibrium in Enclosure 2. However, using very high values for $K_1$ and $K_2$ would lead to an unnecessary increase in computational costs.

The concentration ratios for T$_2$, H$_2$, and HT between enclosures 1 and 2, shown in [ver-1kd_concentration_ratio_T2_k10], [ver-1kd_concentration_ratio_H2_k10], and [ver-1kd_concentration_ratio_HT_k10], demonstrate that the results obtained with TMAP8 are consistent with the analytical results derived from the sorption law for $K \sqrt{RT} = 10$.

!media comparison_ver-1kd.py
       image_name=ver-1kd_comparison_time_k10.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1kd_comparison_time_k10
       caption=Evolution of species concentration over time governed by Sieverts' law with $K = 10/\sqrt{RT}$ and $\eta = \sqrt{2K_1/K_2}$.

!media comparison_ver-1kd.py
       image_name=ver-1kd_equilibrium_constant_k10.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1kd_equilibrium_constant_k10
       caption=Equilibrium constant as a function of time for $\eta = \sqrt{2K_1/K_2}=2$.

!media comparison_ver-1kd.py
       image_name=ver-1kd_concentration_ratio_T2_k10.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1kd_concentration_ratio_T2_k10
       caption=T$_2$ concentration ratio between Enclosures 1 and 2 at the interface for $K = 10/\sqrt{RT}$ and $\eta = \sqrt{2K_1/K_2}$. This verifies TMAP8's ability to apply Sieverts' law across the interface.

!media comparison_ver-1kd.py
       image_name=ver-1kd_concentration_ratio_H2_k10.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1kd_concentration_ratio_H2_k10
       caption=H$_2$ concentration ratio between Enclosures 1 and 2 at the interface for $K = 10/\sqrt{RT}$ and $\eta = \sqrt{2K_1/K_2}$. This verifies TMAP8's ability to apply Sieverts' law across the interface.

!media comparison_ver-1kd.py
       image_name=ver-1kd_concentration_ratio_HT_k10.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1kd_concentration_ratio_HT_k10
       caption=HT concentration ratio between Enclosures 1 and 2 at the interface for $K = 10/\sqrt{RT}$ and $\eta = \sqrt{2K_1/K_2}$. This verifies TMAP8's ability to apply Sieverts' law across the interface.

## Input files

!style halign=left
The input file for this case can be found at [!file](/ver-1kd.i).

!bibtex bibliography
