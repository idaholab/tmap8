# TritiumDiffusivityLi2O

!syntax description /Materials/TritiumDiffusivityLi2O

## Overview

`TritiumDiffusivityLi2O` computes the diffusivity $D$ of tritium in Li$_2$O. This 
diffusivity is presented as both a regular Real- and AD-Real-valued material property 
for use in a variety of simulation configurations. The property fits are implemented as 
published in the literature and stored in the implementation directly in units of m$^2$/s. 
To select the model of diffusivity to use, the [!param](/Materials/TritiumDiffusivityLi2O/model) 
parameter **must** be provided, as the available Li$_2$O correlations correspond to 
different irradiation states and microstructures.

## Implemented Models

The implemented diffusivity models are summarized in [li2o_diffusivity_models_table] and
plotted in [li2o_diffusivity_models_figure].

!table id=li2o_diffusivity_models_table caption=Implemented Li$_2$O tritium diffusivity models. All Arrhenius expressions use the ideal gas constant value from [PhysicalConstants](source/utils/TMAP8PhysicalConstants.md).
| Enum | Expression used in TMAP8 | Property units | Validity range (K) | Reference | Notes |
| :- | :- | :- | :- | :- | :- |
| `Ohira1989` | $D = 1.2 \times 10^{-11}\exp(-45.1\times10^3/RT)$ | m$^2$/s | 600-711 | [!cite](Ohira1989Li2O) | Tritium in unirradiated single-crystal Li$_2$O |
| `Tanifuji1987` | $D = 1.16 \times 10^{-5}\exp(-101\times10^3/RT)$ | m$^2$/s | 573-950 | [!cite](Tanifuji1987Li2O) | Tritium release from neutron-irradiated Li$_2$O single-crystal particles |
| `Kurasawa1991` | $D = 2.0 \times 10^{-7}\exp(-81.7\times10^3/RT)$ | m$^2$/s | 723.15-1093.15 | [!cite](Kurasawa1991Li2O) | In-situ tritium release interpretation for single-crystal Li$_2$O |
| `Terai1988Grain` | $D_g = 1.27 \times 10^{-9}\exp(-54.9\times10^3/RT)$ | m$^2$/s | 633.15-873.15 | [!cite](Terai1988TTTExLi2O) | Grain diffusivity from TTTEx polycrystalline Li$_2$O analysis under $\Phi = 10^{8} n/cm$^2$/s irradiation |
| `Terai1988GrainBoundary` | $D_{int} = 1.61 \times 10^{-2}\exp(-95.1\times10^3/RT)$ | m$^2$/s | 633.15-873.15 | [!cite](Terai1988TTTExLi2O) | Grain-boundary diffusivity from TTTEx polycrystalline Li$_2$O analysis under $\Phi = 10^{8} n/cm$^2$/s irradiation |

Note that the models are not interchangeable descriptions of the same specimen.
They reflect different combinations of material microstructures and irradiation damage.

The [!param](/Materials/TritiumDiffusivityLi2O/validity_action) parameter controls how TMAP8
responds when a model is evaluated outside its documented temperature range.

!media plot_li2o_review_models.py
       image_name=li2o_diffusivity_models.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=li2o_diffusivity_models_figure
       caption=Comparison of the implemented Li$_2$O tritium diffusivity correlations from [li2o_diffusivity_models_table].

!syntax parameters /Materials/TritiumDiffusivityLi2O

!syntax inputs /Materials/TritiumDiffusivityLi2O

!syntax children /Materials/TritiumDiffusivityLi2O

!bibtex bibliography
