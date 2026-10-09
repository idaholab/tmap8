# Deuterium Retention in Neutron-irradiated Tungsten


## Case Description

This validation case is based on the thermal desorption spectroscopy (TDS) experiments and TMAP7 simulations reported by [!cite](Shimada2011). The experiments compared deuterium release from unirradiated tungsten (0 dpa) and neutron-irradiated tungsten (0.025 dpa) after high-flux deuterium-plasma exposure.

!alert note title=Scope of the current validation
The present implementation addresses only the unirradiated sample and compares the TMAP8 result against TMAP7 fit A in Figure 3 of [!cite](Shimada2011). It does not yet validate the neutron-irradiated case. A future extension will enhance the model to capture the behavior of the irradiated sample.

For the unirradiated sample, [!cite](Shimada2011) reported a narrow release spectrum between approximately 450 K and 700 K. Their TMAP7 Fit A assumes a uniform concentration of 4 at.% 1.35 eV traps to a depth of 0.7 $\mu$m.

The objectives of this first stage of `val-2l` are to:

1. Validate TMAP8 predictions against the experimental TDS data for the unirradiated sample;
2. Compare the TMAP8 results with the TMAP7 Fit A model;
3. Verify that the deuterium inventory and integrated surface release satisfy mass conservation;
4. Establish a model that can later be extended to the neutron-irradiated sample.

## Experimental Description

The tungsten specimens were 6 mm-diameter, 0.2 mm-thick discs made from 99.99 at.% polycrystalline tungsten. Both the unirradiated and irradiated specimens were exposed to 100 eV deuterons at a nominal flux of $5\times10^{21}$ m$^{-2}$ s$^{-1}$ and a fluence of $4\times10^{25}$ m$^{-2}$ while the specimen temperature was maintained at 473 K [!citep](Shimada2011). After exposure, deuterium release was measured using TDS.

The measured temperature history is prescribed directly in the TMAP8 model rather than approximated by a constant heating rate. It is imperative that we capture the correct temperature history, as sharp TDS spectra coincide with temperature fluctuations between roughly 100-150 seconds and 200-250 seconds for the neutron-irradiated sample. This temperature history is found in [val-2l_temperature_history].

!media comparison_val-2l.py
    image_name=val-2l_temperature_history.png
    id=val-2l_temperature_history
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    caption=Temperature history prescribed during the TDS simulation. The inset highlights the early-time temperature fluctuations reported during the experiment in [!cite](Shimada2011).

## Model Description

### Geometry and mesh

We model the tungsten disc as a one-dimensional domain through its full 0.2 mm thickness. The two ends of the domain represent the two exposed circular surfaces of the disc. The mesh is segmented and refined near the upstream surface so that the 0.7 micrometer Fit A trap boundary lies on a mesh node. The remaining thickness is progressively coarsened away from the trapped region.

### Governing equations

The physical mobile-species balance is

!equation id=val-2l_mobile_balance
\frac{\partial C_M}{\partial t} - \nabla \cdot \left(D(T) \nabla C_M\right) + \sum_{i=1}^{N_{trap}}f_{T/M_i}\frac{\partial C_{T_i}}{\partial t} = 0,

where $C_M$ and $C_{T_i}$ are the concentration of the mobile and trapped species, respectively, $t$ is the time, $D(T)$ is the temperature-dependent diffusivity of deuterium in tungsten, $N_{trap}$ is the number of traps, and $f_{T/M_i}$ is a user-defined numerical scaling factor for better numerical convergence. The deuterium diffusivity follows the Frauenfelder [!citep](frauenfelder1969solution) relation corrected for deuterium, as reported by [!cite](Causey2002):

!equation id=val-2l_diffusivity
D(T)=D_0\exp\left(-\frac{E_D}{k_B T}\right).

The trapped-species balance is governed by trapping and release:

!equation id=val-2l_trap_balance
\frac{\partial C_{T_i}}{\partial t} = \alpha_t^i \frac{C_{T_i}^{\text{empty}} C_M}{(N f_{T/M,i})} - \alpha_r^i C_{T_i},

where the terms in the right-hand side represent trapping and release, respectively. $\alpha_r^i$ and $\alpha_t^i$ are the release and trapping rate coefficients for trap $i$, $N$ is the density of tungsten, and $C_{T_i}^{empty}$ is the concentration of empty trapping sites of type $i$, defined as

\begin{equation} \label{eqn:trapping_empty}
    C_{T_i}^{empty} = (C_{{T_i}0} N - f_{T/M,i} C_{T_i}  ) ,
\end{equation}

where $C_{T_{i,0}}$ is the fraction of host sites of type $i$ that can contribute to trapping.
Note that in this model, TMAP8 accounts for a single trapping population, which is consistent with the TMAP7 fit A model in [!cite](Shimada2011), so $N_{trap}=1$.

### Initial and boundary conditions

The initial conditions are:

!equation id=val-2l_initial_condition
C_M(x,0) = 0, \quad C_{T_1}(x,0) = \begin{cases}
\frac{C_{T_1,0} N}{f_{T/M}} & \text{if } x \leq 0.7~\mu\text{m} \\
0 & \text{if } x > 0.7~\mu\text{m}
\end{cases}

The mobile concentration is initially zero. Further, we assume that the single trap population is initially saturated, meaning that the trapped concentration equals the trap site density divided by the scaling factor, corresponding to zero empty trap sites ($C_{T_1}^{\text{empty}} = 0$) in the trapped region. No traps are present beyond 0.7 μm depth.

Finite recombination boundary conditions were selected for TMAP7 fit A in [!cite](Shimada2011). However, homogeneous Dirichlet boundary conditions, representing infinite recombination, show better agreement with the TDS data and are applied at both the upstream and downstream surfaces:

!equation id=val-2l_dirichlet
C_M = 0.

The simulation begins at the first temperature in the experimental temperature history and runs for 2 h. The plasma-exposure stage is not simulated; its effect is represented by the prescribed initial trapped-deuterium profile.

## Case and Model Parameters

The physical parameters are summarized in [val-2l_parameters].

!table id=val-2l_parameters caption=Experimental and physical model parameters for the current unirradiated validation case.
| Parameter | Description | Value | Units | Reference |
| :- | :- | -: | :- | :- |
| $L$ | Tungsten thickness | 0.2 | mm | [!cite](Shimada2011) |
| $d$ | Disc diameter | 6 | mm | [!cite](Shimada2011) |
| $T_{\mathrm{exposure}}$ | Plasma-exposure temperature | 473 | K | [!cite](Shimada2011) |
| $D_0$ | Deuterium diffusivity prefactor | $2.9\times10^{-7}$ | m$^2$/s | [!cite](frauenfelder1969solution,Causey2002) |
| $E_D$ | Deuterium diffusion activation energy | 0.39 | eV | [!cite](frauenfelder1969solution,Causey2002) |
| $f_t$ | TMAP7 Fit A trap atomic fraction | 0.04 | - | [!cite](Shimada2011) |
| $x_t$ | TMAP7 Fit A trap depth | 0.7 | $\mu$m | [!cite](Shimada2011) |
| $E_{\mathrm{detrap}}$ | Detrapping energy | 1.30 | eV | [!cite](Shimada2011) |
| $N$ | Tungsten atomic density | $6.25\times10^{28}$ | atom/m$^3$ | [!cite](ambrosek2008verification) |
| $\alpha_{t,0}$ | Trapping prefactor | $9.1316\times10^{12}$ | s$^{-1}$ | [!cite](ambrosek2008verification) |
| $\alpha_{r,0}$ | Release prefactor | $8.4\times10^{12}$ | s$^{-1}$ | [!cite](ambrosek2008verification) |

!alert note title=Detrapping energy selection
[!cite](Shimada2011) considered detrapping energies in the range of 1.30 to 1.50 eV for the various TMAP7 fits. The value of 1.30 eV, at the bottom of this range, was selected for the TMAP8 implementation as it provides improved agreement with the experimental TDS data compared to the value of 1.35 eV selected for TMAP7 fit A.

## Results

### Unirradiated desorption validation

Define the TDS flux root-mean-squared-percentage error (RMSPE) for both TMAP8 and TMAP7 Fit A against the experimental data as:

!equation id=val-2l_error_metric
\mathrm{RMSPE} = \frac{\sqrt{\sum_{i=1}^{n}\left(J_{\mathrm{TMAP},i}-J_{\mathrm{exp},i}\right)^2/n}}{\sum_{i=1}^{n}J_{\mathrm{exp}}/n}\times100.

[val-2l_comparison] compares the TMAP8 desorption flux with the unirradiated experimental data and TMAP7 Fit A from [!cite](Shimada2011). The comparison is evaluated over the interval from 900 s to 2600 s, which contains the primary desorption peak. The two models exhibit complementary strengths and weaknesses: TMAP8 captures the peak magnitude and position accurately but overestimates the desorption flux during the ramp-up (before ~1800 s) and late ramp-down (after ~2400 s) phases of the TDS spectrum. Conversely, TMAP7 Fit A reproduces the rising and falling tails of the spectrum more closely but predicts a higher peak flux than observed experimentally.

!media comparison_val-2l.py
    image_name=val-2l_comparison_desorption.png
    id=val-2l_comparison
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    caption=Comparison of the TMAP8 prediction with the unirradiated experimental TDS data and TMAP7 Fit A reported by [!cite](Shimada2011).

!alert note title=Digitized data
The temperature history, experimental TDS data, and TMAP7 Fit A data were digitized from figures in [!cite](Shimada2011) and may contain small digitization errors.

### Deuterium inventory and mass conservation

[val-2l_inventory] shows the simulated mobile and trapped inventories of deuterium over the duration of the TDS experiment along with the temperature profile.

!media comparison_val-2l.py
    image_name=val-2l_inventory.png
    id=val-2l_inventory
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    caption=Mobile, trapped, and total deuterium inventories during the unirradiated TDS calculation.

The mass-balance residual verifies conservation of mass by comparing two independent estimates of the deuterium inventory change. The residual is computed as:

\begin{equation}
  \text{Residual} = \left[ M(t) - M(0) \right] + \int_0^t \left( J_{\text{upstream}} + J_{\text{downstream}} \right) \, dt,
\end{equation}

where $M(t)$ is the total deuterium inventory at time $t$ (mobile + trapped contributions), $M(0)$ is the initial inventory, and $J_{\text{upstream}}$ and $J_{\text{downstream}}$ are the diffusive fluxes through the upstream and downstream boundaries, respectively. Perfect mass conservation requires the residual to be identically zero, as the change in inventory must equal the negative of the net release. [val-2l_mass_conservation] shows this residual normalized by the initial inventory $M(0)$; values close to zero confirm that the numerical solution conserves mass.

!media comparison_val-2l.py
    image_name=val-2l_mass_conservation.png
    id=val-2l_mass_conservation
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    caption=Deuterium mass-balance residual normalized by the initial deuterium inventory.

### Evolution of mobile and trapped deuterium profiles

[val-2l_profile_animation] shows the evolution of the mobile and trapped
deuterium concentration profiles during the prescribed TDS temperature
history. The marker in the upper panel identifies the temperature associated
with the current time of the simulation. The lower panels show the mobile concentration over
the full 200 $\mu$m specimen thickness and within 1 $\mu$m of the upstream
surface, together with the trapped concentration over the first 7 $\mu$m and
within the first 1 $\mu$m. The dotted vertical line marks the 0.7 $\mu$m
boundary of the Fit A trap region.

!media trapped_profile_animation_val-2l.py
    image_name=val-2l_profile_animation.gif
    id=val-2l_profile_animation
    style=width:75%;margin-bottom:2%;margin-left:auto;margin-right:auto
    caption=Evolution of the mobile and trapped deuterium concentration profiles in the TDS simulation.

## Discussion and Limitations

This stage of `val-2l` validates TMAP8 against the unirradiated experimental TDS data. It exercises temperature-dependent diffusion, trapping and release, a measured temperature history, and inventory accounting in TMAP8. The comparison does not establish that the chosen trap distribution is physically unique or represents the correct underlying physical mechanism. In [!cite](Shimada2011), TMAP7 Fit A was calibrated to the TDS spectrum alone and did not reproduce the measured NRA depth profile. The TMAP8 fit improves upon these results, but can be further improved through optimization methods.

### Planned extension to the neutron-irradiated case

The neutron-irradiated specimen (0.025 dpa) exhibited a much broader desorption spectrum than the unirradiated specimen and required multiple trap populations in the TMAP7 analysis [!citep](Shimada2011). A later extension of `val-2l` will:

1. add the irradiated experimental TDS and temperature-history data;
2. introduce multiple trap populations to attempt to capture multiple sharp spectra;
3. document the irradiation history and the assumptions required, exploring modeling techniques to represent damage to tungsten;
4. perform mass conservation and validation checks incrementally;
5. optimize material properties for chosen trap distributions and types.

## Input Files

The files used in the current unirradiated validation case are:

- [!file](/val-2l.params), which contains the physical and numerical parameters;
- [!file](/val-2l.i), which defines the one-dimensional transport, trapping, release, surface recombination, and postprocessing model.

!bibtex bibliography
