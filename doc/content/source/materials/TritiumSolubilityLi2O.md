# TritiumSolubilityLi2O

!syntax description /Materials/TritiumSolubilityLi2O

## Overview

`TritiumSolubilityLi2O` provides reduced-species tritium solubility models for Li2O and publishes
both a regular and an AD material property from the same object.

The current implementation targets reduced gas-species tritium dissolution behavior represented
with a Sieverts-law type coefficient,

!equation
C = K_s P^{1/2},

where the exact normalization of $K_s$ follows the source-reported coefficient form currently
implemented in TMAP8.

## Modeling Scope

The Li2O literature does not currently support treating all reported chemistry as one scalar solubility model.

Two regimes need to stay distinct:

1. Reduced-species tritium dissolution and transport.
   This is the regime targeted by version 1 of `TritiumSolubilityLi2O`.

2. Oxidized LiOH/LiOT solution chemistry.
   This regime matters for inventory and release, but it is not yet represented here as a source-backed direct scalar property.

## Implemented Models

The implemented solubility model is summarized in [li2o_solubility_models_table] and plotted in
[li2o_solubility_models_figure].

!table id=li2o_solubility_models_table caption=Implemented Li$_2$O reduced-species tritium solubility model. The reported coefficient form uses the ideal gas constant $R = 8.31446261815324$ J/mol/K where needed for comparison with Arrhenius transport relations, consistent with [PhysicalConstants](source/utils/TMAP8PhysicalConstants.md).
| Enum | Expression used in TMAP8 | Property units | Validity range (K) | Reference | Notes |
| :- | :- | :- | :- | :- | :- |
| `Ohira1989` | $\log_{10}(K_{s,T}) = 1290/T + 1.14$ | Source-reported $K_s$ units, pending direct PDF confirmation | Exact fit range still needs direct PDF confirmation | [!cite](Ohira1989Li2O) | Reduced-species tritium dissolution in single-crystal Li2O |

## Validity Notes

The O'Hira source provides a source-backed tritium coefficient, but the accessible snippet remains
ambiguous enough in the unit formatting that the implementation should still be checked against the
primary paper for:

- the exact definition of $K_s$
- the exact pressure basis
- the exact temperature range attached to the fit

The current implementation does not apply a hard temperature-limit check for `Ohira1989` because
the exact fit range still needs direct primary-source confirmation. The
[!param](/Materials/TritiumSolubilityLi2O/validity_action) parameter still supports `ignore`,
`warning`, and `error`, but there is currently no numeric range to enforce for this model.

!media plot_li2o_review_models.py
       image_name=li2o_solubility_review.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=li2o_solubility_models_figure
       caption=Plot of the implemented `Ohira1989` reduced-species tritium solubility coefficient from [li2o_solubility_models_table] as $\ln(K_s)$ versus $1000/T$. The top axis shows the corresponding temperature in K. The y-axis still reflects the source-reported coefficient form pending final primary-paper unit normalization.

The broader Li$_2$O solubility literature also includes H/D reduced-species measurements
from [!cite](Katsuta1983Li2O) and oxidized LiOH-in-Li$_2$O solution chemistry from
[!cite](Tetenbaum1985LiOHInLi2O), but those models are not implemented here.

!syntax parameters /Materials/TritiumSolubilityLi2O

!syntax inputs /Materials/TritiumSolubilityLi2O

!syntax children /Materials/TritiumSolubilityLi2O

!bibtex bibliography
