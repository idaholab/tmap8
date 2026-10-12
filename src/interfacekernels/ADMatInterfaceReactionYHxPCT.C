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
  // delta: ratio P/PLim below which the low-pressure branch dominates
  // zeta:  ratio P/PLim above which the high-pressure branch dominates
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

  // Fitting constant used by the high-pressure branch below
  const ADReal At_Min_HP_fit = -1.01e-6 * Utility::pow<2>(_neighbor_temperature[_qp]) +
                               2.55e-3 * _neighbor_temperature[_qp] - 5.6e-01;

  // -------------------------------
  // Ratio r = P / P_limit   (used for blending thresholds in log-space)
  // -------------------------------
  const ADReal ratio_r = neighbor_pressure / PLim;

  // -------------------------------
  // Low pressure (LP) branch: af(P) = e(T) * P^n(T)
  // Written as a function of pressure so it can be evaluated both at the
  // current pressure and at the delta blending boundary below.
  // -------------------------------
  auto f_LP = [&](const ADReal & P) -> ADReal
  {
    // Sig figs cannot be applied here. This has been tested. DO not change
    const ADReal n_T = 11.01651 - 0.02676499 * _neighbor_temperature[_qp] +
                       2.164250e-5 * Utility::pow<2>(_neighbor_temperature[_qp]) -
                       5.666033e-9 * Utility::pow<3>(_neighbor_temperature[_qp]);
    const ADReal e_T = -122.0936 + 0.2927460 * _neighbor_temperature[_qp] -
                       2.318920e-4 * Utility::pow<2>(_neighbor_temperature[_qp]) +
                       5.922527e-8 * Utility::pow<3>(_neighbor_temperature[_qp]);

    return exp(e_T) * pow(max(P, 1.e-6), n_T);
  };

  // -------------------------------
  // High pressure (HP) branch: distance above the plateau pressure
  // Written as a function of pressure so it can be evaluated both at the
  // current pressure and at the zeta blending boundary below.
  // -------------------------------
  auto f_HP = [&](const ADReal & P) -> ADReal
  {
    return 2. - 1.0015 * pow(At_Min_HP_fit + exp(24.89 - 2.53e-02 * _neighbor_temperature[_qp] +
                                                 (-3.98e-01 + 0.001 * _neighbor_temperature[_qp]) *
                                                     log(max(P - PLim, 1.e-10))),
                             -1);
  };

  // -------------------------------
  // Mid branch (exact continuity at delta*PLim and zeta*PLim)
  // -------------------------------
  // Boundaries in absolute pressure
  const ADReal delta_Plim = delta * PLim; // LP
  const ADReal zeta_Plim = zeta * PLim;   // HP

  // LP value at delta_Plim
  const ADReal f_LP_delta_Plim = f_LP(delta_Plim);

  // HP value at zeta_Plim
  const ADReal f_HP_zeta_Plim = f_HP(zeta_Plim);

  // Solve for af_mid(P) = m0 + m1 * log(P)
  const ADReal L_a = log(max(delta_Plim, 1e-10));
  const ADReal L_b = log(max(zeta_Plim, 1e-10));

  // Determine af_mid(P) slopes
  const ADReal m1 = (f_HP_zeta_Plim - f_LP_delta_Plim) / (L_b - L_a);
  const ADReal m0 = f_LP_delta_Plim - m1 * L_a;

  // Mid branch at current pressure using fitted slope
  auto f_mid = [&](const ADReal & P) -> ADReal { return m0 + m1 * log(max(P, 1e-10)); };

  // -------------------------------
  // Smooth blending in log-space (LP ↔ mid ↔ HP)
  // -------------------------------
  const ADReal x = log(max(ratio_r, 1e-10)); // log(ratio)
  const Real x_delta = log(delta);           // constant threshold (Real)
  const Real x_zeta = log(zeta);             // constant threshold (Real)

  // Sigmoid steps (AD-safe)
  const ADReal s_LP_to_mid = 1.0 / (1.0 + exp(-(x - x_delta) / blend_width)); // LP→mid
  const ADReal s_mid_to_HP = 1.0 / (1.0 + exp(-(x - x_zeta) / blend_width));  // mid→HP

  // Weights
  ADReal w_LP = 1.0 - s_LP_to_mid;                  // Low pressure weights
  ADReal w_mid = s_LP_to_mid * (1.0 - s_mid_to_HP); // Mid pressure weights
  ADReal w_HP = s_mid_to_HP;                        // High pressure weights

  // Normalization
  const ADReal w_sum = w_LP + w_mid + w_HP; // Sum of weights
  w_LP /= w_sum;                            // Ratio of weight for low pressure
  w_mid /= w_sum;                           // Ratio of weight for mid pressure
  w_HP /= w_sum;                            // Ratio of weight for high pressure

  // -------------------------------
  // Final atomic fraction
  // -------------------------------
  ADReal atomic_fraction = w_LP * f_LP(neighbor_pressure) + w_mid * f_mid(neighbor_pressure) +
                           w_HP * f_HP(neighbor_pressure);

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
