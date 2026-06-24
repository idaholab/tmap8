# ADMatInterfaceReactionZr2FeHxPCT

!syntax description /InterfaceKernels/ADMatInterfaceReactionZr2FeHxPCT

## Description

The composition of metal hydrides like zirconium-iron hydride (Zr$_{2}$FeH$_{x}$) is described by pressure-composition-temperature (PCT) data.
In TMAP8, the PCT curve can be imposed by an interface kernel which then dictates the material composition. Wherein, the `ADMatInterfaceReactionZr2FeHxPCT` interface kernel imposes the surface concentration of H in Zr$_{2}$FeH$_{x}$ based on the input pressure (Pa) and temperature (K). `ADMatInterfaceReactionZr2FeHxPCT` is related to [ADMatInterfaceReaction.md], but incorporates the Zr$_{2}$FeH$_{x}$ PCT curves.
 At the interface between a solid (main) and a gas (neighbor), it imposes:
\begin{equation} \label{eq:test_interfacereactionZr2FeHx}
\frac{d C_s}{dt} = 0 = K_b f_{at}(T,P) \rho -  K_f C_s ,
\end{equation}
where $C_s$ is the surface H concentration in mol/m$^3$,
$K_b$ and $K_f$ are the backward and forward surface reaction rate in 1/s, respectively,
$f_{at}(T,P)$ is the composition in atomic fraction of H in Zr$_{2}$FeH$_{x}$ given a gas temperature $T$ and gas pressure $P$,
and $\rho$ is the zirconium-iron molar density in mol/m$^3$.
Note that the neighbor pressure is given as a molecular concentration (i.e., not an atomic concentration) and is converted to pressure within the interface kernel.


[Zr2FeHx_PCT_Data] shows the experimental data from [!cite](yang2025potential) used to create numerical fits for PCT modelling.

!media comparison_Zr2FeHx_PCT.py
       image_name=Zr2FeHx_PCT_Data.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=Zr2FeHx_PCT_Data
       caption=PCT data for Zr$_{2}$FeH$_{x}$ from [!cite](yang2025potential).

The pressure isotherm is captured as:
\begin{equation} \label{eq:atomic_fraction}
f_{at}(T,P) = 5.0 - 8.32 \times 10^{-3}\left[1 \times 10^{-3} +\exp(-2.49 - 7.62\times 10^{-3} T + (5.63 \times 10^{-2} + 1.72 \times 10^{-4} T) (\log\left(P - P_{lim}\right)))\right]^{-1},
\end{equation}

with the pressure limit $P_{lim}$ set to be a constant value of
\begin{equation} \label{eq:pressure_plateau}
P_{lim} = 5\ \text{Pa}
\end{equation}

The validity of this present fit is between:
\begin{equation} \label{eq:bounds}
7 < P\,\text{[Pa]} < 5 \times 10^{5}
\end{equation}


## Test

[/Zr2FeHx_PCT.i] tests the implantation of the Zr$_{2}$FeH$_{x}$ PCT curves in TMAP8 using constant testing conditions, i.e pressure and temperature.
The domain contains two blocks: gas (left) and Zr$_{2}$FeH$_{x}$(right) with an interface between the two blocks.
The diffusion is given by [!cite](yu2024hydrogen) and the surface reaction rate $K$ is taken from [!cite](yang2025potential) ($K_f=K_b=K$). Note that the diffusion is for ZrH$_{1.8}$ because no diffusion data exist for Zr$_{2}$FeH$_{x}$.
To model the interface, the input file employs the [InterfaceDiffusion.md] object to model the flux of hydrogen at the surface, and `ADMatInterfaceReactionZr2FeHxPCT` to model the steady-state condition for the hydrogen concentration at the surface $C_s$ defined by:
\begin{equation} \label{eq:test_interfacereaction}
\frac{d C_s}{dt} = 0 = K (f_{at}(T,P) \rho - C_s),
\end{equation}

The results of the high pressure test for ($T$, $P$) =(598.15 K, $1 \times 10^{3}$ Pa), (623.15 K, $1 \times 10^{4}$ Pa), (648.15 K, $1 \times 10^{2}$ Pa), and (648.15 K, $1 \times 10^{5}$ Pa) are shown in [Zr2FeHx_PCT_fit_2D] and are a good fit.


!media comparison_Zr2FeHx_PCT.py
       image_name=Zr2FeHx_PCT_fit_2D.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=Zr2FeHx_PCT_fit_2D
       caption=PCT data for  Zr$_{2}$FeH$_{x}$ from [!cite](yang2025potential) implemented in TMAP8, and test results.


### Overall PCT Testing

[/Zr2FeHx_PCT.i] can also test the entire PCT modelling capabilities in TMAP8. The model follows the same structure as the previoius section, but has an arbitrarily high diffusion value to acheive steady-state quickly. The model also includes a linear pressure increase to cover the entire PCT curve.

\begin{equation}
P = P_{\text{initial}} + t \frac{P_{\text{max}} - P_{\text{initial}}}{t_{\text{end}}}
\end{equation}

The testing conditions include ($T$, $P_{initial}$) = (598.15 K, $7$ Pa), (623.15 K, $7$ Pa), and (648.15 K, $7$ Pa). The [PCT_all_temperatures_experimental_vs_TMAP8_Zr2Fe] shows the PCT fit against the experimental data. Evidently, the fit exhibits moderate error, but the deviations remain within an acceptable range for modeling purposes.

!media comparison_Zr2FeHx_PCT.py
       image_name=PCT_all_temperatures_experimental_vs_TMAP8_Zr2Fe.png
       style=width:80%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=PCT_all_temperatures_experimental_vs_TMAP8_Zr2Fe
       caption=PCT data for Zr$_{2}$FeH$_{x}$ from [!cite](yang2025potential) with fits implemented in TMAP8, and test results.




## Example Input File Syntax

!listing test/tests/Zr2Fe_hydrogen_system/Zr2FeHx_PCT.i block=InterfaceKernels/interface_reaction_Zr2FeHx_PCT

!syntax parameters /InterfaceKernels/ADMatInterfaceReactionZr2FeHxPCT

!syntax inputs /InterfaceKernels/ADMatInterfaceReactionZr2FeHxPCT

!syntax children /InterfaceKernels/ADMatInterfaceReactionZr2FeHxPCT

