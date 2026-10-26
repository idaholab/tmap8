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
 * Computes the hydrogen isotope solubility in PbLi from literature correlations, converted to
 * atoms m$^{-3}$ Pa$^{-1/2}$. The solubility is provided as both a regular and an AD material
 * property.
 */
class TritiumSolubilityPbLi
  : public ValidatedModelMaterial<PbLiPropertyHelper::SolubilityModel,
                                  PbLiPropertyHelper::SolubilityModelData>
{
public:
  static InputParameters validParams();

  TritiumSolubilityPbLi(const InputParameters & parameters);

protected:
  void computeQpProperties() override;

  /// Lithium atomic fraction of the PbLi (-)
  const Real _lithium_fraction;
  /// Pressure (Pa), if provided, used to check the documented pressure range
  const ADVariableValue * const _pressure;
  /// Regular solubility material property
  MaterialProperty<Real> & _solubility;
  /// AD solubility material property
  ADMaterialProperty<Real> & _ad_solubility;
};
