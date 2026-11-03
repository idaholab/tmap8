# TritiumSolubilityPbLi

!syntax description /Materials/TritiumSolubilityPbLi

## Overview

`TritiumSolubilityPbLi` provides the Sieverts solubility $K_s$ of hydrogen isotopes in liquid PbLi,
derived from multiple sources in the literature. For convenience and use in a variety of simulation
configurations, this class creates both a regular and AD material property from the same
Material object. The solubility is expressed with Sieverts' law,

!equation
C = K_s P^{1/2},

where $C$ is the concentration of hydrogen isotope in PbLi in atoms/m$^3$, $P$ is the partial
pressure of the hydrogen isotope gas in Pa, and $K_s$ is the solubility in atoms/m$^{3}$/Pa$^{1/2}$
provided by the selected literature model. The literature correlations are published in
different bases (atom fractions or molar concentrations) and are converted to this form as
described below.
The solubility has the Arrhenius form

!equation
K_s = f_{A}\, K_0 \exp\left(-\frac{f_{E} E_a}{RT}\right),

where $K_0$ is the pre-exponential factor, $E_a$ is the activation energy in J/mol, $R$ is the ideal
gas constant in J/mol/K (its value is provided by [PhysicalConstants](source/utils/TMAP8PhysicalConstants.md)),
and $T$ is the temperature in K. the $f_i$ terms are scaling parameters detailed below.
This expression is in the basis of the published fit, and its
result is then converted to atoms/m$^{3}$/Pa$^{1/2}$ as described in
[#conversion]. The activation energy is set to zero for the models that are temperature independent.

## Scaling the Model Parameters

The pre-exponential factor and the activation energy of the selected model can be scaled with the
[!param](/Materials/TritiumSolubilityPbLi/prefactor_scaling) ($f_{A} \geq 0$) and
[!param](/Materials/TritiumSolubilityPbLi/activation_energy_scaling) ($f_{E}$) parameters, for example to
explore the sensitivity of a simulation to the uncertainty of a correlation.
Both default to 1, which gives the model as published.
Note that the scaling term (f_{A}) is applied before the conversion to atoms/m$^{3}$/Pa$^{1/2}$.
Scaling does not change the documented validity range of the model, so the
`validity_action` (see below) still refers to the range of the unscaled correlation.

## Conversion to atoms/m$^{3}$/Pa$^{1/2}$ id=conversion

Models from the literature are expressed in different ways and in different units.
All are converted to Sieverts' solubilities in atoms/m$^{3}$/Pa$^{1/2}$ in this class for consistency.

Mole-based fits are multiplied by the Avogadro number $N_A$ (taken from
[PhysicalConstants](source/utils/TMAP8PhysicalConstants.md)). Fits published as the atom fraction
$X$ of hydrogen isotope in the metal are multiplied by the number density of metal atoms in PbLi,

!equation id=eq:at_frac
N = \frac{\rho N_A}{\bar{M}},
\qquad
\bar{M} = x_{Li} M_{Li} + (1 - x_{Li}) M_{Pb},

where $\bar{M}$ is the mean atomic mass of the metal atoms, $M_{Li}$ and $M_{Pb}$ are the molar
masses of lithium and lead in g/mol, set with the
[!param](/Materials/TritiumSolubilityPbLi/lithium_molar_mass) and
[!param](/Materials/TritiumSolubilityPbLi/lead_molar_mass) parameters (default 6.941 and 207.2
g/mol), and $x_{Li}$ is the
[!param](/Materials/TritiumSolubilityPbLi/lithium_atomic_fraction) parameter. The density $\rho$
is not defined in this class: it is evaluated with the fluid properties given in the
[!param](/Materials/TritiumSolubilityPbLi/fp) parameter, which must be a
[LeadLithiumFluidProperties](LeadLithiumFluidProperties.md optional=True) object. These fluid
properties provide the density in kg/m$^3$ from [!cite](MasdeLesValls2008) for
508-880 K, which is converted to g/m$^3$ to be consistent with the molar masses. The parameter is required by
the models published as atom fractions, and the density is not evaluated for the others, even if
the parameter is provided.

This gives $C = N X$, which assumes that the atom fraction is much smaller than 1 ($X \ll 1$), as is
the case for the dilute solutions considered here. The temperature dependence of the number density $N$ is a modeling
choice made in TMAP8, so the effective activation energy of $K_s$ differs slightly from $E_a$. The
density is evaluated at the pressure provided by the
[!param](/Materials/TritiumSolubilityPbLi/pressure) parameter, or at the standard atmosphere
(`atm_to_Pa` in [PhysicalConstants](source/utils/TMAP8PhysicalConstants.md)) if it is not provided.

The correlation of `Katsuta1985` [!citep](Katsuta1985PbLi,MasdeLesValls2008) is published as a Sieverts' constant
$\sqrt{P_{atm}}/X = 2.9\times10^3$ in atm$^{1/2}$, with $P_{atm}$ in atm, and is converted to
$X/\sqrt{P} = 1/(2.9\times10^3\sqrt{101325})$ with the pressure in Pa.

## Implemented Models

The implemented solubility models are summarized in [pbli_solubility_models_table] and plotted in
[pbli_solubility_models_figure].

!table id=pbli_solubility_models_table caption=Implemented PbLi hydrogen isotope solubility models, with the expression and the unit in which each correlation was published. All models are converted to atoms/m$^{3}$/Pa$^{1/2}$. All Arrhenius expressions use the ideal gas constant value from [PhysicalConstants](source/utils/TMAP8PhysicalConstants.md), with the activation energy in J/mol and the temperature in K. Molar concentrations are in moles of hydrogen isotope atoms (not H$_2$ molecules). The composition is the lithium atomic fraction $x_{Li}$ (0.157 to 0.17 corresponds to the eutectic Pb-17Li). Quantities marked with \* do not have a documented range.
| Enum | Expression in the published basis | Published unit | Temperature range (K) | Pressure range (Pa) | Composition $x_{Li}$ | Measured isotope | Reference | Notes |
| :- | :- | :- | :- | :- | :- | :- | :- | :- |
| `Katsuta1985` | $X/\sqrt{P} = 1.08\times10^{-6}$ | at. frac. $\cdot$ Pa$^{-1/2}$ | 573-723 | $1.48\times10^{4}$-$1.06\times10^{5}$ | 0.157-0.17 | hydrogen | [!cite](Katsuta1985PbLi), [!cite](MasdeLesValls2008) | Hydrogen in Li17Pb83, hot extraction, no temperature dependence. |
| `Fauvet1988` | $X/\sqrt{P} = 2.7\times10^{-8}$ | at. frac. $\cdot$ Pa$^{-1/2}$ | 718.15-728.15 | $10^{3}$-$10^{4}$ | 0.157-0.17 | hydrogen | [!cite](Fauvet1988PbLi) | Single datum at 723 K, treated as temperature independent. |
| `Reiter1991Tritium` | $X/\sqrt{P} = 2.32\times10^{-8}\exp(-1.35\times10^3/RT)$ | at. frac. $\cdot$ Pa$^{-1/2}$ | 508-700 | $10^{3}$-$10^{5}$ | 0.157-0.17 | tritium | [!cite](Reiter1991PbLi), [!cite](MasdeLesValls2008) | Published tritium fit for eutectic Pb-17Li. |
| `Reiter1991Hydrogen` | $X/\sqrt{P} = 2.44\times10^{-8}\exp(-1.35\times10^3/RT)$ | at. frac. $\cdot$ Pa$^{-1/2}$ | 508-700 | $10^{3}$-$10^{5}$ | 0.157-0.17 | hydrogen | [!cite](Reiter1991PbLi), [!cite](MasdeLesValls2008) | Published hydrogen fit for eutectic Pb-17Li. |
| `Reiter1991Deuterium` | $X/\sqrt{P} = 2.36\times10^{-8}\exp(-1.35\times10^3/RT)$ | at. frac. $\cdot$ Pa$^{-1/2}$ | 508-700 | $10^{3}$-$10^{5}$ | 0.157-0.17 | deuterium | [!cite](Reiter1991PbLi), [!cite](MasdeLesValls2008) | Published deuterium fit for eutectic Pb-17Li. |
| `Aiello2006` | $K_s = 2.37\times10^{-1}\exp(-12.844\times10^3/RT)$ | mol $\cdot$ m$^{-3}$ $\cdot$ Pa$^{-1/2}$ | 600-900 | $10^{3}$-$10^{5}$ | 0.158 | hydrogen | [!cite](AIELLO2006639) | Hydrogen absorption in Pb-15.8Li with the SOLE device. |
| `Maeda2008` | $X/\sqrt{P} = 2.1\times10^{-6}\exp(-18.7\times10^3/RT)$ | at. frac. $\cdot$ Pa$^{-1/2}$ | 573.15-973.15 | \* | 0.157-0.17 | hydrogen | [!cite](Maeda2008) | Hydrogen fit from unsteady permeation through molten Li-Pb. |
| `Edao2011Hydrogen` | $X/\sqrt{P} = 2.73\times10^{-7}\exp(-4.18\times10^3/RT)$ | at. frac. $\cdot$ Pa$^{-1/2}$ | 573-873 | \* | 0.157-0.17 | hydrogen | [!cite](Edao2011PbLi) | Hydrogen, transient permeation through Li17Pb83. |
| `Edao2011Deuterium` | $X/\sqrt{P} = 4.21\times10^{-7}\exp(-3.1\times10^3/RT)$ | at. frac. $\cdot$ Pa$^{-1/2}$ | 573-873 | \* | 0.157-0.17 | deuterium | [!cite](Edao2011PbLi) | Deuterium, transient permeation through Li17Pb83. |
| `Okitsu2012Hydrogen` | $X/\sqrt{P} = 8.6\times10^{-5}\exp(-53.8\times10^3/RT)$ | at. frac. $\cdot$ Pa$^{-1/2}$ | 773-973 | \* | 0.157-0.17 | hydrogen | [!cite](Okitsu2012PbLi) | Hydrogen in two-component (H + D) permeation through Li17Pb83. The pre-exponential factor corrects a typo in the paper. |
| `Okitsu2012Deuterium` | $X/\sqrt{P} = 1.1\times10^{-4}\exp(-55.2\times10^3/RT)$ | at. frac. $\cdot$ Pa$^{-1/2}$ | 773-973 | \* | 0.157-0.17 | deuterium | [!cite](Okitsu2012PbLi) | Deuterium in two-component (H + D) permeation through Li17Pb83. |
| `Okada2012Hydrogen` | $X/\sqrt{P} = 1.41\times10^{-4}\exp(-57.4\times10^3/RT)$ | at. frac. $\cdot$ Pa$^{-1/2}$ | 773-973 | \* | 0.157-0.17 | hydrogen | [!cite](Okada2012PbLi) | Hydrogen, permeation through Li-Pb. Same data as Okitsu et al. (2012), but different fit. |
| `Okada2012Deuterium` | $X/\sqrt{P} = 1.65\times10^{-4}\exp(-57.6\times10^3/RT)$ | at. frac. $\cdot$ Pa$^{-1/2}$ | 773-973 | \* | 0.157-0.17 | deuterium | [!cite](Okada2012PbLi) | Deuterium, permeation through Li-Pb. Same data as Okitsu et al. (2012), but different fit. |
| `Wu1983` | $X/\sqrt{P} = 6.33\times10^{-7}$ | at. frac. $\cdot$ Pa$^{-1/2}$ | 850-1040 | $10^{-1}$-$10^{0}$ | 0.157-0.17 | deuterium | [!cite](Wu1983PbLi), [!cite](MasdeLesValls2008) | Deuterium, temperature independent value from Wu (1983). Wu (1983) provides other models for different compositions, which are not yet included here. |
| `Chan1984` | $X/\sqrt{P} = 4.7\times10^{-7}\exp(-9\times10^3/RT)$ | at. frac. $\cdot$ Pa$^{-1/2}$ | 573-773 | up to $10^{4}$ | 0.157-0.17 | hydrogen | [!cite](Chan1984PbLi), [!cite](MasdeLesValls2008) | Hydrogen; extrapolation of Li-rich alloy data to Pb-17Li. More compositions are available in Chan and Veleckis (1984). |
| `Fukada2013MixingRule` | $\ln K_s = x_{Li}\ln K_{Li} + (1-x_{Li})\ln K_{Pb}$ | atoms $\cdot$ m$^{-3}$ $\cdot$ Pa$^{-1/2}$ | \* | \* | 0-1 | hydrogen | [!cite](S.Fukada2013MG201203) | Logarithmic mixing rule using user-provided Sieverts constants of pure liquid lithium and lead. |
| `Alberro2015` | $K_s = 8.64\times10^{-3}\exp(-0.9\times10^3/RT)$ | mol $\cdot$ m$^{-3}$ $\cdot$ Pa$^{-1/2}$ | 523-922 | $10^{0}$-$10^{5}$ | 0.157-0.17 | hydrogen | [!cite](Alberro2015PbLi) | Hydrogen solubility in eutectic PbLi. |
| `Penalva2024` | $K_s = 1.95\times10^{-2}$ | mol $\cdot$ m$^{-3}$ $\cdot$ Pa$^{-1/2}$ | 514.15-852.15 | \* | 0.157 | hydrogen | [!cite](Penalva2024PbLi) | Certified Pb-15.7Li data averaged over 514.15-852.15 K, treated as temperature independent. |

Models whose name contains `Reiter1991` and an isotope are the isotope-specific fits published in
[!cite](Reiter1991PbLi). The `Okitsu2012*` and `Okada2012*` models are two different fits of the same
permeation data, from [!cite](Okitsu2012PbLi) and [!cite](Okada2012PbLi). `Fukada2013MixingRule`
is the only model without a documented temperature range, since it depends on user-provided
constants (see below).
An additional solubility model from Schumacher is available, but is not included here:
the references reporting it conflict, and this remains to be resolved.

!media plot_pbli_review_models.py
       image_name=pbli_solubility_models.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=pbli_solubility_models_figure
       caption=Comparison of the implemented PbLi hydrogen isotope solubility correlations from [pbli_solubility_models_table], each drawn over its documented temperature range. The models published as atom fractions are plotted at a lithium atomic fraction of 0.17. `Fukada2013MixingRule` is omitted because it depends on user-provided Sieverts constants.

## Isotope

Each model records the hydrogen isotope it was measured for (see [pbli_solubility_models_table]).
The solubility materials have no isotope parameter, and no isotope scaling is applied:
[!cite](S.Fukada2013MG201203) observed no isotope effect in the solubility between H and D, and this
is assumed to extend to T. The measured isotope is therefore only recorded for documentation.

## Mixing Rule

The `Fukada2013MixingRule` model estimates the solubility of PbLi from the Sieverts constants of
pure liquid lithium and pure liquid lead with a logarithmic mixing rule [!citep](S.Fukada2013MG201203),

!equation
\ln K_s = x_{Li}\ln K_{Li} + (1 - x_{Li})\ln K_{Pb}.

It requires the
[!param](/Materials/TritiumSolubilityPbLi/lithium_sieverts_constant) and
[!param](/Materials/TritiumSolubilityPbLi/lead_sieverts_constant) parameters (both positive, in
atoms $\cdot$ m$^{-3}$ $\cdot$ Pa$^{-1/2}$), which are not provided by the class, and uses
[!param](/Materials/TritiumSolubilityPbLi/lithium_atomic_fraction) as $x_{Li}$. Since the constants
are inputs, the model does not depend on temperature, and it has no documented temperature or
pressure range. It reduces to $K_{Pb}$ for $x_{Li} = 0$ and to $K_{Li}$ for $x_{Li} = 1$.
When using the mixing rule, the scaling parameter [!param](/Materials/TritiumSolubilityPbLi/prefactor_scaling)
multiplies the mixed Sieverts constant.

## Pressure

The [!param](/Materials/TritiumSolubilityPbLi/pressure) parameter is an optional variable
providing the hydrogen isotope partial pressure in Pa. Besides setting the pressure at which the density is evaluated
(see above), it is used to check the pressure against the documented pressure range of the selected
model ([pbli_solubility_models_table]), at every evaluation, with the `validity_action` behavior
described below. The check is skipped if no pressure is provided, and for the models without a
documented pressure range. The range of `Katsuta1985` was published in atm and is converted to Pa.

## Behavior when outside of range of validity

The [!param](/Materials/TritiumSolubilityPbLi/validity_action) parameter sets what TMAP8 does when a
model is evaluated outside its documented validity range, for the temperature and the pressure
(checked at every evaluation) and the lithium atomic fraction (checked once, at construction). The
ranges are listed in [pbli_solubility_models_table]. Note that `Penalva2024` is documented for
Pb-15.7Li only and `Aiello2006` for Pb-15.8Li only, so the default $x_{Li} = 0.17$ triggers a
composition warning unless `lithium_atomic_fraction = 0.157` (`Penalva2024`) or
`lithium_atomic_fraction = 0.158` (`Aiello2006`) is set.

- `ignore`: nothing happens and the model is silently extrapolated.
- `warning` (default): the simulation continues. Each out-of-range temperature or pressure evaluation is recorded in MOOSE's
  solution-invalidity system and summarized in the "Warnings History" table printed at the end of
  the run, with the number of occurrences per time step. Set
  [!param](/Problem/FEProblem/immediately_print_invalid_solution) to print them as they occur.
  A composition violation is reported as a single warning.
- `error`: the run stops immediately with a message giving the model, the offending value
  and the documented range.

Extrapolating a correlation beyond the conditions it was fit to can give unphysical values, so
`warning` or `error` is advisable unless the extrapolation is intentional.

!alert note title=Density temperature range and composition
The density correlation of the fluid properties from [LeadLithiumFluidProperties](LeadLithiumFluidProperties.md optional=True)
is valid for 508-880 K, and MOOSE flags an invalid solution if the temperature is outside this range.
This warning is not controlled by the `validity_action` parameter, so it also appears with `validity_action = ignore`.
It affects the atom-fraction models documented above 880 K, for which the density is extrapolated:
`Wu1983` (up to 1040 K), `Maeda2008` (up to 973.15 K), `Okitsu2012Hydrogen`,
`Okitsu2012Deuterium`, `Okada2012Hydrogen` and `Okada2012Deuterium` (up to 973 K).
In addition, the correlation of [!citep](MasdeLesValls2008) was established for Pb-16Li, and it is
used here for any lithium atomic fraction, while the mean atomic mass $\bar{M}$ does depend on
$x_{Li}$.

!syntax parameters /Materials/TritiumSolubilityPbLi

!syntax inputs /Materials/TritiumSolubilityPbLi

!syntax children /Materials/TritiumSolubilityPbLi

!bibtex bibliography
