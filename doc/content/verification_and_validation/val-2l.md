# Deuterium Retention in Neutron-irradiated Tungsten


## Case Description

This validation case is based on the thermal desorption spectroscopy (TDS) experiments and TMAP7 analysis reported by [!cite](Shimada2011). The experiments compared deuterium release from unirradiated tungsten (0 dpa) and neutron-irradiated tungsten (0.025 dpa) after high-flux deuterium-plasma exposure.

!alert note title=Scope of the current validation
The present implementation addresses only the unirradiated sample and benchmarks the TMAP8 result against TMAP7 fit A in Figure 3 of [!cite](Shimada2011). It does not yet validate the neutron-irradiated case. A future extension will add the trap populations required to model the irradiated sample.

For the unirradiated sample, [!cite](Shimada2011) reported a narrow release spectrum between approximately 450 K and 700 K. Their TMAP7 Fit A validated against this spectra assuming a uniform concentration of 4 at.% 1.35 eV traps to a depth of 0.7 $\mu$m.

The objectives of this first stage of `val-2l` are to:

1. Reproduce the unirradiated TMAP7 Fit A model in TMAP8;
2. Compare the TMAP8 desorption flux with the digitized experimental TDS data;
3. Verify that the deuterium inventory and integrated surface release satisfy mass conservation;
4. Establish a model that can later be extended to the neutron-irradiated sample; and
5. Perform PSS optimization on that model characterize uncertainty in the chosen material properties in the simulations in [!cite](Shimada2011).

## Experimental Description

The tungsten specimens were 6 mm-diameter, 0.2 mm-thick discs made from 99.99 at.% polycrystalline tungsten. Both the unirradiated and irradiated specimens were exposed to 100 eV deuterons at a nominal flux of $5\times10^{21}$ m$^{-2}$ s$^{-1}$ and a fluence of $4\times10^{25}$ m$^{-2}$ while the specimen temperature was maintained at 473 K [!cite](Shimada2011). After exposure, deuterium release was measured using TDS.

The measured temperature history is prescribed directly in the TMAP8 model rather than approximated by a constant heating rate. It is imperative that we capture the correct temperature history, as sharp TDS spectra coincide with temperature fluctuations between roughly 100-150 seconds and 200-250 seconds for the neutron-irradiated sample. The digitized version of this temperature history is found in [val-2l_temperature_history].

!media comparison_val-2l.py
    image_name=val-2l_temperature_history.png
    id=val-2l_temperature_history
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    caption=Temperature history prescribed during the TDS simulation. The inset highlights the early-time temperature fluctuations reported during the experiment.

## Model Description

### Geometry and mesh

TMAP8 models the tungsten disc as a one-dimensional domain through its full 0.2 mm thickness. The two ends of the domain represent the two exposed circular surfaces of the disc. The mesh is segmented and refined near the upstream surface so that the 0.7 micrometer Fit A trap boundary lies on a mesh node. The remaining thickness is progressively coarsened away from the trapped region.

### Governing equations

The physical mobile-species balance is

!equation id=val-2l_mobile_balance
\frac{\partial C_M}{\partial t} - \nabla \cdot \left(D(T) \nabla C_M\right) + \sum_{i=1}^{N_{trap}}f_{T/M_i}\frac{\partial C_{T_i}}{\partial t} = 0,

where $C_M$ and $C_{T_i}$ are the concentration of the mobile and trapped species, respectively, $t$ is the time, $D(T)$ is the temperature-dependent diffusivity of deuterium in tungsten, N_{trap} is the number of traps, and $f_{T/M}$ is a user-defined numerical scaling factor for better numerical convergence. The deuterium diffusivity follows the Frauenfelder [!cite](frauenfelder1969solution) relation corrected for deuterium and reported by [!cite](Causey2002):

!equation id=val-2l_diffusivity
D(T)=D_0\exp\left(-\frac{E_D}{k_B T}\right).

The trapped-species balance is represented by the TMAP8 trapping and release kernels,

!equation id=val-2l_trap_balance
\frac{\partial C_{T_i}}{\partial t} = \alpha_t^i \frac{C_{T_i}^{\text{empty}} C_M}{(N f_{T/M,i})} - \alpha_r^i C_{T_i},

where the terms in the right-hand side represent trapping and release, respectively. $\alpha_r^i$ and $\alpha_t^i$ are the release and trapping rate coefficients for trap $i$, $N$ is the tungsten material density, and $C_{T_i}^{empty}$ is the concentration of empty trapping sites of type $i$, defined as

\begin{equation} \label{eqn:trapping_empty}
    C_{T_i}^{empty} = (C_{{T_i}0} N - f_{T/M,i} C_{T_i}  ) ,
\end{equation}

where $C_{{T_i}0}$ is the fraction of host sites $i$ that can contribute to trapping.

### Initial and boundary conditions

The mobile concentration is initially zero. The single Fit A trap population is initially saturated and distributed uniformly from the upstream surface to a depth of 0.7 micrometers. No traps are assigned beyond that depth.

Finite recombination boundary conditions are applied at the upstream and downstream surfaces:

!equation id=val-2l_recombination
J = -D\nabla C_M = 2K_r(T)C_M^2,

with $K_r$ selected by [!cite](Shimada2011) from [!cite](anderl1992deuterium),

!equation id=val-2l_recombination_coefficient
K_r(T)=K_{r,0}\exp\left(-\frac{E_r}{k_B T}\right).

The simulation begins at the first temperature in the digitized experimental temperature history and runs for 2 h. The plasma-exposure stage is not simulated; its effect is represented by the prescribed initial trapped-deuterium profile.

## Case and Model Parameters

The physical parameters currently used for the unirradiated Fit A benchmark are summarized in [val-2l_parameters].

!table id=val-2l_parameters caption=Experimental and physical model parameters for the current unirradiated TMAP7 Fit A benchmark.
| Parameter | Description | Value | Units | Reference |
| :- | :- | -: | :- | :- |
| $L$ | Tungsten thickness | 0.2 | mm | [!cite](Shimada2011) |
| $d$ | Disc diameter | 6 | mm | [!cite](Shimada2011) |
| $T_{\mathrm{exposure}}$ | Plasma-exposure temperature | 473 | K | [!cite](Shimada2011) |
| $D_0$ | Deuterium diffusivity prefactor | $2.9\times10^{-7}$ | m$^2$/s | [!cite](frauenfelder1969solution,Causey2002) |
| $E_D$ | Deuterium diffusion activation energy | 0.39 | eV | [!cite](frauenfelder1969solution,Causey2002) |
| $K_{r,0}$ | Recombination coefficient prefactor | $3.2\times10^{-15}$ | m$^4$/atom/s | [!cite](anderl1992deuterium) |
| $E_r$ | Recombination activation energy | 1.16 | eV | [!cite](anderl1992deuterium) |
| $f_t$ | TMAP7 Fit A trap atomic fraction | 0.04 | - | [!cite](Shimada2011) |
| $x_t$ | TMAP7 Fit A trap depth | 0.7 | $\mu$m | [!cite](Shimada2011) |
| $E_{\mathrm{detrap}}$ | Fit A detrapping energy | 1.35 | eV | [!cite](Shimada2011) |
| $N_W$ | Tungsten atomic density | $6.25\times10^{28}$ | atom/m$^3$ | [!cite](ambrosek2008verification) |
| $\alpha_{t,0}$ | Trapping prefactor | $9.1316\times10^{12}$ | s$^{-1}$ | [!cite](ambrosek2008verification) |
| $\alpha_{r,0}$ | Release prefactor | $8.4\times10^{12}$ | s$^{-1}$ | [!cite](ambrosek2008verification) |

The concentration variables are rescaled internally by a factor of $10^4$ to improve nonlinear convergence. This scaling does not change the physical trap concentration reported above.


## Results

### Temperature-dependent diffusivity

[val-2l_diffusivity_plot] confirms that the TMAP8 material follows the prescribed Arrhenius relationship over the experimental temperature range.

!media comparison_val-2l.py
    image_name=val-2l_diffusivity_vs_temperature.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=val-2l_diffusivity_plot
    caption=Deuterium diffusivity in tungsten evaluated from the TMAP8 material model as a function of reciprocal temperature.

### Unirradiated desorption benchmark

[val-2l_comparison] compares the TMAP8 desorption flux with the digitized unirradiated experimental data from [!cite](Shimada2011). The comparison is evaluated over the interval from 800 s to 2800 s, which contains the primary desorption peak.

!media comparison_val-2l.py
    image_name=val-2l_comparison_desorption.png
    id=val-2l_comparison
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    caption=Comparison of the TMAP8 prediction using the TMAP7 Fit A parameters with the unirradiated experimental TDS data reported by [!cite](Shimada2011).

The current comparison script calculates the mean-normalized root-mean-squared-percentage error,

!equation id=val-2l_error_metric
\mathrm{RMSPE} = \frac{\sqrt{\sum_{i=1}^{n}\left(J_{\mathrm{TMAP8},i}-J_{\mathrm{exp},i}\right)^2/n}}{\sum_{i=1}^{n}J_{\mathrm{exp}}/n}\times100

### Deuterium inventory and mass conservation

[val-2l_inventory] shows the simulated mobile and trapped inventories of deuterium over the duration of the TDS experiment along with the temperature profile.

!media comparison_val-2l.py
    image_name=val-2l_inventory.png
    id=val-2l_inventory
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    caption=Mobile, trapped, and total deuterium inventories during the unirradiated TDS calculation.

The mass-balance residual is computed from the change in retained deuterium plus the time-integrated release through both surfaces. A value close to zero in [val-2l_mass_conservation] indicates that the numerical solution conserves mass.

!media comparison_val-2l.py
    image_name=val-2l_mass_conservation.png
    id=val-2l_mass_conservation
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    caption=Deuterium mass-balance residual normalized by the initial deuterium inventory.

## Discussion and Limitations

This stage of `val-2l` is intentionally limited to the unirradiated Fit A case. It exercises temperature-dependent diffusion, trapping and release, finite surface recombination, a measured temperature history, and inventory accounting in TMAP8. The comparison does not establish that the Fit A trap distribution is unique. In [!cite](Shimada2011), Fit A was calibrated to the TDS spectrum alone and did not reproduce the measured NRA depth profile.

## PSS Optimization

PSS optimization details will go here.

### Planned extension to the neutron-irradiated case

The neutron-irradiated specimen (0.025 dpa) exhibited a much broader desorption spectrum than the unirradiated specimen and required multiple trap populations in the TMAP7 analysis [!cite](Shimada2011). A later extension of `val-2l` will:

1. add the irradiated experimental TDS and temperature-history data;
2. introduce multiple trap populations to attempt to capture multiple sharp spectra;
3. document the irradiation history and the assumptions required, exploring modeling techniques to represent damage to tungsten;
4. perform mass conservation and validation checks incrementally
5. optimize material properties for chosen trap distributions and types

## Input Files

The files used in the current unirradiated benchmark are:

- [test/tests/val-2l/val-2l.params](val-2l.params), which contains the physical and numerical parameters;
- [test/tests/val-2l/val-2l.i](val-2l.i), which defines the one-dimensional transport, trapping, release, surface recombination, and postprocessing model;

!bibtex bibliography
