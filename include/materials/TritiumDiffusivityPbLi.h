/************************************************************/
/*                DO NOT MODIFY THIS HEADER                 */
/*   TMAP8: Tritium Migration Analysis Program, Version 8   */
/*                                                          */
/*   Copyright 2021 - 2026 Battelle Energy Alliance, LLC    */
/*                   ALL RIGHTS RESERVED                    */
/************************************************************/

#pragma once

#include "ValidatedModelMaterial.h"

#include "PbLiPropertyHelper.h"

/**
 * Computes the hydrogen isotope diffusivity in PbLi from literature correlations, with optional
 * classical isotope scaling. The diffusivity is provided as both a regular and an AD material
 * property.
 */
class TritiumDiffusivityPbLi
  : public ValidatedModelMaterial<PbLiPropertyHelper::DiffusivityModel,
                                  PbLiPropertyHelper::DiffusivityModelData>
{
public:
  static InputParameters validParams();

  TritiumDiffusivityPbLi(const InputParameters & parameters);

protected:
  void computeQpProperties() override;

  /// Pressure (Pa), if provided, used to check the documented pressure range
  const ADVariableValue * const _pressure;
  /// Regular diffusivity material property
  MaterialProperty<Real> & _diffusivity;
  /// AD diffusivity material property
  ADMaterialProperty<Real> & _ad_diffusivity;
};
