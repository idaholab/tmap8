# ADMatInterfaceReactionYHxPCT

!syntax description /InterfaceKernels/ADMatInterfaceReactionYHxPCT

## Description

The composition of metal hydrides like yttrium hydride (YHx) is described by pressure-composition-temperature (PCT) data.
In TMAP8, the PCT curve can be imposed by an interface kernel that then dictates the material composition.
Hence, the `ADMatInterfaceReactionYHxPCT` interface kernel imposes the surface concentration of H in YHx based on the input pressure (Pa) and temperature (K). `ADMatInterfaceReactionYHxPCT` is related to [ADMatInterfaceReaction.md], but includes the YHx PCT curves.
 At the interface between a solid (main) and a gas (neighbor), it imposes:
\begin{equation} \label{eq:test_interfacereactionYHxPCT}
\frac{d C_s}{dt} = 0 = K_b f_{at}(T,P) \rho -  K_f C_s ,
\end{equation}
where $C_s$ is the surface H concentration in mol/m$^3$,
$K_b$ and $K_f$ are the backward and forward surface reaction rate in 1/s, respectively,
$f_{at}(T,P)$ is the composition in atomic fraction of H in YHx given a gas temperature $T$ and gas pressure $P$,
and $\rho$ is the yttrium atomic density in mol/m$^3$.

[YHx_PCT_Data] shows the data used in this interface kernel. The experimental data originates from [!cite](Lundin_1962).
The [YHx_PCT_fit_2D] shows high and low pressure fit with the high pressure fit from [!cite](Matthews2021SWIFT) and the low-pressure is a newly fitted curve.

!media comparison_YHx_PCT.py
       image_name=YHx_PCT_Data.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=YHx_PCT_Data
       caption=PCT data for YHx from [!cite](Lundin_1962).

!media comparison_YHx_PCT.py
       image_name=YHx_PCT_fit_2D.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=YHx_PCT_fit_2D
       caption=PCT data for YHx from [!cite](Lundin_1962) with high pressure fits from [!cite](Matthews2021SWIFT) implemented in TMAP8, and test results.

The plateau representing phase transition is captured as [!citep](Matthews2021SWIFT):
\begin{equation} \label{eq:pressure_plateau}
P_{lim} = \exp\left(-26.1+3.88 \times 10^{-2} T - 9.7 \times 10^{-6} T^2 \right),
\end{equation}
with $P_{lim}$ being the hydrogen partial pressure limit delineating the plateau in Pa and $T$ being the temperature in K.
This fit is shown in [YHx_PCT_plateau_pressure_fit].

!media comparison_YHx_PCT.py
       image_name=YHx_PCT_plateau_pressure_fit.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=YHx_PCT_plateau_pressure_fit
       caption=Fit phase transition region as pressure as a function of temperature.

In the high pressure region, the atomic fraction $f_{at}$ is determined as [!citep](Matthews2021SWIFT):
\begin{equation}
f_{at}(T,P) = 2-\left[1+\exp(21.6 -0.0225 T + (-0.0445 + 7.18 \times 10^{-4} T) (\log\left(P - P_{lim}(T)\right)))\right]^{-1},
\end{equation}
where $P$ is the hydrogen partial pressure in Pa. While in the low pressure region, the atomic fraction $f_{at}$ is determined as:
\begin{equation}
f_{at}(T,P) = 0.5-\left[0.001+\exp(-89.75 + 0.0975 T + (1.20 - 4.41 \times 10^{-3} T) (\log\left(P_{lim}(T) - P\right)))\right]^{-1},
\end{equation}


## Test

[!file](/YHx_PCT.i) tests the implantation of the YHx PCT curves in TMAP8.
The domain contains two blocks: gas (left) and YHx (right) with an interface between the two blocks.
The diffusion is given by [!citep](MAJER2002438) and the surface reaction rate $K$ is taken from [!citep](FISHER19841536) ($K_f=K_b=K$).
To model the interface, the input file employs the [InterfaceDiffusion.md] object to model the flux of hydrogen at the surface, and `ADMatInterfaceReactionYHxPCT` to model the steady-state condition for the hydrogen concentration at the surface $C_s$ defined by:
\begin{equation} \label{eq:test_interfacereaction}
\frac{d C_s}{dt} = 0 = K (f_{at}(T,P) \rho - C_s),
\end{equation}
where $\rho$ is the yttrium atomic density.

The results of the high pressure test for ($T$, $P$) = (1173.15 K, $1 \times 10^{3}$ Pa), (1173.15 K, $1 \times 10^{4}$ Pa), (1173.15 K, $5 \times 10^{4}$ Pa), and(1473.15 K, $5 \times 10^{4}$ Pa). While the low pressure test for ($T$, $P$) = (1473.15 K, $3 \times 10^{3}$ Pa), (1273.15 K, $3 \times 10^{2}$ Pa), (1573.15 K, $5 \times 10^{3}$ Pa), and(1573.15 K, $6 \times 10^{2}$ Pa).

## Example Input File Syntax

!listing test/tests/yttrium_hydrogen_system/YHx_PCT.i block=InterfaceKernels/interface_reaction_YHx_PCT

!syntax parameters /InterfaceKernels/ADMatInterfaceReactionYHxPCT

!syntax inputs /InterfaceKernels/ADMatInterfaceReactionYHxPCT

!syntax children /InterfaceKernels/ADMatInterfaceReactionYHxPCT

