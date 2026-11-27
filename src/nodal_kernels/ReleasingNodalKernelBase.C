/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2025 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#include "ReleasingNodalKernelBase.h"

InputParameters
ReleasingNodalKernelBase::validParams()
{
  InputParameters params = NodalKernel::validParams();
  params.addParam<Real>("detrapping_energy", 0, "The detrapping energy (K)");
  params.addRequiredCoupledVar("temperature", "The temperature (K)");
  return params;
}

ReleasingNodalKernelBase::ReleasingNodalKernelBase(const InputParameters & parameters,
                                                   Real release_rate_coefficient)
  : NodalKernel(parameters),
    _release_rate_coefficient(release_rate_coefficient),
    _detrapping_energy(getParam<Real>("detrapping_energy")),
    _temperature(coupledValue("temperature")),
    _temperature_var(coupled("temperature"))
{
}

Real
ReleasingNodalKernelBase::computeQpResidual()
{
  return _release_rate_coefficient * std::exp(-_detrapping_energy / _temperature[_qp]) * _u[_qp];
}

Real
ReleasingNodalKernelBase::computeQpJacobian()
{
  return _release_rate_coefficient * std::exp(-_detrapping_energy / _temperature[_qp]);
}

Real
ReleasingNodalKernelBase::computeQpOffDiagJacobian(unsigned int jvar)
{
  // The residual is proportional to exp(-E_r / T), so dR/dT = R * E_r / T^2.
  if (jvar == _temperature_var)
    return computeQpResidual() * _detrapping_energy / (_temperature[_qp] * _temperature[_qp]);

  return 0;
}
