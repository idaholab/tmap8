# ver-1n

# Diffusion Problem under Applied Voltage with Constant Source Boundary Condition

## Case Description

This verification case considers one-dimensional deuterium diffusion under an applied voltage through a semi-infinite proton-conducting ceramic (PCC) layer with a constant source at one boundary. PCC materials selectively transport hydrogen isotopes (protium, deuterium, and tritium) at temperatures around 600 $^\circ$C through ionic conduction of hydroxyl defects. This proton-hopping mechanism can be substantially enhanced by applying an electric field, enabling active pumping of hydrogen isotopes across the membrane, even without pressure gradients.

The purpose of this case is to isolate and verify the voltage-assisted migration term in the Nernst--Planck equation. Trapping is excluded, and the Sieverts's boundary conditions are imposed on upstream and downstream surfaces to simplified the comparison with the analytical solution.

## Case Set Up

This verification case models a one-dimensional PCC membrane with a thickness of 10 mm.
The upstream deuterium pressure is held constant, and the corresponding boundary concentration is described by Sieverts' law,

\begin{equation}
\label{eq:p_c_relation}
C_0 = K_s \sqrt{P},
\end{equation}

where $C_0$ is the concentration on the upstream side, $K_s$ is the Sieverts' solubility, and $P$ is the upstream deuterium pressure. The downstream concentration is set to 0.

In the PCC membrane, deuterium occupy charged hydroxyl defects. For the voltage-assisted transport verification, the transported deuterium species is treated as a positively charged mobile species with charge number $z=1$. The one-dimensional Nernst--Planck governing equation is

\begin{equation}
\label{eq:Nernst_Plank}
\frac{\partial C}{\partial t}
=
\frac{\partial}{\partial x}\left(D\frac{\partial C}{\partial x}\right)
+
\frac{\partial}{\partial x}\left(\frac{CDF}{RT}\frac{\partial \phi}{\partial x}\right),
\end{equation}

where $C$ is the concentration of deuterium in the sample, $D$ is the deuterium diffusivity, $F$ is the Faraday constant, $R$ is the ideal gas constant, $T$ is the temperature, $\phi$ is the electric potential applied across the sample, $x$ is the distance from the source boundary, and $t$ is time.

The model parameters used in the verification case are shown in [ver-1n_set_up_values]. The deuterium solubility and diffusivity are taken from [!cite](hossain2020evaluation). The applied voltage is 20 V across the 10 mm membrane.

!table id=ver-1n_set_up_values caption=Values of model properties for the Nernst--Planck verification problem.
| Parameter | Description                          | Value                                                       | Units                 | Reference                 |
| --------- | ------------------------------------ | ----------------------------------------------------------- | --------------------- | --------------------- |
| $R$     | gas constant                         | 8.31446261815324                                            | J/mol/K               | [PhysicalConstants.h](https://physics.nist.gov/cgi-bin/cuu/Value?r) |
| $T$     | temperature                          | 773                                                          | K                     | -- |
| $K_{s}$ | deuterium solubility in PCC          | 6.38$\times 10^{23} \exp(-7726.21 / RT)$                   | atom/m$^3$/Pa$^{0.5}$ | [!cite](hossain2020evaluation) |
| $P$     | upstream pressure                    | 100                                                          | Pa                    | -- |
| $D$     | deuterium diffusivity in PCC         | 2.44$\times 10^{-6} \exp(-71399.15 / RT)$                  | m$^2$/s               | [!cite](hossain2020evaluation) |
| $l$     | thickness of PCC sample              | 10$\times 10^{-3}$                                          | m                     | [!cite](hossain2020evaluation) |
| $F$     | Faraday constant                     | 96485.33                                                    | C/mol      | -- |
| $\phi$  | voltage applied across PCC sample               | 20                                                            | V      | -- |

The verification focuses on two aspects of the solution: (1) the temporal evolution of deuterium concentration at fixed locations, and (2) the spatial concentration profile at fixed times.

## Analytical Solution

[!cite](luping1993rapid) provides the analytical solution for a semi-infinite slab as:

\begin{equation}
\label{eq:Nernst_Plank_analytical}
C = \frac{C_0}{2}\left[
\exp(ax)\,\erfc\left(\frac{x + aDt}{2\sqrt{Dt}}\right)
+
\erfc\left(\frac{x - aDt}{2\sqrt{Dt}}\right)
\right],
\end{equation}

where

\begin{equation}
\label{eq:Nernst_Plank_analytical_constant_a}
a = \frac{zF}{RT}\frac{\partial \phi}{\partial x}.
\end{equation}

Here, $z=1$ is the charge number of the mobile hydroxyl defect carrying the hydrogen isotope. The semi-infinite approximation is valid over the simulated time range because the characteristic diffusion length $\sqrt{Dt}\approx 0.14$~mm remains much smaller than the 10 mm membrane thickness.

## Results

[ver-1n_comparison_time] compares the TMAP8 results and the analytical solution as a function of time at $x = 0.1$ mm and $x = 0.5$ mm. The TMAP8 calculations closely match the analytical solution at both locations, with RMSPE values of 0.14% and 0.51%, respectively.

!media comparison_ver-1n.py
       image_name=ver-1n_comparison_time.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1n_comparison_time
       caption=Comparison of deuterium concentration as a function of time at $x = 0.1$ mm and $x = 0.5$ mm calculated by TMAP8 and by the analytical solution.
As a second check, [ver-1n_comparison_location] compares the concentration as a function of distance from the source at $t = 30$ s and $t = 500$ s. The TMAP8 calculations are in good agreement with the analytical solution, with RMSPE values of 0.86% and 0.11%, respectively.

!media comparison_ver-1n.py
       image_name=ver-1n_comparison_location.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1n_comparison_location
       caption=Comparison of deuterium concentration as a function of distance from the source at $t = 30$ s and $t = 500$ s calculated by TMAP8 and by the analytical solution.

## Input Files

!style halign=left
The input file for this case can be found at [/ver-1n.i]. More information about the changes can be found in the test specification file for this case [/ver-1n/tests].

!bibtex bibliography
