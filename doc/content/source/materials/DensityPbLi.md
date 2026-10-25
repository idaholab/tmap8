# DensityPbLi

!syntax description /Materials/DensityPbLi

## Overview

`DensityPbLi` computes the temperature-dependent density $\rho$ of PbLi in g/m$^3$. The density
is presented as both a regular Real- and AD-Real-valued material property for use in a variety of
simulation configurations.

The density is not used by the
[TritiumDiffusivityPbLi](TritiumDiffusivityPbLi.md) material, but the number density of metal atoms
$N(T) = \rho(T) N_A / \bar{M}$ derived from the same correlation converts the PbLi solubility
correlations published as atom fractions to concentrations, as described in
[TritiumSolubilityPbLi](TritiumSolubilityPbLi.md).

## Implemented Models

The implemented density model is summarized in [pbli_density_models_table] and illustrated in
[pbli_density_models_figure].

!table id=pbli_density_models_table caption=Implemented PbLi density model.
| Enum | Expression used in TMAP8 | Property units | Validity range (K) | Reference | Notes |
| :- | :- | :- | :- | :- | :- |
| `LinearExpansion` | $\rho = 1.052\times10^{7}\,(1 - 1.13\times10^{-4}\, T)$ | g/m$^3$ | not documented | Source not yet verified | Linear temperature dependence, carried over from earlier drafts |

!media plot_pbli_review_models.py
       image_name=pbli_density_models.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=pbli_density_models_figure
       caption=Implemented PbLi density correlation from [pbli_density_models_table]. The model has no documented temperature range, so it is drawn over 500-1000 K for illustration.

!alert warning title=Unverified coefficients
The source of the coefficients of the `LinearExpansion` model, and its temperature range, have not
yet been verified against the primary literature. The model has no documented temperature range,
so `validity_action` never reports a temperature violation.

## Behavior when outside of range of validity

The [!param](/Materials/DensityPbLi/validity_action) parameter sets what TMAP8 does when a model is
evaluated at a temperature outside its documented validity range (`ignore`, `warning` or `error`;
see [TritiumDiffusivityPbLi](TritiumDiffusivityPbLi.md) for a description of each). Because the
`LinearExpansion` model has no documented range, the parameter currently has no effect.

!syntax parameters /Materials/DensityPbLi

!syntax inputs /Materials/DensityPbLi

!syntax children /Materials/DensityPbLi

!bibtex bibliography
