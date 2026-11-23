/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2025 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#include "TrappingNodalKernelBase.h"
#include "Function.h"

InputParameters
TrappingNodalKernelBase::validParams()
{
  InputParameters params = NodalKernel::validParams();
  params.addParam<Real>("trapping_energy", 0, "The trapping energy (K)");
  params.addRequiredParam<Real>("N", "The atomic number density of the host material (1/m^3)");
  params.addRequiredParam<FunctionName>(
      "Ct0", "The fraction of host sites that can contribute to trapping as a function (-)");
  params.addRequiredCoupledVar("mobile_concentration",
                               "The variable representing the mobile concentration of solute "
                               "particles.");
  params.addCoupledVar("other_trapped_concentration_variables",
                       "Other variables representing trapped particle concentrations.");
  params.addRequiredCoupledVar("temperature", "The temperature (K)");
  return params;
}

TrappingNodalKernelBase::TrappingNodalKernelBase(const InputParameters & parameters,
                                                 Real trapping_rate_coefficient,
                                                 Real residual_denominator)
  : NodalKernel(parameters),
    _trapping_rate_coefficient(trapping_rate_coefficient),
    _trapping_energy(getParam<Real>("trapping_energy")),
    _N(getParam<Real>("N")),
    _Ct0(getFunction("Ct0")),
    _mobile_concentration(coupledValue("mobile_concentration")),
    _n_other_concs(coupledComponents("other_trapped_concentration_variables")),
    _last_node(nullptr),
    _temperature(coupledValue("temperature")),
    _temperature_var(coupled("temperature")),
    _residual_denominator(residual_denominator)
{
}

void
TrappingNodalKernelBase::initializeOccupancyTracking(const std::vector<Real> & other_weights,
                                                     Real self_weight)
{
  mooseAssert(other_weights.size() == _n_other_concs,
              "other occupancy weight count must match coupled concentration count");

  _occupancy_concentrations.resize(1 + _n_other_concs);
  _occupancy_weights.resize(1 + _n_other_concs);
  _var_numbers.resize(2 + _n_other_concs);

  for (const auto i : make_range(_n_other_concs))
  {
    _occupancy_concentrations[i] =
        &coupledValue("other_trapped_concentration_variables", /*comp=*/i);
    _occupancy_weights[i] = other_weights[i];
    _var_numbers[i] = coupled("other_trapped_concentration_variables", i);
  }

  _occupancy_concentrations[_n_other_concs] = &_u;
  _occupancy_weights[_n_other_concs] = self_weight;
  _var_numbers[_n_other_concs] = _var.number();
  _var_numbers[_n_other_concs + 1] = coupled("mobile_concentration");
}

Real
TrappingNodalKernelBase::computeQpResidual()
{
  Real empty_trapping_sites = _Ct0.value(_t, (*_current_node)) * _N;
  for (const auto i : index_range(_occupancy_concentrations))
    empty_trapping_sites -= (*_occupancy_concentrations[i])[_qp] * _occupancy_weights[i];

  return -_trapping_rate_coefficient * std::exp(-_trapping_energy / _temperature[_qp]) *
         empty_trapping_sites * _mobile_concentration[_qp] / _residual_denominator;
}

void
TrappingNodalKernelBase::ADHelper()
{
  if (_current_node == _last_node)
    return;

  _last_node = _current_node;

  LocalDN empty_trapping_sites = _Ct0.value(_t, (*_current_node)) * _N;
  for (const auto i : index_range(_occupancy_concentrations))
  {
    LocalDN trap_conc_dn = (*_occupancy_concentrations[i])[_qp];
    trap_conc_dn.derivatives().insert(_var_numbers[i]) = 1.;
    empty_trapping_sites -= trap_conc_dn * _occupancy_weights[i];
  }

  LocalDN mobile_concentration = _mobile_concentration[_qp];
  mobile_concentration.derivatives().insert(_var_numbers.back()) = 1.;

  _jacobian = -_trapping_rate_coefficient * std::exp(-_trapping_energy / _temperature[_qp]) *
              empty_trapping_sites * mobile_concentration / _residual_denominator;
}

Real
TrappingNodalKernelBase::computeQpJacobian()
{
  ADHelper();
  return _jacobian.derivatives()[_var.number()];
}

Real
TrappingNodalKernelBase::computeQpOffDiagJacobian(unsigned int jvar)
{
  // The residual is proportional to exp(-E_t / T), so dR/dT = R * E_t / T^2. Temperature is not
  // part of the AD-seeded variables in ADHelper(), so it is handled analytically here.
  if (jvar == _temperature_var)
    return computeQpResidual() * _trapping_energy / (_temperature[_qp] * _temperature[_qp]);

  if (std::find(_var_numbers.begin(), _var_numbers.end(), jvar) == _var_numbers.end())
    return 0;

  ADHelper();
  return _jacobian.derivatives()[jvar];
}
