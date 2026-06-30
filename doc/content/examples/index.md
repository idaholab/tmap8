# Examples

Inputs which demonstrate potential applications for TMAP8 capabilities,
along with walk-through guides which should in theory allow users to
leverage prior work.

## Fuel cycles from [Abdou et al.](examples/fuel_cycle_Abdou/index.md) and [Meschini et al.](examples/fuel_cycle_Meschini/index.md)

Because TMAP8 is built on MOOSE, it brings MOOSE's capacity to solve ordinary differential
equations using [ScalarKernels](syntax/ScalarKernels/index.md). These can be quite useful to
model parts of the system at high levels of abstraction while working with detailed
models of specific components.
As examples, we propose two fuel cycle models.
[The first model](examples/fuel_cycle_Abdou/index.md) re-creates the fuel cycle model described in [!cite](Abdou2021) as a high-level abstraction of a fuel cycle in a potential fusion power plant.
[The second model](examples/fuel_cycle_Meschini/index.md) re-creates the fuel cycle model described in [!cite](meschini2023modeling), which models the tritium fuel cycle for ARC-and STEP-class DT fusion power plants.

!content location=fuel_cycle


## [Divertor Monoblock](examples/divertor_monoblock/index.md)

TMAP8 is used to model tritium transport in a divertor monoblock to elucidate the effects of pulsed operation (up to fifty 1600-second plasma discharge and cool-down cycles) on the tritium in-vessel inventory source term and ex-vessel release term (i.e., tritium retention and permeation) for safety analysis. This example reproduces the results presented in [!cite](Shimada2024114438).

A series of sensitivity studies were performed on the [Divertor Monoblock](examples/divertor_monoblock/index.md) model including:  (1) steady-pulse operation, (2) a shutdown transient, and (3) a ELM transient [Divertor Monoblock Sensitivity](divertor_monoblock/sensitivity.md).

## [Pore-Scale Tritium Transport in Imported Microstructures](examples/pore_scale_transport/index.md)

This example demonstrates TMAP8's capability to (1) generate pore structures from input images,
and (2) perform pore-scale simulations of tritium transport on these pore structures based on the model described in [!cite](Simon2022).
This example highlights the effect of pore interconnectivity on tritium transport.

## [Hydrogen Transport in Aluminum-Clad Used Nuclear Fuel (AUNF) Mini-Canister Storage](examples/mini_canister/index.md)

TMAP8 is used to model hydrogen transport and permeation through AUNF storage. The storage device considered is a 304 stainless steel mini-canister from Savannah River National Laboratory (SRNL). This example highlights the use of TMAP8-specific features, such as interface kernels and boundary conditions, applied to industry-relevant technologies.
