# val-2b

# Diffusion Experiment in Beryllium

## Test Description

This validation problem is taken from [!cite](macaulay1991deuterium) and is part of the validation suite of TMAP4 and TMAP7 [!citep](longhurst1992verification,ambrosek2008verification), which we reproduce here, with some updates. This case has also been updated and extended in [!cite](Simon2025).

R.G. Macaulay-Newcombe et al. conducted thermal absorption and desorption experiments, as well as implantation experiments, on wafers of polished beryllium [!citep](macaulay1991deuterium).
Of the several data sets presented, the one modeled here is titled "run 2a1" and is represented in Fig. 2(a) in their publication [!citep](macaulay1991deuterium). The beryllium sample was 0.4 mm thick and had an area of 104 mm$^2$, as illustrated in [val-2b_schematic].
It was polished to a mirror finish and then exposed to 13.3 kPa of deuterium at 773 K for 50 hours. It was quickly cooled under a vacuum of about 1 $\mu$Pa. The cooling time constant for the apparatus is taken as 45 minutes, which is consistent with the assumption made in [!citep](longhurst1992verification,ambrosek2008verification).
After removing the sample from the charging furnace, it was transferred in the air to a thermal desorption furnace where the temperature was increased from ambient (300 K) to 1073 K at the rate of 3 K/min. This was done under vacuum, and the pressure of the chamber was monitored by the residual gas analysis and calibrated against standard leaks.
In that way, the emission rate from the sample could be measured as a function of temperature. The sample pressure and temperature histories are shown in [val-2b_temperature_pressure_history].
Experimental data from that measurement, given in Fig. 2(a) in [!cite](macaulay1991deuterium) are reproduced in [val-2b_comparison].

!media figures/val-2b_schematic.jpg
    style=width:75%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=val-2b_schematic
    caption=Schematic of the experiment setup (figure elements are not to scale).

!media comparison_val-2b.py
    image_name=val-2b_temperature_pressure_history.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=val-2b_temperature_pressure_history
    caption=Pressure and temperature histories.

!alert note title=Uncertainty about cooldown duration.
The exact duration of the cooldown period and its temperature history are uncertain. [!cite](macaulay1991deuterium) provides information about 24 hour-cooldown cycles, but it is unclear whether this applies to the charging chamber alone or to the sample as well. In parallel, [!citep](longhurst1992verification,ambrosek2008verification) assume that the cooldown lasted for 40 minutes. With an assumed cooling time constant for the apparatus of 45 minutes, this did not enable the sample to cool down to the starting temperature of the desorption phase of the experiment (i.e., 300 K). To model this case in TMAP8, we decided to select a cooldown duration that is long enough to bring the temperature of the sample to around 300 K, but did not unnecessarily increase the length of the history since no significant changes happen to the deuterium distribution at 300 K due to slow kinetics. For these reasons, we selected a cooldown duration of 5 hours, as shown in [val-2b_temperature_pressure_history].

From Rutherford backscattering measurements made on the samples before charging with deuterium, they deduced that the thickness of the oxide film was 18 nm. This is typical for polished beryllium. The metal is so reactive in air that the film forms almost immediately after any surface oxide removal. On the other hand, it is relatively stable and would only grow slightly when exposed to air between charging and thermal desorption.

## Model Description

This experiment is modeled using a two-segment model in TMAP8 with the segments linked. The first segment is the BeO film which is modeled using 18 elements, each 1 nm in length. The second segment is the beryllium with reflective boundary condition at the mid-plane. The beryllium segment is modeled using 40 elements, each 50 $\mu$m thick. The solubility of deuterium in beryllium used was that given by [!cite](wilson1990beryllium) at Sandia National Laboratory (SNL) based on the work done by W. A. Swansiger, also of SNL.

The diffusivity of deuterium in beryllium was measured by [!cite](abramov1990deuterium). They made measurements on high-grade (99$\%$ pure) and extra-grade (99.8$\%$ pure). The values used here are those for high-grade beryllium, consistent with Dr. Macaulay-Newcombe's measurements of the purity of his samples.

Deuterium transport properties of the BeO are more challenging. First, it is not clear in which state the deuterium exists in the BeO.
However, it has been observed [!cite](longhurst1990tritium) that an activation energy of -78 kJ/mol (exothermic solution) is evident for tritium coming out of neutron-irradiated beryllium in work done by D. L. Baldwin of Pacific Northwest Laboratory.
The same value of energy has appeared in other results. It can be inferred from Dr. Swansiger's work cited by [!cite](wilson1990beryllium) and by [!cite](causey1990tritium), among others, so one may be justified in using it.
Concerning the solubility, measurements reported by [!cite](macaulay1992thermal) and in follow-up conversations indicate about 200 appm of D in BeO after exposure to 13.3 kPa of D$_2$ at 773 K.
That suggests a coefficient of only 1.88 $\times$ 10$^{18}$ d/m$^3$Pa$^{1/2}$.
Since much of the deuterium in the oxide layer will get out during the cool-down process (and because it gives a good fit), the solubility coefficient is taken to be 5 $\times$ 10$^{20}$ d/m$^3$Pa$^{1/2}$.

Deuterium diffusion measurements in BeO were made by [!cite](fowler1977tritium). They found a wide range of results for diffusivity in BeO depending on the physical form of the material, having measured it for single-crystal, sintered, and powdered BeO. The model in [!citep](longhurst1992verification,ambrosek2008verification) uses one expression for the charging phase and another for the thermal desorption phase, believing that the surface film changed somewhat during the transfer between the two furnaces. For the charging phase diffusivity, the model uses 20 times that for the sintered BeO. Thermal expansion mismatches tend to open up cracks and channels in the oxide layer, so this seems a reasonable value. The same activation energy of 48.5 kJ/mol, is retained, however. For the thermal desorption phase, the diffusivity prefactor of the sintered material (7x10$^{-5}$ m$^2$/sec) and an activation energy of 223.7 kJ/mol (53.45 kcal/mol) are used. These values give results lying well within the scatter of Fowler's data. Exposure of the sample to air after heating should have made the oxide more like a single crystal by healing the cracks that may have developed.

## Case and Model Parameters

Diffusivities and solubilities used in the simulation are listed in [val-2b_parameters].

!table id=val-2b_parameters caption=Model parameter values for the charging and the desorption phases [!citep](longhurst1992verification,ambrosek2008verification). $T$ is the temperature in Kelvin.
| Property of deuterium | Value for charging phase              | Value for desorption phase            | Units               |
| --------------------- | ------------------------------------- | ------------------------------------- | ------------------- |
| Diffusivity in Be     | $8.0 \times 10^{-9} \exp(-4220/T)$    | $8.0 \times 10^{-9} \exp(-4220/T)$    | m$^2$/s             |
| Diffusivity in BeO    | $1.40 \times 10^{-4} exp(-24408/T)$   | $7 \times 10^{-5} \exp(-27000/T)$     | m$^2$/s             |
| Solubility in Be      | $7.156 \times 10^{27} \exp(-11606/T)$ | $7.156 \times 10^{27} \exp(-11606/T)$ | at/m$^3$/Pa$^{1/2}$ |
| Solubility in BeO     | $5.00 \times 10^{20} \exp(9377.7/T)$  | $5.00 \times 10^{20} \exp(9377.7/T)$  | at/m$^3$/Pa$^{1/2}$ |

Other parameters used in the simulation are listed in [val-2b_other_parameters].

!table id=val-2b_other_parameters caption=Values of other modeling properties.
| Parameter | Description                          | Value                                                       | Units                 | Reference                 |
| --------- | ------------------------------------ | ----------------------------------------------------------- | --------------------- | --------------------- |
| $l_{Be}$       | thickness of Be                     | 0.4                                           | mm                     | [!cite](anderl1985tritium) |
| $l_{BeO}$       | thickness of BeO                     | 18                                           | nm                     | [!cite](anderl1985tritium) |
| $A$       | area of sample                     | 104                                           | mm$^2$                     | [!cite](anderl1985tritium) |
| $P_1$       | pressure during absorption                     | 13.3                            | kPa                     | [!cite](anderl1985tritium) |
| $P_2$       | pressure during cooldown                     | 1                            | $\mu$Pa                     | [!cite](anderl1985tritium) |
| $P_3$       | pressure during desorption                     | 1000                            | $\mu$Pa                     | [!cite](anderl1985tritium) |
| $T_1$       | temperature during absorption                  | 773          | K                     | [!cite](anderl1985tritium) |
| $T_2$       | final temperature during cooldown                | 300                | K                     | [!cite](anderl1985tritium) |
| $T_3$       | final temperature during desorption                | 1073                | K                     | [!cite](anderl1985tritium) |
| $k_T$       | heating rate                | 3                | K/min                     | [!cite](anderl1985tritium) |

The model applies 13.3 kPa of D$_2$ for 50 hours and 15 seconds followed by cool down with a 45 minute time constant at 1 $\mu$Pa for five hour ([!cite](longhurst1992verification,ambrosek2008verification) used 40 minutes, but we extend it here to 5 hours to let the temperature go down closer to 300 K - see [val-2b_temperature_pressure_history]). The deuterium concentrations in the sample have a complex distribution that results from first charging the sample and then discharging it during the cool down. This problem is then restarted with different model parameters (see [val-2b_parameters]) to simulate thermal desorption in a $1 \times 10^{-3}$ Pa environment that begins at 300 K and goes to 1073 K at 3 K/min.

## Results

[val-2b_comparison] shows the comparison of the TMAP8 calculation and the experimental data during desorption. There is reasonable agreement between the TMAP predictions and the experimental data with a root mean square percentage error of RMSPE = 22.44 %. Note that the agreement could be improved by adjusting the model parameters. It is also possible to perform this optimization with [MOOSE's stochastic tools module](https://mooseframework.inl.gov/modules/stochastic_tools/index.html), which has been demonstrated in [!cite](Simon2025) with parallel subset simulation and in [!cite](DHULIPALA2026102776) with batch Bayesian optimization. The latter approach has been shown to be more computationally efficient than parallel subset simulation.

!media comparison_val-2b.py
       image_name=val-2b_comparison.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=val-2b_comparison
       caption=Comparison of TMAP8 calculation against experimental data, which shows TMAP8's ability to accurately model this validation case.

!alert note title=Experimental data from [!cite](macaulay1991deuterium).
The experimental data used in this case comes directly from Figure (2) in [!cite](macaulay1991deuterium). This is in contrast with the data used in [!cite](longhurst1992verification,ambrosek2008verification), which, although the scale of the data is very similar, differs slightly. Also, note that the units in Figure (2) from [!cite](macaulay1991deuterium) should be atoms/mm$^2$/s $\times 10^{10}$ instead of atoms/mm$^2$ $\times 10^{10}$, which is corrected in [val-2b_comparison].

To verify that the solubility ratio at the interface between the beryllium and its oxide is appropriately modeled, [val-2b_ratio] compares the known solubility ratio with the calculated deuterium concentration ratio at the interface, and they match, as expected.

!media comparison_val-2b.py
       image_name=val-2b_ratio.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=val-2b_ratio
       caption=Solubility and concentration ratio at the Be-BeO interface. The match shows that the solubility difference is properly enforced in TMAP8.

## Input files

!style halign=left
The input file for this case can be found at [!file](/val-2b.i).
To achieve short regression tests (under 2 seconds walltime), the tests in [!file](/val-2b/tests) run a version of the files with a shorter history, looser tolerance, and larger time step. More information about the changes can be found in the test specification file for this case, namely [!file](/ver-1d/tests).

!alert note title=TMAP8 can run this case in one simulation.
In TMAP4 and TMAP7, this case was divided in two simulations to accommodate the different model parameters used during charging and desorption (see [val-2b_parameters] ) [!citep](longhurst1992verification,ambrosek2008verification). In TMAP8, the full history is modeled in one simulation using [!file](/val-2b.i).

!bibtex bibliography
