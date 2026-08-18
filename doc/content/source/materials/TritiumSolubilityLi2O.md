# TritiumSolubilityLi2O

!syntax description /Materials/TritiumSolubilityLi2O

## Overview

`TritiumSolubilityLi2O` provides reduced-species hydrogen isotope solubility models for Li2O and creates
both a regular and an AD Real-valued material property from the same Material object.

The current implementation targets reduced gas-species hydrogen isotope dissolution behavior represented
with a Sieverts-law type coefficient,

!equation
C = K_s P^{1/2},

where $K_s$ is provided by the selected literature model.

## Modeling Scope

The Li2O literature does not currently support treating all reported chemistry as one scalar solubility model.

Two regimes need to stay distinct:

1. Reduced-species hydrogen isotope dissolution and transport.
   This is the regime targeted by this implementation of `TritiumSolubilityLi2O`.

2. Oxidized LiOH/LiOT solution chemistry.
   This regime matters for inventory and release at higher hydrogen isotope content, but it is not implemented here.

## Implemented Models

The implemented solubility model is summarized in [li2o_solubility_models_table] and plotted in
[li2o_solubility_models_figure].

!table id=li2o_solubility_models_table caption=Implemented Li$_2$O reduced-species hydrogen isotope solubility model. The implemented model uses the ideal gas constant provided by [PhysicalConstants](source/utils/TMAP8PhysicalConstants.md).
| Enum | Expression used in TMAP8 | Property units | Validity range (K) | Reference | Notes |
| :- | :- | :- | :- | :- | :- |
| `Ohira1989Tritium` | $K_{s,T} = \exp(1290/T + 1.14)$ | atm$^{1/2}$ | 583-963 K | [!cite](Ohira1989Li2O) | Reduced-species tritium dissolution in single-crystal Li2O |
| `Ohira1989Hydrogen` | $K_{s,T} = \exp(1271/T + 2.33)$ | atm$^{1/2}$ | 476-963 K | [!cite](Ohira1989Li2O) | Reduced-species hydrogen dissolution in single-crystal Li2O |
!alert warning title=Inconsistency in temperature range for `Ohira1989Hydrogen` in [!cite](Ohira1989Li2O). 
In [!cite](Ohira1989Li2O), the test above Eq. (3) states that the upper temperature of the range of validity of the hydrogen solubility is 596 K, but Fig. (3) of the same paper shows values up to around 963 K (as for tritium). In this implementation, we therefore use the value from the figure (i.e., 963 K) and assume that the upper limit in the text is a typo. 
!media plot_li2o_review_models.py
       image_name=li2o_solubility_models.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=li2o_solubility_models_figure
       caption=Comparison of the implemented Li$_2$O hydrogen isotope solubility correlations from [li2o_solubility_models_table].

The broader Li$_2$O solubility literature also includes H/D reduced-species measurements
from [!cite](Katsuta1983Li2O) and oxidized LiOH-in-Li$_2$O solution chemistry from
[!cite](Tetenbaum1985LiOHInLi2O), but those models are not implemented here yet.

The [!param](/Materials/TritiumSolubilityLi2O/validity_action) parameter controls how TMAP8
responds when a model is evaluated outside its documented temperature range.

!syntax parameters /Materials/TritiumSolubilityLi2O

!syntax inputs /Materials/TritiumSolubilityLi2O

!syntax children /Materials/TritiumSolubilityLi2O

!bibtex bibliography
