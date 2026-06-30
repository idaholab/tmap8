/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2025 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#pragma once

#include "ADInterfaceKernel.h"

/**
 *
 * Implements a reaction to establish ReactionRate=k_f*u-k_b*v to compute the surface H
 * concentration in Zr2FeHx from the temperature and partial pressure based on the PCT curves with u
 * the concentration in the solid and v (neighbor) the concentration in the gas.
 *
 * The original data is from Yang, Zhiyi, et al. “A Potential Hydrogen Isotope Storage Material
 * Zr2Fe: Deep Exploration on Phase Transition Behaviors and Disproportionation Mechanism.” Energy
 * Materials, vol. 5, no. 1, Jan. 2025. DOI.org (Crossref),
 * https://doi.org/10.20517/energymater.2024.83.
 */

class ADMatInterfaceReactionZr2FeHxPCT : public ADInterfaceKernel
{
public:
  static InputParameters validParams();

  ADMatInterfaceReactionZr2FeHxPCT(const InputParameters & parameters);

protected:
  virtual ADReal computeQpResidual(Moose::DGResidualType type) override;

  /// Coupled temperature variable
  const GenericVariableValue<true> & _neighbor_temperature;

  /// Density of the solid
  const ADMaterialProperty<Real> & _density;

  /// Forward reaction rate coefficient
  const ADMaterialProperty<Real> & _kf;

  /// Backward reaction rate coefficient
  const ADMaterialProperty<Real> & _kb;
};
