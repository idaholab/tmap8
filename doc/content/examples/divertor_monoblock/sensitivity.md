# Divertor Monoblock Sensitivities

This page documents sensitivity studies of different operating conditions performed on the [Divertor Monoblock](examples/divertor_monoblock/index.md). The original pulsed operation of the divertor monoblock model was modified according to [!cite](Hodille2021126003) towards a single-long tritium and heat flux pulse of an approximate equivalent total fluence. An initial sensitivity study on was performed on the divertor monoblock's boundary conditions under the steady pulse condition using the [Sobol Method](https://mooseframework.inl.gov/modules/stochastic_tools/examples/sobol.html) and other tools within the [Stochastic Tools Module](https://mooseframework.inl.gov/modules/stochastic_tools/). Two additional sensitivity studies were performed on select transients obtained from [!cite](ELMORSHEDY2024101616) and [!cite](Kessel01092013).

## General description of the sensitivity studies and the modified cases

### Introduction

!style halign=left
Many fusion components, especially those exposed to especially unique or extreme conditions, often lack sufficient operation data to evaluate their reliability, availability, maintainability, and inspectability (RAMI). As a proof-of-concept, we seek to  construct a Probabilistic Physics of Failure (PPoF) model of a tokomak divertor system to obtain failure rate metrics and lifetime metric relevant to the RAMI of a nuclear fusion reactor.

To accomplish this, sensitivity studies on the [Divertor Monoblock](examples/divertor_monoblock/index.md) model described in [!cite](Shimada2024114438) will be performed for (1) steady state conditions based on ITER data [!cite](Hodille2021126003), (2) an inadvertent shutdown transient [!cite](ELMORSHEDY2024101616), and (3) an edge-localized mode transient [!cite](Kessel01092013). The sensitivity studies will be performed using the [MOOSE](https://mooseframework.inl.gov/) Stochastic Module and its Sobol Method according to [!cite](SALTELLI2002280). The results of the sensitivity studies will be evaluated for state limits associated with heat transfer and tritium migration physics included in the [Divertor Monoblock](examples/divertor_monoblock/index.md).

First, the modifications made to the [Divertor Monoblock](examples/divertor_monoblock/index.md) model will be described. Second, the conditions the divertor monoblock was subjected to in the steady and transient scenarios will be described. Finally, the results of the sensitivities, namely the first and second order sensitivity indices, example correlations and state frequencies will be presented.

### Divertor Monoblock modifications

The pulsed operation of the divertor monoblock is relatively computationally expensive to accurately model since it requires taking small time steps to capture transients.
For a sensitivity analysis study, where many simulations are required, lowering the cost of individual simulations is paramount.
So as a first approximation, we replace the pulsed operation with a single steady pulse in this study.

### Steady operation

The sensitivity studies must sample from a distribution of parameters to determine the net effects of those parameters
on the model. Here, we vary the incident heat flux, retained tritium surface flux, coolant temperature, and coolant tritium concentration. For all these parameters, the sampling is done from
uniform distributions as shown in [tab:steady_case] and [fig:steady_inputs]. It should be noted that the coolant temperature is unusually high
in this case, as the ITER divertor is designed to have coolant run at 100&deg;C with a 50&deg;C temperature increase at the outlet [!cite](hirai2010iter); however, this is
 the designed 240&deg;C temperature for the divertor to run high-pressure water in the bake-off regime for tritium unloading.

!table id=tab:steady_case caption=Steady case varied boundary conditions.
| Parameter | Samples | Nominal Value | Distribution | Deviation |
| --- | --- | --- | --- | --- |
| Incident Heat Flux | 100 | 10 MW/m$^2$ [!cite](pitts2009iter)| Uniform | $\pm$5% |
| Retained Tritium Surface Flux | 100 | 7.89$\times$10$^{-9}$ m/s (normalized) | Uniform | $\pm$5% |
| Coolant Temperature | 100 | 552 K [!cite](hirai2010iter)| Uniform | $\pm$5% |
| Coolant Tritium Concentration | 100 | 1.0$\times$10$^{-18}$ (normalized) | Uniform | $\pm$1% |

!media divertor_monoblock_sensitivity.py image_name=divertor_monoblock_sensitivity_figures/steady_state_inputs.png id=fig:steady_inputs
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       caption=Distribution of sampled steady-state parameter values.

### Transient case: inadvertent shutdown

!style halign=left

For a transient case of an inadvertent shutdown, we modify parameters as shown in [tab:inadvertent_shutdown_case] and [fig:shutdown_inputs]. This case is modified such that we assume constant operation for 5.5 hours before encountering a `Peak Heat Flux` (and proportionally scaled retained tritium surface flux) for the sampled `Peak Duration` before resuming at one-tenth the heat and tritium flux of the original steady-state.

The top boundary retained tritium surface flux and heat flux are both adjusted to be a function of time, with functions defined in the input file as follows.

!listing test/tests/divertor_monoblock/shutdown_transient_runner.i block=Functions/retained_t_surface_flux_function link=false

!listing test/tests/divertor_monoblock/shutdown_transient_runner.i block=Functions/temperature_flux_bc_function

!table id=tab:inadvertent_shutdown_case caption=Inadvertent shutdown varied parameter space.
| Parameter | Samples | Nominal Value | Distribution | Deviation |
| --- | --- | --- | --- | --- |
| Peak Duration | 1000 | 1s | Normal | $\sigma$=$\pm$5% |
| Peak Heat Flux | 1000 | 20 MW/m$^2$ | Normal | $\sigma$=$\pm$5% |
| Coolant Temperature | 1000 | 552 K [!cite](hirai2010iter) | Normal | $\sigma$=$\pm$5% |
| Tungsten Conductivity | 1000 | 0.95 W/m K [!cite](Shimada2024114438) | Uniform | $\pm$5% |

!media divertor_monoblock_sensitivity.py image_name=divertor_monoblock_sensitivity_figures/transients_inputs.png id=fig:shutdown_inputs
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       caption=Distribution of sampled transient shutdown characteristics.

### Transient case: edge-localized mode disruption

!style halign=left
To simulate an edge-localized mode (ELM) disruption, we simulate a set of input conditions as described in [tab:elm_transient_case]. The heat flux is much larger than the transient shutdown case, but over a shorter duration. Most of the parameters will be selected from a normal distribution, as they reflect variations around some target or estimated value. The results will be shown below in [fig:elm_correlation]. We use the same tungsten conductivity as in [!cite](Shimada2024114438), but vary the conductivity by a constant factor in the range of $\pm$5%.

!table id=tab:elm_transient_case caption=Edge-localized mode transient case parameter space.
| Parameter | Samples | Nominal Value | Distribution | Deviation |
| --- | --- | --- | --- | --- |
| Peak Duration | 1000 | 1.32 ms | Normal | $\sigma$=$\pm$5% |
| Peak Heat Flux | 1000 | 1147 MW/m$^2$ [!cite](loarte2017elms) | Normal | $\sigma$=$\pm$5% |
| Coolant Temperature | 1000 | 552 K [!cite](hirai2010iter)| Normal | $\sigma$=$\pm$5% |
| Tungsten Conductivity | 1000 | 0.95 W/m K [!cite](Shimada2024114438) | Uniform | $\sigma$=$\pm$5% |


## Results

### Steady operation

For purposes of comparison, we look at the maximum observed tungsten temperature and the scaled permeation flux with regards to the heat flux in [fig:ss_correlation].
The maximum tungsten temperature naturally correlates with the heat flux, but also depends on thermal conductivity and coolant temperature, as expected.
The link between heat flux and tritium flux is not as strong. In general, larger values of tritium flux to the coolant are obtained with higher heat flux, which is the results from increased diffusivity and temperatures more likely to be sufficient for tritium release from traps.
However, small tritium flux values are still obtained when a large heat flux is applied. This is attributed to lower temperatures towards the coolant (due to cooler coolant or higher thermal conductivity).
Note, however, that low tritium flux are less likely as the heat flux increases.

!media divertor_monoblock_sensitivity.py image_name=divertor_monoblock_sensitivity_figures/steady_comparison.png id=fig:ss_correlation
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       caption=Correlation between the incident heat flux and the maximum temperature of the tungsten, as well as the total (scaled) permeation flux of tritium into the coolant.

### Inadvertent shutdown

For the inadvertent shutdown case, we can correlate the input parameters with several output parameters. Perhaps most interesting is the relationship between coolant temperature and the scaled tritium flux, where tritium does not permeate effectively for coolant temperatures below about 550 K. In [fig:shutdown_correlation], the upper plots are scatterplots, the lower are kernel density plots and the diagonal are histograms.

!media divertor_monoblock_sensitivity.py image_name=divertor_monoblock_sensitivity_figures/shutdown_pairplots.png id=fig:shutdown_correlation
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       caption=Correlation between the input parameters and several metrics of performance in an inadvertent shutdown scenario.

The results of the simulation are shown in [fig:shutdown_results]. As would be expected, the amount of permeation and the amount of tritium retention have an approximately inverse relationship, and the pairwise interactions across the board are shown. The time at which maximum temperatures occur are all correlated, as one might expect.

!media divertor_monoblock_sensitivity.py image_name=divertor_monoblock_sensitivity_figures/shutdown_transient_results.png id=fig:shutdown_results style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       caption=Distribution of sampled postprocessor values in the inadvertent shutdown case.


### Edge-localized mode disruption

For the case of simulating an ELM disruption event, we show in [fig:elm_correlation] that although the operating conditions vary, the trends are substantially the same.

!media divertor_monoblock_sensitivity.py image_name=divertor_monoblock_sensitivity_figures/elm_pairplots.png id=fig:elm_correlation
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       caption=Correlation between the incident heat flux and the maximum temperature of the tungsten, as well as the total (scaled) permeation flux of tritium.

## Complete input files

Below are the complete input files for the various sensitivity studies. Note that none of the inputs have been optimized for computational costs.

### Steady operation

#### Subapp input

!listing test/tests/divertor_monoblock/steady_state_runner.i link=false

#### Controller input

!listing test/tests/divertor_monoblock/steady_state_sobol.i link=false

### Inadvertent shutdown

#### Subapp input

!listing test/tests/divertor_monoblock/shutdown_transient_runner.i link=false

#### Controller input

!listing test/tests/divertor_monoblock/shutdown_transient_sobol.i link=false

### Edge-localized mode disruption

#### Subapp input

!listing test/tests/divertor_monoblock/elm_transient_runner.i link=false

#### Controller input

!listing test/tests/divertor_monoblock/elm_transient_sobol.i link=false
