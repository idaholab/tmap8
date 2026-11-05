# val-2f

# Modelling self-damaged tungsten effects on deuterium transport

## Case Description

The case being used for validation here involves the use of recrystallized polycrystalline tungsten (PCW) samples, which are subjected to ion irradiation and subsequent analysis using thermal desorption spectroscopy (TDS). The primary objective is to determine how damage influences deuterium trapping and release. This case is drawn and updated from [!cite](dark2024modelling). This case is introduced in [!cite](Simon2027), with full results to appear in a forthcoming publication.

The TDS process is simulated using TMAP8 in a 1D tungsten sample with a thickness of 0.8 mm. The TDS simulation consisted of three phases: implantation, cooldown, and desorption.

The sample temperature histories are shown in [val-2f_temperature_history].

!media comparison_val-2f.py
    image_name=val-2f_temperature_history.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=val-2f_temperature_history
    caption=Temperature history.

## Model Description

### 1- Implantation phase:

During the charging phase, deuterium is continuously implanted into the tungsten sample over a period of 72 hours. The temperature is maintained at 370 K throughout this phase. The surface is exposed to a constant flux of $\phi=5.79\times 10^{19}$ atoms/m$^2$/s, corresponding to a total fluence of $1.5\times 10^{25}$ atoms/m$^2$. The implantation profile follows a Gaussian distribution centered at the mean implantation depth of $R_p=0.7$ nm, with a standard deviation of $\sigma = 0.5$ nm :

\begin{equation}
    \label{eq:source_term}
    S(x) = \frac{1}{\sigma \sqrt{2\pi}} \exp\left( -\frac{(x - R_p)^2}{2\sigma^2} \right) \cdot \phi_{\text{surface}}(t)
\end{equation}

where the surface flux function is given by:

\begin{equation}
    \phi_{\text{surface}}(t) =
    \begin{cases}
        \phi, & t < 72 h \\
        0, & \text{otherwise}
    \end{cases}
\end{equation}

The implantation distribution is illustrated in [val-2f_implantation_distribution]: most of the implanted atoms are found within a few standard deviations ($\sigma$) of the mean implantation depth ($R_p$). In this context, it means that the mesh in the region where deuterium implantation occurs should be refined to a size comparable to $\sigma$. In this TMAP8 simulation, the first mesh region is set to length of $6\sigma$, divided into 100 elements. This allows to capture the majority of the implantation profile and ensure that the mesh is sufficiently refined in this region.

!media comparison_val-2f.py
    image_name=val-2f_implantation_distribution.png
    style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
    id=val-2f_implantation_distribution
    caption=Deuterium implantation.

### 2- Cooldown phase:

After the implantation phase, the system enters the cooldown phase, lasting 12 hours. During this period, the sample temperature is rapidly reduced from 370 K to 295 K. No additional deuterium is introduced during this phase, meaning the source term is set to zero.

### 3- Desorption phase:

The final stage of the simulation is the desorption phase, during which the sample is gradually heated from 300 K to 1000 K at a constant rate of $\beta = 0.05$ K/s.

## Governing equations

### • Damaged induced traps

The evolution of the trapping site density, $N_i$, over time under irradiation is described by [!citep](dark2024modelling):

\begin{equation}
    \label{eq:trapping_sites_density}
    \frac{\partial N_i}{\partial t} = \Phi \cdot K_c \left[ 1 - \frac{N_i}{N_{\text{max,}\Phi}} \right] - A \cdot N_i.
\end{equation}

This equation consists of two terms. The first term, $\Phi \cdot K_c \left[ 1 - \frac{N_i}{n_{\text{max}, \Phi}} \right]$, represents the creation of trapping sites. It increases the trap density up to a saturation density, $N_{\text{max,}\Phi}$, due to the damage imposed on the sample. Here, $\Phi$ is the damage rate in (dpa/s) and $K_c$ is the trap creation factor in (traps/m$^3$/dpa).
The second term, $A \cdot N_i$, accounts for the annealing effect which decreases the density of trapping sites. $A$ is the trap annealing rate in (1/s) and follows an Arrhenius law given by
\begin{equation}
    \label{eq:trapping_sites_annealing_rate}
    A = A_0 \exp\left(\frac{-E_A}{k_B T}\right),
\end{equation}
where $A_0$ is a pre-exponential factor, $E_A$ is the activation energy, $k_B$ is the Boltzmann constant, and $T$ is the temperature.
The parameters for the evolution of the irradiation-induced traps are listed in [val-2f_damaged_induced_traps].

The analytical solution for the ODE is given by:

\begin{equation}
    \label{eq:trapping_sites_density_sol}
    N_i(t) = \frac{\Phi K_c}{\frac{\Phi K_c}{N_{\text{max}, \Phi}} + A} \left[ 1 - \exp\left(-\left(\frac{\Phi K_c}{N_{\text{max}, \Phi}} + A\right)t\right) \right].
\end{equation}

The computed trap densities are provided in [val-2f_traps_values].

### • Deuterium transport equations

The general form of the transport equations for the deuterium in tungsten is given by:

\begin{equation}
    \label{eq:diffusion}
    \frac{\partial C_M}{\partial t} = \nabla \cdot D \nabla C_M + S - \sum_{i=1}^{6} f_{T/M,i} \frac{\partial C_{T_i}}{\partial t}
\end{equation}

and, for $i \in [1,6]$ representing the trapping sites:

\begin{equation}
    \label{eq:trapped_rate}
    \frac{\partial C_{T_i}}{\partial t} = \alpha_t^i  \frac {C_{T_i}^{empty} C_M } {(N f_{T/M,i})} - \alpha_r^i C_{T_i}
\end{equation}

and

\begin{equation}
    C_{T_i}^{empty} = C_{{T_i}0} N - f_{T/M,i} C_{T_i}
\end{equation}

where $C_M$ is the concentration of mobile tritium, $t$ is the time, $S$ is the source term in sample due to the deuterium implantation ([eq:source_term]), $C_{T_i}$ is the trapped species in trap $i$, $\alpha_t^i$ and $\alpha_r^i$ are the trapping and release rate coefficients for trap $i$, $f_{T/M,i}$ is a user-defined numerical factor scaling $C_{T_i}$ to be closer to $C_M$ for better numerical convergence, $C_{{T_i}0}$ is the fraction of host sites $i$ that can contribute to trapping, $C_{T_i}^{empty}$ is the concentration of empty trapping sites, and $N$ is the host density, and $D$ is the deuterium diffusivity in tungsten, which is defined as:

\begin{equation} \label{eq:diffusivity}
D = D_{0} \exp \left( - \frac{E_{D}}{k_b T} \right)
\end{equation}

where $E_{D}$ is the diffusion activation energy, $T$ is the temperature, and $D_{0}$ is the maximum diffusivity coefficient.

$\alpha_t^i$ and $\alpha_r^i$ are defined as:

\begin{equation} \label{eq:trapping}
\alpha_t^i = \alpha_{t0}^i \exp(-\epsilon_t^i / T)
\end{equation}

and

\begin{equation} \label{eq:release}
\alpha_r^i = \alpha_{r0}^i \exp(-\epsilon_r^i / T)
\end{equation}

where $\alpha_{t0}^i$ and $\alpha_{r0}^i$ are the pre-exponential factors of trapping and release. The trapping energy $\epsilon_t^i$ is equal to the diffusion activation energy $E_D$.

### • Boundary conditions

There are several ways to model the surface behavior of deuterium, and this study tested two options. One can assume that every deuterium atom at the surface is immediately desorbed from the materials, effectively assuming an infinite recombination rate at the surface and imposing a null Dirichlet boundary condition for the mobile deuterium concentration ($C_M = 0$ atoms/m$^3$). This is the assumption used in [!cite](dark2024modelling) and reproduced in [val-2f_comparison_inf_recombination].

However, it is also possible to capture the rate of deuterium recombination at the surface
as it recombines into gas. It can be described by the following surface flux:

\begin{equation}
    J = 2 A K_r C^2
\end{equation}

where $J$ represents the recombination flux exiting the sample on both the left and right sides, $A$ is the surface area, and $K_r$ is the deuterium recombination coefficient. The coefficient of 2 accounts for the fact that 2 deuterium atoms combine to form one D$_2$ molecule. Using this condition, the surface concentration will not be imposed, but be governed by the concentration of deuterium coming to the surface from the bulk and the rate of recombination. This boundary condition is used in [val-2f_comparison].

## Case and Model Parameters


In this section provides the model parameters for this validation case. [val-2f_set_up_values] provides the base model parameters for the validation case. Then, we presents two sets of parameter values for the trapping sites. First, in [val-2f_damaged_induced_traps], we lists the parameters related to the damage-induced traps. These parameters capture the irradiation-dependent evolution of trap properties. Second, in [val-2f_traps_values], we reproduce the calibrated values used in [!cite](dark2024modelling) to reproduce the desorption data. As illustrated in [val-2f_trap_induced_density], the trap densities in these two approaches, i.e., analytical solution in [eq:trapping_sites_density_sol] and calibrated values in [val-2f_trap_induced_density], differ.

!table id=val-2f_set_up_values caption=Values of material properties.
| Parameter | Description                                    | Value                       | Units         | Reference                  |
| --------- | ---------------------------------------------- | --------------------------- | ------------- | -------------------------- |
| $k_B$     | Boltzmann constant                             | 1.380649 $\times 10^{-23}$  | J/K           | [PhysicalConstants.h](https://physics.nist.gov/cgi-bin/cuu/Value?r) |
| $T_{\text{initial}}$ | Initial temperature                 | 370                         | K             | [!cite](dark2024modelling) |
| $T_{\text{cooldown}}$ | Cooldown temperature               | 295                         | K             | [!cite](dark2024modelling) |
| $T_{\text{desorption,min}}$ | Desorption start temperature | 300                         | K             | [!cite](dark2024modelling) |
| $T_{\text{desorption,max}}$ | Desorption end temperature   | 1000                        | K             | [!cite](dark2024modelling) |
| $\beta$   | Desorption heating rate                        | 0.05                        | K/s           | [!cite](dark2024modelling) |
| $t_{\text{charge}}$ | Charging time                        | 72                          | h             | [!cite](dark2024modelling) |
| $t_{\text{cooldown}}$ | Cooldown duration                  | 12                          | h             | [!cite](dark2024modelling) |
| $D_0$     | Diffusion pre-factor                           | 1.6 $\times 10^{-7}$        | m$^2$/s       | [!cite](dark2024modelling) |
| $E_D$     | Activation energy for deuterium diffusion      | 0.28                        | eV            | [!cite](dark2024modelling) |
| $R_p$     | Mean implantation depth                        | 0.7                         | nm            | [!cite](dark2024modelling) |
| $\sigma$  | Standard deviation of implantation profile     | 0.5                         | nm            | [!cite](dark2024modelling) |
| $\Phi_D$  | Incident fluence                               | 1.5 $\times 10^{25}$        | atoms/m$^2$   | [!cite](dark2024modelling) |
| $\phi_D$  | Incident flux                                  | 5.79 $\times 10^{19}$       | atoms/m$^2$/s | [!cite](dark2024modelling) |
| $l_W$     | Length of the tungsten sample                  | 0.8                         | mm            | [!cite](dark2024modelling) |
| $N$       | Tungsten density                               | 6.3222 $\times 10^{28 }$    | at/m$^3$      | [J-Dark-PhD](https://zenodo.org/records/11085134) |


!table id=val-2f_damaged_induced_traps caption=Damaged-induced traps parameters from [!cite](dark2024modelling) used in [eq:trapping_sites_density] to capture the evolution of trap properties with irradiation.
| Trap   | $\Phi$ (dpa/s)       | $K_c$ (traps/m$^3$/dpa) | $N_{\text{max,}\Phi}$ (atoms/m$^3$) | $A_0$ (1/s)              | $E_A$ (eV) | $T$ (K)|
| ------ | -------------------- | ----------------------- | ----------------------------------- | ------------------------ | ---------- | ------ |
| Trap 1 | 8.9 $\times 10^{-5}$ | 9.0 $\times 10^{26}$    | 6.9 $\times 10^{25}$                | 6.18 $\times 10^{-3}$    | 0.24       | 800    |
| Trap 2 | 8.9 $\times 10^{-5}$ | 4.2 $\times 10^{26}$    | 7.0 $\times 10^{25}$                | 6.18 $\times 10^{-3}$    | 0.24       | 800    |
| Trap 3 | 8.9 $\times 10^{-5}$ | 2.5 $\times 10^{26}$    | 6.0 $\times 10^{25}$                | 6.18 $\times 10^{-3}$    | 0.30       | 800    |
| Trap 4 | 8.9 $\times 10^{-5}$ | 5.0 $\times 10^{26}$    | 4.7 $\times 10^{25}$                | 6.18 $\times 10^{-3}$    | 0.30       | 800    |
| Trap 5 | 8.9 $\times 10^{-5}$ | 1.0 $\times 10^{26}$    | 2.0 $\times 10^{25}$                | 0                        | -          | 800    |

!table id=val-2f_traps_values caption=Calibrated values of traps parameters for 0.1 dpa from [!cite](dark2024modelling) to match the experimental desorption data.
| Parameter       | Description                             | Value                | Units       | Reference                                         |
| --------------- | --------------------------------------- | -------------------- | ----------- | ------------------------------------------------- |
| $\alpha_{t0}^i$ | Pre-factor of trapping rate coefficient | $\frac{D_0}{6 \cdot (1.1\times 10^{-10})^2}$ | atoms/s | [J-Dark-PhD](https://zenodo.org/records/11085134) |
| $\alpha_{r0}^i$ | Pre-factor of release rate coefficient  | $10^{13}$            | atoms/s     | [J-Dark-PhD](https://zenodo.org/records/11085134) |
| $\epsilon_t^i$  | Trapping energy for all traps           | 0.28                 | eV          | [!cite](dark2024modelling)                        |
| $\epsilon_r^1$  | Release energy for trap 1               | 1.15                 | eV          | [!cite](dark2024modelling)                        |
| $\epsilon_r^2$  | Release energy for trap 2               | 1.35                 | eV          | [!cite](dark2024modelling)                        |
| $\epsilon_r^3$  | Release energy for trap 3               | 1.65                 | eV          | [!cite](dark2024modelling)                        |
| $\epsilon_r^4$  | Release energy for trap 4               | 1.85                 | eV          | [!cite](dark2024modelling)                        |
| $\epsilon_r^5$  | Release energy for trap 5               | 2.05                 | eV          | [!cite](dark2024modelling)                        |
| $\epsilon_r^6$  | Release energy for intrinsic trap       | 1.04                 | eV          | [!cite](dark2024modelling)                        |
| $N_1$           | Density for trap 1                      | 4.63$\times 10^{25}$ | atoms/m$^3$ | [eq:trapping_sites_density_sol]                   |
| $N_2$           | Density for trap 2                      | 2.87$\times 10^{25}$ | atoms/m$^3$ | [eq:trapping_sites_density_sol]                   |
| $N_3$           | Density for trap 3                      | 1.96$\times 10^{25}$ | atoms/m$^3$ | [eq:trapping_sites_density_sol]                   |
| $N_4$           | Density for trap 4                      | 2.97$\times 10^{25}$ | atoms/m$^3$ | [eq:trapping_sites_density_sol]                   |
| $N_5$           | Density for trap 5                      | 7.87$\times 10^{24}$ | atoms/m$^3$ | [eq:trapping_sites_density_sol]                   |
| $N_6$           | Density for intrinsic trap              | 2.4$\times 10^{22}$  | atoms/m$^3$ | [!cite](dark2024modelling)                        |

!media comparison_val-2f.py
        image_name=val-2f_trap_induced_density.png
        style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
        id=val-2f_trap_induced_density
        caption=Trap densities as a function of damage. The analytical solutions are represented by the solid curve, while the points indicate the fitted values used in [!cite](dark2024modelling) at 0.1 dpa.

As described in the boundary conditions section, we use two different approaches for the description of the surface recombination rates. We first impose $C_M = 0$ atoms/m$^3$ to reproduce the results from [!cite](dark2024modelling). However, we also capture the finite kinetics of surface reaction using the recombination rate from [!cite](zhao2020deuterium), which has been increased in this study to better match the TDS data. The values used are listed in [val-2f_recombination_rates]:

!table id=val-2f_recombination_rates caption=Values of recombination rates.
| Parameter | Description                                    | Value                       | Units         | Reference                  |
| --------- | ---------------------------------------------- | --------------------------- | ------------- | -------------------------- |
| $K_r$     | Deuterium recombination coefficient      | 3.8$\times 10^{-26} \exp\left(-\frac{0.34 (\text{eV})}{k_b \cdot T}\right)$ | m$^4$/at/s | [!cite](zhao2020deuterium) |
| $K$       | Adapted deuterium recombination coefficient     | 3.8$\times 10^{-16} \exp\left(-\frac{0.34 (\text{eV})}{k_b \cdot T}\right)$ | m$^4$/at/s | - |

!alert warning title=Typo in formula from [!cite](zhao2020deuterium)
There is a typo in the expression for the deuterium recombination coefficient for clean tungsten surfaces from [!cite](zhao2020deuterium) where the minus sign in the exponential is missing, even though the data shows it should be present. Consequently, we used the corrected value in our simulations, which includes the minus sign.

## Results

The figures below show the comparison of the TMAP8 calculation and the experimental data during desorption. The experimental data are provided by T. Schwarz-Selinger and are available [here](https://zenodo.org/records/11085134).

We first reproduce the results from [!cite](dark2024modelling) using a Dirichlet boundary condition at the surface and using the calibrated trapping properties from [val-2f_traps_values]. [val-2f_deuterium_desorption_inf_recombination] displays the quantities of mobile, trapped, and desorbing deuterium atoms during the desorption process. During desorption, the temperature increases from 300 K to 1000 K. The amount of deuterium trapped will decrease as the temperature rises and the various trapping energies are reached, meaning that deuterium will leave the traps, become mobile, and diffuse out. During desorption, no further implantation occurs, resulting in a decrease in the number of mobile and trapped deuterium atoms and an increase in the number of desorbed deuterium atoms.

Mass conservation in [val-2f_deuterium_desorption_inf_recombination] is maintained during desorption, with a 0.01% root mean squared percentage error (RMSPE) between the initial number of mobile and trapped deuterium atoms and the total number of deuterium atoms (mobile, trapped, and desorbed).

[val-2f_comparison_inf_recombination] shows a good alignment with the experimental data and the results presented in [!cite](dark2024modelling). With an infinite recombination rate, the amount of mobile deuterium is minimal compared to the trapped deuterium, as demonstrated in [val-2f_deuterium_desorption_inf_recombination]. Consequently, the desorbed deuterium flux is almost solely due to the deuterium desorbing from the traps.

!media comparison_val-2f.py
       image_name=val-2f_deuterium_desorption_inf_recombination.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=val-2f_deuterium_desorption_inf_recombination
       caption=Quantity of deuterium atoms during the desorption process for an infinite recombination rate and calibrated trapping properties.

!media comparison_val-2f.py
       image_name=val-2f_comparison_inf_recombination.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=val-2f_comparison_inf_recombination
       caption=Comparison of TMAP8 calculations with experimental data on deuterium flux (atoms/m$^2$/s) for a damage of 0.1 dpa, an infinite recombination rate and calibrated trapping properties.

In this validation case, the recombination rate has been set to a finite value to better reflect real conditions. Specifically, the recombination rate is set to a value 10 orders of magnitude higher than that reported by [!cite](zhao2020deuterium). A recombination rate that is too low leads to the accumulation of a significant amount of mobile deuterium at the onset of the desorption phase. Consequently, this would result in desorption being attributed to mobile deuterium rather than trapped deuterium. The updated, increased recombination rate limits deuterium accumulation in the sample, without imposing a surface concentration.
As shown in [val-2f_deuterium_desorption], the quantity of mobile deuterium is nearly equal to zero, similar to the case with an infinite recombination rate, and mass conservation is maintained. The TMAP8 results in [val-2f_comparison] match well with the experimental data. There still exists an offset between the TMAP8 results and the experimental data, which can be reduced by better fitting the recombination rate and trapping parameters described in [val-2f_traps_values] using the [MOOSE's stochastic tools module](https://mooseframework.inl.gov/modules/stochastic_tools/index.html).
It is important to mention here that the mesh for the infinite recombination rate requires a finer mesh as well as smaller time steps compared to the finite recombination rate case.

!media comparison_val-2f.py
       image_name=val-2f_deuterium_desorption.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=val-2f_deuterium_desorption
       caption=Quantity of deuterium atoms during the desorption process for an adapted recombination rate and uncalibrated trapping properties.

!media comparison_val-2f.py
       image_name=val-2f_comparison.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=val-2f_comparison
       caption=Comparison of TMAP8 calculations with experimental data on deuterium flux (atoms/m$^2$/s) for a damage of 0.1 dpa, an adapted recombination rate and uncalibrated trapping properties.

## Input files

!style halign=left
The input file for this case can be found at [!file](/val-2f.i). To minimize the length of the input file and organize it, it is divided into several parts:

- [!file](/parameters_val-2f.params) lists the key values and model parameters used in this simulation
- [!file](/val-2f_trapping_intrinsic.i) provides the blocks necessary to introduce the intrinsic traps in the simulation
- [!file](/val-2f_trapping_1.i), [!file](/val-2f_trapping_2.i), [!file](/val-2f_trapping_3.i), [!file](/val-2f_trapping_4.i), [!file](/val-2f_trapping_5.i) provide the blocks necessary to introduce the trapping sites 1, 2, 3, 4, and 5, respectively, in the simulation.

To combine them into one input file when running the simulation, [!file](/val-2f.i) uses the `!include` feature.

!alert tip title=Input file include syntax information
To learn more about the `!include` feature, refer to the [application_usage/input_syntax.md] page.

Note that both surface conditions can be modeled using [!file](/val-2f.i). By running it as is, the recombination condition with the updated recombination rate is utilized. [!file](/val-2f/tests) used `cli_args` to modify [!file](/val-2f.i) into using the effectively infinite recombination rate at the surface and impose a null concentration at the surfaces.

To limit the computational costs of the test case, the test runs a version of the file with a smaller and coarser mesh, and fewer time steps. In addition, this validation case includes tests using two time integration schemes. The `implicit-euler` scheme (first-order, single-step) provides higher stability and consistency of the solution across different operating systems and processor core counts, making it better suited for use in Bayesian optimization workflows where numerical stability is important. The `bdf2` scheme (second-order, multi-step) provides higher accuracy and is used for final results calculation. Both schemes are tested for this validation case in [!file](/val-2f/tests). More information about the changes can be found in the test specification file for this case, namely [!file](/val-2f/tests).
