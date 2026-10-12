# ADMatInterfaceReactionYHxPCT

!syntax description /InterfaceKernels/ADMatInterfaceReactionYHxPCT

## Description

The composition of metal hydrides like yttrium hydride (YH$_{x}$) is described by pressure-composition-temperature (PCT) data.
In TMAP8, the PCT curve can be imposed by an interface kernel that then dictates the material composition.
Hence, the `ADMatInterfaceReactionYHxPCT` interface kernel imposes the surface concentration of H in YH$_{x}$ based on the input pressure (Pa) and temperature (K). `ADMatInterfaceReactionYHxPCT` is related to [ADMatInterfaceReaction.md], but includes the YH$_{x}$ PCT curves.
At the interface between a solid (main) and a gas (neighbor), it imposes:
\begin{equation} \label{eq:test_interfacereactionYHxPCT}
\frac{d C_s}{dt} = 0 = K_b f_{at}(T,P) \rho -  K_f C_s,
\end{equation}
where $C_s$ is the surface H concentration in mol/m$^3$,
$K_b$ and $K_f$ are the backward and forward surface reaction rate in 1/s, respectively,
$f_{at}(T,P)$ is the composition in atomic fraction of H in YH$_{x}$ given a gas temperature $T$ and gas pressure $P$,
and $\rho$ is the yttrium molar density in mol/m$^3$.

[YHx_PCT_fit_2D] shows the data used in this interface kernel along with TMAP8 simulation results and analytical fits. The experimental data originates from [!cite](Lundin_1962).

!media comparison_YHx_PCT.py
       image_name=YHx_PCT_fit_2D.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=YHx_PCT_fit_2D
       caption=PCT data for YH$_{x}$ sampled from [!cite](Lundin_1962) with TMAP8 simulation results and analytical fits.

To incorporate the entire PCT curve in TMAP8, the curve is divided into three regimes: an α-phase, low-pressure (α) regime; a β-phase, high-pressure (β) regime; and a bi-phasic bridging regime that smoothly connects the two. Rather than switching sharply between fits at a single threshold pressure, the three regimes are combined using a continuous, smoothly-blended weighting scheme so that $f_{at}(T,P)$ and its derivatives vary smoothly across the entire pressure range. The fitting procedures and the blending approach for each region are described below.

### Low-pressure (α) regime

The low-pressure regime uses a generalized power-law fit in which both the exponent and the prefactor vary smoothly (cubically) with temperature:

\begin{equation}\label{eq:atomic_fraction_α}
f_{at,α}(T,P) = \exp\left(e(T)\right)\,P^{\,n(T)},
\end{equation}

with

\begin{equation}\label{eq:n_T}
n(T) = 11.01651 - 2.676499\times10^{-2}\,T + 2.164250\times10^{-5}\,T^{2} - 5.666033\times10^{-9}\,T^{3},
\end{equation}

\begin{equation}\label{eq:e_T}
e(T) = -122.0936 + 2.927460\times10^{-1}\,T - 2.318920\times10^{-4}\,T^{2} + 5.922527\times10^{-8}\,T^{3}.
\end{equation}

### High-pressure (β) regime

The high-pressure regime retains the original hydride-plateau fit:

\begin{equation}\label{eq:atomic_fraction_β}
f_{at,β}(T,P) = 2.00-1.0015\left[f_{at,min,β}(T)+\exp\left(24.89 - 2.53 \times 10^{-2} T + \left( -3.98 \times 10^{-1} + 1.00 \times 10^{-3} T \right) \log\left(P - P_{lim}(T)\right)\right)\right]^{-1},
\end{equation}

where $f_{at,min,β}(T)$ represents the minimum atomic ratio in the high-pressure regime, expressed as:

\begin{equation}\label{eq:atomic_fraction_β_Min}
f_{at,min,β}(T)=-1.01\times10^{-6}T^{2}+2.55\times10^{-3}T-5.60\times10^{-1}.
\end{equation}

The plateau ($P_{lim}$) representing the phase transition is captured as [!citep](Matthews2021SWIFT):

\begin{equation} \label{eq:pressure_plateau}
P_{lim}(T) = \exp\left(-26.1+3.88 \times 10^{-2} T - 9.7 \times 10^{-6} T^2 \right).
\end{equation}

This fit is shown in [YHx_PCT_plateau_pressure_fit].

!media comparison_YHx_PCT.py
       image_name=YHx_PCT_plateau_pressure_fit.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=YHx_PCT_plateau_pressure_fit
       caption=Fit phase transition region as pressure as a function of temperature.

### Bi-phasic (α+β) bridging regime

Instead of an independently-fitted plateau expression, the bridging regime is constructed to be a log-linear function of pressure that is continuous with the low-pressure regime at $P=\delta P_{lim}(T)$ and with the high-pressure regime at $P=\zeta P_{lim}(T)$:

\begin{equation}\label{eq:m0_definition}
m_{0} = f_{at,α}(T,\delta P_{lim}) - \frac{f_{at,β}(T,\zeta P{lim}) - f_{at,α}(T,\delta P{lim})}{L_{b} - L_{a}} L_{a},
\end{equation}
and
\begin{equation}\label{eq:m1_definition}
m_{1} = \frac{f_{at,β}(T,\zeta P_{lim}) - f_{at,α}(T,\delta P{lim})}{L_{b} - L_{a}},
\end{equation}
with
\begin{equation}
\label{eq:log_bounds}
L_{a} = \ln(\delta P_{lim}), \qquad
L_{b} = \ln(\zeta P_{lim}),
\end{equation}

with $\delta = 0.96$ and $\zeta = 1.13$ marking, respectively, the low- and high-pressure edges (relative to $P_{lim}$) of the bridging regime.

### Smooth blending

The three regime values $f_{at,α}$, $f_{at,α+β}$, and $f_{at,β}$ are combined using smooth (logistic) weight functions of the log-pressure ratio, rather than a hard switch, so that the composite atomic fraction transitions continuously from one regime to the next:

\begin{equation}\label{eq:blend_x}
x = \ln\!\left(\frac{P}{P_{lim}(T)}\right), \qquad x_\delta = \ln(\delta), \qquad x_\zeta = \ln(\zeta),
\end{equation}

\begin{equation}\label{eq:blend_sigmoids}
s_{α→α+β}(x)= \left[1+\exp\!\left(-\frac{x-x_\delta}{\Delta_{\delta}}\right)\right]^{-1}, \qquad
s_{α+β→β}(x) = \left[1+\exp\!\left(-\frac{x-x_\zeta}{\Delta_{\zeta}}\right)\right]^{-1},
\end{equation}

where $\Delta_{\zeta}= \Delta_{\delta}= 0.02$ is the blending width, controlling how rapidly each transition occurs (typical values range 0.02-0.12). The (unnormalized) regime weights are then:

\begin{equation}\label{eq:blend_weights}
w_{α} = \frac{1-s_{α→α+β}(x)}{W}, \qquad w_{α+β} = \frac{s_{α→α+β}(x)\left(1-s_{α+β→β}(x)\right)}{W}, \qquad w_{β} = \frac{s_{α+β→β}(x)}{W},
\end{equation}

and are renormalized so that $w_{α}+w_{α+β}+w_{β}=1$ at every point. The final atomic fraction used by the kernel is the corresponding weighted sum:

\begin{equation}\label{eq:blend_total}
f_{at}(T,P) = w_{α}\,f_{at,α}(T,P) + w_{α+β}\,f_{at,α+β}(T,P) + w_{β}\,f_{at,β}(T,P).
\end{equation}

Because $f_{at,α+β}$ is constructed to agree exactly with $f_{at,α}$ at $P=\delta P_{lim}(T)$ and with $f_{at,β}$ at $P=\zeta P_{lim}(T)$, and because the sigmoid weights vary smoothly through these same points, $f_{at}(T,P)$ transitions continuously across the full PCT curve without the discontinuities that a hard-switched piecewise definition would introduce.

The validity of this present fit is between:

\begin{equation} \label{eq:bounds}
100 < P\,\text{[Pa]} < 10^{5}.
\end{equation}

$f_{at,min,β}(T)$ is a quadratic fit that was verified by plotting it against the PCT data, shown in the figure below. It suffers slight losses due to the non-symmetry of the plateau regime, but remains suitable for modeling purposes. Unlike the previous formulation, the low-pressure regime is no longer bounded by an independent quadratic maximum-atomic-ratio fit; the smooth blend into the bi-phasic bridge naturally constrains its usable range.

!media comparison_YHx_PCT.py
       image_name=YHx_PCT_Plateau_EndPoints_comparison.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=YHx_PCT_Plateau_EndPoints_comparison
       caption=Boundary of atomic ratio fit vs. PCT data from [!cite](Lundin_1962).

## Test

[!file](/YHx_PCT.i) tests the implantation of the YHx PCT curves in TMAP8.
The domain contains two blocks: gas (left) and YHx (right) with an interface between the two blocks.
The diffusion is given by [!citep](MAJER2002438) and the surface reaction rate $K$ is taken from [!citep](FISHER19841536) ($K_f=K_b=K$).
To model the interface, the input file employs the [InterfaceDiffusion.md] object to model the flux of hydrogen at the surface, and `ADMatInterfaceReactionYHxPCT` to model the steady-state condition for the hydrogen concentration at the surface $C_s$ defined by:

\begin{equation} \label{eq:test_interfacereaction}
\frac{d C_s}{dt} = 0 = K (f_{at}(T,P) \rho - C_s),
\end{equation}

The results of the high pressure test for ($T$, $P$) = (1173.15 K, $1 \times 10^{3}$ Pa), (1173.15 K, $1 \times 10^{4}$ Pa), (1173.15 K, $5 \times 10^{4}$ Pa), and (1273.15 K, $3 \times 10^{3}$ Pa),
and the results for the low pressure test for ($T$, $P$) = (1273.15 K, $3 \times 10^{2}$ Pa), (1473.15 K, $3 \times 10^{3}$ Pa), (1573.15 K, $6 \times 10^{2}$ Pa) and (1573.15 K, $5 \times 10^{3}$ Pa).

The [YHx_PCT_fit_2D] figure compares the analytical fits, the independent low-pressure model, and the independent high-pressure model against the experimental data. Overall, the analytical fits show reasonable agreement with the measurements; the root-mean-square errors for the low- and high-pressure regimees, per temperature, are reported directly in the legend of [YHx_PCT_fit_2D] and printed by `comparison_YHx_PCT.py`. The independent low- and high-pressure TMAP8 simulations align well with the analytical trends, demonstrating consistency between the analytical approach and the model-based predictions.

### Overall PCT testing

[!file](/YHx_PCT.i) also tests the entire PCT modelling curve, including the smooth bi-phasic blending across the α, bridging, and β regimes, in TMAP8. The simulation follows the same structure as before, but has an arbitrarily high diffusion value to achieve steady-state quickly. The model also includes a linear pressure increase to cover the entire PCT curve:

\begin{equation}
P = P_{\text{initial}} + t \frac{P_{\text{max}} - P_{\text{initial}}}{t_{\text{end}}}.
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

The [YHx_PCT_fit_2D] shows the PCT fit against the experimental data over the full sweep, including through the smoothly-blended bridging region. The fit exhibits moderate error, with the mean absolute percentage error per temperature reported in the legend of [YHx_PCT_fit_2D] and printed by `comparison_YHx_PCT.py`; the deviations remain within an acceptable range for modeling purposes.

## Example Input File Syntax

!listing test/tests/yttrium_hydrogen_system/YHx_PCT.i block=InterfaceKernels/interface_reaction_YHx_PCT

!syntax parameters /InterfaceKernels/ADMatInterfaceReactionYHxPCT

!syntax inputs /InterfaceKernels/ADMatInterfaceReactionYHxPCT

!syntax children /InterfaceKernels/ADMatInterfaceReactionYHxPCT