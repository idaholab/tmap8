# ver-1m

# Heat Transfer and Hydrogen Thermodiffusion in U-ZrH

## General Case Description

This verification case is taken from [!cite](huang01102000) and considers hydrogen diffusion through a uranium zirconium hydride (UZrH) fuel pellet under the influence of a temperature gradient. The driving forces of hydrogen migration are Fickian diffusion (which was verified in other verification cases including [ver-1b](ver-1b.md) and [ver-1dd](ver-1dd.md)), and the Soret effect (which was verified in [ver-1l](ver-1l.mb)). The temperature profile in the fuel is calculated from conduction with heat generation, which is verified in [ver-1fa](ver-1fa.mb). However, in this case, steady state solution is assumed for heat conduction. The novelty of this verification case is the coupling of these phenomena. 

Fickian diffusion describes mass transport due to a concentration gradient, while the Soret effect describes species migration in response to a temperature gradient. This coupling of transport along thermal and mass gradients can be important for metal hydride moderators for fission reactors because temperature gradients are created by fission in the core which can cause the hydrogen to migrate through the moderator and impact the overall reactivity.

In this problem, hydrogen diffuses radially through a UZrH fuel pin under a temperature profile calculated using different linear heating rates. It is assumed that no hydrogen leaks from the fuel pin, so the outer boundary of the fuel is impermeable. The combined effects of concentration-driven diffusion and temperature-driven thermodiffusion are verified against an analytical solution and compared to literature values from [!cite](huang01102000). Results from four different linear heating rates are shown to further illustrate how different temperatures impact the results.

## Case Set up

This verification case models radial hydrogen diffusion through a two-dimensional pin of radius $r = 0.005$ m with a temperature distribution across the domain, calculated from the heat conduction equation:

\begin{equation} \label{eq:thermal_equation}
\rho C_P \frac{d T}{d t} = \nabla \cdot k \nabla T + q''',
\end{equation}

where $T$ is the temperature, $\rho$ is the density, $C_P$ is the specific heat, $k$ is the thermal conductivity, and $q'''$ is the internal volumetric heat generation rate.

The conduction equation is evaluated across the fuel, gap and cladding with a convective boundary condition to model heat transfer into the coolant.

The outer boundary of the fuel pellet is impermeable (zero hydrogen flux) and there are no hydrogen sources or sinks within the fuel pellet. The initial concentration throughout the domain is uniformly $C_0$ = 1.6 at. frac. (H/Zr).

The governing equation for the coupled Fickian diffusion and the Soret effect is described as:

\begin{equation} \label{eq:hydrogen_diffusion}
    \frac{\partial c_H}{\partial t} = \nabla\cdot\left[-D\left(\nabla c_H+\frac{Q^\ast c_H}{RT^2}\nabla T\right)\right],
\end{equation}

where $c_H$ is the hydrogen atom fraction, $D$ is the diffusivity, and $Q^\ast$ is the heat of transport. The diffusivity is a function of temperature, given by the Arrhenius relation [!citep](majer_mechanism_1994):

\begin{equation}
    D=D_0 \exp\left(-\frac{E_a}{RT}\right),
\end{equation}

where $D_0$ is the limiting diffusivity in m$^2$/s, $E_a$ is the activation energy in kJ/mol, $R$ is the gas constant in J/Kmol, and $T$ is the temperature in K.

The material properties and case parameters are provided in [ver-1m_set_up_values].

!table id=ver-1m_set_up_values caption=Values of material properties and case geometry for the UZrH hydrogen migration verification problem.
| Parameter    | Description                        | Value    | Units       | Reference |
| ------------ | ---------------------------------- | -------- | ----------- | --------- |
| $r_f$        | Pin radius                         | 0.005    | m           | [!cite](huang01102000) |
| $t_g$        | Gap thickness                      | 0.0001   | m           | [!cite](huang01102000) |
| $t_c$        | Cladding thickness                 | 0.001    | m           | [!cite](huang01102000) |
| $k_f$        | Fuel thermal conductivity          | 17.6     | W/mK        | [!cite](huang01102000) |
| $k_c$        | Cladding thermal conductivity      | 16.5     | W/mK        | Estimate
| $C_g$        | Gap conductance                    | 7381     | W/m$^2$K    | [!cite](huang01102000) |
| $h_c$        | Coolant heat transfer coefficient  | 18000    | W/m$^2$K    | Estimate
| $T_{\infty}$ | Temperature of coolant             | 563.15   | K           | [!cite](huang01102000) |
| $D_0$        | Limiting diffusivity               | 1.53$\times$10$^{-7}$  | m$^2$/s     | [!cite](majer_mechanism_1994) |
| $E_a$        | Diffusion activation energy        | 0        | kJ/mol      | *see note
| $Q^\ast$     | Heat of Transport                  | 5.3      | kJ/mol      | [!cite](huang01102000) |
| $C_0$        | Initial concentration              | 1.6      | -           | [!cite](huang01102000) |
| $R$          | Gas constant                       | 8.31446261815324    | J/mol/K      | [PhysicalConstants](source/utils/TMAP8PhysicalConstants.md) |
| LHR          | Linear heating rate                | 150-300  | W/cm        | [!cite](huang01102000) |

Note: The diffusion coefficient is technically different for each linear heating rate as calculated by the equation above, but the value does not impact the steady state solution, so the limiting diffusivity is assumed in all cases.

The verification focuses on two aspects of the solution: (1) the steady state temperature profile and (2) the final steady state spatial hydrogen concentration profile.


## Analytical solution

For steady state radial heat transfer, the conduction equation becomes:

\begin{equation}
      \frac{1}{r}\frac{d}{dr} \left(rk_f \frac{dT}{dr} \right) + q''' = 0
\end{equation}

Using symmetry tells that conduction from the center is equivalent in all directions, meaning that $dT/dr=0$, at $r = 0$, and substituting $q''' = q' / (\pi r_f^2)$ (where q' is the linear heating rate in W/m), gives the temperature profile in the fuel:

\begin{equation}
      T_f(r) = T_c -\frac{q'}{4\pi k_fr_f^2}r^2,
\end{equation}

where $T_c$ is the centerline temperature of the fuel in K, which can be calculated by a thermal resistor model:

\begin{equation}
      T_c = T_\infty + q' \left[\frac{1}{2 \pi r_f h_g} + \frac{ln(\frac{r_{co}}{r_{ci}})}{2 \pi k_c} + \frac{1}{2 \pi r_{co} h_w} + \frac{1}{4 \pi r_f^2} \right].
\end{equation}

For the analytical steady state hydrogen profile, it is assumed that the temperature profile has already reached steady state and does not vary with time. This assumption is valid since hydrogen diffusion is a very slow process compared to conduction.

For steady state, radial hydrogen redistribution the diffusion equation described previously becomes:

\begin{equation}
    0 = \frac{d c_H}{dr} + \frac{Q^\ast C}{RT^2}\frac{dT}{dr}
\end{equation}

The analytical solution to this was calculated by [!cite](stefano_terlizzi_asymptotic_2023):

\begin{equation}
    c_H(r) = K \exp \left(\frac{Q^\ast}{RT(r)}\right),
\end{equation}

where $T(r)$ is the temperature profile and K is determined from mass conservation, assuming that the initial concentration ($C_0$) is uniform:

\begin{equation}
    K = \frac{C_0\pi r_f^2}{\int_{0}^{r_f} r \, \exp\!\left(\frac{Q}{RT(r)}\right) \, dr}
\end{equation}

## Results

### Steady state results

[ver-1m_comparison_analytical_temperature_location.png] shows the comparison of the TMAP8 calculation and the analytical solution for the temperature as a function of the distance from the center of the fuel. The TMAP8 prediction matches the analytical solution with excellent agreement for each linear heating rate, yielding a maximum root mean square percentage error (RMSPE) of RMSPE = 0.18 %.

!media comparison_ver-1m.py
       image_name=ver-1m_comparison_analytical_temperature_location.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1m_comparison_analytical_temperature_location.png
       caption=Comparison of TMAP8 calculation with the analytical solution for steady state temperature profile.

[ver-1m_comparison_analytical_concentration_location.png] shows the comparison of the TMAP8 calculation and the analytical solution for the concentration profile as a function of the distance from the center. The TMAP8 prediction matches the analytical solution with excellent agreement for each linear heating rate, with a maximum RMSPE of 0.02 %. Results from [!cite](huang01102000) are also shown as a comparison.

!media comparison_ver-1m.py
       image_name=ver-1m_comparison_analytical_concentration_location.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1m_comparison_analytical_concentration_location.png
       caption=Comparison of TMAP8 calculation with the analytical solution and literature results for steady state concentration profile.


## Input files

!style halign=left
The input file for this case can be found at [/ver-1m.i], which is also used as test in TMAP8 at [/ver-1m/tests].

!bibtex bibliography
