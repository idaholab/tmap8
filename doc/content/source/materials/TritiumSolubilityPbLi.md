# TritiumSolubilityPbLi

!syntax description /Materials/TritiumSolubilityPbLi

## Overview

`TritiumSolubilityPbLi` provides the Sieverts solubility $K_s$ of hydrogen isotopes, tritium by
default, in liquid PbLi, derived from multiple sources in the literature. For convenience and use in
a variety of simulation configurations, this class creates both a Real- and AD-Real-valued material
property from the same Material object. The solubility is expressed with Sieverts' law,

!equation
C = K_s P^{1/2},

where $C$ is the concentration of hydrogen isotope in PbLi in atoms/m$^3$, $P$ is the partial
pressure of the gas in Pa, and $K_s$ is the solubility in atoms m$^{-3}$ Pa$^{-1/2}$ provided by
the selected literature model. The literature correlations are published in different bases
(atom fractions or molar concentrations), and are converted to this form as described below.
The solubility has the Arrhenius form

!equation
K_s = K_0\, B(T) \exp\left(-\frac{E_a}{RT}\right),

where $K_0$ is the pre-exponential factor in the basis of the published fit, $B(T)$ converts it to
atoms m$^{-3}$ Pa$^{-1/2}$, $E_a$ is the activation energy in J/mol, $R$ is the ideal gas constant
(its value is provided by [PhysicalConstants](source/utils/TMAP8PhysicalConstants.md)), and $T$ is
the temperature in K. The activation energy is negative for the models whose solubility decreases
with temperature.

!alert warning title=Unverified coefficients
The coefficients, units, temperature ranges, composition ranges and measured isotopes of the models
below were carried over from earlier drafts and have not yet been verified against the primary
sources. Entries that are not verified say so in their note. In particular, the pressure
normalization and units of several correlations still need to be confirmed.

## Implemented Models

The implemented solubility models are summarized in [pbli_solubility_models_table] and plotted in
[pbli_solubility_models_figure].

!table id=pbli_solubility_models_table caption=Implemented PbLi hydrogen isotope solubility models, in the basis of the published fit. $N(T)$ is the number density of metal atoms defined below, and $N_A$ is the Avogadro number. All Arrhenius expressions use the ideal gas constant value from [PhysicalConstants](source/utils/TMAP8PhysicalConstants.md).
| Enum | Expression in the published basis | Conversion $B(T)$ | Validity range (K) | Composition $x_{Li}$ | Measured isotope | Reference |
| :- | :- | :- | :- | :- | :- | :- |
| `Katsuta1985` | $X/\sqrt{P} = e^{-8.17}/\sqrt{10^5}\exp(+734/T)$ (atom fraction) | $N(T)$ | 673.15-773.15 | 0.157-0.17 | H | [!cite](Katsuta1985PbLi) |
| `Fauvet1988` | $X/\sqrt{P} = 2.7\times10^{-8}$ (atom fraction) | $N(T)$ | 718.15-728.15 | 0.157-0.17 | H | [!cite](Fauvet1988PbLi) |
| `Maeda2008` | $X/\sqrt{P} = 2.1\times10^{-6}\exp(-18.7\times10^3/RT)$ (atom fraction) | $N(T)$ | 573.15-773.15 | 0.157-0.17 | H | [!cite](Maeda2008PbLi) |
| `Reiter1991` | $K_s = 1.31\times10^{-3}\exp(-1.35\times10^3/RT)$ (mol m$^{-3}$ Pa$^{-1/2}$) | $N_A$ | 508-700 | 0.157-0.17 | H | [!cite](Reiter1991PbLi), [!cite](MasDeLesValls2008PbLi) |
| `Penalva2024` | $K_s = 1.95\times10^{-2}$ (mol m$^{-3}$ Pa$^{-1/2}$) | $N_A$ | 514.15-852.15 | 0.157 only (Pb-15.7Li) | H | [!cite](Penalva2024PbLi) |
| `Fukada2013MixingRule` | $\ln K_s = x_{Li}\ln K_{Li} + (1-x_{Li})\ln K_{Pb}$ (atoms m$^{-3}$ Pa$^{-1/2}$) | 1 | any | 0-1 | H | [!cite](S.Fukada2013MG201203) |

!media plot_pbli_review_models.py
       image_name=pbli_solubility_models.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=pbli_solubility_models_figure
       caption=Comparison of the implemented PbLi hydrogen isotope solubility correlations from [pbli_solubility_models_table], each drawn over its documented temperature range at a lithium atomic fraction of 0.17 (0.157 for `Penalva2024`). `Fukada2013MixingRule` is omitted because it depends on user-provided Sieverts constants.

## Conversion to Atoms m$^{-3}$ Pa$^{-1/2}$

Mole-based fits are multiplied by the Avogadro number $N_A$ (taken from
[PhysicalConstants](source/utils/TMAP8PhysicalConstants.md)). Fits published as the atom fraction
$X$ of hydrogen isotope in the metal are multiplied by the number density of metal atoms in PbLi,

!equation
N(T) = \frac{\rho(T) N_A}{\bar{M}},
\qquad
\bar{M} = x_{Li} M_{Li} + (1 - x_{Li}) M_{Pb},

where $\rho(T)$ is the PbLi density from [DensityPbLi](DensityPbLi.md), $\bar{M}$ is the mean atomic
mass of the metal atoms, $M_{Li} = 6.941\times10^{-3}$ kg/mol, $M_{Pb} = 207.2\times10^{-3}$ kg/mol,
and $x_{Li}$ is the
[!param](/Materials/TritiumSolubilityPbLi/lithium_atomic_fraction) parameter. This gives
$C = N(T) X$, which assumes that the atom fraction is much smaller than 1 ($X \ll 1$), as is the
case for the dilute solutions considered here. The temperature dependence of $N(T)$ is a modeling
choice made in TMAP8, so the effective activation energy of $K_s$ differs slightly from $E_a$.

## Isotope

Each model records the hydrogen isotope it was measured for (see [pbli_solubility_models_table]).
No isotope scaling is applied to the solubility: [!cite](S.Fukada2013MG201203) observed no isotope
effect in the solubility between H and D, and this is assumed to extend to T. The measured
isotope is therefore documentation only.

## Mixing Rule

The `Fukada2013MixingRule` model estimates the solubility of PbLi from the Sieverts constants of
pure liquid lithium and pure liquid lead with a logarithmic mixing rule,

!equation
\ln K_s = x_{Li}\ln K_{Li} + (1 - x_{Li})\ln K_{Pb}.

It requires the
[!param](/Materials/TritiumSolubilityPbLi/lithium_sieverts_constant) and
[!param](/Materials/TritiumSolubilityPbLi/lead_sieverts_constant) parameters (both positive, in
atoms m$^{-3}$ Pa$^{-1/2}$), which are not provided by the class, and uses
[!param](/Materials/TritiumSolubilityPbLi/lithium_atomic_fraction) as $x_{Li}$. Since the constants
are inputs, the model does not depend on temperature. It reduces to $K_{Pb}$ for $x_{Li} = 0$ and to
$K_{Li}$ for $x_{Li} = 1$. The form of the mixing rule has not yet been verified against the
primary source.

## Scaling the Model Parameters

The pre-exponential factor and the activation energy of the selected model can be scaled with the
[!param](/Materials/TritiumSolubilityPbLi/prefactor_scaling) and
[!param](/Materials/TritiumSolubilityPbLi/activation_energy_scaling) parameters, for example to
explore the sensitivity of a simulation to the uncertainty of a correlation. The properties become

!equation
K_s = f_{A}\, K_0\, B(T) \exp\left(-\frac{f_{E} E_a}{RT}\right),

where $f_A$ is `prefactor_scaling` and $f_E$ is `activation_energy_scaling`. Both default to 1, which
gives the model as published. `prefactor_scaling` must not be negative (a value of 0 sets the
property to zero), while `activation_energy_scaling` may take any value, including a negative one.
For the mixing rule, `prefactor_scaling` multiplies the mixed Sieverts constant.
Scaling does not change the documented validity range of the model, so the
`validity_action` still refers to the range of the unscaled correlation.

## Behavior when outside of range of validity

The [!param](/Materials/TritiumSolubilityPbLi/validity_action) parameter sets what TMAP8 does when a
model is evaluated outside its documented validity range, for the temperature (checked at every
evaluation) and the lithium atomic fraction (checked once, at construction). The ranges are listed
in [pbli_solubility_models_table]. Note that `Penalva2024` is documented for Pb-15.7Li only, so
the default $x_{Li} = 0.17$ triggers a composition warning unless
`lithium_atomic_fraction = 0.157` is set.

- `ignore`: nothing happens and the model is silently extrapolated.
- `warning` (default): the simulation continues. Each out-of-range temperature evaluation is recorded in MOOSE's
  solution-invalidity system and summarized in the "Warnings History" table printed at the end of
  the run, with the number of occurrences per time step. Set
  [!param](/Problem/FEProblem/immediately_print_invalid_solution) to print them as they occur.
  A composition violation is reported as a single warning.
- `error`: the run stops immediately with a message giving the model, the offending value
  and the documented range.

Extrapolating a correlation beyond the conditions it was fit to can give unphysical values, so
`warning` or `error` is recommended unless the extrapolation is intentional.

!syntax parameters /Materials/TritiumSolubilityPbLi

!syntax inputs /Materials/TritiumSolubilityPbLi

!syntax children /Materials/TritiumSolubilityPbLi

!bibtex bibliography
