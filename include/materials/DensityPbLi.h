/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2026 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#pragma once

#include "ValidatedModelBase.h"

#include "PbLiPropertyHelper.h"

/**
 * Computes the temperature-dependent density of PbLi from literature correlations.
 * The density is provided as both a regular and an AD material property.
 */
class DensityPbLi : public ValidatedModelBase<PbLiPropertyHelper::DensityModel,
                                              PbLiPropertyHelper::DensityModelData>
{
public:
  static InputParameters validParams();

  DensityPbLi(const InputParameters & parameters);

protected:
  void computeQpProperties() override;

  /// Regular density material property
  MaterialProperty<Real> & _density;
  /// AD density material property
  ADMaterialProperty<Real> & _ad_density;
};
