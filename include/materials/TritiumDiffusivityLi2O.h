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
 * Computes the tritium diffusivity in Li$_2$O from literature Arrhenius correlations.
 * The diffusivity is provided as both a regular and an AD material property.
 */
class TritiumDiffusivityLi2O
  : public ValidatedModelMaterial<Li2OPropertyHelper::DiffusivityModel, Li2OPropertyHelper::DiffusivityModelData>
{
public:
  static InputParameters validParams();

  TritiumDiffusivityLi2O(const InputParameters & parameters);

protected:
  void computeQpProperties() override;

  /// Regular diffusivity material property
  MaterialProperty<Real> & _diffusivity;
  /// AD diffusivity material property
  ADMaterialProperty<Real> & _ad_diffusivity;
};
