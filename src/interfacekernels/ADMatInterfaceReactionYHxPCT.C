/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2025 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#include "ADMatInterfaceReactionYHxPCT.h"

#include "TMAP8PhysicalConstants.h"

registerMooseObject("TMAP8App", ADMatInterfaceReactionYHxPCT);

InputParameters
ADMatInterfaceReactionYHxPCT::validParams()

{
  InputParameters params = ADInterfaceKernel::validParams();
  params.addClassDescription(
      "Implements a reaction to establish ReactionRate=k_f*u-k_b*v to compute the surface H "
      "concentration in YHx from the temperature and partial pressure based on the PCT curves with "
      "u the concentration in the solid and v (neighbor) the concentration in the gas in mol/m^3.");
  params.addRequiredCoupledVar(
      "neighbor_temperature",
      "The variable on the other side of the interface for temperature (K).");
  params.addParam<MaterialPropertyName>("density", "density", "Density of the solid in (mol/m^3).");
  params.addParam<MaterialPropertyName>(
      "forward_rate", "kf", "Forward reaction rate coefficient (1/s).");
  params.addParam<MaterialPropertyName>(
      "backward_rate", "kb", "Backward reaction rate coefficient (1/s).");
  params.addParam<bool>(
      "silence_warnings", false, "Whether to silence correlation out of bound warnings");
  return params;
}

ADMatInterfaceReactionYHxPCT::ADMatInterfaceReactionYHxPCT(const InputParameters & parameters)
  : ADInterfaceKernel(parameters),
    _neighbor_temperature(this->template coupledGenericValue<true>("neighbor_temperature")),
    _density(getADMaterialProperty<Real>("density")),
    _kf(getADMaterialProperty<Real>("forward_rate")),
    _kb(getNeighborADMaterialProperty<Real>("backward_rate")),
    _silence_warnings(getParam<bool>("silence_warnings"))
{
}

ADReal
ADMatInterfaceReactionYHxPCT::computeQpResidual(Moose::DGResidualType type)
{
  using std::exp;
  using std::log;
  using std::max;
  using std::pow;
  ADReal r = 0;

  // tolerance for the pressure being closed to the plateau region
  const Real tolerance = 10; // Pa

  // Calculate the equilibrium concentration value based on PCT curve
  // (/2 because two atoms for a molecule) (pressure in Pa)
  auto neighbor_pressure =
      PhysicalConstants::ideal_gas_constant * _neighbor_temperature[_qp] * _neighbor_value[_qp] / 2;

  // Calculate the value of the pressures for the phase transition plateau (pressure in Pa)
  auto limit_pressure = exp(-26.1 + 3.88e-2 * _neighbor_temperature[_qp] -
                            9.7e-6 * Utility::pow<2>(_neighbor_temperature[_qp]));

  // define atomic fraction variable
  ADReal atomic_fraction = 0.0;
  // return warning if the PCT curves is used out of bounds (pressure in Pa)
  if (!_silence_warnings && ((neighbor_pressure < 0.011) || (neighbor_pressure > 1.e6)))
    mooseDoOnce(mooseWarning("In YHxPCT: pressure ",
                             neighbor_pressure,
                             "Pa and temperature ",
                             _neighbor_temperature[_qp],
                             "K are outside the bounds of the atomic fraction correlation. See "
                             "documentation for YHxPCT material."));

  // Calculate the atomic fraction based on the PCT curve
  if (neighbor_pressure > limit_pressure && abs(neighbor_pressure - limit_pressure) < tolerance)
  {
    // High pressure region, near limit
    atomic_fraction = 0.5;
  }
  else if (neighbor_pressure > limit_pressure)
  {
    // High pressure region (far enough from plateau)
    atomic_fraction = 2. - pow(1. + exp(21.6 - 0.0225 * _neighbor_temperature[_qp] +
                                        (-0.0445 + 7.18e-4 * _neighbor_temperature[_qp]) *
                                            log(max(neighbor_pressure - limit_pressure, 1e-10))),
                               -1);
  }
  else if ((neighbor_pressure < limit_pressure) &&
           (abs(neighbor_pressure - limit_pressure) < tolerance))
  {
    // Low pressure region, near limit
    atomic_fraction = 1.0;
  }
  else if (neighbor_pressure < limit_pressure)
  {
    // Low pressure region (far enough from plateau)
    atomic_fraction =
        0.5 - pow(0.001 + exp(-8.97e01 + 9.75e-2 * _neighbor_temperature[_qp] +
                              (1.20 - 4.41e-3 * _neighbor_temperature[_qp]) *
                                  log(max(limit_pressure - neighbor_pressure, 1e-10))),
                  -1);
  }

  // Convert to concentration
  auto _surface_equilibrium_concentration = atomic_fraction * _density[_qp];

  switch (type)
  {
    // Move all the terms to the LHS to get residual, for primary domain
    // Residual = kf*u - kb*v
    // Weak form for primary domain is: (test, kf*u - kb*v)
    case Moose::Element:
      r = _test[_i][_qp] * (_kf[_qp] * _u[_qp] - _kb[_qp] * _surface_equilibrium_concentration);
      break;

    // Similarly, weak form for secondary domain is: -(test, kf*u - kb*v),
    // flip the sign because the direction is opposite.
    case Moose::Neighbor:
      r = -_test_neighbor[_i][_qp] *
          (_kf[_qp] * _u[_qp] - _kb[_qp] * _surface_equilibrium_concentration);
      break;
  }
  return r;
}
