# ADMatReactionFlexible

!syntax description /Kernels/ADMatReactionFlexible

## Overview

This class adds to the residual a contribution from

\begin{equation}
\frac{dc_0}{dt} = \alpha K \prod_{i}{c_i}
\end{equation}

where $c_i$ are species concentrations provided as nonlinear or coupled variables, $\alpha$ is a constant coefficient, and $K$ is a material property. $\alpha$ can be used to include the stoichiometry of a reaction for specific species. For example, for a reaction such as
\begin{equation}
X \rightarrow 2Y,
\end{equation}
$K$ would be the same for both species, but $\alpha$ would be defined as `-1` for species X, and as `2` for species Y.

The product of the variables listed in `vs` is computed with automatic differentiation, so the Jacobian includes the derivatives with respect to every listed variable, including the kernel's own variable. Variables that are listed in `vs` but are `AuxVariables` are lagged, and their dependence on the nonlinear variables is not included in the Jacobian.

!syntax parameters /Kernels/ADMatReactionFlexible

!syntax inputs /Kernels/ADMatReactionFlexible

!syntax children /Kernels/ADMatReactionFlexible
