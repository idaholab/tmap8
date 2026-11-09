# val-2j

# Tritium Thermal Desorption Spectroscopy from Li$_2$TiO$_3$ Solid Breeder

## Case Description

This validation case models tritium thermal desorption spectroscopy (TDS) from neutron-irradiated Li$_2$TiO$_3$ (lithium titanate) crystalline grains, a candidate solid tritium breeding material for Deuterium-Tritium (D-T) fusion reactors. The experimental data and model are from [!cite](kobayashi2015developing).

Li$_2$TiO$_3$ samples were irradiated at the Kyoto University Reactor (KUR) at various neutron fluences. After irradiation, the tritium release behavior was measured by TDS with a heating rate of 5 K/min starting from 300 K using pure helium as the purge gas. The average grain radius was 1.5 $\mu$m.

Sample E (high defect density, $D_{id}$ = $3.384 \times 10^{26}$ m$^{-3}$, corresponding to 0.018 defect/Li$_2$TiO$_3$) is modeled, where tritium release is significantly influenced by trapping at O$^{-}$-centers and defect annihilation.

## Model Description

### Diffusion of Mobile Species

TMAP8 simulates tritium diffusion and trapping in a single spherical grain of Li$_2$TiO$_3$ using 1D spherical coordinates (`coord_type = RSPHERICAL`). The governing equation for mobile tritium concentration $C$ is [!citep](kobayashi2015developing):

\begin{equation} \label{eq:diffusion_trapping}
\frac{\partial C}{\partial t} = D \left( \frac{\partial^2 C}{\partial r^2} + \frac{2}{r} \frac{\partial C}{\partial r} \right) - \frac{\partial C_T}{\partial t},
\end{equation}

where $C_T$ is the concentration of trapped tritium in O$^{-}$-centers and $D$ is the temperature-dependent diffusivity following the Arrhenius law:

\begin{equation} \label{eq:diffusivity}
D = D_0 \exp \left( -\frac{E_d}{k_B T} \right),
\end{equation}

where $D_0$ is the pre-exponential factor, $E_d$ is the activation energy, $k_B$ is the Boltzmann constant, and $T$ is the temperature.

### Defect annihilation

During TDS heating, radiation-induced defect sites undergo first-order annihilation [!citep](kobayashi2015developing):

\begin{equation} \label{eq:annihilation}
\frac{d D_{id}}{dt} = -k_{dp-da} \, D_{id},
\end{equation}

where $D_{id}$ is the defect density and $k_{dp-da}$ is the annihilation rate coefficient. The trap site fraction $\chi$ is related to $D_{id}$. However, the exact relationship is not clearly indicated in [!citep](kobayashi2015developing). Therefore, the initial trap site density is assumed to equal the defect density with $\chi(0)N = D_{id}$ with $N$ as the lattice site density.

$k_{dp-da}$ is described as:

\begin{equation} \label{eq:annihilation_rate}
k_{dp-da} = k_{dp-da,0} \exp \left( -\frac{E_{dp-da}}{k_B T} \right),
\end{equation}

where $k_{dp-da,0}$ and $E_{dp-da}$ are the annihilation prefactor and energy, respectively. Raising the temperature reduces the available trap sites; the trap site fraction $\chi$ decays over time following [eq:annihilation], preventing re-trapping into annihilated sites. This is implemented by solving the annihilation equation self-consistently as an additional variable within the simulation, using a [ReleasingNodalKernel.md].

### Trapping and Detrapping

Only O$^{-}$-center (hydroxyl group) trapping is included in this model. As noted by [!cite](kobayashi2015developing) (p. 26), tritium release controlled by detrapping from F$^+$-centers (oxygen vacancies) occurs near 580 K, which corresponds to the release temperature controlled by the diffusion process itself. Because F$^+$-center detrapping is not rate-limiting relative to diffusion, it does not produce a distinct feature (i.e., peak) in the TDS spectrum, and is therefore excluded from the model.

The trapped concentration $C_T$ evolves according to:

\begin{equation}  \label{eq:trapping}
\frac{\partial C_T}{\partial t} = \alpha_t \frac{C_T^{\text{empty}} C_M}{N} - \alpha_r C_T - k_{dp-da} C_T,
\end{equation}

where $C_T^{\text{empty}} = \chi N - C_T$ is the empty trap concentration.

The trapping and detrapping rate coefficients follow Arrhenius relationships:

\begin{equation} \label{eq:trapping_rate}
\alpha_t = \alpha_{t0} \exp\left(-\frac{\epsilon_t}{k_B T}\right),
\end{equation}

\begin{equation} \label{eq:detrapping_rate}
\alpha_r = \alpha_{r0} \exp\left(-\frac{\epsilon_r}{k_B T}\right),
\end{equation}

where $\alpha_{t0}$ and $\alpha_{r0}$ are pre-factors of trapping and release rate coefficients, and $\epsilon_t$ and $\epsilon_r$ are the trapping and release energies.
The last term in [eq:trapping], $k_{dp-da} C_T$, accounts for the trapped tritium atoms released when full defects are annealed.

### Boundary and initial conditions

- $\partial C / \partial r = 0$ at $r = 0$ (symmetry at grain center)
- $C = 0$ at $r = r_g$ (fast surface release, [!cite](kobayashi2015developing))

The mobile and trapped tritium concentrations are initialized at their local trapping/detrapping equilibrium values at the starting temperature $T_{\text{start}}$ = 300 K. The equilibrium mobile concentration is computed from the balance of trapping and detrapping rates. This avoids an initial transient from any imbalance between trapping and detrapping.
Since the TDS output is normalized to arbitrary units, only the shape of the release curve matters, not the absolute concentrations.

## Case and Model Parameters

The model parameters are summarized in [val-2j_parameters].

!table id=val-2j_parameters caption=Values of model parameters.
| Parameter | Description | Value | Units | Reference |
| --- | --- | --- | --- | --- |
| $r_g$ | Grain radius | 1.5 | $\mu$m | [!cite](kobayashi2015developing) |
| $D_0$ | Diffusivity pre-exponential | 6.9 $\times 10^{-7}$ | m$^2$/s | [!cite](kobayashi2015developing), Eq. 11 |
| $E_d$ | Diffusion activation energy | 1.07 | eV | [!cite](kobayashi2015developing), Eq. 11 |
| $\alpha_{r0}$ | detrapping prefactor | 4.1 $\times 10^{6}$ | s$^{-1}$ | [!cite](kobayashi2015developing), Eq. 13 |
| $\epsilon_r$ | detrapping energy | 1.19 | eV | [!cite](kobayashi2015developing), Eq. 13 |
| $\alpha_{t0}$ | Trapping prefactor | 4.2 $\times 10^{8}$ | s$^{-1}$ | [!cite](kobayashi2015developing), Eq. 21 |
| $\epsilon_t$ | Trapping energy | 1.04 | eV | [!cite](kobayashi2015developing), Eq. 21 |
| $k_{dp-da,0}$ | Annihilation prefactor | 1.0 $\times 10^{2}$ | s$^{-1}$ | [!cite](kobayashi2015developing), Eq. 18 |
| $E_{dp-da}$ | Annihilation energy | 0.9 | eV | [!cite](kobayashi2015developing), Eq. 18 |
| $N$ | Lattice density | 1.88 $\times 10^{28}$ | m$^{-3}$ | Calculated |
| $\beta$ | TDS heating rate | 5 | K/min | [!cite](kobayashi2015developing) |
| $k_B$ | Boltzmann constant | 1.380649 $\times 10^{-23}$ | J/K | [PhysicalConstants](source/utils/TMAP8PhysicalConstants.md) |
| $D_{id,E}$ | Defect density (Sample E) | $3.384 \times 10^{26}$ | m$^{-3}$ | [!cite](kobayashi2015developing), Table 1 |

## Results

### Results before optimization

[val-2j_comparison_e] shows the comparison between TMAP8 and the experimental TDS spectrum for Sample E (high defect density). The O$^{-}$-center trapping model with defect annihilation captures the broad release profile. The high detrapping energy of O$^{-}$-centers (1.19 eV) produces a release peak above 650 K that is distinct from the diffusion-controlled release. The defect annihilation mechanism reduces the effective trap density at high temperatures, suppressing re-trapping and allowing tritium to escape more efficiently.

!media comparison_val-2j.py
       image_name=val-2j_comparison_sample_e.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=val-2j_comparison_e
       caption=Comparison of TMAP8 calculation with the experimental TDS data for Sample E (high defect density).

### Results after optimization

The agreement between the TMAP8 simulation and experimental data can be improved by optimizing the model parameters using the [MOOSE stochastic tools module](https://mooseframework.inl.gov/modules/stochastic_tools/index.html). A Bayesian optimization approach [!citep](DHULIPALA2026102776) was applied to optimize eight key parameters (i.e., four Arrhenius pre-exponential factors (in log$_{10}$ space) and four activation energies for the diffusivity, trapping, releasing, and defect annealing) to better match the experimental TDS curve for Sample E.
As shown in [val-2j_defect_density_evolution], the normalized defect density with the reference annihilation prefactor ($\alpha_{anneal}$ = 10$^2$ s$^{-1}$) remains close to unity throughout the main release region (below ~750 K) and only decreases significantly at higher temperatures where the tritium release flux is decreasing. Larger annihilation prefactors would shift the defect annihilation and the associated tritium release to lower temperatures, but the optimization consistently finds values near the reference.
The optimization used Gaussian Process active learning with Expected Improvement acquisition, running 40 iterations with 5 parallel proposals per iteration.

!media comparison_val-2j.py
       image_name=val-2j_defect_density_evolution.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=val-2j_defect_density_evolution
       caption=Evolution of the normalized defect density, $D_{id}/D_{id,0}$, during the TDS temperature ramp. As expected, the annihilation temperature strongly depends on $\alpha_{anneal}$.

The objective function evaluates the root mean square percentage error (RMSPE) between the simulated and experimental normalized release rates using a continuous comparison at every simulation timestep. The experimental TDS curve is represented as a piecewise-linear interpolation function, and the RMSPE is accumulated over the full temperature ramp. Low-temperature constraint points (300--475 K) with a small target value penalize parameter sets that produce spurious early release peaks.

[val-2j_optimized_parameters] compares the reference values from [!cite](kobayashi2015developing) with the Bayesian-optimized parameters, along with the parameter ranges used in the optimization.

!table id=val-2j_optimized_parameters caption=Reference and Bayesian-optimized parameter values.
| Parameter | Reference | Optimized | Range | Units |
| --- | --- | --- | --- | --- |
| $D_0$ | 6.9 $\times 10^{-7}$ | 4.50 $\times 10^{-6}$ | 10$^{-8}$ -- 10$^{-4}$ | m$^2$/s |
| $E_d$ | 1.07 | 1.01 | 0.8 -- 1.4 | eV |
| $\alpha_{t0}$ | 4.2 $\times 10^{8}$ | 2.21 $\times 10^{7}$ | 10$^{7}$ -- 10$^{10}$ | s$^{-1}$ |
| $\epsilon_t$ | 1.04 | 0.82 | 0.8 -- 1.3 | eV |
| $\alpha_{r0}$ | 4.1 $\times 10^{6}$ | 2.14 $\times 10^{5}$ | 10$^{5}$ -- 10$^{8}$ | s$^{-1}$ |
| $\epsilon_r$ | 1.19 | 1.08 | 0.9 -- 1.5 | eV |
| $k_{dp-da,0}$ | 1.0 $\times 10^{2}$ | 8.26 $\times 10^{1}$ | 10$^{0}$ -- 10$^{5}$ | s$^{-1}$ |
| $E_{dp-da}$ | 0.9 | 1.27 | 0.5 -- 1.5 | eV |

[val-2j_bayesian_parameter_exploration] compares the reference parameter values from [!cite](kobayashi2015developing) (blue dashed lines) with the Bayesian-optimized values (red solid lines) for each of the eight fitted parameters. The green curves show the distribution of the parameters with top 20% RMSPE evaluations from the Bayesian optimization, providing insight into which parameter regions produce good fits to the experimental data. The gray shaded region indicates the search range used during optimization. The optimized values fall within the high-density regions of the distributions, confirming consistency with the near-optimal parameter space.

!media comparison_val-2j.py
       image_name=val-2j_bayesian_parameter_exploration.png
       style=width:90%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=val-2j_bayesian_parameter_exploration
       caption=Comparison of reference (blue dashed) and Bayesian-optimized (red solid) parameter values. Green curves show the distribution of the parameters with top 20% RMSPE from the Bayesian optimization. The gray shaded region indicates the search range.

[val-2j_arrhenius_comparison] compares the Arrhenius-law temperature dependence of the diffusivity $D(T)$, trapping rate coefficient $\alpha_t(T)$, detrapping rate coefficient $\alpha_r(T)$, and annihilation rate coefficient $k_{dp-da}(T)$ between the reference and optimized parameter sets over the 300--900 K TDS temperature range. The diffusivity pre-exponential factor increases by roughly one order of magnitude while the activation energy remains close to the reference (1.07 to 1.01 eV). The trapping prefactor decreases by about one order of magnitude with a reduced activation energy (1.04 to 0.82 eV), while the detrapping prefactor decreases by about one order of magnitude with a slightly reduced activation energy (1.19 to 1.08 eV). The optimized annihilation prefactor (~83 s$^{-1}$) remains close to the reference value (100 s$^{-1}$), with the annihilation activation energy increasing from 0.9 to 1.27 eV, further suppressing annihilation effects during TDS.

!media comparison_val-2j.py
       image_name=val-2j_arrhenius_comparison.png
       style=width:90%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=val-2j_arrhenius_comparison
       caption=Comparison of Arrhenius temperature dependence for diffusivity, trapping rate, detrapping rate, and annihilation rate between reference and Bayesian-optimized parameter sets.

[val-2j_comparison_optimized] shows the comparison between TMAP8 with the optimized parameters and the experimental data. The optimized parameters significantly reduce the RMSPE compared to the reference parameters, demonstrating improved agreement with the experimental TDS spectrum.

!media comparison_val-2j.py
       image_name=val-2j_comparison_optimized.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=val-2j_comparison_optimized
       caption=Comparison of TMAP8 calculation with Bayesian-optimized parameters against the experimental TDS data for Sample E (high defect density).

## Input files

!style halign=left
The input files for this validation case are:

- [!file](/val-2j_base.i): Contains the shared simulation blocks (mesh, variables, kernels, materials, etc.) used by all val-2j cases.
- [!file](/val-2j.i): Simulates tritium transport in Li$_2$TiO$_3$ spherical sample with reference parameters. [!file](/optimal_bayesian_params.i) overrides with Bayesian-optimized parameters.
- [!file](/bayesian_main_val2j.i) and [!file](/val-2j_bayesian.i): The optimization main and sub input files, respectively, for Bayesian parameter optimization.

More information about these tests can be found in the test specification file for this case, namely [!file](/val-2j/tests).

!bibtex bibliography
