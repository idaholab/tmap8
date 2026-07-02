# ADMatInterfaceReactionZrCoHxPCT

!syntax description /InterfaceKernels/ADMatInterfaceReactionZrCoHxPCT

## Description

The composition of metal hydrides like zirconium-cobalt hydride (ZrCoH$_{x}$) is described by pressure-composition-temperature (PCT) data.
In TMAP8, the PCT curve can be imposed by an interface kernel that then dictates the material composition.
Hence, the `ADMatInterfaceReactionZrCoHxPCT` interface kernel imposes the surface concentration of H in ZrCoH$_{x}$ based on the input pressure (Pa) and temperature (K). `ADMatInterfaceReactionZrCoHxPCT` is related to [ADMatInterfaceReaction.md], but includes the ZrCoH$_{x}$ PCT curves.
 At the interface between a solid (main) and a gas (neighbor), it imposes:
\begin{equation} \label{eq:test_interfacereactionZr2FeHx}
\frac{d C_s}{dt} = 0 = K_b f_{at}(T,P) \rho -  K_f C_s ,
\end{equation}
where $C_s$ is the surface H concentration in mol/m$^3$,
$K_b$ and $K_f$ are the backward and forward surface reaction rate in 1/s, respectively,
$f_{at}(T,P)$ is the composition in atomic fraction of H in ZrCoH$_{x}$ given a gas temperature $T$ and gas pressure $P$,
and $\rho$ is the zirconium-cobalt molar density in mol/m$^3$.

[ZrCoHx_PCT_Data] shows the data used in this interface kernel. The experimental data was selected from several authors for 433.15 K [!cite](nagasaki1986zirconium) and [!cite](jat2013hydrogen) for 524.15 K, 544.15 K, 584.15 K, 604.15 K, and 624.15 K.

!media comparison_ZrCoHx_PCT.py
       image_name=ZrCoHx_PCT_Data.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ZrCoHx_PCT_Data
       caption=PCT data for ZrCoH$_{x}$ from [!cite](jat2013hydrogen) and [!cite](nagasaki1986zirconium).

To include this PCT data in TMAP8 modelling capabilities the high and low pressure regions were extracted and regressed for the resulting equations.
The low pressure is captured as:
\begin{equation}\label{eq:atomic_fraction_LP}
f_{at,LP}(T,P) = 0.7-1\left[5 \times 10^{-3}+\exp(-4.37 + 1.34 \times 10^{-2} T + ( -8.22 \times 10^{-2} - 3.97 \times 10^{-4} T) (\log\left(P_{lim}(T) - P \right)))\right]^{-1}.
\end{equation}

The high pressure is captured as:
\begin{equation}\label{eq:atomic_fraction_HP}
f_{at,HP}(T,P) = 2.7-1.45\left[1.00+\exp(6.57 - 2.21 \times 10^{-2} T + ( 6.52 \times 10^{-1} - 1.17 \times 10^{-5} T) (\log\left(P - P_{lim}(T)\right)))\right]^{-1}.
\end{equation}

[ZrCoHx_PCT_fit_2D] shows the fitting and TMAP8 results used in this interface kernel.

!media comparison_ZrCoHx_PCT.py
       image_name=ZrCoHx_PCT_fit_2D.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ZrCoHx_PCT_fit_2D
       caption=PCT data for $ZrCoH_{x}$ from [!cite](jat2013hydrogen) and [!cite](nagasaki1986zirconium) with fits implemented in TMAP8, and test results.


The plateau representing phase transition is captured as:
\begin{equation} \label{eq:pressure_plateau}
P_{lim} = \exp\left(-9.41 + 3.32 \times 10^{-2} T - 3.30 \times 10^{-6} T^2 \right),
\end{equation}

This fit is shown in [ZrCoHx_PCT_plateau_pressure_fit].

!media comparison_ZrCoHx_PCT.py
       image_name=ZrCoHx_PCT_plateau_pressure_fit.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ZrCoHx_PCT_plateau_pressure_fit
       caption=Fit phase transition region as pressure as a function of temperature.

The subsequent set of equations are bridged using a simoid blending methodology that is present below.

First we express a linear logarithmic interpolation:
\begin{equation}\label{eq:mid_interp}
f_{mid}(P)= m{0} + m_{1}\ln(P),
\end{equation}

where the slope of [eq:mid_interp] are given as

\begin{equation}\label{eq:m0_definition}
m_{0} = f_{LP}(T,\alpha P_{lim}) - \frac{f_{HP}(T,\beta P{lim}) - f_{LP}(T,\alpha P{lim})}{L{b} - L_{a}} L_{a},
\end{equation}
and
\begin{equation}\label{eq:m1_definition}
m_{1} = \frac{f_{HP}(T,\beta P_{lim}) - f_{LP}(T,\alpha P{lim})}{L_{b} - L_{a}} L_{a},
\end{equation}

\begin{equation}
\label{eq:log_bounds}
L_{a} = \ln(\alpha P_{lim}), \qquad
L_{b} = \ln(\beta P_{lim}),
\end{equation}

where $\beta$ and $\alpha$ represent the high- and low-pressure transition as a ratio of high-to-plateau pressure and plateau-to-low pressure regions. For the ratio of plateau-to-low pressure regions a constant value of 1.008 was found to be suitable, while for the high-to-plateau pressure a fitted function, $\beta$, was required.
$\alpha and $\beta$ are defined as
\begin{equation}
\label{eq:alpha_beta_defs}
\beta = 2.39 - 5.10 \times 10^{-3} T + 5.42 \times 10^{-6} T^{2}, \qquad
\alpha = 1.008,
\end{equation}

with the $f_{mid}(P)$ fully described a weight sigmoid blending function can be applied with the following equations:

\begin{equation}
\label{eq:scaled_variables}
r = \frac{P}{P_{lim}}, \qquad
x = \ln(r), \qquad
x_{\alpha} = \ln(\alpha), \qquad
x_{\beta} = \ln(\beta)
\end{equation}

and
\begin{equation}
\label{eq:switching_functions}
s_{(LP\to mid)} = \frac{1}{1 + e^{-(x - x_{\alpha})/\Delta_{\alpha}}}, \qquad
s_{(mid\to HP)} = \frac{1}{1 + e^{-(x - x_{\beta})/\Delta_{\beta}}}
\end{equation}

where $\Delta_{\beta}$ is the tunable base widths of the smooth blending function set to a default 0.08. Subsequent of the sigmoid blending function, a normalization of their weights to induce a smooth transition is written as such:

\begin{equation}
\label{eq:weight_normalization}
W = (1 - s_{(LP\to mid)}) + s_{(LP\to mid)}(1 - s_{(mid\to HP)}) + s_{(mid\to HP)}
\end{equation}

\begin{equation}
\label{eq:weight_definitions}
w_{LP} = \frac{1 - s_{(LP\to mid)}}{W}, \qquad
w_{mid} = \frac{s_{(LP\to mid)}(1 - s_{(mid\to HP)})}{W}, \qquad
w_{HP} = \frac{s_{(mid\to HP)}}{W}
\end{equation}

\begin{equation}
\label{eq:overall_interpolation}
f_{overall}(T,P) = w_{LP}f_{LP}(T,P) + w_{mid}f_{mid}(T,P) + w_{HP}f_{HP}(T,P).
\end{equation}

Lastly, the validity of this present fit is between:
\begin{equation} \label{eq:bounds}
20 < P\,\text{[Pa]} < 2 \times 10^{5}
\end{equation}

## Test

### Testing Individual Regions

[/ZrCoHx_PCT.i] tests the implantation of the ZrCoH$_{x}$ PCT curves in TMAP8.
The domain contains two blocks: gas (left) and ZrCoH$_{x}$ (right) with an interface between the two blocks.
The diffusion is for this test case is given by [!citep](yu2024hydrogen) and the surface reaction rate $K$ is taken from [!citep](jat2013hydrogen) ($K_f=K_b=K$). Note that the diffusion used is based on ZrH$_{1.58}$ hydride since there is not diffusion value on ZrCo hydride. This should not affect the end results of the test case since simulation time goes until equlibrium is achieved.
To model the interface, the input file employs the [InterfaceDiffusion.md] object to model the flux of hydrogen at the surface, and `ADMatInterfaceReactionZrCoHxPCT` to model the steady-state condition for the hydrogen concentration at the surface $C_s$ defined by:
\begin{equation} \label{eq:test_interfacereaction}
\frac{d C_s}{dt} = 0 = K (f_{at}(T,P) \rho - C_s),
\end{equation}


The results of the high pressure test for ($T$, $P$) = (433.15 K, $3 \times 10^{4}$ Pa), (433.15 K, $1 \times 10^{4}$ Pa), (573.15 K, $1 \times 10^{4}$ Pa), and (604.15 K, $5 \times 10^{4}$ Pa). The results of the low pressure test for ($T$, $P$) = (433.15 K, $1 \times 10^{2}$ Pa), (573.15 K, $1 \times 10^{3}$ Pa), (604.15 K, $1 \times 10^{4}$ Pa), and (604.15 K, $3 \times 10^{3}$ Pa) are shown in [ZrCoHx_PCT_fit_2D]. As seen in the results, there are minor deviations, potentially due to rounding errors in the atomic‑fraction expression. Nonetheless, the errors remain below 1%, indicating that the fits are suitable for PCT modeling.


### Overall PCT testing

[/ZrCoHx_PCT.i] also tests the entire PCT modelling curves in TMAP8. The model follows the same structure as before, but has an arbitrarily high diffusion value to acheive steady-state quickly. The simulation also includes a linear pressure increase to cover the entire PCT curve:

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


The [PCT_all_temperatures_experimental_vs_TMAP8_ZrCo] shows the PCT fit against the experimental data. Evidently, the fit exhibits moderate error, but the deviations remain within an acceptable range for modeling purposes.

!media comparison_ZrCoHx_PCT.py
       image_name=PCT_all_temperatures_experimental_vs_TMAP8_ZrCo.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=PCT_all_temperatures_experimental_vs_TMAP8_ZrCo
       caption=PCT data for ZrCoH$_{x}$ from [!cite](jat2013hydrogen) and [!cite](nagasaki1986zirconium) with fits implemented in TMAP8, and test results.


## Example Input File Syntax

!listing test/tests/ZrCo_hydrogen_system/ZrCoHx_PCT.i block=InterfaceKernels/interface_reaction_ZrCoHx_PCT


!syntax parameters /InterfaceKernels/ADMatInterfaceReactionZrCoHxPCT

!syntax inputs /InterfaceKernels/ADMatInterfaceReactionZrCoHxPCT

!syntax children /InterfaceKernels/ADMatInterfaceReactionZrCoHxPCT

