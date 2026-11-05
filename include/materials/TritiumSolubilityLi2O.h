/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2026 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#pragma once

#include "ValidatedModelMaterial.h"

#include "Li2OPropertyHelper.h"

/**
 * Computes the hydrogen isotope solubility in Li$_2$O from reduced-species literature
 * correlations.
 * The solubility is provided as both a regular and an AD material property.
 */
class TritiumSolubilityLi2O : public ValidatedModelMaterial<Li2OPropertyHelper::SolubilityModel,
                                                            Li2OPropertyHelper::SolubilityModelData>
{
public:
  static InputParameters validParams();

  TritiumSolubilityLi2O(const InputParameters & parameters);

protected:
  void computeQpProperties() override;

  /// Regular solubility material property
  MaterialProperty<Real> & _solubility;
  /// AD solubility material property
  ADMaterialProperty<Real> & _ad_solubility;
};
