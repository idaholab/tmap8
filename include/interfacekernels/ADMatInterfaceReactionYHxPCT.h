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
 * concentration in YHx from the temperature and partial pressure based on the PCT curves with u the
 * concentration in the solid and v (neighbor) the concentration in the gas.
 *
 * The original data is from C. E. Lundin, J. P. Blackledge, Pressure-Temperature-Composition
 * Relationships of the Yttrium-Hydrogen System, Journal of The Electrochemical Society 109 (9)
 * (1962) 838–5.
 * The fits are from Matthews et al., Metal Hydride Simulations Using SWIFT, LANL technical report
 * LA-UR-21-27538, 2021.
 */

class ADMatInterfaceReactionYHxPCT : public ADInterfaceKernel
{
public:
  static InputParameters validParams();

  ADMatInterfaceReactionYHxPCT(const InputParameters & parameters);

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

  /// Flag to silence correlation out of bound warnings
  const bool _silence_warnings;
};
