/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2025 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/
#include "ADMatInterfaceReactionZr2FeHxPCT.h"

#include "PhysicalConstants.h"

registerMooseObject("TMAP8App", ADMatInterfaceReactionZr2FeHxPCT);

InputParameters
ADMatInterfaceReactionZr2FeHxPCT::validParams()
{
  InputParameters params = ADInterfaceKernel::validParams();
  params.addClassDescription(
      "Implements a reaction to establish ReactionRate=k_f*u-k_b*v to compute the surface H "
      "concentration in Zr2FeHx from the temperature and partial pressure based on the PCT curves "
      "with "
      "u the concentration in the solid and v (neighbor) the concentration in the gas in mol/m^3.");
  params.addRequiredCoupledVar(
      "neighbor_temperature",
      "The variable on the other side of the interface for temperature (K).");
  params.addParam<MaterialPropertyName>("density", "density", "Density of the solid in (mol/m^3).");
  params.addParam<MaterialPropertyName>(
      "forward_rate", "kf", "Forward reaction rate coefficient (1/s).");
  params.addParam<MaterialPropertyName>(
      "backward_rate", "kb", "Backward reaction rate coefficient (1/s).");
  return params;
}

ADMatInterfaceReactionZr2FeHxPCT::ADMatInterfaceReactionZr2FeHxPCT(
    const InputParameters & parameters)
  : ADInterfaceKernel(parameters),
    _neighbor_temperature(this->template coupledGenericValue<true>("neighbor_temperature")),
    _density(getADMaterialProperty<Real>("density")),
    _kf(getADMaterialProperty<Real>("forward_rate")),
    _kb(getNeighborADMaterialProperty<Real>("backward_rate"))
{
}

ADReal
ADMatInterfaceReactionZr2FeHxPCT::computeQpResidual(Moose::DGResidualType type)
{
  // Variables
  ADReal limit_pressure = 5.; // lower pressure limit of fit in Pa
  ADReal r = 0.;

  using std::exp;
  using std::log;
  using std::max;

  // Gas pressure (Pa): R * T * c / 2 (two atoms per molecule)
  auto neighbor_pressure =
      PhysicalConstants::ideal_gas_constant * _neighbor_temperature[_qp] * _neighbor_value[_qp] / 2;

  // Give a warning if the initial or computed neighbor pressure is out of the analytical model
  if (((neighbor_pressure < 7) || (neighbor_pressure > 5e5)))
    mooseDoOnce(mooseWarning("In Zr2FeHxPCT: pressure ",
                             neighbor_pressure,
                             "Pa and temperature ",
                             _neighbor_temperature[_qp],
                             "K are outside the bounds of the atomic fraction correlation. See "
                             "documentation for Zr2FeHxPCT material."));

  // Calculate the atomic fraction based on the PCT curve
  auto atomic_fraction =
      5.0 - 8.32e-03 / (1.e-03 + exp(-2.49 - 7.62e-03 * _neighbor_temperature[_qp] +
                                     (5.63e-02 + 1.72e-04 * _neighbor_temperature[_qp]) *
                                         log(max(neighbor_pressure - limit_pressure, 1.e-10))));

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
