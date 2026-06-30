# ADMatInterfaceReactionYHxPCT

!syntax description /InterfaceKernels/ADMatInterfaceReactionYHxPCT

## Description

The composition of metal hydrides like yttrium hydride ($YH_{x}$) is described by pressure-composition-temperature (PCT) data.
In TMAP8, the PCT curve can be imposed by an interface kernel that then dictates the material composition.
Hence, the `ADMatInterfaceReactionYHxPCT` interface kernel imposes the surface concentration of H in $YH_{x}$ based on the input pressure (Pa) and temperature (K). `ADMatInterfaceReactionYHxPCT` is related to [ADMatInterfaceReaction.md], but includes the $YH_{x}$ PCT curves.
 At the interface between a solid (main) and a gas (neighbor), it imposes:
\begin{equation} \label{eq:test_interfacereactionYHxPCT}
\frac{d C_s}{dt} = 0 = K_b f_{at}(T,P) \rho -  K_f C_s ,
\end{equation}
where $C_s$ is the surface H concentration in mol/m$^3$,
$K_b$ and $K_f$ are the backward and forward surface reaction rate in 1/s, respectively,
$f_{at}(T,P)$ is the composition in atomic fraction of H in $YH_{x}$ given a gas temperature $T$ and gas pressure $P$,
and $\rho$ is the yttrium molar density in mol/m$^3$.

[YHx_PCT_Data] shows the data used in this interface kernel. The experimental data originates from [!cite](Lundin_1962).


!media comparison_YHx_PCT.py
       image_name=YHx_PCT_Data.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=YHx_PCT_Data
       caption=PCT data for $YH_{x}$ sampled from [!cite](Lundin_1962).


To incorporate the entire PCT curve in TMAP8, the curve was divided into three regions: the low-pressure (LP) region, the plateau region (PR), and the high-pressure (HP) region. The fitting procedures and the modeling approach for each region are described below.

\begin{equation}\label{eq:atomic_fraction_HP}
f_{at,LP}(T,P) = f_{max,LP}(T)-10\left[1 \times 10^{-3}+\exp(-50.0 + 5.73 \times 10^{-2} T + ( 8.30 \times 10^{-1} - 2.69 \times 10^{-3} T) (\log\left(P_{lim}(T) - P \right)))\right]^{-1}
\end{equation}

\begin{equation}\label{eq:atomic_fraction_PR}
f_{at,PR}(T,P) = 1.33 - 2.18 \times 10^{-4}, T
\left( 10.6 - 4.35 \times 10^{-3}, T \right)
\log\left( \frac{P}{\gamma P_{\text{lim}}} \right)
\end{equation}

\begin{equation}\label{eq:atomic_fraction_LP}
f_{at,HP}(T,P) = 2.00-1.0015\left[f_{min,HP}(T)+\exp(24.89 - 2.53 \times 10^{-2} T + ( -3.98 \times 10^{-1} + 1.00 \times 10^{-3} T) (\log\left(P - P_{lim}(T)\right)))\right]^{-1}
\end{equation}

where $\gamma$ is a tolerance factor set to 1.15. While ${f_{max,LP}(T)}$ and ${f_{min,HP}(T)}$ represents maximum and miniumum atomic ratio per temperature in the low pressure and high high region, respectively. These formulas are expressed as:

\begin{equation}\label{eq:atomic_fraction_LP_Max}
f_{\text{Max},LP}(T)=1.01\times10^{-6}T^{2}-2.56\times10^{-3}T+2.16
\end{equation}

\begin{equation}\label{eq:atomic_fraction_HP_Min}
f_{\text{Min},HP}(T)=-1.01\times10^{-6}T^{2}+2.55\times10^{-3}T-5.61\times10^{-1}
\end{equation}

The plateau ($P_{lim}$) representing phase transition is captured as [!citep](Matthews2021SWIFT):
\begin{equation} \label{eq:pressure_plateau}
P_{lim} = \exp\left(-26.1+3.88 \times 10^{-2} T - 9.7 \times 10^{-6} T^2 \right),
\end{equation}

This fit is shown in [YHx_PCT_plateau_pressure_fit].

!media comparison_YHx_PCT.py
       image_name=YHx_PCT_plateau_pressure_fit.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=YHx_PCT_plateau_pressure_fit
       caption=Fit phase transition region as pressure as a function of temperature.

These fits are applied within the following conditional statement for entire PCT modelling capabilities

\begin{equation}
\text{If} \left (\frac{P}{P_{\text{lim}}}\right) > 1.15:
\quad f_{HP}(T,P)
\end{equation}

\begin{equation}
\text{Else-if} \left (\frac{P}{P_{\text{lim}}}\right) <1.05:
\quad f_{LP}(T,P)
\end{equation}

\begin{equation}
\text{Else: }
\quad f_{PR}(T,P)
\end{equation}

The validity of this present fit is between:
\begin{equation} \label{eq:bounds}
100 < P\,\text{[Pa]} < 10^{5}
\end{equation}


The ${f_{max,LP}(T)}$ and ${f_{min,HP}(T)}$ are quadratic fits that were verified by plotting the fit against the PCT data shown in the figure below. Evidently,the ${f_{min,HP}(T)}$ suffer slight losses due to non-symmetry of plateau region. Nonetheless, the fits are suitable for modelling purposes.

!media comparison_YHx_PCT.py
       image_name=YHx_PCT_Plateau_EndPoints_comparison.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=YHx_PCT_Plateau_EndPoints_comparison
       caption=Boundary of atomic ratio fit vs. PCT data from [!cite](Lundin_1962).


## Test

### Testing Individual Regions

[/YHx_PCT.i] tests the high and low pressure fits separately in TMAP8.
The domain contains two blocks: gas (left) and $YH_{x}$ (right) with an interface between the two blocks.
The diffusion is given by [!citep](MAJER2002438) and the surface reaction rate $K$ is taken from [!citep](FISHER19841536) ($K_f=K_b=K$).
To model the interface, the input file employs the [InterfaceDiffusion.md] object to model the flux of hydrogen at the surface, and `ADMatInterfaceReactionYHxPCT` to model the steady-state condition for the hydrogen concentration at the surface $C_s$ defined by:
\begin{equation} \label{eq:test_interfacereaction}
\frac{d C_s}{dt} = 0 = K (f_{at}(T,P) \rho - C_s),
\end{equation}


The results of the high pressure test for ($T$, $P$) = (1173.15 K, $1 \times 10^{3}$ Pa), (1173.15 K, $1 \times 10^{4}$ Pa), (1173.15 K, $5 \times 10^{4}$ Pa), and(1273.15 K, $3 \times 10^{3}$ Pa),
and the results for the the low pressure test for ($T$, $P$) =(1273.15 K, $3 \times 10^{2}$ Pa), (1473.15 K, $3 \times 10^{3}$ Pa), (1573.15 K, $6 \times 10^{2}$ Pa) and (1573.15 K, $6 \times 10^{2}$ Pa)


The [YHx_PCT_fit_2D] shows the indepedent low pressure and high pressure testing against the experimental data.As seen in the results, there are minor deviations, potentially due to rounding errors in the atomic‑fraction expression. Nonetheless, the errors remain below 1%, indicating that the fits are suitable for PCT modeling.


!media comparison_YHx_PCT.py
       image_name=YHx_PCT_fit_2D.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=YHx_PCT_fit_2D
       caption=PCT data for YHx from [!cite](Lundin_1962) with fits implemented in TMAP8, and test results.

### Overall PCT testing

For overall PCT capabilities [/YHx_PCT_Overall.i] tests the entire PCT modelling curves in TMAP8. The model follows the same structure as [/YHx_PCT.i], but has an arbitrarily high diffusion value to acheive steady-state quickly. The model also includes a linear pressure increase to cover the entire PCT curve.

\begin{equation}
P = P_{\text{initial}} + t \frac{P_{\text{max}} - P_{\text{initial}}}{t_{\text{end}}}
\end{equation}

The testing conditions include
($T$, $P_{initial}$) = (1173.15 K, $2 \times 10^{2}$ Pa),
(1223.15 K, $2 \times 10^{2}$ Pa),
(1273.15 K, $2 \times 10^{2}$ Pa),
(1323.15 K, $2 \times 10^{2}$ Pa),
(1373.15 K, $2 \times 10^{2}$ Pa),
(1423.15 K, $2 \times 10^{2}$ Pa),
(1473.15 K, $2 \times 10^{2}$ Pa),
(1523.15 K, $2 \times 10^{2}$ Pa),
and (1573.15 K, $2 \times 10^{2}$ Pa).

The [PCT_all_temperatures_experimental_vs_TMAP8_YHx] shows the PCT fit against the experimental data.Evidently, the fit exhibits moderate error, but the deviations remain within an acceptable range for modeling purposes.


!media comparison_YHx_PCT.py
       image_name=PCT_all_temperatures_experimental_vs_TMAP8_YHx.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=PCT_all_temperatures_experimental_vs_TMAP8_YHx
       caption=PCT data for YHx from [!cite](Lundin_1962) with fits implemented in TMAP8, and test results.


## Example Input File Syntax

!listing test/tests/yttrium_hydrogen_system/YHx_PCT.i block=InterfaceKernels/interface_reaction_YHx_PCT

!syntax parameters /InterfaceKernels/ADMatInterfaceReactionYHxPCT

!syntax inputs /InterfaceKernels/ADMatInterfaceReactionYHxPCT

!syntax children /InterfaceKernels/ADMatInterfaceReactionYHxPCT

