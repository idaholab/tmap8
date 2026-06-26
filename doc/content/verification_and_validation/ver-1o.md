# ver-1o

# Joule Heating in a Proton-Conducting Ceramic Slab under Applied Voltage

## Case Description

This verification case isolates the temperature response caused by Joule heating in a one-dimensional proton-conducting ceramic (PCC) slab under an applied voltage. In PCC membranes, the electrical current induced by an applied voltage generates Joule heating, which can increase the local temperature and influence hydrogen-isotope transport. This case verifies the thermal part of the voltage-assisted PCC model independently against an analytical solution for a slab with a uniform volumetric heat source.

This verification case use a 5 mm half-domain that represents one half of the original 10 mm membrane. The left boundary is held at a prescribed wall temperature, and the right boundary is adiabatic to represent the symmetry plane at the slab centerline. The same electric field as the original full-domain configuration is retained by using a 20 V drop across the full 10 mm membrane.

## Case Set Up

The heat equation with a Joule heating source is

\begin{equation}
\label{eq:ver-1o_heat}
\rho c_p \frac{\partial T}{\partial t}
= \kappa \frac{\partial^2 T}{\partial x^2} + \dot{q}_J,
\end{equation}

where $\rho$ is the density, $c_p$ is the specific heat capacity, $\kappa$ is the thermal conductivity, and $\dot{q}_J$ is the volumetric Joule heating rate. The Joule heating is computed from a constant electrical conductivity and a constant applied electric field,

\begin{equation}
\label{eq:ver-1o_joule}
\dot{q}_J = \sigma E^2 = \sigma \left(\frac{V_{\mathrm{full}}}{L_{\mathrm{full}}}\right)^2,
\end{equation}

where $\sigma$ is the electrical conductivity, $V_{\mathrm{full}}$ is the voltage drop across the full slab, and $L_{\mathrm{full}}$ is the full slab thickness. The half-domain solved in TMAP8 has thickness $L = L_{\mathrm{full}}/2$, with boundary conditions

\begin{equation}
\label{eq:ver-1o_bcs}
T(0,t) = T_{\mathrm{wall}},
\qquad
\left.\frac{\partial T}{\partial x}\right|_{x=L} = 0.
\end{equation}

The imposed voltage profile in the input file is

\begin{equation}
\label{eq:ver-1o_voltage_profile}
\phi(x) = V_{\mathrm{left}} - \left(\frac{V_{\mathrm{full}}}{L_{\mathrm{full}}}\right)x,
\end{equation}

so the electric field magnitude is constant across the domain. Because the conductivity and electric field are both constant, $\dot{q}_J$ is uniform in space.

The model parameters used in this case are listed in [ver-1o_set_up_values]. The thermal properties of the BCY20 membrane are taken from [!cite](yamanaka2003thermophysical). The remaining parameters are selected to simplify the verification problem. The electrical conductivity is set to a constant reference value, and the thermal conductivity $\kappa$ is deliberately set lower than the physical BCY20 value to produce a meaningful temperature rise for verification purposes.

!table id=ver-1o_set_up_values caption=Values of model properties for the Joule heating verification problem.
| Parameter | Description | Value | Units | Reference |
| --------- | ----------- | ----- | ----- | --------- |
| $T_{\mathrm{wall}}$ | wall temperature | 773 | K | -- |
| $L_{\mathrm{full}}$ | full PCC slab thickness | 10$\times 10^{-3}$ | m | -- |
| $L$ | simulated half-slab thickness | 5$\times 10^{-3}$ | m | -- |
| $V_{\mathrm{full}}$ | voltage applied across the full PCC slab | 20 | V | -- |
| $\sigma$ | electrical conductivity | 1$\times 10^{-3}$ | S/m | -- |
| $\kappa$ | thermal conductivity | 0.014 | W/(m$\cdot$K) | -- |
| $c_p$ | specific heat capacity | 120 | J/(mol$\cdot$K) | [!cite](yamanaka2003thermophysical) |
| $\rho$ | density | 6.154 | g/cm$^3$ | -- |

The verification focuses on two aspects of the thermal solution: (1) the transient maximum temperature rise at the insulated symmetry plane, and (2) the transient spatial temperature profile at selected times.

## Analytical Solution

[!cite](miller1967transient) provides the analytical solution for the transient temperature solution under a constant volumetric heat source as:

\begin{equation}
\label{eq:ver1o_transient}
T(x,t) = T_{\mathrm{wall}} + \frac{\dot{q}_J \ell^2}{\kappa}
\left[
  \frac{x}{\ell} - \frac{1}{2}\!\left(\frac{x}{\ell}\right)^{\!2}
  - 2 \sum_{n=0}^{\infty}
    \frac{\sin\!\left(\lambda_n x/\ell\right)}{\lambda_n^3}
    \exp\!\left(-\lambda_n^2 \frac{\alpha t}{\ell^2}\right)
\right],
\end{equation}

where $\alpha = \kappa/(\rho c_p)$ is the thermal diffusivity, and the eigenvalues $\lambda_n$ are described as

\begin{equation}
\label{eq:ver1o_lambda}
\lambda_n = \left(n + \tfrac{1}{2}\right)\pi, \qquad n = 0,\, 1,\, 2,\, \ldots,
\end{equation}

where $n$ is the integer mode number in the Fourier series. As $t \to \infty$, \cref{eq:ver1o_transient} reduces to the steady-state parabolic profile

\begin{equation}
\label{eq:ver1o_ss}
T(x) = T_{\mathrm{wall}} + \frac{\dot{q}_J}{\kappa}\!\left(\ell x - \frac{x^2}{2}\right).
\end{equation}


## Results

[ver-1o_comparison_temperature_history] compares the maximum temperature rise history, $\Delta T_{\max}(t)$, predicted by TMAP8 against the analytical solution evaluated at the insulated face $x = L$. The TMAP8 result closely matches the analytical solution, with an RMSPE of 0.50%.

!media comparison_ver-1o.py
       image_name=ver-1o_comparison_temperature_history.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1o_comparison_temperature_history
       caption=Comparison of the TMAP8 transient maximum temperature rise history with the analytical half-slab solution for a constant Joule-heating source, prescribed surface temperature at $x = 0$, and insulated symmetry plane at $x = L$.

[ver-1o_comparison_temperature_profiles] compares the transient temperature profiles at $t = 1000$ s and $t = 20000$ s with the analytical solution. The simulated profiles show excellent agreement with the analytical solution, with RMSPE values below 0.01% at both times.

!media comparison_ver-1o.py
       image_name=ver-1o_comparison_temperature_profiles.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=ver-1o_comparison_temperature_profiles
       caption=Comparison of the TMAP8 transient temperature profiles at $t = 1000$ s and $t = 20000$ s with the analytical half-slab solution.

## Input Files

!style halign=left
The input file for this case can be found at [/ver-1o.i]. More information about the changes can be found in the test specification file for this case [/ver-1o/tests].

!bibtex bibliography
