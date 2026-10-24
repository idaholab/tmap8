# TritiumSolubilityLi2O

!syntax description /Materials/TritiumSolubilityLi2O

## Overview

`TritiumSolubilityLi2O` provides reduced-species hydrogen isotope solubility $K_s$ for 
Li$_2$O, derived from multiple available sources in the literature. For convenience and 
use in a variety of simulation configurations, this class creates both a Real- and AD-Real-valued 
material property from the same Material object. The current implementation targets reduced 
gas-species hydrogen isotope dissolution behavior represented with a Sieverts-law type 
coefficient,

!equation
C = K_s P^{1/2},

where $C$ is the concentration of hydrogen isotope in Li$_2$O in atoms/m$^3$, $P$ is the partial
pressure of the gas in Pa, and $K_s$ is the solubility in atoms m$^{-3}$ Pa$^{-1/2}$ provided by
the selected literature model. It has the Arrhenius form

!equation
K_s = K_0 \exp\left(-\frac{E_a}{RT}\right),

where $K_0$ is the pre-exponential factor in atoms m$^{-3}$ Pa$^{-1/2}$, $E_a$ is the activation
energy in J/mol, $R$ is the ideal gas constant, and $T$ is the temperature in K.

## Modeling Scope

The Li$_2$O literature does not currently support treating all reported chemistry as one scalar solubility model.

Two regimes need to stay distinct:

1. Reduced-species hydrogen isotope dissolution and transport.
   This is the regime targeted by this implementation of `TritiumSolubilityLi2O`.

2. Oxidized LiOH/LiOT solution chemistry.
   This regime matters for inventory and release at higher hydrogen isotope content, but it is not implemented here.

## Implemented Models

The implemented solubility model is summarized in [li2o_solubility_models_table] and plotted in
[li2o_solubility_models_figure].

!table id=li2o_solubility_models_table caption=Implemented Li$_2$O reduced-species hydrogen isotope solubility models, converted from the correlations of [!cite](Ohira1989Li2O) as described below. The models use the ideal gas constant provided by [PhysicalConstants](source/utils/TMAP8PhysicalConstants.md).
| Enum | Expression used in TMAP8 | Property units | Validity range (K) | Reference | Notes |
| :- | :- | :- | :- | :- | :- |
| `Ohira1989Tritium` | $K_{s,T} = 2.77 \times 10^{25}\exp(-24.70\times10^3/RT)$ | atoms m$^{-3}$ Pa$^{-1/2}$ | 583-963 K | [!cite](Ohira1989Li2O) | Reduced-species tritium dissolution in single-crystal Li$_2$O |
| `Ohira1989Hydrogen` | $K_{s,H} = 1.79 \times 10^{24}\exp(-24.33\times10^3/RT)$ | atoms m$^{-3}$ Pa$^{-1/2}$ | 476-963 K | [!cite](Ohira1989Li2O) | Reduced-species hydrogen dissolution in single-crystal Li$_2$O |

### Conversion of the O'Hira et al. correlations

The correlations of [!cite](Ohira1989Li2O) are not reported in the form needed by TMAP8, and have
been converted. The paper defines the Sieverts' constant as

!equation
K = \frac{\sqrt{P_{atm}}}{X},

where $P_{atm}$ is the gas pressure in atm and $X = n_{H} / (n_{Li} + n_{O} + n_{H})$ is the atom
fraction of hydrogen isotope in the solid. It is therefore the *inverse* of a solubility, expressed
per total lattice atom and for a pressure in atm. The reported fits are

!equation
\log_{10} K = \frac{a}{T} + b,

with $K$ in atm$^{1/2}$ and $T$ in K, where $a = 1271 \pm 46$ K and $b = 2.33 \pm 0.07$ for hydrogen
(476-963 K), and $a = 1290 \pm 81$ K and $b = 1.14 \pm 0.11$ for tritium (583-963 K). Inverting the
definition of $K$ gives $X = 10^{-b}\,10^{-a/T}\sqrt{P_{atm}}$. The volumetric concentration is
$C = N_{at} X$, where $N_{at}$ is the number density of all lattice atoms (Li and O), and
$P_{atm} = P / 101325$ with $P$ in Pa. Therefore,

!equation
C = K_s \sqrt{P},
\qquad
K_s = K_0 \exp\left(-\frac{E_a}{RT}\right),
\qquad
K_0 = \frac{N_{at}\, 10^{-b}}{\sqrt{101325}},
\qquad
E_a = a R \ln(10),

with $C$ in atoms/m$^3$, $P$ in Pa, $K_s$ in atoms m$^{-3}$ Pa$^{-1/2}$, $K_0$ in atoms m$^{-3}$
Pa$^{-1/2}$, and $E_a$ in J/mol. This gives $K_0 = 1.79 \times 10^{24}$ atoms m$^{-3}$ Pa$^{-1/2}$
and $E_a = 24.33$ kJ/mol for hydrogen, and $K_0 = 2.77 \times 10^{25}$ atoms m$^{-3}$ Pa$^{-1/2}$ and
$E_a = 24.70$ kJ/mol for tritium. Because the paper's constant is inverted, its positive $1/T$ slope
means that the solubility *increases* with temperature, and $E_a$ is positive in
$\exp(-E_a/RT)$. These activation energies agree with the heats of dissolution measured in
[!cite](Ohira1989Li2O), $24.3 \pm 0.9$ kJ/mol for hydrogen and $25.3 \pm 1.2$ kJ/mol for tritium.

The atom density is $N_{at} = 12 / a_0^3 = 1.218 \times 10^{29}$ atoms/m$^3$. It follows from the
anti-fluorite structure of Li$_2$O, which has 4 formula units (12 atoms) per cubic unit cell of
lattice parameter $a_0 = 4.619 \times 10^{-10}$ m. This is equivalent to a density of 2.013 g/cm$^3$
with a molar mass of 29.88 g/mol (agreement to 0.05%). In the implementation, the coefficients $a$
and $b$ of the paper, $a_0$, and the number of atoms per unit cell are kept as named constants, and
$K_0$ and $E_a$ are derived from them in the code.

!alert warning title=Inconsistency in temperature range for `Ohira1989Hydrogen` in [!cite](Ohira1989Li2O). 
In [!cite](Ohira1989Li2O), the text above Eq. (3) states that the upper temperature of the range of validity of the hydrogen solubility is 596 K, but Fig. (3) of the same paper shows values up to approximately 963 K (as for tritium). In this implementation, we therefore use the value from the figure (i.e., 963 K) and assume that the upper limit in the text is a typo. 

!media plot_li2o_review_models.py
       image_name=li2o_solubility_models.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=li2o_solubility_models_figure
       caption=Comparison of the implemented Li$_2$O hydrogen isotope solubility correlations from [li2o_solubility_models_table].

The broader Li$_2$O solubility literature also includes H/D reduced-species measurements
from [!cite](Katsuta1983Li2O) and oxidized LiOH-in-Li$_2$O solution chemistry from
[!cite](Tetenbaum1985LiOHInLi2O), but those models are not implemented here yet.

The [!param](/Materials/TritiumSolubilityLi2O/validity_action) parameter sets what TMAP8 does when a model is evaluated
at a temperature outside its documented validity range (the ranges are listed in
[li2o_solubility_models_table]):

- `ignore`: nothing happens and the model is silently extrapolated.
- `warning` (default): the simulation continues. Each out-of-range evaluation is recorded in MOOSE's
  solution-invalidity system and summarized in the "Warnings History" table printed at the end of
  the run, with the number of occurrences per time step. Set
  [!param](/Problem/FEProblem/immediately_print_invalid_solution) to print them as they occur.
- `error`: the run stops immediately with a message giving the model, the offending temperature
  and the documented range.

Extrapolating a correlation beyond the conditions it was fit to can give unphysical values, so
`warning` or `error` is recommended unless the extrapolation is intentional.

!syntax parameters /Materials/TritiumSolubilityLi2O

!syntax inputs /Materials/TritiumSolubilityLi2O

!syntax children /Materials/TritiumSolubilityLi2O

!bibtex bibliography
