/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2025 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#include "ADMatInterfaceReactionZrCoHxPCT.h"

#include "PhysicalConstants.h"

registerMooseObject("TMAP8App", ADMatInterfaceReactionZrCoHxPCT);

InputParameters
ADMatInterfaceReactionZrCoHxPCT::validParams()

{
  InputParameters params = ADInterfaceKernel::validParams();
  params.addClassDescription(
      "Implements a reaction to establish ReactionRate=k_f*u-k_b*v to compute the surface H "
      "concentration in ZrCoHx from the temperature and partial pressure based on the PCT curves "
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

ADMatInterfaceReactionZrCoHxPCT::ADMatInterfaceReactionZrCoHxPCT(const InputParameters & parameters)
  : ADInterfaceKernel(parameters),
    _neighbor_temperature(this->template coupledGenericValue<true>("neighbor_temperature")),
    _density(getADMaterialProperty<Real>("density")),
    _kf(getADMaterialProperty<Real>("forward_rate")),
    _kb(getNeighborADMaterialProperty<Real>("backward_rate"))
{
}

ADReal
ADMatInterfaceReactionZrCoHxPCT::computeQpResidual(Moose::DGResidualType type)
{

  // Variables
  ADReal r = 0.;
  ADReal m1 = 0.0;
  ADReal m0 = 0.0;

  // Local conveniences
  using std::exp;
  using std::log;
  using std::max;

  // Gas pressure (Pa): R * T * c / 2 (two atoms per molecule)
  const ADReal neighbor_pressure = PhysicalConstants::ideal_gas_constant *
                                   _neighbor_temperature[_qp] * _neighbor_value[_qp] / 2.0;

  // Give a warning if the initial or computed neighbor pressure is out of the analytical model
  if (((neighbor_pressure < 20) || (neighbor_pressure > 2.e5)))
    mooseDoOnce(mooseWarning("In ZrCoHxPCT: pressure ",
                             neighbor_pressure,
                             "Pa and temperature ",
                             _neighbor_temperature[_qp],
                             "K are outside the bounds of the atomic fraction correlation. See "
                             "documentation for ZrCoHxPCT material."));

  // Plateau / limit pressure (Pa)
  const ADReal limit_pressure = exp(-9.41 + 3.32e-02 * _neighbor_temperature[_qp] -
                                    3.30e-06 * Utility::pow<2>(_neighbor_temperature[_qp]));

  // Transition fitted parameters, beta -> high pressure; alpha -> low pressure
  const ADReal beta_corr = 2.39 - 5.1e-03 * _neighbor_temperature[_qp] +
                           5.42e-06 * Utility::pow<2>(_neighbor_temperature[_qp]);
  const Real alpha = 1.008;

  // -------------------------------
  // Ratio r = P / P_limit   (used for blending thresholds in log-space)
  // -------------------------------
  const ADReal ratio_r = neighbor_pressure / limit_pressure;

  // Low pressure (LP) Branch
  const ADReal af_LP_grid =
      0.7 - 1.0 / (5e-03 + exp(-4.37 + 1.34e-02 * _neighbor_temperature[_qp] +
                               (-8.22e-02 - 3.97e-04 * _neighbor_temperature[_qp]) *
                                   log(max(limit_pressure - neighbor_pressure, 1e-10))));

  // High pressure (HP) branch
  const ADReal af_HP_grid =
      2.7 - 1.45 / (1.00 + exp(6.57 - 2.21e-02 * _neighbor_temperature[_qp] +
                               (6.52e-01 - 1.17e-05 * _neighbor_temperature[_qp]) *
                                   log(max(neighbor_pressure - limit_pressure, 1e-10))));

  // -------------------------------
  // Mid branch (exact continuity at P_a and P_b)
  // -------------------------------
  // Boundaries in absolute pressure
  const ADReal P_a = alpha * limit_pressure;     // LP
  const ADReal P_b = beta_corr * limit_pressure; // HP

  // LP value at P_a (same formula as LP branch)
  const ADReal af_a = 0.7 - 1.0 / (5e-03 + exp(-4.37 + 1.34e-02 * _neighbor_temperature[_qp] +
                                               (-8.22e-02 - 3.97e-04 * _neighbor_temperature[_qp]) *
                                                   log(max(limit_pressure - P_a, 1e-10))));

  // HP value at P_b (same formula as HP branch)
  const ADReal af_b = 2.7 - 1.45 / (1.00 + exp(6.57 - 2.21e-02 * _neighbor_temperature[_qp] +
                                               (6.52e-01 - 1.17e-05 * _neighbor_temperature[_qp]) *
                                                   log(max(P_b - limit_pressure, 1e-10))));

  // Solve for af_mid(P) = m0 + m1 * log(P)
  const ADReal L_a = log(max(P_a, 1e-10));
  const ADReal L_b = log(max(P_b, 1e-10));

  // Determine af_mid(P) slopes
  m1 = (af_b - af_a) / (L_b - L_a);
  m0 = af_a - (af_b - af_a) / (L_b - L_a) * L_a;

  // Mid branch at current pressure using limited slope
  const ADReal af_mid_here = m0 + m1 * log(max(neighbor_pressure, 1e-10));

  // -------------------------------
  // Smooth blending in log-space (LP ↔ mid ↔ HP)
  // -------------------------------
  // Base widths (tunable)
  const Real base_delta_alpha_log = 0.08; // typical: 0.05–0.12
  const Real base_delta_beta_log = 0.08;  // typical: 0.05–0.12

  const ADReal x = log(max(ratio_r, 1e-10));      // log(ratio)
  const Real x_alpha = log(alpha);                // constant threshold (Real)
  const ADReal x_beta = log(max(beta_corr, 1.0)); // log(beta(T))

  // Sigmoid steps (AD-safe)
  const ADReal s_alpha = 1.0 / (1.0 + exp(-(x - x_alpha) / base_delta_alpha_log)); // LP→mid
  const ADReal s_beta = 1.0 / (1.0 + exp(-(x - x_beta) / base_delta_beta_log));    // mid→HP

  // Weights
  ADReal w_LP = 1.0 - s_alpha;             // Low pressure weights
  ADReal w_mid = s_alpha * (1.0 - s_beta); // Mid pressure weights
  ADReal w_HP = s_beta;                    // High pressure weights

  // Defensive normalization
  const ADReal w_sum = w_LP + w_mid + w_HP; // Sum of weights
  w_LP /= w_sum;                            // Ratio of weight for low pressure
  w_mid /= w_sum;                           // Ratio of weight for mid pressure
  w_HP /= w_sum;                            // Ratio of weight for high pressure

  // -------------------------------
  // Final atomic fraction
  // -------------------------------
  ADReal atomic_fraction = w_LP * af_LP_grid + w_mid * af_mid_here + w_HP * af_HP_grid;

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
