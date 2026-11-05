# ver-1hb

# Convective Gas Outflow Problem in Equilibrating Enclosures

## Problem set up

This verification problem models two species 'T$_2$' (gaseous tritium) and 'D$_2$' (gaseous deuterium) equilibrating in pressure between two enclosures. It recreates the ver-1hb case in [!cite](ambrosek2008verification). This TMAP8 case is published in [!cite](Simon2027). Enclosure 1 is pre-charged with tritium and Enclosure 2 is pre-charged with deuterium. The gases flow between the two enclosures until the T$_2$ and D$_2$ partial pressures in the two enclosures equilibrate. The pressure change rates for this system for T$_2$ gas are given by
\begin{equation} \label{eq:dt_P1_T}
\frac{dP^1_{T_2}}{dt} = \frac{Q}{V} (P^2_{T_2} - P^1_{T_2}),
\end{equation}
\begin{equation} \label{eq:dt_P2_T}
\frac{dP^2_{T_2}}{dt} = - \frac{Q}{V} (P^2_{T_2} - P^1_{T_2}),
\end{equation}
and for $D_2$ gas are given by
\begin{equation} \label{eq:dt_P1_D}
\frac{dP^1_{D_2}}{dt} = \frac{Q}{V} (P^2_{D_2} - P^1_{D_2}),
\end{equation}
\begin{equation} \label{eq:dt_P2_D}
\frac{dP^2_{D_2}}{dt} = - \frac{Q}{V} (P^2_{D_2} - P^1_{D_2}),
\end{equation}
where $Q$ is the volumetric flow rate (m$^3 \cdot$s$^{-1}$), $V$ is the volume (m$^3$), and $P^i_j$ is the pressure in enclosure $i$ of gas species $j$ ($j$ = $T_2$ or $D_2$).

We solve these time evolution equations for the T$_2$ and D$_2$ pressures in the two enclosures using TMAP8 with $t$ as the time and the initial condition set to $P^1_{T_2} = P^2_{D_2} = 1$ Pa and $P^2_{T_2} = P^1_{D_2} = 0$ Pa. We use $V = 1$ m$^3$ and $Q = 0.1$ m$^3 \cdot$s$^{-1}$. The system of two enclosures is illustrated in [ver-1hb_schematic].

!media figures/ver-1hb_schematic.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=ver-1hb_schematic
    caption=Schematic of the ver-1hb case: T$_2$ and D$_2$ equilibrate in pressure between two enclosures through a flow $Q$.

## Analytical solution

Mass balance between the two enclosures gives the following relationship between the pressure of species in the two enclosures
\begin{equation} \label{eq:mass_balance}
P^1_j (t) + P^2_j (t) = P^1_i (t=0) + P^2_i (t=0),
\end{equation}
where $t$ is time and $P^i_j (t=0)$ is the initial pressure of the gas $j$ in enclosure $i$. By substituting [eq:mass_balance] into [eq:dt_P1_T] and [eq:dt_P2_T] based on [!cite](ambrosek2008verification), we get
\begin{equation} \label{eq:T2_analytical_soln}
P^i_{T_2} = P^S_{T_2} + \left(P^i_{T_2}-P^S_{T_2}\right) \exp\left(-\frac{2Q}{V} t \right),
\end{equation}
where $P^S_{T_2} = \left(P^1_{T_2} (t=0) + P^2_{T_2} (t=0)\right)/2$. Similarly, for D$_2$ we get
\begin{equation} \label{eq:D2_analytical_soln}
P^i_{D_2} = P^S_{D_2} + \left(P^i_{D_2}-P^S_{D_2}\right) \exp\left(-\frac{2Q}{V} t \right),
\end{equation}
where $P^S_{D_2} = \left(P^1_{D_2} (t=0) + P^2_{D_2} (t=0)\right)/2$.

Note that the TMAP7 verification case in [!cite](ambrosek2008verification) provides the initial values of gas pressures and compares plots of gas pressure, but the analytical solutions use concentration variables. We used pressure variables throughout the derivation here to keep consistent units, but the pressure can be converted to concentration if needed using the ideal gas law as discussed in [ver-1ha.md].

## Results and comparison against analytical solution

The comparison of TMAP8 results against the analytical solution is shown in [ver-1hb_comparison_tritium] and [ver-1hb_comparison_deuterium]. The match between TMAP8's predictions and the analytical solution of T$_2$ pressure is satisfactory, with root mean square percentage errors (RMSPE) of 0.1 and 0.13 % for the first and second enclosures respectively. The RMSPE values are flipped for the D$_2$ calculations, since the initial pressure conditions are also flipped for D$_2$ compared to T$_2$.

!media comparison_ver-1hb.py
       image_name=ver-1hb_comparison_pressure_tritium.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1hb_comparison_tritium
       caption=Comparison of pressure of species T$_2$ for the first and second enclosures equilibrating predicted by TMAP8 and provided by the analytical solution. The RMSPE is the root mean square percent error between the analytical solution and TMAP8 predictions. This recreates the verification figure from TMAP7 [!cite](ambrosek2008verification).

!media comparison_ver-1hb.py
       image_name=ver-1hb_comparison_pressure_deuterium.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1hb_comparison_deuterium
       caption=Comparison of pressure of species D$_2$ for the first and second enclosures equilibrating predicted by TMAP8 and provided by the analytical solution. The RMSPE is the root mean square percent error between the analytical solution and TMAP8 predictions. This recreates the verification figure from TMAP7 [!cite](ambrosek2008verification).

## Input files

!style halign=left
The input file for this case can be found at [!file](/ver-1hb.i), which is also used as test in TMAP8 at [!file](/ver-1hb/tests).

!bibtex bibliography
