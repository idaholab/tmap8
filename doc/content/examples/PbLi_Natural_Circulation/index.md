# Lead-Lithium Eutectic Natural Circulation Model

This example demonstrates the use of MOOSE's Thermal Hydraulics Module (THM) [Path-Integrated Incompressible Flow Model](modules/thermal_hydraulics/theory_manual/path_integrated_incompressible_model/index.md) to simulate buoyancy-driven, pump-free natural circulation of a lead-lithium (PbLi) eutectic coolant. The example reproduces a thermal convection loop (TCL) constructed at Oak Ridge National Laboratory (ORNL) to study the compatibility of an FeCrAl structural alloy with flowing PbLi [!citep](pawel2017fecral), and compares TMAP8 results against both the ORNL experimental measurements and a RELAP5-3D model of the same loop developed at the University of Tennessee-Knoxville (UTK) [!citep](meehan2022relap53d). PbLi is a leading breeder/coolant candidate for dual-coolant lead-lithium (DCLL) fusion blankets because of its high tritium breeding capability and favorable thermal properties, so correctly capturing natural circulation in PbLi systems is relevant to blanket thermal-hydraulic design.

Two input files are provided:

1. [!file](PbLi_Loop_steady.i) — solves directly for the steady, fully-developed natural-circulation state of the loop.
2. [!file](PbLi_Loop_transient.i) — starts the loop at a uniform initial temperature and marches in time toward the same steady state, demonstrating transient start-up behavior.

The two files share an identical geometry, material model, and boundary conditions; [!file](PbLi_Loop_transient.i) only adds time-derivative kernels on every scalar variable and uses a [Transient](executioners/Transient.md) executioner in place of [Steady](executioners/Steady.md) (see [#executioner]).

## Experimental Loop Description

!style halign=left
The ORNL TCL is a rectangular loop fabricated entirely from APMT (Fe-21Cr-5Al-3Mo), an iron-chromium-aluminum (FeCrAl) alloy, filled with eutectic Pb-17at.%Li [!citep](pawel2017fecral). As shown in [fig:loop_schematic], the loop forms a rectangle with two near-vertical "legs," each about 0.71 m tall, spaced about 0.495 m apart, connected by two near-horizontal legs, each about 0.495 m long, that are sloped at approximately a 1:4 ratio rather than running perfectly level [!citep](pawel2017fecral). Clamshell heaters heat the hot leg and part of the horizontal legs, while the remaining portions of the loop, including the entire cold leg, are unheated and only lightly insulated, losing heat passively to the ambient environment; the resulting temperature difference between the hot and cold legs creates a density gradient that drives natural circulation of the PbLi without any pump. The loop operated continuously for 1000 h at a measured peak (hot leg) temperature of about 550 $^\circ$C and a flow velocity, estimated from hot-spot transit-time tests, of approximately $-0.0067$ m/s [!citep](pawel2017fecral).

!media plot_comparison.py
  image_name=PbLi_Loop.png
  id=fig:loop_schematic
  caption=TMAP8 transient temperature predictions at the top and bottom of the hot and cold legs of the PbLi natural circulation loop as the system evolves from the uniform initial condition toward the steady state summarized in [#results].
  style=width:70%;margin-bottom:2%;margin-left:auto;margin-right:auto;

[!cite](meehan2022relap53d) built a RELAP5-3D model of this same ORNL loop as part of a broader validation effort for transient thermal-hydraulic analysis of DCLL fusion blankets. [tab:loop_params] lists the loop geometry, PbLi thermal properties, and derived boundary conditions reported by [!cite](meehan2022relap53d) that are used directly in the TMAP8 model below.

!table id=tab:loop_params caption=PbLi loop nodalization parameters, adapted from Table 1 of [!cite](meehan2022relap53d).
| Parameter | Value | Units |
| :-- | :-- | :-- |
| Horizontal leg spacing, $L_x$ | 0.495 | m |
| Vertical leg spacing, $L_y$ | 0.71 | m |
| Horizontal leg slope | 1:4 | n/a |
| Pipe inner diameter | 0.0267 | m |
| Pipe wall thickness | 0.0031 | m |
| Loop average temperature | 745 | K |
| Horizontal leg heater power, $Q_{horiz}$ | 129.9 | W |
| Vertical leg heater power, $Q_{vert}$ | 558.9 | W |
| Forms loss coefficient, $K$ | 58.0 | n/a |
| Effective ambient heat transfer coefficient, $h_\infty$ | 12.0 | W/(m$^2$ K) |

## Nomenclature

!style halign=left
[tab:variables] lists the scalar variables used in this example, each repeated once per flow segment ($i = 01, \ldots, 40$ for fluid and inner/outer wall temperatures). All forty segments share the same mass flow rate and characteristic pressure drop.

!table id=tab:variables caption=Nomenclature of scalar variables.
| Variable | Description | Units |
| :-- | :-- | :-- |
| `m1` | Loop mass flow rate, $\dot{m}$ (shared by every segment) | kg/s |
| `dPc` | Characteristic pressure drop around the loop, $\Delta P_c$ | Pa |
| `T01`-`T40` | Fluid temperature of segment $i$, $T_i$ | K |
| `Twi01`-`Twi40` | Inner-surface pipe wall temperature of segment $i$, $T_{i,w}$ | K |
| `Two01`-`Two40` | Outer-surface pipe wall temperature of segment $i$, $T_{o,w}$ | K |

## Geometry and Discretization

!style halign=left
The loop is discretized into 40 equal-length segments: 20 segments form the cold leg (`T01`-`T20`), and 20 form the hot leg (`T21`-`T40`), matching the control-volume layout used by [!cite](meehan2022relap53d). Each leg alternates ten near-horizontal segments (sloped at $\arctan(0.25)$ from horizontal) and ten vertical segments, so that the fluid travels around the full rectangular path and back to its starting point; segment 40 feeds back into segment 1 (`outlet_temperature = T01` in `[temp40]`), closing the loop. The pipe cross-section is circular, and the stainless pipe wall is subdivided radially into an inner-surface node and an outer-surface node to capture the radial temperature gradient (conjugate heat transfer), following the [Conjugate Heat Transfer](modules/thermal_hydraulics/theory_manual/path_integrated_incompressible_model/index.md#conjugate-heat-transfer) formulation of the Path-Integrated Incompressible Flow Model. The mesh itself is not used to represent the flow network: because `ScalarVariables` require no mesh connectivity, the model places all physics in `[ScalarKernels]`, and the single-element mesh exists only because MOOSE requires one to be defined:

!listing test/tests/PbLi_Natural_Circulation/PbLi_Loop_steady.i block=Mesh link=false

[!param](/Problem/allow_invalid_solution) is set to `true` because, in the course of Newton iteration toward the natural-circulation steady state, the solver may transiently evaluate the [LeadLithiumFluidProperties](LeadLithiumFluidProperties.md) object outside its strict range of validity before converging back inside it.

## Fluid and Solid Properties

!style halign=left
The PbLi fluid properties used by the scalar kernels are supplied by [LeadLithiumFluidProperties](LeadLithiumFluidProperties.md), which provides density, viscosity, specific heat, and thermal conductivity as functions of temperature based on compilations in the literature [!citep](Schulz1991,Zinkle1998,MasdeLesValls2008). A separate `rhof` [ParsedFunction](ParsedFunction.md), matching the linear PbLi density correlation reported by [!cite](meehan2022relap53d), is used only by the `rhoave` and `flow_velocity` postprocessors (see [#results]) to convert the predicted mass flow rate into a flow velocity for comparison with experiment. The pipe wall material (APMT) is represented with a [ThermalFunctionSolidProperties](ThermalFunctionSolidProperties.md) object, with its temperature-dependent thermal conductivity and specific heat given by [PiecewiseLinear](PiecewiseLinear.md) functions fit from room temperature up to 1473.15 K, and a constant density of 7250 kg/m$^3$:

!listing test/tests/PbLi_Natural_Circulation/PbLi_Loop_steady.i block=Functions link=false

!listing test/tests/PbLi_Natural_Circulation/PbLi_Loop_steady.i block=FluidProperties link=false

!listing test/tests/PbLi_Natural_Circulation/PbLi_Loop_steady.i block=SolidProperties link=false

## Governing Equations and Scalar Kernels

!style halign=left
This example solves the discretized form of the Path-Integrated Incompressible Flow Model's governing equations, as derived in the [theory manual](modules/thermal_hydraulics/theory_manual/path_integrated_incompressible_model/index.md). Four coupled physics are modeled, each handled by a dedicated family of [ScalarKernels](syntax/ScalarKernels/index.md):

1. **Loop momentum balance.** The cold leg (segments `T01`-`T20`) uses [ADIncompressibleMomentumSPScalarKernel](IncompressibleMomentumSPScalarKernel.md) to solve for the shared mass flow rate `m1`, while the hot leg (segments `T21`-`T40`) uses the complementary [ADCoupledPressureIncompressibleMomentumSPScalarKernel](CoupledPressureIncompressibleMomentumSPScalarKernel.md) to solve for the characteristic pressure drop `dPc`, closing the loop into a single circuit. For every horizontal segment, [!param](/ScalarKernels/IncompressibleMomentumSPScalarKernel/forms_losses) is zero, while every vertical segment carries the forms loss coefficient $K=58.0$ listed in [tab:loop_params] to represent the flow resistance of the tungsten specimen-chain spacers described by [!cite](pawel2017fecral) and quantified by [!cite](meehan2022relap53d) from a COMSOL parametric study. No pump pressure is applied ([!param](/ScalarKernels/IncompressibleMomentumSPScalarKernel/pump_pressures) is zero everywhere) because circulation in this loop is driven entirely by buoyancy, through the $\rho_i g L_i \sin\alpha_i$ term:

   !listing test/tests/PbLi_Natural_Circulation/PbLi_Loop_steady.i block=ScalarKernels/cold_leg link=false

2. **Segment energy balance.** Each fluid segment's temperature is governed by [ADIncompressibleEnergySPScalarKernel](IncompressibleEnergySPScalarKernel.md), which advances the fluid temperature using the upstream/downstream neighbor temperatures, the shared mass flow rate, and convective heat exchange with that segment's inner wall node:

   !listing test/tests/PbLi_Natural_Circulation/PbLi_Loop_steady.i block=ScalarKernels/temp1 link=false

3. **Inner wall conjugate heat transfer.** [ADPipeInnerWallTemperatureScalarKernel](PipeInnerWallTemperatureScalarKernel.md) solves for each segment's inner wall surface temperature from radial conduction to the outer wall node, axial conduction to the neighboring inner wall nodes, and convection with the fluid:

   !listing test/tests/PbLi_Natural_Circulation/PbLi_Loop_steady.i block=ScalarKernels/innerwalltemp1 link=false

4. **Outer wall boundary condition.** Depending on location, each segment's outer wall node uses one of two kernels: [ADPipeOuterWallHeatFluxScalarKernel](PipeOuterWallHeatFluxScalarKernel.md) applies the clamshell heater power as an imposed heat flux on the heated hot-leg and part of the horizontal segments, while [ADPipeOuterWallAmbientTemperatureScalarKernel](PipeOuterWallAmbientTemperatureScalarKernel.md) applies convective cooling to ambient air (at $T_\infty = 293.15$ K and $h_\infty = 12.0$ W/(m$^2$ K), from [tab:loop_params]) elsewhere, including along the entire cold leg:

   !listing test/tests/PbLi_Natural_Circulation/PbLi_Loop_steady.i block=ScalarKernels/outerwalltemp21 link=false

   !listing test/tests/PbLi_Natural_Circulation/PbLi_Loop_steady.i block=ScalarKernels/outerwalltemp1 link=false

   The applied heat flux is computed from the total heater power and the perimeter and length of the heated segment, for example for the horizontal legs:

   !listing test/tests/PbLi_Natural_Circulation/PbLi_Loop_steady.i start=Q_horiz = 129.9 end=chains_loss = 58.0 link=false

Each physical quantity ([!param](/ScalarKernels/IncompressibleMomentumSPScalarKernel/areas), [!param](/ScalarKernels/IncompressibleMomentumSPScalarKernel/lengths), perimeters, etc.) is derived once at the top of the input file from the pipe inner diameter and wall thickness in [tab:loop_params], then supplied identically to every one of the 40 repeated momentum, energy, and wall-temperature kernels.

## Executioner id=executioner

!style halign=left
[!file](PbLi_Loop_steady.i) uses a [Steady](executioners/Steady.md) executioner with full Newton iteration to directly solve for the steady-state natural-circulation condition:

!listing test/tests/PbLi_Natural_Circulation/PbLi_Loop_steady.i block=Executioner link=false

[!file](PbLi_Loop_transient.i) is identical except that an [ADScalarTimeDerivative](ADScalarTimeDerivative.md) (or, for the pressure-drop variable `dPc`, a [CoupledODETimeDerivative](CoupledODETimeDerivative.md)) is added for every scalar variable, and the executioner is switched to [Transient](executioners/Transient.md), starting the simulation at a uniform `initial_temperature` of 745 K and marching to a `end_time` of 1800 s using an [IterationAdaptiveDT](timesteppers/IterationAdaptiveDT.md) timestepper:

!listing test/tests/PbLi_Natural_Circulation/PbLi_Loop_transient.i block=Executioner link=false

## Results

!style halign=left id=results
[fig:loop_schematic] shows the predicted fluid temperature at the top and bottom of the hot and cold legs over the course of the transient simulation, as it rises from the uniform 745 K initial condition toward the loop's steady-state temperature distribution. By the end of either simulation, the top of the hot leg (`T40`) reaches about 805 K and the bottom of the cold leg (`T20`) settles near 702 K, giving a hot-to-cold temperature difference consistent with the roughly 100 K gradient reported for the experiment.

The input files include a set of [Postprocessors](syntax/Postprocessors/index.md) that evaluate the TMAP8 prediction directly against both the RELAP5-3D model and the ORNL experimental measurements reported in Table 2 of [!cite](meehan2022relap53d):

!listing test/tests/PbLi_Natural_Circulation/PbLi_Loop_steady.i block=Postprocessors/RELAP_comp_Tlow link=false

!listing test/tests/PbLi_Natural_Circulation/PbLi_Loop_steady.i block=Postprocessors/experiment_comp_Tlow link=false

[tab:results] summarizes the steady-state comparison. TMAP8 shows good agreement with both the ORNL experimental data and the independent RELAP5-3D model, which were themselves within a few percent of each other, confirming that the Path-Integrated Incompressible Flow Model correctly captures the buoyancy-driven circulation and temperature distribution of this numerically challenging, conceptually simple natural circulation loop.

!table id=tab:results caption=Comparison of steady-state TMAP8 predictions against the RELAP5-3D model and ORNL experimental measurements reported by [!cite](meehan2022relap53d).
| Quantity | TMAP8 | RELAP5-3D | Experiment |
| :-- | :-- | :-- | :-- |
| Bottom of cold leg temperature, `T20` [K] | 702.6 | 708.1 | 707.5 |
| Top of hot leg temperature, `T40` [K] | 805.6 | 827.7 | 823.2 |
| Flow velocity [m/s] | 0.0065 | 0.0065 | 0.0067 |

## Input Files

!style halign=left
The complete input files for this example are [!file](/PbLi_Loop_steady.i) and [!file](/PbLi_Loop_transient.i).

!listing test/tests/PbLi_Natural_Circulation/PbLi_Loop_steady.i

!listing test/tests/PbLi_Natural_Circulation/PbLi_Loop_transient.i

!bibtex bibliography
