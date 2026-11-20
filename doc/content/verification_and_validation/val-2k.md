# val-2k

# Oxide effects on deuterium release from self-irradiated tungsten

## Overall Case Description

This validation case is based on the natural-oxide and thin-oxide experiments reported in [!cite](Kremer2022oxide).
The experimental study performs thermal desorption spectroscopy (TDS) and measures deuterium release from self-irradiated tungsten samples with a natural oxide layer and with electrochemically grown oxide layers between 5 nm and 100 nm.
This case uses the same overarching model (e.g., tungsten diffusion, trapping, and surface-release formulation) to capture the deuterium release behavior of four self-irradiated tungsten samples with distinct oxygen-field configurations: natural oxide and 5 nm, 10 nm, and 15 nm thin oxide films.
The effect of the thin oxide films on the release is discussed, with the model providing key mechanistic insights into the observed experimental behavior.
The release behavior is compared against the time-dependent experimental HD + D$_2$ and HDO + D$_2$O signals as the temperature increases.
In the present implementation, those grouped measurements are represented phenomenologically through an explicit D$_2$ release and an oxygen-gated D$_2$O release rather than through separate explicit HD and HDO transport species.

The aim of this study is to understand the effect of the presence of an oxide layer on deuterium retention and release from tungsten samples.
While tungsten oxidation is expected to be limited in fusion power plant conditions, it does take place in laboratory environments, which can affect laboratory observations.
Understanding oxide effects can thus help better tie laboratory experiments to performance in fusion-relevant environments, thus increasing the impact of laboratory experiments and accelerating fusion energy deployment.

## Sample history and dimensions

The reference sample history is taken from [!cite](Kremer2022oxide).
In the experiment, the 0.8 mm tungsten specimens are first self-irradiated, which generates a self-damaged near-surface region (2.3 $\mu$m thick).
The samples are then loaded with deuterium so that the retained inventory is concentrated in the first few micrometers of the sample.
The loading is performed at 370 K to enable deuterium mobility while minimizing defect annealing in the self-damaged region.
Once loaded, a thin oxide layer is deposited using an electrochemical process at low temperature.
The advantage of this approach is that compared to thermal oxidation, the temperature remains low (e.g., room temperature), which limits deuterium transport and defect annealing.
[!cite](Kremer2022oxide) note that electro-chemically grown tungsten oxide has an amorphous structure and, therefore, differs from thermally grown oxide or natural oxide, which might affect the release behavior.

While [!cite](Kremer2022oxide) offers a wide range of data and observations for oxide-layer thicknesses reaching up to 100 nm, the current study focuses on the thinner oxide films discussed in the experimental paper, namely a sample with a natural oxide layer and then samples with 5 nm, 10 nm, and 15 nm-thick oxide films.
The paper describes the natural oxide as being 1-2 nm thick, and the present model uses 1 nm as a representative natural-oxide value for that case.
All four desorption calculations start from the same preloaded tungsten state and follow the digitized temperature history from Fig. 6 in [!cite](Kremer2022oxide), which heats the sample from about 296 K to about 1000 K over roughly 4.17 h.

The initial deuterium profile used at the start of desorption is shown in [val-2k_natural_oxide_profile] for the 15 nm configuration (the same approach is used for the other samples).
The shaded regions identify the oxide, damaged tungsten, and bulk tungsten sections in the plotted depth range.
In this configuration, most of the retained inventory is placed in the irradiation-induced traps inside the damaged region, while the mobile deuterium concentration remains comparatively negligible.

!media comparison_val-2k.py
    image_name=val-2k_natural_oxide_profile.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=val-2k_natural_oxide_profile
    caption=Initial deuterium concentration profile used to start the 15 nm `val-2k` desorption calculation. The profile shows the mobile deuterium concentration (negligible), the six trapped populations, their total, and the oxide, damaged tungsten, and bulk tungsten sections.

## Model Description

To capture the deuterium release behavior from self-irradiated tungsten with a thin oxide film, the model includes the following features:

- A one-dimensional geometry with an oxide layer, a self-damaged region, and the tungsten bulk, as illustrated in [val-2k_natural_oxide_profile].
- Deuterium transport involves Fickian diffusion, trapping and resolution, and surface reactions.
- Trapping and resolution are governed by six trap families: one intrinsic trap family and five irradiation-induced trap families. This is directly inspired by [val-2f](val-2f.md), which validates TMAP8 based on deuterium release from self-irradiated tungsten. The full set of trap site densities is adapted from [val-2f](val-2f.md) so the initial areal inventory matches the prescribed `val-2k` preload.
- The density of the intrinsic trap, since it is independent of irradiation, is homogeneous in the sample. The densities of irradiation-induced traps, however, are homogeneous in the 2.3 $\mu$m-thick self-damaged region, and then quickly decrease to 0 in the bulk of the sample with a transition length of 0.05 $\mu$m. Irradiation-induced trap densities also decrease to 0 in the oxide layer with a transition length of 0.25 nm (see [val-2k_natural_oxide_profile]).
- Deuterium release takes place either as D$_2$ or as D$_2$O by combining with an oxygen atom at the surface. The surface recombination rates of these reactions are different.
- The oxide layer is modeled as an additional layer on top of the self-damaged region. The transport properties of deuterium in the oxide layer remain equal to those in tungsten (e.g., same diffusivity), except that no trapping sites are present in the oxide layer. Note that the thickness of the oxygen layer does not evolve in time, even as oxygen atoms are released as D$_2$O. These simplifications are considered reasonable as the oxide layer represents only a small volume and thickness in these cases.
- The oxide layer is initialized with a given oxygen concentration (consistent across all cases), which is null everywhere else. The diffusivity of oxygen in the oxide layer is accounted for, but the diffusion of oxygen deeper into the tungsten sample is suppressed.
- The mesh is refined near the exposed surface. This is to resolve the oxide-to-damaged-tungsten and damaged-to-bulk-tungsten transition and to accurately capture the surface reactions, oxygen transport, and behavior in the self-damaged region. In particular, elements of the same size as in the oxide layer extend 2.5 nm (10 transition widths) into the tungsten beyond the oxide/tungsten interface to resolve the steep oxygen concentration and diffusivity transition there. Without this refinement, the coarser tungsten elements under-resolve the transition, which overestimates the initial oxygen inventory by up to 5% and causes oxygen undershoots that, once clipped by the non-negativity bound on the oxygen concentration, create oxygen mass. Deeper into the sample, the mesh is coarser to reduce computational size.
- The only difference between the four configurations of interest (e.g., natural oxide and 5, 10, and 15 nm-thick oxide films) is the thickness of the oxide layer and the mesh refinement area. The model formulation, other initial conditions, and all the model parameters are consistent across all cases.

As in [val-2f](val-2f.md), the implementation is solved internally in dimensionless form, but the physical governing equations are written first here for clarity. The mobile deuterium balance is

\begin{equation}
\frac{\partial C_M}{\partial t} =
\nabla \cdot \left(D_D \nabla C_M \right) -
\sum_{i \in \{intr,1,\dots,5\}} \frac{\partial C_{T_i}}{\partial t},
\end{equation}

with one trapped-species evolution equation for each trap family:

\begin{equation}
\frac{\partial C_{T_i}}{\partial t} =
\alpha_{t,i} \frac{C_{T_i}^{empty} C_M}{N} - \alpha_{r,i} C_{T_i},
\end{equation}

\begin{equation}
C_{T_i}^{empty} = C_{T_i,0} N - C_{T_i},
\end{equation}

where $C_M$ is the mobile deuterium concentration, $t$ is the time, $C_{T_i}$ is the concentration trapped in family $i$, $C_{T_i}^{empty}$ is the remaining empty trap capacity, $C_{T_i,0}$ is the fraction of host sites that can act as trap family $i$, and $N$ is the tungsten host density. $D_D$ is the deuterium diffusivity in tungsten (and tungsten oxide in this model), and $\alpha_{t,i}$ and $\alpha_{r,i}$ are the trapping and resolution rates for trapping family $i$, respectively.

The oxygen field evolves according to

\begin{equation}
\frac{\partial C_O}{\partial t} =
\nabla \cdot \left(D_O \nabla C_O \right),
\end{equation}

where $C_O$ is the oxygen concentration and $D_O$ is the oxygen diffusivity in the oxide layer.
In the current model, oxygen diffusion is masked so that it is active only inside the oxide layer.

The temperature-dependent diffusivities and trapping/detrapping rates follow Arrhenius forms:

\begin{equation}
D_D = D_{D,0} \exp \left(- \frac{E_D}{k_B T} \right),
\end{equation}
and
\begin{equation}
D_O = D_{O,0} \exp \left(- \frac{E_{D,O}}{k_B T} \right),
\end{equation}

for the diffusivities, and

\begin{equation}
\alpha_{t,i} = \alpha_{t,i,0} \exp \left(- \frac{E_D}{k_B T} \right),
\end{equation}
and
\begin{equation}
\alpha_{r,i} = \alpha_{r,i,0} \exp \left(- \frac{E_{T,i}}{k_B T} \right),
\end{equation}

for the trapping and detrapping rates.

The surface reactions represented in the model are

\begin{equation}
2D \rightarrow D_2
\qquad \text{and} \qquad
2D + O \rightarrow D_2O,
\end{equation}

which give the corresponding surface fluxes

\begin{equation}
J_{D_2}^{(D\ at)} = -2 K_{r,D_2} C_M^2,
\end{equation}
\begin{equation}
J_{D_2O}^{(D\ at)} = -2 K_{r,D_2O} C_O C_M^2,
\end{equation}
and
\begin{equation}
J_O = \frac{1}{2} J_{D_2O}^{(D\ at)},
\end{equation}

where $J_{D_2}^{(D\ at)}$ and $J_{D_2O}^{(D\ at)}$ are deuterium-atom fluxes leaving the mobile-deuterium balance from $D_2$ and $D_2O$ reactions, with units of D atoms m$^{-2}$ s$^{-1}$.
Equivalently, the molecular heavy-water flux is $J_{D_2O}^{(mol)} = \frac{1}{2} J_{D_2O}^{(D\ at)}$, so the oxygen loss flux satisfies $J_O = J_{D_2O}^{(mol)}$ because one oxygen atom is consumed per released D$_2$O molecule.
While the reverse reactions, e.g., molecular dissociation at the surface, are possible, they are neglected here for simplicity due to the low partial pressure of deuterium in the gas surrounding the sample.

The surface reaction rates also follow Arrhenius forms and are defined as

\begin{equation}
K_{r,D_2} = K_{r,D_2,0} \exp \left(- \frac{E_{r,D_2}}{k_B T} \right),
\end{equation}
and
\begin{equation}
K_{r,D_2O} = K_{r,D_2O,0} \exp \left(- \frac{E_{r,D_2O}}{k_B T} \right).
\end{equation}

For numerical stability, the input files rewrite these equations in dimensionless form using the reference ratios

\begin{equation}
\hat{x} = \frac{x}{L_{\text{ref}}}, \qquad
\hat{t} = \frac{t}{t_{\text{ref}}}, \qquad
\hat{C}_M = \frac{C_M}{C_{M,\text{ref}}}, \qquad
\hat{C}_{T_i} = \frac{C_{T_i}}{C_{T_i,\text{ref}}}, \qquad
\hat{C}_O = \frac{C_O}{C_{O,\text{ref}}},
\end{equation}

with $L_{\text{ref}} = 1$ $\mu$m and $t_{\text{ref}} = 1$ s.
The corresponding dimensionless groups used in the input files are

\begin{equation}
\hat{\alpha}_{t,i} = t_{\text{ref}} \alpha_{t,i} \frac{C_{M,\text{ref}}}{N},
\end{equation}
\begin{equation}
\hat{\alpha}_{r,i} = t_{\text{ref}} \alpha_{r,i},
\end{equation}
\begin{equation}
\hat{D}_D = D_D \frac{t_{\text{ref}}}{L_{\text{ref}}^2},
\end{equation}
\begin{equation}
\hat{D}_O = D_O \frac{t_{\text{ref}}}{L_{\text{ref}}^2},
\end{equation}
\begin{equation}
\hat{K}_{r,D_2} = K_{r,D_2} \frac{C_{M,\text{ref}} t_{\text{ref}}}{L_{\text{ref}}},
\end{equation}
and
\begin{equation}
\hat{K}_{r,D_2O} = K_{r,D_2O} \frac{C_{M,\text{ref}} t_{\text{ref}}}{L_{\text{ref}}}.
\end{equation}

The transient solve is therefore carried out in dimensionless variables, while physical-unit auxiliary variables and postprocessors are written for direct comparison with the experimental TDS data and for generation of the validation figures.

## Case and Model Parameters

The literature-based and calibrated model parameters, geometry, and sample history conditions are listed in [val-2k_parameters].
The initial oxygen concentration is derived from the paper-reported removal of $100 \times 10^{19}$ O/m$^2$ from the first 13.5 nm of oxide and is reduced by an additional factor of 1.5 in the current calibrated model, which yields about $4.94 \times 10^{28}$ O/m$^3$.

!table id=val-2k_parameters caption=Literature-based and calibrated model parameters, geometry, and sample history conditions used in `val-2k`.
| Parameter | Description | Value | Units | Reference |
| --------- | ----------- | ----- | ----- | --------- |
| $l_W$ | Tungsten thickness | 0.8 | mm | [!cite](Kremer2022oxide) |
| $l_{ox}$ | Oxide thickness | 1, 5, 10, 15 | nm | Natural-oxide proxy plus explicit thin-film cases from [!cite](Kremer2022oxide) |
| $w_{ox}$ | Tanh transition width used for oxide-to-W blending | 0.25 | nm | Numerical resolution choice |
| $l_d$ | Self-damaged depth | 2.3 | $\mu$m | [!cite](Kremer2022oxide) |
| $T_0$ | Initial desorption temperature | $\approx$ 295.775 | K | Digitized from Fig. 6 in [!cite](Kremer2022oxide) |
| $T_f$ | Final desorption temperature | $\approx$ 1001.408 | K | Digitized from Fig. 6 in [!cite](Kremer2022oxide) |
| $t_f$ | Final desorption time | 4.166 | h | Digitized from Fig. 6 in [!cite](Kremer2022oxide) |
| $D_{D,0}$ | Deuterium diffusivity prefactor | 1.6 $\times 10^{-7}$ | m$^2$/s | From [val-2f](val-2f.md) |
| $E_D$ | Deuterium diffusion activation energy | 0.28 | eV | From [val-2f](val-2f.md) |
| $D_{0,O}$ | Oxygen diffusivity prefactor in oxide film | 2.0 $\times 10^{-17}$ | m$^2$/s | Calibrated, starting from [!cite](Jiang2009oxygenDiffusion) |
| $E_{D,O}$ | Oxygen diffusion activation energy in oxide film | 0.45 | eV | Calibrated, starting from [!cite](Jiang2009oxygenDiffusion) |
| $C_{O,0}$ | Initial oxygen concentration in oxide film | 4.94 $\times 10^{28}$ | at/m$^3$ | Adapted from the oxygen areal density from [!cite](Kremer2021oxideBarrier) |
| $w_d$ | Tanh transition width used for damaged-to-bulk W blending | 0.05 | $\mu$m | Numerical resolution choice |
| $L_{\text{ref}}$ | Reference length for the dimensionless solve | 1 | $\mu$m | Chosen to match the val-2f dimensionless formulation |
| $t_{\text{ref}}$ | Reference time for the dimensionless solve | 1 | s | Chosen to match the val-2f dimensionless formulation |
| $C_{M,\text{ref}}$ | Mobile reference concentration | 6.3222 $\times 10^{16}$ | at/m$^3$ | From [val-2f](val-2f.md) |
| $C_{T,\text{ref}}^{intr}$ | Intrinsic-trap reference concentration | 6.3222 $\times 10^{17}$ | at/m$^3$ | From [val-2f](val-2f.md) |
| $C_{T,\text{ref}}^{1-5}$ | Non-intrinsic trap reference concentration | 6.3222 $\times 10^{20}$ | at/m$^3$ | From [val-2f](val-2f.md) |
| $s_T$ | Uniform trap-density scale factor | 6.644848 | - | Chosen so the six-trap model matches the prior `val-2k` initial areal inventory |
| $E_{T,intr}$ | Intrinsic detrapping energy | 1.08 | eV | Adapted from [val-2f](val-2f.md) |
| $E_{T,1}$ | Trap 1 detrapping energy | 1.20 | eV | Adapted from [val-2f](val-2f.md) |
| $E_{T,2}$ | Trap 2 detrapping energy | 1.38 | eV | Adapted from [val-2f](val-2f.md) |
| $E_{T,3}$ | Trap 3 detrapping energy | 1.65 | eV | From [val-2f](val-2f.md) |
| $E_{T,4}$ | Trap 4 detrapping energy | 1.85 | eV | From [val-2f](val-2f.md) |
| $E_{T,5}$ | Trap 5 detrapping energy | 2.05 | eV | From [val-2f](val-2f.md) |
| $C_{T,intr,0} N$ | Intrinsic trap site density | 1.595 $\times 10^{23}$ | at/m$^3$ | Scaled from [val-2f](val-2f.md) |
| $C_{T_1,0} N$ | Trap 1 site density | 3.076 $\times 10^{26}$ | at/m$^3$ | Scaled from [val-2f](val-2f.md) |
| $C_{T_2,0} N$ | Trap 2 site density | 1.910 $\times 10^{26}$ | at/m$^3$ | Scaled from [val-2f](val-2f.md) |
| $C_{T_3,0} N$ | Trap 3 site density | 1.304 $\times 10^{26}$ | at/m$^3$ | Scaled from [val-2f](val-2f.md) |
| $C_{T_4,0} N$ | Trap 4 site density | 2.392 $\times 10^{26}$ | at/m$^3$ | Adapted from [val-2f](val-2f.md) |
| $C_{T_5,0} N$ | Trap 5 site density | 7.330 $\times 10^{25}$ | at/m$^3$ | Adapted from [val-2f](val-2f.md) |
| $K_{r,D_2}$ | Recombination prefactor | 3.8 $\times 10^{-16}$ | m$^4$/at/s | Adapted from [val-2f](val-2f.md) |
| $E_{r,D_2}$ | Recombination activation energy | 0.34 | eV | Adapted from [val-2f](val-2f.md) |
| $K_{r,D_2O}$ | D$_2$O surface-release prefactor | 3.8 $\times 10^{1}$ | m$^4$/at/s | Calibrated |
| $E_{r,D_2O}$ | D$_2$O surface-release activation energy | 2.10 | eV | Calibrated |

## Results

The main interpretation from [!cite](Kremer2022oxide) is that the oxide film acts both as a deuterium reservoir and as a transport barrier, delaying release as the oxide gets thicker. The paper also reports that chemical interaction between outgassing deuterium and the oxide begins above about 475 K, and that heavy-water release dominates above about 700 K while enough oxide remains available. The calibrated `val-2k` model is evaluated against those trends as well as against the digitized TDS curves.

[val-2k_comparison] compares the deuterium release behavior of all four oxide-layer configurations against the digitized HD + D$_2$ and HDO + D$_2$O desorption data from Fig. 6 of [!cite](Kremer2022oxide).
The figure also overlays the digitized temperature history from the TDS experiment.
In all release figures, the experimental curves come from digitized grouped measurements in the paper, while the simulation curves come from the present calibrated model and are reported as deuterium-atom release rates to match the plotted grouped signals.
While [val-2k_comparison] shows the experimentally measured and simulated D$_2$ and D$_2$O release curves for all four configurations, [val-2k_natural_oxide_case_comparison], [val-2k_5nm_oxide_case_comparison], [val-2k_10nm_oxide_case_comparison], and [val-2k_15nm_oxide_case_comparison] show a subset of the same data by focusing, for clarity, on the natural oxide case and the 5 nm, 10 nm, and 15 nm-thick oxide-film cases, respectively.
This makes it easier to inspect the onset temperature, peak placement, D$_2$/D$_2$O balance, and general trends for each oxide thickness without visual crowding from the other three cases.

!media comparison_val-2k.py
    image_name=val-2k_comparison.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=val-2k_comparison
    caption=Comparison of the D$_2$ and D$_2$O release simulation predictions against TDS experimental measurements from [!cite](Kremer2022oxide) for all four oxide thicknesses.

!media comparison_val-2k.py
    image_name=val-2k_natural_oxide_case_comparison.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=val-2k_natural_oxide_case_comparison
    caption=Focused comparison of the D$_2$ and D$_2$O release simulation predictions against TDS experimental measurements from [!cite](Kremer2022oxide) for the natural-oxide case, represented here with a 1 nm oxide layer. The data is a subset of the data in [val-2k_comparison].

!media comparison_val-2k.py
    image_name=val-2k_5nm_oxide_case_comparison.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=val-2k_5nm_oxide_case_comparison
    caption=Focused comparison of the D$_2$ and D$_2$O release simulation predictions against TDS experimental measurements from [!cite](Kremer2022oxide) for the 5 nm-thick oxide case. The data is a subset of the data in [val-2k_comparison].

!media comparison_val-2k.py
    image_name=val-2k_10nm_oxide_case_comparison.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=val-2k_10nm_oxide_case_comparison
    caption=Focused comparison of the D$_2$ and D$_2$O release simulation predictions against TDS experimental measurements from [!cite](Kremer2022oxide) for the 10 nm-thick oxide case. The data is a subset of the data in [val-2k_comparison].

!media comparison_val-2k.py
    image_name=val-2k_15nm_oxide_case_comparison.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=val-2k_15nm_oxide_case_comparison
    caption=Focused comparison of the D$_2$ and D$_2$O release simulation predictions against TDS experimental measurements from [!cite](Kremer2022oxide) for the 15 nm-thick oxide case. The data is a subset of the data in [val-2k_comparison].

In the case of the natural oxide shown in [val-2k_natural_oxide_case_comparison], the deuterium release is dominated by D$_2$ release with two main peaks dictated by the trapping energies.
This is consistent with the results discussed in [val-2f](val-2f.md) and [!cite](dark2024modelling).
The low release in D$_2$O form is attributed to the lower availability of oxygen, since the 1 nm natural-oxide inventory quickly gets depleted, as shown in [val-2k_natural_oxide_oxygen_inventory].
The model captures the main trends observed experimentally.
The position and magnitude of the two peaks for D$_2$ release are predicted, as well as the ratio of D$_2$ to D$_2$O release.
The main difference in trends is the short peak in D$_2$O instead of the wider peak observed experimentally.
This could be attributed to an overestimation of the oxygen availability or D$_2$O surface reaction rate at lower temperatures.

!media comparison_val-2k.py
    image_name=val-2k_natural_oxide_oxygen_inventory.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=val-2k_natural_oxide_oxygen_inventory
    caption=Total oxygen inventory remaining in the sample over time.

[val-2k_natural_oxide_inventory] shows the evolution of the deuterium inventory as a mobile species and in each trap over time.
The deuterium release is dominated by the trapping populations, while the mobile deuterium inventory remains much smaller throughout the desorption ramp, as mobile deuterium quickly reacts at the surface of the sample.
The lower-energy traps begin to empty first as the temperature rises, followed by the deeper trap populations later in the ramp, as expected.
This behavior is found to be common to all four cases, with no significant effect of the oxide thickness on the detrapping behavior.
This is expected since the traps description is common across all cases.

!media comparison_val-2k.py
    image_name=val-2k_natural_oxide_inventory.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=val-2k_natural_oxide_inventory
    caption=Evolution of the mobile and trapped deuterium inventories during desorption for the 1 nm natural-oxide sample. This behavior is common to all four cases.

As the oxide film thickness increases, the following trends are observable experimentally in [val-2k_comparison]:

- The ratio of D$_2$O release over D$_2$ increases as oxygen availability increases.
- The low-temperature D$_2$ peak maintains its position, but its magnitude decreases consistently.
- The high-temperature peak shifts to higher temperatures and its magnitude decreases, even disappearing when the oxide thickness increases from 10 nm to 15 nm.
- The D$_2$O release increases, with a first peak aligned with the first D$_2$ peak, then a stable region, and then either a decrease in the case of the 5 nm-thick oxide or another peak aligned with the second D$_2$ peak for thicker oxides. This secondary D$_2$O peak for the 10 nm oxide decreases sooner than for the 15 nm oxide.

These trends are all qualitatively captured by the calibrated model.
Furthermore, even if the model lacks a purely mechanistic description of the deuterium and oxide behavior, the simulations offer some physical insights explaining these observed trends.

Oxygen availability was found to be a key parameter during model calibration.
As the oxide thickness increases and the oxygen inventory increases (see [val-2k_natural_oxide_oxygen_inventory]), the ratio of D$_2$ to D$_2$O release decreases.
Then, as the oxygen inventory gets depleted, D$_2$O release naturally decreases.
This helps explain the lack of a secondary peak in D$_2$O release for the 5 nm oxide sample, as well as the thinner secondary D$_2$O peak for the 10 nm oxide sample compared with the 15 nm oxide sample.
As described in [!cite](Kremer2022oxide), the oxide layer disappears during TDS for most cases, but some remains for the 15 nm-thick oxide film case (see [val-2k_natural_oxide_oxygen_inventory]).
Note that while no oxide was observed after TDS for the 10 nm sample, the simulation predicts some remaining inventory, albeit only a small fraction of the initial amount.
The oxide is completely gone for the natural oxide and 5 nm-thickness cases in both experiments and simulations.

For oxygen to be effectively used for D$_2$O release, however, the ratio of the D$_2$ and D$_2$O surface reaction rates must be advantageous, and the oxygen diffusion in the oxide layer needs to be sufficient.
The slight delay in the onset in D$_2$O release at low temperature compared to D$_2$ release is captured by a lower D$_2$O surface reaction rate at low temperature.
However, at high temperature, the surface reaction rate of D$_2$O needs to surpass that of D$_2$ to observe the suppression of the secondary D$_2$ peak in favor of the secondary D$_2$O peak.
[val-2k_natural_oxide_recombination_rates] shows the two phenomenological surface-release coefficients over the experimental desorption temperature window.
In the calibrated parameter set, the D$_2$O release is strongly suppressed at low temperature by its larger activation energy, then rises more steeply and overtakes the D$_2$ coefficient at about 520 K, enabling the behavior discussed above.

!media comparison_val-2k.py
    image_name=val-2k_natural_oxide_recombination_rates.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=val-2k_natural_oxide_recombination_rates
    caption=Arrhenius-form surface recombination coefficients used for the D$_2$ and D$_2$O release reactions.

In the case of the 15 nm-thick oxide, the secondary D$_2$ peak is not completely suppressed in the current model.
However, this might be resolved with further model calibration.


To check the numerical accuracy of the simulation presented here, the mass conservation of deuterium and oxygen are computed.
[val-2k_natural_oxide_mass_conservation] tracks the deuterium mass-balance residual normalized by the initial deuterium inventory for every currently available modeled case.
The residual is formed from the change in deuterium retained in the sample plus the time-integrated left and right surface release fluxes, so values close to zero indicate mass conservation, which is the case here.

!media comparison_val-2k.py
    image_name=val-2k_natural_oxide_mass_conservation.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=val-2k_natural_oxide_mass_conservation
    caption=Relative deuterium mass-balance residual over time for all four cases, which shows that mass conservation errors are below reasonable limits.

[val-2k_natural_oxide_oxygen_conservation] tracks the oxygen conservation residual normalized by the initial oxygen inventory in each available oxygen-field case.
The residual is formed from the change in oxygen retained in the sample plus the time-integrated oxygen loss tied to D$_2$O release, so values close to zero indicate mass conservation, which is the case here, with relative residuals below 0.02% for all four cases.

!media comparison_val-2k.py
    image_name=val-2k_natural_oxide_oxygen_conservation.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=val-2k_natural_oxide_oxygen_conservation
    caption=Relative oxygen conservation residual over time for all four cases, which shows that mass conservation errors are below reasonable limits.


## Discussion and future work

The model proposed herein uses a general formulation and consistent parameters for all four samples with different oxide thicknesses, and qualitatively captures the main experimentally-observed trends and differences between all configurations published in [!cite](Kremer2022oxide).
By doing so, it provides key physical insights into the experimental measurements and observations.
This insight is valuable to tie laboratory observations, where tungsten oxidation often takes place, to performance in fusion power plant environments.
Using this novel model, the laboratory deuterium TDS data can be analyzed and the effect of the oxide layer can be isolated, hence providing a model applicable to fusion energy system conditions.

This model, however, has limitations that should be addressed by future work.
The limitations discussed in [!cite](Kremer2022oxide) (e.g., electrochemically grown oxide being different from thermally grown oxide) still apply to this study.
A more thorough characterization of the oxide and a general analysis including different oxide structures would help generalize the current model, which currently does not differentiate between different oxide types.
In addition, the model makes other key assumptions and simplifications that could be challenged in the future to confirm the interpretation proposed in this study.
For example, the model does not capture the increased surface diffusion of deuterium, discussed in the original paper [!citep](Kremer2022oxide) as a key release mechanism, as deuterium atoms diffuse along the sample surface to find remaining pockets of oxygen to be released as D$_2$O.
To model this, the geometry should be expanded to a 2D or 3D model, which is possible in TMAP8 [!citep](Franklin2025,Shimada2024,Simon2022,Simon2025).

The current study implemented the model and performed ad hoc calibration of the model parameters based on the potential driving mechanisms of oxide evolution and deuterium detrapping, diffusion, and surface reactions.
While the experimentally-observed trends are qualitatively captured by the model, the simulation results are quantitatively different from the experimental measurements.
Using Bayesian inference across all sets of experimental data would make it possible to calibrate the model to the experimental data while quantifying uncertainties and sources of error from model inadequacy, experimental error, and model-parameter uncertainty [!citep](DHULIPALA2026102776,DHULIPALA2025155795).
The current oxygen diffusivity and D$_2$ and D$_2$O release parameters are, therefore, best interpreted as calibrated effective kinetics for matching the observed TDS trends rather than as a mechanistic description, which will be the goal of future work.

## Input files

!style halign=left
The input files for this case are structured as follows:

- The four cases, i.e., natural oxide, 5 nm, 10 nm, and 15 nm oxide thickness samples, are simulated using the [!file](/val-2k_natural_oxide.i), [!file](/val-2k_5nm_oxide.i), [!file](/val-2k_10nm_oxide.i), and [!file](/val-2k_15nm_oxide.i) inputs, respectively.
- Their shared geometry, history, and material properties are listed in [!file](/parameters_val-2k_common.params), while the case-specific oxide thickness, output file names, and profile-output subfolder paths are defined directly in the wrapper input files.
- The shared models are organized using [!file](/val-2k_base.i), [!file](/val-2k_layer.i), [!file](/val-2k_traps.i), and [!file](/val-2k_surface.i).

The associated tests are defined in [!file](/val-2k/tests).

!alert note title=Not optimized for performance
The input files used in this study are not optimized for performance. The solver and preconditioner type, mesh size, and time stepper could be optimized to reduce computational costs and memory needs.

!bibtex bibliography
