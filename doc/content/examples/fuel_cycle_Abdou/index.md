# Fuel Cycle

This demonstration re-creates the tritium fuel cycle model described by [!cite](Abdou2021). It is also described in [!cite](Simon2025).

There are multiple ways to generate an input file that uses scalar kernels. The [`ParsedODEKernel`](scalarkernels/ParsedODEKernel.md)
and [`ODETimeDerivative`](scalarkernels/ODETimeDerivative.md) can be used to deal with almost any system of ordinary differential equations,
but there is also a utility class [`FuelCycleSystemScalarKernel`](scalarkernels/FuelCycleSystemScalarKernel.md) which can be used to 
simplify the inputs.

### Generating the Input File

First, we instantiate a mesh

!listing test/tests/fuel_cycle_Abdou/fuel_cycle.i link=false block=Mesh

For our purposes this does nothing, but MOOSE requires a defined mesh as a placeholder to run the rest of the simulation.

Next, we need to define our system. Following the convention in [!cite](Abdou2021), we have 11 modeled systems, each with
their own ODE and tritium inventory:

!table id=tritsystems caption=Systems and labels used in this example.
| System Name | System Number | Tritium Inventory Variable| System Equation |
| --- | --- | --- | --- |
| Breeding zone | 1 | `T_01_BZ` | [eqn:t1] |
| Tritium Extraction System | 2 | `T_02_TES` | [eqn:t2] |
| First Wall | 3 | `T_03_FW` | [eqn:t3] |
| Divertor | 4 | `T_04_DIV` | [eqn:t4] |
| Heat Exchanger | 5 | `T_05_HX` | [eqn:t5] |
| Coolant Purification System | 6 | `T_06_CPS` | [eqn:t6] |
| Vacuum Pump | 7 | `T_07_vacuum` | [eqn:t7] |
| Fuel Clean-up  | 8 | `T_08_FCU` | [eqn:t8] |
| Isotope Separation System | 9 | `T_09_ISS` | [eqn:t9] |
| Exhaust and Water Detritiation System | 10 | `T_10_exhaust` | [eqn:t10] |
| Storage and Management | 11 | `T_11_storage` | [eqn:t11] |


\begin{equation}
\label{eqn:t1}
\frac{dI_1}{dt} = \Lambda \dot{N}^{-} + (1-\eta_2)\frac{I_2}{\tau_2} - \frac{I_1}{\tau_1}- \frac{I_1\varepsilon_1}{\tau_1} - I_1\lambda
\end{equation}

\begin{equation}
\label{eqn:t2}
\frac{dI_2}{dt} = (1-f_{1-5})\frac{I_1}{\tau_1} - \frac{I_2}{\tau_2} - \frac{I_2\varepsilon_2}{\tau_2} - I_2\lambda
\end{equation}

\begin{equation}
\label{eqn:t3}
\frac{dI_3}{dt} = f_{p-3}\frac{\dot{N}^{-}}{\eta_f f_b} + f_{5-3}(1-f_{5-6})(1-f_{5-10})\frac{I_5}{\tau_5} + f_{6-3}(1-\eta_6)\frac{I_6}{\tau_6} - \frac{I_3}{\tau_3} - \frac{I_3\varepsilon_3}{\tau_3} - I_3\lambda
\end{equation}

\begin{equation}
\label{eqn:t4}
\frac{dI_4}{dt} = f_{p-4}\frac{\dot{N}^{-}}{\eta_f f_b} + (1-f_{5-3})(1-f_{5-6})(1-f_{5-10})\frac{I_5}{\tau_5} + (1-f_{6-3})(1-\eta_6)\frac{I_6}{\tau_6} - \frac{I_4}{\tau_4} - \frac{I_4\varepsilon_4}{\tau_4}  - I_4\lambda
\end{equation}

\begin{equation}
\label{eqn:t5}
\frac{dI_5}{dt} = f_{1-5}\frac{I_1}{\tau_1}  + \frac{I_3}{\tau_3} + \frac{I_4}{\tau_4} - \frac{I_5}{\tau_5} -\frac{I_5\varepsilon_5}{\tau_5} - I_5\lambda
\end{equation}

\begin{equation}
\label{eqn:t6}
\frac{dI_6}{dt} = f_{5-6}(1-f_{5-10})\frac{I_5}{\tau_5} - \frac{I_6}{\tau_6} - \frac{I_6\varepsilon_6}{\tau_6} - I_6\lambda
\end{equation}

\begin{equation}
\label{eqn:t7}
\frac{dI_7}{dt} = (1-\eta_f f_b - f_{p-3} - f_{p-4})\frac{\dot{N}^{-}}{\eta_f f_b} - \frac{I_7}{\tau_7} - \frac{I_7\varepsilon_7}{\tau_7} - I_7\lambda
\end{equation}

\begin{equation}
\label{eqn:t8}
\frac{dI_8}{dt} = \frac{I_7}{\tau_7} - \frac{I_8}{\tau_8} - \frac{I_8\varepsilon_8}{\tau_8} - I_8\lambda
\end{equation}

\begin{equation}
\label{eqn:t9}
\frac{dI_9}{dt} = (1-f_{8-11})\frac{I_8}{\tau_8} + \frac{I_{10}}{\tau_{10}} + \eta_2 \frac{I_2}{\tau_2} + \eta_6 \frac{I_6}{\tau_6} - \frac{I_9\varepsilon_9}{\tau_9} - \frac{I_9}{\tau_9} - I_9\lambda
\end{equation}
\begin{equation}
\label{eqn:t10}
\frac{dI_{10}}{dt} = f_{5-10}\frac{I_5}{\tau_5} + f_{9-10}\frac{I_9}{\tau_9} - \frac{I_{10}}{\tau_{10}} - \frac{I_{10}\varepsilon_{10}}{\tau_{10}} - I_{10}\lambda
\end{equation}
\begin{equation}
\label{eqn:t11}
\frac{dI_{11}}{dt} = f_{8-11}\frac{I_8}{\tau_8} + (1-f_{9-10})\frac{I_9}{\tau_9} - \frac{\dot{N}^{-}}{\eta_f f_b} - I_{11}\lambda
\end{equation}

!media create_fc_diagram_figure.py
       image_name=fuel_cycle_abdou_generic_AD_fuelcycle.svg
       style=width:100%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=fc_diagram
       caption=Dependency diagram of the fuel cycle system.
[fc_diagram] illustrates the fuel cycle and shows the dependencies between systems.
For an interpretation of these equations and explanations about the notations, readers should refer to [!cite](Abdou2021) (Appendix).
We instantiate the variables in the typical [`Variables`](/syntax/Variables) block, making sure to set the [!param](/Variables/family) attribute to `SCALAR` for each variable.
The default initial condition is zero.

!listing test/tests/fuel_cycle_Abdou/fuel_cycle.i link=false block=Variables

Next we initiate the [`ScalarKernels`](/syntax/ScalarKernels) block. We can model the time-dependent terms with [`ODETimeDerivative`](scalarkernels/ODETimeDerivative.md) objects
and the other terms can be lumped in [`ParsedODEKernel`](scalarkernels/ParsedODEKernel.md) objects. We should have one [`ODETimeDerivative`](scalarkernels/ODETimeDerivative.md)
 and one (or more) [`ParsedODEKernel`](scalarkernels/ParsedODEKernel.md) object(s) per equation above. Internally, TMAP8 will sum the contributions of each object, so we need to
negate the [`ParsedODEKernel`](scalarkernels/ParsedODEKernel.md) equation from its representation above (move it to the left hand side). We use [`Postprocessors`](/syntax/Postprocessors)
to re-use the recurring variables.

!listing test/tests/fuel_cycle_Abdou/fuel_cycle.i link=true block=ScalarKernels

Manually entering equations that describe these systems opens the potential for arithmetical errors, so the [`FuelCycleSystemScalarKernel`](scalarkernels/FuelCycleSystemScalarKernel.md)
 scalar kernel has been created, allowing each system to be modelled with one scalar kernel. Each of the parameters in the scalar kernel is only required to be a [`Functor`](/syntax/Functors), allowing
great flexibility in the kinds of information that can be fed to the scalar kernel. An example model using each approach can be found at `fuel_cycle_abdou.i` and `fuel_cycle_abdou_generic.i`

!listing test/tests/fuel_cycle_Abdou/fuel_cycle_abdou_generic.i link=true block=ScalarKernels

Finally, we define the [`Postprocessors`](/syntax/Postprocessors) and set their values to those referenced in [!cite](Abdou2021). Because the [`Postprocessors`](/syntax/Postprocessors) are
inputs, not outputs, we must be careful to properly set the [!param](/Postprocessors/ConstantPostprocessor/execute_on) parameter. We also gather the values of the different variables in
 separate [`Postprocessors`](/syntax/Postprocessors) and take their sum to obtain the total tritium inventory.

!listing test/tests/fuel_cycle_Abdou/fuel_cycle.i link=false block=Postprocessors


Finally, we can set the [`Executioner`](/syntax/Executioner) block. In this case, we ask for a simple [`Transient`](executioners/Transient.md) executioner with an exponentially growing
[`TimeStepper`](/syntax/Executioner/TimeStepper), [`IterationAdaptiveDT`](timesteppers/IterationAdaptiveDT.md).

!listing test/tests/fuel_cycle_Abdou/fuel_cycle.i link=false block=Executioner

With these blocks set, we can now run the simulation and track tritium inventory.

Implementing a high-fidelity model to replace the default values of specific postprocessors or to more accurately model
specific components is an exercise left for a later date.

### Comparing Results Against Literature

In order to compare against [!cite](Abdou2021), we need to make a few assumptions. First, we set the residence times and other parameters to the values listed in Tables 1-3 of [!cite](Abdou2021)
(the underlined value if there are multiple options). Here we also assume that the "Fuel clean-up and isotope separation system" total residence time of 4 hours as specified in the
paper refers to a residence time of 4 hours for the isotope separation system, and negligible (1 second) residence times for the vacuum pump and fuel clean-up system.

Targeting the black lines of Figure 3 of [!cite](Abdou2021), we also need to determine the appropriate reserve inventory $\frac{\dot{N}^-}{\eta_f f_b}t_r q$, which, given $q=0.25$ and
 $t_r=1\ \text{day}$ comes out to 127.5 kg. With this constraint, we can determine the relevant TBR to obtain a doubling time of 5 years, and iterating by hand, a value of 1.9247 yields a
doubling time of 5 years to three decimal places if `T_11_storage` is given an initial condition of 225.4215 as shown in [!ref](assumptions).

!table id=assumptions caption=Assumptions and iteratively obtained conditions used for this example.
| Parameter | Value |
| --- | --- |
| `residence7` ($\tau_7$) | 1 s |
| `residence8` ($\tau_8$) | 1 s |
| `residence9` ($\tau_9$) | 14400 s |
| `TBR` ($\Lambda$) | 1.9247 |
| Initial value for `T_11_storage` | 225.4215 kg |



We compare our results with those from the black lines in Figure 3 from [!cite](Abdou2021) in [comparison]. The lighter lines are estimates of the values shown in the paper,
and the darker lines are the results from the model. The agreement is quite good, with only a slight deviation for the tritium extraction system inventory as it transitions to a steady-state value.

!media plot_comparison.py
       image_name=fuel_cycle_abdou_03.png
       style=width:50%;margin-bottom:2%;margin-left:auto;margin-right:auto
       id=comparison
       caption=Tritium inventories of specific systems as a function of time. Shaded regions are best estimate of Figure 3 in [!cite](Abdou2021).

!listing test/tests/fuel_cycle_Abdou/fuel_cycle.i

#### How to run

This example can be run from three different driver input files: an explicit model, [!file](tests/fuel_cycle_Abdou/fuel_cycle.i), using [`ParsedODEKernel`](scalarkernels/ParsedODEKernel.md), and two class-based models which leverage [`FuelCycleSystemScalarKernel`](scalarkernels/FuelCycleSystemScalarKernel.md), one with automatic differentiation, [!file](tests/fuel_cycle_Abdou/fuel_cycle_abdou_generic_AD.i), and one without automatic differentiation, [!file](tests/fuel_cycle_Abdou/fuel_cycle_abdou_generic.i). As there is significant overlap between the two models, they both use the `!include` syntax to import common terms from the base file [!file](tests/fuel_cycle_Abdou/fuel_cycle_abdou_base.i).

### Python-based Interactive Script

A python-based graphical interactive script is available at [!file](/test/tests/fuel_cycle_Abdou/fuel_cycle_gui.py) as a demonstration of the various effects of
individual parameters. To use it, navigate to the scripts directory and run the script. All of the input parameters for the model can be changed by editing the associated entry,
then clicking the "Run" button. Once the simulation has run, checkboxes will appear for each system-level tritium inventory. Time units can also be adjusted by selecting the appropriate
timescale.

!bibtex bibliography
