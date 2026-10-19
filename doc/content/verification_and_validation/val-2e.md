# val-2e

# Co-permeation of H$_2$ and D$_2$ through Pd

## Case Description

This validation problem is taken from [!cite](ambrosek2008verification), which utilized experimental data from [!cite](kizu2001co).
Kizu et al. describe permeation experiments in which H$_2$ and D$_2$ permeate through thin Pd membranes.
This case is part of the validation suite of TMAP7 as val-2e [!citep](ambrosek2008verification).

The experimental equipment has two vacuum chambers separated by a Pd membrane.
The membrane area is 1.8 $\times 10^{-4}$ m$^2$ and has thicknesses of either 0.025 mm or 0.05 mm, depending on the test.
Copper gaskets hold the membrane in place, and it is reasonably assumed that gas can only move from one chamber to another by diffusing through the membrane.
The membrane's temperature is controlled between 820 and 870 K using an electric heater and a thermocouple.
Gas is supplied to one chamber (the upstream chamber) from regulated bottles at different compositions and pressures.
The base pressure on both upstream and downstream chambers is maintained below 1 $\times 10^{-6}$ Pa using turbomolecular and rotary pumps.
Pressure is measured by an ion gauge on each side, and downstream gas composition is measured with a quadrupole mass spectrometer.
Flow rates through the membrane are determined by pressure increases in the downstream chamber at a fixed pumping rate of 0.1 m$^3$/s.

The structure of the system is shown in [val-2e_equipment_schematic].
Enclosure 1 is the source of background pressure to the experimental system.
Enclosure 4 is the vacuum pumping system that provides a sink for all system flows.
Enclosure 5 is the gas feed to the upstream experimental chamber, Enclosure 2.
The pressures in Enclosures 1, 4, and 5 are held constant or as a functional value while the pressures in Enclosures 2 and 3 evolve with the flow and diffusion.
Depending on the experiment, the feed pressure of H$_2$ is 0, 0.14, or 0.063 Pa.
Combined with the evacuation to Enclosure 4, this provides the upstream H$_2$ pressure for permeation.
The D$_2$ pressure is a stepped function of time, one step corresponding to each of the data points from [!cite](kizu2001co).
Steps are arbitrarily set at 100 s, but equilibrium is achieved in times much shorter than that. Effectively no HD is fed into the upstream experimental chamber, in keeping with the experimental setup given by [!cite](kizu2001co).
Rather, with either solution-law or recombination limited-boundary conditions for diffusion, HD is formed in accordance with the laws of chemical equilibrium.
Likewise in the downstream chamber, Enclosure 3, HD is formed together with H$_2$ and D$_2$ in chemical equilibrium from diffusing H and D.

!media figures/val-2e_equipment_schematic.png
        style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
        id=val-2e_equipment_schematic
        caption=Schematic of the modeled enclosures for val-2e.

The first three test cases are permeation tests of D$_2$ alone through membranes of each thickness.
For the 0.025 membrane, tests are conducted at both 825 K and 865 K whereas the 0.05 mm membrane is tested only at 825 K.

[tab:val-2e_cases] described the different subcases being modeled in this validation effort.

!table id=tab:val-2e_cases caption=Different subcases being modeled in this validation effort and their specific conditions.
| case name  | Temperature (K) | Membrane thickness (mm) | Inlet gas composition            | Remark |
| -----------  | ---------------- | --------------------------- | ---------------------------- | --------- |
| val-2ea        | 825                      | 0.05                                       | D$_2$                                     | Assumes solubility equilibrium ([eq:seivert_concentration]) |
| val-2eb        | 825                      | 0.025                                     | D$_2$                                     | Assumes solubility equilibrium ([eq:seivert_concentration]) |
| val-2ec        | 865                      | 0.025                                     | D$_2$                                     | Assumes solubility equilibrium ([eq:seivert_concentration]) |
| val-2ed        | 870                      | 0.025                                     | D$_2$ + H$_2$ at 0.063 Pa | Assumes solubility equilibrium ([eq:seivert_concentration]) |
| val-2ee        | 870                      | 0.025                                     | D$_2$ + H$_2$ at 0.063 Pa | Accounts for recombination kinetics ([eq:recombination]) |



## Model Description

In the first three cases (val-2ea, val-2eb, and val-2ec), TMAP8 simulates a one-dimensional domain to represent the deuterium diffusion and gas flowing in the enclosures.
Note that this case can easily be extended to a two- or three-dimensional case.

This model considers the diffusion of deuterium on both sides of the Pd membrane.
First, the diffusion of deuterium in the membrane is described as:

\begin{equation} \label{eq:diffusion}
\frac{d C_i}{d t} = \nabla \cdot D_i \nabla C_i,
\end{equation}

where $C_i$ is the concentration of hydrogen isotope $i$ in membrane,
$i$ represents hydrogen isotope H or D,
$t$ is the time, and
$D_i$ is the diffusivity of hydrogen isotope $i$.

The flow of gas into Enclosures 2 and 3 can be given by

\begin{equation} \label{eq:dt_P2}
\frac{dP_{Ij}}{dt} = \frac{Q (P_{I,j-1}-P_{Ij})}{V_j},
\end{equation}

where $Q$ is the volumetric flow rate of always 0.1 m$^3$/s,
$V_j$ is the volume of current Enclosure $j$, $P_{I,j-1}$ and $P_{I,j}$ are the pressure of gas molecules $I$ in the previous Enclosure $j-1$ and current Enclosure $j$, respectively, and gas molecules $I$ represent H$_2$, or D$_2$, or HD.

The hydrogen isotopes recombine into gas on both sides of the membrane, and there are several ways to model this process, two of which are used in this validation case: (1) assuming steady state at the surface, also called lawdep boundary conditions in TMAP4 and TMAP7 [!citep](ambrosek2008verification), and (2) capturing the kinetics of dissociation and recombination, also called ratedep conditions in TMAP4 and TMAP7 [!citep](ambrosek2008verification).

By assuming that the kinetics of the dissociation and recombination processes are faster than diffusion, surface reactions can be assumed to be at steady state.
The concentrations on both sides can then be described as

\begin{equation} \label{eq:seivert_concentration}
C_i = K_s P_{Ij}^{n},
\end{equation}

where $K_s$ is the solubility of the hydrogen isotope in the membrane and $n$ is the exponent for the relation of pressure and concentration.

However, for the kinetics of surface reactions to be captured, the boundary conditions are set as

\begin{equation} \label{eq:recombination}
J_{ij} = 2 A (K_r C_i^2 - K_d P_{Ij}),
\end{equation}

where $J_{ij}$ is the recombination flux of hydrogen isotope $i$ out of the sample sides in Enclosure $j$,
$A$ is the area on either side of the membrane,
and $K_r$ and $K_d$ are the recombination and dissociation coefficients, respectively.
The coefficient of 2 accounts for the fact that two atoms (D and H) form one isotope molecule (HD).

The two co-permeation simulations (i.e., val-2ed and val-2ec) also include the chemical reactions in the upstream and downstream enclosure.
The reaction rates for H$_2$, D$_2$, and HD are described by

\begin{equation} \label{eq:chemical_reaction_lawdep}
\frac{- 2 d P_{H_2}}{dt} = \frac{- 2 d P_{D_2}}{dt} = \frac{d P_{HD}}{dt} = 2 P_{H_2}^{0.5} P_{D_2}^{0.5} - P_{HD}
\end{equation}

for lawdep boundary conditions and

\begin{equation} \label{eq:chemical_reaction_ratedep}
\frac{- 2 d P_{H_2}}{dt} = \frac{- 2 d P_{D_2}}{dt} = \frac{d P_{HD}}{dt} = \frac{k_b T A}{V} (K_r C_H C_D - K_d P_{HD}),
\end{equation}

for ratedep boundary conditions,
where $k_b$ is the Boltzmann’s constant,
$A$ is the surface area of the membrane, and
$T$ is the temperature.

## Case and Model Parameters

The pressure history of deuterium in Enclosure 5 for the first three simulations (val-2ea, val-2eb, and val-2ec) is presented in [val-2e_abc_pressure_history], as shown in [val-2e_comparison_pressure_history]. The initial pressures on other enclosures are presented in [val-2e_abc_pressure_initial].

!table id=val-2e_abc_pressure_history caption=Values of deuterium pressure on Enclosure 5 during simulations val-2ea, val-2eb, and val-2ec [!citep](ambrosek2008verification).
| Time (s)      | Pressure $P_{D_2,5}$ (Pa)      |
| ---------     | ---------------------------- |
| 0 - 150       | 1.2 $\times 10^{-4}$         |
| 150 - 250     | 2.41 $\times 10^{-4}$        |
| 250 - 350     | 6.06 $\times 10^{-4}$        |
| 350 - 450     | 1.3 $\times 10^{-3}$         |
| 450 - 550     | 2.53 $\times 10^{-3}$        |
| 550 - 650     | 7.08 $\times 10^{-3}$        |
| 650 - 750     | 1.45 $\times 10^{-2}$        |
| 750 - 850     | 2.63 $\times 10^{-2}$        |
| 850 - 950     | 6.51 $\times 10^{-2}$        |
| 950 - 1050    | 1.16 $\times 10^{-1}$        |
| 1050 - 1150   | 2.97 $\times 10^{-1}$        |
| 1150 - 1250   | 7.6 $\times 10^{-1}$         |
| 1250 - 1350   | 1.55                         |
| 1350 - 1900   | 3.37                         |

!media comparison_val-2e.py
       image_name=val-2e_comparison_pressure_history.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=val-2e_comparison_pressure_history
       caption= The pressure history of D$_2$ in Enclosure 5 for simulations val-2ea, val-2eb, and val-2ec.

!table id=val-2e_abc_pressure_initial caption=Values of deuterium pressure during simulations val-2ea, val-2eb, and val-2ec [!citep](ambrosek2008verification).
| Parameter | Description                          | Value                                                       | Units                 |
| --------- | ------------------------------------ | ----------------------------------------------------------- | --------------------- |
| $P_{D_2,1}$ | Deuterium pressure in Enclosure 1    | 1 $\times 10^{-6}$                                          | Pa                    |
| $P_{D_2,2}$ | Deuterium pressure in Enclosure 2    | 1 $\times 10^{-6}$                                          | Pa                    |
| $P_{D_2,3}$ | Deuterium pressure in Enclosure 3    | 1 $\times 10^{-6}$                                          | Pa                    |
| $P_{D_2,4}$ | Deuterium pressure in Enclosure 4    | 1 $\times 10^{-10}$                                         | Pa                    |

The pressure history of D$_2$ in Enclosure 5 for the next two simulations (val-2ed and val-2ee) is presented in [val-2e_de_pressure_history], as shown in [val-2e_comparison_mixture_pressure_history]. The initial pressures on other enclosures are presented in [val-2e_de_pressure_initial].

!table id=val-2e_de_pressure_history caption=Values of deuterium pressure on Enclosure 5 during simulations val-2ed and val-2ee [!citep](ambrosek2008verification).
| Time (s)      | Pressure $P_{D_2,5}$ (Pa)      |
| ---------     | ---------------------------- |
| 0 - 150       | 1.8421 $\times 10^{-4}$      |
| 150 - 250     | 1 $\times 10^{-3}$           |
| 250 - 350     | 3 $\times 10^{-3}$           |
| 350 - 450     | 9 $\times 10^{-3}$           |
| 450 - 550     | 2.7 $\times 10^{-2}$         |
| 550 - 650     | 8.1 $\times 10^{-2}$         |
| 650 - 750     | 2.43 $\times 10^{-1}$        |
| 750 - 1000    | 7.29 $\times 10^{-1}$        |

!media comparison_val-2e.py
       image_name=val-2e_comparison_mixture_pressure_history.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=val-2e_comparison_mixture_pressure_history
       caption= The pressure history of D$_2$ in Enclosure 5 for simulations val-2ed and val-2ee.

!table id=val-2e_de_pressure_initial caption=Values of pressure of H$_2$, D$_2$, and HD during simulations val-2ed and val-2ee [!citep](ambrosek2008verification).
| Parameter   | Description                          | Value                                                    | Units                 |
| ----------- | ------------------------------------ | -------------------------------------------------------- | --------------------- |
| $P_{D_2,1}$ | D$_2$ pressure in Enclosure 1        | 1 $\times 10^{-7}$                                       | Pa                    |
| $P_{H_2,1}$ | H$_2$ pressure in Enclosure 1        | 1 $\times 10^{-7}$                                       | Pa                    |
| $P_{HD,1}$  | HD pressure in Enclosure 1           | 1 $\times 10^{-7}$                                       | Pa                    |
| $P_{D_2,2}$ | Initial D$_2$ pressure in Enclosure 2 | 1 $\times 10^{-7}$                                      | Pa                    |
| $P_{H_2,2}$ | Initial H$_2$ pressure in Enclosure 2 | 6.3 $\times 10^{-2}$                                    | Pa                    |
| $P_{HD,2}$  | Initial HD pressure in Enclosure 2   | 1 $\times 10^{-7}$                                       | Pa                    |
| $P_{D_2,3}$ | Initial D$_2$ pressure in Enclosure 3 | 1 $\times 10^{-20}$                                     | Pa                    |
| $P_{H_2,3}$ | Initial H$_2$ pressure in Enclosure 3 | 1 $\times 10^{-20}$                                     | Pa                    |
| $P_{HD,3}$  | Initial HD pressure in Enclosure 3   | 1 $\times 10^{-20}$                                      | Pa                    |
| $P_{D_2,4}$ | D$_2$ pressure in Enclosure 4        | 1 $\times 10^{-10}$                                      | Pa                    |
| $P_{H_2,4}$ | H$_2$ pressure in Enclosure 4        | 1 $\times 10^{-10}$                                      | Pa                    |
| $P_{HD,4}$  | HD pressure in Enclosure 4           | 1 $\times 10^{-10}$                                      | Pa                    |
| $P_{H_2,5}$ | H$_2$ pressure in Enclosure 5        | 6.3 $\times 10^{-2}$                                     | Pa                    |
| $P_{HD,5}$  | HD pressure in Enclosure 5           | 1 $\times 10^{-10}$                                      | Pa                    |


!alert note title=Updates of times and initial pressures in val-2ee to be consistent with val-2ed.
In [!cite](ambrosek2008verification), the times and initial pressures in val-2ee are different from the values used in val-2ed. However, we use the same values from val-2ed in val-2ee for consistency. The trivial differences in times and initial pressures do not impact the final results.

Other case and model parameters used in TMAP8 are listed in [val-2e_parameters]:


!table id=val-2e_parameters caption=Values of material properties.
| Parameter | Description                          | Value                                                       | Units                 | Reference                 |
| --------- | ------------------------------------ | ----------------------------------------------------------- | --------------------- | --------------------- |
| $k_b$     | Boltzmann constant                   | 1.380649 $\times 10^{-23}$                                  | J/K                   | [PhysicalConstants.h](https://physics.nist.gov/cgi-bin/cuu/Value?k) |
| $R$       | Gas constant                         | 8.31446261815324                                            | J/mol/K               | [PhysicalConstants.h](https://physics.nist.gov/cgi-bin/cuu/Value?r) |
| $A$ | Surface area  | 1.8$\times 10^{-4}$                                      | m$^2$ | [!cite](kizu2001co) |
| $V$ | Enclosure volume   | 0.005     | m$^3$            | [!cite](kizu2001co) |
| $T_1$ | Temperature in val-2ea and val-2eb | 825                                          | K            | [!cite](kizu2001co) |
| $T_2$ | Temperature in val-2ec | 865                                          | K            | [!cite](kizu2001co) |
| $T_3$ | Temperature in val-2ed and val-2ee | 870                                          | K            | [!cite](kizu2001co) |
| $Q$   | Flow rate in all enclosures         | 0.1                       | m$^3$/s                   | [!cite](ambrosek2008verification) |
| $L_1$ | Thickness of membrane in val-2ea     | 5$\times 10^{-5}$         | m                    | [!cite](kizu2001co) |
| $L_2$ | Thickness of membrane in val-2eb, val-2ec, val-2ed, val-2ee | 2.5$\times 10^{-5}$ | m          | [!cite](kizu2001co) |
| $D_H$ | Hydrogen diffusivity in membrane         | 3.728$\times 10^{-4} \exp(-1315.8/T)$        | m$^2$/s              | [!cite](katz1960permeability) |
| $D_D$ | Deuterium diffusivity in membrane         | 2.636$\times 10^{-4} \exp(-1315.8/T)$        | m$^2$/s              | [!cite](ambrosek2008verification) |
| $K_{s,1}$ | Solubility of hydrogen isotope in val-2ea, val-2eb, val-2ec  | 1.511$\times 10^{23} \exp(-5918/T)$        | atom/m$^3$/Pa$^{0.9297}$  | [!cite](ambrosek2008verification) |
| $K_{s,2}$ | Solubility of hydrogen isotope in val-2ed, val-2ee  | 9.355$\times 10^{22} \exp(-5918/T)$        | atom/m$^3$/Pa$^{0.9297}$  | [!cite](ambrosek2008verification) |
| $n$ | exponent for the relation of pressure and concentration | 0.9297         | -                     | [!cite](kizu2001co) |
| $K_{r,D_2}$ | D$_2$ recombination coefficient | 2.502$\times 10^{-24} / \sqrt{4T} \exp(11836/T)$        | m$^4$/s              | [!cite](ambrosek2008verification) |
| $K_{r,H_2}$ | H$_2$ recombination coefficient | 2.502$\times 10^{-24} / \sqrt{2T} \exp(11836/T)$        | m$^4$/s              | [!cite](ambrosek2008verification) |
| $K_{r,HD}$ | HD recombination coefficient | 2.502$\times 10^{-24} / \sqrt{3T} \exp(11836/T)$        | m$^4$/s              | [!cite](ambrosek2008verification) |
| $K_{d,D_2}$ | D$_2$ dissociation coefficient | 2.1897$\times 10^{22} / \sqrt{4T}$     | molecular/m$^2$/Pa              | [!cite](ambrosek2008verification) |
| $K_{d,H_2}$ | H$_2$ dissociation coefficient | 2.1897$\times 10^{22} / \sqrt{2T}$     | molecular/m$^2$/Pa              | [!cite](ambrosek2008verification) |
| $K_{d,HD}$ | HD dissociation coefficient | 2.1897$\times 10^{22} / \sqrt{3T}$     | molecular/m$^2$/Pa              | [!cite](ambrosek2008verification) |

!alert warning title=Typo in [!cite](ambrosek2008verification)
There are typos in the equations for hydrogen diffusivity and recombination and dissociation coefficients in the input files from TMAP7 in val-2ed and val-2ee. The correct values are provided in [val-2e_parameters] and used in TMAP8. The pre-factor for hydrogen diffusivity used in TMAP8 is 3.728 $\times 10^{-4}$ m$^2$/s instead of 2.636 $\times 10^{-4}$ m$^2$/s as used in the input file published in [!cite](ambrosek2008verification). The activation energy for recombination coefficient used in TMAP8 is -11836 K (making the term in the exponential positive) instead of the 11836 K value used in the input file in [!cite](ambrosek2008verification) - note that the value listed in Eq. (71) in [!cite](ambrosek2008verification) is correct. The values of the species molecular weight in amu are also updated from the input files shown in [!cite](ambrosek2008verification).

!alert warning title=Solubility values for val-2ea, val-2eb, val-2ec differ from those for val-2ed, val-2ee
To achieve a lower RMSPE in [val-2e_comparison_diffusion], the solubility values for val-2ea, val-2eb, and val-2ec were taken from the simulation input files in [!cite](ambrosek2008verification), rather than using the values provided in the documentation in [!cite](ambrosek2008verification).

## Results

[val-2e_comparison_diffusion] shows the comparison of the TMAP8 calculation and the experimental data from [!cite](kizu2001co), including simulations val-2ea, val-2eb, and val-2ec. There are reasonable agreements between the TMAP predictions and the experimental data with root mean square percentage errors (RMSPE) of RMSPE = 23.51 %, 30.80 %, and 47.70 % for val-2ea, val-2eb, and val-2ec, respectively.

!media comparison_val-2e.py
       image_name=val-2e_comparison_diffusion.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=val-2e_comparison_diffusion
       caption= Comparison of the D$_2$ flux versus D$_2$ pressure on the upstream side of the membrane from TMAP8 calculation and the experimental data.

[val-2e_comparison_mixture_diffusion] shows the comparison of the D$_2$, H$_2$, and HD flux versus effective D$_2$ pressure on the upstream side of the membrane from val-2ed using TMAP8 assuming steady state for surface reactions (i.e., lawdep conditions) and the experimental data. The effective D$_2$ pressure is calculated using $P_{D_2} + 0.5 P_{HD}$. Although the total gas release is well captured, the release of individual gases is not well predicted, except for H$_2$ at low pressure and D$_2$ at high pressure. In this scenario, RMSPE = 76.26 %, 100.83 %, 115.79 %, and 10.77 % for H$_2$, D$_2$, HD, and the summation of all gases, respectively.

!media comparison_val-2e.py
       image_name=val-2e_comparison_mixture_diffusion.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=val-2e_comparison_mixture_diffusion
       caption= Comparison of the D$_2$, H$_2$, and HD flux versus effective D$_2$ pressure on the upstream side of the membrane from TMAP8 calculation using steady state surface condition (i.e., lawdep) for case val-2ed and the experimental data.

[val-2e_comparison_mixture_diffusion_recombination] shows the comparison of the D$_2$, H$_2$, and HD flux versus effective D$_2$ pressure on the upstream side of the membrane from val-2ee using TMAP8 accounting for dissociation and recombination at the membrane's surface (i.e.,  ratedep conditions) and the experimental data. There is a reasonable agreement between the TMAP8 predictions and the experimental data, except for the high pressure conditions greater than 0.1 Pa and for HD, especially at higher pressures. In this scenario, RMSPE = 11.34 %, 30.70 %, 79.72 %, 43.99 % for H$_2$, D$_2$, HD, and the summation of all gases, respectively.
Note that the agreement could be improved by adjusting the model parameters. It is also possible to perform this optimization with [MOOSE's stochastic tools module](https://mooseframework.inl.gov/modules/stochastic_tools/index.html).

!alert warning title=Typo in experimental data from [!cite](ambrosek2008verification)
The experimental data from [!cite](ambrosek2008verification) for all cases in val-2e are slightly lower than the experimental data from [!cite](kizu2001co). We have therefore extracted and used the original experimental data from [!cite](kizu2001co).

!media comparison_val-2e.py
       image_name=val-2e_comparison_mixture_diffusion_recombination.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=val-2e_comparison_mixture_diffusion_recombination
       caption= Comparison of the D$_2$, H$_2$, and HD flux versus effective D$_2$ pressure on the upstream side of the membrane from TMAP8 calculation capturing dissociation and recombination at the surface (i.e., ratedep conditions) for case val-2ee and the experimental data.

!alert note title=Difference between the simulation results from TMAP7 and TMAP8
Due to the corrected typos in [val-2e_parameters], the simulation results in val-2ed and val-2ee from TMAP8 differ from the results from TMAP7.

## Input files

!style halign=left
For this case, the main input files are [!file](/val-2ea.i), [!file](/val-2ed.i), and [!file](/val-2ee.i). Note that [!file](/val-2ed.i) and [!file](/val-2ee.i) utilize a common base file [!file](/val-2e_base_three_gases.i) with the line `!include val-2e_base_three_gases.i`, and [!file](/val-2ea.i) and [!file](/val-2e_base_three_gases.i) utilize a common base file [!file](/val-2e_base.i) with the line `!include val-2e_base.i`. The base input files contain all the features and TMAP8 objects common to these cases, reducing duplication. These files are also used as tests in TMAP8 at [!file](/val-2e/tests). Sub-cases `ver-1eb` and `ver-1ec` are adapted from [!file](/val-2ea.i), as it done in [!file](/val-2e/tests).

!alert tip title=Input file include syntax information
To learn more about the `!include` feature, refer to the [application_usage/input_syntax.md] page.

!bibtex bibliography
