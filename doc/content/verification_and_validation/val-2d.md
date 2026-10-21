# val-2d

# Thermal Desorption Spectroscopy on Tungsten

## Case Description

This validation problem is taken from [!cite](hino1998hydrogen) and uses multiple trapping capability. This case is part of the validation suite of TMAP7 as val-2d [!citep](ambrosek2008verification).
In this experiment, tritium is implanted at 5 keV and a flux of 1 $\times 10^{19}$ atom/m$^2$/s for 5,000 seconds into a 0.1-mm-thick polycrystalline tungsten foil with a surface area of 50 $\times$ 50 mm$^2$ at room temperature (300 K).
The background pressure in the implantation chamber is 10$^{-3}$ Pa while the implantation is going on and 10$^{-5}$ Pa the rest of the time.
Following the implantation, the sample is subjected to thermal desorption spectroscopy by heating under vacuum at 50 K/min to 1,273 K and is then held at that temperature for several minutes.

The system is in the structure of [val-2d_schematic]. The implantation chamber (Enclosure 1) has a volume of 0.1 $m^3$ and is evacuated by a turbo-molecular vacuum pump.
The implantation chamber is defined for this problem as an enclosure having a preprogrammed temperature of 300 K for 5,000 seconds followed by a ramp to 1,273 K at a ramp rate of 50 K/min.
Gas leakage from the ion source is represented by an enclosure with a pressure of $1 \times 10^{-3}$ Pa during implantation followed by $1 \times 10^{-5}$ Pa and flow to the implantation chamber at the vacuum pumping rate.
Flow rate from the implantation chamber is taken to be 0.07 m$^3$/s on the basis of the stated pressure in the test chamber during implantation, given that nearly all implanted gas re-emerges during that time. The vacuum pump is represented by an enclosure (Enclosure 2) held at 10$^{-8}$ Pa.

!media figures/val-2d_schematic.png
        style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
        id=val-2d_schematic
        caption=Schematic of the modeled enclosures for val-2d.

Based on TRIM calculations [!citep](eckstein2013computer,biersack1982stopping), implantation in the sample shows a normal distribution, which has a peak at 4.6 nm below the surface and a characteristic half width of 3 nm. Implantation is activated for 5,000 s and then terminated.

Three trapping site populations are accounted for in the sample. Trap concentrations and distributions are considered adjustable parameters while energies were determined by TDS peak temperatures.
The first trap is assumed to be associated with implantation (damage and precipitation) and to be normally distributed with a peak at 4.6 nm and a characteristic width of 10 nm, consistent with the observations of [!cite](haasz1999effect) that the damage zone exceeds the implantation depth.
Its trap energy is adjusted, based on the temperature of the first peak, to be 1.2 eV, and it is assumed to be 0.086 atom fraction at the peak. Its distribution is defined as:

\begin{equation} \label{eq:normal_distribution_trap}
\chi^1 = \frac{0.002156}{\sigma \sqrt{2 \pi}} \exp \left( - \frac{(x - \mu )^2}{2 \sigma^2} \right),
\end{equation}

where $\sigma = 10 \times 10^{-9}$ m is the characteristic width of the normal distribution, and $\mu = 4.6 \times 10^{-9}$ m is the depth of the normal distribution from the upstream side. [eq:normal_distribution_trap] uses the factor of 0.002156 to correspond to the peak atom fraction of 0.086 from [!cite](ambrosek2008verification).

The second is a uniform trap associated with dislocations and is assigned a trap release energy of 1.6 eV, typical of but slightly higher than that seen by [!cite](anderl1992deuterium). Its concentration is adjusted to equal 0.00175 atom fraction. The third trap is also assumed to be uniformly distributed and to have a trapping energy of 3.1 eV, nearly the same as the deep trap seen by [!cite](frauenfelder1969solution) with a concentration of 0.002 atom fraction. It is only marginally filled during the implantation because of the diffusive limitation to flow into the depth of the sample.

Therefore, the diffusion of tritium in sample is described as:

\begin{equation} \label{eq:diffusion}
\frac{d C_M}{d t} = \nabla \cdot D \nabla C_M + S - \sum_{i=1}^{3} f_{T/M,i} \frac{dC_{T_i}}{dt} ,
\end{equation}

and, for $i=1$, $i=2$, and $i=3$:

\begin{equation}
    \label{eqn:trapped_rate}
    \frac{dC_{T_i}}{dt} = \alpha_t^i \frac{C_{T_i}^{empty} C_M } {(N f_{T/M,i})} - \alpha_r^i C_{T_i},
\end{equation}

and

\begin{equation}
    C_{T_i}^{empty} = (C_{{T_i}0} N - f_{T/M,i} C_{T_i}  ) ,
\end{equation}

where $C_M$ is the concentration of mobile tritium, $t$ is the time, $S$ is the source term in sample due to the tritium ion implantation, $C_{T_i}$ is the trapped species in trap $i$, $\alpha_t^i$ and $\alpha_r^i$ are the trapping and release rate coefficients for trap $i$, respectively, $f_{T/M,i}$ is a user-defined numerical factor scaling $C_{T_i}$ to be closer to $C_M$ for better numerical convergence, $C_{{T_i}0}$ is the fraction of host sites $i$ that can contribute to trapping, $C_{T_i}^{empty}$ is the concentration of empty trapping sites, $N$ is the host density, and $D$ is the tritium diffusivity in tungsten, which is defined as:

\begin{equation} \label{eq:diffusivity}
D = D_{0} \exp \left( - \frac{E_{D}}{k_b T} \right),
\end{equation}

where $E_{D}$ is the diffusion activation energy, $k_b$ is the Boltzmann’s constant, $T$ is the temperature, and $D_{0}$ is the maximum diffusivity coefficient. TMAP7 ([!cite](ambrosek2008verification)) assigns two different values, $D_{0,l}$ and $D_{0,r}$, for the implantation zone ($x < 15 \times 10^{-9}$ m) and the other zone ($x > 15 \times 10^{-9}$ m).

$\alpha_t^i$ and $\alpha_r^i$ are defined as:

\begin{equation} \label{eq:trapping}
\alpha_t^i = \alpha_{t0}^i \exp(-\epsilon_t^i / T),
\end{equation}

and

\begin{equation} \label{eq:release}
\alpha_r^i = \alpha_{r0}^i \exp(-\epsilon_r^i / T),
\end{equation}

where $\alpha_{t0}^i$ and $\alpha_{r0}^i$ are pre-exponential factors of trapping and release rate coefficients, respectively, and $\epsilon_t^i$ and $\epsilon_r^i$ are the trapping and detrapping energies, respectively.

The thermal diffusion after 5000 s is governing by:

\begin{equation} \label{eq:thermal}
\rho C_P \frac{d T}{d t} = \nabla \cdot D_T \nabla T,
\end{equation}

where $\rho$ is the density of tungsten, $C_P$ is the specific heat, and $D_T$ is the thermal conductivity.

All the model parameters are taken from [!cite](hino1998hydrogen,haasz1999effect,anderl1992deuterium,frauenfelder1969solution,ambrosek2008verification) and listed in [val-2d_set_up_values]. Whenever the original values are updated, it is specified in [val-2d_set_up_values].

## Model Description

In this case, TMAP8 simulates a one-dimensional domain to represent the tritium implantation, diffusion, and trapping and detrapping throughout the thermal history. Note that this case can easily be extended to a two- or three-dimensional case.

The source term in the model is described as a normal distribution in [eq:normal_distribution]:

\begin{equation} \label{eq:normal_distribution}
S = F \frac{1}{\sigma \sqrt{2 \pi}} \exp \left( - \frac{(x - \mu )^2}{2 \sigma^2} \right),
\end{equation}

where $F$ is the implantation flux provided in [val-2d_set_up_values], $\sigma = 3 \times 10^{-9}$ m is the characteristic width of the normal distribution, and $\mu = 4.6 \times 10^{-9}$ m is the depth of the normal distribution from the upstream side.

The pressures on the upstream and downstream sides are close to vacuum pressures and do not have a significant impact on tritium desorption. Thus, TMAP8 ignores the pressure in these enclosures for simplification. Also, because both surfdep and Dirichlet boundary conditions have similar desorption performance in the near vacuum environment, we use the Dirichlet boundary condition to improve the model efficiency. The concentrations on upstream and downstream sides are defined as:

\begin{equation} \label{eq:boundary_condition}
C_M = 0.
\end{equation}

Due to the high thermal conductivity in tungsten, the model simplifies the thermal diffusion as an instantaneous process to increase the model efficiency. That is, the temperature inside the tungsten sample is consistent with the temperature on the surface of tungsten sample. The temperature is set to 300 K during implantation, and the temperature after implantation on the upstream and downstream sides is defined as:

\begin{equation} \label{eq:temperature}
T =
    \begin{cases}
        T_l &, t < 5000 s \\
        T_l + k_T (t - 5000) &, 5000 s  < t < 6167.6 s \\
        T_h &, t > 6167.6 s
    \end{cases}
,
\end{equation}

where $T_l = 300$ K and $T_h = 1273$ K are the lowest and highest temperatures, respectively, and $k_T$ is the heating rate.

The objective of this simulation is to determine the desorption flux on the sample. This case only considers the flux on the upstream side due to the marginally filled sample during implantation. The simulation results match the experimental data published in [!cite](hino1998hydrogen) and reproduced in [val-2d_comparison].

## Case and Model Parameters

All the model parameters are listed in [val-2d_set_up_values]:

!table id=val-2d_set_up_values caption=Values of material properties. Note that parameters marked with * are currently not used in the input file.
| Parameter | Description                          | Value                                                       | Units                 | Reference                 |
| --------- | ------------------------------------ | ----------------------------------------------------------- | --------------------- | --------------------- |
| $k_b$     | Boltzmann constant                   | 1.380649 $\times 10^{-23}$                                  | J/K                   | [PhysicalConstants.h](https://physics.nist.gov/cgi-bin/cuu/Value?r) |
| $F$       | Implantation flux                    | 1 $\times 10^{19}$                                          | at/m$^2$/s            | [!cite](hino1998hydrogen) |
| $D_{0,l}$ | Maximum diffusivity coefficient when $x < 15 \times 10 ^ {-9}$ m | 4.1 $\times 10^{-7}$            | m$^2$/2               | [!cite](frauenfelder1969solution) |
| $D_{0,r}$ | Maximum diffusivity coefficient when $x > 15 \times 10 ^ {-9}$ m | 4.1 $\times 10^{-6}$            | m$^2$/2               | [!cite](ambrosek2008verification) |
| $E_D$     | Activity energy for diffusion        | 0.39                                                        | eV                    | [!cite](frauenfelder1969solution) |
| $C_{M,0}$ | Initial concentration of mobile tritium     | 1 $\times 10^{-10}$                                         | at/m$^3$              | [!cite](ambrosek2008verification) |
| $N$       | Host density                         | 6.25 $\times 10^{28}$                                       | at/m$^3$              | [!cite](ambrosek2008verification) |
| $\chi^1_0$ | Initial atom fraction in Trap 1     | 0                                                           | -                     | [!cite](ambrosek2008verification) |
| $\chi^2_0$ | Initial atom fraction in Trap 2     | 4.4 $\times 10^{-10}$                                       | -                     | [!cite](ambrosek2008verification) |
| $\chi^3_0$ | Initial atom fraction in Trap 3     | 1.4 $\times 10^{-10}$                                       | -                     | [!cite](ambrosek2008verification) |
| $\epsilon_t$ | Trapping energy for three traps   | 0.39 / k_b                                                  | K                     | [!cite](ambrosek2008verification) |
| $\epsilon_r^1$ | Release energy for Trap 1       | 1.20 / k_b                                                  | K                     | [!cite](ambrosek2008verification,haasz1999effect) |
| $\epsilon_r^2$ | Release energy for Trap 2       | 1.60 / k_b                                                  | K                     | [!cite](ambrosek2008verification,anderl1992deuterium) |
| $\epsilon_r^3$ | Release energy for Trap 3       | 3.10 / k_b                                                  | K                     | [!cite](ambrosek2008verification,frauenfelder1969solution) |
| $\chi^1$  | Maximum atom fraction in Trap 1      | 0.002156                                                    | -                     | [!cite](ambrosek2008verification) |
| $\chi^2$  | Maximum atom fraction in Trap 2      | 0.00175                                                     | -                     | Adjusted from [!cite](ambrosek2008verification) |
| $\chi^3$  | Maximum atom fraction in Trap 3      | 0.00200                                                     | -                     | [!cite](ambrosek2008verification) |
| $\alpha_{t0}$ | Pre-factor of trapping rate coefficient | 9.1316 $\times 10^{12}$                              | 1/s                   | [!cite](ambrosek2008verification) |
| $\alpha_{r0}$ | Pre-factor of release rate coefficient  | 8.4 $\times 10^{12}$                                 | 1/s                   | [!cite](ambrosek2008verification) |
| $A$       | * Area of tungsten sample            | 0.0025                                                      | m$^2$                 | [!cite](hino1998hydrogen) |
| $l$       | Thickness of tungsten sample         | 1 $\times 10^{-4}$                                          | m                     | [!cite](hino1998hydrogen) |
| $T_l$     | Lowest temperature                   | 300                                                         | K                     | [!cite](hino1998hydrogen) |
| $T_h$     | Highest temperature                  | 1273                                                        | K                     | [!cite](hino1998hydrogen) |
| $k_T$     | Heating rate          | 50                                                          | K/min                 | [!cite](hino1998hydrogen) |


!alert note title=The $\chi^2$ is adjusted to better correspond to experimental results
TMAP7 ([!cite](ambrosek2008verification)) adjusts the maximum atom fraction to 0.0041 in Trap 2 from [!cite](anderl1992deuterium) to better correspond to experimental results. Thus, we also adjust it to 0.00175 to correspond to experimental results from [!cite](hino1998hydrogen).

## Results

In this case, there is a general background drift on desorption flux due to an increasing source of atoms going into the gas phase as the heated region spreads with time. Thus, we add a ramped signal peaking at 4.87 $\times 10^{17}$ H$_2$/m$^2$/s to the results of the TMAP8 during the thermal desorption.
[val-2d_comparison] shows the comparison of the TMAP8 calculation and the experimental data. There is reasonable agreement between the TMAP predictions and the experimental data with the root mean square percentage error of RMSPE = 32.81 %.
Note that the agreement could be improved by adjusting the model parameters and adding more potential traps. TMAP7 is limited to three traps, but TMAP8 can introduce an arbitrarily number of trapping populations. It is also possible to perform this optimization with [MOOSE's stochastic tools module](https://mooseframework.inl.gov/modules/stochastic_tools/index.html).

There are several potential reasons for the imperfect fit with the data from [!cite](hino1998hydrogen); the most prominent one is the two-dimensionality of the experiment arising from beam nonuniformity and radial diffusion [!citep](anderl1992deuterium). The actual trap energies are probably a little lower than the ones indicated above if the time lag caused by two-dimensionality is significant. The exchange of hydrogen with chamber surfaces, particularly the sample support structure, may also be a factor.

One reason the measured signal falls off after $\approx$ 6300 s while the computed one remains steady is that the source of additional atoms in the experiment may be an expanding area that grow nonlinearly, while the sample is being heated but stopped growing and thus stops emitting when the heating stops.

!media comparison_val-2d.py
       image_name=val-2d_comparison.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=val-2d_comparison
       caption=Comparison of TMAP8 calculation with the experimental data on the upstream side of the sample.

## Input files

!style halign=left
The input file for this case can be found at [!file](/val-2d.i). The input file is different from the input file used as test in TMAP8. To limit the computational costs of the test case, the test runs a version of the file with a coarser mesh and fewer time steps. More information about the changes can be found in the test specification file for this case, namely [!file](/val-2d/tests).

!bibtex bibliography
