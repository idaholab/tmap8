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

  // Fitting constants of High-Pressure (HP)
  const ADReal HP_A = 2.7;
  const ADReal HP_B = 1.45;
  const ADReal HP_C = 1.00;
  const ADReal HP_D = 6.57;
  const ADReal HP_E = 2.21e-02;
  const ADReal HP_F = 6.52e-01;
  const ADReal HP_G = 1.17e-05;
  // Fitting constants of  Low-Pressure (LP)
  const ADReal LP_A = 0.7;
  const ADReal LP_B = 1.0;
  const ADReal LP_C = 5.e-03;
  const ADReal LP_D = -4.37;
  const ADReal LP_E = -1.34e-02;
  const ADReal LP_F = -8.22e-02;
  const ADReal LP_G = 3.97e-04;


  // -------------------------------
  // Shared PCT correlation shape
  // -------------------------------
  // Both the LP and HP branches (and their values at the blending boundaries
  // P_a and P_b) evaluate the exact same functional form:
  //
  //   af(P) = A - B / (C + exp(D - E*T + (F - G*T) * log(max(pressure_diff, 1e-10))))
  //
  // Only the fitting-constant set (A..G) and the "distance from the plateau
  // pressure" term (pressure_diff) differ between calls, so we factor the
  // formula into a single lambda and reuse it for every branch below.
 auto pctCorrelation = [&](const auto & A,
                            const auto & B,
                            const auto & C,
                            const auto & D,
                            const auto & E,
                            const auto & F,
                            const auto & G,
                            const ADReal & pressure_diff) -> ADReal
  {
    return A - B / (C + exp(D - E *  _neighbor_temperature[_qp] + (F - G *  _neighbor_temperature[_qp]) * log(max(pressure_diff, 1e-10))));
  };

  // Gas pressure (Pa): R * T * c / 2 (two atoms per molecule)
  const ADReal neighbor_pressure =
      PhysicalConstants::ideal_gas_constant *  _neighbor_temperature[_qp] * _neighbor_value[_qp] / 2.0;

  // Give a warning if the initial or computed neighbor pressure is out of the analytical model
  if (((neighbor_pressure < 20) || (neighbor_pressure > 2.e5)))
    mooseDoOnce(mooseWarning("In ZrCoHxPCT: pressure ",
                             neighbor_pressure,
                             "Pa and temperature ",
                              _neighbor_temperature[_qp],
                             "K are outside the bounds of the atomic fraction correlation. See "
                             "documentation for ZrCoHxPCT material."));

  // Plateau / limit pressure (Pa)
  const ADReal PLim =
      exp(-9.41 + 3.32e-02 *  _neighbor_temperature[_qp] - 3.30e-06 * Utility::pow<2>( _neighbor_temperature[_qp]));

  // Transition fitted parameters, beta -> high pressure; alpha -> low pressure
  const ADReal beta_corr = 2.39 - 5.1e-03 *  _neighbor_temperature[_qp] + 5.42e-06 * Utility::pow<2>( _neighbor_temperature[_qp]);
  const Real alpha = 1.008;

  // -------------------------------
  // Ratio r = P / P_limit   (used for blending thresholds in log-space)
  // -------------------------------
  const ADReal ratio_r = neighbor_pressure / PLim;

  // Low pressure (LP) branch: distance below the plateau pressure
  const ADReal f_LP =
      pctCorrelation(LP_A, LP_B, LP_C, LP_D, LP_E, LP_F, LP_G, PLim - neighbor_pressure);

  // High pressure (HP) branch: distance above the plateau pressure
  const ADReal f_HP =
      pctCorrelation(HP_A, HP_B, HP_C, HP_D, HP_E, HP_F, HP_G, neighbor_pressure - PLim);

  // -------------------------------
  // Mid branch (exact continuity at alpha*Plim and beta*Plim)
  // -------------------------------
  // Boundaries in absolute pressure
  const ADReal alpha_Plim = alpha * PLim;     // LP
  const ADReal beta_Plim = beta_corr * PLim; // HP

  // LP value at alpha_Plim
  const ADReal f_LP_alpha_Plim = pctCorrelation(LP_A, LP_B, LP_C, LP_D, LP_E, LP_F, LP_G, PLim - alpha_Plim);

  // HP value at beta_Plim
  const ADReal f_HP_beta_Plim = pctCorrelation(HP_A, HP_B, HP_C, HP_D, HP_E, HP_F, HP_G, beta_Plim - PLim);

  // Solve for af_mid(P) = m0 + m1 * log(P)
  const ADReal L_a = log(max(alpha_Plim, 1e-10));
  const ADReal L_b = log(max(beta_Plim, 1e-10));

  // Determine af_mid(P) slopes
  m1 = (f_HP_beta_Plim - f_LP_alpha_Plim) / (L_b - L_a);
  m0 = f_LP_alpha_Plim - (f_HP_beta_Plim - f_LP_alpha_Plim) / (L_b - L_a) * L_a;

  // Mid branch at current pressure using limited slope
  const ADReal f_mid= m0 + m1 * log(max(neighbor_pressure, 1e-10));

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
  const ADReal s_LP_to_mid = 1.0 / (1.0 + exp(-(x - x_alpha) / base_delta_alpha_log)); // LP→mid
  const ADReal s_mid_to_HP = 1.0 / (1.0 + exp(-(x - x_beta) / base_delta_beta_log));    // mid→HP

  // Weights
  ADReal w_LP = 1.0 - s_LP_to_mid;             // Low pressure weights
  ADReal w_mid = s_LP_to_mid * (1.0 - s_mid_to_HP); // Mid pressure weights
  ADReal w_HP = s_mid_to_HP;                    // High pressure weights

  // Normalization
  const ADReal w_sum = w_LP + w_mid + w_HP; // Sum of weights
  w_LP /= w_sum;                            // Ratio of weight for low pressure
  w_mid /= w_sum;                           // Ratio of weight for mid pressure
  w_HP /= w_sum;                            // Ratio of weight for high pressure

  // -------------------------------
  // Final atomic fraction
  // -------------------------------
  ADReal atomic_fraction = w_LP * f_LP + w_mid * f_mid+ w_HP * f_HP;

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
