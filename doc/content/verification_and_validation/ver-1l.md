# ver-1l

# Diffusion with Soret Effect (Thermodiffusion)

## General Case Description

This verification case considers tritium diffusion through a semi-infinite layer under the influence of a temperature gradient. The two transport driving forces are Fickian diffusion (which was verified in other verification cases, including [ver-1b](ver-1b.md) and [ver-1dd](ver-1dd.md)), and the Soret effect (also known as thermodiffusion or thermophoresis).
The Soret effect describes the phenomenon where species migration occurs in response to a temperature gradient. This coupling of thermal and mass transport can be particularly important in fusion applications where significant temperature gradients exist across material structures.

In this problem, tritium diffuses through a material layer subjected to a constant linear temperature gradient. The left boundary maintains a constant tritium concentration, while the right boundary is impermeable. The combined effects of concentration-driven diffusion and temperature-driven thermodiffusion are verified against an analytical solution. For simplicity, no trapping or solubility effects are included in this case. This TMAP8 case is published in [!cite](Simon2027). The geometry and boundary conditions of this case are shown in [ver-1l_schematic].

!media figures/ver-1l_schematic.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=ver-1l_schematic
    caption=Schematic of the ver-1l case: a slab with a fixed concentration on the left boundary, an impermeable right boundary, and a linear temperature gradient.

## Case Set up

This verification case models tritium diffusion through a one-dimensional slab of thickness $l = 100$ m with a linear temperature distribution across the domain. The left boundary ($x = 0$) is maintained at a constant concentration $C_{\text{left}} = 100$ mol/m$^3$, while the right boundary ($x = l$) is impermeable (zero flux). The initial concentration throughout the domain is $C_0 = 0.1$ mol/m$^3$. The temperature varies linearly from $T_{\text{left}} = 1$ K at the left boundary to $T_{\text{right}} = 0$ K at the right boundary, creating a constant temperature gradient.
Note that these very simple values are selected for the simplicity of the verification case and do not aim to represent a realistic case.

The governing equation for the coupled Fickian diffusion and the Soret effect is described as:

\begin{equation}
    \frac{\partial C}{\partial t} = \nabla \cdot \left( D \nabla C + D S_T C \nabla T \right),
\end{equation}

where $C$ is the concentration of mobile species, $D$ is the diffusivity, and $S_T$ is the Soret coefficient. The material properties and case parameters are provided in [ver-1l_set_up_values].

!table id=ver-1l_set_up_values caption=Values of material properties and case geometry for the Soret effect verification problem.
| Parameter | Description                | Value  | Units       |
| --------- | -------------------------- | ------ | ----------- |
| $l$       | Thickness                  | 100    | m           |
| $D$       | Diffusivity                | 0.1    | m$^2$/s     |
| $S_T$     | Soret coefficient          | 50     | 1/K         |
| $C_0$     | Initial concentration      | 0.1    | mol/m$^3$   |
| $C_{\text{left}}$ | Concentration on left | 100    | mol/m$^3$   |
| $T_{\text{left}}$ | Temperature on left   | 1      | K           |
| $T_{\text{right}}$ | Temperature on right | 0      | K           |

The verification focuses on two aspects of the solution: (1) the temporal evolution of concentration at a specific location ($x = 10$ m), and (2) the spatial concentration profile at a specific time ($t = 100$ s).

## Analytical solution

For a semi-infinite domain with constant diffusivity and Soret coefficient, subject to a constant temperature gradient $\nabla T$, the analytical solution provided in [!cite](xie2015analytical) is described as:

\begin{equation}
    C(x,t) = \left[ \frac{1}{2} \text{erfc} \left( \frac{D S_T t \nabla T + x}{2\sqrt{D t}} \right) + \frac{1}{2} e^{- S_T x \nabla T} \text{erfc} \left( \frac{- D S_T t \nabla T + x}{2\sqrt{D t}} \right) \right] (C_{\text{left}} - C_0) + C_0,
\end{equation}

where $\text{erfc}$ is the error function.

## Results

### Verification of concentration at a fixed location as a function of time

[ver-1l_comparison_analytical_concentration_location] shows the comparison of the TMAP8 calculation and the analytical solution for the concentration at location $x = 10$ m as a function of time. The TMAP8 prediction matches the analytical solution with excellent agreement, yielding a root mean square percentage error of RMSPE = 0.87 %.

!media comparison_ver-1l.py
       image_name=ver-1l_comparison_analytical_concentration_location.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1l_comparison_analytical_concentration_location
       caption=Comparison of TMAP8 calculation with the analytical solution for the concentration at $x = 10$ m as a function of time.

### Verification of concentration profile as a function of position at a fixed time

[ver-1l_comparison_analytical_concentration_time] shows the comparison of the TMAP8 calculation and the analytical solution for the concentration profile at time $t = 100$ s. The concentration profile exhibits a characteristic shape that differs from pure Fickian diffusion due to the thermodiffusion contribution. The TMAP8 prediction is in good agreement with the analytical solution, with a root mean square percentage error of RMSPE = 0.21 %.

!media comparison_ver-1l.py
       image_name=ver-1l_comparison_analytical_concentration_time.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1l_comparison_analytical_concentration_time
       caption=Comparison of TMAP8 calculation with the analytical solution for the concentration profile at $t = 100$ s as a function of position.

## Input files

!style halign=left
The input file for this case can be found at [!file](/ver-1l.i), which is also used as test in TMAP8 at [!file](/ver-1l/tests).

!bibtex bibliography
