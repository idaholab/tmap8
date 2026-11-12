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
      "concentration in YHx from the temperature and partial pressure based on the PCT curves "
      "based "
      "on smoothly-blended low-pressure, mid, and high-pressure branches, with u the concentration "
      "in the solid and v (neighbor) the concentration in the gas in mol/m^3.");
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

  // Variables
  ADReal r = 0.;

  // Local conveniences
  using std::exp;
  using std::log;
  using std::max;
  using std::pow;

  // -------------------------------
  // Blending boundaries
  // -------------------------------
  // delta: ratio P/PLim below which the alpha phase dominates
  // zeta:  ratio P/PLim above which the beta phase dominates
  // blend_width: width of the smooth transition between branches
  const Real delta = 0.96;
  const Real zeta = 1.13;
  const Real blend_width = 0.02;

  // Gas pressure (Pa): R * T * c / 2 (two atoms per molecule)
  const ADReal neighbor_pressure =
      PhysicalConstants::ideal_gas_constant * _neighbor_temperature[_qp] * _neighbor_value[_qp] / 2;

  // Give a warning if the initial or computed neighbor pressure is out of the analytical model
  if (!_silence_warnings && ((neighbor_pressure < 1.e2) || (neighbor_pressure > 1.e6)))
    mooseDoOnce(mooseWarning("In YHxPCT: pressure ",
                             neighbor_pressure,
                             "Pa and temperature ",
                             _neighbor_temperature[_qp],
                             "K are outside the bounds of the atomic fraction correlation. See "
                             "documentation for YHxPCT material."));

  // Plateau / limit pressure (Pa)
  const ADReal PLim = exp(-26.1 + 3.88e-2 * _neighbor_temperature[_qp] -
                          9.70e-6 * Utility::pow<2>(_neighbor_temperature[_qp]));

  // Fitting constant used by the beta phase below
  const ADReal At_Min_beta_fit = -1.01e-6 * Utility::pow<2>(_neighbor_temperature[_qp]) +
                               2.55e-3 * _neighbor_temperature[_qp] - 5.6e-01;

  // -------------------------------
  // Ratio r = P / P_limit   (used for blending thresholds in log-space)
  // -------------------------------
  const ADReal ratio_r = neighbor_pressure / PLim;

  // -------------------------------
  // alpha phase: af(P) = g(T) * P^n(T)
  // Written as a function of pressure so it can be evaluated both at the
  // current pressure and at the delta blending boundary below.
  // -------------------------------
  auto f_alpha = [&](const ADReal & P) -> ADReal
  {
    // Sig figs cannot be applied here. This has been tested. DO not change
    const ADReal n_T = 11.01651 - 0.02676499 * _neighbor_temperature[_qp] +
                       2.164250e-5 * Utility::pow<2>(_neighbor_temperature[_qp]) -
                       5.666033e-9 * Utility::pow<3>(_neighbor_temperature[_qp]);
    const ADReal g_T = -122.0936 + 0.2927460 * _neighbor_temperature[_qp] -
                       2.318920e-4 * Utility::pow<2>(_neighbor_temperature[_qp]) +
                       5.922527e-8 * Utility::pow<3>(_neighbor_temperature[_qp]);

    return exp(g_T) * pow(max(P, 1.e-6), n_T);
  };

  // -------------------------------
  // beta phase: distance above the plateau pressure
  // Written as a function of pressure so it can be evaluated both at the
  // current pressure and at the zeta blending boundary below.
  // -------------------------------
  auto f_beta = [&](const ADReal & P) -> ADReal
  {
    return 2. - 1.0015 * pow(At_Min_beta_fit + exp(24.89 - 2.53e-02 * _neighbor_temperature[_qp] +
                                                 (-3.98e-01 + 0.001 * _neighbor_temperature[_qp]) *
                                                     log(max(P - PLim, 1.e-10))),
                             -1);
  };

  // -------------------------------
  // bi-phasic phase (exact continuity at delta*PLim and zeta*PLim)
  // -------------------------------
  // Boundaries in absolute pressure
  const ADReal delta_Plim = delta * PLim; // alpha
  const ADReal zeta_Plim = zeta * PLim;   // beta

  // alpha value at delta_Plim
  const ADReal f_alpha_delta_Plim = f_alpha(delta_Plim);

  // beta value at zeta_Plim
  const ADReal f_beta_zeta_Plim = f_beta(zeta_Plim);

  // Solve for af_mid(P) = m0 + m1 * log(P)
  const ADReal L_a = log(max(delta_Plim, 1e-10));
  const ADReal L_b = log(max(zeta_Plim, 1e-10));

  // Determine af_mid(P) slopes
  const ADReal m1 = (f_beta_zeta_Plim - f_alpha_delta_Plim) / (L_b - L_a);
  const ADReal m0 = f_alpha_delta_Plim - m1 * L_a;

  // bi-phasic phase at current pressure using fitted slope
  auto f_mid = [&](const ADReal & P) -> ADReal { return m0 + m1 * log(max(P, 1e-10)); };

  // -------------------------------
  // Smooth blending in log-space (alpha ↔ mid ↔ beta)
  // -------------------------------
  const ADReal x = log(max(ratio_r, 1e-10)); // log(ratio)
  const Real x_delta = log(delta);           // constant threshold (Real)
  const Real x_zeta = log(zeta);             // constant threshold (Real)

  // Sigmoid steps (AD-safe)
  const ADReal s_alpha_to_mid = 1.0 / (1.0 + exp(-(x - x_delta) / blend_width)); // alpha→mid
  const ADReal s_mid_to_beta = 1.0 / (1.0 + exp(-(x - x_zeta) / blend_width));  // mid→beta

  // Weights
  ADReal w_alpha = 1.0 - s_alpha_to_mid;                  // Low pressure weights
  ADReal w_mid = s_alpha_to_mid * (1.0 - s_mid_to_beta); // Mid pressure weights
  ADReal w_beta = s_mid_to_beta;                        // High pressure weights

  // Normalization
  const ADReal w_sum = w_alpha + w_mid + w_beta; // Sum of weights
  w_alpha /= w_sum;                            // Ratio of weight for low pressure
  w_mid /= w_sum;                           // Ratio of weight for mid pressure
  w_beta /= w_sum;                            // Ratio of weight for high pressure

  // -------------------------------
  // Final atomic fraction
  // -------------------------------
  ADReal atomic_fraction = w_alpha * f_alpha(neighbor_pressure) + w_mid * f_mid(neighbor_pressure) +
                           w_beta * f_beta(neighbor_pressure);

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
