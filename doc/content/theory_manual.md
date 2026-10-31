# Base Theory for TMAP8

This page introduces some of the basic theoretical concepts used in TMAP8.
However, this list is not exhaustive, and users should refer to the publications listed in the [publications.md] (including [!cite](Simon2025)),
the [verification_and_validation/index.md], and the [syntax/index.md] page for a more comprehensive description of capabilities, theoretical concepts, and available objects.

Tritium transport in solid materials can be divided into two main parts: (1) bulk transport in the interior of the materials and
(2) surface reactions.
We succinctly describe how TMAP8 models each part below. For more details on fuel cycle modeling, see [fuel_cycle_Abdou/index.md] or [fuel_cycle_Meschini/index.md].

## Bulk Transport

### Main system of equations (the so-called strong forms)

Bulk transport in TMAP8 can be represented by the generalized equation from McNabb and Foster [!cite](McNabbFoster1963):

\begin{equation}
    \label{eqn:diffusion_mobile_general}
    \frac{dC_M}{dt} = \nabla \cdot \textbf{J}  - k C_{M} + S + \sum_{i=1}^{N_{trap}} \left( \alpha_r^i f_{T/M,i} C_{T_i} -\alpha_t^i  \frac {C_{T_i}^{empty} C_M } {N} \right),
\end{equation}

where $C_M$ is the concentration of the mobile species, $t$ is the time, $\textbf{J}$ is the flux of the mobile species, $k$ is the decay rate constant, and $S$ is the generation term.
The last term on the right-hand side represents trapping and release.
$C_{T_i}$ is the trapped species in trap $i$, $f_{T/M,i}$ is a user-defined numerical factor scaling $C_{T_i}$ to be closer to $C_M$ for better numerical convergence.
$\alpha_r^i$ and $\alpha_t^i$ are the release and trapping rate coefficients for trap $i$, $N$ is the host material density, and $C_{T_i}^{empty}$ is the concentration of empty trapping sites of type $i$, defined as

\begin{equation} \label{eqn:trapping_empty}
    C_{T_i}^{empty} = (C_{{T_i}0} N - f_{T/M,i} C_{T_i}  ) ,
\end{equation}

where $C_{{T_i}0}$ is the fraction of host sites $i$ that can contribute to trapping.
The flux $\textbf{J}$ can be defined as

\begin{equation}
    \label{eqn:diffusion_mobile_general_flux}
    \textbf{J} = D \nabla C_M + D S_T C_M \nabla T
\end{equation}

where $D$ is the diffusivity of the mobile species, $S_T$ is the Soret coefficient, and $T$ is the temperature.
In this instance, the flux accounts for Fickian diffusion and the Soret effect.
Note that other tritium transport mechanisms, including the Nernst-Planck effect [!cite](masliyah2006electrokinetic) and stress-induced diffusion [!cite](SOFRONIS1989317), can also contribute to the flux of mobile species and be included in such a model in TMAP8.

Trapping is a key mechanism of tritium transport, as hydrogen isotopes tend to be captured by small defects in the solid materials, which slows down diffusion and increases retention.
For example, tritium atoms can be trapped in interstitial sites, vacancies, dislocations, grain boundaries, pores, etc. These trapping sites are described with an associated density, which can evolve as a function of space, time, irradiation, etc., as well as rates and energies for trapping and release.
In this kind of tritium transport model, the evolution of the concentration of trapped tritium in each trapping site is governed by, for $i \in [1, N_{trap}]$ with $N_{trap}$ the number of traps,

\begin{equation}
    \label{eqn:trapped_rate_general}
    \frac{dC_{T_i}}{dt} = \alpha_t^i  \frac {C_{T_i}^{empty} C_M } {N f_{T/M,i}} - \alpha_r^i C_{T_i} - k C_{T_i}.
\end{equation}

Note that these equations can also be solved as a dimensionless system with [TrappingNodalKernelDimensionless.md] and [ReleasingNodalKernelDimensionless.md] or, with the physics syntax, [SpeciesTrappingPhysics.md].

Since TMAP8 uses the finite element method to solve this system of equations, it is necessary to derive the weak form of these equations. The derivation of the weak forms of the equations can be found in [!cite](Simon2025) and is reproduced below.

### Derivation of the weak forms of the equations

#### Step 1: Define and rearrange the strong forms of the equations

For clarity, the weak-form derivation below considers the reduced case with no decay, no source term, and no thermal diffusion, i.e. $k = 0$, $S = 0$, and $S_T = 0$.
The reduced strong forms of the governing equations are provided by [eqn:diffusion_mobile_general] and [eqn:trapped_rate_general], and can be rearranged as:

\begin{equation} \label{eqn:diffusion_mobile_step1}
    \frac{\partial C_M}{\partial t} - \nabla \cdot \left( D \nabla C_M \right) + \sum_{i=1}^{N_{trap}} f_{T/M,i} \frac{\partial C_{T_i}}{\partial t} = 0,
\end{equation}
and, for $i \in [1, N_{trap}]$:
\begin{equation} \label{eqn:trapped_rate_step1}
    \frac{\partial C_{T_i}}{\partial t} - \alpha_t^i \frac{C_{T_i}^{\text{empty}} C_M}{(N f_{T/M,i})} + \alpha_r^i C_{T_i} = 0,
\end{equation}
respectively.

#### Step 2: Multiply every term by a test function

Multiply each term of the equations by an appropriate test function $\psi$ (or $\psi_i$ for $C_{T_i}$):

[eqn:diffusion_mobile_step1] becomes
\begin{equation} \label{eqn:diffusion_mobile_step2}
    \psi \frac{\partial C_M}{\partial t} - \psi \nabla \cdot \left( D \nabla C_M \right) + \psi \, \sum_{i=1}^{N_{trap}} f_{T/M,i} \frac{\partial C_{T_i}}{\partial t} = 0,
\end{equation}
and, for $i \in [1, N_{trap}]$, [eqn:trapped_rate_step1] becomes
\begin{equation} \label{eqn:trapped_rate_step2}
    \psi_i \left( \frac{\partial C_{T_i}}{\partial t} - \alpha_t^i \frac{C_{T_i}^{\text{empty}} C_M}{N f_{T/M,i}} + \alpha_r^i C_{T_i} \right) = 0.
\end{equation}

#### Step 3: Integrate over the domain $\Omega$

After integration over the domain, we obtain:

\begin{equation} \label{eqn:diffusion_mobile_step3}
    \int_\Omega \psi \frac{\partial C_M}{\partial t} \, d\Omega - \int_\Omega \psi \nabla \cdot \left( D \nabla C_M \right) \, d\Omega + \int_\Omega \psi \, \sum_{i=1}^{N_{trap}} f_{T/M,i} \frac{\partial C_{T_i}}{\partial t} \, d\Omega = 0,
\end{equation}

and, for $i \in [1, N_{trap}]$,
\begin{equation} \label{eqn:trapped_rate_step3}
    \int_\Omega \psi_i \frac{\partial C_{T_i}}{\partial t} \, d\Omega - \int_\Omega \psi_i \alpha_t^i \frac{C_{T_i}^{\text{empty}} C_M}{N f_{T/M,i}} \, d\Omega + \int_\Omega \psi_i \alpha_r^i C_{T_i} \, d\Omega = 0.
\end{equation}

#### Step 4: Integrate by parts and apply the divergence theorem

For the divergence term in [eqn:diffusion_mobile_step3], applying integration by parts and the divergence theorem provides
\begin{equation}
    \int_\Omega \psi \nabla \cdot \left( D \nabla C_M \right) \, d\Omega = - \int_\Omega \nabla \psi \cdot \left( D \nabla C_M \right) \, d\Omega + \oint\limits_{\partial \Omega} \psi \left( D \nabla C_M \right) \cdot \mathbf{n} \, d\partial \Omega,
\end{equation}
where $\partial \Omega$ is the boundary of the domain and $\mathbf{n}$ is the outward-facing normal vector.

This updated term is then substituted back into [eqn:diffusion_mobile_step3], which leads to:
\begin{equation} \label{eqn:diffusion_mobile_step4}
    \int_\Omega \psi \frac{\partial C_M}{\partial t} \, d\Omega + \int_\Omega \nabla \psi \cdot \left( D \nabla C_M \right) \, d\Omega - \oint\limits_{\partial \Omega} \psi \left( D \nabla C_M \right) \cdot \mathbf{n} \, d\partial \Omega + \int_\Omega \psi \, \sum_{i=1}^{N_{trap}} f_{T/M,i} \frac{\partial C_{T_i}}{\partial t} \, d\Omega = 0.
\end{equation}

Since no divergence terms exist in [eqn:trapped_rate_step3], no integration by parts is needed.

#### Step 5: Derive the final weak form in inner product notation

[eqn:diffusion_mobile_step4] and [eqn:trapped_rate_step3] can be expressed in inner product notation, where $\langle a, b \rangle = \int_\Omega a b \, d\Omega$.

[eqn:diffusion_mobile_step4] becomes
\begin{equation}
    \langle \psi, \frac{\partial C_M}{\partial t} \rangle + \langle \nabla \psi, D \nabla C_M \rangle - \int_{\partial \Omega} \psi \left( D \nabla C_M \right) \cdot \mathbf{n} \, d\Gamma + \langle \psi, \sum_{i=1}^{N_{trap}} f_{T/M,i} \frac{\partial C_{T_i}}{\partial t} \rangle  = 0,
\end{equation}
and, for $i \in [1, N_{trap}]$, [eqn:trapped_rate_step3] becomes
\begin{equation}
    \langle \psi_i, \frac{\partial C_{T_i}}{\partial t} \rangle - \langle \psi_i, \alpha_t^i \frac{C_{T_i}^{\text{empty}} C_M}{N f_{T/M,i}} \rangle + \langle \psi_i, \alpha_r^i C_{T_i} \rangle = 0.
\end{equation}
These weak forms of the equations can now be used for finite element analysis.

It is important to note that other tritium bulk transport models have been developed.
For example, the multi-occupancy trap model enables each trap to capture several hydrogen isotope atoms, knowing that the binding energy of trapping depends on the number and type of other atoms present in the trap.
Atomistic level calculations such as density functional theory studies have shown that several atoms can indeed occupy individual traps, especially larger defects such as pores [!citep](FERNANDEZ2015307,Heinola2010).
Hodille et al. [!cite](Hodille2016), [!cite](Schmid2014), and more recently [!cite](Kaur2025) have deployed multi-occupancy trapping models.
While ongoing efforts are implementing the multi-occupancy model in TMAP8, the current paper uses, verifies, and validates the system of equations described by [eqn:diffusion_mobile_general], [eqn:diffusion_mobile_general_flux], and [eqn:trapped_rate_general].


## Surface Reactions

!style halign=left
At the surface, reactions can be described by several models and assumptions, each with different levels of fidelity or simplicity.
One can assume quasi-steady-state equilibrium at the surface if reaction kinetics are much faster than the kinetics of bulk transport or capture the dissociation and recombination reactions taking place at the material's surface.
TMAP8 can support these different assumptions, as well as convective transport at the surface (see [ver-1ha](ver-1ha.md) and [ver-1hb](ver-1hb.md)).
TMAP7 proposed three main surface conditions, namely `ratedep`, `surfdep`, and `lawdep` [!citep](ambrosek2008verification).
TMAP8 reproduces these models in a more general way, which is detailed below.

### Dissociation and recombination reaction kinetics - Ratedep conditions

!style halign=left
The `ratedep` condition applies when dissociation and recombination reaction kinetics govern the surface reactions [!cite](ambrosek2008verification).
`ratedep` assumes that the generation and release rate of molecules is the product of two or more atom concentrations at the surface and a recombination rate coefficient.
Once formed, molecules immediately leave the surface.

Note that in TMAP8, just like in TMAP7, atoms in the mesh elements closest to the surface contribute to recombination processes.
Atoms deeper in the mesh do not directly contribute to recombinations.
However, if the size of the mesh elements is larger than the size of the lattice, which it usually is, atoms from lattice layers deeper in the materials also contribute to recombinations, as opposed to having only surface atoms contribute.

Under the `ratedep` assumptions, the net flux of atoms of species $s$ into the surface is given by

\begin{equation} \label{eq:flux_rate_dep_net}
J_s = \sum_{m}a_{ms} J_m
\end{equation}

where $m$ denotes different molecules, $a_{ms}$ is the number of atoms of species $s$ in a molecule $m$, and $J_m$ is the flux for a given molecule, defined as

\begin{equation} \label{eq:flux_rate_dep_molecule}
J_m = K_{d_m} P_m - \sum_{i,j} K_{r_m} C_i C_j
\end{equation}

where $K_{d_m}$ is the dissociation rate, $P_m$ is the partial pressure, $K_{r_m}$ is the recombination rate for molecule $m$, and
$C_i$ is the concentration of atomic or complex species $i$.
Note that in TMAP8, additional terms can be added if a molecule contains more than two atoms, which was not possible in TMAP7.
For example, generating H$_2$O was the result of a two-step process, first generating OH and then H$_2$O.
In TMAP8, however, it is possible to either follow TMAP7's approach or directly account for the reaction between an arbitrary number of atomic or complex species.

The following V&V cases, among others, utilize, verify, and validate the `ratedep` conditions: [ver-1ia](ver-1ia.md), [ver-1ib](ver-1ib.md), and [val-2e](val-2e.md).

For example, [ver-1ia](ver-1ia.md) considers the following reaction and model:

!include /ver-1ia.md start=When two species react on a surface to form a third end=This case uses equal starting pressures

### Surface-energy-driven kinetics - Surfdep conditions

!style halign=left
The `surfdep` condition applies when recombination is limited by surface energy.
Following the  `surfdep` model, the production rate to form surface species proceeds as the product of random lateral jumps,
but release is thermally activated and involves the surface binding energy explicitly.
Inversely, the transition from molecules to single atoms is modeled as a two-step process, where molecules are first absorbed by the surface and then dissociate.

When using the `surfdep` approach, the molecular flux across the surface $J_m$ is then given by
\begin{equation} \label{eq:flux_surface_dep_net}
J_m = \frac{P_m}{\sqrt{2 \pi M k_B T}} \exp\left( -\frac{E_x}{k_B T} \right) - C_m \nu_0 \exp\left( -\frac{E_x-E_c}{k_B T} \right)
\end{equation}

where $M$ is the molecular mass,
$E_x$ is the barrier energy for molecular entry to the surface (assumed positive),
$E_c$ is the surface binding energy of molecule $m$,
and $\nu_0$ is the Debye frequency ($\sim$10$^{13}$ s$^{-1}$ for tungsten).

The following V&V cases, among others, utilize and verify the `surfdep` conditions: [ver-1ic](ver-1ic.md) and [ver-1id](ver-1id.md).

For example, [ver-1ic](ver-1ic.md) considers the following reaction and model:

!include /ver-1ic.md start=The problem considers the reaction between end=This case uses equal starting pressures

### Surface Equilibrium - Lawdep conditions

!style halign=left
Both conditions described capture dissociation and recombination reactions, including their kinetics.
However, when the kinetics of the dissociation and recombination processes are much faster than other timescales in the systems (e.g., diffusion), capturing them would likely reduce the required time step and hence increase computational costs without significantly affecting the long-term results.
In that case, it is reasonable to assume that the surface reactions are at a quasi-steady state and set the surface concentrations to their equilibrium values.

In TMAP4 and TMAP7, this is coined the `lawdep` condition.
While TMAP8 does not use this terminology, it supports this quasi-steady-state assumption through the [InterfaceSorption.md] and/or [EquilibriumBC.md] capabilities, which enable both Sieverts' and Henry's law.
Sieverts' law applies when diatomic gases dissociate into individual atoms during dissolution and thermodynamic equilibrium is reached.
Henry's law applies when no dissociation and recombination reactions take place at the interface and equilibrium is reached.

!alert note title=InterfaceKernels vs. Boundary Conditions
Boundary conditions are applied to the boundary of the modeled domain, when the other side of the interface is not being modeled.
For example, the TMAP8 boundary condition applying a sorption law at the boundary is [EquilibriumBC.md].
Interface kernels, however, are applied at interfaces between two subdomains, such as two different materials with different solubilities.
In the case of a sorption law, it also imposes conservation of mass at the interface, as detailed in [InterfaceSorption.md].
Learn more about InterfaceKernels in the [InterfaceKernels/index.md] page.

The following V&V cases, among others, use the quasi-steady-state approximation for surface equilibrium:

- [ver-1ie](ver-1ie.md) and [ver-1if](ver-1if.md),
- [ver-1kb](ver-1kb.md), [ver-1kc-1](ver-1kc-1.md), [ver-1kc-2](ver-1kc-2.md), and [ver-1kd](ver-1kd.md),
- [val-2c](val-2c.md).


!bibtex bibliography
