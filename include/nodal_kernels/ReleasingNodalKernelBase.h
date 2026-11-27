/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2025 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#pragma once

#include "NodalKernel.h"

/**
 * Shared implementation for trapped-species release nodal kernels.
 *
 * This base class factors the common Arrhenius release residual and Jacobian
 * used by both the dimensional and dimensionless releasing kernels.
 */
class ReleasingNodalKernelBase : public NodalKernel
{
public:
  ReleasingNodalKernelBase(const InputParameters & parameters, Real release_rate_coefficient);

  static InputParameters validParams();

protected:
  Real computeQpResidual() override;
  Real computeQpJacobian() override;
  Real computeQpOffDiagJacobian(unsigned int jvar) override;

  /// Effective release-rate coefficient multiplying the Arrhenius factor and variable value.
  const Real _release_rate_coefficient;
  /// Detrapping activation energy, expressed in Kelvin.
  const Real _detrapping_energy;
  /// Coupled temperature field.
  const VariableValue & _temperature;
  /// Variable number of the coupled temperature (for the analytic temperature Jacobian).
  const unsigned int _temperature_var;
};
