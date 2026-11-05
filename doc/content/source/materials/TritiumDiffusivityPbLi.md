# TritiumDiffusivityPbLi

!syntax description /Materials/TritiumDiffusivityPbLi

## Overview

`TritiumDiffusivityPbLi` computes the diffusivity $D$ of hydrogen isotopes, tritium by default, in
liquid PbLi. This diffusivity is presented as both a regular and AD material
property.
The property fits are implemented as published in the literature, except where the notes column of
[pbli_diffusivity_models_table] states otherwise.

The diffusivity is computed as

!equation
D = f_{A}\, f_{iso}\, D_0 \exp\left(-\frac{f_{E} E_a}{RT}\right),

where $D_0$ is the pre-exponential factor in m$^2$/s,
$E_a$ is the activation energy in J/mol,
$R$ is the ideal gas constant in J/mol/K from [PhysicalConstants](source/utils/TMAP8PhysicalConstants.md),
and $T$ is teh temperature in K.
The $f_i$ parameters are scaling parameters described below.

To select the model of diffusivity to use (i.e., $D_0$ and $E_a$),
the [!param](/Materials/TritiumDiffusivityPbLi/model)
parameter +must+ be provided, as the available PbLi correlations were measured for different
hydrogen isotopes, temperature and pressure ranges, and compositions.
The different options are documented in [pbli_diffusivity_models_table].

## Hydrogen Isotope and Isotope Scaling

The [!param](/Materials/TritiumDiffusivityPbLi/isotope) parameter selects the hydrogen isotope
(`H`, `D` or `T`, default `T`) the diffusivity is requested for. Each model records the isotope it
was measured for (see [pbli_diffusivity_models_table]). If the two differ, the
`validity_action` applies, with a message naming both isotopes. Since the default isotope is `T`,
this includes every model that was not measured for tritium (except the isotope-independent
`Reiter1991`), unless
[!param](/Materials/TritiumDiffusivityPbLi/isotope_scaling) ($f_{iso}$) is `true`.
With isotope scaling, the pre-exponential factor is multiplied by the classical mass factor

!equation
\frac{D_{requested}}{D_{measured}} = \sqrt{\frac{m_{measured}}{m_{requested}}},

where $m$ is the mass number of the isotope (1, 2 and 3 for H, D and T). This is the ratio predicted
by classical rate theory. [!cite](S.Fukada2013MG201203) reports a hydrogen diffusivity 1.4 times
larger than that of deuterium, "near to a value predicted from the classical theory" ($\sqrt{2}
\approx 1.41$). Isotope scaling composes with the parameter scaling described below.

## Scaling the Model Parameters

The pre-exponential factor and the activation energy of the selected model can be scaled with the
[!param](/Materials/TritiumDiffusivityPbLi/prefactor_scaling) ($f_A$) and
[!param](/Materials/TritiumDiffusivityPbLi/activation_energy_scaling) ($f_E$) parameters,
for example to explore the sensitivity of a simulation to the uncertainty of a correlation.
`prefactor_scaling` must not be negative (a value of 0 sets the property to zero), while
`activation_energy_scaling` may take any value, including a negative one.
Scaling does not change the documented validity range of the model, so the
`validity_action` still refers to the range of the unscaled correlation.

## Implemented Models

The implemented diffusivity models are summarized in [pbli_diffusivity_models_table] and
plotted in [pbli_diffusivity_models_figure].

!table id=pbli_diffusivity_models_table caption=Implemented PbLi hydrogen isotope diffusivity models, with the pre-exponential factor $D_0$ in m$^2$/s and the activation energy $E_a$ in J/mol of the expression above. All models assume the eutectic composition, with a lithium atomic fraction $x_{Li}$ between 0.157 and 0.17 (Pb-17Li). Quantities marked with \* do not have a documented range.
| Enum | $D_0$ (m$^2$/s), $E_a$ (J/mol) | Temperature range (K) | Pressure range (Pa) | Measured isotope | Reference | Notes |
| :- | :- | :- | :- | :- | :- | :- |
| `Fauvet1988` | $1.5\times10^{-9}$, 0 | 723.15 (single point) | $10^{3}$-$10^{4}$ | hydrogen | [!cite](Fauvet1988PbLi) | Single datum at 723.15 K (450 C), treated as temperature independent. The temperature is not checked against any range. |
| `Reiter1991` | $4.03\times10^{-8}$, $19.5\times10^{3}$ | 508-700 | $10^{3}$-$10^{5}$ | D and T average | [!cite](Reiter1991PbLi), [!cite](MasdeLesValls2008) | Isotope-independent fit (average of D and T) for eutectic Pb-17Li, used as published for any isotope; see `Reiter1991Hydrogen_HTM` and `Reiter1991Deuterium_HTM` for the isotope-specific fits. |
| `Reiter1991Hydrogen_HTM` | $7.48\times10^{-8}$, $22.956\times10^{3}$ | 524-690 | $10^{3}$-$10^{5}$ | hydrogen | [!cite](Reiter1991PbLi), [!cite](delaporte-mathurin_remdelaportemathurinh-transport-materials_2023) | Not as published: Arrhenius fit of Reiter's 16 digitized hydrogen data points. |
| `Reiter1991Deuterium_HTM` | $1.38\times10^{-8}$, $13.609\times10^{3}$ | 524-691 | $10^{3}$-$10^{5}$ | deuterium | [!cite](Reiter1991PbLi), [!cite](delaporte-mathurin_remdelaportemathurinh-transport-materials_2023) | Not as published: Arrhenius fit of Reiter's 6 digitized deuterium data points. |
| `Shibuya1987` | $2.62\times10^{-9}$, $6.63\times10^{3}$ | 573.15-773.15 | \* | tritium | [!cite](Shibuya1987PbLi), [!cite](MasdeLesValls2008) | Tritium, isothermal release from neutron-irradiated Li17Pb83. Not as published: least-squares Arrhenius fit of the three published values, with a residual of up to about 3 %. The prefactor listed in [!cite](MasdeLesValls2008) has a typo (exponent of -3 instead of -9). |
| `Terai1992` | $2.5\times10^{-7}$, $27\times10^{3}$ | 573.15-973.15 | $3\times10^{3}$ | tritium | [!cite](Terai1992PbLi), [!cite](MasdeLesValls2008) | Tritium diffusivity fit in Pb-17Li under neutron irradiation. |
| `Maeda2008` | $1.8\times10^{-8}$, $11.59\times10^{3}$ | 573.15-973.15 | \* | hydrogen | [!cite](Maeda2008) | Hydrogen fit from unsteady permeation through molten Li-Pb. Surface resistance affected the data below 673 K. |
| `Edao2011Hydrogen` | $8.18\times10^{-8}$, $15.8\times10^{3}$ | 573-873 | \* | hydrogen | [!cite](Edao2011PbLi) | Hydrogen, transient permeation through Li17Pb83. |
| `Edao2011Deuterium` | $5.73\times10^{-8}$, $13.6\times10^{3}$ | 573-873 | \* | deuterium | [!cite](Edao2011PbLi) | Deuterium, transient permeation through Li17Pb83. |
| `Okitsu2012Hydrogen` | $2\times10^{-8}$, $11.2\times10^{3}$ | 773-973 | \* | hydrogen | [!cite](Okitsu2012PbLi) | Hydrogen in two-component (H + D) permeation through Li17Pb83. Not as published: the pre-exponential factor corrects a typo in the paper. |
| `Okitsu2012Deuterium` | $4.8\times10^{-8}$, $20.3\times10^{3}$ | 773-973 | \* | deuterium | [!cite](Okitsu2012PbLi) | Deuterium in two-component (H + D) permeation through Li17Pb83. |
| `Okada2012Hydrogen` | $4.68\times10^{-8}$, $17.6\times10^{3}$ | 773-973 | \* | hydrogen | [!cite](Okada2012PbLi) | Hydrogen, permeation through Li-Pb, 5 data points. Same data as Okitsu et al. (2012), but different fit. |
| `Okada2012Deuterium` | $2.64\times10^{-8}$, $15.6\times10^{3}$ | 773-973 | \* | deuterium | [!cite](Okada2012PbLi) | Deuterium, permeation through Li-Pb, 5 data points. Same data as Okitsu et al. (2012), but different fit. |

Models whose name ends with `_HTM` are Arrhenius fits of the data points of
[!cite](Reiter1991PbLi) from the h-transport-materials database
[!citep](delaporte-mathurin_remdelaportemathurinh-transport-materials_2023).
`Reiter1991` is the isotope-averaged expression usually quoted for [!cite](Reiter1991PbLi), averaged over D and T. It is flagged as isotope-independent: it is used as published for any requested isotope, never scaled, and never triggers an isotope mismatch.
`Shibuya1987` is a fit of the three values published in [!cite](Shibuya1987PbLi), which are shown
together with the fit in [pbli_diffusivity_models_figure].
The `Okitsu2012*` and `Okada2012*` models are two different fits of the same permeation data,
from [!cite](Okitsu2012PbLi) and [!cite](Okada2012PbLi).

!media plot_pbli_review_models.py
       image_name=pbli_diffusivity_models.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=pbli_diffusivity_models_figure
       caption=Comparison of the implemented PbLi hydrogen isotope diffusivity models from [pbli_diffusivity_models_table], each drawn over its documented temperature range. The data points are the three values of `Shibuya1987` published in [!cite](Shibuya1987PbLi) (6.6e-10, 7.8e-10 and 9.5e-10 m$^2$/s at 573, 673 and 773 K).

## Composition

The [!param](/Materials/TritiumDiffusivityPbLi/lithium_atomic_fraction) parameter (default 0.17) is
the lithium atomic fraction of the PbLi. It does not affect the diffusivity expressions, but it is
checked once, at the start of the simulation, against the documented composition range of the
selected model with the `validity_action` behavior described below.

## Pressure

The [!param](/Materials/TritiumDiffusivityPbLi/pressure) parameter is an optional variable
providing the hydrogen isotope partial pressure in Pa.
It does not affect the diffusivity expressions:
it is only used to check the pressure against the documented pressure range of the selected model
([pbli_diffusivity_models_table]), at every evaluation, with the `validity_action` behavior
described below. The check is skipped if no pressure is provided, and for the models without a
documented pressure range. For example, `Terai1992` is documented for a single pressure of
$3\times10^3$ Pa. The temperature of `Fauvet1988`, documented for a single temperature, is never checked.

## Behavior when outside of range of validity

The [!param](/Materials/TritiumDiffusivityPbLi/validity_action) parameter sets what TMAP8 does when a model is evaluated
outside its documented validity range, for the temperature and the pressure (checked at every
evaluation), and the lithium atomic fraction and the isotope (both checked once, at construction):

- `ignore`: nothing happens and the model is silently extrapolated.
- `warning` (default): the simulation continues. Each out-of-range temperature or pressure evaluation is recorded in MOOSE's
  solution-invalidity system and summarized in the "Warnings History" table printed at the end of
  the run, with the number of occurrences per time step. Set
  [!param](/Problem/FEProblem/immediately_print_invalid_solution) to print them as they occur.
  Composition and isotope violations are reported as a single warning.
- `error`: the run stops immediately with a message giving the model, the offending value
  and the documented range.

Extrapolating a correlation beyond the conditions it was fit to can give unphysical values, so
`warning` or `error` is advisable unless the extrapolation is intentional.

## Example Input File

The following block computes the diffusivity of the `Terai1992` model from a temperature variable,
and provides both the regular and the AD material property.

!listing test/tests/pbli_transport_materials/pbli_single_point_property_base.i block=Materials/pbli_property

!syntax parameters /Materials/TritiumDiffusivityPbLi

!syntax inputs /Materials/TritiumDiffusivityPbLi

!syntax children /Materials/TritiumDiffusivityPbLi

!bibtex bibliography
