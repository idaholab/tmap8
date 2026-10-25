# TritiumDiffusivityPbLi

!syntax description /Materials/TritiumDiffusivityPbLi

## Overview

`TritiumDiffusivityPbLi` computes the diffusivity $D$ of hydrogen isotopes, tritium by default, in
liquid PbLi. This diffusivity is presented as both a regular Real- and AD-Real-valued material
property for use in a variety of simulation configurations. The property fits are implemented as
published in the literature and stored in the implementation directly in units of m$^2$/s.
To select the model of diffusivity to use, the [!param](/Materials/TritiumDiffusivityPbLi/model)
parameter +must+ be provided, as the available PbLi correlations were measured for different
hydrogen isotopes, temperature ranges and compositions.

!alert warning title=Unverified coefficients
The coefficients, temperature ranges, composition ranges and measured isotopes of the models
below were carried over from earlier drafts and have not yet been verified against the primary
sources. Entries that are not verified say so in their note.

## Implemented Models

The implemented diffusivity models are summarized in [pbli_diffusivity_models_table] and
plotted in [pbli_diffusivity_models_figure].

!table id=pbli_diffusivity_models_table caption=Implemented PbLi hydrogen isotope diffusivity models. All Arrhenius expressions use the ideal gas constant value from [PhysicalConstants](source/utils/TMAP8PhysicalConstants.md). The composition range is the lithium atomic fraction $x_{Li}$ (0.157 to 0.17 corresponds to the eutectic Pb-17Li).
| Enum | Expression used in TMAP8 | Property units | Validity range (K) | Measured isotope | Reference | Notes |
| :- | :- | :- | :- | :- | :- | :- |
| `Fauvet1988` | $D = 1.5\times10^{-9}$ | m$^2$/s | 718.15-728.15 | H | [!cite](Fauvet1988PbLi) | Single datum at 450 C, treated as temperature independent |
| `Reiter1991` | $D = 4.03\times10^{-8}\exp(-19.5\times10^3/RT)$ | m$^2$/s | 508-700 | H | [!cite](Reiter1991PbLi), [!cite](MasDeLesValls2008PbLi) | Recommended database fit for eutectic Pb-17Li |
| `Terai1992` | $D = 2.50\times10^{-7}\exp(-27.0\times10^3/RT)$ | m$^2$/s | 573.15-973.15 | T | [!cite](Terai1992PbLi) | Tritium diffusivity in Pb-17Li |
| `Maeda2008` | $D = 1.8\times10^{-8}\exp(-11.59\times10^3/RT)$ | m$^2$/s | 573.15-773.15 | H | [!cite](Maeda2008PbLi) | Hydrogen isotope fit measured in molten Li-Pb |

All models are documented for a lithium atomic fraction between 0.157 and 0.17.

!media plot_pbli_review_models.py
       image_name=pbli_diffusivity_models.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=pbli_diffusivity_models_figure
       caption=Comparison of the implemented PbLi hydrogen isotope diffusivity correlations from [pbli_diffusivity_models_table], each drawn over its documented temperature range.

## Hydrogen Isotope and Isotope Scaling

The [!param](/Materials/TritiumDiffusivityPbLi/isotope) parameter selects the hydrogen isotope
(`H`, `D` or `T`, default `T`) the diffusivity is requested for. Each model records the isotope it
was measured for (see [pbli_diffusivity_models_table]). If the two differ, the
`validity_action` applies, with a message naming both isotopes, unless
[!param](/Materials/TritiumDiffusivityPbLi/isotope_scaling) is `true`. With isotope scaling, the
pre-exponential factor is multiplied by the classical mass factor

!equation
\frac{D_{requested}}{D_{measured}} = \sqrt{\frac{m_{measured}}{m_{requested}}},

where $m$ is the mass number of the isotope (1, 2 and 3 for H, D and T). This is the ratio predicted
by classical rate theory. [!cite](S.Fukada2013MG201203) reports a hydrogen diffusivity 1.4 times
larger than that of deuterium, "near to a value predicted from the classical theory" ($\sqrt{2}
\approx 1.41$). Isotope scaling composes with the parameter scaling described below.

## Composition

The [!param](/Materials/TritiumDiffusivityPbLi/lithium_atomic_fraction) parameter (default 0.17) is
the lithium atomic fraction of the PbLi. It does not enter the diffusivity expressions, but it is
checked once, at the start of the simulation, against the documented composition range of the
selected model with the `validity_action` behavior described below.

## Scaling the Model Parameters

The pre-exponential factor and the activation energy of the selected model can be scaled with the
[!param](/Materials/TritiumDiffusivityPbLi/prefactor_scaling) and
[!param](/Materials/TritiumDiffusivityPbLi/activation_energy_scaling) parameters, for example to explore the
sensitivity of a simulation to the uncertainty of a correlation. The properties become

!equation
D = f_{A}\, f_{iso}\, D_0 \exp\left(-\frac{f_{E} E_a}{RT}\right),

where $D_0$ is the pre-exponential factor of the selected model, $f_A$ is `prefactor_scaling`,
$f_E$ is `activation_energy_scaling`, $f_{iso}$ is the isotope scaling factor (1 unless
`isotope_scaling` is `true`), and $E_a$ is the activation energy of the selected model in J/mol.
Both scaling parameters default to 1, which gives the model as published.
`prefactor_scaling` must not be negative (a value of 0 sets the property to zero), while
`activation_energy_scaling` may take any value, including a negative one.
Scaling does not change the documented validity range of the model, so the
`validity_action` still refers to the range of the unscaled correlation.

## Behavior when outside of range of validity

The [!param](/Materials/TritiumDiffusivityPbLi/validity_action) parameter sets what TMAP8 does when a model is evaluated
outside its documented validity range, for the temperature (checked at every evaluation), the
lithium atomic fraction and the isotope (both checked once, at construction):

- `ignore`: nothing happens and the model is silently extrapolated.
- `warning` (default): the simulation continues. Each out-of-range temperature evaluation is recorded in MOOSE's
  solution-invalidity system and summarized in the "Warnings History" table printed at the end of
  the run, with the number of occurrences per time step. Set
  [!param](/Problem/FEProblem/immediately_print_invalid_solution) to print them as they occur.
  Composition and isotope violations are reported as a single warning.
- `error`: the run stops immediately with a message giving the model, the offending value
  and the documented range.

Extrapolating a correlation beyond the conditions it was fit to can give unphysical values, so
`warning` or `error` is recommended unless the extrapolation is intentional.

!syntax parameters /Materials/TritiumDiffusivityPbLi

!syntax inputs /Materials/TritiumDiffusivityPbLi

!syntax children /Materials/TritiumDiffusivityPbLi

!bibtex bibliography
