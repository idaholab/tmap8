# ADMatInterfaceReactionZrCoHxPCT

!syntax description /InterfaceKernels/ADMatInterfaceReactionZrCoHxPCT

## Description

The composition of metal hydrides like zirconium-cobalt hydride (ZrCoH$_{x}$) is described by pressure-composition-temperature (PCT) data.
In TMAP8, the PCT curve can be imposed by an interface kernel that then dictates the material composition.
Hence, the `ADMatInterfaceReactionZrCoHxPCT` interface kernel imposes the surface concentration of H in ZrCoH$_{x}$ based on the input pressure (Pa) and temperature (K). `ADMatInterfaceReactionZrCoHxPCT` is related to [ADMatInterfaceReaction.md], but includes the ZrCoH$_{x}$ PCT curves.
At the interface between a solid (main) and a gas (neighbor), it imposes:
\begin{equation} \label{eq:test_interfacereactionZrCoHx}
\frac{d C_s}{dt} = 0 = K_b f_{at}(T,P) \rho -  K_f C_s,
\end{equation}
where $C_s$ is the surface H concentration in mol/m$^3$,
$K_b$ and $K_f$ are the backward and forward surface reaction rate in 1/s, respectively,
$f_{at}(T,P)$ is the composition in atomic fraction of H in ZrCoH$_{x}$ given a gas temperature $T$ and gas pressure $P$,
and $\rho$ is the zirconium-cobalt molar density in mol/m$^3$.

[ZrCoHx_PCT_combined] shows the experimental data, fitted equation, and TMAP8 simulation results. The experimental data was selected from several authors for 433.15 K [!cite](nagasaki1986zirconium) and [!cite](jat2013hydrogen) for 524.15 K, 544.15 K, 584.15 K, 604.15 K, and 624.15 K.

To incorporate the entire PCT curve in TMAP8, the curve is divided into three regimes: an α-phase, low-pressure (α) regime; a β-phase, high-pressure (β) regime; and a bi-phasic bridging regime that smoothly connects the two. Rather than switching sharply between fits at a single threshold pressure, the three regimes are combined using a continuous, smoothly-blended weighting scheme so that $f_{at}(T,P)$ and its derivatives vary smoothly across the entire pressure range. The fitting procedures and the blending approach for each region are described below.

### Low-pressure (α) regime

The low-pressure regime is captured as:
\begin{equation}\label{eq:atomic_fraction_alpha}
f_{at,\alpha}(T,P) = 0.7-1\left[5 \times 10^{-3}+\exp\left(-4.37 + 1.34 \times 10^{-2} T + \left( -8.22 \times 10^{-2} - 3.97 \times 10^{-4} T \right) \log\left(P_{lim}(T) - P\right)\right)\right]^{-1}.
\end{equation}

### High-pressure (β) regime

The high-pressure regime is captured as:
\begin{equation}\label{eq:atomic_fraction_beta}
f_{at,\beta}(T,P) = 2.7-1.45\left[1.00+\exp\left(6.57 - 2.21 \times 10^{-2} T + \left( 6.52 \times 10^{-1} - 1.17 \times 10^{-5} T \right) \log\left(P - P_{lim}(T)\right)\right)\right]^{-1}.
\end{equation}

!media comparison_ZrCoHx_PCT.py
       image_name=ZrCoHx_PCT_combined.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ZrCoHx_PCT_combined
       caption=PCT data for $ZrCoH_{x}$ from [!cite](jat2013hydrogen) and [!cite](nagasaki1986zirconium) with fits implemented in TMAP8 and test results.

The plateau ($P_{lim}$) representing the phase transition is captured as:
\begin{equation} \label{eq:pressure_plateau}
P_{lim}(T) = \exp\left(-9.41 + 3.32 \times 10^{-2} T - 3.30 \times 10^{-6} T^2 \right).
\end{equation}

This fit is shown in [ZrCoHx_PCT_plateau_pressure_fit].

!media comparison_ZrCoHx_PCT.py
       image_name=ZrCoHx_PCT_plateau_pressure_fit.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ZrCoHx_PCT_plateau_pressure_fit
       caption=Fit phase transition region as pressure as a function of temperature.

### Bi-phasic (α+β) bridging regime

The α and β regimes are bridged using a sigmoid blending methodology, described below.

First, the bridging regime is expressed as a linear-logarithmic interpolation in pressure:
\begin{equation}\label{eq:mid_interp}
f_{at,\alpha+\beta}(P)= m_{0} + m_{1}\ln(P),
\end{equation}

where the slope and intercept of [eq:mid_interp] are chosen so that the bridging regime is continuous with the low-pressure regime at $P=\delta P_{lim}(T)$ and with the high-pressure regime at $P=\zeta P_{lim}(T)$:

\begin{equation}\label{eq:m0_definition}
m_{0} = f_{at,\alpha}(T,\delta P_{lim}) - \frac{f_{at,\beta}(T,\zeta P_{lim}) - f_{at,\alpha}(T,\delta P_{lim})}{L_{b} - L_{a}} L_{a},
\end{equation}
and
\begin{equation}\label{eq:m1_definition}
m_{1} = \frac{f_{at,\beta}(T,\zeta P_{lim}) - f_{at,\alpha}(T,\delta P_{lim})}{L_{b} - L_{a}},
\end{equation}
with
\begin{equation}
\label{eq:log_bounds}
L_{a} = \ln(\delta P_{lim}), \qquad
L_{b} = \ln(\zeta P_{lim}),
\end{equation}

where $\delta$ and $\zeta$ mark, respectively, the low- and high-pressure edges (relative to $P_{lim}$) of the bridging regime. For the low-pressure edge, a constant value of $\delta = 1.008$ was found to be suitable, while for the high-pressure edge a fitted function, $\zeta(T)$, was required:

\begin{equation}
\label{eq:delta_zeta_defs}
\delta = 1.008, \qquad
\zeta = 2.39 - 5.10 \times 10^{-3} T + 5.42 \times 10^{-6} T^{2}.
\end{equation}

### Smooth blending

With $f_{at,\alpha+\beta}(P)$ fully described, a smooth (logistic) weight blending scheme can be applied using the following equations:

\begin{equation}
\label{eq:blend_x}
x = \ln\!\left(\frac{P}{P_{lim}(T)}\right), \qquad
x_{\delta} = \ln(\delta), \qquad
x_{\zeta} = \ln(\zeta),
\end{equation}
and
\begin{equation}
\label{eq:blend_sigmoids}
s_{\alpha\to\alpha+\beta}(x) = \left[1+\exp\!\left(-\frac{x-x_{\delta}}{\Delta_{\delta}}\right)\right]^{-1}, \qquad
s_{\alpha+\beta\to\beta}(x) = \left[1+\exp\!\left(-\frac{x-x_{\zeta}}{\Delta_{\zeta}}\right)\right]^{-1},
\end{equation}

where $\Delta_{\delta} = \Delta_{\zeta} = 0.08$ are the tunable base widths of the smooth blending function, controlling how rapidly each transition occurs. The (unnormalized) regime weights are then:

\begin{equation}
\label{eq:weight_normalization}
W = \left(1 - s_{\alpha\to\alpha+\beta}\right) + s_{\alpha\to\alpha+\beta}\left(1 - s_{\alpha+\beta\to\beta}\right) + s_{\alpha+\beta\to\beta},
\end{equation}

\begin{equation}
\label{eq:weight_definitions}
w_{\alpha} = \frac{1 - s_{\alpha\to\alpha+\beta}}{W}, \qquad
w_{\alpha+\beta} = \frac{s_{\alpha\to\alpha+\beta}\left(1 - s_{\alpha+\beta\to\beta}\right)}{W}, \qquad
w_{\beta} = \frac{s_{\alpha+\beta\to\beta}}{W},
\end{equation}

and are renormalized so that $w_{\alpha}+w_{\alpha+\beta}+w_{\beta}=1$ at every point. The final atomic fraction used by the kernel is the corresponding weighted sum:

\begin{equation}
\label{eq:overall_interpolation}
f_{at}(T,P) = w_{\alpha}\,f_{at,\alpha}(T,P) + w_{\alpha+\beta}\,f_{at,\alpha+\beta}(T,P) + w_{\beta}\,f_{at,\beta}(T,P).
\end{equation}

Because $f_{at,\alpha+\beta}$ is constructed to agree exactly with $f_{at,\alpha}$ at $P=\delta P_{lim}(T)$ and with $f_{at,\beta}$ at $P=\zeta P_{lim}(T)$, and because the sigmoid weights vary smoothly through these same points, $f_{at}(T,P)$ transitions continuously across the full PCT curve without the discontinuities that a hard-switched piecewise definition would introduce.

The validity of this present fit is between:
\begin{equation} \label{eq:bounds}
20 < P\,\text{[Pa]} < 2 \times 10^{5}.
\end{equation}

## Test

[!file](/ZrCoHx_PCT.i) tests the implantation of the ZrCoHx PCT curves in TMAP8.
The domain contains two blocks: gas (left) and ZrCoHx (right) with an interface between the two blocks.
The diffusion for this test case is given by [!citep](yu2024hydrogen) and the surface reaction rate $K$ is taken from [!citep](jat2013hydrogen) ($K_f=K_b=K$). Note that the diffusion used is based on ZrH$_{1.58}$ hydride since there is no diffusion value for ZrCo hydride. This should not affect the end results of the test case since simulation time goes until equilibrium is achieved.
To model the interface, the input file employs the [InterfaceDiffusion.md] object to model the flux of hydrogen at the surface, and `ADMatInterfaceReactionZrCoHxPCT` to model the steady-state condition for the hydrogen concentration at the surface $C_s$ defined by:

\begin{equation} \label{eq:test_interfacereaction}
\frac{d C_s}{dt} = 0 = K (f_{at}(T,P) \rho - C_s),
\end{equation}

The results of the high pressure test for ($T$, $P$) = (433.15 K, $3 \times 10^{4}$ Pa), (433.15 K, $1 \times 10^{4}$ Pa), (573.15 K, $1 \times 10^{4}$ Pa), and (604.15 K, $5 \times 10^{4}$ Pa), and the results of the low pressure test for ($T$, $P$) = (433.15 K, $1 \times 10^{2}$ Pa), (573.15 K, $1 \times 10^{3}$ Pa), (604.15 K, $1 \times 10^{4}$ Pa), and (604.15 K, $3 \times 10^{3}$ Pa), are shown in [ZrCoHx_PCT_combined]. Overall, the analytical fits show reasonable agreement with the measurements, yielding average root-mean-square errors of 0.056 for the low-pressure region and 0.089 for the high-pressure region.

### Overall PCT testing

[!file](/ZrCoHx_PCT.i) also tests the entire PCT modelling curve, including the smooth bi-phasic blending across the α, bridging, and β regimes, in TMAP8. The simulation follows the same structure as before, but has an arbitrarily high diffusion value to achieve steady-state quickly. The model also includes a linear pressure increase to cover the entire PCT curve:

\begin{equation}
P = P_{\text{initial}} + t \frac{P_{\text{max}} - P_{\text{initial}}}{t_{\text{end}}}.
\end{equation}

The testing conditions include
($T$, $P_{initial}$) = (423.15 K, $2.5 \times 10^{1}$ Pa),
(524.15 K, $2.5 \times 10^{1}$ Pa),
(544.15 K, $2.5 \times 10^{1}$ Pa),
(564.15 K, $2.5 \times 10^{1}$ Pa),
(584.15 K, $2.5 \times 10^{1}$ Pa),
(604.15 K, $2.5 \times 10^{1}$ Pa),
and (624.15 K, $2.5 \times 10^{1}$ Pa).

The [ZrCoHx_PCT_combined] figure shows the PCT fit against the experimental data over the full sweep, including through the smoothly-blended bridging region. The fit exhibits a moderate average error of 24%, but the deviations remain within an acceptable range for modeling purposes.

## Example Input File Syntax

!listing test/tests/ZrCo_hydrogen_system/ZrCoHx_PCT.i block=InterfaceKernels/interface_reaction_ZrCoHx_PCT

!syntax parameters /InterfaceKernels/ADMatInterfaceReactionZrCoHxPCT

!syntax inputs /InterfaceKernels/ADMatInterfaceReactionZrCoHxPCT

!syntax children /InterfaceKernels/ADMatInterfaceReactionZrCoHxPCT