/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2025 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#pragma once

#include "ADKernel.h"

/**
 * This kernel adds to the residual a contribution of \f$ - coeff*L*vs \f$ where
 * coeff is a simple coefficient, \f$ K \f$ is a material property and \f$ vs \f$
 * is the multiplication of several variables (nonlinear or coupled).
 */
class ADMatReactionFlexible : public ADKernel
{
public:
  static InputParameters validParams();

  ADMatReactionFlexible(const InputParameters & parameters);

protected:
  virtual ADReal computeQpResidual() override;

  /**
   * Kernel variable (can be nonlinear or coupled variable)
   * (For constrained Allen-Cahn problems, v = lambda
   * where lambda is the Lagrange multiplier)
   */
  const unsigned int _num_vs;
  const std::vector<const ADVariableValue *> _vs;

  /// Reaction rate
  const ADMaterialProperty<Real> & _reaction_rate;

  /**
   * An optional input-file supplied coefficient for multiplying the reaction
   * term. It can be used to include the stoichiometry of a reaction for specific
   * species.
   */
  const Real _coeff;
};
