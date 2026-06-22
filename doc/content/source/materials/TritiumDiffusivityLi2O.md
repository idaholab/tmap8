# TritiumDiffusivityLi2O

!syntax description /Materials/TritiumDiffusivityLi2O

## Overview

`TritiumDiffusivityLi2O` provides literature-based tritium diffusivity correlations for Li2O and
publishes both a regular and an AD material property from the same object.

The class returns the diffusivity $D$ in m$^2$/s. The literature fits are implemented as reported
and stored in the implementation directly in m$^2$/s.
The [!param](/Materials/TritiumDiffusivityLi2O/model) parameter is required because the available
Li$_2$O correlations correspond to different irradiation states and microstructures.

!equation
D \; [m^2/s]

## Implemented Models

The implemented diffusivity models are summarized in [li2o_diffusivity_models_table] and
compared in [li2o_diffusivity_models_figure].

!table id=li2o_diffusivity_models_table caption=Implemented Li$_2$O tritium diffusivity models. All Arrhenius expressions use the ideal gas constant $R = 8.31446261815324$ J/mol/K, consistent with [PhysicalConstants](source/utils/TMAP8PhysicalConstants.md).
| Enum | Expression used in TMAP8 | Property units | Validity range (K) | Reference | Notes |
| :- | :- | :- | :- | :- | :- |
| `Ohira1989` | $D = 1.2 \times 10^{-11}\exp(-45.1\times10^3/RT)$ | m$^2$/s | 600-711 | [!cite](Ohira1989Li2O) | Tritium in unirradiated single-crystal Li2O |
| `Tanifuji1987` | $D = 1.16 \times 10^{-5}\exp(-101\times10^3/RT)$ | m$^2$/s | 573-950 | [!cite](Tanifuji1987Li2O) | Tritium release from neutron-irradiated Li2O single-crystal particles |
| `Kurasawa1991` | $D = 2.0 \times 10^{-7}\exp(-81.7\times10^3/RT)$ | m$^2$/s | 723.15-1093.15 | [!cite](Kurasawa1991Li2O) | In-situ tritium release interpretation for single-crystal Li2O |
| `Tanaka1988Grain` | $D_g = 1.27 \times 10^{-9}\exp(-54.9\times10^3/RT)$ | m$^2$/s | 633.15-873.15 | [!cite](Tanaka1988TTTExLi2O) | Grain diffusivity from TTTEx polycrystalline Li2O analysis |
| `Tanaka1988GrainBoundary` | $D_{int} = 1.61 \times 10^{-2}\exp(-95.1\times10^3/RT)$ | m$^2$/s | 633.15-873.15 | [!cite](Tanaka1988TTTExLi2O) | Grain-boundary diffusivity from TTTEx polycrystalline Li2O analysis |

The models are not interchangeable descriptions of the same specimen. They reflect different
combinations of:

- single crystal versus polycrystalline interpretation
- irradiated versus unirradiated conditions
- post-irradiation versus in-situ release interpretation
- grain versus grain-boundary meaning for the TTTEx-derived models

The [!param](/Materials/TritiumDiffusivityLi2O/validity_action) parameter controls how TMAP8
responds when a model is evaluated outside its documented temperature range. The supported actions
are `ignore`, `warning`, and `error`.

!media plot_li2o_review_models.py
       image_name=li2o_diffusivity_models.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=li2o_diffusivity_models_figure
       caption=Comparison of the implemented Li$_2$O tritium diffusivity correlations from [li2o_diffusivity_models_table], plotted as $\ln(D)$ versus $1000/T$ with $D$ expressed in m$^2$/s. The top axis shows the corresponding temperature in K.

!syntax parameters /Materials/TritiumDiffusivityLi2O

!syntax inputs /Materials/TritiumDiffusivityLi2O

!syntax children /Materials/TritiumDiffusivityLi2O

!bibtex bibliography
