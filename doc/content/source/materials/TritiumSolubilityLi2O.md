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
K_s = K_0(T) \exp\left(-\frac{E_a}{RT}\right),

where $K_0(T)$ is the pre-exponential factor in atoms m$^{-3}$ Pa$^{-1/2}$, which depends weakly on
temperature through the thermal expansion of Li$_2$O as described below, $E_a$ is the activation
energy in J/mol, $R$ is the ideal gas constant (its value is provided by
[PhysicalConstants](source/utils/TMAP8PhysicalConstants.md)), and $T$ is the temperature in K.

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
| `Ohira1989Tritium` | $K_{s,T} = N_{at}(T)\, 2.28 \times 10^{-4}\exp(-24.70\times10^3/RT)$ | atoms m$^{-3}$ Pa$^{-1/2}$ | 583-963 K | [!cite](Ohira1989Li2O) | Reduced-species tritium dissolution in single-crystal Li$_2$O |
| `Ohira1989Hydrogen` | $K_{s,H} = N_{at}(T)\, 1.47 \times 10^{-5}\exp(-24.33\times10^3/RT)$ | atoms m$^{-3}$ Pa$^{-1/2}$ | 476-963 K | [!cite](Ohira1989Li2O) | Reduced-species hydrogen dissolution in single-crystal Li$_2$O |

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
$C = N_{at}(T) X$, where $N_{at}(T)$ is the temperature-dependent number density of all lattice atoms (Li and O). The number 101325
is the definition of one standard atmosphere in pascals: 1 atm = 101325 Pa exactly (available as
`atm_to_Pa` in [PhysicalConstants](source/utils/TMAP8PhysicalConstants.md)). The pressures in [!cite](Ohira1989Li2O) are in atm and TMAP8 uses
Pa, so $P_{atm} = P_{Pa}/101325$, where $P = P_{Pa}$ is the pressure in Pa. Therefore,

!equation
C = K_s \sqrt{P},
\qquad
K_s = N_{at}(T)\, X_0 \exp\left(-\frac{E_a}{RT}\right),
\qquad
X_0 = \frac{10^{-b}}{\sqrt{101325}},
\qquad
E_a = a R \ln(10),

with $C$ in atoms/m$^3$, $P$ in Pa, $K_s$ in atoms m$^{-3}$ Pa$^{-1/2}$, $X_0$ in Pa$^{-1/2}$, and
$E_a$ in J/mol. This gives $X_0 = 1.47 \times 10^{-5}$ Pa$^{-1/2}$ and $E_a = 24.33$ kJ/mol for
hydrogen, and $X_0 = 2.28 \times 10^{-4}$ Pa$^{-1/2}$ and $E_a = 24.70$ kJ/mol for tritium.
Because the paper's constant is inverted, its positive $1/T$ slope
means that the solubility *increases* with temperature, and $E_a$ is positive in
$\exp(-E_a/RT)$. These activation energies agree with the heats of dissolution measured in
[!cite](Ohira1989Li2O), $24.3 \pm 0.9$ kJ/mol for hydrogen and $25.3 \pm 1.2$ kJ/mol for tritium.

The atom density is $N_{at}(T) = 12 / a_0(T)^3$. It follows from the anti-fluorite structure of
Li$_2$O (space group Fm$\bar{3}$m) [!citep](Zintl1934Li2O), which has 4 formula units (12 atoms) per
cubic unit cell. The lattice parameter $a_0(T)$ is a weighted linear least-squares fit, using the
quoted uncertainties as weights, to the temperature-dependent lattice constants of Table I of
[!cite](Farley1991Li2O) (293-1603 K):

!equation
a_0(T) = 4.55224 \times 10^{-10} + 1.69514 \times 10^{-14}\, T,

with $a_0$ in m and $T$ in K.
The fit reproduces the tabulated values with a root-mean-square
deviation of 0.01 Å (0.2%), and corresponds to a linear thermal expansion coefficient of about
$3.6 \times 10^{-5}$ K$^{-1}$ near 700 K.
Because of this large thermal expansion, $N_{at}$ decreases by about 5% between 476 K
($1.207 \times 10^{29}$ atoms/m$^3$) and 963 K
($1.145 \times 10^{29}$ atoms/m$^3$), the validity range of [!cite](Ohira1989Li2O).
Using a temperature-dependent $N_{at}$ makes the solubility prefactor weakly temperature dependent,
so the effective activation energy of $K_s$ differs slightly from $E_a$.
At 293 K, the fit gives $a_0 = 4.602$ Å, equivalent to a density of 2.036 g/cm$^3$ with a molar
mass of 29.88 g/mol, which is 1.1% above the theoretical density of 2.013 g/cm$^3$ tabulated in
[!cite](Johnson1988CeramicBreeders).
The temperature dependence of $N_{at}$ was not applied in [!cite](Ohira1989Li2O) and is a modeling choice made in TMAP8.
In the implementation, the coefficients $a$ and $b$ of the paper, the coefficients of $a_0(T)$,
and the number of atoms per unit cell are kept as named constants, and $X_0$ and $E_a$ are derived
from them in the code.

!syntax parameters /Materials/TritiumSolubilityLi2O

!syntax inputs /Materials/TritiumSolubilityLi2O

!syntax children /Materials/TritiumSolubilityLi2O

!bibtex bibliography
